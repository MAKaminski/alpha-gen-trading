"""Test-specific storage models to avoid SQLAlchemy conflicts."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncIterator, TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import Field, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.alphagen.config import load_app_config


class TestEquityTickRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    symbol: str
    price: float
    session_vwap: float
    ma9: float
    as_of: datetime


class TestOptionQuoteRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    option_symbol: str
    strike: float
    bid: float
    ask: float
    expiry: datetime
    as_of: datetime


class TestPositionSnapshotRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    symbol: str
    quantity: int
    average_price: float
    market_value: float
    as_of: datetime


class TestNormalizedTickRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    as_of: datetime
    equity_symbol: str
    equity_price: float
    session_vwap: float
    ma9: float
    option_symbol: str
    option_strike: float
    option_bid: float
    option_ask: float
    option_expiry: datetime


class TestSignalRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    signal_type: str
    strength: float
    as_of: datetime


class TestTradeIntentRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    symbol: str
    action: str
    quantity: int
    price: float
    as_of: datetime


class TestExecutionRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    symbol: str
    action: str
    quantity: int
    price: float
    as_of: datetime


def get_test_engine() -> AsyncEngine:
    """Get a test database engine."""
    return create_async_engine("sqlite+aiosqlite:///:memory:")


@asynccontextmanager
async def test_session_scope() -> AsyncIterator[AsyncSession]:
    """Test session scope context manager."""
    engine = get_test_engine()
    async with AsyncSession(engine) as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    await engine.dispose()


async def init_test_models() -> None:
    """Initialize test models."""
    engine = get_test_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    await engine.dispose()
