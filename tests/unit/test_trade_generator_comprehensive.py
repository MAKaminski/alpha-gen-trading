"""Comprehensive tests for trade_generator module."""

import pytest
from unittest.mock import AsyncMock, patch, Mock
from datetime import datetime

from alphagen.trade_generator import TradeGenerator
from alphagen.core.events import Signal, TradeIntent
from alphagen.config import EST


class TestTradeGeneratorComprehensive:
    """Comprehensive tests for TradeGenerator."""

    @pytest.fixture
    def mock_emit(self):
        """Create a mock emit function."""
        return AsyncMock()

    @pytest.fixture
    def sample_signal(self):
        """Create a sample Signal."""
        as_of = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        return Signal(
            as_of=as_of,
            action="SELL_TO_OPEN",
            option_symbol="QQQ240119C00400000",
            reference_price=2.60,
            rationale="VWAP crossed above MA9",
            cooldown_until=as_of,
        )

    @pytest.mark.asyncio
    async def test_handle_signal_creates_trade_intent(self, mock_emit, sample_signal):
        """Test handle_signal creates and emits trade intent."""
        with patch("alphagen.trade_generator.load_app_config") as mock_load_config:
            # Mock the config
            mock_config = Mock()
            mock_config.risk.stop_loss_multiple = 2.0
            mock_config.risk.take_profit_multiple = 0.5
            mock_config.risk.max_position_size = 10
            mock_load_config.return_value = mock_config

            generator = TradeGenerator(emit=mock_emit)

            await generator.handle_signal(sample_signal)

            # Should emit the trade intent
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[0][0]
            assert isinstance(call_args, TradeIntent)
            assert call_args.as_of == sample_signal.as_of
            assert call_args.action == sample_signal.action
            assert call_args.option_symbol == sample_signal.option_symbol
            assert call_args.quantity == 10
            assert call_args.limit_price == 2.60
            assert call_args.stop_loss == 2.60 * 3.0  # 1 + 2.0
            assert call_args.take_profit == 2.60 * 0.5  # 1 - 0.5

    @pytest.mark.asyncio
    async def test_handle_signal_with_zero_take_profit(self, mock_emit, sample_signal):
        """Test handle_signal with very small reference price ensures minimum take profit."""
        with patch("alphagen.trade_generator.load_app_config") as mock_load_config:
            # Mock the config
            mock_config = Mock()
            mock_config.risk.stop_loss_multiple = 2.0
            mock_config.risk.take_profit_multiple = 0.5
            mock_config.risk.max_position_size = 10
            mock_load_config.return_value = mock_config

            # Use a very small reference price
            sample_signal.reference_price = 0.01

            generator = TradeGenerator(emit=mock_emit)

            await generator.handle_signal(sample_signal)

            # Should emit the trade intent with minimum take profit
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[0][0]
            assert call_args.take_profit == 0.01  # Minimum value

    @pytest.mark.asyncio
    async def test_handle_signal_with_large_reference_price(
        self, mock_emit, sample_signal
    ):
        """Test handle_signal with large reference price."""
        with patch("alphagen.trade_generator.load_app_config") as mock_load_config:
            # Mock the config
            mock_config = Mock()
            mock_config.risk.stop_loss_multiple = 1.5
            mock_config.risk.take_profit_multiple = 0.3
            mock_config.risk.max_position_size = 25
            mock_load_config.return_value = mock_config

            # Use a large reference price
            sample_signal.reference_price = 10.0

            generator = TradeGenerator(emit=mock_emit)

            await generator.handle_signal(sample_signal)

            # Should emit the trade intent
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args[0][0]
            assert call_args.quantity == 25
            assert call_args.limit_price == 10.0
            assert call_args.stop_loss == 10.0 * 2.5  # 1 + 1.5
            assert call_args.take_profit == 10.0 * 0.7  # 1 - 0.3

    def test_initialization_loads_config(self, mock_emit):
        """Test initialization loads app config."""
        with patch("alphagen.trade_generator.load_app_config") as mock_load_config:
            mock_config = Mock()
            mock_load_config.return_value = mock_config

            generator = TradeGenerator(emit=mock_emit)

            # Should load config and store risk settings
            mock_load_config.assert_called_once()
            assert generator._risk == mock_config.risk
