# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] zephyr.infrastructure.pipeline.backpressure_manager
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_backpressure_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Pipeline — Backpressure Manager

跨层背压信号管理器。管理 D_DATA→D_FACTOR→D_SIGNAL 数据管道中的背压控制信号。

三态背压模型（CTR-BP-001~003）：
  PAUSE   — 下游处理能力不足，暂停指定标的的数据下发 duration_ms 毫秒
  THROTTLE — 队列开始堆积，将下发速率降至 max_rate_per_sec 条/秒
  RESUME   — 处理能力恢复，恢复正常下发

典型流：
  1. D_FACTOR/D_SIGNAL 检测到队列堆积 → emit PAUSE / THROTTLE
  2. BackpressureManager 记录状态并通知 D_DATA 停止/降速
  3. 超时或下游处理完成 → emit RESUME
  4. BackpressureManager 清除状态并通知 D_DATA 恢复

CTR 契约：
  消费者 — CTR-BP-001 (BackpressurePause), CTR-BP-002 (Throttle), CTR-BP-003 (Resume)

SSoT: cross_layer_contracts.yaml → CTR-BP-001~003
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from zephyr.infrastructure.pipeline.backpressure_types import (
    BackpressurePause,
    BackpressureResume,
    BackpressureThrottle,
)

_logger = logging.getLogger(__name__)


class BpState(str, Enum):
    NORMAL = "normal"
    PAUSED = "paused"
    THROTTLED = "throttled"


@dataclass
class BpSymbolState:
    symbol: str
    state: BpState = BpState.NORMAL
    max_rate_per_sec: int = 0
    paused_until: float = 0.0
    paused_at: str = ""
    reason: str = ""
    signal_id: str = ""


