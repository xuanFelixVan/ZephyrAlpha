# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.anomaly.flapping_detector
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-UNK_flapping_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Flapping Detector — v0.40.0 R494

Blindspot: Alerts that oscillate between ACTIVE/CLEAR rapidly — "flapping" —
generate noise without signal. Distinct from alert desensitization (which
measures response rate decay over time). Flapping is about state-change
frequency per unit time.

Risk: R494 — Flapping alerts consume attention budget, mask real anomalies,
and cause human operators to ignore the alert channel entirely.

Mitigation: Track state-change frequency per alert_id. If state toggles N
times within window → classify as flapping → suppress or aggregate into
a single "flapping group" notification.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class AlertState(str, Enum):
    ACTIVE = "ACTIVE"
    CLEAR = "CLEAR"


class FlappingSeverity(str, Enum):
    NONE = "NONE"
    WARNING = "WARNING"
    FLAPPING = "FLAPPING"
    SUPPRESSED = "SUPPRESSED"


@dataclass
class FlappingDetector:
    max_state_changes_per_hour: int = 12
    suppression_duration: float = 900.0
    min_active_duration: float = 30.0

    alert_states: dict[str, list[dict]] = field(default_factory=dict)
    suppressed_alerts: dict[str, float] = field(default_factory=dict)
    flapping_events: list[dict] = field(default_factory=list)

    def record_state_change(self, alert_id: str, new_state: AlertState) -> dict:
        now = time.time()

        if alert_id in self.suppressed_alerts:
            if now < self.suppressed_alerts[alert_id]:
                return {
                    "alert_id": alert_id,
                    "state": new_state.value,
                    "suppressed": True,
                    "remaining_s": round(self.suppressed_alerts[alert_id] - now, 1),
                }
            del self.suppressed_alerts[alert_id]

        if alert_id not in self.alert_states:
            self.alert_states[alert_id] = []

        history = self.alert_states[alert_id]
        history.append({"ts": now, "state": new_state.value})

        window_start = now - 3600
        history = [h for h in history if h["ts"] > window_start]
        self.alert_states[alert_id] = history

        state_changes = sum(1 for i in range(1, len(history)) if history[i]["state"] != history[i - 1]["state"])

        if state_changes > self.max_state_changes_per_hour:
            self.suppressed_alerts[alert_id] = now + self.suppression_duration
            self.flapping_events.append(
                {
                    "ts": now,
                    "alert_id": alert_id,
                    "changes_per_hour": state_changes,
                    "severity": FlappingSeverity.SUPPRESSED.value,
                }
            )
            return {
                "alert_id": alert_id,
                "flapping": True,
                "severity": FlappingSeverity.SUPPRESSED.value,
                "changes_per_hour": state_changes,
                "suppressed_until": round(now + self.suppression_duration, 0),
                "recommendation": "aggregate_into_flapping_group",
            }

        severity = (
            FlappingSeverity.FLAPPING
            if state_changes > self.max_state_changes_per_hour / 2
            else FlappingSeverity.WARNING
            if state_changes > 3
            else FlappingSeverity.NONE
        )

        return {
            "alert_id": alert_id,
            "flapping": severity is not FlappingSeverity.NONE,
            "severity": severity.value,
            "changes_per_hour": state_changes,
        }

    def is_suppressed(self, alert_id: str) -> bool:
        if alert_id in self.suppressed_alerts:
            if time.time() < self.suppressed_alerts[alert_id]:
                return True
            del self.suppressed_alerts[alert_id]
        return False

    def get_flapping_stats(self) -> dict:
        return {
            "suppressed_count": len(self.suppressed_alerts),
            "total_flapping_events": len(self.flapping_events),
            "recent_flapping": [e for e in self.flapping_events if time.time() - e["ts"] < 3600],
        }

    def overall_alert_stability(self) -> float:
        total = len(self.alert_states)
        if total == 0:
            return 1.0
        flapping = sum(
            1
            for aid, hist in self.alert_states.items()
            if len(hist) >= 2
            and sum(1 for i in range(1, len(hist)) if hist[i]["state"] != hist[i - 1]["state"])
            > self.max_state_changes_per_hour
        )
        return round(max(0.0, 1.0 - flapping / total), 3)
