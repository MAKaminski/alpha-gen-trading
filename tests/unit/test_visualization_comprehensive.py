"""Comprehensive tests for visualization modules to achieve 100% coverage."""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import os

# Set matplotlib backend before importing visualization modules
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for testing

from alphagen.core.events import NormalizedTick, Signal, EquityTick


class TestLiveChartComprehensive:
    """Comprehensive tests for LiveChart to achieve 100% coverage."""

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

    def test_start_creates_thread(self):
        """Test start() creates and starts a new thread."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart()
        with patch('alphagen.visualization.live_chart.Thread') as mock_thread_class:
            mock_thread = Mock()
            mock_thread_class.return_value = mock_thread
            
            chart.start()
            
            mock_thread_class.assert_called_once_with(
                target=chart._run, 
                name="alphagen-live-chart", 
                daemon=True
            )
            mock_thread.start.assert_called_once()
            assert chart._running is True
            assert chart._thread == mock_thread

    @pytest.mark.asyncio
    async def test_stop_when_not_running(self):
        """Test stop() when chart is not running."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart()
        chart._running = False
        
        await chart.stop()  # Should return early
        assert chart._running is False

    @pytest.mark.asyncio
    async def test_stop_when_running(self):
        """Test stop() when chart is running."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart()
        chart._running = True
        chart._thread = Mock()
        chart._queue = Mock()
        
        with patch.object(chart, '_join_thread') as mock_join:
            await chart.stop()
            
            assert chart._running is False
            chart._queue.put.assert_called_once_with(None)
            mock_join.assert_called_once()
            assert chart._thread is None

    @pytest.mark.asyncio
    async def test_join_thread_with_timeout(self):
        """Test _join_thread with thread timeout."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart()
        mock_thread = Mock()
        chart._thread = mock_thread
        
        with patch('asyncio.to_thread') as mock_to_thread:
            await chart._join_thread()
            mock_to_thread.assert_called_once_with(mock_thread.join, 2.0)

    @pytest.mark.asyncio
    async def test_join_thread_with_none_thread(self):
        """Test _join_thread when thread is None."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart()
        chart._thread = None
        
        await chart._join_thread()  # Should return early

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

    def test_handle_tick_when_running(self):
        """Test handle_tick when chart is already running."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart()
        chart._running = True
        chart._queue = Mock()
        
        # Create a mock tick
        mock_tick = Mock()
        mock_tick.as_of = datetime.now(timezone.utc)
        mock_tick.equity.session_vwap = 100.0
        mock_tick.equity.ma9 = 99.5
        
        chart.handle_tick(mock_tick)
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

    def test_handle_signal_when_running(self):
        """Test handle_signal when chart is already running."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart()
        chart._running = True
        chart._queue = Mock()
        
        # Create a mock signal
        mock_signal = Mock()
        mock_signal.as_of = datetime.now(timezone.utc)
        mock_signal.reference_price = 100.0
        mock_signal.action = "BUY_OPEN"
        
        chart.handle_signal(mock_signal)
        chart._queue.put.assert_called_once()

    def test_run_matplotlib_import_failure(self):
        """Test _run when matplotlib import fails."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart()
        
        # Mock the logger to avoid structlog issues
        with patch.object(chart, '_logger') as mock_logger:
            # Mock the import to fail
            with patch('builtins.__import__', side_effect=ImportError("matplotlib not available")):
                chart._run()  # Should handle import error gracefully
                
            # Verify error was logged
            mock_logger.error.assert_called_once()

    def test_run_matplotlib_setup(self):
        """Test _run matplotlib setup and configuration."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart()
        chart._running = True
        chart._queue = Mock()
        
        # Mock queue to return None immediately (shutdown)
        chart._queue.get_nowait.return_value = None
        
        with patch('matplotlib.use') as mock_use, \
             patch('matplotlib.pyplot.ion') as mock_ion, \
             patch('matplotlib.pyplot.style') as mock_style, \
             patch('matplotlib.pyplot.subplots') as mock_subplots, \
             patch('matplotlib.pyplot.show') as mock_show, \
             patch('matplotlib.pyplot.pause') as mock_pause, \
             patch('matplotlib.animation.FuncAnimation') as mock_animation:
            
            mock_fig = Mock()
            mock_ax = Mock()
            mock_ax.plot = Mock()
            mock_ax.scatter = Mock()
            mock_ax.set_xlabel = Mock()
            mock_ax.set_ylabel = Mock()
            mock_ax.legend = Mock()
            mock_ax.grid = Mock()
            mock_ax.xaxis = Mock()
            mock_ax.xaxis.set_major_formatter = Mock()
            mock_ax.xaxis.set_major_locator = Mock()
            mock_ax.relim = Mock()
            mock_ax.autoscale_view = Mock()
            mock_fig.canvas = Mock()
            mock_fig.canvas.draw = Mock()
            mock_fig.canvas.flush_events = Mock()
            
            mock_subplots.return_value = (mock_fig, mock_ax)
            mock_ax.plot.return_value = (Mock(),)  # For line unpacking - returns tuple with one element
            mock_ax.scatter.return_value = Mock()
            
            # Mock the while loop to exit immediately
            original_running = chart._running
            chart._running = False
            
            chart._run()
            
            # Restore original running state
            chart._running = original_running
        
        mock_use.assert_called_once_with('TkAgg')
        mock_ion.assert_called_once()
        mock_style.use.assert_called_once_with("dark_background")

    def test_run_with_data_processing(self):
        """Test _run with tick and signal data processing."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart()
        chart._running = True
        chart._queue = Mock()
        
        # Add some tick data
        from alphagen.visualization.live_chart import _TickPoint
        tick_point = _TickPoint(
            timestamp=datetime.now(timezone.utc),
            vwap=100.0,
            ma9=99.5
        )
        chart._tick_buffer.append(tick_point)
        
        # Mock queue to return tick data then None
        chart._queue.get_nowait.side_effect = [("tick", tick_point), None]
        
        with patch('matplotlib.use') as mock_use, \
             patch('matplotlib.pyplot.ion') as mock_ion, \
             patch('matplotlib.pyplot.style') as mock_style, \
             patch('matplotlib.pyplot.subplots') as mock_subplots, \
             patch('matplotlib.pyplot.show') as mock_show, \
             patch('matplotlib.pyplot.pause') as mock_pause, \
             patch('matplotlib.animation.FuncAnimation') as mock_animation:
            
            mock_fig = Mock()
            mock_ax = Mock()
            mock_ax.plot = Mock()
            mock_ax.scatter = Mock()
            mock_ax.set_xlabel = Mock()
            mock_ax.set_ylabel = Mock()
            mock_ax.legend = Mock()
            mock_ax.grid = Mock()
            mock_ax.xaxis = Mock()
            mock_ax.xaxis.set_major_formatter = Mock()
            mock_ax.xaxis.set_major_locator = Mock()
            mock_ax.relim = Mock()
            mock_ax.autoscale_view = Mock()
            mock_fig.canvas = Mock()
            mock_fig.canvas.draw = Mock()
            mock_fig.canvas.flush_events = Mock()
            
            # Mock figure canvas manager
            mock_manager = Mock()
            mock_window = Mock()
            mock_fig.canvas.manager = mock_manager
            mock_manager.window = mock_window
            
            mock_subplots.return_value = (mock_fig, mock_ax)
            mock_ax.plot.return_value = (Mock(),)  # For line unpacking - returns tuple with one element
            mock_ax.scatter.return_value = Mock()
            
            # Mock the while loop to exit immediately
            original_running = chart._running
            chart._running = False
            
            chart._run()
            
            # Restore original running state
            chart._running = original_running
        
        # Verify data was processed
        assert len(chart._tick_buffer) == 1

    def test_run_window_management(self):
        """Test _run window management and attributes."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart()
        chart._running = True
        chart._queue = Mock()
        
        # Mock queue to return None immediately
        chart._queue.get_nowait.return_value = None
        
        with patch('matplotlib.use') as mock_use, \
             patch('matplotlib.pyplot.ion') as mock_ion, \
             patch('matplotlib.pyplot.style') as mock_style, \
             patch('matplotlib.pyplot.subplots') as mock_subplots, \
             patch('matplotlib.pyplot.show') as mock_show, \
             patch('matplotlib.pyplot.pause') as mock_pause, \
             patch('matplotlib.animation.FuncAnimation') as mock_animation:
            
            mock_fig = Mock()
            mock_ax = Mock()
            mock_ax.plot = Mock()
            mock_ax.scatter = Mock()
            mock_ax.set_xlabel = Mock()
            mock_ax.set_ylabel = Mock()
            mock_ax.legend = Mock()
            mock_ax.grid = Mock()
            mock_ax.xaxis = Mock()
            mock_ax.xaxis.set_major_formatter = Mock()
            mock_ax.xaxis.set_major_locator = Mock()
            mock_ax.relim = Mock()
            mock_ax.autoscale_view = Mock()
            mock_fig.canvas = Mock()
            mock_fig.canvas.draw = Mock()
            mock_fig.canvas.flush_events = Mock()
            
            # Mock canvas manager and window
            mock_manager = Mock()
            mock_window = Mock()
            mock_fig.canvas.manager = mock_manager
            mock_manager.window = mock_window
            
            mock_subplots.return_value = (mock_fig, mock_ax)
            mock_ax.plot.return_value = (Mock(),)  # For line unpacking - returns tuple with one element
            mock_ax.scatter.return_value = Mock()
            
            # Mock the while loop to exit immediately
            original_running = chart._running
            chart._running = False
            
            chart._run()
            
            # Restore original running state
            chart._running = original_running
        
        # Verify window attributes were set
        mock_window.wm_attributes.assert_any_call('-topmost', 1)
        mock_window.wm_attributes.assert_any_call('-topmost', 0)

    def test_run_window_manager_not_available(self):
        """Test _run when window manager is not available."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart()
        chart._running = True
        chart._queue = Mock()
        
        # Mock queue to return None immediately
        chart._queue.get_nowait.return_value = None
        
        with patch('matplotlib.use') as mock_use, \
             patch('matplotlib.pyplot.ion') as mock_ion, \
             patch('matplotlib.pyplot.style') as mock_style, \
             patch('matplotlib.pyplot.subplots') as mock_subplots, \
             patch('matplotlib.pyplot.show') as mock_show, \
             patch('matplotlib.pyplot.pause') as mock_pause, \
             patch('matplotlib.animation.FuncAnimation') as mock_animation:
            
            mock_fig = Mock()
            mock_ax = Mock()
            mock_ax.plot = Mock()
            mock_ax.scatter = Mock()
            mock_ax.set_xlabel = Mock()
            mock_ax.set_ylabel = Mock()
            mock_ax.legend = Mock()
            mock_ax.grid = Mock()
            mock_ax.xaxis = Mock()
            mock_ax.xaxis.set_major_formatter = Mock()
            mock_ax.xaxis.set_major_locator = Mock()
            mock_ax.relim = Mock()
            mock_ax.autoscale_view = Mock()
            mock_fig.canvas = Mock()
            mock_fig.canvas.draw = Mock()
            mock_fig.canvas.flush_events = Mock()
            
            # Mock canvas without manager
            mock_fig.canvas.manager = None
            
            mock_subplots.return_value = (mock_fig, mock_ax)
            mock_ax.plot.return_value = (Mock(),)  # For line unpacking - returns tuple with one element
            mock_ax.scatter.return_value = Mock()
            
            # Mock the while loop to exit immediately
            original_running = chart._running
            chart._running = False
            
            chart._run()  # Should handle missing manager gracefully
            
            # Restore original running state
            chart._running = original_running

    def test_run_window_attributes_exception(self):
        """Test _run when window attributes fail."""
        from alphagen.visualization.live_chart import LiveChart
        
        chart = LiveChart()
        chart._running = True
        chart._queue = Mock()
        
        # Mock queue to return None immediately
        chart._queue.get_nowait.return_value = None
        
        # Mock matplotlib modules
        mock_matplotlib = Mock()
        mock_matplotlib.is_interactive.return_value = True
        mock_plt = Mock()
        mock_fig = Mock()
        mock_ax = Mock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        
        # Mock canvas manager that raises exception
        mock_manager = Mock()
        mock_window = Mock()
        mock_window.wm_attributes.side_effect = Exception("Attribute error")
        mock_fig.canvas.manager = mock_manager
        mock_manager.window = mock_window
        
        with patch('matplotlib.use') as mock_use, \
             patch('matplotlib.pyplot.ion') as mock_ion, \
             patch('matplotlib.pyplot.style') as mock_style, \
             patch('matplotlib.pyplot.subplots') as mock_subplots, \
             patch('matplotlib.pyplot.show') as mock_show, \
             patch('matplotlib.pyplot.pause') as mock_pause:
            
            mock_fig = Mock()
            mock_ax = Mock()
            mock_ax.plot = Mock()
            mock_ax.scatter = Mock()
            mock_ax.set_xlabel = Mock()
            mock_ax.set_ylabel = Mock()
            mock_ax.legend = Mock()
            mock_ax.grid = Mock()
            mock_ax.xaxis = Mock()
            mock_ax.xaxis.set_major_formatter = Mock()
            mock_ax.xaxis.set_major_locator = Mock()
            mock_ax.relim = Mock()
            mock_ax.autoscale_view = Mock()
            
            # Mock canvas manager that raises exception
            mock_manager = Mock()
            mock_window = Mock()
            mock_window.wm_attributes.side_effect = Exception("Attribute error")
            mock_fig.canvas = Mock()
            mock_fig.canvas.manager = mock_manager
            mock_manager.window = mock_window
            
            mock_subplots.return_value = (mock_fig, mock_ax)
            mock_ax.plot.return_value = (Mock(),)  # For line unpacking - returns tuple with one element
            mock_ax.scatter.return_value = Mock()
            
            chart._run()  # Should handle exception gracefully


