# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.anomaly.heisenbug_detector
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
# [A_module] module_id=MOD-UNK_heisenbug_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Heisenbug Detector — v0.38.0 R470

Blindspot: Bugs that change behavior or disappear when observed; observation act
alters system state (timing, logging overhead, debugger attachment).

Risk: R470 — AI debugging creates false confidence: "I fixed it" when bug merely
hid from the diagnostic instrumentation.

Mitigation: Shadow monitoring with randomized sampling. Track observation-sensitive
metrics via passive collection (no active probing). Compare anomaly rates between
actively-monitored and passively-monitored windows. If anomaly rate drops >50% during
active monitoring -> flag as potential Heisenbug.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class ObservationMode(str, Enum):
    PASSIVE = "PASSIVE"
    ACTIVE = "ACTIVE"


@dataclass
class HeisenbugDetector:
    passive_anomaly_rate: float = 0.0
    active_anomaly_rate: float = 0.0
    passive_samples: int = 0
    active_samples: int = 0
    heisenbug_threshold: float = 0.5
    observation_timeline: list[dict] = field(default_factory=list)

    def record(self, anomaly_detected: bool, mode: ObservationMode) -> dict:
        entry = {"ts": time.time(), "mode": mode.value, "anomaly": anomaly_detected}
        self.observation_timeline.append(entry)
        if len(self.observation_timeline) > 1000:
            self.observation_timeline = self.observation_timeline[-1000:]

        if mode is ObservationMode.PASSIVE:
            self.passive_samples += 1
            if anomaly_detected:
                self.passive_anomaly_rate = (
                    self.passive_anomaly_rate * (self.passive_samples - 1) / self.passive_samples
                    + 1.0 / self.passive_samples
                )
        else:
            self.active_samples += 1
            if anomaly_detected:
                self.active_anomaly_rate = (
                    self.active_anomaly_rate * (self.active_samples - 1) / self.active_samples
                    + 1.0 / self.active_samples
                )

        return entry

    def detect_heisenbug(self) -> dict:
        if self.passive_samples < 10:
            return {"heisenbug_detected": False, "confidence": 0.0, "reason": "insufficient passive samples"}

        if self.passive_anomaly_rate == 0:
            return {"heisenbug_detected": False, "confidence": 0.0, "reason": "no passive anomalies"}

        ratio = self.active_anomaly_rate / max(self.passive_anomaly_rate, 0.001)
        heisenbug = ratio < self.heisenbug_threshold
        confidence = 1.0 - ratio if ratio < 1.0 else 0.0

        return {
            "heisenbug_detected": heisenbug,
            "confidence": min(confidence, 0.95),
            "passive_rate": round(self.passive_anomaly_rate, 4),
            "active_rate": round(self.active_anomaly_rate, 4),
            "rate_ratio": round(ratio, 3),
            "recommendation": "shadow_replay_without_instrumentation" if heisenbug else "continue_monitoring",
        }

    def reset_observation_window(self) -> None:
        self.passive_anomaly_rate = 0.0
        self.active_anomaly_rate = 0.0
        self.passive_samples = 0
        self.active_samples = 0
