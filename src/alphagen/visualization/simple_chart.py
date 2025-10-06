"""Simple matplotlib chart that works on the main thread."""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Deque, Optional

import structlog

from alphagen.core.events import NormalizedTick, Signal


@dataclass(slots=True)
class _TickPoint:
    timestamp: datetime
    vwap: float
    ma9: float


@dataclass(slots=True)
class _SignalPoint:
    timestamp: datetime
    price: float
    action: str


class SimpleChart:
    """Simple real-time chart that works on the main thread."""

    def __init__(self, max_points: int = 100) -> None:
        self._logger = structlog.get_logger("alphagen.simple_chart")
        self._max_points = max_points
        self._tick_buffer: Deque[_TickPoint] = deque(maxlen=max_points)
        self._signal_buffer: Deque[_SignalPoint] = deque(maxlen=64)
        self._running = False
        self._fig = None
        self._ax = None
        self._line_vwap = None
        self._line_ma9 = None
        self._scatter = None

    def start(self) -> None:
        """Start the chart (non-blocking)."""
        if self._running:
            return
        
        self._running = True
        self._setup_chart()
        self._logger.info("simple_chart_started")

    def stop(self) -> None:
        """Stop the chart."""
        if not self._running:
            return
        
        self._running = False
        if self._fig:
            plt.close(self._fig)
            self._fig = None
        self._logger.info("simple_chart_stopped")

    def _setup_chart(self) -> None:
        """Set up the matplotlib chart."""
        try:
            # Enable interactive mode for debugger compatibility
            plt.ion()
            plt.style.use("dark_background")
            self._fig, self._ax = plt.subplots(
                num="Alpha-Gen QQQ VWAP vs MA9",
                figsize=(12, 8),
            )
            
            self._line_vwap, = self._ax.plot([], [], label="VWAP", color="#4caf50", linewidth=2)
            self._line_ma9, = self._ax.plot([], [], label="MA9", color="#2196f3", linewidth=2)
            self._scatter = self._ax.scatter([], [], marker="x", color="#ffeb3b", s=60, label="Cross")
            
            self._ax.set_xlabel("Time (ET)")
            self._ax.set_ylabel("Price ($)")
            self._ax.set_title("Alpha-Gen Live Trading Chart")
            self._ax.legend(loc="upper left")
            self._ax.grid(True, linestyle="--", alpha=0.3)
            
            # Set up animation
            self._ani = animation.FuncAnimation(
                self._fig, 
                self._update_chart, 
                interval=1000,  # Update every second
                blit=False
            )
            
            plt.show(block=False)  # Non-blocking show
            plt.pause(0.1)  # Ensure the window appears
            self._logger.info("chart_window_created", title="Alpha-Gen QQQ VWAP vs MA9")
            
        except Exception as e:
            self._logger.error("chart_setup_failed", error=str(e))

    def _update_chart(self, frame: int) -> None:
        """Update the chart with new data."""
        if not self._running or not self._tick_buffer:
            return
        
        try:
            # Convert data to arrays
            times = [t.timestamp for t in self._tick_buffer]
            vwap_data = [t.vwap for t in self._tick_buffer]
            ma9_data = [t.ma9 for t in self._tick_buffer]
            
            # Update lines
            self._line_vwap.set_data(times, vwap_data)
            self._line_ma9.set_data(times, ma9_data)
            
            # Update signals
            if self._signal_buffer:
                signal_times = [s.timestamp for s in self._signal_buffer]
                signal_prices = [s.price for s in self._signal_buffer]
                self._scatter.set_offsets(list(zip(signal_times, signal_prices)))
            else:
                self._scatter.set_offsets([])
            
            # Auto-scale
            self._ax.relim()
            self._ax.autoscale_view()
            
        except Exception as e:
            self._logger.error("chart_update_failed", error=str(e))

    def handle_tick(self, tick: NormalizedTick) -> None:
        """Handle incoming market data tick."""
        if not self._running:
            return
        
        point = _TickPoint(
            timestamp=tick.as_of,
            vwap=tick.equity.session_vwap,
            ma9=tick.equity.ma9,
        )
        self._tick_buffer.append(point)
        self._logger.debug("chart_tick_added", vwap=point.vwap, ma9=point.ma9)

    def handle_signal(self, signal: Signal) -> None:
        """Handle incoming trading signal."""
        if not self._running:
            return
        
        marker = _SignalPoint(
            timestamp=signal.as_of,
            price=signal.reference_price,
            action=signal.action,
        )
        self._signal_buffer.append(marker)
        self._logger.info("chart_signal_added", action=signal.action, price=signal.reference_price)
