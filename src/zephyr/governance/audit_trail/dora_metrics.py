# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.governance.audit_trail.dora_metrics
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不可变审计记录;密码学完整性;只追加
# [MODIFY-GUARD] docs/03_modules/_domain-governance/audit-trail/blueprint.md;src/zephyr/audit-trail/__init__.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] IntegrityError;WriteError
# [TESTS] tests/test_audit_trail/
# [A_module] module_id=MOD-GOV_dora_metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class DORATargets:
    deployment_frequency_weekly: int = 7
    lead_time_hours: float = 1.0
    change_failure_rate_pct: float = 5.0
    mttr_hours: float = 1.0


@dataclass
class DORACollector:
    targets: DORATargets = field(default_factory=DORATargets)
    deployments_this_week: int = 0
    avg_lead_time_hours: float = 0.0
    failure_count: int = 0
    total_changes: int = 0
    incidents: int = 0
    total_recovery_hours: float = 0.0
    last_updated: str | None = None

    @property
    def df_met(self) -> bool:
        return self.deployments_this_week >= self.targets.deployment_frequency_weekly

    @property
    def lt_met(self) -> bool:
        return self.avg_lead_time_hours < self.targets.lead_time_hours

    @property
    def cfr(self) -> float:
        if self.total_changes == 0:
            return 0.0
        return round(self.failure_count / self.total_changes * 100, 2)

    @property
    def cfr_met(self) -> bool:
        return self.cfr < self.targets.change_failure_rate_pct

    @property
    def mttr(self) -> float:
        if self.incidents == 0:
            return 0.0
        return round(self.total_recovery_hours / self.incidents, 2)

    @property
    def mttr_met(self) -> bool:
        return self.mttr < self.targets.mttr_hours

    @property
    def all_met(self) -> bool:
        return self.df_met and self.lt_met and self.cfr_met and self.mttr_met

    def record_deployment(self, count: int = 1) -> None:
        self.deployments_this_week += count
        self.last_updated = datetime.now(UTC).isoformat()

    def record_change(self, lead_time_hours: float, failed: bool = False) -> None:
        self.total_changes += 1
        self.avg_lead_time_hours = round(
            (self.avg_lead_time_hours * (self.total_changes - 1) + lead_time_hours) / self.total_changes,
            2,
        )
        if failed:
            self.failure_count += 1
        self.last_updated = datetime.now(UTC).isoformat()

    def record_incident(self, recovery_hours: float) -> None:
        self.incidents += 1
        self.total_recovery_hours += recovery_hours
        self.last_updated = datetime.now(UTC).isoformat()

    def report(self) -> dict[str, object]:
        return {
            "deployment_frequency": f"{self.deployments_this_week}/week (target ≥{self.targets.deployment_frequency_weekly}) {'✅' if self.df_met else '❌'}",
            "lead_time": f"{self.avg_lead_time_hours}h (target <{self.targets.lead_time_hours}h) {'✅' if self.lt_met else '❌'}",
            "change_failure_rate": f"{self.cfr}% (target <{self.targets.change_failure_rate_pct}%) {'✅' if self.cfr_met else '❌'}",
            "mttr": f"{self.mttr}h (target <{self.targets.mttr_hours}h) {'✅' if self.mttr_met else '❌'}",
            "all_met": self.all_met,
        }
