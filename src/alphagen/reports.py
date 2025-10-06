"""Reporting utilities for P/L summaries."""
from __future__ import annotations

from datetime import date

from sqlalchemy import text

from alphagen.storage import get_engine


async def fetch_daily_pnl(trade_date: date | None = None) -> list[dict[str, float]]:
    engine = get_engine()
    base_sql = (
        "SELECT DATE(as_of) as trade_date, "
        "SUM(pnl_contrib) as realized_pnl, "
        "COUNT(*) as trade_count "
        "FROM executionrow "
    )
    params: dict[str, str] = {}
    if trade_date:
        base_sql += "WHERE DATE(as_of) = :trade_date "
        params["trade_date"] = trade_date.isoformat()
    base_sql += "GROUP BY DATE(as_of) ORDER BY trade_date DESC"
    stmt = text(base_sql)
    async with engine.connect() as conn:
        result = await conn.execute(stmt, params)
        rows = [dict(row._mapping) for row in result]
    return rows
