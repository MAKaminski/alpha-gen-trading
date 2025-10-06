"""Base contracts and callback structures for market data providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from alphagen.core.events import EquityTick, OptionQuote


@dataclass(slots=True)
class StreamCallbacks:
    on_equity_tick: "Callback[EquityTick]"
    on_option_quote: "Callback[OptionQuote]"
    on_error: "Callback[Exception]"


class Callback(Protocol):
    async def __call__(self, payload):  # pragma: no cover - protocol signature
        ...


class MarketDataProvider(Protocol):
    async def start(self, callbacks: StreamCallbacks) -> None: ...

    async def stop(self) -> None: ...
