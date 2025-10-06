"""Schwab REST client wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

import httpx
import structlog

from alphagen.config import load_app_config
from alphagen.core.events import (
    OptionQuote,
    PositionSnapshot,
    TradeExecution,
    TradeIntent,
)
from alphagen.core.time_utils import to_est


@dataclass
class SchwabClient:
    _client: httpx.AsyncClient
    _account_id: str
    _logger: structlog.BoundLogger = structlog.get_logger("alphagen.schwab")

    @classmethod
    def create(cls) -> "SchwabClient":
        cfg = load_app_config().schwab
        headers = {
            "Authorization": f"Bearer {cfg.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        base_url = cfg.base_url or "https://api.schwabapi.com"
        client = httpx.AsyncClient(base_url=base_url, headers=headers, timeout=30)
        return cls(client, cfg.account_id)

    async def close(self) -> None:
        await self._client.aclose()

    async def fetch_positions(self) -> list[PositionSnapshot]:
        # Use the correct Schwab API v1 endpoint
        endpoint = f"/trader/v1/accounts/{self._account_id}/positions"
        response = await self._client.get(endpoint)
        response.raise_for_status()
        payload = response.json()
        snapshots: list[PositionSnapshot] = []
        for entry in payload.get("positions", []):
            snapshots.append(
                PositionSnapshot(
                    symbol=entry["symbol"],
                    quantity=int(entry["quantity"]),
                    average_price=float(entry["averagePrice"]),
                    market_value=float(entry["marketValue"]),
                    as_of=to_est(datetime.fromisoformat(entry["asOf"])),
                )
            )
        return snapshots

    async def submit_order(self, intent: TradeIntent) -> TradeExecution:
        endpoint = f"/trader/v1/accounts/{self._account_id}/orders"
        order_payload = {
            "symbol": intent.option_symbol,
            "side": intent.action,
            "quantity": intent.quantity,
            "orderType": "LIMIT",
            "price": intent.limit_price,
            "stopPrice": intent.stop_loss,
        }
        response = await self._client.post(endpoint, json=order_payload)
        response.raise_for_status()
        order_id = response.json().get("orderId", "unknown")
        return TradeExecution(
            order_id=order_id,
            status="submitted",
            fill_price=intent.limit_price,
            pnl_contrib=0.0,
            as_of=to_est(datetime.now(timezone.utc)),
            intent=intent,
        )

    async def close_positions(
        self, intents: Iterable[TradeIntent]
    ) -> list[TradeExecution]:
        executions: list[TradeExecution] = []
        for intent in intents:
            exec_result = await self.submit_order(intent)
            executions.append(exec_result)
        return executions

    async def fetch_option_quote(self, option_symbol: str) -> OptionQuote | None:
        endpoint = f"/marketdata/v1/quotes/{option_symbol}"
        response = await self._client.get(endpoint)
        response.raise_for_status()
        payload = response.json()
        quote_payload = (
            payload.get(option_symbol) or payload.get("quotes", {}).get(option_symbol)
            if isinstance(payload.get("quotes"), dict)
            else None
        )
        if not quote_payload:
            return None
        bid = float(quote_payload.get("bidPrice") or 0.0)
        ask = float(quote_payload.get("askPrice") or 0.0)
        strike = float(quote_payload.get("strikePrice") or 0.0)
        quote_time = quote_payload.get("quoteTimeInLong") or quote_payload.get(
            "quoteTime"
        )
        as_of = (
            to_est(datetime.fromtimestamp(quote_time / 1000, tz=timezone.utc))
            if quote_time
            else to_est(datetime.now(timezone.utc))
        )
        expiry_raw = quote_payload.get("expirationDate") or quote_payload.get(
            "optionExpirationDate"
        )
        if expiry_raw:
            try:
                expiry = datetime.fromisoformat(expiry_raw.replace("Z", "+00:00"))
            except ValueError:
                expiry = datetime.now(timezone.utc)
        else:
            expiry = datetime.now(timezone.utc)
        return OptionQuote(
            option_symbol=option_symbol,
            strike=strike,
            bid=bid,
            ask=ask,
            expiry=expiry,
            as_of=as_of,
        )
