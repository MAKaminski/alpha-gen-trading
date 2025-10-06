"""Polygon websocket consumers for equity and option data."""
from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Optional

import websockets
from websockets.client import WebSocketClientProtocol

from alphagen.config import DEFAULT_EQUITY_TICKER, load_app_config
from alphagen.core.events import EquityTick, OptionQuote
from alphagen.core.time_utils import to_est
from alphagen.market_data.base import MarketDataProvider, StreamCallbacks


class PolygonMarketDataProvider(MarketDataProvider):
    def __init__(self, ticker: str = DEFAULT_EQUITY_TICKER) -> None:
        self._cfg = load_app_config().polygon
        self._ticker = ticker
        self._equity_ws: Optional[WebSocketClientProtocol] = None
        self._options_ws: Optional[WebSocketClientProtocol] = None
        self._callbacks: Optional[StreamCallbacks] = None
        self._tasks: list[asyncio.Task[None]] = []

    async def start(self, callbacks: StreamCallbacks) -> None:
        self._callbacks = callbacks
        await self._connect_streams()
        self._tasks = [
            asyncio.create_task(self._consume_equity()),
            asyncio.create_task(self._consume_options()),
        ]

    async def stop(self) -> None:
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        if self._equity_ws:
            await self._equity_ws.close()
        if self._options_ws:
            await self._options_ws.close()

    async def _connect_streams(self) -> None:
        auth_payload = json.dumps({"action": "auth", "params": self._cfg.api_key})
        self._equity_ws = await websockets.connect(self._cfg.stock_ws_url, ping_interval=10)
        await self._equity_ws.send(auth_payload)
        await self._equity_ws.send(
            json.dumps({"action": "subscribe", "params": f"XA.{self._ticker}"})
        )

        self._options_ws = await websockets.connect(
            self._cfg.options_ws_url, ping_interval=10
        )
        await self._options_ws.send(auth_payload)
        await self._options_ws.send(
            json.dumps({"action": "subscribe", "params": f"Q.{self._ticker}"})
        )

    async def _consume_equity(self) -> None:
        assert self._callbacks and self._equity_ws
        try:
            async for raw in self._equity_ws:
                data = json.loads(raw)
                for entry in data:
                    if entry.get("ev") != "XA":
                        continue
                    tick = EquityTick(
                        symbol=entry["sym"],
                        price=float(entry.get("c", 0.0)),
                        session_vwap=float(entry.get("vw", 0.0)),
                        ma9=float(entry.get("ma", 0.0)),
                        as_of=to_est(datetime.fromtimestamp(entry["s"] / 1000)),
                    )
                    await self._callbacks.on_equity_tick(tick)
        except Exception as exc:  # pylint: disable=broad-except
            await self._callbacks.on_error(exc)

    async def _consume_options(self) -> None:
        assert self._callbacks and self._options_ws
        try:
            async for raw in self._options_ws:
                data = json.loads(raw)
                for entry in data:
                    if entry.get("ev") != "Q":
                        continue
                    quote = OptionQuote(
                        option_symbol=entry["sym"],
                        strike=float(entry.get("k", 0.0)),
                        bid=float(entry.get("bp", 0.0)),
                        ask=float(entry.get("ap", 0.0)),
                        expiry=datetime.fromtimestamp(entry.get("x", 0) / 1000),
                        as_of=to_est(datetime.fromtimestamp(entry["t"] / 1000)),
                    )
                    await self._callbacks.on_option_quote(quote)
        except Exception as exc:  # pylint: disable=broad-except
            await self._callbacks.on_error(exc)
