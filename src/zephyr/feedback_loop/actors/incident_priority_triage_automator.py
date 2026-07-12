# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.actors.incident_priority_triage_automator
# [DOMAIN] D_FEEDBACK_LOOP
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
# [A_module] module_id=MOD-UNK_incident_priority_triage_automator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Incident Priority Triage Automator — v0.37.0 R463

Blindspot: Security/operational incidents arrive at varying velocities;
manual triage causes delay in critical response.

Risk: R463 — Low-priority incident blocks response to high-priority one.

Mitigation: Automated SEV-level classification based on blast radius,
data sensitivity, and system criticality. P0/P1 auto-page; P3/P4 batch.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


@dataclass
class IncidentPriorityTriageAutomator:
    auto_page_threshold: Severity = Severity.P1
    batch_window: float = 600.0

    incidents: list[dict] = field(default_factory=list)
    triage_count: dict[str, int] = field(default_factory=lambda: {s.value: 0 for s in Severity})

    def classify(self, incident: dict) -> Severity:
        score = 0
        if incident.get("data_sensitive", False):
            score += 3
        if incident.get("user_facing", False):
            score += 2
        if incident.get("system_critical", False):
            score += 2
        blast = incident.get("blast_radius", 0)
        score += min(blast, 4)

        if score >= 7:
            return Severity.P0
        elif score >= 5:
            return Severity.P1
        elif score >= 3:
            return Severity.P2
        elif score >= 1:
            return Severity.P3
        return Severity.P4

    def triage(self, incident: dict) -> dict:
        severity = self.classify(incident)
        incident["severity"] = severity.value
        incident["triaged_at"] = __import__("time").time()
        self.incidents.append(incident)
        self.triage_count[severity.value] = self.triage_count.get(severity.value, 0) + 1

        should_page = self._severity_rank(severity) <= self._severity_rank(self.auto_page_threshold)
        return {
            **incident,
            "action": "PAGE" if should_page else "BATCH",
            "severity": severity.value,
        }

    @staticmethod
    def _severity_rank(s: Severity) -> int:
        return list(Severity).index(s)

    def get_counts(self) -> dict:
        return dict(self.triage_count)
