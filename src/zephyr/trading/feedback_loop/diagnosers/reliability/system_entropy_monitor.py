# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.reliability.system_entropy_monitor
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
# [A_module] module_id=MOD-UNK_system_entropy_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R527: SystemEntropyMonitor
FLE内部熵增趋势 — 配置/行为混乱度单调递增->即将混沌
"""

import hashlib
import json
import time
from dataclasses import dataclass, field


@dataclass
class EntropySnapshot:
    timestamp: float
    config_entropy: float
    behavior_entropy: float
    total_entropy: float
    state_hash: str


@dataclass
class SystemEntropyMonitor:
    snapshots: list[EntropySnapshot] = field(default_factory=list)
    max_snapshots: int = 50
    entropy_warning_threshold: float = 0.6
    entropy_critical_threshold: float = 0.8
    trend_window: int = 10

    def compute_and_record(self, config: dict, behavior_patterns: list[str]) -> dict:
        config_entropy = self._compute_config_entropy(config)
        behavior_entropy = self._compute_behavior_entropy(behavior_patterns)
        total = (config_entropy + behavior_entropy) / 2.0

        state_hash = hashlib.sha256(
            json.dumps({"config": config, "behaviors": behavior_patterns}, sort_keys=True).encode()
        ).hexdigest()[:12]

        self.snapshots.append(
            EntropySnapshot(
                timestamp=time.time(),
                config_entropy=config_entropy,
                behavior_entropy=behavior_entropy,
                total_entropy=total,
                state_hash=state_hash,
            )
        )
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots = self.snapshots[-self.max_snapshots :]

        return {
            "config_entropy": round(config_entropy, 3),
            "behavior_entropy": round(behavior_entropy, 3),
            "total_entropy": round(total, 3),
        }

    def analyze_trend(self) -> dict:
        if len(self.snapshots) < self.trend_window:
            return {"status": "insufficient_data", "entropy": 0}

        recent = self.snapshots[-self.trend_window :]
        avg_entropy = sum(s.total_entropy for s in recent) / len(recent)

        if len(recent) >= 5:
            half_ago = recent[: len(recent) // 2]
            half_now = recent[len(recent) // 2 :]
            avg_ago = sum(s.total_entropy for s in half_ago) / len(half_ago)
            avg_now = sum(s.total_entropy for s in half_now) / len(half_now)
            trend = "increasing" if avg_now > avg_ago + 0.05 else "decreasing" if avg_now < avg_ago - 0.05 else "stable"
        else:
            trend = "undetermined"

        status = "healthy"
        if avg_entropy > self.entropy_critical_threshold:
            status = "critical_chaos"
        elif avg_entropy > self.entropy_warning_threshold:
            status = "warning_entropy"

        is_unbounded_increase = trend == "increasing" and avg_entropy > 0.4

        return {
            "status": status,
            "avg_entropy": round(avg_entropy, 3),
            "trend": trend,
            "is_unbounded_increase": is_unbounded_increase,
            "recommendation": "MANUAL_INTERVENTION" if is_unbounded_increase else "MONITOR",
            "snapshot_count": len(self.snapshots),
        }

    @staticmethod
    def _compute_config_entropy(config: dict) -> float:
        if not config:
            return 0.0
        values = []
        for v in config.values():
            if isinstance(v, (int, float)):
                values.append(float(v))
        if len(values) < 2:
            return 0.0

        total = sum(abs(v) for v in values)
        if total < 1e-10:
            return 0.0
        probs = [abs(v) / total for v in values]
        import math

        entropy = -sum(p * math.log2(p + 1e-10) for p in probs)
        return min(entropy / math.log2(len(values) + 1e-10), 1.0)

    @staticmethod
    def _compute_behavior_entropy(patterns: list[str]) -> float:
        if not patterns:
            return 0.0
        unique = set(patterns)
        return len(unique) / max(len(patterns), 1)
