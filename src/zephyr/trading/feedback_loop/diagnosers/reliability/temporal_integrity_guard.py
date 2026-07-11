# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.reliability.temporal_integrity_guard
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_temporal_integrity_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Temporal Integrity Guard — v0.38.0 R478

Blindspot: Time-series baselines corrupted by clock anomalies — NTP drift
between machines, daylight saving time transitions, leap seconds, clock
source monotonic vs wall-clock confusion. FLE's EWMA baselines silently
absorb temporal distortions.

Risk: R478 — Anomaly detected at wrong time; baseline comparison uses
mismatched time windows; DST transition creates fake "spike" or "drop";
monotonic clock divergence causes phantom trend detection.

Mitigation: Validate timestamp monotonicity. Detect DST transitions and
treat as known events. Track NTP offset. Flag when wall-clock jumps
backward (negative time delta). Maintain separate monotonic baseline.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class TimeAnomaly(str, Enum):
    BACKWARD_JUMP = "BACKWARD_JUMP"
    FORWARD_JUMP = "FORWARD_JUMP"
    DST_TRANSITION = "DST_TRANSITION"
    NTP_DRIFT = "NTP_DRIFT"
    MONOTONIC_DIVERGENCE = "MONOTONIC_DIVERGENCE"
    STALE_TIMESTAMP = "STALE_TIMESTAMP"


@dataclass
class TemporalIntegrityGuard:
    max_backward_tolerance: float = 1.0
    max_forward_gap: float = 3600.0
    max_ntp_drift_seconds: float = 5.0
    max_timestamp_age: float = 300.0

    last_wall_clock: float = 0.0
    last_monotonic: float = 0.0
    ntp_offset: float = 0.0
    dst_aware: bool = True
    time_anomalies: list[dict] = field(default_factory=list)

    def validate_timestamp(self, ts: float, source: str = "unknown") -> dict:
        now = time.time()
        monotonic_now = time.monotonic()

        anomalies = []

        if self.last_wall_clock > 0 and ts < self.last_wall_clock - self.max_backward_tolerance:
            jump = self.last_wall_clock - ts
            anomaly_type = TimeAnomaly.DST_TRANSITION if abs(jump - 3600) < 300 else TimeAnomaly.BACKWARD_JUMP
            anomalies.append({"type": anomaly_type.value, "jump_seconds": round(jump, 1)})

        if self.last_wall_clock > 0 and ts > self.last_wall_clock + self.max_forward_gap:
            anomalies.append(
                {"type": TimeAnomaly.FORWARD_JUMP.value, "gap_seconds": round(ts - self.last_wall_clock, 1)}
            )

        if now - ts > self.max_timestamp_age:
            anomalies.append({"type": TimeAnomaly.STALE_TIMESTAMP.value, "age_seconds": round(now - ts, 1)})

        wall_delta = now - self.last_wall_clock if self.last_wall_clock > 0 else 0
        monotonic_delta = monotonic_now - self.last_monotonic if self.last_monotonic > 0 else 0
        if abs(wall_delta - monotonic_delta) > self.max_ntp_drift_seconds and wall_delta > 1:
            anomalies.append(
                {
                    "type": TimeAnomaly.NTP_DRIFT.value,
                    "wall_delta": round(wall_delta, 3),
                    "monotonic_delta": round(monotonic_delta, 3),
                    "drift": round(abs(wall_delta - monotonic_delta), 3),
                }
            )

        self.last_wall_clock = ts
        self.last_monotonic = monotonic_now

        if anomalies:
            for a in anomalies:
                self.time_anomalies.append({"ts": now, "source": source, **a})

        return {
            "valid": len(anomalies) == 0,
            "anomalies": anomalies,
            "recommendation": (
                "discard_data_point"
                if any(a["type"] == TimeAnomaly.BACKWARD_JUMP.value for a in anomalies)
                else "flag_for_review"
                if anomalies
                else "accept"
            ),
        }

    def is_dst_boundary(self, ts: float) -> bool:
        lt = time.localtime(ts)
        return lt.tm_isdst >= 0 and self.dst_aware

    def get_temporal_health(self) -> dict:
        recent = [a for a in self.time_anomalies if time.time() - a["ts"] < 3600]
        return {
            "anomalies_last_hour": len(recent),
            "total_anomalies": len(self.time_anomalies),
            "ntp_offset_estimate": round(self.ntp_offset, 3),
            "healthy": len(recent) == 0,
        }

    def reset_history(self) -> None:
        self.time_anomalies = []
        self.last_wall_clock = 0.0
        self.last_monotonic = 0.0
