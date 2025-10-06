"""Live chart visualization for market data and signals."""
from __future__ import annotations

import asyncio
from typing import Optional

import structlog

from alphagen.core.events import NormalizedTick, Signal


class LiveChart:
    """Live chart visualization for market data and trading signals."""

    def __init__(self) -> None:
        self._logger = structlog.get_logger("alphagen.visualization")
        self._running = False
        self._task: Optional[asyncio.Task[None]] = None

    async def start(self) -> None:
        """Start the live chart visualization."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_chart())
        self._logger.info("live_chart_started")

    async def stop(self) -> None:
        """Stop the live chart visualization."""
        if not self._running:
            return
        self._running = False
        if self._task:
            self._task.cancel()
            await asyncio.gather(self._task, return_exceptions=True)
            self._task = None
        self._logger.info("live_chart_stopped")

    def handle_tick(self, tick: NormalizedTick) -> None:
        """Handle incoming market data tick."""
        # For now, just log the tick data
        # In a real implementation, this would update a live chart
        self._logger.debug(
            "chart_tick",
            symbol=tick.symbol,
            price=tick.price,
            timestamp=tick.as_of.isoformat()
        )

    def handle_signal(self, signal: Signal) -> None:
        """Handle incoming trading signal."""
        # For now, just log the signal
        # In a real implementation, this would add signal markers to the chart
        self._logger.info(
            "chart_signal",
            symbol=signal.option_symbol,
            action=signal.action,
            timestamp=signal.as_of.isoformat()
        )

    async def _run_chart(self) -> None:
        """Main chart update loop."""
        try:
            while self._running:
                # In a real implementation, this would update the chart display
                await asyncio.sleep(0.1)  # 10 FPS update rate
        except asyncio.CancelledError:
            self._logger.debug("chart_task_cancelled")
            raise
