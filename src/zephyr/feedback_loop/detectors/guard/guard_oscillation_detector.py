# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.guard.guard_oscillation_detector
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-UNK_guard_oscillation_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R519: GuardOscillationDetector
守卫状态振荡频率/振幅分析 — Guard A<->B 反复切换
对标: Control Theory — detect limit cycles in guard state transitions
"""

import time
from dataclasses import dataclass, field


@dataclass
class GuardStateChange:
    guard_id: str
    from_state: str
    to_state: str
    timestamp: float


@dataclass
class GuardOscillationDetector:
    state_changes: list[GuardStateChange] = field(default_factory=list)
    max_changes: int = 200
    oscillation_threshold: float = 6.0
    analysis_window: float = 3600.0

    def record_state_change(self, guard_id: str, from_state: str, to_state: str) -> None:
        self.state_changes.append(
            GuardStateChange(
                guard_id=guard_id,
                from_state=from_state,
                to_state=to_state,
                timestamp=time.time(),
            )
        )
        if len(self.state_changes) > self.max_changes:
            self.state_changes = self.state_changes[-self.max_changes :]

    def detect_oscillations(self) -> dict:
        now = time.time()
        cutoff = now - self.analysis_window
        recent = [c for c in self.state_changes if c.timestamp >= cutoff]

        guard_pairs = {}
        for c in recent:
            pair_key = (c.guard_id, c.from_state, c.to_state)
            if pair_key not in guard_pairs:
                guard_pairs[pair_key] = 0
            guard_pairs[pair_key] += 1

        oscillations = {}
        for (guard_id, from_state, to_state), count in guard_pairs.items():
            inverse_key = (guard_id, to_state, from_state)
            inverse_count = guard_pairs.get(inverse_key, 0)
            total_swings = min(count, inverse_count)

            if total_swings >= self.oscillation_threshold:
                oscillations[guard_id] = {
                    "total_swings": total_swings,
                    "pattern": f"{from_state} <-> {to_state}",
                    "frequency_per_hour": round(total_swings / (self.analysis_window / 3600.0), 1),
                    "severity": "critical" if total_swings >= 20 else "high" if total_swings >= 12 else "medium",
                }

        return {
            "oscillating_guards": list(oscillations.keys()),
            "details": oscillations,
            "total_guards_monitored": len(set(c.guard_id for c in recent)),
        }
