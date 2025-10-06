"""Real-time matplotlib visualization for VWAP vs MA9."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime
from queue import Empty, Queue
from threading import Thread
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


class LiveChart:
    """Render VWAP and MA9 lines with crossover markers in real time."""

    def __init__(self, max_points: int = 600) -> None:
        self._logger = structlog.get_logger("alphagen.live_chart")
        self._max_points = max_points
        self._tick_buffer: Deque[_TickPoint] = deque(maxlen=max_points)
        self._signal_buffer: Deque[_SignalPoint] = deque(maxlen=64)
        self._queue: Queue[Optional[tuple[str, object]]] = Queue()
        self._thread: Thread | None = None
        self._running = False

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = Thread(target=self._run, name="alphagen-live-chart", daemon=True)
        self._thread.start()

    async def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        self._queue.put(None)
        if self._thread:
            await self._join_thread()
            self._thread = None

    async def _join_thread(self) -> None:
        from asyncio import to_thread

        thread = self._thread
        if thread is None:
            return
        await to_thread(thread.join, 2.0)

    def handle_tick(self, tick: NormalizedTick) -> None:
        if not self._running:
            self.start()
        point = _TickPoint(
            timestamp=tick.as_of,
            vwap=tick.equity.session_vwap,
            ma9=tick.equity.ma9,
        )
        self._queue.put(("tick", point))

    def handle_signal(self, signal: Signal) -> None:
        if not self._running:
            self.start()
        marker = _SignalPoint(
            timestamp=signal.as_of,
            price=signal.reference_price,
            action=signal.action,
        )
        self._queue.put(("signal", marker))

    # --- internal helpers -------------------------------------------------

    def _run(self) -> None:
        try:
            import matplotlib
            import matplotlib.dates as mdates
            import matplotlib.pyplot as plt
            from matplotlib.animation import FuncAnimation
            import numpy as np
            
            # Ensure we're using an interactive backend
            if not matplotlib.is_interactive():
                # Use TkAgg backend since we're in a tkinter environment
                matplotlib.use('TkAgg')
                plt.ion()  # Turn on interactive mode
                
        except Exception as exc:  # pragma: no cover - matplotlib import failure
            self._logger.error("live_chart_import_failed", error=str(exc))
            return

        plt.style.use("dark_background")
        fig, ax = plt.subplots(
            num="Alpha-Gen QQQ VWAP vs MA9",
            figsize=(10, 6),
        )
        line_vwap, = ax.plot([], [], label="VWAP", color="#4caf50", linewidth=1.8)
        line_ma9, = ax.plot([], [], label="MA9", color="#2196f3", linewidth=1.4)
        scatter = ax.scatter([], [], marker="x", color="#ffeb3b", s=60, label="Cross")
        ax.set_xlabel("Time (ET)")
        ax.set_ylabel("Price ($)")
        ax.legend(loc="upper left")
        ax.grid(True, linestyle="--", alpha=0.3)

        date_formatter = mdates.DateFormatter("%H:%M:%S")
        ax.xaxis.set_major_formatter(date_formatter)

        def update(_frame: int):
            closing = False
            while True:
                try:
                    item = self._queue.get_nowait()
                except Empty:
                    break
                if item is None:
                    closing = True
                    break
                kind, payload = item
                if kind == "tick":
                    self._tick_buffer.append(payload)  # type: ignore[arg-type]
                elif kind == "signal":
                    self._signal_buffer.append(payload)  # type: ignore[arg-type]

            if closing:
                plt.close(fig)
                return line_vwap,

            if not self._tick_buffer:
                return line_vwap,

            times = np.array([mdates.date2num(pt.timestamp) for pt in self._tick_buffer])
            vwap = np.array([pt.vwap for pt in self._tick_buffer])
            ma9 = np.array([pt.ma9 for pt in self._tick_buffer])

            line_vwap.set_data(times, vwap)
            line_ma9.set_data(times, ma9)

            if self._signal_buffer:
                signals_list = list(self._signal_buffer)
                xs = np.array([mdates.date2num(sig.timestamp) for sig in signals_list])
                ys = np.array([sig.price for sig in signals_list])
                scatter.set_offsets(np.column_stack((xs, ys)))
                sizes = np.array([80.0 if sig.action.endswith("OPEN") else 50.0 for sig in signals_list])
                scatter.set_sizes(sizes)
            else:
                scatter.set_offsets(np.empty((0, 2)))
                scatter.set_sizes(np.empty((0,), dtype=float))

            ax.relim()
            ax.autoscale_view()
            fig.autofmt_xdate()
            return line_vwap, line_ma9, scatter

        FuncAnimation(fig, update, interval=250, cache_frame_data=False)
        try:
            self._logger.info("live_chart_displaying", backend=matplotlib.get_backend(), interactive=matplotlib.is_interactive())
            
            # Show the chart first
            plt.show(block=False)  # Non-blocking so GUI can continue
            self._logger.info("live_chart_window_created")
            
            # Make the window more prominent after it's created
            try:
                if hasattr(fig.canvas, 'manager') and hasattr(fig.canvas.manager, 'window'):
                    fig.canvas.manager.window.wm_attributes('-topmost', 1)  # Bring to front
                    fig.canvas.manager.window.wm_attributes('-topmost', 0)  # Allow normal stacking
                    self._logger.info("chart_window_brought_to_front")
                else:
                    self._logger.warning("chart_window_manager_not_available")
            except Exception as e:
                self._logger.warning("chart_window_attributes_failed", error=str(e))
            
            # Force a redraw
            fig.canvas.draw()
            fig.canvas.flush_events()
            
            # Keep the chart alive
            while self._running:
                plt.pause(0.1)
                
        except Exception as e:
            self._logger.warning("chart_display_error", error=str(e))
        finally:
            self._running = False
            self._logger.info("live_chart_closed")
