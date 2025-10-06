"""ETL stage that normalizes raw Polygon streams into aligned ticks."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Coroutine, Optional

from alphagen.config import DEFAULT_EQUITY_TICKER
from alphagen.core.events import EquityTick, NormalizedTick, OptionQuote
from alphagen.core.time_utils import within_trading_window


@dataclass
class Normalizer:
    emit: Callable[[NormalizedTick], Coroutine[None, None, None]]
    equity_symbol: str = DEFAULT_EQUITY_TICKER

    def __post_init__(self) -> None:
        self._latest_equity: Optional[EquityTick] = None
        self._latest_option: Optional[OptionQuote] = None
        self._option_buffer: deque[OptionQuote] = deque(maxlen=20)

    async def ingest_equity(self, tick: EquityTick) -> None:
        if tick.symbol != self.equity_symbol:
            return
        if not within_trading_window(tick.as_of):
            return
        self._latest_equity = tick
        await self._attempt_emit()

    async def ingest_option(self, quote: OptionQuote) -> None:
        if quote.option_symbol.startswith(self.equity_symbol):
            self._option_buffer.append(quote)
            if not within_trading_window(quote.as_of):
                return
            self._latest_option = self._select_nearest_option(quote.as_of)
            await self._attempt_emit()

    async def _attempt_emit(self) -> None:
        if not self._latest_equity:
            return
        normalized = NormalizedTick(
            as_of=self._latest_equity.as_of.replace(microsecond=0),
            equity=self._latest_equity,
            option=self._latest_option,
        )
        await self.emit(normalized)

    def _select_nearest_option(self, now: datetime) -> Optional[OptionQuote]:
        same_day_quotes = [
            quote for quote in self._option_buffer if quote.expiry.date() == now.date()
        ]
        if not same_day_quotes:
            return None
        underlying_price = self._latest_equity.price if self._latest_equity else None
        if underlying_price is None:
            return same_day_quotes[-1]
        return min(
            same_day_quotes,
            key=lambda q: abs(q.strike - underlying_price),
        )
