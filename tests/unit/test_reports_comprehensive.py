"""Comprehensive tests for reports module."""

import pytest

from src.alphagen.reports import fetch_daily_pnl


class TestReportsComprehensive:
    """Comprehensive tests for reports functions."""

    def test_fetch_daily_pnl_function_exists(self):
        """Test that fetch_daily_pnl function exists and is callable."""
        assert callable(fetch_daily_pnl)
        assert hasattr(fetch_daily_pnl, "__call__")

    def test_fetch_daily_pnl_function_signature(self):
        """Test that fetch_daily_pnl has the correct function signature."""
        import inspect

        sig = inspect.signature(fetch_daily_pnl)
        params = list(sig.parameters.keys())

        # Should have one optional parameter
        assert len(params) == 1
        assert params[0] == "trade_date"

        # Parameter should have default value of None
        assert sig.parameters["trade_date"].default is None

    @pytest.mark.asyncio
    async def test_fetch_daily_pnl_returns_list(self):
        """Test that fetch_daily_pnl returns a list."""
        result = await fetch_daily_pnl()
        assert isinstance(result, list)

        # Each item should be a dict
        for item in result:
            assert isinstance(item, dict)
            assert "trade_date" in item
            assert "realized_pnl" in item
            assert "trade_count" in item
