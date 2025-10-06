"""Tests for events module."""

from datetime import datetime, timedelta

from src.alphagen.core.events import (
    EquityTick,
    OptionQuote,
    PositionSnapshot,
    NormalizedTick,
    Signal,
    TradeIntent,
    TradeExecution,
    CooldownState,
    PositionState,
)
from src.alphagen.config import EST


class TestEquityTick:
    """Test EquityTick dataclass."""

    def test_equity_tick_creation(self):
        """Test creating an EquityTick instance."""
        as_of = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        tick = EquityTick(
            symbol="QQQ", price=400.0, session_vwap=399.5, ma9=398.0, as_of=as_of
        )

        assert tick.symbol == "QQQ"
        assert tick.price == 400.0
        assert tick.session_vwap == 399.5
        assert tick.ma9 == 398.0
        assert tick.as_of == as_of

    def test_equity_tick_post_init_sets_est_timezone(self):
        """Test that __post_init__ sets EST timezone for naive datetime."""
        naive_dt = datetime(2024, 1, 15, 10, 0, 0)
        tick = EquityTick(
            symbol="QQQ", price=400.0, session_vwap=399.5, ma9=398.0, as_of=naive_dt
        )

        assert tick.as_of.tzinfo == EST
        assert tick.as_of.replace(tzinfo=None) == naive_dt


class TestOptionQuote:
    """Test OptionQuote dataclass."""

    def test_option_quote_creation(self):
        """Test creating an OptionQuote instance."""
        as_of = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        expiry = datetime(2024, 1, 19, 16, 0, 0, tzinfo=EST)

        quote = OptionQuote(
            option_symbol="QQQ240119C00400000",
            strike=400.0,
            bid=2.50,
            ask=2.75,
            expiry=expiry,
            as_of=as_of,
        )

        assert quote.option_symbol == "QQQ240119C00400000"
        assert quote.strike == 400.0
        assert quote.bid == 2.50
        assert quote.ask == 2.75
        assert quote.expiry == expiry
        assert quote.as_of == as_of

    def test_option_quote_mid_calculation(self):
        """Test mid price calculation."""
        as_of = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        expiry = datetime(2024, 1, 19, 16, 0, 0, tzinfo=EST)

        quote = OptionQuote(
            option_symbol="QQQ240119C00400000",
            strike=400.0,
            bid=2.50,
            ask=2.75,
            expiry=expiry,
            as_of=as_of,
        )

        expected_mid = (2.50 + 2.75) / 2
        assert quote.mid() == expected_mid


class TestPositionSnapshot:
    """Test PositionSnapshot dataclass."""

    def test_position_snapshot_creation(self):
        """Test creating a PositionSnapshot instance."""
        as_of = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)

        snapshot = PositionSnapshot(
            symbol="QQQ240119C00400000",
            quantity=10,
            average_price=2.60,
            market_value=26.0,
            as_of=as_of,
        )

        assert snapshot.symbol == "QQQ240119C00400000"
        assert snapshot.quantity == 10
        assert snapshot.average_price == 2.60
        assert snapshot.market_value == 26.0
        assert snapshot.as_of == as_of


class TestNormalizedTick:
    """Test NormalizedTick dataclass."""

    def test_normalized_tick_creation(self):
        """Test creating a NormalizedTick instance."""
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

        tick = NormalizedTick(as_of=as_of, equity=equity, option=option)

        assert tick.as_of == as_of
        assert tick.equity == equity
        assert tick.option == option

    def test_normalized_tick_with_none_option(self):
        """Test creating a NormalizedTick with None option."""
        as_of = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        equity = EquityTick(
            symbol="QQQ", price=400.0, session_vwap=399.5, ma9=398.0, as_of=as_of
        )

        tick = NormalizedTick(as_of=as_of, equity=equity, option=None)

        assert tick.as_of == as_of
        assert tick.equity == equity
        assert tick.option is None


class TestSignal:
    """Test Signal dataclass."""

    def test_signal_creation(self):
        """Test creating a Signal instance."""
        as_of = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        cooldown_until = as_of + timedelta(minutes=5)

        signal = Signal(
            as_of=as_of,
            action="SHORT",
            option_symbol="QQQ240119C00400000",
            reference_price=2.60,
            rationale="VWAP crossed above MA9",
            cooldown_until=cooldown_until,
        )

        assert signal.as_of == as_of
        assert signal.action == "SHORT"
        assert signal.option_symbol == "QQQ240119C00400000"
        assert signal.reference_price == 2.60
        assert signal.rationale == "VWAP crossed above MA9"
        assert signal.cooldown_until == cooldown_until


class TestTradeIntent:
    """Test TradeIntent dataclass."""

    def test_trade_intent_creation(self):
        """Test creating a TradeIntent instance."""
        as_of = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)

        intent = TradeIntent(
            as_of=as_of,
            action="SHORT",
            option_symbol="QQQ240119C00400000",
            quantity=10,
            limit_price=2.60,
            stop_loss=3.00,
            take_profit=2.20,
        )

        assert intent.as_of == as_of
        assert intent.action == "SHORT"
        assert intent.option_symbol == "QQQ240119C00400000"
        assert intent.quantity == 10
        assert intent.limit_price == 2.60
        assert intent.stop_loss == 3.00
        assert intent.take_profit == 2.20


