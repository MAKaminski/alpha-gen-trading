"""Pytest configuration and shared fixtures."""
import asyncio
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from alphagen.core.events import EquityTick, OptionQuote, NormalizedTick
from alphagen.core.time_utils import now_est


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_equity_tick():
    """Create a mock equity tick for testing."""
    return EquityTick(
        symbol="QQQ",
        price=400.0,
        session_vwap=399.0,
        ma9=401.0,
        as_of=now_est(),
    )


@pytest.fixture
def mock_option_quote():
    """Create a mock option quote for testing."""
    return OptionQuote(
        option_symbol="QQQ241220C00400000",
        strike=400.0,
        bid=5.50,
        ask=5.75,
        expiry=datetime(2024, 12, 20, 16, 0, 0, tzinfo=timezone.utc),
        as_of=now_est(),
    )


@pytest.fixture
def mock_normalized_tick(mock_equity_tick, mock_option_quote):
    """Create a mock normalized tick for testing."""
    return NormalizedTick(
        as_of=now_est(),
        equity=mock_equity_tick,
        option=mock_option_quote,
    )


@pytest.fixture
def mock_schwab_client():
    """Create a mock Schwab client for testing."""
    client = AsyncMock()
    client.fetch_positions.return_value = []
    client.fetch_option_quote.return_value = None
    client.submit_order.return_value = AsyncMock()
    client.close.return_value = AsyncMock()
    return client


@pytest.fixture
def mock_market_data_provider():
    """Create a mock market data provider for testing."""
    provider = AsyncMock()
    provider.start.return_value = AsyncMock()
    provider.stop.return_value = AsyncMock()
    return provider


@pytest.fixture
def sample_config():
    """Create a sample configuration for testing."""
    from alphagen.config import AppConfig, PolygonSettings, SchwabSettings, StorageSettings, RiskSettings, FeatureSettings
    from zoneinfo import ZoneInfo
    
    return AppConfig(
        polygon=PolygonSettings(
            api_key="test_key",
            equity_ticker="QQQ",
            options_underlying="QQQ",
        ),
        schwab=SchwabSettings(
            api_key="test_key",
            api_secret="test_secret",
            account_id="123456",
        ),
        storage=StorageSettings(
            database_url="sqlite+aiosqlite:///:memory:",
        ),
        risk=RiskSettings(),
        features=FeatureSettings(),
        timezone=ZoneInfo("America/New_York"),
    )
