# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.reliability.human_anomaly_flood_detector
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
# [A_module] module_id=MOD-UNK_human_anomaly_flood_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Human Anomaly Flood Detector — v0.40.0 R500

Blindspot: FLE may correctly detect 50 anomalies, but surfacing all 50 to a
single human owner creates cognitive overload. The human stops responding not
because of alert desensitization (system-level) but because of anomaly flood
(human-level throughput limit).

Risk: R500 — Human owner overwhelmed by anomaly volume -> misses the one
critical P0 among 49 P3s -> system failure from human attention bottleneck.

Mitigation: Track anomalies-per-human-per-hour. If rate exceeds human processing
capacity -> auto-triage: auto-resolve P3/P4, aggregate P2 into digest, only
surface P0/P1 individually. Alert when human is at risk of "flood dropout."
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class FloodLevel(str, Enum):
    NORMAL = "NORMAL"
    ELEVATED = "ELEVATED"
    FLOOD = "FLOOD"
    DROWNING = "DROWNING"


@dataclass
class HumanAnomalyFloodDetector:
    max_anomalies_per_human_per_hour: int = 10
    auto_triage_threshold: int = 20
    flood_suppression_duration: float = 1800.0

    human_exposure: dict[str, list[dict]] = field(default_factory=dict)
    flood_events: list[dict] = field(default_factory=list)
    auto_triage_active: bool = False

    def record_anomaly_exposure(self, human_id: str, anomaly_id: str, severity: str, dismissed: bool = False) -> dict:
        now = time.time()

        if human_id not in self.human_exposure:
            self.human_exposure[human_id] = []

        exposure = self.human_exposure[human_id]
        exposure.append(
            {
                "ts": now,
                "anomaly_id": anomaly_id,
                "severity": severity,
                "dismissed": dismissed,
            }
        )

        window_start = now - 3600
        exposure = [e for e in exposure if e["ts"] > window_start]
        self.human_exposure[human_id] = exposure

        hourly_rate = len(exposure)
        dismissed_count = sum(1 for e in exposure if e.get("dismissed"))

        if hourly_rate > self.auto_triage_threshold:
            level = FloodLevel.DROWNING
            self.auto_triage_active = True
        elif hourly_rate > self.max_anomalies_per_human_per_hour:
            level = FloodLevel.FLOOD
            self.auto_triage_active = True
        elif hourly_rate > self.max_anomalies_per_human_per_hour / 2:
            level = FloodLevel.ELEVATED
        else:
            level = FloodLevel.NORMAL

        if level in (FloodLevel.FLOOD, FloodLevel.DROWNING):
            self.flood_events.append(
                {
                    "ts": now,
                    "human_id": human_id,
                    "level": level.value,
                    "hourly_rate": hourly_rate,
                    "dismissed_pct": round(100.0 * dismissed_count / max(hourly_rate, 1), 1),
                }
            )

        critical_among_flood = sum(1 for e in exposure if e.get("severity", "").startswith("P0"))

        return {
            "human_id": human_id,
            "flood_level": level.value,
            "anomalies_per_hour": hourly_rate,
            "dismissed_count": dismissed_count,
            "critical_buried": critical_among_flood > 0 and level is not FloodLevel.NORMAL,
            "auto_triage_active": self.auto_triage_active,
            "recommendation": (
                "auto_triage_p3_p4_immediately"
                if level is FloodLevel.DROWNING
                else "aggregate_p2_into_digest"
                if level is FloodLevel.FLOOD
                else "reduce_surface_frequency"
                if level is FloodLevel.ELEVATED
                else "continue"
            ),
        }

    def get_auto_triage_plan(self, human_id: str) -> dict:
        exposure = self.human_exposure.get(human_id, [])
        if not exposure:
            return {"triage_needed": False}

        by_severity: dict[str, int] = {}
        for e in exposure:
            sev = e.get("severity", "UNKNOWN")
            by_severity[sev] = by_severity.get(sev, 0) + 1

        plan = {
            "surface_directly": [],
            "aggregate_into_digest": [],
            "auto_resolve": [],
        }

        for sev, count in by_severity.items():
            if sev.startswith("P0") or sev.startswith("P1"):
                plan["surface_directly"].append({"severity": sev, "count": count})
            elif sev.startswith("P2"):
                plan["aggregate_into_digest"].append({"severity": sev, "count": count})
            else:
                plan["auto_resolve"].append({"severity": sev, "count": count})

        return {
            "triage_needed": self.auto_triage_active,
            "plan": plan,
            "total_anomalies": len(exposure),
            "human_id": human_id,
        }

    def get_all_human_status(self) -> dict:
        result = {}
        for human_id in list(self.human_exposure.keys()):
            recent = [e for e in self.human_exposure[human_id] if time.time() - e["ts"] < 3600]
            dismissed = sum(1 for e in recent if e.get("dismissed"))
            result[human_id] = {
                "hourly_rate": len(recent),
                "dismissed_pct": round(100.0 * dismissed / max(len(recent), 1), 1) if recent else 0,
                "flooded": len(recent) > self.max_anomalies_per_human_per_hour,
            }
        return result

    def overall_human_attention_health(self) -> float:
        flooded = sum(
            1
            for hid, exp in self.human_exposure.items()
            if len([e for e in exp if time.time() - e["ts"] < 3600]) > self.max_anomalies_per_human_per_hour
        )
        total = len(self.human_exposure)
        if total == 0:
            return 1.0
        return round(max(0.0, 1.0 - flooded / total), 3)

    def reset_auto_triage(self) -> None:
        self.auto_triage_active = False
