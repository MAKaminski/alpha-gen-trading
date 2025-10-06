"""Configuration and application constants for Alpha-Gen."""
from __future__ import annotations

from datetime import time, timedelta
from enum import Enum
from functools import lru_cache
from os import getenv
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file
load_dotenv()


EST = ZoneInfo("America/New_York")
MARKET_OPEN = time(hour=9, minute=30)
MARKET_CLOSE = time(hour=16, minute=0)
SESSION_BUFFER = timedelta(minutes=30)
TRADE_COOLDOWN = timedelta(seconds=30)
DEFAULT_EQUITY_TICKER = "QQQ"
OPTION_CONTRACT_MULTIPLIER = 100


class MarketDataSource(str, Enum):
    SCHWAB = "schwab"
    POLYGON = "polygon"


DEFAULT_MARKET_DATA_SOURCE = MarketDataSource.SCHWAB


class PolygonSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POLYGON_")

    api_key: str | None = Field(None, alias="API_KEY")
    equity_ticker: str = Field(DEFAULT_EQUITY_TICKER, alias="EQUITY_TICKER")
    options_underlying: str = Field(DEFAULT_EQUITY_TICKER, alias="OPTIONS_UNDERLYING")
    stock_ws_url: str = Field("wss://socket.polygon.io/stocks", alias="STOCK_WS_URL")
    options_ws_url: str = Field("wss://socket.polygon.io/options", alias="OPTIONS_WS_URL")
    s3_access_key: str | None = Field(None, alias="S3_ACCESS_KEY")
    s3_secret_key: str | None = Field(None, alias="S3_SECRET_KEY")
    s3_endpoint: str | None = Field(None, alias="S3_ENDPOINT")


class SchwabSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SCHWAB_")

    api_key: str | None = Field(None)
    api_secret: str | None = Field(None)
    account_id: str | None = Field(None)
    base_url: str = Field("https://api.schwab.com")
    paper_trading: bool = Field(True)
    callback_url: str | None = Field("http://localhost:8080/callback")
    token_path: str = Field("./config/schwab_token.json")


class StorageSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="")

    database_url: str = Field("sqlite+aiosqlite:///./alpha_gen.db", alias="DATABASE_URL")


class RiskSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RISK_")

    stop_loss_multiple: float = Field(2.0, alias="STOP_LOSS_MULTIPLE")
    take_profit_multiple: float = Field(0.5, alias="TAKE_PROFIT_MULTIPLE")
    max_position_size: int = Field(25, alias="MAX_POSITION_SIZE")
    trading_capital: float = Field(5_000_000.0, alias="TRADING_CAPITAL")


class FeatureSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FEATURE_")

    enable_chart: bool = Field(False, alias="ENABLE_CHART")


class AppConfig(BaseModel):
    polygon: PolygonSettings
    schwab: SchwabSettings
    storage: StorageSettings = StorageSettings()
    risk: RiskSettings = RiskSettings()
    features: FeatureSettings = FeatureSettings()
    timezone: ZoneInfo = EST
    market_data_source: MarketDataSource = DEFAULT_MARKET_DATA_SOURCE


@lru_cache(maxsize=1)
def load_app_config() -> AppConfig:
    """Load settings from environment (cached)."""
    source = getenv("MARKET_DATA_SOURCE")
    if source and source.lower() != DEFAULT_MARKET_DATA_SOURCE.value:
        raise ValueError("Polygon market data is disabled; only 'schwab' is currently supported")
    market_source = DEFAULT_MARKET_DATA_SOURCE
    return AppConfig(
        polygon=PolygonSettings(),
        schwab=SchwabSettings(),
        storage=StorageSettings(),
        risk=RiskSettings(),
        features=FeatureSettings(),
        market_data_source=market_source,
    )
