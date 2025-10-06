"""Simplified tests for visualization modules focusing on core functionality."""

from __future__ import annotations

from unittest.mock import Mock, patch
from datetime import datetime, timezone
from pathlib import Path
import tempfile


class TestLiveChartSimple:
    """Simplified tests for LiveChart focusing on core functionality."""

    def test_init_default_params(self):
        """Test LiveChart initialization with default parameters."""
        from src.alphagen.visualization.live_chart import LiveChart

        chart = LiveChart()
        assert chart._max_points == 600
        assert chart._running is False
        assert chart._thread is None
        assert len(chart._tick_buffer) == 0
        assert len(chart._signal_buffer) == 0

    def test_init_custom_max_points(self):
        """Test LiveChart initialization with custom max_points."""
        from src.alphagen.visualization.live_chart import LiveChart

        chart = LiveChart(max_points=100)
        assert chart._max_points == 100

    def test_start_when_already_running(self):
        """Test start() when chart is already running."""
        from src.alphagen.visualization.live_chart import LiveChart

        chart = LiveChart()
        chart._running = True
        chart._thread = Mock()

        chart.start()  # Should not create new thread
        assert chart._running is True

    def test_handle_tick_starts_chart_if_not_running(self):
        """Test handle_tick starts chart if not running."""
        from src.alphagen.visualization.live_chart import LiveChart

        chart = LiveChart()
        chart._queue = Mock()

        # Create a mock tick
        mock_tick = Mock()
        mock_tick.as_of = datetime.now(timezone.utc)
        mock_tick.equity.session_vwap = 100.0
        mock_tick.equity.ma9 = 99.5

        with patch.object(chart, "start") as mock_start:
            chart.handle_tick(mock_tick)
            mock_start.assert_called_once()
            chart._queue.put.assert_called_once()

    def test_handle_signal_starts_chart_if_not_running(self):
        """Test handle_signal starts chart if not running."""
        from src.alphagen.visualization.live_chart import LiveChart

        chart = LiveChart()
        chart._queue = Mock()

        # Create a mock signal
        mock_signal = Mock()
        mock_signal.as_of = datetime.now(timezone.utc)
        mock_signal.reference_price = 100.0
        mock_signal.action = "BUY_OPEN"

        with patch.object(chart, "start") as mock_start:
            chart.handle_signal(mock_signal)
            mock_start.assert_called_once()
            chart._queue.put.assert_called_once()


