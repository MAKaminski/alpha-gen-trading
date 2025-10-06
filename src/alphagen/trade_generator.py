"""Generate trade intents from signals."""

from __future__ import annotations

from typing import Callable, Coroutine

from alphagen.config import load_app_config
from alphagen.core.events import Signal, TradeIntent


class TradeGenerator:
    def __init__(
        self,
        emit: Callable[[TradeIntent], Coroutine[None, None, None]],
    ) -> None:
        self._emit = emit
        self._risk = load_app_config().risk

    async def handle_signal(self, signal: Signal) -> None:
        credit = signal.reference_price
        stop_price = credit * (1 + self._risk.stop_loss_multiple)
        take_profit_price = max(credit * (1 - self._risk.take_profit_multiple), 0.01)
        intent = TradeIntent(
            as_of=signal.as_of,
            action=signal.action,
            option_symbol=signal.option_symbol,
            quantity=self._risk.max_position_size,
            limit_price=credit,
            stop_loss=stop_price,
            take_profit=take_profit_price,
        )
        await self._emit(intent)
