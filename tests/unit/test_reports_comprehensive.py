"""Comprehensive tests for reports module."""

import pytest
from datetime import date
from unittest.mock import AsyncMock, patch, Mock

from alphagen.reports import fetch_daily_pnl


class TestReportsComprehensive:
    """Comprehensive tests for reports functions."""

    @pytest.mark.asyncio
    async def test_fetch_daily_pnl_without_date(self):
        """Test fetch_daily_pnl without specific date."""
        # Mock the engine and connection
        mock_engine = AsyncMock()
        mock_conn = AsyncMock()
        
        # Create a proper async context manager
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_engine.connect.return_value = mock_context_manager
        
        # Mock the result
        mock_result = AsyncMock()
        mock_row1 = Mock()
        mock_row1._mapping = {"trade_date": "2024-01-15", "realized_pnl": 150.0, "trade_count": 5}
        mock_row2 = Mock()
        mock_row2._mapping = {"trade_date": "2024-01-14", "realized_pnl": -50.0, "trade_count": 2}
        mock_result.__iter__.return_value = [mock_row1, mock_row2]
        mock_conn.execute.return_value = mock_result
        
        with patch('alphagen.reports.get_engine', return_value=mock_engine):
            result = await fetch_daily_pnl()
            
            # Should return the expected data
            assert len(result) == 2
            assert result[0]["trade_date"] == "2024-01-15"
            assert result[0]["realized_pnl"] == 150.0
            assert result[0]["trade_count"] == 5
            assert result[1]["trade_date"] == "2024-01-14"
            assert result[1]["realized_pnl"] == -50.0
            assert result[1]["trade_count"] == 2

    @pytest.mark.asyncio
    async def test_fetch_daily_pnl_with_specific_date(self):
        """Test fetch_daily_pnl with specific date."""
        # Mock the engine and connection
        mock_engine = AsyncMock()
        mock_conn = AsyncMock()
        
        # Create a proper async context manager
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_engine.connect.return_value = mock_context_manager
        
        # Mock the result
        mock_result = AsyncMock()
        mock_row = Mock()
        mock_row._mapping = {"trade_date": "2024-01-15", "realized_pnl": 150.0, "trade_count": 5}
        mock_result.__iter__.return_value = [mock_row]
        mock_conn.execute.return_value = mock_result
        
        with patch('alphagen.reports.get_engine', return_value=mock_engine):
            result = await fetch_daily_pnl(date(2024, 1, 15))
            
            # Should return the expected data
            assert len(result) == 1
            assert result[0]["trade_date"] == "2024-01-15"
            assert result[0]["realized_pnl"] == 150.0
            assert result[0]["trade_count"] == 5
            
            # Should call execute with the correct parameters
            mock_conn.execute.assert_called_once()
            call_args = mock_conn.execute.call_args
            assert "trade_date" in call_args[1]
            assert call_args[1]["trade_date"] == "2024-01-15"

    @pytest.mark.asyncio
    async def test_fetch_daily_pnl_empty_result(self):
        """Test fetch_daily_pnl with empty result."""
        # Mock the engine and connection
        mock_engine = AsyncMock()
        mock_conn = AsyncMock()
        mock_engine.connect.return_value = mock_conn
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        
        # Mock empty result
        mock_result = AsyncMock()
        mock_result.__iter__.return_value = []
        mock_conn.execute.return_value = mock_result
        
        with patch('alphagen.reports.get_engine', return_value=mock_engine):
            result = await fetch_daily_pnl()
            
            # Should return empty list
            assert result == []