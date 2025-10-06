"""Application orchestrator for Alpha-Gen."""
from __future__ import annotations

import asyncio
import signal
from typing import Dict

import structlog

from alphagen import __version__
from alphagen.config import load_app_config
from alphagen.core.events import EquityTick, NormalizedTick, OptionQuote, PositionState, Signal, TradeExecution, TradeIntent
from alphagen.etl.normalizer import Normalizer
from alphagen.etl.position import PositionCalculator
from alphagen.market_data import StreamCallbacks, create_market_data_provider
from alphagen.schwab_oauth_client import SchwabOAuthClient
from alphagen.signals import SignalEngine
from alphagen.storage import (
    init_models,
    insert_equity_tick,
    insert_execution,
    insert_normalized_tick,
    insert_option_quote,
    insert_positions,
    insert_signal,
    insert_trade_intent,
)
from alphagen.trade_generator import TradeGenerator
from alphagen.trade_manager import TradeManager
from alphagen.visualization.file_chart import FileChart
from alphagen.option_monitor import OptionMonitor


class AlphaGenApp:
    def __init__(self) -> None:
        self._logger = structlog.get_logger("alphagen.app")
        self._config = load_app_config()
        self._schwab = SchwabOAuthClient.create()
        
        if self._schwab is None:
            self._logger.warning("schwab_client_not_available", 
                                msg="Schwab client not initialized - check configuration")
        
        self._option_monitor = OptionMonitor(
            client=self._schwab,
            on_quote=self._handle_option_quote_update,
        )
        self._trade_manager = TradeManager(
            emit_execution=self._record_execution,
            schwab_client=self._schwab,
            option_monitor=self._option_monitor,
        )
        self._position_calculator = PositionCalculator(emit=self._on_position_state)
        self._latest_position_state: PositionState | None = None
        # Use file chart for debugger compatibility
        self._chart = FileChart() if self._config.features.enable_chart else None
        self._trade_generator = TradeGenerator(emit=self._handle_trade_intent)
        self._signal_engine = SignalEngine(emit=self._handle_signal)
        self._normalizer = Normalizer(emit=self._handle_normalized_tick)
        self._market_data = create_market_data_provider()
        self._running = False
        self._background_tasks: list[asyncio.Task[None]] = []
        self._intent_index: Dict[int, int] = {}

    async def run(self) -> None:
        self._logger.info("starting", version=__version__)
        await init_models()
        if self._chart:
            self._chart.start()
        self._running = True
        self._background_tasks.append(asyncio.create_task(self._position_poll_loop()))
        callbacks = StreamCallbacks(
            on_equity_tick=self._handle_equity_tick,
            on_option_quote=self._handle_option_quote,
            on_error=self._handle_stream_error,
        )
        await self._market_data.start(callbacks)
        stop_event = asyncio.Event()

        def _cancel(*_: object) -> None:
            self._logger.info("shutdown_signal")
            stop_event.set()

        for sig in (signal.SIGINT, signal.SIGTERM):
            asyncio.get_running_loop().add_signal_handler(sig, _cancel)

        await stop_event.wait()
        await self.shutdown()

    async def shutdown(self) -> None:
        self._running = False
        for task in self._background_tasks:
            task.cancel()
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        if self._chart:
            self._chart.stop()
        await self._option_monitor.shutdown()
        await self._trade_manager.close_all(reason="shutdown")
        await self._market_data.stop()
        await self._schwab.close()
        self._logger.info("shutdown_complete")

    async def _handle_equity_tick(self, tick: EquityTick) -> None:
        await insert_equity_tick(tick)
        await self._normalizer.ingest_equity(tick)

    async def _handle_option_quote(self, quote: OptionQuote) -> None:
        await insert_option_quote(quote)
        await self._normalizer.ingest_option(quote)

    async def _handle_stream_error(self, exc: Exception) -> None:
        self._logger.error("market_data_stream_error", error=str(exc))

    async def _handle_normalized_tick(self, tick: NormalizedTick) -> None:
        await insert_normalized_tick(tick)
        if self._chart:
            self._chart.handle_tick(tick)
        await self._signal_engine.handle_tick(tick)
        await self._trade_manager.handle_tick(tick)

    async def _handle_signal(self, signal_event: Signal) -> None:
        self._logger.info("signal", symbol=signal_event.option_symbol, action=signal_event.action)
        await insert_signal(signal_event)
        if self._chart:
            self._chart.handle_signal(signal_event)
        await self._trade_generator.handle_signal(signal_event)

    async def _handle_trade_intent(self, intent: TradeIntent) -> None:
        intent_id = await insert_trade_intent(intent)
        self._intent_index[id(intent)] = intent_id
        await self._trade_manager.handle_intent(intent)

    async def _record_execution(self, execution: TradeExecution) -> None:
        intent = execution.intent
        intent_id = self._intent_index.get(id(intent))
        if intent_id is None:
            intent_id = await insert_trade_intent(intent)
            self._intent_index[id(intent)] = intent_id
        await insert_execution(execution, intent_id=intent_id)
        await self._position_calculator.register_execution(execution)

    async def _position_poll_loop(self) -> None:
        poll_interval = 15
        while self._running:
            try:
                positions = await self._schwab.fetch_positions()
                await insert_positions(positions)
                await self._position_calculator.update_from_broker(positions)
                self._logger.info("schwab_positions_updated", count=len(positions))
            except Exception as exc:  # pylint: disable=broad-except
                self._logger.warning("schwab_poll_error", error=str(exc))
            await asyncio.sleep(poll_interval)

    async def _on_position_state(self, state) -> None:
        self._latest_position_state = state
        self._logger.info(
            "position_state",
            timestamp=state.as_of.isoformat(),
            exposure=state.total_market_value(),
        )

    async def _handle_option_quote_update(self, quote: OptionQuote) -> None:
        await self._trade_manager.update_option_quote(quote)


async def main() -> None:
    app = AlphaGenApp()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
