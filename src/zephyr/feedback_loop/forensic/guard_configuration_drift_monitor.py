# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.forensic.guard_configuration_drift_monitor
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-UNK_guard_configuration_drift_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R521: GuardConfigurationDriftMonitor
集体守卫参数vs黄金基线漂移 — 定期快照，漂移>阈值告警
"""

import hashlib
import json
import time
from dataclasses import dataclass, field


@dataclass
class GuardConfigSnapshot:
    timestamp: float
    config: dict[str, float]
    hash: str
    drift_from_golden: float = 0.0


@dataclass
class GuardConfigurationDriftMonitor:
    golden_baseline: dict[str, float] = field(default_factory=dict)
    golden_hash: str = ""
    snapshots: list[GuardConfigSnapshot] = field(default_factory=list)
    max_snapshots: int = 50
    drift_threshold: float = 0.15

    def establish_golden_baseline(self, config: dict[str, float]) -> str:
        self.golden_baseline = dict(config)
        self.golden_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16]
        return self.golden_hash

    def take_snapshot(self, current_config: dict[str, float]) -> dict:
        h = hashlib.sha256(json.dumps(current_config, sort_keys=True).encode()).hexdigest()[:16]

        drift = self._compute_drift(self.golden_baseline, current_config)

        snapshot = GuardConfigSnapshot(
            timestamp=time.time(),
            config=dict(current_config),
            hash=h,
            drift_from_golden=drift,
        )
        self.snapshots.append(snapshot)
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots = self.snapshots[-self.max_snapshots :]

        severity = "stable"
        if drift > 0.3:
            severity = "critical_drift"
        elif drift > self.drift_threshold:
            severity = "moderate_drift"

        return {
            "hash": h,
            "golden_hash": self.golden_hash,
            "drift": round(drift, 4),
            "severity": severity,
            "config_changed": h != self.golden_hash,
            "total_params": len(current_config),
        }

    def _compute_drift(self, baseline: dict[str, float], current: dict[str, float]) -> float:
        all_keys = set(baseline.keys()) | set(current.keys())
        if not all_keys:
            return 0.0

        diffs = []
        for key in all_keys:
            base = baseline.get(key, 0.0)
            curr = current.get(key, 0.0)
            max_val = max(abs(base), abs(curr), 1e-10)
            diffs.append(abs(curr - base) / max_val)

        return sum(diffs) / len(diffs)

    def get_drift_trend(self) -> dict:
        if len(self.snapshots) < 3:
            return {"trend": "insufficient_data"}

        recent = self.snapshots[-5:]
        drift_values = [s.drift_from_golden for s in recent]

        increasing = all(drift_values[i] >= drift_values[i - 1] - 0.001 for i in range(1, len(drift_values)))
        avg = sum(drift_values) / len(drift_values)

        return {
            "trend": "monotonically_increasing" if increasing else "fluctuating",
            "avg_drift": round(avg, 4),
            "recommendation": "REBASELINE" if avg > self.drift_threshold else "MONITOR",
        }
