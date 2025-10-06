"""Position calculator that merges broker snapshots with intent state."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Callable, Coroutine, Iterable

from alphagen.core.events import PositionSnapshot, PositionState, TradeExecution
from alphagen.core.time_utils import now_est


class PositionCalculator:
    def __init__(
        self,
        emit: Callable[[PositionState], Coroutine[None, None, None]],
    ) -> None:
        self._emit = emit
        self._snapshots: dict[str, PositionSnapshot] = {}
        self._open_intents: dict[str, TradeExecution] = {}

    async def update_from_broker(self, snapshots: Iterable[PositionSnapshot]) -> None:
        for snapshot in snapshots:
            self._snapshots[snapshot.symbol] = snapshot
        await self._emit_state()

    async def register_execution(self, execution: TradeExecution) -> None:
        symbol = execution.intent.option_symbol
        if execution.intent.action.upper().startswith("BUY"):
            self._open_intents.pop(symbol, None)
        else:
            self._open_intents[symbol] = execution
        await self._emit_state()

    async def _emit_state(self) -> None:
        merged = defaultdict(lambda: PositionSnapshot("UNK", 0, 0.0, 0.0, now_est()))
        for symbol, snapshot in self._snapshots.items():
            merged[symbol] = snapshot
        for symbol, execution in self._open_intents.items():
            if symbol not in merged:
                merged[symbol] = PositionSnapshot(
                    symbol=symbol,
                    quantity=-execution.intent.quantity
                    if execution.intent.action.lower().startswith("sell")
                    else execution.intent.quantity,
                    average_price=execution.fill_price,
                    market_value=-execution.fill_price * execution.intent.quantity,
                    as_of=execution.as_of,
                )
        await self._emit(
            PositionState(
                as_of=now_est(),
                symbols=dict(merged),
            )
        )
