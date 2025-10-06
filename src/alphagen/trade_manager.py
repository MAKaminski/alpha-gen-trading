"""Trade execution and lifecycle management."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Coroutine, Dict, Optional

from alphagen.core.events import NormalizedTick, OptionQuote, TradeExecution, TradeIntent
from alphagen.config import OPTION_CONTRACT_MULTIPLIER
from alphagen.core.time_utils import session_bounds
from alphagen.option_monitor import OptionMonitor
from alphagen.schwab_client import SchwabClient
import structlog


@dataclass
class TradeManager:
    emit_execution: Callable[[TradeExecution], Coroutine[None, None, None]]
    schwab_client: SchwabClient
    option_monitor: OptionMonitor | None = None
    _open_positions: Dict[str, TradeExecution] = field(default_factory=dict)
    _last_quotes: Dict[str, OptionQuote] = field(default_factory=dict)
    _logger: structlog.BoundLogger = field(default_factory=lambda: structlog.get_logger("alphagen.trade_manager"), init=False)

    async def handle_intent(self, intent: TradeIntent) -> None:
        symbol = intent.option_symbol
        if self._open_positions and symbol not in self._open_positions:
            self._logger.warning(
                "single_position_rule_blocked",
                existing=list(self._open_positions.keys()),
                incoming=symbol,
            )
            return
        if symbol in self._open_positions:
            await self._close_position(symbol, reason="rollover")
        execution = await self.schwab_client.submit_order(intent)
        self._open_positions[symbol] = execution
        await self.emit_execution(execution)
        if self.option_monitor and intent.action.upper().startswith("SELL"):
            self.option_monitor.track(symbol)

    async def handle_tick(self, tick: NormalizedTick) -> None:
        if not tick.option:
            return
        symbol = tick.option.option_symbol
        await self.update_option_quote(tick.option)

    async def update_option_quote(self, quote: OptionQuote) -> None:
        symbol = quote.option_symbol
        self._last_quotes[symbol] = quote
        if symbol not in self._open_positions:
            return
        await self._evaluate_exits(symbol, quote.mid(), quote.as_of)

    async def _evaluate_exits(self, symbol: str, price: float, as_of: datetime) -> None:
        execution = self._open_positions[symbol]
        entry_intent = execution.intent
        _, end = session_bounds(as_of)
        reason: str | None = None
        if price <= entry_intent.take_profit:
            reason = "take-profit"
        elif price >= entry_intent.stop_loss:
            reason = "stop-loss"
        elif as_of >= end:
            reason = "session-close"
        if reason is None:
            return
        await self._close_position(symbol, price=price, reason=reason)

    async def close_all(self, reason: str = "manual") -> None:
        for symbol in list(self._open_positions.keys()):
            await self._close_position(symbol, reason=reason)

    async def _close_position(
        self,
        symbol: str,
        price: Optional[float] = None,
        reason: str = "manual",
    ) -> None:
        execution = self._open_positions.get(symbol)
        if not execution:
            return
        quote = self._last_quotes.get(symbol)
        fill_price = price or (quote.mid() if quote else execution.fill_price)
        closing_intent = TradeIntent(
            as_of=quote.as_of if quote else execution.as_of,
            action="BUY_TO_CLOSE",
            option_symbol=symbol,
            quantity=execution.intent.quantity,
            limit_price=fill_price,
            stop_loss=0,
            take_profit=0,
        )
        closing_execution = await self.schwab_client.submit_order(closing_intent)
        pnl = self._calculate_pnl(execution, closing_execution)
        closing_execution.pnl_contrib = pnl
        await self.emit_execution(closing_execution)
        del self._open_positions[symbol]
        if self.option_monitor:
            self.option_monitor.untrack(symbol)

    def _calculate_pnl(self, entry: TradeExecution, exit_exec: TradeExecution) -> float:
        multiplier = OPTION_CONTRACT_MULTIPLIER
        direction = -1 if entry.intent.action.upper().startswith("SELL") else 1
        per_contract = (exit_exec.fill_price - entry.fill_price) * direction
        return per_contract * entry.intent.quantity * multiplier
