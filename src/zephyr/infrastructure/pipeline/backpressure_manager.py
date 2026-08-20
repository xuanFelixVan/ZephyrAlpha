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
# [A_module] module_id=MOD-INF-009 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Pipeline — Backpressure Manager

跨层背压信号管理器。管理 D_DATA->D_FACTOR->D_SIGNAL 数据管道中的背压控制信号。

三态背压模型（CTR-BP-001~003）：
  PAUSE   — 下游处理能力不足，暂停指定标的的数据下发 duration_ms 毫秒
  THROTTLE — 队列开始堆积，将下发速率降至 max_rate_per_sec 条/秒
  RESUME   — 处理能力恢复，恢复正常下发

典型流：
  1. D_FACTOR/D_SIGNAL 检测到队列堆积 -> emit PAUSE / THROTTLE
  2. BackpressureManager 记录状态并通知 D_DATA 停止/降速
  3. 超时或下游处理完成 -> emit RESUME
  4. BackpressureManager 清除状态并通知 D_DATA 恢复

CTR 契约：
  消费者 — CTR-BP-001 (BackpressurePause), CTR-BP-002 (Throttle), CTR-BP-003 (Resume)

SSoT: cross_layer_contracts.yaml -> CTR-BP-001~003

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 背压控制信号
#   fields: BackpressurePause（duration_ms）/ BackpressureThrottle（max_rate_per_sec）/ BackpressureResume，均含 symbol/reason/signal_id
#   code: backpressure_types（CTR-BP-001~003，L51-55 import）
# - id: I2
#   name: symbol 查询参数
#   fields: 标的代码字符串
#   code: get_state(symbol) / is_blocked(symbol) L203/L215
# 层: 算法
# - id: A1
#   name_zh: ① 暂停信号处理
#   name_en: BackpressureManager.handle_pause
#   intro: 下游处理不过来时把该标的置为暂停，记下恢复截止时刻并通知回调
#   desc: RLock 内 _get_or_create 建态；state=PAUSED；paused_until=time.time()+duration_ms/1000；追加 history；逐个调 on_pause handler（异常吞掉记 error）
#   inputs: I1
#   outputs: BpSymbolState(PAUSED)
# - id: A2
#   name_zh: ② 降速信号处理
#   name_en: handle_throttle
#   intro: 队列开始堆积时把该标的发送速率压到指定条数每秒
#   desc: state=THROTTLED；记 max_rate_per_sec；追加 history；触发 on_throttle 回调
#   inputs: I1
#   outputs: BpSymbolState(THROTTLED)
# - id: A3
#   name_zh: ③ 恢复信号处理
#   name_en: handle_resume
#   intro: 下游缓过来了就清掉暂停/降速状态，恢复正常下发
#   desc: state=NORMAL；max_rate_per_sec=0、paused_until=0 清零；追加 history；触发 on_resume 回调
#   inputs: I1
#   outputs: BpSymbolState(NORMAL)
# - id: A4
#   name_zh: ④ 阻塞查询与超时自愈
#   name_en: is_blocked
#   intro: 查某标的是否还被压着，暂停超时就自动放行为正常
#   desc: PAUSED 且 time.time()≥paused_until → 自动转 NORMAL 记 auto-resume 日志返回 False；未过期返回 True
#   inputs: I2
#   outputs: True=仍阻塞 / False=可下发
# - id: A5
#   name_zh: ⑤ 背压统计
#   name_en: get_stats
#   intro: 汇总当前各状态标的数量和累计事件数，给监控用
#   desc: 遍历 _states 按 PAUSED/THROTTLED/NORMAL 计数；total_events=len(_history)
#   inputs: I2
#   outputs: 统计字典
# 层: 输出
# - id: O1
#   name_zh: 标背压状态
#   name_en: BpSymbolState
#   intro: 每个标的的三态背压状态（normal/paused/throttled）及速率与截止时间
#   invariant: 三态互斥
#   downstream: D_DATA 数据下发层（CTR-BP-001~003 契约消费者，[CONSUMERS] 头未登记）
# - id: O2
#   name_zh: 背压统计报告
#   name_en: get_stats dict
#   intro: paused/throttled/normal 计数与事件总量，供管道健康监控
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I1 --> A3
# I2 --> A4
# I2 --> A5
# A1 --> A4
# A1 --> O1
# A2 --> O1
# A3 --> O1
# A4 --> O1
# A5 --> O2
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

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def history(self) -> list[BpSymbolState]:
        """只读：history（Stage 4 公共化）。"""
        return self._history

    @history.setter
    def history(self, value):
        """写入：history（Stage 4 公共化）。"""
        self._history = value

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
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    _logger.error("pause handler error: %s", e, exc_info=True)

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
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    _logger.error("throttle handler error: %s", e, exc_info=True)

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
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    _logger.error("resume handler error: %s", e, exc_info=True)

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