class TestTradeExecution:
    """Test TradeExecution dataclass."""

    def test_trade_execution_creation(self):
        """Test creating a TradeExecution instance."""
        as_of = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        intent = TradeIntent(
            as_of=as_of,
            action="SHORT",
            option_symbol="QQQ240119C00400000",
            quantity=10,
            limit_price=2.60,
            stop_loss=3.00,
            take_profit=2.20,
        )

        execution = TradeExecution(
            order_id="12345",
            status="FILLED",
            fill_price=2.58,
            pnl_contrib=0.20,
            as_of=as_of,
            intent=intent,
        )

        assert execution.order_id == "12345"
        assert execution.status == "FILLED"
        assert execution.fill_price == 2.58
        assert execution.pnl_contrib == 0.20
        assert execution.as_of == as_of
        assert execution.intent == intent


class TestCooldownState:
    """Test CooldownState dataclass."""

    def test_cooldown_state_creation(self):
        """Test creating a CooldownState instance."""
        until = datetime(2024, 1, 15, 10, 5, 0, tzinfo=EST)
        cooldown = CooldownState(until=until)

        assert cooldown.until == until

    def test_cooldown_state_active_before_expiry(self):
        """Test active returns True before expiry."""
        until = datetime(2024, 1, 15, 10, 5, 0, tzinfo=EST)
        cooldown = CooldownState(until=until)
        now = datetime(2024, 1, 15, 10, 2, 0, tzinfo=EST)

        assert cooldown.active(now) is True

    def test_cooldown_state_inactive_after_expiry(self):
        """Test active returns False after expiry."""
        until = datetime(2024, 1, 15, 10, 5, 0, tzinfo=EST)
        cooldown = CooldownState(until=until)
        now = datetime(2024, 1, 15, 10, 6, 0, tzinfo=EST)

        assert cooldown.active(now) is False

    def test_cooldown_state_expired_class_method(self):
        """Test expired class method returns expired cooldown."""
        cooldown = CooldownState.expired()

        assert cooldown.until == datetime.min.replace(tzinfo=EST)
        # Should be inactive for any reasonable datetime
        now = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        assert cooldown.active(now) is False

    def test_cooldown_state_extend(self):
        """Test extend method creates new cooldown with extended duration."""
        until = datetime(2024, 1, 15, 10, 5, 0, tzinfo=EST)
        cooldown = CooldownState(until=until)
        duration = timedelta(minutes=10)

        extended = cooldown.extend(duration)

        expected_until = until + duration
        assert extended.until == expected_until

    def test_cooldown_state_extend_with_custom_from_time(self):
        """Test extend method with custom from_time parameter."""
        until = datetime(2024, 1, 15, 10, 5, 0, tzinfo=EST)
        cooldown = CooldownState(until=until)
        duration = timedelta(minutes=10)
        from_time = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)

        extended = cooldown.extend(duration, from_time)

        expected_until = from_time + duration
        assert extended.until == expected_until


class TestPositionState:
    """Test PositionState dataclass."""

    def test_position_state_creation(self):
        """Test creating a PositionState instance."""
        as_of = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        snapshot1 = PositionSnapshot(
            symbol="QQQ240119C00400000",
            quantity=10,
            average_price=2.60,
            market_value=26.0,
            as_of=as_of,
        )
        snapshot2 = PositionSnapshot(
            symbol="QQQ240119P00395000",
            quantity=5,
            average_price=1.80,
            market_value=9.0,
            as_of=as_of,
        )

        positions = PositionState(
            as_of=as_of,
            symbols={"QQQ240119C00400000": snapshot1, "QQQ240119P00395000": snapshot2},
        )

        assert positions.as_of == as_of
        assert len(positions.symbols) == 2
        assert positions.symbols["QQQ240119C00400000"] == snapshot1
        assert positions.symbols["QQQ240119P00395000"] == snapshot2

    def test_position_state_total_market_value(self):
        """Test total_market_value calculation."""
        as_of = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        snapshot1 = PositionSnapshot(
            symbol="QQQ240119C00400000",
            quantity=10,
            average_price=2.60,
            market_value=26.0,
            as_of=as_of,
        )
        snapshot2 = PositionSnapshot(
            symbol="QQQ240119P00395000",
            quantity=5,
            average_price=1.80,
            market_value=9.0,
            as_of=as_of,
        )

        positions = PositionState(
            as_of=as_of,
            symbols={"QQQ240119C00400000": snapshot1, "QQQ240119P00395000": snapshot2},
        )

        expected_total = 26.0 + 9.0
        assert positions.total_market_value() == expected_total

    def test_position_state_total_market_value_empty(self):
        """Test total_market_value with empty positions."""
        as_of = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        positions = PositionState(as_of=as_of, symbols={})

        assert positions.total_market_value() == 0.0