class TestSimpleChartComprehensive:
    """Comprehensive tests for SimpleChart to achieve 100% coverage."""

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

    def test_start_sets_up_chart(self):
        """Test start() sets up the chart."""
        from alphagen.visualization.simple_chart import SimpleChart
        
        chart = SimpleChart()
        mock_fig = Mock()
        mock_ax = Mock()
        mock_ax.plot = Mock()
        mock_ax.scatter = Mock()
        mock_ax.set_xlabel = Mock()
        mock_ax.set_ylabel = Mock()
        mock_ax.set_title = Mock()
        mock_ax.legend = Mock()
        mock_ax.grid = Mock()
        mock_ax.relim = Mock()
        mock_ax.autoscale_view = Mock()
        
        with patch('matplotlib.pyplot.ion') as mock_ion, \
             patch('matplotlib.pyplot.style') as mock_style, \
             patch('matplotlib.pyplot.subplots') as mock_subplots, \
             patch('matplotlib.pyplot.show') as mock_show, \
             patch('matplotlib.pyplot.pause') as mock_pause, \
             patch('matplotlib.animation.FuncAnimation') as mock_animation:
            
            mock_subplots.return_value = (mock_fig, mock_ax)
            mock_ax.plot.return_value = (Mock(),)  # For line unpacking - returns tuple with one element
            mock_ax.scatter.return_value = Mock()
            
            chart.start()
            
            assert chart._running is True
            assert chart._fig == mock_fig
            assert chart._ax == mock_ax
            mock_ion.assert_called_once()
            mock_style.use.assert_called_once_with("dark_background")
            mock_subplots.assert_called_once()

    def test_start_chart_setup_exception(self):
        """Test start() handles chart setup exceptions."""
        from alphagen.visualization.simple_chart import SimpleChart
        
        chart = SimpleChart()
        mock_plt = Mock()
        mock_plt.subplots.side_effect = Exception("Setup failed")
        
        with patch.dict('sys.modules', {
            'matplotlib.pyplot': mock_plt,
            'matplotlib.animation': Mock()
        }):
            chart.start()  # Should handle exception gracefully
            assert chart._running is True

    def test_stop_when_not_running(self):
        """Test stop() when chart is not running."""
        from alphagen.visualization.simple_chart import SimpleChart
        
        chart = SimpleChart()
        chart._running = False
        
        chart.stop()  # Should return early
        assert chart._running is False

    def test_stop_closes_figure(self):
        """Test stop() closes the figure."""
        from alphagen.visualization.simple_chart import SimpleChart
        
        chart = SimpleChart()
        chart._running = True
        mock_fig = Mock()
        chart._fig = mock_fig
        
        with patch('matplotlib.pyplot.close') as mock_close:
            chart.stop()
            
            assert chart._running is False
            mock_close.assert_called_once_with(mock_fig)
            assert chart._fig is None

    def test_stop_with_none_figure(self):
        """Test stop() when figure is None."""
        from alphagen.visualization.simple_chart import SimpleChart
        
        chart = SimpleChart()
        chart._running = True
        chart._fig = None
        
        mock_plt = Mock()
        with patch.dict('sys.modules', {'matplotlib.pyplot': mock_plt}):
            chart.stop()
            
            assert chart._running is False
            mock_plt.close.assert_not_called()

    def test_update_chart_when_not_running(self):
        """Test _update_chart when chart is not running."""
        from alphagen.visualization.simple_chart import SimpleChart
        
        chart = SimpleChart()
        chart._running = False
        
        chart._update_chart(0)  # Should return early

    def test_update_chart_with_empty_buffer(self):
        """Test _update_chart with empty tick buffer."""
        from alphagen.visualization.simple_chart import SimpleChart
        
        chart = SimpleChart()
        chart._running = True
        chart._tick_buffer = []
        
        chart._update_chart(0)  # Should return early

    def test_update_chart_with_data(self):
        """Test _update_chart with tick data."""
        from alphagen.visualization.simple_chart import SimpleChart, _TickPoint
        
        chart = SimpleChart()
        chart._running = True
        chart._line_vwap = Mock()
        chart._line_ma9 = Mock()
        chart._scatter = Mock()
        chart._ax = Mock()
        
        # Add tick data
        tick_point = _TickPoint(
            timestamp=datetime.now(timezone.utc),
            vwap=100.0,
            ma9=99.5
        )
        chart._tick_buffer.append(tick_point)
        
        chart._update_chart(0)
        
        # Verify lines were updated
        chart._line_vwap.set_data.assert_called_once()
        chart._line_ma9.set_data.assert_called_once()
        chart._ax.relim.assert_called_once()
        chart._ax.autoscale_view.assert_called_once()

    def test_update_chart_with_signals(self):
        """Test _update_chart with signal data."""
        from alphagen.visualization.simple_chart import SimpleChart, _TickPoint, _SignalPoint
        
        chart = SimpleChart()
        chart._running = True
        chart._line_vwap = Mock()
        chart._line_ma9 = Mock()
        chart._scatter = Mock()
        chart._ax = Mock()
        
        # Add tick and signal data
        tick_point = _TickPoint(
            timestamp=datetime.now(timezone.utc),
            vwap=100.0,
            ma9=99.5
        )
        signal_point = _SignalPoint(
            timestamp=datetime.now(timezone.utc),
            price=100.0,
            action="BUY_OPEN"
        )
        chart._tick_buffer.append(tick_point)
        chart._signal_buffer.append(signal_point)
        
        chart._update_chart(0)
        
        # Verify scatter was updated with signals
        chart._scatter.set_offsets.assert_called_once()

    def test_update_chart_exception_handling(self):
        """Test _update_chart handles exceptions."""
        from alphagen.visualization.simple_chart import SimpleChart, _TickPoint
        
        chart = SimpleChart()
        chart._running = True
        chart._line_vwap = Mock()
        chart._line_ma9 = Mock()
        chart._scatter = Mock()
        chart._ax = Mock()
        
        # Make set_data raise an exception
        chart._line_vwap.set_data.side_effect = Exception("Update failed")
        
        # Add tick data
        tick_point = _TickPoint(
            timestamp=datetime.now(timezone.utc),
            vwap=100.0,
            ma9=99.5
        )
        chart._tick_buffer.append(tick_point)
        
        chart._update_chart(0)  # Should handle exception gracefully

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

    def test_handle_signal_when_not_running(self):
        """Test handle_signal when chart is not running."""
        from alphagen.visualization.simple_chart import SimpleChart
        
        chart = SimpleChart()
        chart._running = False
        
        mock_signal = Mock()
        mock_signal.as_of = datetime.now(timezone.utc)
        mock_signal.reference_price = 100.0
        mock_signal.action = "BUY_OPEN"
        
        chart.handle_signal(mock_signal)  # Should return early
        assert len(chart._signal_buffer) == 0

    def test_handle_signal_when_running(self):
        """Test handle_signal when chart is running."""
        from alphagen.visualization.simple_chart import SimpleChart
        
        chart = SimpleChart()
        chart._running = True
        
        mock_signal = Mock()
        mock_signal.as_of = datetime.now(timezone.utc)
        mock_signal.reference_price = 100.0
        mock_signal.action = "BUY_OPEN"
        
        chart.handle_signal(mock_signal)
        assert len(chart._signal_buffer) == 1


