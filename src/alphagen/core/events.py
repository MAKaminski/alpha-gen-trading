"""Domain event models used across the pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from alphagen.config import EST


@dataclass(slots=True)
class EquityTick:
    symbol: str
    price: float
    session_vwap: float
    ma9: float
    as_of: datetime

    def __post_init__(self) -> None:
        if self.as_of.tzinfo is None:
            self.as_of = self.as_of.replace(tzinfo=EST)


@dataclass(slots=True)
class OptionQuote:
    option_symbol: str
    strike: float
    bid: float
    ask: float
    expiry: datetime
    as_of: datetime

    def mid(self) -> float:
        return (self.bid + self.ask) / 2


@dataclass(slots=True)
class PositionSnapshot:
    symbol: str
    quantity: int
    average_price: float
    market_value: float
    as_of: datetime


@dataclass(slots=True)
class NormalizedTick:
    as_of: datetime
    equity: EquityTick
    option: Optional[OptionQuote]


@dataclass(slots=True)
class Signal:
    as_of: datetime
    action: str
    option_symbol: str
    reference_price: float
    rationale: str
    cooldown_until: datetime


@dataclass(slots=True)
class TradeIntent:
    as_of: datetime
    action: str
    option_symbol: str
    quantity: int
    limit_price: float
    stop_loss: float
    take_profit: float


@dataclass(slots=True)
class TradeExecution:
    order_id: str
    status: str
    fill_price: float
    pnl_contrib: float
    as_of: datetime
    intent: TradeIntent


@dataclass(slots=True)
class CooldownState:
    until: datetime

    def active(self, now: datetime) -> bool:
        return now < self.until

    @classmethod
    def expired(cls) -> "CooldownState":
        return cls(until=datetime.min.replace(tzinfo=EST))

    def extend(self, duration: timedelta, from_time: Optional[datetime] = None) -> "CooldownState":
        start = from_time or self.until
        return CooldownState(until=start + duration)


@dataclass(slots=True)
class PositionState:
    as_of: datetime
    symbols: dict[str, PositionSnapshot]

    def total_market_value(self) -> float:
        return sum(pos.market_value for pos in self.symbols.values())
