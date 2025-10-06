"""Comprehensive tests for trade_manager module."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from src.alphagen.trade_manager import TradeManager
from src.alphagen.core.events import (
    NormalizedTick,
    EquityTick,
    OptionQuote,
    TradeIntent,
    TradeExecution,
)
from src.alphagen.config import EST


class TestTradeManagerComprehensive:
    """Comprehensive tests for TradeManager."""

    @pytest.fixture
    def mock_schwab_client(self):
        """Create a mock Schwab client."""
        client = AsyncMock()
        client.submit_order = AsyncMock()
        return client

    @pytest.fixture
    def mock_option_monitor(self):
        """Create a mock option monitor."""
        monitor = MagicMock()
        monitor.track = MagicMock()
        return monitor

    @pytest.fixture
    def mock_emit_execution(self):
        """Create a mock emit_execution function."""
        return AsyncMock()

    @pytest.fixture
    def trade_manager(
        self, mock_emit_execution, mock_schwab_client, mock_option_monitor
    ):
        """Create a TradeManager instance."""
        return TradeManager(
            emit_execution=mock_emit_execution,
            schwab_client=mock_schwab_client,
            option_monitor=mock_option_monitor,
        )

    @pytest.fixture
    def sample_tick(self):
        """Create a sample NormalizedTick."""
        as_of = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        equity = EquityTick(
            symbol="QQQ", price=400.0, session_vwap=399.5, ma9=398.0, as_of=as_of
        )
        option = OptionQuote(
            option_symbol="QQQ240119C00400000",
            strike=400.0,
            bid=2.50,
            ask=2.75,
            expiry=datetime(2024, 1, 19, 16, 0, 0, tzinfo=EST),
            as_of=as_of,
        )
        return NormalizedTick(as_of=as_of, equity=equity, option=option)

    @pytest.fixture
    def sample_intent(self):
        """Create a sample TradeIntent."""
        as_of = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        return TradeIntent(
            as_of=as_of,
            action="SELL_TO_OPEN",
            option_symbol="QQQ240119C00400000",
            quantity=10,
            limit_price=2.60,
            stop_loss=3.00,
            take_profit=2.20,
        )

    @pytest.mark.asyncio
    async def test_handle_intent_rollover_existing_position(
        self, trade_manager, sample_intent
    ):
        """Test handle_intent closes existing position when same symbol."""
        # Set up existing position
        existing_execution = TradeExecution(
            order_id="12345",
            status="FILLED",
            fill_price=2.58,
            pnl_contrib=0.20,
            as_of=datetime(2024, 1, 15, 9, 0, 0, tzinfo=EST),
            intent=sample_intent,
        )
        trade_manager._open_positions[sample_intent.option_symbol] = existing_execution

        # Mock the _close_position method
        trade_manager._close_position = AsyncMock()

        await trade_manager.handle_intent(sample_intent)

        # Should close existing position first
        trade_manager._close_position.assert_called_once_with(
            sample_intent.option_symbol, reason="rollover"
        )

    @pytest.mark.asyncio
    async def test_handle_tick_with_option_updates_quote(
        self, trade_manager, sample_tick
    ):
        """Test handle_tick with option updates the quote."""
        trade_manager.update_option_quote = AsyncMock()

        await trade_manager.handle_tick(sample_tick)

        trade_manager.update_option_quote.assert_called_once_with(sample_tick.option)

    @pytest.mark.asyncio
    async def test_handle_tick_without_option_does_nothing(self, trade_manager):
        """Test handle_tick without option does nothing."""
        as_of = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        equity = EquityTick(
            symbol="QQQ", price=400.0, session_vwap=399.5, ma9=398.0, as_of=as_of
        )
        tick = NormalizedTick(as_of=as_of, equity=equity, option=None)

        trade_manager.update_option_quote = AsyncMock()

        await trade_manager.handle_tick(tick)

        trade_manager.update_option_quote.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_option_quote_stores_quote(self, trade_manager, sample_tick):
        """Test update_option_quote stores the quote."""
        await trade_manager.update_option_quote(sample_tick.option)

        assert sample_tick.option.option_symbol in trade_manager._last_quotes
        assert (
            trade_manager._last_quotes[sample_tick.option.option_symbol]
            == sample_tick.option
        )

    @pytest.mark.asyncio
    async def test_update_option_quote_checks_exit_conditions(
        self, trade_manager, sample_tick
    ):
        """Test update_option_quote checks exit conditions for open positions."""
        # Set up an open position
        execution = TradeExecution(
            order_id="12345",
            status="FILLED",
            fill_price=2.58,
            pnl_contrib=0.20,
            as_of=datetime(2024, 1, 15, 9, 0, 0, tzinfo=EST),
            intent=TradeIntent(
                as_of=datetime(2024, 1, 15, 9, 0, 0, tzinfo=EST),
                action="SELL_TO_OPEN",
                option_symbol=sample_tick.option.option_symbol,
                quantity=10,
                limit_price=2.60,
                stop_loss=3.00,
                take_profit=2.20,
            ),
        )
        trade_manager._open_positions[sample_tick.option.option_symbol] = execution

        # Mock the _evaluate_exits method
        trade_manager._evaluate_exits = AsyncMock()

        await trade_manager.update_option_quote(sample_tick.option)

        trade_manager._evaluate_exits.assert_called_once_with(
            sample_tick.option.option_symbol,
            sample_tick.option.mid(),
            sample_tick.as_of,
        )

    @pytest.mark.asyncio
    async def test_evaluate_exits_take_profit(self, trade_manager, sample_intent):
        """Test _evaluate_exits triggers take profit exit."""
        # Set up position with take profit condition
        execution = TradeExecution(
            order_id="12345",
            status="FILLED",
            fill_price=2.58,
            pnl_contrib=0.20,
            as_of=datetime(2024, 1, 15, 9, 0, 0, tzinfo=EST),
            intent=sample_intent,
        )
        trade_manager._open_positions[sample_intent.option_symbol] = execution

        # Mock _close_position
        trade_manager._close_position = AsyncMock()

        # Price below take profit should trigger exit
        await trade_manager._evaluate_exits(
            sample_intent.option_symbol,
            sample_intent.take_profit - 0.1,  # Below take profit
            datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST),
        )

        trade_manager._close_position.assert_called_once_with(
            sample_intent.option_symbol,
            price=sample_intent.take_profit - 0.1,
            reason="take-profit",
        )

    @pytest.mark.asyncio
    async def test_evaluate_exits_stop_loss(self, trade_manager, sample_intent):
        """Test _evaluate_exits triggers stop loss exit."""
        # Set up position with stop loss condition
        execution = TradeExecution(
            order_id="12345",
            status="FILLED",
            fill_price=2.58,
            pnl_contrib=0.20,
            as_of=datetime(2024, 1, 15, 9, 0, 0, tzinfo=EST),
            intent=sample_intent,
        )
        trade_manager._open_positions[sample_intent.option_symbol] = execution

        # Mock _close_position
        trade_manager._close_position = AsyncMock()

        # Price above stop loss should trigger exit
        await trade_manager._evaluate_exits(
            sample_intent.option_symbol,
            sample_intent.stop_loss + 0.1,  # Above stop loss
            datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST),
        )

        trade_manager._close_position.assert_called_once_with(
            sample_intent.option_symbol,
            price=sample_intent.stop_loss + 0.1,
            reason="stop-loss",
        )

    @pytest.mark.asyncio
    async def test_evaluate_exits_session_close(self, trade_manager, sample_intent):
        """Test _evaluate_exits triggers session close exit."""
        # Set up position
        execution = TradeExecution(
            order_id="12345",
            status="FILLED",
            fill_price=2.58,
            pnl_contrib=0.20,
            as_of=datetime(2024, 1, 15, 9, 0, 0, tzinfo=EST),
            intent=sample_intent,
        )
        trade_manager._open_positions[sample_intent.option_symbol] = execution

        # Mock _close_position
        trade_manager._close_position = AsyncMock()

        # Time after session end should trigger exit
        session_end = datetime(2024, 1, 15, 16, 30, 0, tzinfo=EST)  # After market close
        await trade_manager._evaluate_exits(
            sample_intent.option_symbol,
            2.60,  # Normal price
            session_end,
        )

        trade_manager._close_position.assert_called_once_with(
            sample_intent.option_symbol, price=2.60, reason="session-close"
        )

    @pytest.mark.asyncio
    async def test_evaluate_exits_no_exit(self, trade_manager, sample_intent):
        """Test _evaluate_exits does not exit when conditions not met."""
        # Set up position
        execution = TradeExecution(
            order_id="12345",
            status="FILLED",
            fill_price=2.58,
            pnl_contrib=0.20,
            as_of=datetime(2024, 1, 15, 9, 0, 0, tzinfo=EST),
            intent=sample_intent,
        )
        trade_manager._open_positions[sample_intent.option_symbol] = execution

        # Mock _close_position
        trade_manager._close_position = AsyncMock()

        # Normal price and time should not trigger exit
        await trade_manager._evaluate_exits(
            sample_intent.option_symbol,
            2.60,  # Normal price
            datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST),  # Normal time
        )

        trade_manager._close_position.assert_not_called()

    @pytest.mark.asyncio
    async def test_close_all_closes_all_positions(self, trade_manager):
        """Test close_all closes all open positions."""
        # Set up multiple positions
        symbol1 = "QQQ240119C00400000"
        symbol2 = "QQQ240119P00395000"
        trade_manager._open_positions[symbol1] = MagicMock()
        trade_manager._open_positions[symbol2] = MagicMock()

        # Mock _close_position
        trade_manager._close_position = AsyncMock()

        await trade_manager.close_all(reason="manual")

        # Should close both positions
        assert trade_manager._close_position.call_count == 2
        trade_manager._close_position.assert_any_call(symbol1, reason="manual")
        trade_manager._close_position.assert_any_call(symbol2, reason="manual")

    @pytest.mark.asyncio
    async def test_close_position_with_nonexistent_symbol(self, trade_manager):
        """Test _close_position with nonexistent symbol does nothing."""
        trade_manager.emit_execution = AsyncMock()

        await trade_manager._close_position("NONEXISTENT", reason="manual")

        trade_manager.emit_execution.assert_not_called()

    @pytest.mark.asyncio
    async def test_close_position_with_existing_position(
        self, trade_manager, sample_intent
    ):
        """Test _close_position with existing position closes it."""
        # Set up position
        execution = TradeExecution(
            order_id="12345",
            status="FILLED",
            fill_price=2.58,
            pnl_contrib=0.20,
            as_of=datetime(2024, 1, 15, 9, 0, 0, tzinfo=EST),
            intent=sample_intent,
        )
        trade_manager._open_positions[sample_intent.option_symbol] = execution

        # Mock the schwab client to return a closing execution
        closing_execution = TradeExecution(
            order_id="67890",
            status="FILLED",
            fill_price=2.50,
            pnl_contrib=0.0,
            as_of=datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST),
            intent=sample_intent,
        )
        trade_manager.schwab_client.submit_order = AsyncMock(
            return_value=closing_execution
        )

        # Mock emit_execution
        trade_manager.emit_execution = AsyncMock()

        await trade_manager._close_position(
            sample_intent.option_symbol, price=2.50, reason="manual"
        )

        # Should remove from open positions
        assert sample_intent.option_symbol not in trade_manager._open_positions

        # Should emit execution
        trade_manager.emit_execution.assert_called_once()
        call_args = trade_manager.emit_execution.call_args[0][0]
        assert call_args.status == "FILLED"
        assert call_args.fill_price == 2.50
