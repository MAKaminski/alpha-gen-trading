"""Application orchestrator for Alpha-Gen."""

from __future__ import annotations

import asyncio
import json
import signal
import sys
import os
from typing import Dict

import structlog

from alphagen import __version__
from alphagen.config import load_app_config
from alphagen.core.events import (
    EquityTick,
    NormalizedTick,
    OptionQuote,
    PositionState,
    Signal,
    TradeExecution,
    TradeIntent,
)
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

# Add backend to path to access the data bridge
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.append(backend_path)

try:
    from services.schwab_client import data_bridge
    print("✅ DataBridge imported successfully")
except ImportError as e:
    print(f"❌ DataBridge import failed: {e}")
    # Fallback if backend services aren't available
    class MockDataBridge:
        def send_data_to_websocket(self, data):
            print(f"Mock bridge: {data[:100]}...")

    data_bridge = MockDataBridge()
    print("✅ Using MockDataBridge")


class AlphaGenApp:
    def __init__(self) -> None:
        self._logger = structlog.get_logger("alphagen.app")
        self._config = load_app_config()
        self._schwab = SchwabOAuthClient.create()

        if self._schwab is None:
            self._logger.warning(
                "schwab_client_not_available",
                msg="Schwab client not initialized - check configuration",
            )

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
        print(f"📈 AlphaGen: Handling equity tick for {tick.symbol} at ${tick.price}")
        await insert_equity_tick(tick)
        await self._normalizer.ingest_equity(tick)

        # Send to WebSocket clients
        equity_data = {
            "type": "equity_tick",
            "data": {
                "symbol": tick.symbol,
                "price": tick.price,
                "session_vwap": tick.session_vwap,
                "ma9": tick.ma9,
                "timestamp": tick.as_of.isoformat(),
            }
        }
        print(f"📨 AlphaGen: Sending equity data to bridge: {equity_data}")
        data_bridge.send_data_to_websocket(json.dumps(equity_data))

    async def _handle_option_quote(self, quote: OptionQuote) -> None:
        await insert_option_quote(quote)
        await self._normalizer.ingest_option(quote)

        # Send to WebSocket clients
        option_data = {
            "type": "option_quote",
            "data": {
                "option_symbol": quote.option_symbol,
                "strike": quote.strike,
                "bid": quote.bid,
                "ask": quote.ask,
                "expiry": quote.expiry.isoformat(),
                "timestamp": quote.as_of.isoformat(),
            }
        }
        data_bridge.send_data_to_websocket(json.dumps(option_data))

    async def _handle_normalized_tick(self, tick: NormalizedTick) -> None:
        import sys
        print("🚨🚨🚨 AlphaGen: _handle_normalized_tick METHOD ENTERED!", file=sys.stderr)
        print("🚨🚨🚨 AlphaGen: _handle_normalized_tick METHOD ENTERED!")
        try:
            print("🚨 AlphaGen: _handle_normalized_tick CALLED!")
            print(f"📊 AlphaGen: Handling normalized tick at {tick.as_of}")
            print(f"📊 AlphaGen: Normalized tick data - VWAP={tick.equity.session_vwap if tick.equity else 'None'}, MA9={tick.equity.ma9 if tick.equity else 'None'}")
            await insert_normalized_tick(tick)

            # Send to WebSocket clients for chart updates
            normalized_data = {
                "type": "normalized_tick",
                "data": {
                    "timestamp": tick.as_of.isoformat(),
                    "equity": {
                        "session_vwap": tick.equity.session_vwap if tick.equity else None,
                        "ma9": tick.equity.ma9 if tick.equity else None,
                    },
                    "option": {
                        "delta": tick.option.delta if tick.option else None,
                        "gamma": tick.option.gamma if tick.option else None,
                        "theta": tick.option.theta if tick.option else None,
                        "vega": tick.option.vega if tick.option else None,
                    } if tick.option else None,
                }
            }
            print(f"📨 AlphaGen: Sending normalized data to bridge: VWAP={tick.equity.session_vwap if tick.equity else 'None'}, MA9={tick.equity.ma9 if tick.equity else 'None'}")
            data_bridge.send_data_to_websocket(json.dumps(normalized_data))
        except Exception as e:
            print(f"❌ AlphaGen: Error in _handle_normalized_tick: {e}")
            import traceback
            traceback.print_exc()

    async def _handle_signal(self, signal: Signal) -> None:
        await insert_signal(signal)

        # Send to WebSocket clients
        signal_data = {
            "type": "signal",
            "data": {
                "signal_type": signal.signal_type,
                "strength": signal.strength,
                "timestamp": signal.as_of.isoformat(),
                "metadata": signal.metadata,
            }
        }
        data_bridge.send_data_to_websocket(json.dumps(signal_data))

    async def _record_execution(self, execution: TradeExecution) -> None:
        await insert_execution(execution)

        # Send to WebSocket clients
        execution_data = {
            "type": "trade_execution",
            "data": {
                "order_id": execution.order_id,
                "status": execution.status,
                "fill_price": execution.fill_price,
                "pnl_contrib": execution.pnl_contrib,
                "timestamp": execution.as_of.isoformat(),
            }
        }
        data_bridge.send_data_to_websocket(json.dumps(execution_data))

    async def _handle_trade_intent(self, intent: TradeIntent) -> None:
        await insert_trade_intent(intent)

        # Send to WebSocket clients
        intent_data = {
            "type": "trade_intent",
            "data": {
                "action": intent.action,
                "option_symbol": intent.option_symbol,
                "quantity": intent.quantity,
                "limit_price": intent.limit_price,
                "timestamp": intent.as_of.isoformat(),
            }
        }
        data_bridge.send_data_to_websocket(json.dumps(intent_data))

    async def _on_position_state(self, state: PositionState) -> None:
        # Update latest position state
        self._latest_position_state = state

        # Send to WebSocket clients
        position_data = {
            "type": "position_state",
            "data": {
                "total_pnl": state.total_pnl,
                "total_value": state.total_value,
                "positions": [
                    {
                        "symbol": pos.symbol,
                        "quantity": pos.quantity,
                        "market_value": pos.market_value,
                        "pnl": pos.pnl,
                    }
                    for pos in state.positions
                ],
                "timestamp": state.as_of.isoformat(),
            }
        }
        data_bridge.send_data_to_websocket(json.dumps(position_data))

    async def _handle_stream_error(self, exc: Exception) -> None:
        self._logger.error("market_data_stream_error", error=str(exc))

        # Send error to WebSocket clients
        error_data = {
            "type": "error",
            "data": {
                "message": str(exc),
                "timestamp": asyncio.get_event_loop().time(),
            }
        }
        data_bridge.send_data_to_websocket(json.dumps(error_data))

    async def _handle_normalized_tick(self, tick: NormalizedTick) -> None:
        await insert_normalized_tick(tick)
        if self._chart:
            self._chart.handle_tick(tick)
        await self._signal_engine.handle_tick(tick)
        await self._trade_manager.handle_tick(tick)

    async def _handle_signal(self, signal_event: Signal) -> None:
        self._logger.info(
            "signal", symbol=signal_event.option_symbol, action=signal_event.action
        )
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
