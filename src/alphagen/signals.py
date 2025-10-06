"""Signal generation logic based on normalized ticks."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Callable, Coroutine, Optional

from alphagen.config import TRADE_COOLDOWN
from alphagen.core.events import CooldownState, NormalizedTick, Signal
from alphagen.core.time_utils import now_est


class SignalEngine:
    def __init__(
        self,
        emit: Callable[[Signal], Coroutine[None, None, None]],
        cooldown: timedelta = TRADE_COOLDOWN,
    ) -> None:
        self._emit = emit
        self._last_diff: Optional[float] = None
        self._cooldown_state = CooldownState.expired()
        self._cooldown_duration = cooldown

    async def handle_tick(self, tick: NormalizedTick) -> None:
        if not tick.option:
            return
        diff = tick.equity.session_vwap - tick.equity.ma9
        now = tick.as_of
        if self._cooldown_state.active(now):
            self._last_diff = diff
            return
        if self._last_diff is None:
            self._last_diff = diff
            return
        crossed = (
            diff == 0 or (diff > 0 > self._last_diff) or (diff < 0 < self._last_diff)
        )
        if not crossed:
            self._last_diff = diff
            return
        action = "SELL_TO_OPEN" if diff > 0 else "SELL_PUT_TO_OPEN"
        rationale = (
            f"VWAP/MA9 crossover detected (diff={diff:.4f}, prev={self._last_diff:.4f})"
        )
        cooldown_until = now + self._cooldown_duration
        signal = Signal(
            as_of=now,
            action=action,
            option_symbol=tick.option.option_symbol,
            reference_price=tick.option.mid(),
            rationale=rationale,
            cooldown_until=cooldown_until,
        )
        await self._emit(signal)
        self._cooldown_state = CooldownState(until=cooldown_until)
        self._last_diff = diff

    def clear_cooldown(self) -> None:
        self._cooldown_state = CooldownState.expired()

    def remaining_cooldown(self, now: Optional[datetime] = None) -> timedelta:
        now = now or now_est()
        return max(self._cooldown_state.until - now, timedelta())
