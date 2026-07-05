# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.forensic.automated_rca_postmortem_generator
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
# [A_module] module_id=MOD-UNK_automated_rca_postmortem_generator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Automated RCA Postmortem Generator — v0.38.0 R486

Blindspot: In 1-person+AI maintenance, postmortems are never written because
no one has time. Root cause analysis exists only in the developer's memory.
Same failure mode repeats because lessons aren't codified.

Risk: R486 — Recurring incidents never documented; tribal knowledge lost when
context switches; AI has no postmortem corpus to learn from.

Mitigation: Auto-generate postmortem from event timelines. Chain causal events
using temporal ordering + correlation. Generate timeline, 追问到底分析,
contributing factors, and action items. Format as structured document.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class IncidentSeverity(str, Enum):
    P0_CRITICAL = "P0"
    P1_HIGH = "P1"
    P2_MEDIUM = "P2"
    P3_LOW = "P3"


@dataclass
class AutomatedRCAPostmortemGenerator:
    max_timeline_events: int = 100
    root_cause_depth: int = 5
    inversion_verification_enabled: bool = True

    incident_timelines: dict[str, list[dict]] = field(default_factory=dict)
    generated_postmortems: list[dict] = field(default_factory=list)

    def start_incident(
        self, incident_id: str, severity: IncidentSeverity, title: str, affected_systems: list[str]
    ) -> None:
        self.incident_timelines[incident_id] = [
            {
                "ts": time.time(),
                "event": "INCIDENT_START",
                "severity": severity.value,
                "title": title,
                "affected": affected_systems,
            }
        ]

    def record_event(self, incident_id: str, event_type: str, description: str) -> None:
        if incident_id not in self.incident_timelines:
            return
        timeline = self.incident_timelines[incident_id]
        timeline.append({"ts": time.time(), "event": event_type, "description": description})
        if len(timeline) > self.max_timeline_events:
            self.incident_timelines[incident_id] = timeline[-self.max_timeline_events :]

    def close_incident(self, incident_id: str, resolution: str, recovery_time_seconds: float) -> dict | None:
        timeline = self.incident_timelines.get(incident_id)
        if not timeline:
            return None

        timeline.append({"ts": time.time(), "event": "INCIDENT_RESOLVED", "resolution": resolution})

        start_event = timeline[0]
        detection = next((e for e in timeline if e["event"] in ("ANOMALY_DETECTED", "ALERT_TRIGGERED")), None)
        diagnosis = next((e for e in timeline if e["event"] in ("DIAGNOSIS_COMPLETE", "ROOT_CAUSE_IDENTIFIED")), None)
        mitigation = next((e for e in timeline if e["event"] in ("ACTION_DISPATCHED", "MITIGATION_APPLIED")), None)

        root_cause_chain = self._generate_root_cause_chain(timeline)

        postmortem = {
            "incident_id": incident_id,
            "generated_at": time.time(),
            "title": start_event.get("title", "Untitled Incident"),
            "severity": start_event.get("severity", "P3"),
            "affected_systems": start_event.get("affected", []),
            "timeline": [
                {"ts": e["ts"], "event": e["event"], "description": e.get("description", "")} for e in timeline
            ],
            "detection_latency_s": round((detection["ts"] - start_event["ts"]) if detection else 0, 1),
            "diagnosis_latency_s": round(
                (diagnosis["ts"] - (detection["ts"] if detection else start_event["ts"])) if diagnosis else 0, 1
            ),
            "mitigation_latency_s": round(
                (mitigation["ts"] - (diagnosis["ts"] if diagnosis else start_event["ts"])) if mitigation else 0, 1
            ),
            "total_recovery_time_s": round(recovery_time_seconds, 1),
            "resolution": resolution,
            "root_cause_chain": root_cause_chain,
            "action_items": self._generate_action_items(timeline, root_cause_chain),
        }

        self.generated_postmortems.append(postmortem)
        return postmortem

    def _generate_root_cause_chain(self, timeline: list[dict]) -> list[dict]:
        whys = []
        root_events = [
            e
            for e in timeline
            if "root_cause" in e.get("event", "").lower() or "diagnosis" in e.get("event", "").lower()
        ]
        symptoms = [e for e in timeline if e["event"] in ("ANOMALY_DETECTED", "ALERT_TRIGGERED", "METRIC_SPIKE")]

        cause_chain = symptoms[-1]["description"] if symptoms else "Unknown symptom"
        for i in range(min(self.root_cause_depth, len(root_events) + 1)):
            whys.append(
                {
                    "level": i + 1,
                    "question": f"Why did '{cause_chain}' occur?" if i == 0 else "Why?",
                    "answer": root_events[i]["description"] if i < len(root_events) else "Further investigation needed",
                }
            )
            if i < len(root_events):
                cause_chain = root_events[i]["description"]
        return whys

    def _generate_action_items(self, timeline: list[dict], root_cause_chain: list[dict]) -> list[dict]:
        items = []
        items.append({"priority": "P0", "action": "Add automated detection for this failure pattern", "owner": "FLE"})
        items.append({"priority": "P1", "action": "Add regression test for the root cause condition", "owner": "CI/CD"})

        detection_events = [e for e in timeline if e["event"] == "ANOMALY_DETECTED"]
        if not detection_events:
            items.append(
                {"priority": "P0", "action": "Improve anomaly detection to catch this earlier", "owner": "FLE"}
            )

        items.append({"priority": "P2", "action": "Update runbook with resolution steps", "owner": "owner"})
        return items

    def get_postmortem_summary(self, incident_id: str) -> dict | None:
        for pm in self.generated_postmortems:
            if pm["incident_id"] == incident_id:
                return {
                    "title": pm["title"],
                    "severity": pm["severity"],
                    "recovery_time_s": pm["total_recovery_time_s"],
                    "detection_latency_s": pm["detection_latency_s"],
                    "action_items_count": len(pm["action_items"]),
                }
        return None

    def recurring_pattern_analysis(self) -> list[dict]:
        patterns: dict[str, list[str]] = {}
        for pm in self.generated_postmortems:
            title = pm.get("title", "")
            if title not in patterns:
                patterns[title] = []
            patterns[title].append(pm["incident_id"])

        return [
            {"pattern": title, "occurrence_count": len(ids), "incident_ids": ids, "recurring": len(ids) > 1}
            for title, ids in patterns.items()
            if len(ids) > 1
        ]
