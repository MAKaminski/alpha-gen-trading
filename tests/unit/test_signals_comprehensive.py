"""Comprehensive tests for signals module."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

from alphagen.signals import SignalEngine
from alphagen.core.events import NormalizedTick, EquityTick, OptionQuote, Signal
from alphagen.config import EST


class TestSignalEngineComprehensive:
    """Comprehensive tests for SignalEngine."""

    @pytest.fixture
    def mock_emit(self):
        """Create a mock emit function."""
        return AsyncMock()

    @pytest.fixture
    def signal_engine(self, mock_emit):
        """Create a SignalEngine instance."""
        return SignalEngine(emit=mock_emit)

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

    @pytest.mark.asyncio
    async def test_handle_tick_no_crossover_no_signal(self, signal_engine, sample_tick):
        """Test handle_tick with no crossover does not emit signal."""
        # Set up tick with no crossover (both positive)
        sample_tick.equity.session_vwap = 400.0
        sample_tick.equity.ma9 = 398.0
        signal_engine._last_diff = 1.0  # Previous diff was positive

        await signal_engine.handle_tick(sample_tick)

        signal_engine._emit.assert_not_called()
        assert signal_engine._last_diff == 2.0  # Updated to new diff

    @pytest.mark.asyncio
    async def test_handle_tick_crossover_emits_signal(self, signal_engine, sample_tick):
        """Test handle_tick with crossover emits signal."""
        # Set up tick with crossover (positive to negative)
        sample_tick.equity.session_vwap = 397.0
        sample_tick.equity.ma9 = 398.0
        signal_engine._last_diff = 1.0  # Previous diff was positive

        await signal_engine.handle_tick(sample_tick)

        signal_engine._emit.assert_called_once()
        call_args = signal_engine._emit.call_args[0][0]
        assert isinstance(call_args, Signal)
        assert call_args.action == "SELL_PUT_TO_OPEN"
        assert call_args.option_symbol == "QQQ240119C00400000"

    @pytest.mark.asyncio
    async def test_handle_tick_zero_crossover_emits_signal(
        self, signal_engine, sample_tick
    ):
        """Test handle_tick with zero diff emits signal."""
        # Set up tick with zero diff
        sample_tick.equity.session_vwap = 400.0
        sample_tick.equity.ma9 = 400.0
        signal_engine._last_diff = 1.0  # Previous diff was positive

        await signal_engine.handle_tick(sample_tick)

        signal_engine._emit.assert_called_once()
        call_args = signal_engine._emit.call_args[0][0]
        assert isinstance(call_args, Signal)
        # When diff is 0, action is determined by diff > 0, which is False, so SELL_PUT_TO_OPEN
        assert call_args.action == "SELL_PUT_TO_OPEN"

    @pytest.mark.asyncio
    async def test_handle_tick_negative_to_positive_crossover(
        self, signal_engine, sample_tick
    ):
        """Test handle_tick with negative to positive crossover."""
        # Set up tick with negative to positive crossover
        sample_tick.equity.session_vwap = 401.0
        sample_tick.equity.ma9 = 400.0
        signal_engine._last_diff = -1.0  # Previous diff was negative

        await signal_engine.handle_tick(sample_tick)

        signal_engine._emit.assert_called_once()
        call_args = signal_engine._emit.call_args[0][0]
        assert call_args.action == "SELL_TO_OPEN"

    def test_clear_cooldown(self, signal_engine):
        """Test clear_cooldown sets cooldown to expired."""
        # Set up an active cooldown
        signal_engine._cooldown_state = signal_engine._cooldown_state.extend(
            timedelta(minutes=5)
        )

        signal_engine.clear_cooldown()

        # Should be expired (before any reasonable time)
        assert not signal_engine._cooldown_state.active(datetime.now(tz=EST))

    def test_remaining_cooldown_with_custom_time(self, signal_engine):
        """Test remaining_cooldown with custom time parameter."""
        # Set up an active cooldown
        now = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        signal_engine._cooldown_state = signal_engine._cooldown_state.extend(
            timedelta(minutes=5), from_time=now
        )

        # Test with time 2 minutes into cooldown
        test_time = now + timedelta(minutes=2)
        remaining = signal_engine.remaining_cooldown(test_time)

        assert remaining == timedelta(minutes=3)

    def test_remaining_cooldown_expired(self, signal_engine):
        """Test remaining_cooldown when cooldown is expired."""
        # Set up expired cooldown
        signal_engine._cooldown_state = signal_engine._cooldown_state.expired()

        remaining = signal_engine.remaining_cooldown()

        assert remaining == timedelta()

    def test_remaining_cooldown_uses_now_est_when_no_time_provided(self, signal_engine):
        """Test remaining_cooldown uses now_est() when no time provided."""
        from unittest.mock import patch

        # Set up an active cooldown
        now = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        signal_engine._cooldown_state = signal_engine._cooldown_state.extend(
            timedelta(minutes=5), from_time=now
        )

        with patch("alphagen.signals.now_est", return_value=now):
            remaining = signal_engine.remaining_cooldown()

            assert remaining == timedelta(minutes=5)

    @pytest.mark.asyncio
    async def test_handle_tick_updates_cooldown_state(self, signal_engine, sample_tick):
        """Test handle_tick updates cooldown state after emitting signal."""
        # Set up tick with crossover
        sample_tick.equity.session_vwap = 401.0
        sample_tick.equity.ma9 = 400.0
        signal_engine._last_diff = -1.0

        await signal_engine.handle_tick(sample_tick)

        # Cooldown state should be updated
        assert signal_engine._cooldown_state.until > sample_tick.as_of
        assert signal_engine._cooldown_state.active(sample_tick.as_of)

    @pytest.mark.asyncio
    async def test_handle_tick_with_custom_cooldown_duration(self, mock_emit):
        """Test SignalEngine with custom cooldown duration."""
        custom_cooldown = timedelta(minutes=10)
        signal_engine = SignalEngine(emit=mock_emit, cooldown=custom_cooldown)

        # Set up tick with crossover
        as_of = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        equity = EquityTick(
            symbol="QQQ", price=400.0, session_vwap=401.0, ma9=400.0, as_of=as_of
        )
        option = OptionQuote(
            option_symbol="QQQ240119C00400000",
            strike=400.0,
            bid=2.50,
            ask=2.75,
            expiry=datetime(2024, 1, 19, 16, 0, 0, tzinfo=EST),
            as_of=as_of,
        )
        tick = NormalizedTick(as_of=as_of, equity=equity, option=option)
        signal_engine._last_diff = -1.0

        await signal_engine.handle_tick(tick)

        # Check that signal has correct cooldown
        call_args = mock_emit.call_args[0][0]
        expected_cooldown_until = as_of + custom_cooldown
        assert call_args.cooldown_until == expected_cooldown_until