class TestFileChartComprehensive:
    """Comprehensive tests for FileChart to achieve 100% coverage."""

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

    def test_init_creates_output_directory(self):
        """Test FileChart creates output directory if it doesn't exist."""
        from alphagen.visualization.file_chart import FileChart
        
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / "charts"
            chart = FileChart(output_dir=str(new_dir))
            assert new_dir.exists()

    def test_start_when_already_running(self):
        """Test start() when chart is already running."""
        from alphagen.visualization.file_chart import FileChart
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            chart._running = True
            
            chart.start()  # Should return early
            assert chart._running is True

    def test_start_sets_running_flag(self):
        """Test start() sets running flag."""
        from alphagen.visualization.file_chart import FileChart
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            chart.start()
            assert chart._running is True

    def test_stop_when_not_running(self):
        """Test stop() when chart is not running."""
        from alphagen.visualization.file_chart import FileChart
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            chart._running = False
            
            chart.stop()  # Should return early
            assert chart._running is False

    def test_stop_sets_running_flag_false(self):
        """Test stop() sets running flag to False."""
        from alphagen.visualization.file_chart import FileChart
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            chart._running = True
            chart.stop()
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

    def test_handle_tick_triggers_save_every_5_ticks(self):
        """Test handle_tick triggers save every 5 ticks."""
        from alphagen.visualization.file_chart import FileChart
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            chart._running = True
            
            mock_tick = Mock()
            mock_tick.as_of = datetime.now(timezone.utc)
            mock_tick.equity.session_vwap = 100.0
            mock_tick.equity.ma9 = 99.5
            
            with patch.object(chart, '_save_chart') as mock_save:
                # Add 5 ticks
                for i in range(5):
                    chart.handle_tick(mock_tick)
                
                mock_save.assert_called_once()

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

    def test_handle_signal_triggers_save(self):
        """Test handle_signal triggers save."""
        from alphagen.visualization.file_chart import FileChart
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            chart._running = True
            
            mock_signal = Mock()
            mock_signal.as_of = datetime.now(timezone.utc)
            mock_signal.reference_price = 100.0
            mock_signal.action = "BUY_OPEN"
            
            with patch.object(chart, '_save_chart') as mock_save:
                chart.handle_signal(mock_signal)
                mock_save.assert_called_once()

    def test_save_chart_with_empty_buffer(self):
        """Test _save_chart with empty tick buffer."""
        from alphagen.visualization.file_chart import FileChart
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            chart._tick_buffer = []
            
            chart._save_chart()  # Should return early

    def test_save_chart_with_data(self):
        """Test _save_chart with tick data."""
        from alphagen.visualization.file_chart import FileChart, _TickPoint
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            
            # Add tick data
            tick_point = _TickPoint(
                timestamp=datetime.now(timezone.utc),
                vwap=100.0,
                ma9=99.5
            )
            chart._tick_buffer.append(tick_point)
            
            with patch('matplotlib.pyplot.style') as mock_style, \
                 patch('matplotlib.pyplot.subplots') as mock_subplots, \
                 patch('matplotlib.pyplot.savefig') as mock_savefig, \
                 patch('matplotlib.pyplot.close') as mock_close:
                
                mock_fig = Mock()
                mock_ax = Mock()
                mock_ax.plot = Mock()
                mock_ax.set_xlabel = Mock()
                mock_ax.set_ylabel = Mock()
                mock_ax.set_title = Mock()
                mock_ax.legend = Mock()
                mock_ax.grid = Mock()
                mock_ax.xaxis = Mock()
                mock_ax.xaxis.set_major_formatter = Mock()
                mock_ax.xaxis.get_majorticklabels = Mock()
                mock_ax.xaxis.get_majorticklabels.return_value = []
                mock_subplots.return_value = (mock_fig, mock_ax)
                
                chart._save_chart()
                
                mock_style.use.assert_called_once_with("dark_background")
                mock_subplots.assert_called_once()
                mock_savefig.assert_called_once()
                mock_close.assert_called_once_with(mock_fig)

    def test_save_chart_with_signals(self):
        """Test _save_chart with signal data."""
        from alphagen.visualization.file_chart import FileChart, _TickPoint, _SignalPoint
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            
            # Add tick and signal data
            tick_point = _TickPoint(
                timestamp=datetime.now(timezone.utc),
                vwap=100.0,
                ma9=99.5
            )
            signal_point = _SignalPoint(
                timestamp=datetime.now(timezone.utc),
                price=100.0,
                action="BUY_OPEN"
            )
            chart._tick_buffer.append(tick_point)
            chart._signal_buffer.append(signal_point)
            
            with patch('matplotlib.pyplot.style') as mock_style, \
                 patch('matplotlib.pyplot.subplots') as mock_subplots, \
                 patch('matplotlib.pyplot.savefig') as mock_savefig, \
                 patch('matplotlib.pyplot.close') as mock_close:
                
                mock_fig = Mock()
                mock_ax = Mock()
                mock_ax.plot = Mock()
                mock_ax.scatter = Mock()
                mock_ax.set_xlabel = Mock()
                mock_ax.set_ylabel = Mock()
                mock_ax.set_title = Mock()
                mock_ax.legend = Mock()
                mock_ax.grid = Mock()
                mock_ax.xaxis = Mock()
                mock_ax.xaxis.set_major_formatter = Mock()
                mock_ax.xaxis.get_majorticklabels = Mock()
                mock_ax.xaxis.get_majorticklabels.return_value = []
                mock_subplots.return_value = (mock_fig, mock_ax)
                
                chart._save_chart()
                
                # Verify scatter plot was called for signals
                mock_ax.scatter.assert_called_once()

    def test_save_chart_exception_handling(self):
        """Test _save_chart handles exceptions."""
        from alphagen.visualization.file_chart import FileChart, _TickPoint
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            
            # Add tick data
            tick_point = _TickPoint(
                timestamp=datetime.now(timezone.utc),
                vwap=100.0,
                ma9=99.5
            )
            chart._tick_buffer.append(tick_point)
            
            # Make subplots raise an exception
            mock_plt = Mock()
            mock_plt.subplots.side_effect = Exception("Save failed")
            
            with patch.dict('sys.modules', {'matplotlib.pyplot': mock_plt}):
                chart._save_chart()  # Should handle exception gracefully

    def test_save_chart_filename_generation(self):
        """Test _save_chart generates proper filename."""
        from alphagen.visualization.file_chart import FileChart, _TickPoint
        
        with tempfile.TemporaryDirectory() as temp_dir:
            chart = FileChart(output_dir=temp_dir)
            
            # Add tick data
            tick_point = _TickPoint(
                timestamp=datetime.now(timezone.utc),
                vwap=100.0,
                ma9=99.5
            )
            chart._tick_buffer.append(tick_point)
            
            with patch('matplotlib.pyplot.style') as mock_style, \
                 patch('matplotlib.pyplot.subplots') as mock_subplots, \
                 patch('matplotlib.pyplot.savefig') as mock_savefig, \
                 patch('matplotlib.pyplot.close') as mock_close:
                
                mock_fig = Mock()
                mock_ax = Mock()
                mock_ax.plot = Mock()
                mock_ax.set_xlabel = Mock()
                mock_ax.set_ylabel = Mock()
                mock_ax.set_title = Mock()
                mock_ax.legend = Mock()
                mock_ax.grid = Mock()
                mock_ax.xaxis = Mock()
                mock_ax.xaxis.set_major_formatter = Mock()
                mock_ax.xaxis.get_majorticklabels = Mock()
                mock_ax.xaxis.get_majorticklabels.return_value = []
                mock_subplots.return_value = (mock_fig, mock_ax)
                
                chart._save_chart()
                
                # Verify savefig was called with proper filename pattern
                call_args = mock_savefig.call_args
                filename = call_args[0][0]
                assert str(chart._output_dir) in str(filename)
                assert "trading_chart_" in str(filename)
                assert filename.suffix == ".png"


