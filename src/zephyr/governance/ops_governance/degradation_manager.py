# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.degradation_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.ops_governance.budget_models
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_degradation_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import time
from dataclasses import dataclass, field
from enum import Enum, auto

from .budget_models import BudgetDimension, ModelTier


class DegradationLevel(Enum):
    NORMAL = (auto(), "正常模式")
    NOTIFY = (auto(), "通知——预算消耗 50%")
    WARNING = (auto(), "警告——预算消耗 70%")
    MODEL_SWITCH = (auto(), "模型降级 / 上下文压缩——80%")
    COMPRESS = (auto(), "惨烈压缩——85%")
    MINIMAL = (auto(), "最小模式——95%")
    HALT = (auto(), "停止——100%")


@dataclass
class DegradationAction:
    level: DegradationLevel
    source_dimension: BudgetDimension
    action: str
    model_tier: ModelTier = ModelTier.MINIMAL
    narrow_context: bool = False
    reroute_provider: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class DegradationState:
    current_level: DegradationLevel = DegradationLevel.NORMAL
    reason: str = ""
    since: float = field(default_factory=time.time)
    history: list[DegradationAction] = field(default_factory=list)
    recovery_cooldown_until: float = 0.0
    forced_by: str = ""

    @property
    def is_degraded(self) -> bool:
        return self.current_level != DegradationLevel.NORMAL

    def can_advance(self) -> bool:
        return self.current_level != DegradationLevel.HALT

    def can_retreat(self) -> bool:
        now = time.time()
        return now > self.recovery_cooldown_until


