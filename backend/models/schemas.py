from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class WebSocketMessage(BaseModel):
    type: str
    data: Optional[Dict[str, Any]] = None

class MarketDataResponse(BaseModel):
    symbol: str
    price: float
    timestamp: datetime
    volume: Optional[int] = None

class EquityTick(BaseModel):
    symbol: str
    price: float
    timestamp: datetime
    volume: Optional[int] = None

class OptionQuote(BaseModel):
    option_symbol: str
    bid: float
    ask: float
    timestamp: datetime
    volume: Optional[int] = None

class NormalizedTick(BaseModel):
    timestamp: datetime
    equity: Dict[str, Any]
    option: Optional[Dict[str, Any]] = None

class LogMessage(BaseModel):
    level: str  # info, warning, error, debug
    message: str
    timestamp: Optional[datetime] = None

class StreamStatus(BaseModel):
    active: bool
    symbol: str
    last_update: Optional[datetime] = None
    connection_status: str
