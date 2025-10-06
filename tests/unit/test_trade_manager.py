"""Unit tests for trade management logic."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from alphagen.trade_manager import TradeManager
from alphagen.core.events import TradeIntent, TradeExecution, NormalizedTick, EquityTick, OptionQuote
from alphagen.core.time_utils import now_est


@pytest.fixture
def mock_emit_execution():
    """Create a mock execution emitter."""
    return AsyncMock()


@pytest.fixture
def mock_schwab_client():
    """Create a mock Schwab client."""
    client = AsyncMock()
    client.submit_order.return_value = TradeExecution(
        order_id="test_order_123",
        status="submitted",
        fill_price=5.50,
        pnl_contrib=0.0,
        as_of=now_est(),
        intent=TradeIntent(
            as_of=now_est(),
            action="SELL_TO_OPEN",
            option_symbol="QQQ241220C00400000",
            quantity=25,
            limit_price=5.50,
            stop_loss=11.00,
            take_profit=2.75,
        ),
    )
    return client


@pytest.fixture
def mock_option_monitor():
    """Create a mock option monitor."""
    monitor = MagicMock()
    monitor.track = MagicMock()
    monitor.untrack = MagicMock()
    return monitor


@pytest.fixture
def trade_manager(mock_emit_execution, mock_schwab_client, mock_option_monitor):
    """Create a trade manager for testing."""
    return TradeManager(
        emit_execution=mock_emit_execution,
        schwab_client=mock_schwab_client,
        option_monitor=mock_option_monitor,
    )


@pytest.mark.asyncio
async def test_trade_manager_initialization(trade_manager):
    """Test trade manager initializes correctly."""
    assert trade_manager._open_positions == {}
    assert trade_manager._last_quotes == {}


@pytest.mark.asyncio
async def test_handle_intent_opens_position(trade_manager, mock_emit_execution):
    """Test handling a trade intent opens a position."""
    intent = TradeIntent(
        as_of=now_est(),
        action="SELL_TO_OPEN",
        option_symbol="QQQ241220C00400000",
        quantity=25,
        limit_price=5.50,
        stop_loss=11.00,
        take_profit=2.75,
    )
    
    await trade_manager.handle_intent(intent)
    
    # Verify position was opened
    assert "QQQ241220C00400000" in trade_manager._open_positions
    mock_emit_execution.assert_called_once()
    trade_manager.option_monitor.track.assert_called_once_with("QQQ241220C00400000")


@pytest.mark.asyncio
async def test_single_position_rule(trade_manager, mock_emit_execution):
    """Test that single position rule prevents multiple positions."""
    # Open first position
    intent1 = TradeIntent(
        as_of=now_est(),
        action="SELL_TO_OPEN",
        option_symbol="QQQ241220C00400000",
        quantity=25,
        limit_price=5.50,
        stop_loss=11.00,
        take_profit=2.75,
    )
    
    await trade_manager.handle_intent(intent1)
    
    # Try to open second position (should be blocked)
    intent2 = TradeIntent(
        as_of=now_est(),
        action="SELL_TO_OPEN",
        option_symbol="QQQ241220C00400001",  # Different symbol
        quantity=25,
        limit_price=5.50,
        stop_loss=11.00,
        take_profit=2.75,
    )
    
    await trade_manager.handle_intent(intent2)
    
    # Should still only have one position
    assert len(trade_manager._open_positions) == 1
    assert "QQQ241220C00400000" in trade_manager._open_positions
    assert "QQQ241220C00400001" not in trade_manager._open_positions


@pytest.mark.asyncio
async def test_take_profit_exit(trade_manager, mock_emit_execution):
    """Test position exit on take profit."""
    # Open position
    intent = TradeIntent(
        as_of=now_est(),
        action="SELL_TO_OPEN",
        option_symbol="QQQ241220C00400000",
        quantity=25,
        limit_price=5.50,
        stop_loss=11.00,
        take_profit=2.75,  # 50% of entry credit
    )
    
    await trade_manager.handle_intent(intent)
    
    # Create quote that triggers take profit
    quote = OptionQuote(
        option_symbol="QQQ241220C00400000",
        strike=400.0,
        bid=2.50,  # Below take profit level
        ask=2.75,
        expiry=now_est() + timedelta(hours=1),
        as_of=now_est(),
    )
    
    await trade_manager.update_option_quote(quote)
    
    # Position should be closed
    assert "QQQ241220C00400000" not in trade_manager._open_positions
    assert mock_emit_execution.call_count == 2  # One for open, one for close


@pytest.mark.asyncio
async def test_stop_loss_exit(trade_manager, mock_emit_execution):
    """Test position exit on stop loss."""
    # Open position
    intent = TradeIntent(
        as_of=now_est(),
        action="SELL_TO_OPEN",
        option_symbol="QQQ241220C00400000",
        quantity=25,
        limit_price=5.50,
        stop_loss=11.00,  # 200% of entry credit
        take_profit=2.75,
    )
    
    await trade_manager.handle_intent(intent)
    
    # Create quote that triggers stop loss
    quote = OptionQuote(
        option_symbol="QQQ241220C00400000",
        strike=400.0,
        bid=11.50,  # Above stop loss level
        ask=12.00,
        expiry=now_est() + timedelta(hours=1),
        as_of=now_est(),
    )
    
    await trade_manager.update_option_quote(quote)
    
    # Position should be closed
    assert "QQQ241220C00400000" not in trade_manager._open_positions
    assert mock_emit_execution.call_count == 2  # One for open, one for close


@pytest.mark.asyncio
async def test_pnl_calculation(trade_manager):
    """Test P&L calculation for closed positions."""
    # Create entry execution
    entry_intent = TradeIntent(
        as_of=now_est(),
        action="SELL_TO_OPEN",
        option_symbol="QQQ241220C00400000",
        quantity=25,
        limit_price=5.50,
        stop_loss=11.00,
        take_profit=2.75,
    )
    
    entry_execution = TradeExecution(
        order_id="entry_123",
        status="filled",
        fill_price=5.50,
        pnl_contrib=0.0,
        as_of=now_est(),
        intent=entry_intent,
    )
    
    # Create exit execution
    exit_intent = TradeIntent(
        as_of=now_est(),
        action="BUY_TO_CLOSE",
        option_symbol="QQQ241220C00400000",
        quantity=25,
        limit_price=2.75,
        stop_loss=0.0,
        take_profit=0.0,
    )
    
    exit_execution = TradeExecution(
        order_id="exit_123",
        status="filled",
        fill_price=2.75,
        pnl_contrib=0.0,
        as_of=now_est(),
        intent=exit_intent,
    )
    
    # Calculate P&L
    pnl = trade_manager._calculate_pnl(entry_execution, exit_execution)
    
    # For a short position: (entry_price - exit_price) * quantity * multiplier
    # (5.50 - 2.75) * 25 * 100 = 6,875
    expected_pnl = (5.50 - 2.75) * 25 * 100
    assert pnl == expected_pnl


@pytest.mark.asyncio
async def test_close_all_positions(trade_manager, mock_emit_execution):
    """Test closing all positions."""
    # Open a position
    intent = TradeIntent(
        as_of=now_est(),
        action="SELL_TO_OPEN",
        option_symbol="QQQ241220C00400000",
        quantity=25,
        limit_price=5.50,
        stop_loss=11.00,
        take_profit=2.75,
    )
    
    await trade_manager.handle_intent(intent)
    
    # Close all positions
    await trade_manager.close_all(reason="manual")
    
    # Position should be closed
    assert len(trade_manager._open_positions) == 0
    assert mock_emit_execution.call_count == 2  # One for open, one for close
