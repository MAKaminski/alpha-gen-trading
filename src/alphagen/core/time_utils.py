"""Time utilities for market session management."""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta
import holidays

from alphagen.config import EST, MARKET_CLOSE, MARKET_OPEN, SESSION_BUFFER

US_MARKET_HOLIDAYS = holidays.NYSE()


def now_est() -> datetime:
    return datetime.now(tz=EST)


def within_trading_window(moment: datetime | None = None) -> bool:
    moment = moment or now_est()
    if moment.date() in US_MARKET_HOLIDAYS:
        return False
    window_open = datetime.combine(moment.date(), MARKET_OPEN, tzinfo=EST) - SESSION_BUFFER
    window_close = datetime.combine(moment.date(), MARKET_CLOSE, tzinfo=EST) + SESSION_BUFFER
    return window_open <= moment <= window_close


def session_bounds(day: datetime | None = None) -> tuple[datetime, datetime]:
    day = day or now_est()
    session_start = datetime.combine(day.date(), MARKET_OPEN, tzinfo=EST)
    session_end = datetime.combine(day.date(), MARKET_CLOSE, tzinfo=EST)
    return session_start - SESSION_BUFFER, session_end + SESSION_BUFFER


def next_session_open(after: datetime | None = None) -> datetime:
    probe = (after or now_est()) + timedelta(days=0)
    while True:
        probe += relativedelta(days=1)
        if probe.date() in US_MARKET_HOLIDAYS:
            continue
        start, _ = session_bounds(probe)
        if start > (after or now_est()):
            return start


def to_est(timestamp: datetime, tz: ZoneInfo | None = None) -> datetime:
    tz = tz or EST
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=tz).astimezone(EST)
    return timestamp.astimezone(EST)
