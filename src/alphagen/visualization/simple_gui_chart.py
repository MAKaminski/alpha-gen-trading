"""Simple GUI chart that works better with tkinter."""

from __future__ import annotations

import asyncio
import tkinter as tk
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from collections import deque
from typing import Deque
from sqlmodel import select

from alphagen.core.events import NormalizedTick


class SimpleGUChart:
    """Simple chart that embeds in tkinter GUI."""

    def __init__(self, parent_frame: tk.Widget, max_points: int = 4320):  # 3 days of minute data
        self.parent_frame = parent_frame
        self.max_points = max_points
        self.data_buffer: Deque[NormalizedTick] = deque(maxlen=max_points)
        self.time_scale = "3day"  # Default to 3-day view

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
            "3day": {"max_points": 72, "label": "3 Days"},
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
        # Don't pack here - will be packed when shown in GUI

        # Initialize plot
        (self.line_price,) = self.ax.plot(
            [], [], label="Price", color="#ff6b35", linewidth=2
        )
        (self.line_vwap,) = self.ax.plot(
            [], [], label="VWAP", color="#4caf50", linewidth=2
        )
        (self.line_ma9,) = self.ax.plot(
            [], [], label="MA9", color="#2196f3", linewidth=2
        )
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Price ($)")
        self.ax.set_title("Alpha-Gen QQQ Price vs VWAP vs MA9 - 3 Day Scale")
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)

        # Set up time formatting with better spacing
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        # Limit to maximum 6 labels on X-axis to prevent crowding
        self.ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=6))

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

            # Update time axis formatting based on scale - limit to max 6 labels
            if scale == "1min":
                # Limit to maximum 6 labels on X-axis
                self.ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=6))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            elif scale == "5min":
                # Limit to maximum 6 labels on X-axis
                self.ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=6))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            elif scale == "15min":
                # Limit to maximum 6 labels on X-axis
                self.ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=6))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            elif scale == "1hour":
                # Limit to maximum 6 labels on X-axis
                self.ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=6))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            elif scale == "4hour":
                # Limit to maximum 6 labels on X-axis
                self.ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=6))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
            elif scale == "1day":
                # Limit to maximum 6 labels on X-axis
                self.ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=6))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
            elif scale == "3day":
                # Show days for 3-day view
                self.ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=6))
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))

            self._update_plot()

    def handle_tick(self, tick: NormalizedTick) -> None:
        """Handle normalized tick data."""
        self.data_buffer.append(tick)
        self._update_plot()

    async def load_historical_data(self) -> None:
        """Load last 3 days of historical data from database."""
        from alphagen.storage import session_scope
        from alphagen.storage import EquityTickRow
        from alphagen.core.events import EquityTick, OptionQuote

        try:
            # Get last 3 days of data
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=3)

            async with session_scope() as session:
                # Query equity tick data from last 3 days
                statement = select(EquityTickRow).where(
                    EquityTickRow.as_of >= cutoff_time,
                    EquityTickRow.price > 0  # Filter out zero prices
                ).order_by(EquityTickRow.as_of)
                result = await session.exec(statement)
                rows = result.all()

                # Convert to NormalizedTick objects
                for row in rows:
                    equity_tick = EquityTick(
                        symbol=row.symbol,
                        price=row.price,
                        session_vwap=row.session_vwap,
                        ma9=row.ma9,
                        as_of=row.as_of
                    )

                    # Create a dummy option quote (not needed for chart)
                    option_quote = OptionQuote(
                        option_symbol="DUMMY",
                        strike=0.0,
                        bid=0.0,
                        ask=0.0,
                        as_of=row.as_of,
                        expiry=row.as_of
                    )

                    normalized_tick = NormalizedTick(
                        as_of=row.as_of,
                        equity=equity_tick,
                        option=option_quote
                    )

                    self.data_buffer.append(normalized_tick)

                self._update_plot()

        except Exception as e:
            print(f"Error loading historical data: {e}")

    def _update_plot(self) -> None:
        """Update the plot with current data."""
        if not self.data_buffer:
            return

        # Extract data
        times = [t.as_of for t in self.data_buffer]
        price_values = [t.equity.price for t in self.data_buffer]
        vwap_values = [t.equity.session_vwap for t in self.data_buffer]
        ma9_values = [t.equity.ma9 for t in self.data_buffer]

        # Filter out zero prices that would skew the chart
        valid_data = [(t, p, v, m) for t, p, v, m in zip(times, price_values, vwap_values, ma9_values) if p > 0]

        if not valid_data:
            return

        times, price_values, vwap_values, ma9_values = zip(*valid_data)

        # Update min/max price tracking
        all_prices = list(price_values) + list(vwap_values) + list(ma9_values)
        if all_prices:
            current_min = min(all_prices)
            current_max = max(all_prices)
            self.min_price = min(self.min_price, current_min)
            self.max_price = max(self.max_price, current_max)

        # Update lines
        self.line_price.set_data(times, price_values)
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

    def show(self) -> None:
        """Show the chart in its parent frame."""
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def hide(self) -> None:
        """Hide the chart."""
        self.canvas.get_tk_widget().pack_forget()

    def clear(self) -> None:
        """Clear the chart."""
        self.data_buffer.clear()
        self.line_price.set_data([], [])
        self.line_vwap.set_data([], [])
        self.line_ma9.set_data([], [])

        # Reset price tracking
        self.min_price = float("inf")
        self.max_price = float("-inf")

        # Reset to auto-scaling
        self.ax.relim()
        self.ax.autoscale_view()

        self.canvas.draw()
