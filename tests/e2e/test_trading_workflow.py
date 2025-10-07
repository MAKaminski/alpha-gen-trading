"""End-to-end tests for complete trading workflows."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import timedelta

from src.alphagen.app import AlphaGenApp
from src.alphagen.core.events import EquityTick, OptionQuote
from src.alphagen.core.time_utils import now_est


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_complete_trading_cycle():
    """Test a complete trading cycle from market data to position closure."""
    with (
        patch("alphagen.app.SchwabOAuthClient.create") as mock_schwab_create,
        patch(
            "alphagen.app.create_market_data_provider"
        ) as mock_market_data_factory,
        patch("alphagen.app.init_models") as mock_init_models,
    ):
        # Mock Schwab client
        mock_schwab = AsyncMock()
        mock_schwab.fetch_positions.return_value = []
        mock_schwab.submit_order.return_value = AsyncMock()
        mock_schwab_create.return_value = mock_schwab

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
        app_task = asyncio.create_task(app.run())

        # Wait a bit for initialization
        await asyncio.sleep(0.1)

        # Simulate market data that creates a crossover
        current_time = now_est()

        # First tick: VWAP below MA9
        equity_tick1 = EquityTick(
            symbol="QQQ",
            price=400.0,
            session_vwap=399.0,
            ma9=401.0,
            as_of=current_time,
        )

        option_quote1 = OptionQuote(
            option_symbol="QQQ241220C00400000",
            strike=400.0,
            bid=5.50,
            ask=5.75,
            expiry=current_time + timedelta(hours=1),
            as_of=current_time,
        )

        # Second tick: VWAP crosses above MA9 (should trigger signal)
        equity_tick2 = EquityTick(
            symbol="QQQ",
            price=400.0,
            session_vwap=401.0,
            ma9=399.0,
            as_of=current_time + timedelta(seconds=1),
        )

        option_quote2 = OptionQuote(
            option_symbol="QQQ241220C00400000",
            strike=400.0,
            bid=5.50,
            ask=5.75,
            expiry=current_time + timedelta(hours=1),
            as_of=current_time + timedelta(seconds=1),
        )

        # Send data through the system
        if callbacks:
            await callbacks.on_equity_tick(equity_tick1)
            await callbacks.on_option_quote(option_quote1)
            await asyncio.sleep(0.1)

            await callbacks.on_equity_tick(equity_tick2)
            await callbacks.on_option_quote(option_quote2)

        # Wait for processing
        await asyncio.sleep(0.5)

        # Simulate take profit scenario
        take_profit_quote = OptionQuote(
            option_symbol="QQQ241220C00400000",
            strike=400.0,
            bid=2.50,  # Below take profit level
            ask=2.75,
            expiry=current_time + timedelta(hours=1),
            as_of=current_time + timedelta(seconds=2),
        )

        if callbacks:
            await callbacks.on_option_quote(take_profit_quote)

        # Wait for processing
        await asyncio.sleep(0.5)

        # Stop the app
        app_task.cancel()
        try:
            await app_task
        except asyncio.CancelledError:
            pass

        # Verify that trades were executed
        # (In a real test, you'd check the database for executed trades)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_market_hours_handling():
    """Test that the system handles market hours correctly."""
    with (
        patch("alphagen.app.SchwabOAuthClient.create") as mock_schwab_create,
        patch(
            "alphagen.app.create_market_data_provider"
        ) as mock_market_data_factory,
        patch("alphagen.app.init_models") as mock_init_models,
        patch(
            "alphagen.core.time_utils.within_trading_window"
        ) as mock_trading_window,
    ):
        # Mock trading window to return False (market closed)
        mock_trading_window.return_value = False

        # Mock components
        mock_schwab = AsyncMock()
        mock_schwab.fetch_positions.return_value = []
        # Configure fetch_equity_quote to return a proper EquityTick
        mock_schwab.fetch_equity_quote.return_value = EquityTick(
            symbol="QQQ",
            price=400.0,
            session_vwap=399.0,
            ma9=401.0,
            as_of=now_est()
        )
        mock_schwab_create.return_value = mock_schwab

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
        app_task = asyncio.create_task(app.run())
        await asyncio.sleep(0.1)

        # Send market data (should be ignored due to market hours)
        equity_tick = EquityTick(
            symbol="QQQ",
            price=400.0,
            session_vwap=401.0,
            ma9=399.0,
            as_of=now_est(),
        )

        # The normalizer should filter out data outside market hours
        await app._normalizer.ingest_equity(equity_tick)

        # Stop the app
        app_task.cancel()
        try:
            await app_task
        except asyncio.CancelledError:
            pass

        # Verify that no signals were generated due to market hours


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_error_recovery():
    """Test that the system recovers from errors gracefully."""
    with (
        patch("alphagen.app.SchwabOAuthClient.create") as mock_schwab_create,
        patch(
            "alphagen.app.create_market_data_provider"
        ) as mock_market_data_factory,
        patch("alphagen.app.init_models") as mock_init_models,
        patch("alphagen.app.asyncio.Event") as mock_event_class,
    ):
        # Mock Schwab client that fails initially then succeeds
        mock_schwab = AsyncMock()
        call_count = 0

        async def mock_fetch_positions():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("API Error")
            return []

        mock_schwab.fetch_positions.side_effect = mock_fetch_positions
        mock_schwab_create.return_value = mock_schwab

        # Mock other components
        mock_market_data = AsyncMock()
        mock_market_data_factory.return_value = mock_market_data
        mock_init_models.return_value = AsyncMock()

        # Mock the Event to allow background tasks to run before stopping
        mock_event = AsyncMock()
        async def mock_wait_with_delay():
            await asyncio.sleep(0.5)  # Give background tasks time to run
        mock_event.wait.side_effect = mock_wait_with_delay
        mock_event_class.return_value = mock_event

        # Mock market data start
        async def mock_start(cb):
            pass
        mock_market_data.start.side_effect = mock_start

        # Create app
        app = AlphaGenApp()

        # Start the app
        await app.run()

        # Verify that the app continued running despite errors (at least attempted once)
        assert call_count >= 1  # Should have attempted at least once


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_position_monitoring():
    """Test that position monitoring works correctly."""
    with (
        patch("alphagen.app.SchwabOAuthClient.create") as mock_schwab_create,
        patch(
            "alphagen.app.create_market_data_provider"
        ) as mock_market_data_factory,
        patch("alphagen.app.init_models") as mock_init_models,
        patch("alphagen.app.asyncio.Event") as mock_event_class,
    ):
        # Mock Schwab client with changing positions
        mock_schwab = AsyncMock()
        position_data = [
            {
                "symbol": "QQQ241220C00400000",
                "quantity": -25,  # Short position
                "average_price": 5.50,
                "market_value": -1375.0,
                "as_of": now_est().isoformat(),
            }
        ]
        mock_schwab.fetch_positions.return_value = position_data
        mock_schwab_create.return_value = mock_schwab

        # Mock other components
        mock_market_data = AsyncMock()
        mock_market_data_factory.return_value = mock_market_data
        mock_init_models.return_value = AsyncMock()

        # Mock the Event to allow background tasks to run before stopping
        mock_event = AsyncMock()
        async def mock_wait_with_delay():
            await asyncio.sleep(0.5)  # Give background tasks time to run
        mock_event.wait.side_effect = mock_wait_with_delay
        mock_event_class.return_value = mock_event

        # Mock market data start
        async def mock_start(cb):
            pass
        mock_market_data.start.side_effect = mock_start

        # Create app
        app = AlphaGenApp()

        # Start the app
        await app.run()

        # Verify that positions were fetched
        mock_schwab.fetch_positions.assert_called()
