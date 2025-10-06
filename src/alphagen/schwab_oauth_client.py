"""Schwab OAuth2 client wrapper using schwab-py library."""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import structlog
from schwab.auth import client_from_login_flow, client_from_token_file
from schwab.client import Client

from alphagen.config import load_app_config
from alphagen.core.events import OptionQuote, PositionSnapshot, TradeExecution, TradeIntent
from alphagen.core.time_utils import to_est


@dataclass
class SchwabOAuthClient:
    """Schwab client using OAuth2 authentication."""
    
    _client: Client
    _account_id: str
    _logger: structlog.BoundLogger = structlog.get_logger("alphagen.schwab_oauth")

    @classmethod
    def create(cls) -> "SchwabOAuthClient":
        """Create Schwab client with OAuth2 authentication."""
        cfg = load_app_config().schwab
        logger = structlog.get_logger("alphagen.schwab_oauth")
        
        # Check if we have a token file
        token_path = Path(cfg.token_path)
        
        try:
            if token_path.exists():
                logger.info("loading_existing_token", path=str(token_path))
                client = client_from_token_file(
                    token_path=str(token_path),
                    api_key=cfg.api_key,
                    app_secret=cfg.api_secret
                )
            else:
                logger.info("no_token_file_found", path=str(token_path))
                # For now, create a mock client since we need user interaction for OAuth2
                # In production, this would redirect to Schwab's OAuth2 flow
                raise FileNotFoundError("Token file not found - OAuth2 flow required")
                
        except Exception as e:
            logger.warning("oauth_authentication_failed", error=str(e))
            # Create a mock client for development
            client = None
            
        return cls(client, cfg.account_id)

    async def close(self) -> None:
        """Close the client connection."""
        if self._client:
            # schwab-py client doesn't have an explicit close method
            pass

    async def fetch_positions(self) -> list[PositionSnapshot]:
        """Fetch current positions from Schwab."""
        if not self._client:
            self._logger.error("no_client_available", msg="OAuth2 client not initialized - cannot fetch real data")
            # Return empty list instead of mock data
            return []
            
        try:
            # Use schwab-py client to get account information
            account_info = self._client.get_account(self._account_id)
            
            # Handle case where get_account returns a Response object
            if hasattr(account_info, 'json'):
                account_info = account_info.json()
            elif hasattr(account_info, 'text'):
                import json
                account_info = json.loads(account_info.text)
            
            snapshots: list[PositionSnapshot] = []
            if isinstance(account_info, dict) and 'securitiesAccount' in account_info:
                positions = account_info['securitiesAccount'].get('positions', [])
                for position in positions:
                    instrument = position.get('instrument', {})
                    symbol = instrument.get('symbol', 'UNKNOWN')
                    
                    # Calculate net quantity (long - short)
                    long_qty = float(position.get('longQuantity', 0))
                    short_qty = float(position.get('shortQuantity', 0))
                    net_qty = int(long_qty - short_qty)
                    
                    # Get market value and average price
                    market_value = float(position.get('marketValue', 0.0))
                    average_price = float(position.get('averagePrice', 0.0))
                    
                    snapshots.append(
                        PositionSnapshot(
                            symbol=symbol,
                            quantity=net_qty,
                            average_price=average_price,
                            market_value=market_value,
                            as_of=to_est(datetime.now(timezone.utc)),
                        )
                    )
            else:
                self._logger.warning("unexpected_account_info_format", account_info_type=type(account_info).__name__)
                # Return empty list if we can't parse the account info
                return []
            
            self._logger.info("positions_fetched", count=len(snapshots))
            return snapshots
            
        except Exception as e:
            self._logger.error("fetch_positions_error", error=str(e))
            return []

    async def submit_order(self, intent: TradeIntent) -> TradeExecution:
        """Submit an order to Schwab."""
        if not self._client:
            self._logger.warning("no_client_available", msg="OAuth2 client not initialized")
            return TradeExecution(
                order_id="mock_order",
                status="failed",
                fill_price=0.0,
                pnl_contrib=0.0,
                as_of=to_est(datetime.now(timezone.utc)),
                intent=intent,
            )
            
        try:
            # Use schwab-py client to place order
            order_spec = {
                "orderType": "LIMIT",
                "session": "NORMAL",
                "duration": "DAY",
                "orderStrategyType": "SINGLE",
                "price": str(intent.limit_price),
                "orderLegCollection": [
                    {
                        "instruction": intent.action.upper(),
                        "quantity": intent.quantity,
                        "instrument": {
                            "symbol": intent.option_symbol,
                            "assetType": "OPTION"
                        }
                    }
                ]
            }
            
            order_response = self._client.place_order(self._account_id, order_spec)
            order_id = order_response.get('order_id', 'unknown')
            
            return TradeExecution(
                order_id=order_id,
                status="submitted",
                fill_price=intent.limit_price,
                pnl_contrib=0.0,
                as_of=to_est(datetime.now(timezone.utc)),
                intent=intent,
            )
            
        except Exception as e:
            self._logger.error("submit_order_error", error=str(e))
            return TradeExecution(
                order_id="error",
                status="failed",
                fill_price=0.0,
                pnl_contrib=0.0,
                as_of=to_est(datetime.now(timezone.utc)),
                intent=intent,
            )

    async def close_positions(self, intents: Iterable[TradeIntent]) -> list[TradeExecution]:
        """Close multiple positions."""
        executions: list[TradeExecution] = []
        for intent in intents:
            exec_result = await self.submit_order(intent)
            executions.append(exec_result)
        return executions

    async def fetch_option_quote(self, option_symbol: str) -> OptionQuote | None:
        """Fetch option quote for a given symbol."""
        if not self._client:
            self._logger.error("no_client_available", msg="OAuth2 client not initialized - cannot fetch real data")
            return None
            
        try:
            # Use schwab-py client to get option quote
            quote_response = self._client.get_option_chain(
                option_symbol,
                contract_type="CALL",  # or "PUT"
                include_quotes=True
            )
            
            # Parse the response to extract quote data
            # This is a simplified example - real implementation would parse the full response
            if quote_response and 'callExpDateMap' in quote_response:
                # Extract the first available quote
                for exp_date, strikes in quote_response['callExpDateMap'].items():
                    for strike, contracts in strikes.items():
                        for contract in contracts:
                            if contract['symbol'] == option_symbol:
                                return OptionQuote(
                                    option_symbol=option_symbol,
                                    strike=float(contract['strikePrice']),
                                    bid=float(contract['bid'] or 0.0),
                                    ask=float(contract['ask'] or 0.0),
                                    expiry=datetime.fromisoformat(contract['expirationDate'].replace('Z', '+00:00')),
                                    as_of=to_est(datetime.now(timezone.utc)),
                                )
            
            return None
            
        except Exception as e:
            self._logger.warning("fetch_option_quote_error", symbol=option_symbol, error=str(e))
            return None

    def save_token(self, token_path: str) -> None:
        """Save the OAuth2 token to a file."""
        if self._client and hasattr(self._client, 'save_token'):
            self._client.save_token(token_path)
            self._logger.info("token_saved", path=token_path)
