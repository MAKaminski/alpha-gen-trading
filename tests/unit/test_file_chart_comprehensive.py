"""Comprehensive tests for file_chart module."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from alphagen.visualization.file_chart import FileChart, _TickPoint


class TestFileChartComprehensive:
    """Comprehensive tests for FileChart."""

    @pytest.fixture
    def file_chart(self):
        """Create a FileChart instance."""
        return FileChart()

    def test_save_chart_exception_handling(self, file_chart):
        """Test _save_chart handles exceptions properly."""
        # Add some data to the buffer so the method doesn't return early
        file_chart._tick_buffer.append(
            _TickPoint(timestamp=datetime.now(), vwap=100.0, ma9=99.0)
        )

        # Mock plt.savefig to raise an exception
        with patch("matplotlib.pyplot.savefig", side_effect=Exception("Save failed")):
            # Mock the logger
            file_chart._logger = Mock()

            # Should not raise exception, should log error
            file_chart._save_chart()

            # Should log the error
            file_chart._logger.error.assert_called_once_with(
                "chart_save_failed", error="Save failed"
            )

    def test_save_chart_success(self, file_chart):
        """Test _save_chart saves successfully."""
        # Add some data to the buffer so the method doesn't return early
        file_chart._tick_buffer.append(
            _TickPoint(timestamp=datetime.now(), vwap=100.0, ma9=99.0)
        )

        # Mock the logger
        file_chart._logger = Mock()

        # Mock plt.savefig
        with patch("matplotlib.pyplot.savefig") as mock_savefig:
            # Should save successfully
            file_chart._save_chart()

            # Should call savefig
            mock_savefig.assert_called_once()

            # Should log success
            file_chart._logger.info.assert_called_once()
            call_args = file_chart._logger.info.call_args
            assert call_args[0][0] == "chart_saved"
            assert "filename" in call_args[1]
