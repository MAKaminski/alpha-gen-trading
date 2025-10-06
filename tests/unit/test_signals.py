"""Unit tests for signal generation logic."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

from alphagen.signals import SignalEngine
from alphagen.core.events import NormalizedTick, EquityTick, OptionQuote
from alphagen.core.time_utils import now_est


@pytest.mark.asyncio
async def test_signal_engine_initialization():
    """Test signal engine initializes correctly."""
    emit_callback = AsyncMock()
    engine = SignalEngine(emit=emit_callback)
    
    assert engine._last_diff is None
    assert not engine._cooldown_state.active(now_est())


@pytest.mark.asyncio
async def test_signal_generation_vwap_ma9_crossover():
    """Test signal generation when VWAP crosses above MA9."""
    emit_callback = AsyncMock()
    engine = SignalEngine(emit=emit_callback)
    
    # Create test data with VWAP crossing above MA9
    current_time = now_est()
    
    # First tick: VWAP below MA9
    tick1 = NormalizedTick(
        as_of=current_time,
        equity=EquityTick("QQQ", 400.0, 399.0, 401.0, current_time),
        option=OptionQuote("QQQ241220C00400000", 400.0, 5.50, 5.75, current_time, current_time),
    )
    
    # Second tick: VWAP crosses above MA9
    tick2 = NormalizedTick(
        as_of=current_time + timedelta(seconds=1),
        equity=EquityTick("QQQ", 400.0, 401.0, 399.0, current_time + timedelta(seconds=1)),
        option=OptionQuote("QQQ241220C00400000", 400.0, 5.50, 5.75, current_time, current_time),
    )
    
    # Process first tick (should not generate signal)
    await engine.handle_tick(tick1)
    emit_callback.assert_not_called()
    
    # Process second tick (should generate signal)
    await engine.handle_tick(tick2)
    emit_callback.assert_called_once()
    
    # Verify signal properties
    call_args = emit_callback.call_args[0][0]
    assert call_args.action == "SELL_TO_OPEN"
    assert call_args.option_symbol == "QQQ241220C00400000"
    assert "VWAP/MA9 crossover detected" in call_args.rationale


@pytest.mark.asyncio
async def test_signal_generation_ma9_vwap_crossover():
    """Test signal generation when MA9 crosses above VWAP."""
    emit_callback = AsyncMock()
    engine = SignalEngine(emit=emit_callback)
    
    current_time = now_est()
    
    # First tick: VWAP above MA9
    tick1 = NormalizedTick(
        as_of=current_time,
        equity=EquityTick("QQQ", 400.0, 401.0, 399.0, current_time),
        option=OptionQuote("QQQ241220C00400000", 400.0, 5.50, 5.75, current_time, current_time),
    )
    
    # Second tick: MA9 crosses above VWAP
    tick2 = NormalizedTick(
        as_of=current_time + timedelta(seconds=1),
        equity=EquityTick("QQQ", 400.0, 399.0, 401.0, current_time + timedelta(seconds=1)),
        option=OptionQuote("QQQ241220C00400000", 400.0, 5.50, 5.75, current_time, current_time),
    )
    
    await engine.handle_tick(tick1)
    await engine.handle_tick(tick2)
    
    emit_callback.assert_called_once()
    call_args = emit_callback.call_args[0][0]
    assert call_args.action == "SELL_PUT_TO_OPEN"


@pytest.mark.asyncio
async def test_cooldown_prevents_multiple_signals():
    """Test that cooldown prevents multiple signals within the cooldown period."""
    emit_callback = AsyncMock()
    engine = SignalEngine(emit=emit_callback)
    
    current_time = now_est()
    
    # First tick: VWAP below MA9
    tick1 = NormalizedTick(
        as_of=current_time,
        equity=EquityTick("QQQ", 400.0, 399.0, 401.0, current_time),
        option=OptionQuote("QQQ241220C00400000", 400.0, 5.50, 5.75, current_time, current_time),
    )
    
    # Second tick: VWAP crosses above MA9 (generates signal)
    tick2 = NormalizedTick(
        as_of=current_time + timedelta(seconds=1),
        equity=EquityTick("QQQ", 400.0, 401.0, 399.0, current_time + timedelta(seconds=1)),
        option=OptionQuote("QQQ241220C00400000", 400.0, 5.50, 5.75, current_time, current_time),
    )
    
    # Process first tick (no signal, just sets baseline)
    await engine.handle_tick(tick1)
    assert emit_callback.call_count == 0
    
    # Process second tick (generates signal due to crossover)
    await engine.handle_tick(tick2)
    assert emit_callback.call_count == 1
    
    # Process another tick immediately (should not generate signal due to cooldown)
    tick3 = NormalizedTick(
        as_of=current_time + timedelta(seconds=2),
        equity=EquityTick("QQQ", 400.0, 402.0, 398.0, current_time + timedelta(seconds=2)),
        option=OptionQuote("QQQ241220C00400000", 400.0, 5.50, 5.75, current_time, current_time),
    )
    
    await engine.handle_tick(tick3)
    assert emit_callback.call_count == 1  # Still only one call


@pytest.mark.asyncio
async def test_no_signal_without_option():
    """Test that no signal is generated when there's no option data."""
    emit_callback = AsyncMock()
    engine = SignalEngine(emit=emit_callback)
    
    current_time = now_est()
    
    tick = NormalizedTick(
        as_of=current_time,
        equity=EquityTick("QQQ", 400.0, 401.0, 399.0, current_time),
        option=None,  # No option data
    )
    
    await engine.handle_tick(tick)
    emit_callback.assert_not_called()


def test_cooldown_state_management():
    """Test cooldown state management."""
    from alphagen.core.events import CooldownState
    from datetime import timedelta
    
    # Test expired cooldown
    expired = CooldownState.expired()
    assert not expired.active(now_est())
    
    # Test active cooldown
    future_time = now_est() + timedelta(seconds=30)
    active = CooldownState(until=future_time)
    assert active.active(now_est())
    
    # Test extending cooldown
    extended = active.extend(timedelta(seconds=60))
    assert extended.until > active.until
