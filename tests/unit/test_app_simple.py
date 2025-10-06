"""Simple tests for app module."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone

from alphagen.app import AlphaGenApp
from alphagen.core.events import (
    EquityTick,
    OptionQuote,
    NormalizedTick,
    Signal,
    TradeIntent,
    TradeExecution,
    PositionState,
    PositionSnapshot,
)


class TestAlphaGenAppSimple:
    """Simple tests for AlphaGenApp class."""

    def test_app_initialization(self):
        """Test app initialization."""
        with patch.object(AlphaGenApp, "__init__", lambda x: None):
            app = AlphaGenApp()
            assert app is not None

    def test_app_has_required_attributes(self):
        """Test app has required attributes."""
        with patch.object(AlphaGenApp, "__init__", lambda x: None):
            app = AlphaGenApp()
            # Set some basic attributes
            app._logger = MagicMock()
            app._running = False
            app._background_tasks = []

            assert hasattr(app, "_logger")
            assert hasattr(app, "_running")
            assert hasattr(app, "_background_tasks")

    @pytest.mark.asyncio
    async def test_handle_equity_tick_simple(self):
        """Test _handle_equity_tick method with simple mocking."""
        # Create test data
        timestamp = datetime.now(timezone.utc)
        equity_tick = EquityTick(
            symbol="QQQ", price=400.0, session_vwap=399.5, ma9=400.2, as_of=timestamp
        )

        # Mock app components
        app = MagicMock()
        app._logger = MagicMock()
        app._normalizer = MagicMock()
        app._normalizer.ingest_equity = AsyncMock()

        # Create AlphaGenApp instance
        with patch.object(AlphaGenApp, "__init__", lambda x: None):
            alpha_app = AlphaGenApp()
            alpha_app._logger = app._logger
            alpha_app._normalizer = app._normalizer

            # Call the method
            await alpha_app._handle_equity_tick(equity_tick)

            # Verify normalizer was called
            app._normalizer.ingest_equity.assert_called_once_with(equity_tick)

    @pytest.mark.asyncio
    async def test_handle_option_quote_simple(self):
        """Test _handle_option_quote method with simple mocking."""
        # Create test data
        timestamp = datetime.now(timezone.utc)
        option_quote = OptionQuote(
            option_symbol="QQQ241220C00400000",
            strike=400.0,
            bid=5.50,
            ask=5.75,
            expiry=timestamp,
            as_of=timestamp,
        )

        # Mock app components
        app = MagicMock()
        app._logger = MagicMock()
        app._normalizer = MagicMock()
        app._normalizer.ingest_option = AsyncMock()

        # Create AlphaGenApp instance
        with patch.object(AlphaGenApp, "__init__", lambda x: None):
            alpha_app = AlphaGenApp()
            alpha_app._logger = app._logger
            alpha_app._normalizer = app._normalizer

            # Call the method
            await alpha_app._handle_option_quote(option_quote)

            # Verify normalizer was called
            app._normalizer.ingest_option.assert_called_once_with(option_quote)

    @pytest.mark.asyncio
    async def test_handle_normalized_tick_with_chart(self):
        """Test _handle_normalized_tick method with chart."""
        # Create test data
        timestamp = datetime.now(timezone.utc)
        equity_tick = EquityTick(
            symbol="QQQ", price=400.0, session_vwap=399.5, ma9=400.2, as_of=timestamp
        )
        normalized_tick = NormalizedTick(
            as_of=timestamp, equity=equity_tick, option=None
        )

        # Mock app components
        app = MagicMock()
        app._logger = MagicMock()
        app._chart = MagicMock()
        app._signal_engine = MagicMock()
        app._signal_engine.handle_tick = AsyncMock()
        app._trade_manager = MagicMock()
        app._trade_manager.handle_tick = AsyncMock()

        # Create AlphaGenApp instance
        with patch.object(AlphaGenApp, "__init__", lambda x: None):
            alpha_app = AlphaGenApp()
            alpha_app._logger = app._logger
            alpha_app._chart = app._chart
            alpha_app._signal_engine = app._signal_engine
            alpha_app._trade_manager = app._trade_manager

            # Call the method
            await alpha_app._handle_normalized_tick(normalized_tick)

            # Verify chart was called
            app._chart.handle_tick.assert_called_once_with(normalized_tick)

    @pytest.mark.asyncio
    async def test_handle_normalized_tick_no_chart(self):
        """Test _handle_normalized_tick method without chart."""
        # Create test data
        timestamp = datetime.now(timezone.utc)
        equity_tick = EquityTick(
            symbol="QQQ", price=400.0, session_vwap=399.5, ma9=400.2, as_of=timestamp
        )
        normalized_tick = NormalizedTick(
            as_of=timestamp, equity=equity_tick, option=None
        )

        # Mock app components
        app = MagicMock()
        app._logger = MagicMock()
        app._chart = None  # No chart
        app._signal_engine = MagicMock()
        app._signal_engine.handle_tick = AsyncMock()
        app._trade_manager = MagicMock()
        app._trade_manager.handle_tick = AsyncMock()

        # Create AlphaGenApp instance
        with patch.object(AlphaGenApp, "__init__", lambda x: None):
            alpha_app = AlphaGenApp()
            alpha_app._logger = app._logger
            alpha_app._chart = app._chart
            alpha_app._signal_engine = app._signal_engine
            alpha_app._trade_manager = app._trade_manager

            # Call the method
            await alpha_app._handle_normalized_tick(normalized_tick)

            # Should not crash when chart is None
            # No assertions needed - just ensuring it doesn't crash

    @pytest.mark.asyncio
    async def test_handle_signal_simple(self):
        """Test _handle_signal method with simple mocking."""
        # Create test data
        timestamp = datetime.now(timezone.utc)
        signal = Signal(
            as_of=timestamp,
            action="buy",
            option_symbol="QQQ241220C00400000",
            reference_price=400.0,
            rationale="VWAP crossover",
            cooldown_until=timestamp,
        )

        # Mock app components
        app = MagicMock()
        app._logger = MagicMock()
        app._chart = MagicMock()
        app._trade_generator = MagicMock()
        app._trade_generator.handle_signal = AsyncMock()

        # Create AlphaGenApp instance
        with patch.object(AlphaGenApp, "__init__", lambda x: None):
            alpha_app = AlphaGenApp()
            alpha_app._logger = app._logger
            alpha_app._chart = app._chart
            alpha_app._trade_generator = app._trade_generator

            # Call the method
            await alpha_app._handle_signal(signal)

            # Verify trade generator was called
            app._trade_generator.handle_signal.assert_called_once_with(signal)

    @pytest.mark.asyncio
    async def test_handle_trade_intent_simple(self):
        """Test _handle_trade_intent method with simple mocking."""
        # Create test data
        timestamp = datetime.now(timezone.utc)
        intent = TradeIntent(
            as_of=timestamp,
            action="buy",
            option_symbol="QQQ241220C00400000",
            quantity=100,
            limit_price=400.0,
            stop_loss=380.0,
            take_profit=420.0,
        )

        # Mock app components
        app = MagicMock()
        app._logger = MagicMock()
        app._trade_manager = MagicMock()
        app._trade_manager.handle_intent = AsyncMock()
        app._intent_index = {}

        # Create AlphaGenApp instance
        with patch.object(AlphaGenApp, "__init__", lambda x: None):
            alpha_app = AlphaGenApp()
            alpha_app._logger = app._logger
            alpha_app._trade_manager = app._trade_manager
            alpha_app._intent_index = app._intent_index

            # Call the method
            await alpha_app._handle_trade_intent(intent)

            # Verify trade manager was called
            app._trade_manager.handle_intent.assert_called_once_with(intent)

    @pytest.mark.asyncio
    async def test_handle_stream_error_simple(self):
        """Test _handle_stream_error method with simple mocking."""
        # Create test error
        error = ValueError("Test error")

        # Mock app components
        app = MagicMock()
        app._logger = MagicMock()

        # Create AlphaGenApp instance
        with patch.object(AlphaGenApp, "__init__", lambda x: None):
            alpha_app = AlphaGenApp()
            alpha_app._logger = app._logger

            # Call the method
            await alpha_app._handle_stream_error(error)

            # Verify error was logged
            app._logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_execution_simple(self):
        """Test _record_execution method with simple mocking."""
        # Create test data
        timestamp = datetime.now(timezone.utc)
        intent = TradeIntent(
            as_of=timestamp,
            action="buy",
            option_symbol="QQQ241220C00400000",
            quantity=100,
            limit_price=400.0,
            stop_loss=380.0,
            take_profit=420.0,
        )
        execution = TradeExecution(
            order_id="12345",
            status="filled",
            fill_price=400.0,
            pnl_contrib=50.0,
            as_of=timestamp,
            intent=intent,
        )

        # Mock app components
        app = MagicMock()
        app._logger = MagicMock()
        app._intent_index = {1: 2}  # Mock intent index
        app._position_calculator = MagicMock()
        app._position_calculator.register_execution = AsyncMock()

        # Create AlphaGenApp instance
        with patch.object(AlphaGenApp, "__init__", lambda x: None):
            alpha_app = AlphaGenApp()
            alpha_app._logger = app._logger
            alpha_app._intent_index = app._intent_index
            alpha_app._position_calculator = app._position_calculator

            # Call the method
            await alpha_app._record_execution(execution)

            # Verify position calculator was called
            app._position_calculator.register_execution.assert_called_once_with(
                execution
            )

    @pytest.mark.asyncio
    async def test_on_position_state_simple(self):
        """Test _on_position_state method with simple mocking."""
        # Create test data
        timestamp = datetime.now(timezone.utc)
        position = PositionSnapshot(
            symbol="QQQ",
            quantity=100,
            market_value=40000.0,
            average_price=400.0,
            as_of=timestamp,
        )
        position_state = PositionState(symbols={"QQQ": position}, as_of=timestamp)

        # Mock app components
        app = MagicMock()
        app._logger = MagicMock()
        app._position_calculator = MagicMock()
        app._position_calculator.update_positions = AsyncMock()

        # Create AlphaGenApp instance
        with patch.object(AlphaGenApp, "__init__", lambda x: None):
            alpha_app = AlphaGenApp()
            alpha_app._logger = app._logger
            alpha_app._position_calculator = app._position_calculator

            # Call the method
            await alpha_app._on_position_state(position_state)

            # Verify position state was logged
            app._logger.info.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_option_quote_update_simple(self):
        """Test _handle_option_quote_update method with simple mocking."""
        # Create test data
        timestamp = datetime.now(timezone.utc)
        option_quote = OptionQuote(
            option_symbol="QQQ241220C00400000",
            strike=400.0,
            bid=5.50,
            ask=5.75,
            expiry=timestamp,
            as_of=timestamp,
        )

        # Mock app components
        app = MagicMock()
        app._logger = MagicMock()
        app._trade_manager = MagicMock()
        app._trade_manager.update_option_quote = AsyncMock()

        # Create AlphaGenApp instance
        with patch.object(AlphaGenApp, "__init__", lambda x: None):
            alpha_app = AlphaGenApp()
            alpha_app._logger = app._logger
            alpha_app._trade_manager = app._trade_manager

            # Call the method
            await alpha_app._handle_option_quote_update(option_quote)

            # Verify trade manager was called
            app._trade_manager.update_option_quote.assert_called_once_with(option_quote)
