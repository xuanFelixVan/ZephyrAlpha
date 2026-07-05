# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.budget_models
# [DOMAIN] D_OPS
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
# [A_module] module_id=MOD-RES_budget_models | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Budget Enforcer data models — MOD-INF-024

Token/Cost/Time 3D seven-level (L0-L6) budget system with pre-flight gate,
model routing, degradation management, and tamper-evident audit.
Blueprint: docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class BudgetDimension(Enum):
    TOKEN = "TOKEN"
    COST = "COST"
    TIME = "TIME"


class BudgetLevel(Enum):
    L0_NORMAL = 0
    L1_WARNING = 1
    L2_THROTTLED = 2
    L3_DEGRADED = 3
    L4_EMERGENCY = 4
    L5_HARD_STOP = 5
    L6_LOCKDOWN = 6


class GateDecision(Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    DEGRADE = "DEGRADE"
    BORROW = "BORROW"
    NARROW = "NARROW"


class ModelTier(Enum):
    PREMIUM = "PREMIUM"
    STANDARD = "STANDARD"
    ECONOMY = "ECONOMY"
    MINIMAL = "MINIMAL"


@dataclass
class BudgetPolicy:
    policy_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    dimension: BudgetDimension = BudgetDimension.TOKEN
    daily_limit: float = 1_000_000.0
    hourly_limit: float = 100_000.0
    per_request_limit: float = 16_000.0
    warning_threshold: float = 0.70
    throttle_threshold: float = 0.85
    degrade_threshold: float = 0.90
    emergency_threshold: float = 0.95
    hard_stop_threshold: float = 0.98
    enabled: bool = True


@dataclass
class BudgetConsumption:
    consumption_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    policy_id: str = ""
    dimension: BudgetDimension = BudgetDimension.TOKEN
    consumed_daily: float = 0.0
    consumed_hourly: float = 0.0
    consumed_per_request: float = 0.0
    request_count_daily: int = 0
    last_reset_daily: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_reset_hourly: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class GateResult:
    request_id: str
    decision: GateDecision
    reason: str = ""
    budget_level: BudgetLevel = BudgetLevel.L0_NORMAL
    model_tier: ModelTier = ModelTier.STANDARD
    estimated_tokens: int = 0
    estimated_cost: float = 0.0
    remaining_daily: float = 0.0
    remaining_hourly: float = 0.0


@dataclass
class BudgetAlert:
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    policy_id: str = ""
    dimension: BudgetDimension = BudgetDimension.TOKEN
    level: BudgetLevel = BudgetLevel.L0_NORMAL
    message: str = ""
    triggered_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    acknowledged: bool = False


@dataclass
class DegradationStep:
    step_id: int
    description: str
    model_tier: ModelTier
    auto_trigger_level: BudgetLevel
    max_tokens_per_request: int = 16_000
    cooldown_seconds: int = 300
