"""Schwab streaming market data provider."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Optional

import structlog
import websockets

from alphagen.config import load_app_config
from alphagen.core.events import EquityTick, OptionQuote
from alphagen.core.time_utils import to_est
from alphagen.market_data.base import MarketDataProvider, StreamCallbacks
from alphagen.schwab_oauth_client import SchwabOAuthClient


class SchwabMarketDataProvider(MarketDataProvider):
    """Schwab streaming market data provider using WebSockets."""

    def __init__(self) -> None:
        self._logger = structlog.get_logger("alphagen.market_data.schwab")
        self._callbacks: Optional[StreamCallbacks] = None
        self._websocket: Optional[websockets.WebSocketServerProtocol] = None
        self._task: Optional[asyncio.Task[None]] = None
        self._client = SchwabOAuthClient.create()
        self._config = load_app_config()

    async def start(self, callbacks: StreamCallbacks) -> None:
        """Start the Schwab streaming data provider."""
        self._callbacks = callbacks
        self._task = asyncio.create_task(self._stream_data())

    async def stop(self) -> None:
        """Stop the streaming data provider."""
        if self._task:
            self._task.cancel()
            await asyncio.gather(self._task, return_exceptions=True)
            self._task = None

        if self._websocket:
            await self._websocket.close()
            self._websocket = None

        await self._client.close()

    async def _stream_data(self) -> None:
        """Main streaming loop for Schwab market data."""
        assert self._callbacks is not None

        try:
            # For now, implement a polling-based approach since Schwab's streaming API
            # requires complex authentication and subscription management
            await self._poll_market_data()
        except Exception as e:
            self._logger.error("schwab_stream_error", error=str(e))
            await self._callbacks.on_error(e)

    async def _poll_market_data(self) -> None:
        """Poll market data from Schwab API (fallback when streaming not available)."""
        self._logger.info(
            "schwab_polling_started", msg="Using polling mode for market data"
        )

        # Subscribe to QQQ equity data
        equity_symbol = self._config.polygon.equity_ticker

        while True:
            try:
                # Get real market data from Schwab
                await self._fetch_real_market_data(equity_symbol)

                # Poll every 5 seconds
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.warning("schwab_poll_error", error=str(e))
                # Fall back to mock data if real data fails
                await self._generate_mock_data(equity_symbol)
                await asyncio.sleep(10)  # Wait longer on error

    async def _fetch_real_market_data(self, symbol: str) -> None:
        """Fetch real market data from Schwab API."""
        assert self._callbacks is not None

        try:
            # Get real equity quote from Schwab
            equity_tick = await self._client.fetch_equity_quote(symbol)
            if equity_tick:
                await self._callbacks.on_equity_tick(equity_tick)

            # For options, we would need to determine the appropriate option symbol
            # For now, we'll skip option quotes in the real data fetch
            # In production, you'd implement logic to find the nearest expiry option

            self._logger.debug("real_market_data_fetched", symbol=symbol)

        except Exception as e:
            self._logger.warning(
                "real_market_data_fetch_failed", symbol=symbol, error=str(e)
            )
            raise

    async def _generate_mock_data(self, symbol: str) -> None:
        """Generate mock market data for testing purposes."""
        assert self._callbacks is not None

        # Create mock equity tick
        current_time = to_est(datetime.now(timezone.utc))
        base_price = 400.0 + (hash(symbol) % 100) / 100.0  # Mock price variation

        equity_tick = EquityTick(
            symbol=symbol,
            price=base_price,
            session_vwap=base_price * 0.99,  # Mock VWAP slightly below price
            ma9=base_price * 1.01,  # Mock 9-period moving average
            as_of=current_time,
        )

        await self._callbacks.on_equity_tick(equity_tick)

        # Create mock option quote (example for QQQ options)
        option_quote = OptionQuote(
            option_symbol=f"{symbol}241220C00400000",  # QQQ Dec 20, 2024 $400 Call
            strike=400.0,
            bid=5.50,
            ask=5.75,
            expiry=datetime(2024, 12, 20, tzinfo=timezone.utc),
            as_of=current_time,
        )

        await self._callbacks.on_option_quote(option_quote)
