# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-CORE-BP
# [MODULE] zephyr.factor.core.backpressure.limiter
# [DOMAIN] D_FACTOR
# [DEPENDENCIES]
# [CONSUMERS] zephyr.factor.core.dag_manager; zephyr.factor.core.dist_feature_eng
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三态状态机（NORMAL/THROTTLED/PAUSED）单调转换；release 不超过 acquire 次数（防御性）
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] acquire 在 PAUSED 或超时返回 False（不抛）；release 不抛；inflight 永不 <0
# [TESTS] tests/factor/test_backpressure.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_FACTOR core backpressure.limiter——进程内在途并发限流器。

基于 threading.Semaphore 控制在途因子计算数量，三态状态机：
- NORMAL：inflight/max_inflight < high_watermark
- THROTTLED：inflight/max_inflight ≥ high_watermark（仍受理但告警）
- PAUSED：外部强制暂停（pause() 调用，拒绝所有新 acquire）

与 shared/infra/limiter.py:SyncTokenBucketLimiter 的边界：
- SyncTokenBucketLimiter 是速率限流（permits/sec，token bucket）
- BackpressureLimiter 是在途并发限流（max_inflight，Semaphore）
- 两者正交，解决不同问题
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from enum import Enum

from zephyr.factor.core.config_manager.loader import get_section


class BackpressureState(str, Enum):
    """三态状态机。"""

    NORMAL = "normal"
    THROTTLED = "throttled"
    PAUSED = "paused"


@dataclass(frozen=True)
class BackpressureConfig:
    """背压限流器配置。

    Attributes:
        max_inflight: 最大在途并发数
        acquire_timeout_s: acquire 超时秒数（超时返回 False）
        high_watermark: 高水位比例（inflight/max_inflight ≥ 此值 → THROTTLED）
        low_watermark: 低水位比例（inflight/max_inflight ≤ 此值 → NORMAL）
    """

    max_inflight: int = 8
    acquire_timeout_s: float = 30.0
    high_watermark: float = 0.8
    low_watermark: float = 0.5


def _default_config() -> BackpressureConfig:
    """从 core/_config.yaml 的 backpressure 节构建默认配置（真源=YAML，缺省回退常量）。"""
    s = get_section("backpressure")
    return BackpressureConfig(
        max_inflight=int(s.get("max_inflight", 8)),
        acquire_timeout_s=float(s.get("acquire_timeout_s", 30.0)),
        high_watermark=float(s.get("high_watermark", 0.8)),
        low_watermark=float(s.get("low_watermark", 0.5)),
    )


@dataclass
class BackpressureStats:
    """背压限流器运行时统计（快照）。"""

    state: BackpressureState
    inflight: int
    max_inflight: int
    total_acquired: int
    total_rejected: int


class BackpressureLimiter:
    """进程内在途并发限流器。

    Usage::

        limiter = BackpressureLimiter(BackpressureConfig(max_inflight=4))
        if limiter.acquire():
            try:
                compute_factor(...)
            finally:
                limiter.release()
        else:
            # 被限流（PAUSED 或超时）
            skip_or_retry()
    """

    def __init__(self, config: BackpressureConfig | None = None) -> None:
        self._config = config or _default_config()
        self._semaphore = threading.Semaphore(self._config.max_inflight)
        self._lock = threading.Lock()
        self._inflight = 0
        self._state = BackpressureState.NORMAL
        self._paused = False
        self._total_acquired = 0
        self._total_rejected = 0

    def acquire(self) -> bool:
        """尝试获取执行许可。

        Returns:
            True=获取成功，调用方必须在完成后调用 release()
            False=被拒绝（PAUSED 状态或超时）

        Notes:
            - PAUSED 状态直接拒绝（不阻塞）
            - 非 PAUSED 状态阻塞等待 Semaphore，最长 acquire_timeout_s 秒
            - 成功后据当前水位更新 state（NORMAL ↔ THROTTLED）
        """
        with self._lock:
            if self._paused:
                self._total_rejected += 1
                return False

        # 在锁外尝试获取 semaphore（阻塞最长 timeout）
        acquired = self._semaphore.acquire(timeout=self._config.acquire_timeout_s)
        if not acquired:
            with self._lock:
                self._total_rejected += 1
            return False

        with self._lock:
            self._inflight += 1
            self._total_acquired += 1
            self._update_state_locked()
            return True

    def release(self) -> None:
        """释放执行许可。

        Notes:
            - 防御性：inflight 永不 <0
            - 释放后据水位回落更新 state（THROTTLED → NORMAL）
            - PAUSED 状态下 release 仍然生效（允许在途任务完成）
        """
        with self._lock:
            if self._inflight > 0:
                self._inflight -= 1
            self._update_state_locked()
        self._semaphore.release()

    def pause(self) -> None:
        """强制进入 PAUSED 状态，拒绝所有新 acquire。"""
        with self._lock:
            self._paused = True
            self._state = BackpressureState.PAUSED

    def resume(self) -> None:
        """解除 PAUSED 状态，恢复据水位判定。"""
        with self._lock:
            self._paused = False
            self._update_state_locked()

    def stats(self) -> BackpressureStats:
        """返回当前状态快照（线程安全）。"""
        with self._lock:
            return BackpressureStats(
                state=self._state,
                inflight=self._inflight,
                max_inflight=self._config.max_inflight,
                total_acquired=self._total_acquired,
                total_rejected=self._total_rejected,
            )

    def _update_state_locked(self) -> None:
        """据当前 inflight/max_inflight 比例刷新 state（调用方持 self._lock）。

        转换规则：
        - PAUSED 优先（_paused=True 时强制 PAUSED）
        - inflight/max ≥ high_watermark → THROTTLED
        - inflight/max ≤ low_watermark → NORMAL
        - 中间区间保持当前状态（滞后区间，避免抖动）
        """
        if self._paused:
            self._state = BackpressureState.PAUSED
            return

        if self._config.max_inflight <= 0:
            self._state = BackpressureState.NORMAL
            return

        ratio = self._inflight / self._config.max_inflight
        if ratio >= self._config.high_watermark:
            self._state = BackpressureState.THROTTLED
        elif ratio <= self._config.low_watermark:
            self._state = BackpressureState.NORMAL
        # 中间区间：保持当前 state（滞后区间）
