"""Option quote polling to support stop-loss/take-profit logic."""

from __future__ import annotations

import asyncio
from typing import Awaitable, Callable

import structlog

from alphagen.core.events import OptionQuote
from alphagen.schwab_client import SchwabClient

QuoteCallback = Callable[[OptionQuote], Awaitable[None]]


class OptionMonitor:
    """Continuously refresh quotes for open option positions."""

    def __init__(
        self,
        client: SchwabClient,
        on_quote: QuoteCallback,
        interval_seconds: float = 1.0,
    ) -> None:
        self._client = client
        self._on_quote = on_quote
        self._interval = interval_seconds
        self._logger = structlog.get_logger("alphagen.option_monitor")
        self._tasks: dict[str, asyncio.Task[None]] = {}

    def track(self, symbol: str) -> None:
        if symbol in self._tasks:
            return
        self._logger.info("option_monitor_track", symbol=symbol)
        task = asyncio.create_task(self._poll(symbol), name=f"option-monitor-{symbol}")
        self._tasks[symbol] = task

    def untrack(self, symbol: str) -> None:
        task = self._tasks.pop(symbol, None)
        if not task:
            return
        self._logger.info("option_monitor_untrack", symbol=symbol)
        task.cancel()

    async def shutdown(self) -> None:
        tasks = list(self._tasks.values())
        if not tasks:
            return
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self._tasks.clear()

    async def _poll(self, symbol: str) -> None:
        try:
            while True:
                try:
                    quote = await self._client.fetch_option_quote(symbol)
                    if quote:
                        await self._on_quote(quote)
                except asyncio.CancelledError:  # pragma: no cover - cooperative cancel
                    raise
                except Exception as exc:  # pylint: disable=broad-except
                    self._logger.warning(
                        "option_monitor_error", symbol=symbol, error=str(exc)
                    )
                await asyncio.sleep(self._interval)
        except asyncio.CancelledError:
            self._logger.debug("option_monitor_task_cancelled", symbol=symbol)
            raise
