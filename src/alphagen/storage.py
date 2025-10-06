"""Database models and repository helpers."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncIterator, TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import Field, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.alphagen.config import load_app_config


class EquityTickRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    symbol: str
    price: float
    session_vwap: float
    ma9: float
    as_of: datetime


class OptionQuoteRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    option_symbol: str
    strike: float
    bid: float
    ask: float
    expiry: datetime
    as_of: datetime


class PositionSnapshotRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    symbol: str
    quantity: int
    average_price: float
    market_value: float
    as_of: datetime


class NormalizedTickRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    as_of: datetime
    equity_symbol: str
    equity_price: float
    session_vwap: float
    ma9: float
    option_symbol: str | None
    option_bid: float | None
    option_ask: float | None


class SignalRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    action: str
    option_symbol: str
    rationale: str
    as_of: datetime
    cooldown_until: datetime


class TradeIntentRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    action: str
    option_symbol: str
    quantity: int
    limit_price: float
    stop_loss: float
    take_profit: float
    as_of: datetime


class ExecutionRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: str
    status: str
    fill_price: float
    pnl_contrib: float
    as_of: datetime
    intent_id: int | None = Field(default=None)


_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        database_url = load_app_config().storage.database_url
        _engine = create_async_engine(database_url, echo=False, future=True)
    return _engine


async def init_models() -> None:
    async with get_engine().begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    session = AsyncSession(get_engine())
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


# --- Persistence helpers -------------------------------------------------
if TYPE_CHECKING:
    from alphagen.core.events import (
        EquityTick,
        OptionQuote,
        PositionSnapshot,
        Signal,
        TradeExecution,
        TradeIntent,
        NormalizedTick,
    )


async def insert_equity_tick(tick: "EquityTick") -> None:
    async with session_scope() as session:
        session.add(
            EquityTickRow(
                symbol=tick.symbol,
                price=tick.price,
                session_vwap=tick.session_vwap,
                ma9=tick.ma9,
                as_of=tick.as_of,
            )
        )


async def insert_option_quote(quote: "OptionQuote") -> None:
    async with session_scope() as session:
        session.add(
            OptionQuoteRow(
                option_symbol=quote.option_symbol,
                strike=quote.strike,
                bid=quote.bid,
                ask=quote.ask,
                expiry=quote.expiry,
                as_of=quote.as_of,
            )
        )


async def insert_signal(signal: "Signal") -> None:
    async with session_scope() as session:
        session.add(
            SignalRow(
                action=signal.action,
                option_symbol=signal.option_symbol,
                rationale=signal.rationale,
                as_of=signal.as_of,
                cooldown_until=signal.cooldown_until,
            )
        )


async def insert_trade_intent(intent: "TradeIntent") -> int:
    async with session_scope() as session:
        row = TradeIntentRow(
            action=intent.action,
            option_symbol=intent.option_symbol,
            quantity=intent.quantity,
            limit_price=intent.limit_price,
            stop_loss=intent.stop_loss,
            take_profit=intent.take_profit,
            as_of=intent.as_of,
        )
        session.add(row)
        await session.flush()
        return row.id or 0


async def insert_execution(
    execution: "TradeExecution", intent_id: int | None = None
) -> None:
    async with session_scope() as session:
        session.add(
            ExecutionRow(
                order_id=execution.order_id,
                status=execution.status,
                fill_price=execution.fill_price,
                pnl_contrib=execution.pnl_contrib,
                as_of=execution.as_of,
                intent_id=intent_id,
            )
        )


async def insert_positions(positions: list["PositionSnapshot"]) -> None:
    if not positions:
        return
    async with session_scope() as session:
        for snapshot in positions:
            session.add(
                PositionSnapshotRow(
                    symbol=snapshot.symbol,
                    quantity=snapshot.quantity,
                    average_price=snapshot.average_price,
                    market_value=snapshot.market_value,
                    as_of=snapshot.as_of,
                )
            )


async def insert_normalized_tick(tick: "NormalizedTick") -> None:
    async with session_scope() as session:
        option = tick.option
        session.add(
            NormalizedTickRow(
                as_of=tick.as_of,
                equity_symbol=tick.equity.symbol,
                equity_price=tick.equity.price,
                session_vwap=tick.equity.session_vwap,
                ma9=tick.equity.ma9,
                option_symbol=option.option_symbol if option else None,
                option_bid=option.bid if option else None,
                option_ask=option.ask if option else None,
            )
        )
