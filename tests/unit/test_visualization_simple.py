"""Simplified tests for visualization modules focusing on core functionality."""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from pathlib import Path
import tempfile

from alphagen.core.events import NormalizedTick, Signal, EquityTick


class TestLiveChartSimple:
    """Simplified tests for LiveChart focusing on core functionality."""

    def test_init_default_params(self):
        """Test LiveChart initialization with default parameters."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart()
        assert chart._max_points == 600
        assert chart._running is False
        assert chart._thread is None
        assert len(chart._tick_buffer) == 0
        assert len(chart._signal_buffer) == 0

    def test_init_custom_max_points(self):
        """Test LiveChart initialization with custom max_points."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart(max_points=100)
        assert chart._max_points == 100

    def test_start_when_already_running(self):
        """Test start() when chart is already running."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart()
        chart._running = True
        chart._thread = Mock()
        
        chart.start()  # Should not create new thread
        assert chart._running is True

    def test_handle_tick_starts_chart_if_not_running(self):
        """Test handle_tick starts chart if not running."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart()
        chart._queue = Mock()
        
        # Create a mock tick
        mock_tick = Mock()
        mock_tick.as_of = datetime.now(timezone.utc)
        mock_tick.equity.session_vwap = 100.0
        mock_tick.equity.ma9 = 99.5
        
        with patch.object(chart, 'start') as mock_start:
            chart.handle_tick(mock_tick)
            mock_start.assert_called_once()
            chart._queue.put.assert_called_once()

    def test_handle_signal_starts_chart_if_not_running(self):
        """Test handle_signal starts chart if not running."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart()
        chart._queue = Mock()
        
        # Create a mock signal
        mock_signal = Mock()
        mock_signal.as_of = datetime.now(timezone.utc)
        mock_signal.reference_price = 100.0
        mock_signal.action = "BUY_OPEN"
        
        with patch.object(chart, 'start') as mock_start:
            chart.handle_signal(mock_signal)
            mock_start.assert_called_once()
            chart._queue.put.assert_called_once()


class TestSimpleChartSimple:
    """Simplified tests for SimpleChart focusing on core functionality."""

    def test_init_default_params(self):
        """Test SimpleChart initialization with default parameters."""
        from alphagen.visualization.simple_chart import SimpleChart
        
        chart = SimpleChart()
        assert chart._max_points == 100
        assert chart._running is False
        assert chart._fig is None
        assert chart._ax is None
        assert len(chart._tick_buffer) == 0
        assert len(chart._signal_buffer) == 0

    def test_init_custom_max_points(self):
        """Test SimpleChart initialization with custom max_points."""
        from alphagen.visualization.simple_chart import SimpleChart
        
        chart = SimpleChart(max_points=50)
        assert chart._max_points == 50

    def test_start_when_already_running(self):
        """Test start() when chart is already running."""
        from alphagen.visualization.simple_chart import SimpleChart
        
        chart = SimpleChart()
        chart._running = True
        
        chart.start()  # Should return early
        assert chart._running is True

    def test_stop_when_not_running(self):
        """Test stop() when chart is not running."""
        from alphagen.visualization.simple_chart import SimpleChart
        
        chart = SimpleChart()
        chart._running = False
        
        chart.stop()  # Should return early
        assert chart._running is False

    def test_handle_tick_when_not_running(self):
        """Test handle_tick when chart is not running."""
        from alphagen.visualization.simple_chart import SimpleChart
        
        chart = SimpleChart()
        chart._running = False
        
        mock_tick = Mock()
        mock_tick.as_of = datetime.now(timezone.utc)
        mock_tick.equity.session_vwap = 100.0
        mock_tick.equity.ma9 = 99.5
        
        chart.handle_tick(mock_tick)  # Should return early
        assert len(chart._tick_buffer) == 0

    def test_handle_tick_when_running(self):
        """Test handle_tick when chart is running."""
        from alphagen.visualization.simple_chart import SimpleChart
        
        chart = SimpleChart()
        chart._running = True
        
        mock_tick = Mock()
        mock_tick.as_of = datetime.now(timezone.utc)
        mock_tick.equity.session_vwap = 100.0
        mock_tick.equity.ma9 = 99.5
        
        chart.handle_tick(mock_tick)
        assert len(chart._tick_buffer) == 1


class TestFileChartSimple:
    """Simplified tests for FileChart focusing on core functionality."""

    def test_init_default_params(self):
        """Test FileChart initialization with default parameters."""
        from alphagen.visualization.file_chart import FileChart
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            assert chart._max_points == 100
            assert chart._running is False
            assert chart._output_dir == Path(temp_dir)
            assert len(chart._tick_buffer) == 0
            assert len(chart._signal_buffer) == 0

    def test_init_custom_params(self):
        """Test FileChart initialization with custom parameters."""
        from alphagen.visualization.file_chart import FileChart
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir, max_points=50)
            assert chart._max_points == 50
            assert chart._output_dir == Path(temp_dir)

    def test_start_when_already_running(self):
        """Test start() when chart is already running."""
        from alphagen.visualization.file_chart import FileChart
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            chart._running = True
            
            chart.start()  # Should return early
            assert chart._running is True

    def test_stop_when_not_running(self):
        """Test stop() when chart is not running."""
        from alphagen.visualization.file_chart import FileChart
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            chart._running = False
            
            chart.stop()  # Should return early
            assert chart._running is False

    def test_handle_tick_when_not_running(self):
        """Test handle_tick when chart is not running."""
        from alphagen.visualization.file_chart import FileChart
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            chart._running = False
            
            mock_tick = Mock()
            mock_tick.as_of = datetime.now(timezone.utc)
            mock_tick.equity.session_vwap = 100.0
            mock_tick.equity.ma9 = 99.5
            
            chart.handle_tick(mock_tick)  # Should return early
            assert len(chart._tick_buffer) == 0

    def test_handle_tick_when_running(self):
        """Test handle_tick when chart is running."""
        from alphagen.visualization.file_chart import FileChart
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            chart._running = True
            
            mock_tick = Mock()
            mock_tick.as_of = datetime.now(timezone.utc)
            mock_tick.equity.session_vwap = 100.0
            mock_tick.equity.ma9 = 99.5
            
            chart.handle_tick(mock_tick)
            assert len(chart._tick_buffer) == 1

    def test_handle_signal_when_not_running(self):
        """Test handle_signal when chart is not running."""
        from alphagen.visualization.file_chart import FileChart
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            chart._running = False
            
            mock_signal = Mock()
            mock_signal.as_of = datetime.now(timezone.utc)
            mock_signal.reference_price = 100.0
            mock_signal.action = "BUY_OPEN"
            
            chart.handle_signal(mock_signal)  # Should return early
            assert len(chart._signal_buffer) == 0

    def test_handle_signal_when_running(self):
        """Test handle_signal when chart is running."""
        from alphagen.visualization.file_chart import FileChart
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            chart._running = True
            
            mock_signal = Mock()
            mock_signal.as_of = datetime.now(timezone.utc)
            mock_signal.reference_price = 100.0
            mock_signal.action = "BUY_OPEN"
            
            chart.handle_signal(mock_signal)
            assert len(chart._signal_buffer) == 1


class TestSimpleGUIChartSimple:
    """Simplified tests for SimpleGUChart focusing on core functionality."""

    def test_init_default_params(self):
        """Test SimpleGUChart initialization with default parameters."""
        from alphagen.visualization.simple_gui_chart import SimpleGUChart
        
        mock_parent = Mock()
        chart = SimpleGUChart(mock_parent)
        
        assert chart.max_points == 100
        assert chart.time_scale == "1min"
        assert len(chart.data_buffer) == 0
        assert chart.parent_frame == mock_parent

    def test_init_custom_max_points(self):
        """Test SimpleGUChart initialization with custom max_points."""
        from alphagen.visualization.simple_gui_chart import SimpleGUChart
        
        mock_parent = Mock()
        chart = SimpleGUChart(mock_parent, max_points=50)
        
        assert chart.max_points == 50

    def test_scale_configs(self):
        """Test scale configurations are properly set."""
        from alphagen.visualization.simple_gui_chart import SimpleGUChart
        
        mock_parent = Mock()
        chart = SimpleGUChart(mock_parent)
        
        expected_scales = ["1min", "5min", "15min", "1hour", "4hour", "1day"]
        assert list(chart.scale_configs.keys()) == expected_scales
        
        for scale in expected_scales:
            config = chart.scale_configs[scale]
            assert "max_points" in config
            assert "label" in config

    def test_change_time_scale(self):
        """Test changing time scale."""
        from alphagen.visualization.simple_gui_chart import SimpleGUChart
        
        mock_parent = Mock()
        chart = SimpleGUChart(mock_parent)
        
        chart.change_time_scale("5min")
        assert chart.time_scale == "5min"

    def test_change_time_scale_invalid(self):
        """Test changing to invalid time scale."""
        from alphagen.visualization.simple_gui_chart import SimpleGUChart
        
        mock_parent = Mock()
        chart = SimpleGUChart(mock_parent)
        original_scale = chart.time_scale
        
        chart.change_time_scale("invalid")
        assert chart.time_scale == original_scale  # Should remain unchanged

    def test_get_current_data_empty(self):
        """Test getting current data when buffer is empty."""
        from alphagen.visualization.simple_gui_chart import SimpleGUChart
        
        mock_parent = Mock()
        chart = SimpleGUChart(mock_parent)
        
        data = chart.get_current_data()
        assert data == []

    def test_clear_data(self):
        """Test clearing all data from buffer."""
        from alphagen.visualization.simple_gui_chart import SimpleGUChart
        
        mock_parent = Mock()
        chart = SimpleGUChart(mock_parent)
        
        # Add some data
        for i in range(3):
            mock_equity = Mock()
            mock_equity.session_vwap = 100.0 + i
            mock_equity.ma9 = 99.5 + i
            
            mock_tick = Mock()
            mock_tick.as_of = datetime.now(timezone.utc)
            mock_tick.equity = mock_equity
            
            chart.add_tick(mock_tick)
        
        assert len(chart.data_buffer) == 3
        chart.clear_data()
        assert len(chart.data_buffer) == 0

    def test_get_time_scale_label(self):
        """Test getting time scale label."""
        from alphagen.visualization.simple_gui_chart import SimpleGUChart
        
        mock_parent = Mock()
        chart = SimpleGUChart(mock_parent)
        
        chart.time_scale = "1min"
        label = chart.get_time_scale_label()
        assert label == "1 Minute"
        
        chart.time_scale = "5min"
        label = chart.get_time_scale_label()
        assert label == "5 Minutes"

    def test_get_available_scales(self):
        """Test getting available time scales."""
        from alphagen.visualization.simple_gui_chart import SimpleGUChart
        
        mock_parent = Mock()
        chart = SimpleGUChart(mock_parent)
        
        scales = chart.get_available_scales()
        expected_scales = ["1min", "5min", "15min", "1hour", "4hour", "1day"]
        assert scales == expected_scales
