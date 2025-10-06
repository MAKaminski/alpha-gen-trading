"""Factory for selecting the configured market data provider."""

from __future__ import annotations

from alphagen.config import MarketDataSource, load_app_config
from alphagen.market_data.base import MarketDataProvider
from alphagen.market_data.schwab_stream import SchwabMarketDataProvider


def create_market_data_provider() -> MarketDataProvider:
    cfg = load_app_config()
    if cfg.market_data_source != MarketDataSource.SCHWAB:
        raise RuntimeError("Polygon market data is currently disabled")
    return SchwabMarketDataProvider()
