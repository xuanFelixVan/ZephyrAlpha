# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.trackers.risk_mitigation_tracker
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/risk/test_risk_mitigation_tracker.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_risk_mitigation_tracker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""风险缓解追踪——捕获哪些克隆报告了但在N次扫描后仍未fix."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class MitigationEntry:
    clone_id: str
    first_seen: str
    last_seen: str
    scan_count: int
    severity: str
    status: str = "UNFIXED"


@dataclass
class RiskMitigationTracker:
    entries: dict[str, MitigationEntry] = field(default_factory=dict)
    stale_threshold: int = 10

    def track(self, clone_id: str, severity: str) -> MitigationEntry:
        now = datetime.now(UTC).isoformat()
        if clone_id in self.entries:
            entry = self.entries[clone_id]
            entry.last_seen = now
            entry.scan_count += 1
            if entry.scan_count >= self.stale_threshold and entry.status == "UNFIXED":
                entry.status = "STALE"
            return entry

        entry = MitigationEntry(clone_id=clone_id, first_seen=now, last_seen=now, scan_count=1, severity=severity)
        self.entries[clone_id] = entry
        return entry

    def mark_fixed(self, clone_id: str) -> None:
        if clone_id in self.entries:
            self.entries[clone_id].status = "FIXED"

    def get_stale(self) -> list[MitigationEntry]:
        return [e for e in self.entries.values() if e.status == "STALE"]

    def summary(self) -> dict[str, Any]:
        total = len(self.entries)
        unfixed = sum(1 for e in self.entries.values() if e.status == "UNFIXED")
        stale = sum(1 for e in self.entries.values() if e.status == "STALE")
        fixed = sum(1 for e in self.entries.values() if e.status == "FIXED")
        return {
            "total": total,
            "unfixed": unfixed,
            "stale": stale,
            "fixed": fixed,
            "stale_threshold": self.stale_threshold,
        }
