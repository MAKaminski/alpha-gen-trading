"""Command-line interface for Alpha-Gen."""
from __future__ import annotations

import asyncio
from datetime import datetime

import click

from alphagen.app import main as run_app
from alphagen.reports import fetch_daily_pnl


@click.group()
def cli() -> None:
    """Alpha-Gen management CLI."""


@cli.command()
def run() -> None:
    """Start the real-time Alpha-Gen service."""
    asyncio.run(run_app())


@cli.command()
@click.option("--for-date", "for_date", type=click.DateTime(formats=["%Y-%m-%d"]))
def report(for_date: datetime | None) -> None:
    """Display daily P/L summary."""
    async def _display() -> None:
        data = await fetch_daily_pnl(for_date.date() if for_date else None)
        for row in data:
            click.echo(
                f"{row['trade_date']}: PnL={row['realized_pnl']:.2f} on {row['trade_count']} trades"
            )

    asyncio.run(_display())


if __name__ == "__main__":
    cli()
