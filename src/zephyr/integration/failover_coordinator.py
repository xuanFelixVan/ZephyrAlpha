# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/blueprint.md
# [MODULE] zephyr.integration.failover_coordinator
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.data.source_circuit_breaker; zephyr.trading.trading_contracts.risk.trading_kill_switch; zephyr.shared.utils.time_utils
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三源优先级静态序+质量分动态降级双因子选源；切换原子（先定目标再换现役）；all_degraded 锁存（恢复前不重复联动）；全部公共方法不抛异常（协调器不得阻断数据主链路）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] evaluate/force_switch/update_quality/report_* 不抛异常；未知源操作静默忽略并 log
# [TESTS] tests/integration/test_failover_coordinator.py
# [A_module] module_id=MOD-INF-042 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FailoverCoordinator（B1-00329 / CAND-BACL-002 / D-INT-26）。

三源优先级 + 质量分动态切换协调器：
- 源健康双因子：per-source 熔断器（复用 zephyr.data.source_circuit_breaker，OPEN=不健康）
  + 质量分（update_quality 注入，低于 degraded_score_threshold=降级）
- 选源：按注册优先级（1=最高）取首个健康源；现役源降级 → 切换；高优先级源恢复 → 自动回切
- 切换事件广播：event_bus.emit("data.failover.switch", payload)（EventBus 契约，可注入）
- 全部源降级超阈值：联动 trading 熔断——on_all_degraded hook（生产接 trading_kill_switch
  执行体），payload 标记 KillSwitchLevel.CIRCUIT_BREAKER + read_only_no_new_position
  （只读/禁开仓语义）；锁存防重复触发，任一源恢复即复位
- 切换与联动入审计：audit_sink 事件（生产接 AiAuditLogger 哈希链）

与既有件分工：source_circuit_breaker 管单源自动止血，market_data.failover.manager 管
vendor 主备切换执行，本协调器管跨源编排+质量分+Kill-Switch 联动（不重复实现熔断状态机）。
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Final

from zephyr.data.source_circuit_breaker import CircuitBreakerRegistry, CircuitState
from zephyr.shared.utils.time_utils import now_utc
from zephyr.trading.trading_contracts.risk.trading_kill_switch import KillSwitchLevel

logger = logging.getLogger(__name__)

__all__ = [
    "FailoverCoordinator",
    "SwitchEvent",
]

_SWITCH_TOPIC: Final[str] = "data.failover.switch"
_ALL_DEGRADED_TOPIC: Final[str] = "data.failover.all_degraded"
_ALL_DEGRADED_ACTION: Final[str] = "read_only_no_new_position"  # 只读/禁开仓


@dataclass(frozen=True)
class SwitchEvent:
    """一次切换/联动事件（不可变）。"""

    from_source: str | None
    to_source: str | None
    reason: str  # initial / source_degraded / auto_failback / all_degraded / 手动原因
    timestamp: str
    quality_snapshot: dict[str, float] = field(default_factory=dict)


