"""Comprehensive tests for storage module."""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from alphagen.storage import init_models, session_scope, insert_positions
from alphagen.core.events import PositionSnapshot
from alphagen.config import EST


class TestStorageComprehensive:
    """Comprehensive tests for storage functions."""

    @pytest.mark.asyncio
    async def test_init_models_success(self):
        """Test init_models creates all tables successfully."""
        with patch('alphagen.storage.get_engine') as mock_get_engine:
            mock_engine = AsyncMock()
            mock_conn = AsyncMock()
            mock_engine.begin.return_value.__aenter__.return_value = mock_conn
            mock_get_engine.return_value = mock_engine
            
            await init_models()
            
            mock_engine.begin.assert_called_once()
            mock_conn.run_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_scope_success(self):
        """Test session_scope commits on success."""
        with patch('alphagen.storage.get_engine') as mock_get_engine:
            mock_session = AsyncMock()
            mock_get_engine.return_value = mock_session
            
            async with session_scope() as session:
                assert session == mock_session
            
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_scope_rollback_on_exception(self):
        """Test session_scope rolls back on exception."""
        with patch('alphagen.storage.get_engine') as mock_get_engine:
            mock_session = AsyncMock()
            mock_get_engine.return_value = mock_session
            
            with pytest.raises(ValueError):
                async with session_scope():
                    raise ValueError("Test exception")
            
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_insert_positions_empty_list(self):
        """Test insert_positions with empty list does nothing."""
        with patch('alphagen.storage.session_scope') as mock_session_scope:
            await insert_positions([])
            mock_session_scope.assert_not_called()

    @pytest.mark.asyncio
    async def test_insert_positions_with_data(self):
        """Test insert_positions with position data."""
        as_of = datetime(2024, 1, 15, 10, 0, 0, tzinfo=EST)
        positions = [
            PositionSnapshot(
                symbol="QQQ240119C00400000",
                quantity=10,
                average_price=2.60,
                market_value=26.0,
                as_of=as_of
            ),
            PositionSnapshot(
                symbol="QQQ240119P00395000",
                quantity=5,
                average_price=1.80,
                market_value=9.0,
                as_of=as_of
            )
        ]
        
        with patch('alphagen.storage.session_scope') as mock_session_scope:
            mock_session = AsyncMock()
            mock_session_scope.return_value.__aenter__.return_value = mock_session
            
            await insert_positions(positions)
            
            mock_session_scope.assert_called_once()
            assert mock_session.add.call_count == 2