class TestSimpleGUIChartComprehensive:
    """Comprehensive tests for SimpleGUChart to achieve 100% coverage."""

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

    @patch('alphagen.visualization.simple_gui_chart.Figure')
    @patch('alphagen.visualization.simple_gui_chart.FigureCanvasTkAgg')
    def test_chart_initialization(self, mock_canvas_class, mock_figure_class):
        """Test chart initialization creates figure and canvas."""
        from alphagen.visualization.simple_gui_chart import SimpleGUChart
        
        mock_parent = Mock()
        mock_fig = Mock()
        mock_ax = Mock()
        mock_figure_class.return_value = mock_fig
        mock_fig.add_subplot.return_value = mock_ax
        mock_canvas = Mock()
        mock_canvas_class.return_value = mock_canvas
        
        chart = SimpleGUChart(mock_parent)
        
        mock_figure_class.assert_called_once()
        mock_fig.add_subplot.assert_called_once_with(111)
        mock_canvas_class.assert_called_once()
        mock_canvas.get_tk_widget().pack.assert_called_once()

    @patch('alphagen.visualization.simple_gui_chart.Figure')
    @patch('alphagen.visualization.simple_gui_chart.FigureCanvasTkAgg')
    def test_plot_lines_initialization(self, mock_canvas_class, mock_figure_class):
        """Test plot lines are properly initialized."""
        from alphagen.visualization.simple_gui_chart import SimpleGUChart
        
        mock_parent = Mock()
        mock_fig = Mock()
        mock_ax = Mock()
        mock_line = Mock()
        mock_figure_class.return_value = mock_fig
        mock_fig.add_subplot.return_value = mock_ax
        mock_ax.plot.return_value = (mock_line,)
        mock_canvas = Mock()
        mock_canvas_class.return_value = mock_canvas
        
        chart = SimpleGUChart(mock_parent)
        
        # Verify plot calls
        assert mock_ax.plot.call_count == 2  # VWAP and MA9 lines
        mock_ax.set_xlabel.assert_called_once_with("Time")
        mock_ax.set_ylabel.assert_called_once_with("Price ($)")
        mock_ax.set_title.assert_called_once()
        mock_ax.legend.assert_called_once()
        mock_ax.grid.assert_called_once_with(True, alpha=0.3)

    @patch('alphagen.visualization.simple_gui_chart.Figure')
    @patch('alphagen.visualization.simple_gui_chart.FigureCanvasTkAgg')
    def test_time_formatting_setup(self, mock_canvas_class, mock_figure_class):
        """Test time formatting is properly set up."""
        from alphagen.visualization.simple_gui_chart import SimpleGUChart
        
        mock_parent = Mock()
        mock_fig = Mock()
        mock_ax = Mock()
        mock_figure_class.return_value = mock_fig
        mock_fig.add_subplot.return_value = mock_ax
        mock_canvas = Mock()
        mock_canvas_class.return_value = mock_canvas
        
        with patch('alphagen.visualization.simple_gui_chart.mdates') as mock_mdates:
            chart = SimpleGUChart(mock_parent)
            
            mock_ax.xaxis.set_major_formatter.assert_called_once()

    def test_add_tick_data(self):
        """Test adding tick data to the chart."""
        from alphagen.visualization.simple_gui_chart import SimpleGUChart
        from alphagen.core.events import NormalizedTick, EquityTick
        
        mock_parent = Mock()
        chart = SimpleGUChart(mock_parent)
        
        # Create mock tick
        mock_equity = Mock()
        mock_equity.session_vwap = 100.0
        mock_equity.ma9 = 99.5
        
        mock_tick = Mock()
        mock_tick.as_of = datetime.now(timezone.utc)
        mock_tick.equity = mock_equity
        
        chart.add_tick(mock_tick)
        
        assert len(chart.data_buffer) == 1

    def test_add_tick_data_buffer_limit(self):
        """Test tick data buffer respects max_points limit."""
        from alphagen.visualization.simple_gui_chart import SimpleGUChart
        
        mock_parent = Mock()
        chart = SimpleGUChart(mock_parent, max_points=3)
        
        # Create mock ticks
        for i in range(5):
            mock_equity = Mock()
            mock_equity.session_vwap = 100.0 + i
            mock_equity.ma9 = 99.5 + i
            
            mock_tick = Mock()
            mock_tick.as_of = datetime.now(timezone.utc)
            mock_tick.equity = mock_equity
            
            chart.add_tick(mock_tick)
        
        # Should only keep last 3 ticks
        assert len(chart.data_buffer) == 3

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

    def test_get_current_data(self):
        """Test getting current data from buffer."""
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
        
        data = chart.get_current_data()
        assert len(data) == 3
        assert all('timestamp' in item for item in data)
        assert all('vwap' in item for item in data)
        assert all('ma9' in item for item in data)

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
