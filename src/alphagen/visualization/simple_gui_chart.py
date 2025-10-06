"""Simple GUI chart that works better with tkinter."""

from __future__ import annotations

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from collections import deque
from typing import Deque

from alphagen.core.events import NormalizedTick


class SimpleGUChart:
    """Simple chart that embeds in tkinter GUI."""

    def __init__(self, parent_frame: tk.Widget, max_points: int = 100):
        self.parent_frame = parent_frame
        self.max_points = max_points
        self.data_buffer: Deque[NormalizedTick] = deque(maxlen=max_points)
        self.time_scale = "1min"  # Default time scale
        self.scale_configs = {
            "1min": {"max_points": 60, "label": "1 Minute"},
            "5min": {"max_points": 60, "label": "5 Minutes"},
            "15min": {"max_points": 60, "label": "15 Minutes"},
            "1hour": {"max_points": 24, "label": "1 Hour"},
            "4hour": {"max_points": 18, "label": "4 Hours"},
            "1day": {"max_points": 24, "label": "1 Day"},
        }

        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)

        # Create tkinter canvas
        self.canvas = FigureCanvasTkAgg(self.fig, parent_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initialize plot
        (self.line_vwap,) = self.ax.plot(
            [], [], label="VWAP", color="#4caf50", linewidth=2
        )
        (self.line_ma9,) = self.ax.plot(
            [], [], label="MA9", color="#2196f3", linewidth=2
        )
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Price ($)")
        self.ax.set_title("Alpha-Gen QQQ VWAP vs MA9 - 1 Minute Scale")
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)

        # Set up time formatting
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        self.ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))

    def set_time_scale(self, scale: str) -> None:
        """Set the time scale for the chart."""
        if scale in self.scale_configs:
            self.time_scale = scale
            config = self.scale_configs[scale]
            # Update max points based on scale
            self.data_buffer = deque(self.data_buffer, maxlen=config["max_points"])
            self.ax.set_title(f"Alpha-Gen QQQ VWAP vs MA9 - {config['label']} Scale")

            # Update time axis formatting based on scale
            if scale == "1min":
                self.ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
            elif scale == "5min":
                self.ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            elif scale == "15min":
                self.ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            elif scale == "1hour":
                self.ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            elif scale == "4hour":
                self.ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
            elif scale == "1day":
                self.ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))

            self._update_plot()

    def handle_tick(self, tick: NormalizedTick) -> None:
        """Handle normalized tick data."""
        self.data_buffer.append(tick)
        self._update_plot()

    def _update_plot(self) -> None:
        """Update the plot with current data."""
        if not self.data_buffer:
            return

        # Extract data
        times = [t.as_of for t in self.data_buffer]
        vwap_values = [t.equity.session_vwap for t in self.data_buffer]
        ma9_values = [t.equity.ma9 for t in self.data_buffer]

        # Update lines
        self.line_vwap.set_data(times, vwap_values)
        self.line_ma9.set_data(times, ma9_values)

        # Auto-scale
        if times:
            self.ax.relim()
            self.ax.autoscale_view()

        # Redraw
        self.canvas.draw()

    def clear(self) -> None:
        """Clear the chart."""
        self.data_buffer.clear()
        self.line_vwap.set_data([], [])
        self.line_ma9.set_data([], [])
        self.canvas.draw()
