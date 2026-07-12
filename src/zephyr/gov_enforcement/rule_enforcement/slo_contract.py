# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.slo_contract
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_slo_contract | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""SLO-Driven Escalation Contract — D-022-12.

SLI/SLO/Error Budget system with 4-tier budget policy and contract SLO,
tightly coupled to escalation level selection.

Reference: Google SRE (SLI/SLO/Error Budget/Burn Rate), Nasdaq Pre-Trade Risk.
"""

from __future__ import annotations

from typing import Final
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class BudgetTier(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    EXHAUSTED = "exhausted"


class ContractPriority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class SLIName(str, Enum):
    CODE_REJECTION = "code_rejection"
    CONSENSUS_CONFLICT = "consensus_conflict"
    RETRY_FATIGUE = "retry_fatigue"
    HUMAN_OVERRIDE = "human_override"
    DEADLOCK = "deadlock"
    BUDGET_CONSUMPTION = "budget_consumption"
    RESPONSE_LATENCY = "response_latency"


@dataclass
class SLIDefinition:
    name: SLIName
    description: str
    target: float
    error_budget_ratio: float
    window_seconds: float = 86400.0


@dataclass
class SLOContractTerms:
    priority: ContractPriority
    ack_timeout_s: float
    resolve_timeout_s: float
    penalty: str


@dataclass
class SLIReading:
    name: SLIName
    value: float
    timestamp: float = field(default_factory=time.time)
    within_slo: bool = True


@dataclass
class BudgetSnapshot:
    tier: BudgetTier
    error_budget_remaining_pct: float
    burn_rate_per_hour: float
    cooldown_active: bool = False
    cooldown_until_s: float = 0.0


DEFAULT_SLIS: Final[dict[SLIName, SLIDefinition]] = {
    SLIName.CODE_REJECTION: SLIDefinition(
        name=SLIName.CODE_REJECTION,
        description="AI代码被Gate/GLM拒绝率",
        target=0.95,
        error_budget_ratio=0.05,
    ),
    SLIName.CONSENSUS_CONFLICT: SLIDefinition(
        name=SLIName.CONSENSUS_CONFLICT,
        description="Pipeline多模型共识破裂率",
        target=0.98,
        error_budget_ratio=0.02,
    ),
    SLIName.RETRY_FATIGUE: SLIDefinition(
        name=SLIName.RETRY_FATIGUE,
        description="操作达最大重试比例",
        target=0.90,
        error_budget_ratio=0.10,
    ),
    SLIName.HUMAN_OVERRIDE: SLIDefinition(
        name=SLIName.HUMAN_OVERRIDE,
        description="AI决策被人推翻比例",
        target=0.85,
        error_budget_ratio=0.15,
    ),
    SLIName.DEADLOCK: SLIDefinition(
        name=SLIName.DEADLOCK,
        description="多Agent死锁发生率",
        target=0.999,
        error_budget_ratio=0.001,
    ),
    SLIName.BUDGET_CONSUMPTION: SLIDefinition(
        name=SLIName.BUDGET_CONSUMPTION,
        description="Token/API预算消耗速度",
        target=0.90,
        error_budget_ratio=0.10,
    ),
    SLIName.RESPONSE_LATENCY: SLIDefinition(
        name=SLIName.RESPONSE_LATENCY,
        description="升级引擎判定延迟",
        target=0.99,
        error_budget_ratio=0.01,
    ),
}

DEFAULT_CONTRACTS: Final[dict[ContractPriority, SLOContractTerms]] = {
    ContractPriority.P0: SLOContractTerms(
        priority=ContractPriority.P0,
        ack_timeout_s=900,
        resolve_timeout_s=14400,
        penalty="超时->安全模式",
    ),
    ContractPriority.P1: SLOContractTerms(
        priority=ContractPriority.P1,
        ack_timeout_s=14400,
        resolve_timeout_s=86400,
        penalty="升级P0",
    ),
    ContractPriority.P2: SLOContractTerms(
        priority=ContractPriority.P2,
        ack_timeout_s=86400,
        resolve_timeout_s=259200,
        penalty="auto_close",
    ),
}

TRADING_OVERRIDE: Final[SLOContractTerms] = SLOContractTerms(
    priority=ContractPriority.P0,
    ack_timeout_s=300,
    resolve_timeout_s=900,
    penalty="超时清仓",
)

TIER_POLICY: Final[dict[BudgetTier, dict[str, Any]]] = {
    BudgetTier.HEALTHY: {
        "threshold": 50.0,
        "auto_guard_modifier": 1.0,
        "description": "正常AI自主",
    },
    BudgetTier.WARNING: {
        "threshold": 20.0,
        "auto_guard_modifier": 0.9,
        "description": "auto_guard阈值降低10%",
    },
    BudgetTier.CRITICAL: {
        "threshold": 0.0,
        "auto_guard_modifier": 0.6,
        "description": "所有操作至少auto_guard+通知Owner",
    },
    BudgetTier.EXHAUSTED: {
        "threshold": -1.0,
        "auto_guard_modifier": 0.0,
        "description": "锁定——禁止自主高风险->Owner手动重置+24h冷却",
    },
}


class SLOContractEngine:
    """SLO-driven escalation contract engine.

    Tracks SLI readings against SLO targets, manages error budgets across
    4 tiers, and provides contract escalation behavior based on burn rate.
    """

    def __init__(
        self,
        slis: dict[SLIName, SLIDefinition] | None = None,
        contracts: dict[ContractPriority, SLOContractTerms] | None = None,
        window_seconds: float = 86400.0,
    ):
        self._slis = dict(slis) if slis else dict(DEFAULT_SLIS)
        self._contracts = dict(contracts) if contracts else dict(DEFAULT_CONTRACTS)
        self._window_seconds = window_seconds
        self._readings: dict[SLIName, list[SLIReading]] = {sli: [] for sli in self._slis}
        self._budget_snapshot: dict[SLIName, BudgetSnapshot] = {}
        self._cooldown_lock = False
        self._cooldown_until = 0.0
        for sli in self._slis:
            self._recompute_budget(sli)

    @property
    def window_seconds(self) -> float:
        return self._window_seconds

    @property
    def cooldown_active(self) -> bool:
        if self._cooldown_lock and time.time() < self._cooldown_until:
            return True
        self._cooldown_lock = False
        return False

    def record(self, sli_name: SLIName, value: float) -> SLIReading:
        if sli_name not in self._slis:
            raise KeyError(f"Unknown SLI: {sli_name}")
        sla = self._slis[sli_name]
        within_slo = value >= sla.target
        reading = SLIReading(name=sli_name, value=value, within_slo=within_slo)
        self._readings[sli_name].append(reading)
        cutoff = time.time() - self._window_seconds
        self._readings[sli_name] = [r for r in self._readings[sli_name] if r.timestamp > cutoff]
        self._recompute_budget(sli_name)
        return reading

    def get_budget(self, sli_name: SLIName) -> BudgetSnapshot:
        if sli_name not in self._budget_snapshot:
            self._recompute_budget(sli_name)
        return self._budget_snapshot.get(sli_name) or BudgetSnapshot(
            tier=BudgetTier.HEALTHY,
            error_budget_remaining_pct=100.0,
            burn_rate_per_hour=0.0,
        )

    def get_worst_budget_tier(self) -> BudgetSnapshot:
        worst: BudgetSnapshot | None = None
        for sli_name in self._slis:
            snap = self.get_budget(sli_name)
            if (
                worst is None
                or budget_tier_ordering(snap.tier) > budget_tier_ordering(worst.tier)
                or (snap.tier == worst.tier and snap.error_budget_remaining_pct < worst.error_budget_remaining_pct)
            ):
                worst = snap
        return worst or BudgetSnapshot(
            tier=BudgetTier.HEALTHY,
            error_budget_remaining_pct=100.0,
            burn_rate_per_hour=0.0,
        )

    def get_contract(self, priority: ContractPriority) -> SLOContractTerms:
        return self._contracts.get(priority, DEFAULT_CONTRACTS[ContractPriority.P2])

    def get_trading_override(self) -> SLOContractTerms:
        return TRADING_OVERRIDE

    def get_recommended_scaling(self) -> dict[str, Any]:
        worst = self.get_worst_budget_tier()
        tier = worst.tier
        policy = TIER_POLICY[tier]

        if tier is BudgetTier.HEALTHY or tier is BudgetTier.WARNING:
            level_offset = 0
        elif tier is BudgetTier.CRITICAL:
            level_offset = 1
        else:
            level_offset = 4

        return {
            "current_tier": tier.value,
            "error_budget_remaining_pct": worst.error_budget_remaining_pct,
            "burn_rate_per_hour": worst.burn_rate_per_hour,
            "auto_guard_modifier": policy["auto_guard_modifier"],
            "escalation_level_offset": level_offset,
            "description": policy["description"],
            "cooldown_active": worst.cooldown_active,
        }

    def should_escalate(self, sli_name: SLIName, value: float) -> tuple[bool, str]:
        reading = self.record(sli_name, value)
        budget = self.get_budget(sli_name)
        if budget.tier is BudgetTier.EXHAUSTED:
            return True, f"Error budget exhausted for {sli_name.value}"
        if budget.tier is BudgetTier.CRITICAL and not reading.within_slo:
            return True, f"Critical budget + SLO violation for {sli_name.value}"
        if not reading.within_slo and budget.burn_rate_per_hour > 5.0:
            return True, f"High burn rate ({budget.burn_rate_per_hour:.1f}/h) for {sli_name.value}"
        return False, "Within acceptable thresholds"

    def force_exhaust(self, sli_name: SLIName) -> None:
        now = time.time()
        self._cooldown_lock = True
        self._cooldown_until = now + 86400
        if sli_name in self._budget_snapshot:
            snap = self._budget_snapshot[sli_name]
            self._budget_snapshot[sli_name] = BudgetSnapshot(
                tier=BudgetTier.EXHAUSTED,
                error_budget_remaining_pct=0.0,
                burn_rate_per_hour=snap.burn_rate_per_hour,
                cooldown_active=True,
                cooldown_until_s=now + 86400,
            )

    def reset_budget(self, sli_name: SLIName | None = None) -> None:
        targets = [sli_name] if sli_name else list(self._slis.keys())
        for name in targets:
            if name in self._slis:
                self._budget_snapshot[name] = BudgetSnapshot(
                    tier=BudgetTier.HEALTHY,
                    error_budget_remaining_pct=100.0,
                    burn_rate_per_hour=0.0,
                    cooldown_active=False,
                    cooldown_until_s=0.0,
                )
                self._readings[name] = []

    def summary(self) -> dict[str, Any]:
        scaling = self.get_recommended_scaling()
        budgets = {}
        for sli_name in self._slis:
            snap = self.get_budget(sli_name)
            budgets[sli_name.value] = {
                "tier": snap.tier.value,
                "budget_pct": snap.error_budget_remaining_pct,
                "burn_rate_per_h": snap.burn_rate_per_hour,
            }
        return {
            "scaling_recommendation": scaling,
            "budgets": budgets,
            "contract_slo": {
                p.value: {
                    "ack_s": self._contracts[p].ack_timeout_s,
                    "resolve_s": self._contracts[p].resolve_timeout_s,
                }
                for p in ContractPriority
            },
        }

    def _recompute_budget(self, sli_name: SLIName) -> None:
        sla = self._slis[sli_name]
        readings = self._readings.get(sli_name, [])
        if not readings:
            self._budget_snapshot[sli_name] = BudgetSnapshot(
                tier=BudgetTier.HEALTHY,
                error_budget_remaining_pct=100.0,
                burn_rate_per_hour=0.0,
            )
            return
        violations = sum(1 for r in readings if not r.within_slo)
        total = len(readings)
        violation_rate = violations / total
        error_budget_consumed = violation_rate
        error_budget_remaining = max(0.0, sla.error_budget_ratio - error_budget_consumed)
        remaining_pct = (
            (error_budget_remaining / sla.error_budget_ratio) * 100.0 if sla.error_budget_ratio > 0 else 100.0
        )
        remaining_pct = max(0.0, min(100.0, remaining_pct))

        if readings:
            first_ts = readings[0].timestamp
            last_ts = readings[-1].timestamp
            duration_h = max(0.0001, (last_ts - first_ts) / 3600.0)
            burn_rate_per_hour = (
                (error_budget_consumed / sla.error_budget_ratio * 100.0) / duration_h
                if sla.error_budget_ratio > 0
                else 0.0
            )
        else:
            burn_rate_per_hour = 0.0

        cooldown = self._cooldown_lock and time.time() < self._cooldown_until
        if cooldown:
            remaining_pct = 0.0

        tier = BudgetTier.HEALTHY
        if remaining_pct <= 0:
            tier = BudgetTier.EXHAUSTED
        elif remaining_pct <= 20:
            tier = BudgetTier.CRITICAL
        elif remaining_pct <= 50:
            tier = BudgetTier.WARNING

        self._budget_snapshot[sli_name] = BudgetSnapshot(
            tier=tier,
            error_budget_remaining_pct=remaining_pct,
            burn_rate_per_hour=burn_rate_per_hour,
            cooldown_active=cooldown,
            cooldown_until_s=self._cooldown_until if cooldown else 0.0,
        )


def budget_tier_ordering(tier: BudgetTier) -> int:  # 5.153.14 修复: PascalCase_snake_case混合改为snake_case
    _order = {
        BudgetTier.HEALTHY: 0,
        BudgetTier.WARNING: 1,
        BudgetTier.CRITICAL: 2,
        BudgetTier.EXHAUSTED: 3,
    }
    return _order.get(tier, 0)