class DegradationManager:
    LEVEL_ORDER: list[DegradationLevel] = [
        DegradationLevel.NORMAL,
        DegradationLevel.NOTIFY,
        DegradationLevel.WARNING,
        DegradationLevel.MODEL_SWITCH,
        DegradationLevel.COMPRESS,
        DegradationLevel.MINIMAL,
        DegradationLevel.HALT,
    ]

    THRESHOLDS: dict[DegradationLevel, float] = {
        DegradationLevel.NOTIFY: 0.50,
        DegradationLevel.WARNING: 0.70,
        DegradationLevel.MODEL_SWITCH: 0.80,
        DegradationLevel.COMPRESS: 0.85,
        DegradationLevel.MINIMAL: 0.95,
        DegradationLevel.HALT: 1.00,
    }

    def __init__(self, recovery_cooldown: float = 180.0, anti_spiral_limit: int = 1):
        self._state = DegradationState()
        self._lock = threading.Lock()
        self._recovery_cooldown = recovery_cooldown
        self._anti_spiral_limit = anti_spiral_limit
        self._recent_advances: list[float] = []
        self._circuit_breaker_failures: int = 0
        self._circuit_breaker_open: bool = False
        self._circuit_breaker_opened_at: float = 0.0
        self._circuit_breaker_threshold: int = 3
        self._circuit_breaker_reset_seconds: float = 300.0

    @property
    def state(self) -> DegradationState:
        with self._lock:
            return self._state

    def evaluate(
        self,
        usage_ratio: float,
        dimension: BudgetDimension,
        current_tier: ModelTier = ModelTier.ECONOMY,
    ) -> DegradationAction | None:
        with self._lock:
            return self._evaluate_locked(usage_ratio, dimension, current_tier)

    def _evaluate_locked(
        self,
        usage_ratio: float,
        dimension: BudgetDimension,
        current_tier: ModelTier,
    ) -> DegradationAction | None:
        if self._circuit_breaker_open:
            if time.time() - self._circuit_breaker_opened_at > self._circuit_breaker_reset_seconds:
                self._circuit_breaker_open = False
                self._circuit_breaker_failures = 0
            else:
                return None

        if usage_ratio >= 1.0:
            return self._force_halt(dimension)

        target_level = self._resolve_level(usage_ratio)
        if target_level == DegradationLevel.NORMAL:
            return self._try_retreat(dimension)

        if target_level.value[0] <= self._state.current_level.value[0]:
            return None

        return self._advance(target_level, dimension, current_tier, usage_ratio)

    def _resolve_level(self, usage_ratio: float) -> DegradationLevel:
        best = DegradationLevel.NORMAL
        for level in DegradationLevel:
            threshold = self.THRESHOLDS.get(level)
            if threshold is not None and usage_ratio >= threshold:
                best = level
        return best

    def _advance(
        self,
        target: DegradationLevel,
        dimension: BudgetDimension,
        current_tier: ModelTier,
        usage_ratio: float,
    ) -> DegradationAction | None:
        now = time.time()
        self._recent_advances = [t for t in self._recent_advances if now - t < 60]
        if len(self._recent_advances) >= self._anti_spiral_limit:
            return None
        self._recent_advances.append(now)

        new_tier = self._compute_target_tier(target, current_tier)

        action = DegradationAction(
            level=target,
            source_dimension=dimension,
            action=target.name,
            model_tier=new_tier,
            narrow_context=target in (DegradationLevel.COMPRESS, DegradationLevel.MINIMAL),
        )
        self._state.current_level = target
        self._state.reason = f"{dimension.value} usage={usage_ratio:.1%}"
        self._state.since = now
        self._state.history.append(action)

        return action

    def _try_retreat(self, dimension: BudgetDimension) -> DegradationAction | None:
        if not self._state.is_degraded:
            return None
        if not self._state.can_retreat():
            return None

        self._state.current_level = DegradationLevel.NORMAL
        self._state.reason = "usage normalized"
        self._state.since = time.time()
        self._state.recovery_cooldown_until = time.time() + self._recovery_cooldown

        retreat = DegradationAction(
            level=DegradationLevel.NORMAL,
            source_dimension=dimension,
            action="RETREAT",
        )
        self._state.history.append(retreat)
        return retreat

    def _force_halt(self, dimension: BudgetDimension) -> DegradationAction:
        self._state.current_level = DegradationLevel.HALT
        self._state.reason = f"{dimension.value} exhausted"
        self._state.since = time.time()
        self._state.forced_by = dimension.value

        halt = DegradationAction(
            level=DegradationLevel.HALT,
            source_dimension=dimension,
            action="HALT",
        )
        self._state.history.append(halt)
        return halt

    @staticmethod
    def _compute_target_tier(level: DegradationLevel, current: ModelTier) -> ModelTier:
        mapping = {
            DegradationLevel.MODEL_SWITCH: ModelTier.ECONOMY,
            DegradationLevel.COMPRESS: ModelTier.MINIMAL,
            DegradationLevel.MINIMAL: ModelTier.MINIMAL,
        }
        target = mapping.get(level)
        if target is None:
            return current
        tier_order = [ModelTier.PREMIUM, ModelTier.STANDARD, ModelTier.ECONOMY, ModelTier.MINIMAL]
        current_idx = tier_order.index(current) if current in tier_order else len(tier_order) - 1
        target_idx = tier_order.index(target)
        if target_idx <= current_idx:
            return current
        return target

    def manual_retreat(self, reason: str = "manual") -> DegradationAction:
        with self._lock:
            self._state.current_level = DegradationLevel.NORMAL
            self._state.reason = reason
            self._state.since = time.time()
            self._state.recovery_cooldown_until = time.time() + self._recovery_cooldown
            action = DegradationAction(
                level=DegradationLevel.NORMAL,
                source_dimension=BudgetDimension.TOKEN,
                action=reason,
            )
            self._state.history.append(action)
            return action

    def record_dependency_failure(self, dependency_name: str) -> None:
        with self._lock:
            self._circuit_breaker_failures += 1
            if self._circuit_breaker_failures >= self._circuit_breaker_threshold:
                self._circuit_breaker_open = True
                self._circuit_breaker_opened_at = time.time()

    @property
    def circuit_breaker_open(self) -> bool:
        with self._lock:
            return self._circuit_breaker_open

    def reset(self) -> None:
        with self._lock:
            self._state = DegradationState()