class BackpressureManager:
    """跨层背压管理器

    线程安全。维护每个 symbol 的背压状态。
    支持 register_on_pause / register_on_resume 回调注册。
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._states: dict[str, BpSymbolState] = {}
        self._history: list[BpSymbolState] = []
        self._on_pause_handlers: list[Callable[[BpSymbolState], None]] = []
        self._on_resume_handlers: list[Callable[[BpSymbolState], None]] = []
        self._on_throttle_handlers: list[Callable[[BpSymbolState], None]] = []

    def handle_pause(self, signal: BackpressurePause) -> BpSymbolState:
        with self._lock:
            state = self._get_or_create(signal.symbol)
            state.state = BpState.PAUSED
            state.paused_at = datetime.now(UTC).isoformat()
            state.paused_until = time.time() + signal.duration_ms / 1000.0
            state.reason = signal.reason
            state.signal_id = signal.signal_id
            self._history.append(
                BpSymbolState(
                    symbol=state.symbol,
                    state=state.state,
                    reason=state.reason,
                    signal_id=state.signal_id,
                    paused_at=state.paused_at,
                )
            )

            _logger.warning(
                "[BP] PAUSE symbol=%s duration_ms=%d reason=%s",
                signal.symbol,
                signal.duration_ms,
                signal.reason,
            )

            for handler in self._on_pause_handlers:
                try:
                    handler(state)
                except Exception as e:
                    _logger.error("pause handler error: %s", e)

        return state

    def handle_throttle(self, signal: BackpressureThrottle) -> BpSymbolState:
        with self._lock:
            state = self._get_or_create(signal.symbol)
            state.state = BpState.THROTTLED
            state.max_rate_per_sec = signal.max_rate_per_sec
            state.reason = signal.reason
            state.signal_id = signal.signal_id
            self._history.append(
                BpSymbolState(
                    symbol=state.symbol,
                    state=state.state,
                    max_rate_per_sec=state.max_rate_per_sec,
                    reason=state.reason,
                    signal_id=state.signal_id,
                )
            )

            _logger.info(
                "[BP] THROTTLE symbol=%s rate=%d/s reason=%s",
                signal.symbol,
                signal.max_rate_per_sec,
                signal.reason,
            )

            for handler in self._on_throttle_handlers:
                try:
                    handler(state)
                except Exception as e:
                    _logger.error("throttle handler error: %s", e)

        return state

    def handle_resume(self, signal: BackpressureResume) -> BpSymbolState:
        with self._lock:
            state = self._get_or_create(signal.symbol)
            old_state = state.state
            state.state = BpState.NORMAL
            state.max_rate_per_sec = 0
            state.paused_until = 0.0
            state.reason = signal.reason
            state.signal_id = signal.signal_id
            self._history.append(
                BpSymbolState(
                    symbol=state.symbol,
                    state=state.state,
                    reason=state.reason,
                    signal_id=state.signal_id,
                )
            )

            if old_state is not BpState.NORMAL:
                _logger.info(
                    "[BP] RESUME symbol=%s reason=%s (was %s)",
                    signal.symbol,
                    signal.reason,
                    old_state.value,
                )

            for handler in self._on_resume_handlers:
                try:
                    handler(state)
                except Exception as e:
                    _logger.error("resume handler error: %s", e)

        return state

    def get_state(self, symbol: str) -> BpSymbolState:
        with self._lock:
            return self._get_or_create(symbol)

    def get_all_paused(self) -> list[BpSymbolState]:
        with self._lock:
            return [s for s in self._states.values() if s.state is BpState.PAUSED]

    def get_all_throttled(self) -> list[BpSymbolState]:
        with self._lock:
            return [s for s in self._states.values() if s.state is BpState.THROTTLED]

    def is_blocked(self, symbol: str) -> bool:
        with self._lock:
            state = self._get_or_create(symbol)
            if state.state is BpState.PAUSED:
                if state.paused_until > 0 and time.time() >= state.paused_until:
                    state.state = BpState.NORMAL
                    _logger.info("[BP] auto-resume symbol=%s (timeout)", symbol)
                else:
                    return True
            return False

    def register_on_pause(self, handler: Callable[[BpSymbolState], None]) -> None:
        self._on_pause_handlers.append(handler)

    def register_on_resume(self, handler: Callable[[BpSymbolState], None]) -> None:
        self._on_resume_handlers.append(handler)

    def register_on_throttle(self, handler: Callable[[BpSymbolState], None]) -> None:
        self._on_throttle_handlers.append(handler)

    def clear(self) -> None:
        with self._lock:
            self._states.clear()
            self._history.clear()
            self._on_pause_handlers.clear()
            self._on_resume_handlers.clear()
            self._on_throttle_handlers.clear()

    def get_stats(self) -> dict[str, Any]:
        with self._lock:
            paused = sum(1 for s in self._states.values() if s.state is BpState.PAUSED)
            throttled = sum(1 for s in self._states.values() if s.state is BpState.THROTTLED)
            normal = sum(1 for s in self._states.values() if s.state is BpState.NORMAL)
            return {
                "total_tracked_symbols": len(self._states),
                "paused_count": paused,
                "throttled_count": throttled,
                "normal_count": normal,
                "total_events": len(self._history),
            }

    def _get_or_create(self, symbol: str) -> BpSymbolState:
        if symbol not in self._states:
            self._states[symbol] = BpSymbolState(symbol=symbol)
        return self._states[symbol]


def _make_bp_signal_id() -> str:
    return f"bps-{uuid.uuid4().hex[:8]}"


def emit_pause(
    mgr: BackpressureManager,
    symbol: str,
    duration_ms: int,
    reason: str,
) -> BpSymbolState:
    return mgr.handle_pause(
        BackpressurePause(
            signal_id=_make_bp_signal_id(),
            symbol=symbol,
            duration_ms=duration_ms,
            reason=reason,
            idempotency_key=str(uuid.uuid4()),
        )
    )


def emit_throttle(
    mgr: BackpressureManager,
    symbol: str,
    max_rate_per_sec: int,
    reason: str,
) -> BpSymbolState:
    return mgr.handle_throttle(
        BackpressureThrottle(
            signal_id=_make_bp_signal_id(),
            symbol=symbol,
            max_rate_per_sec=max_rate_per_sec,
            reason=reason,
            idempotency_key=str(uuid.uuid4()),
        )
    )


def emit_resume(
    mgr: BackpressureManager,
    symbol: str,
    reason: str,
) -> BpSymbolState:
    return mgr.handle_resume(
        BackpressureResume(
            signal_id=_make_bp_signal_id(),
            symbol=symbol,
            reason=reason,
            idempotency_key=str(uuid.uuid4()),
        )
    )


__all__ = [
    "BackpressureManager",
    "BpState",
    "BpSymbolState",
    "emit_pause",
    "emit_resume",
    "emit_throttle",
]
