# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.forensic.point_in_time_reconstructor
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
# [A_module] module_id=MOD-UNK_point_in_time_reconstructor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Point-in-Time Reconstructor — v0.37.0 R465

Blindspot: After an incident, no ability to reconstruct exact system state
at any historical timestamp for forensic root-cause analysis.

Risk: R465 — Incident postmortem relies on incomplete state reconstruction.

Mitigation: Event-sourced state reconstruction. Log all state transitions
with vector clocks. Replay from last known-good snapshot + apply events
up to target timestamp to reconstruct any point in time.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class PointInTimeReconstructor:
    snapshot_interval: float = 3600.0

    snapshots: list[dict] = field(default_factory=list)
    events: list[dict] = field(default_factory=list)
    vector_clock: dict[str, int] = field(default_factory=dict)
    last_snapshot_at: float = 0.0

    def take_snapshot(self, state: dict) -> None:
        now = time.time()
        self.snapshots.append(
            {
                "ts": now,
                "state": state.copy(),
                "vector_clock": dict(self.vector_clock),
            }
        )
        self.last_snapshot_at = now
        if len(self.snapshots) > 24:
            self.snapshots = self.snapshots[-24:]

    def record_event(self, component: str, event_type: str, payload: dict) -> None:
        self.vector_clock[component] = self.vector_clock.get(component, 0) + 1
        self.events.append(
            {
                "ts": time.time(),
                "component": component,
                "type": event_type,
                "payload": payload,
                "vc": dict(self.vector_clock),
            }
        )
        if len(self.events) > 10000:
            self.events = self.events[-10000:]

    def reconstruct(self, target_ts: float) -> dict | None:
        snapshot = None
        for s in reversed(self.snapshots):
            if s["ts"] <= target_ts:
                snapshot = s
                break

        if not snapshot:
            return None

        reconstructed = snapshot["state"].copy()
        for event in self.events:
            if snapshot["ts"] < event["ts"] <= target_ts:
                reconstructed[f"event_{event['component']}_{event['type']}"] = event["payload"]

        reconstructed["_reconstructed_at_ts"] = target_ts
        return reconstructed

    def get_event_count_between(self, start_ts: float, end_ts: float) -> int:
        return sum(1 for e in self.events if start_ts < e["ts"] <= end_ts)
