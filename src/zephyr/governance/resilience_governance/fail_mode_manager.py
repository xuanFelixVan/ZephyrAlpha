# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.resilience_governance.fail_mode_manager
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_fail_mode_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import time
from dataclasses import dataclass, field
from enum import Enum, auto


class FailMode(Enum):
    OPEN = auto()
    CLOSED = auto()
    DEGRADED = auto()
    DEAD = auto()


@dataclass
class FailModeState:
    mode: FailMode
    reason: str
    since: float = field(default_factory=time.time)
    recoverable: bool = True
    auto_recovery_at: float | None = None


@dataclass
class HealthCheck:
    component: str
    healthy: bool
    detail: str
    latency_ms: float = 0.0
    checked_at: float = field(default_factory=time.time)


class FailModeManager:
    COMPONENTS: list[str] = [
        "budget_engine",
        "degradation_manager",
        "model_router",
        "timeout_guard",
        "stream_abort_guard",
        "trust_ring_manager",
    ]

    def __init__(self, default_mode: FailMode = FailMode.OPEN):
        self._state = FailModeState(mode=default_mode, reason="initialized")
        self._health_checks: list[HealthCheck] = []
        self._fail_count: dict[str, int] = {}
        self._recovery_timeout: float = 300.0

    def record_health_check(self, component: str, healthy: bool, detail: str = "", latency_ms: float = 0.0) -> HealthCheck:
        """记录一次健康检查结果（5.12.2#4 治本：从 health_check 改名，消除"记录"vs"查询"语义混淆）。"""
        check = HealthCheck(component=component, healthy=healthy, detail=detail, latency_ms=latency_ms)
        self._health_checks.append(check)
        if not healthy:
            self._fail_count[component] = self._fail_count.get(component, 0) + 1
        return check

    def evaluate(self) -> FailModeState:
        if not self._health_checks:
            return self._state

        recent = [c for c in self._health_checks if time.time() - c.checked_at < 60]
        unhealthy = [c for c in recent if not c.healthy]
        critical_fails = sum(1 for c, n in self._fail_count.items() if n >= 3)

        if critical_fails >= 3:
            self._state = FailModeState(mode=FailMode.DEAD, reason=f"{critical_fails} 组件连续失败")
        elif len(unhealthy) >= 2:
            self._state = FailModeState(mode=FailMode.CLOSED, reason=f"{len(unhealthy)} 组件不健康")
        elif len(unhealthy) >= 1:
            self._state = FailModeState(mode=FailMode.DEGRADED, reason=f"{len(unhealthy)} 组件降级")
        else:
            if self._state.mode is not FailMode.OPEN:
                self._state = FailModeState(mode=FailMode.OPEN, reason="所有组件恢复正常")

        return self._state

    def current_mode(self) -> FailMode:
        self.evaluate()
        return self._state.mode

    def should_recover(self) -> bool:
        self.evaluate()
        if self._state.mode is FailMode.OPEN:
            return True
        if self._state.auto_recovery_at and time.time() > self._state.auto_recovery_at:
            return True
        return False

    def auto_recover(self) -> None:
        self._state = FailModeState(mode=FailMode.OPEN, reason="auto-recovery triggered")
        self._fail_count.clear()

    def recent_checks(self, n: int = 20) -> list[HealthCheck]:
        return self._health_checks[-n:]

    def component_fail_count(self, component: str) -> int:
        return self._fail_count.get(component, 0)

    def reset(self) -> None:
        self._state = FailModeState(mode=FailMode.OPEN, reason="reset")
        self._health_checks.clear()
        self._fail_count.clear()
