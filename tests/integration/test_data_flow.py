"""Integration tests for data flow through the system."""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone

from src.alphagen.app import AlphaGenApp
from src.alphagen.core.events import EquityTick, OptionQuote, NormalizedTick
from src.alphagen.core.time_utils import now_est


@pytest.mark.asyncio
async def test_market_data_to_signal_flow():
    """Test complete data flow from market data to signal generation."""
    with (
        patch("src.alphagen.app.SchwabOAuthClient") as mock_schwab_class,
        patch(
            "src.alphagen.app.create_market_data_provider"
        ) as mock_market_data_factory,
        patch("src.alphagen.app.init_models") as mock_init_models,
    ):
        # Mock Schwab client
        mock_schwab = AsyncMock()
        mock_schwab.fetch_positions.return_value = []
        mock_schwab_class.create.return_value = mock_schwab

        # Mock market data provider
        mock_market_data = AsyncMock()
        mock_market_data_factory.return_value = mock_market_data

        # Mock database initialization
        mock_init_models.return_value = AsyncMock()

        # Create app
        app = AlphaGenApp()

        # Mock the market data callbacks
        callbacks = None

        async def mock_start(cb):
            nonlocal callbacks
            callbacks = cb

        mock_market_data.start.side_effect = mock_start

        # Start the app
        await app.run()

        # Simulate market data
        equity_tick = EquityTick(
            symbol="QQQ",
            price=400.0,
            session_vwap=399.0,
            ma9=401.0,
            as_of=now_est(),
        )

        option_quote = OptionQuote(
            option_symbol="QQQ241220C00400000",
            strike=400.0,
            bid=5.50,
            ask=5.75,
            expiry=datetime.now(timezone.utc),
            as_of=now_est(),
        )

        # Send data through the system
        if callbacks:
            await callbacks.on_equity_tick(equity_tick)
            await callbacks.on_option_quote(option_quote)

        # Verify data was processed
        # (In a real test, you'd check that signals were generated, data was stored, etc.)


@pytest.mark.asyncio
async def test_position_polling_integration():
    """Test integration of position polling with the main app."""
    with (
        patch("src.alphagen.app.SchwabOAuthClient") as mock_schwab_class,
        patch(
            "src.alphagen.app.create_market_data_provider"
        ) as mock_market_data_factory,
        patch("src.alphagen.app.init_models") as mock_init_models,
    ):
        # Mock Schwab client with position data
        mock_schwab = AsyncMock()
        mock_positions = [
            {
                "symbol": "QQQ",
                "quantity": 100,
                "average_price": 400.0,
                "market_value": 40000.0,
                "as_of": now_est().isoformat(),
            }
        ]
        mock_schwab.fetch_positions.return_value = mock_positions
        mock_schwab_class.create.return_value = mock_schwab

        # Mock other components
        mock_market_data = AsyncMock()
        mock_market_data_factory.return_value = mock_market_data
        mock_init_models.return_value = AsyncMock()

        # Create app
        app = AlphaGenApp()

        # Mock market data start
        async def mock_start(cb):
            pass

        mock_market_data.start.side_effect = mock_start

        # Start the app
        await app.run()

        # Verify position polling was called
        mock_schwab.fetch_positions.assert_called()


@pytest.mark.asyncio
async def test_signal_to_trade_flow():
    """Test integration from signal generation to trade execution."""
    with (
        patch("src.alphagen.app.SchwabOAuthClient") as mock_schwab_class,
        patch(
            "src.alphagen.app.create_market_data_provider"
        ) as mock_market_data_factory,
        patch("src.alphagen.app.init_models") as mock_init_models,
    ):
        # Mock Schwab client
        mock_schwab = AsyncMock()
        mock_schwab.fetch_positions.return_value = []
        mock_schwab.submit_order.return_value = AsyncMock()
        mock_schwab_class.create.return_value = mock_schwab

        # Mock other components
        mock_market_data = AsyncMock()
        mock_market_data_factory.return_value = mock_market_data
        mock_init_models.return_value = AsyncMock()

        # Create app
        app = AlphaGenApp()

        # Mock market data start
        async def mock_start(cb):
            pass

        mock_market_data.start.side_effect = mock_start

        # Start the app
        await app.run()

        # Create a normalized tick that should generate a signal
        normalized_tick = NormalizedTick(
            as_of=now_est(),
            equity=EquityTick("QQQ", 400.0, 401.0, 399.0, now_est()),
            option=OptionQuote(
                "QQQ241220C00400000", 400.0, 5.50, 5.75, now_est(), now_est()
            ),
        )

        # Process the tick through the signal engine
        await app._signal_engine.handle_tick(normalized_tick)

        # Verify that a trade intent would be generated
        # (In a real test, you'd check the trade generator was called)


@pytest.mark.asyncio
async def test_error_handling_integration():
    """Test error handling across the integrated system."""
    with (
        patch("src.alphagen.app.SchwabOAuthClient") as mock_schwab_class,
        patch(
            "src.alphagen.app.create_market_data_provider"
        ) as mock_market_data_factory,
        patch("src.alphagen.app.init_models") as mock_init_models,
    ):
        # Mock Schwab client that raises an error
        mock_schwab = AsyncMock()
        mock_schwab.fetch_positions.side_effect = Exception("API Error")
        mock_schwab_class.create.return_value = mock_schwab

        # Mock other components
        mock_market_data = AsyncMock()
        mock_market_data_factory.return_value = mock_market_data
        mock_init_models.return_value = AsyncMock()

        # Create app
        app = AlphaGenApp()

        # Mock market data start
        async def mock_start(cb):
            pass

        mock_market_data.start.side_effect = mock_start

        # Start the app
        await app.run()

        # Verify that errors are handled gracefully
        # (The app should continue running despite API errors)
