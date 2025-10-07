"""Simple GUI chart that works better with tkinter."""

from __future__ import annotations

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
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

        # Track min/max values for Y-axis scaling
        self.min_price = float("inf")
        self.max_price = float("-inf")

        self.scale_configs = {
            "1min": {"max_points": 60, "label": "1 Minute"},
            "5min": {"max_points": 60, "label": "5 Minutes"},
            "15min": {"max_points": 60, "label": "15 Minutes"},
            "1hour": {"max_points": 24, "label": "1 Hour"},
            "4hour": {"max_points": 18, "label": "4 Hours"},
            "1day": {"max_points": 24, "label": "1 Day"},
        }

        # Create matplotlib figure with higher DPI for better readability
        self.fig = Figure(figsize=(10, 6), dpi=120)
        self.ax = self.fig.add_subplot(111)

        # Set larger font sizes for better readability
        plt.rcParams.update(
            {
                "font.size": 12,
                "axes.titlesize": 14,
                "axes.labelsize": 12,
                "xtick.labelsize": 10,
                "ytick.labelsize": 10,
                "legend.fontsize": 11,
            }
        )

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

        # Set up time formatting with better spacing
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        self.ax.xaxis.set_major_locator(
            mdates.MinuteLocator(interval=10)
        )  # Show every 10 minutes by default
        self.ax.xaxis.set_minor_locator(
            mdates.MinuteLocator(interval=5)
        )  # Minor ticks every 5 minutes

        # Rotate labels for better readability and add padding
        self.ax.tick_params(axis="x", rotation=45, labelsize=10)
        self.ax.tick_params(axis="y", labelsize=10)

        # Add padding to prevent label cutoff
        self.fig.tight_layout(pad=2.0)

    def set_time_scale(self, scale: str) -> None:
        """Set the time scale for the chart."""
        if scale in self.scale_configs:
            self.time_scale = scale
            config = self.scale_configs[scale]
            # Update max points based on scale
            self.data_buffer = deque(self.data_buffer, maxlen=config["max_points"])
            self.ax.set_title(f"Alpha-Gen QQQ VWAP vs MA9 - {config['label']} Scale")

            # Update time axis formatting based on scale with better spacing
            if scale == "1min":
                self.ax.xaxis.set_major_locator(
                    mdates.MinuteLocator(interval=10)
                )  # Every 10 minutes
                self.ax.xaxis.set_minor_locator(
                    mdates.MinuteLocator(interval=5)
                )  # Minor every 5 minutes
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            elif scale == "5min":
                self.ax.xaxis.set_major_locator(
                    mdates.MinuteLocator(interval=30)
                )  # Every 30 minutes
                self.ax.xaxis.set_minor_locator(
                    mdates.MinuteLocator(interval=15)
                )  # Minor every 15 minutes
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            elif scale == "15min":
                self.ax.xaxis.set_major_locator(
                    mdates.HourLocator(interval=1)
                )  # Every hour
                self.ax.xaxis.set_minor_locator(
                    mdates.MinuteLocator(interval=30)
                )  # Minor every 30 minutes
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            elif scale == "1hour":
                self.ax.xaxis.set_major_locator(
                    mdates.HourLocator(interval=4)
                )  # Every 4 hours
                self.ax.xaxis.set_minor_locator(
                    mdates.HourLocator(interval=2)
                )  # Minor every 2 hours
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            elif scale == "4hour":
                self.ax.xaxis.set_major_locator(
                    mdates.HourLocator(interval=12)
                )  # Every 12 hours
                self.ax.xaxis.set_minor_locator(
                    mdates.HourLocator(interval=6)
                )  # Minor every 6 hours
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
            elif scale == "1day":
                self.ax.xaxis.set_major_locator(
                    mdates.DayLocator(interval=1)
                )  # Every day
                self.ax.xaxis.set_minor_locator(
                    mdates.HourLocator(interval=12)
                )  # Minor every 12 hours
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))

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

        # Update min/max price tracking
        all_prices = vwap_values + ma9_values
        if all_prices:
            current_min = min(all_prices)
            current_max = max(all_prices)
            self.min_price = min(self.min_price, current_min)
            self.max_price = max(self.max_price, current_max)

        # Update lines
        self.line_vwap.set_data(times, vwap_values)
        self.line_ma9.set_data(times, ma9_values)

        # Set Y-axis limits with reasonable padding
        if times and self.min_price != float("inf") and self.max_price != float("-inf"):
            price_range = self.max_price - self.min_price
            if price_range > 0:
                # Add 5% padding above and below
                padding = price_range * 0.05
                y_min = self.min_price - padding
                y_max = self.max_price + padding

                # Round to nice numbers
                y_min = round(y_min, 2)
                y_max = round(y_max, 2)

                self.ax.set_ylim(y_min, y_max)

                # Set Y-axis ticks to reasonable increments
                tick_range = y_max - y_min
                if tick_range > 20:
                    # Use $2 increments for very large ranges
                    tick_step = 2.0
                elif tick_range > 10:
                    # Use $1 increments for large ranges
                    tick_step = 1.0
                elif tick_range > 2:
                    # Use $0.50 increments for medium ranges
                    tick_step = 0.50
                elif tick_range > 0.5:
                    # Use $0.10 increments for small ranges
                    tick_step = 0.10
                else:
                    # Use $0.05 increments for very small ranges
                    tick_step = 0.05

                import numpy as np

                ticks = np.arange(
                    np.ceil(y_min / tick_step) * tick_step,
                    np.floor(y_max / tick_step) * tick_step + tick_step,
                    tick_step,
                )
                self.ax.set_yticks(ticks)

                # Format Y-axis labels to show appropriate decimal places
                if tick_step >= 1.0:
                    self.ax.yaxis.set_major_formatter(
                        plt.FuncFormatter(lambda x, p: f"${x:.0f}")
                    )
                elif tick_step >= 0.10:
                    self.ax.yaxis.set_major_formatter(
                        plt.FuncFormatter(lambda x, p: f"${x:.2f}")
                    )
                else:
                    self.ax.yaxis.set_major_formatter(
                        plt.FuncFormatter(lambda x, p: f"${x:.3f}")
                    )
            else:
                # Fallback to auto-scaling if no range
                self.ax.relim()
                self.ax.autoscale_view()
        else:
            # Auto-scale if no data yet
            self.ax.relim()
            self.ax.autoscale_view()

        # Redraw
        self.canvas.draw()

    def clear(self) -> None:
        """Clear the chart."""
        self.data_buffer.clear()
        self.line_vwap.set_data([], [])
        self.line_ma9.set_data([], [])

        # Reset price tracking
        self.min_price = float("inf")
        self.max_price = float("-inf")

        # Reset to auto-scaling
        self.ax.relim()
        self.ax.autoscale_view()

        self.canvas.draw()
