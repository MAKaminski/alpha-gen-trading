"""File-based chart that saves images instead of showing windows."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Deque

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


class FileChart:
    """Chart that saves images to files instead of showing windows."""

    def __init__(self, output_dir: str = "charts", max_points: int = 100) -> None:
        self._logger = structlog.get_logger("alphagen.file_chart")
        self._max_points = max_points
        self._tick_buffer: Deque[_TickPoint] = deque(maxlen=max_points)
        self._signal_buffer: Deque[_SignalPoint] = deque(maxlen=64)
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(exist_ok=True)
        self._running = False

    def start(self) -> None:
        """Start the chart."""
        if self._running:
            return

        self._running = True
        self._logger.info("file_chart_started", output_dir=str(self._output_dir))

    def stop(self) -> None:
        """Stop the chart."""
        if not self._running:
            return

        self._running = False
        self._logger.info("file_chart_stopped")

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

        # Update chart every 5 ticks
        if len(self._tick_buffer) % 5 == 0:
            self._save_chart()

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
        self._logger.info(
            "chart_signal_added", action=signal.action, price=signal.reference_price
        )

        # Save chart when signal occurs
        self._save_chart()

    def _save_chart(self) -> None:
        """Save the current chart to a file."""
        if not self._tick_buffer:
            return

        try:
            plt.style.use("dark_background")
            fig, ax = plt.subplots(figsize=(12, 8))

            # Convert data to arrays
            times = [t.timestamp for t in self._tick_buffer]
            vwap_data = [t.vwap for t in self._tick_buffer]
            ma9_data = [t.ma9 for t in self._tick_buffer]

            # Plot lines
            ax.plot(times, vwap_data, label="VWAP", color="#4caf50", linewidth=2)
            ax.plot(times, ma9_data, label="MA9", color="#2196f3", linewidth=2)

            # Plot signals
            if self._signal_buffer:
                signal_times = [s.timestamp for s in self._signal_buffer]
                signal_prices = [s.price for s in self._signal_buffer]
                ax.scatter(
                    signal_times,
                    signal_prices,
                    marker="x",
                    color="#ffeb3b",
                    s=60,
                    label="Signals",
                )

            ax.set_xlabel("Time (ET)")
            ax.set_ylabel("Price ($)")
            ax.set_title("Alpha-Gen Live Trading Chart")
            ax.legend(loc="upper left")
            ax.grid(True, linestyle="--", alpha=0.3)

            # Format x-axis
            import matplotlib.dates as mdates

            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self._output_dir / f"trading_chart_{timestamp}.png"
            plt.savefig(filename, dpi=150, bbox_inches="tight")
            plt.close(fig)

            self._logger.info("chart_saved", filename=str(filename))

        except Exception as e:
            self._logger.error("chart_save_failed", error=str(e))
