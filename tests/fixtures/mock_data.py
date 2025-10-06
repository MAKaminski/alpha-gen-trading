"""Mock data fixtures for testing."""
from datetime import datetime, timedelta
from typing import List

from alphagen.core.events import EquityTick, OptionQuote, NormalizedTick, TradeIntent, Signal
from alphagen.core.time_utils import now_est


def create_equity_tick(
    symbol: str = "QQQ",
    price: float = 400.0,
    session_vwap: float = 399.0,
    ma9: float = 401.0,
    timestamp: datetime = None
) -> EquityTick:
    """Create a mock equity tick."""
    if timestamp is None:
        timestamp = now_est()
    
    return EquityTick(
        symbol=symbol,
        price=price,
        session_vwap=session_vwap,
        ma9=ma9,
        as_of=timestamp,
    )


def create_option_quote(
    option_symbol: str = "QQQ241220C00400000",
    strike: float = 400.0,
    bid: float = 5.50,
    ask: float = 5.75,
    timestamp: datetime = None
) -> OptionQuote:
    """Create a mock option quote."""
    if timestamp is None:
        timestamp = now_est()
    
    return OptionQuote(
        option_symbol=option_symbol,
        strike=strike,
        bid=bid,
        ask=ask,
        expiry=timestamp + timedelta(hours=1),
        as_of=timestamp,
    )


def create_normalized_tick(
    equity_tick: EquityTick = None,
    option_quote: OptionQuote = None,
    timestamp: datetime = None
) -> NormalizedTick:
    """Create a mock normalized tick."""
    if timestamp is None:
        timestamp = now_est()
    
    if equity_tick is None:
        equity_tick = create_equity_tick(timestamp=timestamp)
    
    if option_quote is None:
        option_quote = create_option_quote(timestamp=timestamp)
    
    return NormalizedTick(
        as_of=timestamp,
        equity=equity_tick,
        option=option_quote,
    )


def create_trade_intent(
    action: str = "SELL_TO_OPEN",
    option_symbol: str = "QQQ241220C00400000",
    quantity: int = 25,
    limit_price: float = 5.50,
    stop_loss: float = 11.00,
    take_profit: float = 2.75,
    timestamp: datetime = None
) -> TradeIntent:
    """Create a mock trade intent."""
    if timestamp is None:
        timestamp = now_est()
    
    return TradeIntent(
        as_of=timestamp,
        action=action,
        option_symbol=option_symbol,
        quantity=quantity,
        limit_price=limit_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
    )


def create_signal(
    action: str = "SELL_TO_OPEN",
    option_symbol: str = "QQQ241220C00400000",
    reference_price: float = 5.50,
    rationale: str = "VWAP/MA9 crossover detected",
    timestamp: datetime = None
) -> Signal:
    """Create a mock signal."""
    if timestamp is None:
        timestamp = now_est()
    
    return Signal(
        as_of=timestamp,
        action=action,
        option_symbol=option_symbol,
        reference_price=reference_price,
        rationale=rationale,
        cooldown_until=timestamp + timedelta(seconds=30),
    )


def create_crossover_scenario() -> List[NormalizedTick]:
    """Create a series of ticks that demonstrate a VWAP/MA9 crossover."""
    base_time = now_est()
    
    # Initial state: VWAP below MA9
    tick1 = create_normalized_tick(
        equity_tick=create_equity_tick(
            price=400.0,
            session_vwap=399.0,
            ma9=401.0,
            timestamp=base_time
        ),
        option_quote=create_option_quote(timestamp=base_time),
        timestamp=base_time
    )
    
    # Crossover: VWAP crosses above MA9
    tick2 = create_normalized_tick(
        equity_tick=create_equity_tick(
            price=400.0,
            session_vwap=401.0,
            ma9=399.0,
            timestamp=base_time + timedelta(seconds=1)
        ),
        option_quote=create_option_quote(timestamp=base_time + timedelta(seconds=1)),
        timestamp=base_time + timedelta(seconds=1)
    )
    
    # Continue trend
    tick3 = create_normalized_tick(
        equity_tick=create_equity_tick(
            price=400.0,
            session_vwap=402.0,
            ma9=398.0,
            timestamp=base_time + timedelta(seconds=2)
        ),
        option_quote=create_option_quote(timestamp=base_time + timedelta(seconds=2)),
        timestamp=base_time + timedelta(seconds=2)
    )
    
    return [tick1, tick2, tick3]


def create_take_profit_scenario() -> List[OptionQuote]:
    """Create a series of option quotes that trigger take profit."""
    base_time = now_est()
    
    # Entry price
    entry_quote = create_option_quote(
        bid=5.50,
        ask=5.75,
        timestamp=base_time
    )
    
    # Price moves down (profitable for short position)
    profit_quote1 = create_option_quote(
        bid=4.00,
        ask=4.25,
        timestamp=base_time + timedelta(seconds=1)
    )
    
    # Price hits take profit level
    take_profit_quote = create_option_quote(
        bid=2.50,
        ask=2.75,
        timestamp=base_time + timedelta(seconds=2)
    )
    
    return [entry_quote, profit_quote1, take_profit_quote]


def create_stop_loss_scenario() -> List[OptionQuote]:
    """Create a series of option quotes that trigger stop loss."""
    base_time = now_est()
    
    # Entry price
    entry_quote = create_option_quote(
        bid=5.50,
        ask=5.75,
        timestamp=base_time
    )
    
    # Price moves up (unprofitable for short position)
    loss_quote1 = create_option_quote(
        bid=7.00,
        ask=7.25,
        timestamp=base_time + timedelta(seconds=1)
    )
    
    # Price hits stop loss level
    stop_loss_quote = create_option_quote(
        bid=11.50,
        ask=12.00,
        timestamp=base_time + timedelta(seconds=2)
    )
    
    return [entry_quote, loss_quote1, stop_loss_quote]