class FailoverCoordinator:
    """三源优先级+质量分动态切换协调器（全部源降级联动 trading 熔断）。"""

    def __init__(
        self,
        *,
        sources: tuple[str, ...] | list[str],
        breaker_registry: CircuitBreakerRegistry | None = None,
        degraded_score_threshold: float = 0.5,
        event_bus: Any = None,
        on_all_degraded: Callable[[dict[str, Any]], None] | None = None,
        audit_sink: Callable[[dict[str, Any]], None] | None = None,
        clock: Callable[[], Any] = now_utc,
    ) -> None:
        if not sources:
            raise ValueError("sources 不能为空（至少一个数据源）")
        self._priority: list[str] = list(sources)  # 索引即优先级（0=最高）
        self._breakers = breaker_registry or CircuitBreakerRegistry()
        self._threshold = degraded_score_threshold
        self._bus = event_bus
        self._on_all_degraded = on_all_degraded
        self._audit_sink = audit_sink
        self._clock = clock
        self._quality: dict[str, float] = {s: 1.0 for s in sources}
        self._active: str | None = None
        self._all_degraded_latched = False

    # ── 观测摄入 ──────────────────────────────────────────

    def update_quality(self, source: str, score: float) -> None:
        """更新源质量分（0..1，越界截断）。"""
        if source not in self._quality:
            logger.warning("failover: unknown source %s quality ignored", source)
            return
        self._quality[source] = min(1.0, max(0.0, float(score)))

    def quality_of(self, source: str) -> float:
        return self._quality.get(source, 0.0)

    def report_success(self, source: str) -> None:
        if source in self._quality:
            self._breakers.record_success(source)

    def report_failure(self, source: str) -> None:
        if source in self._quality:
            self._breakers.record_failure(source)

    def breaker_state(self, source: str) -> CircuitState | None:
        if source not in self._quality:
            return None
        return self._breakers.state(source)

    # ── 状态查询 ──────────────────────────────────────────

    def active_source(self) -> str | None:
        return self._active

    def all_degraded(self) -> bool:
        """全部源降级超阈值（熔断 OPEN 或质量分低于阈值）。"""
        return all(not self._is_healthy(s) for s in self._priority)

    # ── 核心编排 ──────────────────────────────────────────

    def evaluate(self) -> SwitchEvent | None:
        """评估一次选源：初始选择/降级切换/恢复回切/全降级联动。"""
        try:
            return self._evaluate_inner()
        except Exception:  # noqa: BLE001 — 协调器不得阻断数据主链路
            logger.warning("failover evaluate suppressed error", exc_info=True)
            return None

    def force_switch(self, to_source: str, *, reason: str = "manual") -> SwitchEvent | None:
        """手动强制切换（目标须为已注册源）。"""
        if to_source not in self._quality:
            logger.warning("failover: force_switch unknown source %s", to_source)
            return None
        return self._switch(to_source, reason)

    # ── 内部 ──────────────────────────────────────────────

    def _evaluate_inner(self) -> SwitchEvent | None:
        # 熔断状态刷新：OPEN 冷却到点 → HALF_OPEN 放行探针（协调器选源即探针）
        for s in self._priority:
            if self._breakers.state(s) is CircuitState.OPEN:
                self._breakers.allow_request(s)
        healthy = [s for s in self._priority if self._is_healthy(s)]

        # 全部源降级 → 联动 trading 熔断（锁存）
        if not healthy:
            self._active = None
            self._trigger_all_degraded()
            return SwitchEvent(
                from_source=None,
                to_source=None,
                reason="all_degraded",
                timestamp=self._now_iso(),
                quality_snapshot=dict(self._quality),
            )

        # 全降级恢复：解锁
        self._all_degraded_latched = False

        # 初始选择
        if self._active is None:
            return self._switch(healthy[0], "initial")

        # 现役源降级 → 切到最优健康源
        if not self._is_healthy(self._active):
            return self._switch(healthy[0], "source_degraded")

        # 高优先级源恢复 → 自动回切
        best = healthy[0]
        if self._priority.index(best) < self._priority.index(self._active):
            return self._switch(best, "auto_failback")

        return None

    def _is_healthy(self, source: str) -> bool:
        # OPEN=不健康；CLOSED/HALF_OPEN（探针候选）=健康，再看质量分阈值
        if self._breakers.state(source) is CircuitState.OPEN:
            return False
        return self._quality.get(source, 0.0) >= self._threshold

    def _switch(self, to_source: str, reason: str) -> SwitchEvent:
        event = SwitchEvent(
            from_source=self._active,
            to_source=to_source,
            reason=reason,
            timestamp=self._now_iso(),
            quality_snapshot=dict(self._quality),
        )
        self._active = to_source
        self._broadcast(_SWITCH_TOPIC, event)
        self._audit(
            "failover.switch",
            from_source=event.from_source,
            to_source=event.to_source,
            reason=reason,
            quality_snapshot=event.quality_snapshot,
        )
        return event

    def _trigger_all_degraded(self) -> None:
        if self._all_degraded_latched:
            return
        self._all_degraded_latched = True
        linkage = {
            "kill_switch_level": KillSwitchLevel.CIRCUIT_BREAKER.value,
            "action": _ALL_DEGRADED_ACTION,
            "reason": "全部数据源降级超阈值",
            "quality_snapshot": dict(self._quality),
        }
        self._broadcast(_ALL_DEGRADED_TOPIC, linkage)
        self._audit("failover.all_degraded", **linkage)
        if self._on_all_degraded is not None:
            try:
                self._on_all_degraded(linkage)
            except Exception:  # noqa: BLE001 — 联动 hook 异常不回灌协调器
                logger.warning("failover on_all_degraded hook failed", exc_info=True)

    def _broadcast(self, topic: str, payload: Any) -> None:
        if self._bus is None:
            return
        body = payload.__dict__ if hasattr(payload, "__dict__") else dict(payload)
        try:
            self._bus.emit(topic, body)
        except Exception:  # noqa: BLE001 — 广播失败不阻断切换主链路
            logger.warning("failover broadcast failed topic=%s", topic, exc_info=True)

    def _audit(self, event: str, **detail: Any) -> None:
        if self._audit_sink is None:
            return
        try:
            self._audit_sink({"event": event, "ts": self._now_iso(), **detail})
        except Exception:  # noqa: BLE001 — 审计失败不阻断切换主链路
            logger.warning("failover audit sink failed", exc_info=True)

    def _now_iso(self) -> str:
        now = self._clock()
        return now.isoformat() if hasattr(now, "isoformat") else str(now)