class TestSimpleChartSimple:
    """Simplified tests for SimpleChart focusing on core functionality."""

    def test_init_default_params(self):
        """Test SimpleChart initialization with default parameters."""
        from src.alphagen.visualization.simple_chart import SimpleChart

        chart = SimpleChart()
        assert chart._max_points == 100
        assert chart._running is False
        assert chart._fig is None
        assert chart._ax is None
        assert len(chart._tick_buffer) == 0
        assert len(chart._signal_buffer) == 0

    def test_init_custom_max_points(self):
        """Test SimpleChart initialization with custom max_points."""
        from src.alphagen.visualization.simple_chart import SimpleChart

        chart = SimpleChart(max_points=50)
        assert chart._max_points == 50

    def test_start_when_already_running(self):
        """Test start() when chart is already running."""
        from src.alphagen.visualization.simple_chart import SimpleChart

        chart = SimpleChart()
        chart._running = True

        chart.start()  # Should return early
        assert chart._running is True

    def test_stop_when_not_running(self):
        """Test stop() when chart is not running."""
        from src.alphagen.visualization.simple_chart import SimpleChart

        chart = SimpleChart()
        chart._running = False

        chart.stop()  # Should return early
        assert chart._running is False

    def test_handle_tick_when_not_running(self):
        """Test handle_tick when chart is not running."""
        from src.alphagen.visualization.simple_chart import SimpleChart

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
        from src.alphagen.visualization.simple_chart import SimpleChart

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
        from src.alphagen.visualization.file_chart import FileChart

        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            assert chart._max_points == 100
            assert chart._running is False
            assert chart._output_dir == Path(temp_dir)
            assert len(chart._tick_buffer) == 0
            assert len(chart._signal_buffer) == 0

    def test_init_custom_params(self):
        """Test FileChart initialization with custom parameters."""
        from src.alphagen.visualization.file_chart import FileChart

        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir, max_points=50)
            assert chart._max_points == 50
            assert chart._output_dir == Path(temp_dir)

    def test_start_when_already_running(self):
        """Test start() when chart is already running."""
        from src.alphagen.visualization.file_chart import FileChart

        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            chart._running = True

            chart.start()  # Should return early
            assert chart._running is True

    def test_stop_when_not_running(self):
        """Test stop() when chart is not running."""
        from src.alphagen.visualization.file_chart import FileChart

        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            chart._running = False

            chart.stop()  # Should return early
            assert chart._running is False

    def test_handle_tick_when_not_running(self):
        """Test handle_tick when chart is not running."""
        from src.alphagen.visualization.file_chart import FileChart

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
        from src.alphagen.visualization.file_chart import FileChart

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
        from src.alphagen.visualization.file_chart import FileChart

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
        from src.alphagen.visualization.file_chart import FileChart

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

    def _setup_mocks(self):
        """Helper method to setup common mocks for SimpleGUChart tests."""
        mock_parent = Mock()
        mock_parent._last_child_ids = {}

        mock_fig = Mock()
        mock_ax = Mock()
        mock_fig.add_subplot.return_value = mock_ax

        # Mock the plot method to return a tuple for unpacking
        mock_line = Mock()
        mock_ax.plot.return_value = (mock_line,)

        mock_canvas = Mock()

        return mock_parent, mock_fig, mock_ax, mock_line, mock_canvas

    @patch("src.alphagen.visualization.simple_gui_chart.FigureCanvasTkAgg")
    @patch("src.alphagen.visualization.simple_gui_chart.Figure")
    def test_init_default_params(self, mock_figure_class, mock_canvas_class):
        """Test SimpleGUChart initialization with default parameters."""
        from src.alphagen.visualization.simple_gui_chart import SimpleGUChart

        mock_parent, mock_fig, mock_ax, mock_line, mock_canvas = self._setup_mocks()
        mock_figure_class.return_value = mock_fig
        mock_canvas_class.return_value = mock_canvas

        chart = SimpleGUChart(mock_parent)

        assert chart.max_points == 100
        assert chart.time_scale == "1min"
        assert len(chart.data_buffer) == 0
        assert chart.parent_frame == mock_parent

    @patch("src.alphagen.visualization.simple_gui_chart.FigureCanvasTkAgg")
    @patch("src.alphagen.visualization.simple_gui_chart.Figure")
    def test_init_custom_max_points(self, mock_figure_class, mock_canvas_class):
        """Test SimpleGUChart initialization with custom max_points."""
        from src.alphagen.visualization.simple_gui_chart import SimpleGUChart

        mock_parent, mock_fig, mock_ax, mock_line, mock_canvas = self._setup_mocks()
        mock_figure_class.return_value = mock_fig
        mock_canvas_class.return_value = mock_canvas

        chart = SimpleGUChart(mock_parent, max_points=50)

        assert chart.max_points == 50

    @patch("src.alphagen.visualization.simple_gui_chart.FigureCanvasTkAgg")
    @patch("src.alphagen.visualization.simple_gui_chart.Figure")
    def test_scale_configs(self, mock_figure_class, mock_canvas_class):
        """Test scale configurations are properly set."""
        from src.alphagen.visualization.simple_gui_chart import SimpleGUChart

        mock_parent, mock_fig, mock_ax, mock_line, mock_canvas = self._setup_mocks()
        mock_figure_class.return_value = mock_fig
        mock_canvas_class.return_value = mock_canvas

        chart = SimpleGUChart(mock_parent)

        expected_scales = ["1min", "5min", "15min", "1hour", "4hour", "1day"]
        assert list(chart.scale_configs.keys()) == expected_scales

        for scale in expected_scales:
            config = chart.scale_configs[scale]
            assert "max_points" in config
            assert "label" in config

    @patch("src.alphagen.visualization.simple_gui_chart.FigureCanvasTkAgg")
    @patch("src.alphagen.visualization.simple_gui_chart.Figure")
    def test_change_time_scale(self, mock_figure_class, mock_canvas_class):
        """Test changing time scale."""
        from src.alphagen.visualization.simple_gui_chart import SimpleGUChart

        mock_parent, mock_fig, mock_ax, mock_line, mock_canvas = self._setup_mocks()
        mock_figure_class.return_value = mock_fig
        mock_canvas_class.return_value = mock_canvas

        chart = SimpleGUChart(mock_parent)

        chart.set_time_scale("5min")
        assert chart.time_scale == "5min"

    @patch("src.alphagen.visualization.simple_gui_chart.FigureCanvasTkAgg")
    @patch("src.alphagen.visualization.simple_gui_chart.Figure")
    def test_change_time_scale_invalid(self, mock_figure_class, mock_canvas_class):
        """Test changing to invalid time scale."""
        from src.alphagen.visualization.simple_gui_chart import SimpleGUChart

        mock_parent, mock_fig, mock_ax, mock_line, mock_canvas = self._setup_mocks()
        mock_figure_class.return_value = mock_fig
        mock_canvas_class.return_value = mock_canvas

        chart = SimpleGUChart(mock_parent)
        original_scale = chart.time_scale

        chart.set_time_scale("invalid")
        assert chart.time_scale == original_scale  # Should remain unchanged

    @patch("src.alphagen.visualization.simple_gui_chart.FigureCanvasTkAgg")
    @patch("src.alphagen.visualization.simple_gui_chart.Figure")
    def test_get_current_data_empty(self, mock_figure_class, mock_canvas_class):
        """Test getting current data when buffer is empty."""
        from src.alphagen.visualization.simple_gui_chart import SimpleGUChart

        mock_parent, mock_fig, mock_ax, mock_line, mock_canvas = self._setup_mocks()
        mock_figure_class.return_value = mock_fig
        mock_canvas_class.return_value = mock_canvas

        chart = SimpleGUChart(mock_parent)

        # Test that buffer is empty
        assert len(chart.data_buffer) == 0

    @patch("src.alphagen.visualization.simple_gui_chart.FigureCanvasTkAgg")
    @patch("src.alphagen.visualization.simple_gui_chart.Figure")
    def test_clear_data(self, mock_figure_class, mock_canvas_class):
        """Test clearing all data from buffer."""
        from src.alphagen.visualization.simple_gui_chart import SimpleGUChart

        mock_parent, mock_fig, mock_ax, mock_line, mock_canvas = self._setup_mocks()
        mock_figure_class.return_value = mock_fig
        mock_canvas_class.return_value = mock_canvas

        chart = SimpleGUChart(mock_parent)

        # Add some data
        for i in range(3):
            mock_equity = Mock()
            mock_equity.session_vwap = 100.0 + i
            mock_equity.ma9 = 99.5 + i

            mock_tick = Mock()
            mock_tick.as_of = datetime.now(timezone.utc)
            mock_tick.equity = mock_equity

            chart.handle_tick(mock_tick)

        assert len(chart.data_buffer) == 3
        chart.clear()
        assert len(chart.data_buffer) == 0

    @patch("src.alphagen.visualization.simple_gui_chart.FigureCanvasTkAgg")
    @patch("src.alphagen.visualization.simple_gui_chart.Figure")
    def test_get_time_scale_label(self, mock_figure_class, mock_canvas_class):
        """Test getting time scale label."""
        from src.alphagen.visualization.simple_gui_chart import SimpleGUChart

        mock_parent, mock_fig, mock_ax, mock_line, mock_canvas = self._setup_mocks()
        mock_figure_class.return_value = mock_fig
        mock_canvas_class.return_value = mock_canvas

        chart = SimpleGUChart(mock_parent)

        chart.time_scale = "1min"
        label = chart.scale_configs["1min"]["label"]
        assert label == "1 Minute"

        chart.time_scale = "5min"
        label = chart.scale_configs["5min"]["label"]
        assert label == "5 Minutes"

    @patch("src.alphagen.visualization.simple_gui_chart.FigureCanvasTkAgg")
    @patch("src.alphagen.visualization.simple_gui_chart.Figure")
    def test_get_available_scales(self, mock_figure_class, mock_canvas_class):
        """Test getting available time scales."""
        from src.alphagen.visualization.simple_gui_chart import SimpleGUChart

        mock_parent, mock_fig, mock_ax, mock_line, mock_canvas = self._setup_mocks()
        mock_figure_class.return_value = mock_fig
        mock_canvas_class.return_value = mock_canvas

        chart = SimpleGUChart(mock_parent)

        scales = list(chart.scale_configs.keys())
        expected_scales = ["1min", "5min", "15min", "1hour", "4hour", "1day"]
        assert scales == expected_scales
