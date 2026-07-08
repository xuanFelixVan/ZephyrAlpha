# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.diagnosis.knowledge_bus_factor_monitor
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_knowledge_bus_factor_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Knowledge Bus Factor Monitor — v0.38.0 R481

Blindspot: "Bus factor" — the number of people who would need to be hit by a bus
before the project is in serious trouble. In 1-person+AI maintenance, bus factor=1
by definition. But system knowledge also concentrates in specific agents/modules.

Risk: R481 — The one human owner is also the only person who understands X subsystem.
If owner is unavailable + that subsystem fails -> no one (human or AI) can fix it.

Mitigation: Track knowledge distribution across subsystems. Assign and monitor
"AI bus factor" — how many independent agents understand each subsystem. Alert when
any subsystem has bus factor < 2. Generate knowledge transfer recommendations.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class KnowledgeBusFactorMonitor:
    min_bus_factor: int = 2
    max_owner_assignments: int = 5

    subsystem_owners: dict[str, list[str]] = field(default_factory=dict)
    human_assignments: dict[str, list[str]] = field(default_factory=dict)
    bus_factor_alerts: list[dict] = field(default_factory=list)

    def register_subsystem(self, subsystem: str, owners: list[str]) -> None:
        self.subsystem_owners[subsystem] = owners
        for owner in owners:
            if owner not in self.human_assignments:
                self.human_assignments[owner] = []
            if subsystem not in self.human_assignments[owner]:
                self.human_assignments[owner].append(subsystem)

    def remove_owner(self, subsystem: str, owner: str) -> None:
        if subsystem in self.subsystem_owners and owner in self.subsystem_owners[subsystem]:
            self.subsystem_owners[subsystem].remove(owner)
        if owner in self.human_assignments and subsystem in self.human_assignments[owner]:
            self.human_assignments[owner].remove(subsystem)

    def check_bus_factor(self) -> dict:
        alerts = []
        critical_subsystems = []

        for subsystem, owners in self.subsystem_owners.items():
            bf = len(owners)
            if bf < self.min_bus_factor:
                critical_subsystems.append(subsystem)
                alerts.append(
                    {
                        "subsystem": subsystem,
                        "bus_factor": bf,
                        "owners": list(owners),
                        "severity": "CRITICAL" if bf == 0 else "HIGH" if bf == 1 else "MEDIUM",
                        "recommendation": "assign_backup_owner" if bf < 2 else "monitor",
                    }
                )

        for human, subsystems in self.human_assignments.items():
            if len(subsystems) > self.max_owner_assignments:
                alerts.append(
                    {
                        "human_owner": human,
                        "assignment_count": len(subsystems),
                        "max_recommended": self.max_owner_assignments,
                        "severity": "HIGH",
                        "recommendation": "redistribute_knowledge_ownership",
                    }
                )

        if alerts:
            self.bus_factor_alerts.extend([{**a, "ts": time.time()} for a in alerts])

        return {
            "critical_subsystems": critical_subsystems,
            "total_subsystems": len(self.subsystem_owners),
            "alerts": alerts,
            "overall_bus_factor_health": 1.0 - len(critical_subsystems) / max(len(self.subsystem_owners), 1),
        }

    def get_knowledge_heatmap(self) -> dict:
        heatmap = {}
        for subsystem, owners in self.subsystem_owners.items():
            heatmap[subsystem] = {
                "bus_factor": len(owners),
                "owners": owners,
                "risk_level": "SAFE" if len(owners) >= 2 else "AT_RISK" if len(owners) == 1 else "ORPHANED",
            }
        return heatmap

    def suggest_knowledge_transfer(self) -> list[dict]:
        suggestions = []
        overloaded = sorted(
            [(h, len(s)) for h, s in self.human_assignments.items() if len(s) > self.max_owner_assignments],
            key=lambda x: -x[1],
        )
        underloaded = sorted(
            [(h, len(s)) for h, s in self.human_assignments.items() if len(s) < self.max_owner_assignments],
            key=lambda x: x[1],
        )

        for sub, owners in self.subsystem_owners.items():
            if len(owners) < self.min_bus_factor and underloaded:
                suggestions.append(
                    {
                        "subsystem": sub,
                        "current_bus_factor": len(owners),
                        "suggested_new_owner": underloaded[0][0],
                    }
                )

        return suggestions

    def overall_bus_factor_score(self) -> float:
        if not self.subsystem_owners:
            return 1.0
        safe = sum(1 for owners in self.subsystem_owners.values() if len(owners) >= self.min_bus_factor)
        return round(safe / len(self.subsystem_owners), 3)
