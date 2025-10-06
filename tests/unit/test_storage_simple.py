"""Simple tests for storage module."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone

from alphagen.storage import (
    EquityTickRow, OptionQuoteRow, PositionSnapshotRow, NormalizedTickRow,
    SignalRow, TradeIntentRow, ExecutionRow, get_engine, init_models,
    session_scope, insert_equity_tick, insert_option_quote, insert_positions,
    insert_normalized_tick, insert_signal, insert_trade_intent, insert_execution
)
from alphagen.core.events import (
    EquityTick, OptionQuote, PositionSnapshot, NormalizedTick, Signal,
    TradeIntent, TradeExecution
)


class TestStorageModels:
    """Test storage model creation."""

    def test_equity_tick_row_creation(self):
        """Test EquityTickRow creation."""
        timestamp = datetime.now(timezone.utc)
        row = EquityTickRow(
            symbol="QQQ",
            price=400.0,
            session_vwap=399.5,
            ma9=400.2,
            as_of=timestamp
        )
        assert row.symbol == "QQQ"
        assert row.price == 400.0

    def test_option_quote_row_creation(self):
        """Test OptionQuoteRow creation."""
        timestamp = datetime.now(timezone.utc)
        row = OptionQuoteRow(
            option_symbol="QQQ241220C00400000",
            strike=400.0,
            bid=5.50,
            ask=5.75,
            expiry=timestamp,
            as_of=timestamp
        )
        assert row.option_symbol == "QQQ241220C00400000"
        assert row.strike == 400.0

    def test_position_snapshot_row_creation(self):
        """Test PositionSnapshotRow creation."""
        timestamp = datetime.now(timezone.utc)
        row = PositionSnapshotRow(
            symbol="QQQ",
            quantity=100,
            market_value=40000.0,
            average_price=400.0,
            as_of=timestamp
        )
        assert row.symbol == "QQQ"
        assert row.quantity == 100

    def test_normalized_tick_row_creation(self):
        """Test NormalizedTickRow creation."""
        timestamp = datetime.now(timezone.utc)
        row = NormalizedTickRow(
            as_of=timestamp,
            equity_symbol="QQQ",
            equity_price=400.0,
            option_symbol=None,
            option_strike=None
        )
        assert row.equity_symbol == "QQQ"
        assert row.equity_price == 400.0

    def test_signal_row_creation(self):
        """Test SignalRow creation."""
        timestamp = datetime.now(timezone.utc)
        row = SignalRow(
            as_of=timestamp,
            action="buy",
            option_symbol="QQQ241220C00400000",
            reference_price=400.0,
            rationale="VWAP crossover",
            cooldown_until=timestamp
        )
        assert row.action == "buy"
        assert row.option_symbol == "QQQ241220C00400000"

    def test_trade_intent_row_creation(self):
        """Test TradeIntentRow creation."""
        timestamp = datetime.now(timezone.utc)
        row = TradeIntentRow(
            as_of=timestamp,
            action="buy",
            option_symbol="QQQ241220C00400000",
            quantity=100,
            limit_price=400.0,
            stop_loss=380.0,
            take_profit=420.0
        )
        assert row.action == "buy"
        assert row.quantity == 100

    def test_execution_row_creation(self):
        """Test ExecutionRow creation."""
        timestamp = datetime.now(timezone.utc)
        row = ExecutionRow(
            order_id="12345",
            status="filled",
            fill_price=400.0,
            pnl_contrib=50.0,
            as_of=timestamp,
            intent_id=1
        )
        assert row.order_id == "12345"
        assert row.status == "filled"


class TestStorageFunctions:
    """Test storage functions."""

    def test_get_engine(self):
        """Test get_engine function."""
        engine = get_engine()
        assert engine is not None

    @pytest.mark.asyncio
    async def test_init_models(self):
        """Test init_models function."""
        # This should not raise an exception
        await init_models()

    @pytest.mark.asyncio
    async def test_session_scope_success(self):
        """Test session_scope context manager success."""
        async with session_scope() as session:
            # Just verify we get a session object
            assert session is not None

    @pytest.mark.asyncio
    async def test_session_scope_exception(self):
        """Test session_scope context manager with exception."""
        with patch('alphagen.storage.get_engine') as mock_get_engine:
            mock_engine = MagicMock()
            mock_session = MagicMock()
            mock_get_engine.return_value = mock_engine
            mock_engine.begin.return_value.__aenter__.return_value = mock_session
            mock_engine.begin.return_value.__aexit__.return_value = None

            try:
                async with session_scope():
                    raise ValueError("Test exception")
            except ValueError:
                pass  # Expected exception

    @pytest.mark.asyncio
    async def test_insert_equity_tick(self):
        """Test insert_equity_tick function."""
        with patch('alphagen.storage.session_scope') as mock_session_scope:
            mock_session = MagicMock()
            mock_session_scope.return_value.__aenter__.return_value = mock_session
            mock_session_scope.return_value.__aexit__.return_value = None

            timestamp = datetime.now(timezone.utc)
            tick = EquityTick(
                symbol="QQQ",
                price=400.0,
                session_vwap=399.5,
                ma9=400.2,
                as_of=timestamp
            )

            await insert_equity_tick(tick)

            mock_session.add.assert_called_once()
            added_row = mock_session.add.call_args[0][0]
            assert isinstance(added_row, EquityTickRow)
            assert added_row.symbol == "QQQ"

    @pytest.mark.asyncio
    async def test_insert_option_quote(self):
        """Test insert_option_quote function."""
        with patch('alphagen.storage.session_scope') as mock_session_scope:
            mock_session = MagicMock()
            mock_session_scope.return_value.__aenter__.return_value = mock_session
            mock_session_scope.return_value.__aexit__.return_value = None

            timestamp = datetime.now(timezone.utc)
            quote = OptionQuote(
                option_symbol="QQQ241220C00400000",
                strike=400.0,
                bid=5.50,
                ask=5.75,
                expiry=timestamp,
                as_of=timestamp
            )

            await insert_option_quote(quote)

            mock_session.add.assert_called_once()
            added_row = mock_session.add.call_args[0][0]
            assert isinstance(added_row, OptionQuoteRow)
            assert added_row.option_symbol == "QQQ241220C00400000"

    @pytest.mark.asyncio
    async def test_insert_positions(self):
        """Test insert_positions function."""
        with patch('alphagen.storage.session_scope') as mock_session_scope:
            mock_session = MagicMock()
            mock_session_scope.return_value.__aenter__.return_value = mock_session
            mock_session_scope.return_value.__aexit__.return_value = None

            timestamp = datetime.now(timezone.utc)
            position = PositionSnapshot(
                symbol="QQQ",
                quantity=100,
                market_value=40000.0,
                average_price=400.0,
                as_of=timestamp
            )

            await insert_positions([position])

            mock_session.add.assert_called_once()
            added_row = mock_session.add.call_args[0][0]
            assert isinstance(added_row, PositionSnapshotRow)
            assert added_row.symbol == "QQQ"

    @pytest.mark.asyncio
    async def test_insert_normalized_tick(self):
        """Test insert_normalized_tick function."""
        with patch('alphagen.storage.session_scope') as mock_session_scope:
            mock_session = MagicMock()
            mock_session_scope.return_value.__aenter__.return_value = mock_session
            mock_session_scope.return_value.__aexit__.return_value = None

            timestamp = datetime.now(timezone.utc)
            equity_tick = EquityTick(
                symbol="QQQ",
                price=400.0,
                session_vwap=399.5,
                ma9=400.2,
                as_of=timestamp
            )
            normalized_tick = NormalizedTick(
                as_of=timestamp,
                equity=equity_tick,
                option=None
            )

            await insert_normalized_tick(normalized_tick)

            mock_session.add.assert_called_once()
            added_row = mock_session.add.call_args[0][0]
            assert isinstance(added_row, NormalizedTickRow)
            assert added_row.equity_symbol == "QQQ"

    @pytest.mark.asyncio
    async def test_insert_signal(self):
        """Test insert_signal function."""
        with patch('alphagen.storage.session_scope') as mock_session_scope:
            mock_session = MagicMock()
            mock_session_scope.return_value.__aenter__.return_value = mock_session
            mock_session_scope.return_value.__aexit__.return_value = None

            timestamp = datetime.now(timezone.utc)
            signal = Signal(
                as_of=timestamp,
                action="buy",
                option_symbol="QQQ241220C00400000",
                reference_price=400.0,
                rationale="VWAP crossover",
                cooldown_until=timestamp
            )

            await insert_signal(signal)

            mock_session.add.assert_called_once()
            added_row = mock_session.add.call_args[0][0]
            assert isinstance(added_row, SignalRow)
            assert added_row.action == "buy"

    @pytest.mark.asyncio
    async def test_insert_trade_intent(self):
        """Test insert_trade_intent function."""
        with patch('alphagen.storage.session_scope') as mock_session_scope:
            mock_session = MagicMock()
            mock_session.flush = AsyncMock()
            mock_session_scope.return_value.__aenter__.return_value = mock_session
            mock_session_scope.return_value.__aexit__.return_value = None

            timestamp = datetime.now(timezone.utc)
            intent = TradeIntent(
                as_of=timestamp,
                action="buy",
                option_symbol="QQQ241220C00400000",
                quantity=100,
                limit_price=400.0,
                stop_loss=380.0,
                take_profit=420.0
            )

            await insert_trade_intent(intent)

            mock_session.add.assert_called_once()
            added_row = mock_session.add.call_args[0][0]
            assert isinstance(added_row, TradeIntentRow)
            assert added_row.action == "buy"

    @pytest.mark.asyncio
    async def test_insert_execution(self):
        """Test insert_execution function."""
        with patch('alphagen.storage.session_scope') as mock_session_scope:
            mock_session = MagicMock()
            mock_session_scope.return_value.__aenter__.return_value = mock_session
            mock_session_scope.return_value.__aexit__.return_value = None

            timestamp = datetime.now(timezone.utc)
            intent = TradeIntent(
                as_of=timestamp,
                action="buy",
                option_symbol="QQQ241220C00400000",
                quantity=100,
                limit_price=400.0,
                stop_loss=380.0,
                take_profit=420.0
            )
            execution = TradeExecution(
                order_id="12345",
                status="filled",
                fill_price=400.0,
                pnl_contrib=50.0,
                as_of=timestamp,
                intent=intent
            )

            await insert_execution(execution)

            mock_session.add.assert_called_once()
            added_row = mock_session.add.call_args[0][0]
            assert isinstance(added_row, ExecutionRow)
            assert added_row.order_id == "12345"
