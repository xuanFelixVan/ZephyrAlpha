# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.escalation_models
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-RES_escalation_models | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Escalation Protocol data models — MOD-INF-022

Defines escalation events, levels (L0-L4), rules, delegation decisions, and economic guards.
Blueprint: docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
"""

from __future__ import annotations

from typing import Final
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class EscalationLevel(Enum):
    L0_SELF_HEAL = 0
    L1_AUTO_FIX = 1
    L2_HUMAN_REVIEW = 2
    L3_CRITICAL = 3
    L4_EMERGENCY = 4


class EscalationState(Enum):
    DETECTED = "DETECTED"
    EVALUATING = "EVALUATING"
    ESCALATED = "ESCALATED"
    DELEGATED = "DELEGATED"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"
    TIMED_OUT = "TIMED_OUT"


class RuleCategory(Enum):
    AUTO_GUARD_FAILURE = "auto_guard_failure"
    BUDGET_EXCEEDED = "budget_exceeded"
    DRIFT_DETECTED = "drift_detected"
    DEADLOCK = "deadlock"
    TIMEOUT = "timeout"
    QUALITY_DEGRADATION = "quality_degradation"
    SECURITY_VIOLATION = "security_violation"
    OWNER_ABSENT = "owner_absent"
    CASCADE_FAILURE = "cascade_failure"
    REWARD_HACKING_REBOUND = "reward_hacking_rebound"
    CUSTOM = "custom"


class DelegationStrategy(Enum):
    LOAD_BALANCED = "load_balanced"
    EXPERTISE_MATCH = "expertise_match"
    ROUND_ROBIN = "round_robin"
    PRIORITY_QUEUE = "priority_queue"
    NONE = "none"


@dataclass
class EscalationEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    module_id: str = "MOD-INF-022"
    source_event_id: str | None = None
    category: RuleCategory = RuleCategory.CUSTOM
    level: EscalationLevel = EscalationLevel.L0_SELF_HEAL
    state: EscalationState = EscalationState.DETECTED
    description: str = ""
    owner_id: str | None = None
    delegate_id: str | None = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    resolved_at: datetime | None = None
    circuit_breaker_triggered: bool = False
    economic_guard_passed: bool = True
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class EscalationRule:
    rule_id: str
    category: RuleCategory
    target_level: EscalationLevel
    priority: int = 0
    condition: str = ""
    auto_escalate: bool = True
    cooldown_seconds: int = 300
    max_escalations_per_hour: int = 10
    delegate_strategy: DelegationStrategy = DelegationStrategy.NONE
    notification_channels: list[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class EconomicGuard:
    guard_id: str
    max_cost_per_escalation: float = 5.0
    daily_budget: float = 100.0
    consumed_today: float = 0.0
    last_reset: datetime = field(default_factory=lambda: datetime.now(UTC))
    hard_limit_reached: bool = False

    def can_proceed(self, estimated_cost: float = 1.0) -> bool:
        self._maybe_reset()
        if self.hard_limit_reached:
            return False
        if self.consumed_today + estimated_cost > self.daily_budget:
            self.hard_limit_reached = True
            return False
        return True

    def consume(self, cost: float) -> None:
        self._maybe_reset()
        self.consumed_today += cost

    def _maybe_reset(self) -> None:
        now = datetime.now(UTC)
        if (now - self.last_reset).days >= 1:
            self.consumed_today = 0.0
            self.hard_limit_reached = False
            self.last_reset = now


@dataclass
class EscalationResult:
    event: EscalationEvent
    escalated: bool
    new_level: EscalationLevel
    delegated_to: str | None = None
    circuit_broken: bool = False
    message: str = ""
    suggestion: str = ""


@dataclass
class DelegationRecord:
    delegation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_owner: str = ""
    to_delegate: str = ""
    task_id: str | None = None
    strategy: DelegationStrategy = DelegationStrategy.LOAD_BALANCED
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    accepted: bool = False
    completed: bool = False
    depth_exceeded: bool = False
    deadlock_detected: bool = False


DEFAULT_ESCALATION_RULES: Final[list[EscalationRule]] = [
    EscalationRule(
        "R001",
        RuleCategory.AUTO_GUARD_FAILURE,
        EscalationLevel.L1_AUTO_FIX,
        priority=10,
        cooldown_seconds=60,
        delegate_strategy=DelegationStrategy.NONE,
    ),
    EscalationRule(
        "R002", RuleCategory.BUDGET_EXCEEDED, EscalationLevel.L2_HUMAN_REVIEW, priority=20, cooldown_seconds=300
    ),
    EscalationRule(
        "R003",
        RuleCategory.DRIFT_DETECTED,
        EscalationLevel.L1_AUTO_FIX,
        priority=15,
        cooldown_seconds=120,
        delegate_strategy=DelegationStrategy.EXPERTISE_MATCH,
    ),
    EscalationRule(
        "R004",
        RuleCategory.DEADLOCK,
        EscalationLevel.L3_CRITICAL,
        priority=50,
        cooldown_seconds=60,
        delegate_strategy=DelegationStrategy.LOAD_BALANCED,
    ),
    EscalationRule("R005", RuleCategory.TIMEOUT, EscalationLevel.L1_AUTO_FIX, priority=8, cooldown_seconds=60),
    EscalationRule(
        "R006", RuleCategory.QUALITY_DEGRADATION, EscalationLevel.L2_HUMAN_REVIEW, priority=12, cooldown_seconds=600
    ),
    EscalationRule(
        "R007", RuleCategory.SECURITY_VIOLATION, EscalationLevel.L4_EMERGENCY, priority=100, cooldown_seconds=30
    ),
    EscalationRule(
        "R008",
        RuleCategory.OWNER_ABSENT,
        EscalationLevel.L2_HUMAN_REVIEW,
        priority=25,
        cooldown_seconds=300,
        delegate_strategy=DelegationStrategy.LOAD_BALANCED,
    ),
    EscalationRule(
        "R009", RuleCategory.CASCADE_FAILURE, EscalationLevel.L3_CRITICAL, priority=60, cooldown_seconds=120
    ),
    EscalationRule(
        "R010",
        RuleCategory.REWARD_HACKING_REBOUND,
        EscalationLevel.L4_EMERGENCY,
        priority=200,
        cooldown_seconds=0,
        delegate_strategy=DelegationStrategy.NONE,
    ),
]
