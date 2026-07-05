# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.correlation.agent_trajectory_anomaly_detector
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
# [A_module] module_id=MOD-UNK_agent_trajectory_anomaly_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R503: AgentTrajectoryAnomalyDetector
FLE自身执行轨迹静默故障检测 — drift / cycle / miss
对标: IBM Silent Failures in Multi-Agent Trajectories (arXiv 2511.04032, 2025)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TrajectoryAnomalyType(str, Enum):
    DRIFT = "drift"
    CYCLE = "cycle"
    MISSING_STEP = "missing_step"


@dataclass
class TrajectoryEvent:
    phase: str
    component: str
    timestamp: float
    input_hash: str
    output_hash: str


@dataclass
class AgentTrajectoryAnomalyDetector:
    expected_phases: tuple[str, ...] = ("collect", "detect", "diagnose", "act", "verify")
    trajectory_history: list[TrajectoryEvent] = field(default_factory=list)
    max_history: int = 200
    cycle_threshold: int = 3
    drift_threshold: float = 0.4

    def record_step(self, event: TrajectoryEvent) -> None:
        self.trajectory_history.append(event)
        if len(self.trajectory_history) > self.max_history:
            self.trajectory_history = self.trajectory_history[-self.max_history :]

    def detect_trajectory_anomalies(self) -> dict:
        if len(self.trajectory_history) < 4:
            return {"status": "insufficient_data", "anomalies": []}

        anomalies = []
        anomalies.extend(self._detect_drift())
        anomalies.extend(self._detect_cycles())
        anomalies.extend(self._detect_missing_steps())

        return {
            "status": "anomalous" if anomalies else "normal",
            "anomalies": anomalies,
            "trajectory_depth": len(self.trajectory_history),
        }

    def _detect_drift(self) -> list[dict]:
        recent = self.trajectory_history[-10:]
        if len(recent) < 5:
            return []

        phase_sequence = [e.phase for e in recent]
        expected_idx = [self.expected_phases.index(p) for p in phase_sequence if p in self.expected_phases]
        if len(expected_idx) < 3:
            return []

        diffs = [expected_idx[i + 1] - expected_idx[i] for i in range(len(expected_idx) - 1)]
        forward_ratio = sum(1 for d in diffs if d >= 0) / len(diffs)

        if forward_ratio < self.drift_threshold:
            return [{"type": TrajectoryAnomalyType.DRIFT.value, "forward_ratio": round(forward_ratio, 3)}]
        return []

    def _detect_cycles(self) -> list[dict]:
        recent_components = [e.component for e in self.trajectory_history[-20:]]
        seen = {}
        for i, comp in enumerate(recent_components):
            if comp in seen:
                distance = i - seen[comp]
                if distance > 1:
                    cycle_members = recent_components[seen[comp] : i + 1]
                    if len(set(cycle_members)) <= self.cycle_threshold:
                        return [
                            {
                                "type": TrajectoryAnomalyType.CYCLE.value,
                                "components": list(set(cycle_members)),
                                "span": distance,
                            }
                        ]
            seen[comp] = i
        return []

    def _detect_missing_steps(self) -> list[dict]:
        phases_seen = {e.phase for e in self.trajectory_history[-30:]}
        missing = [p for p in self.expected_phases if p not in phases_seen]
        if missing:
            return [{"type": TrajectoryAnomalyType.MISSING_STEP.value, "missing_phases": missing}]
        return []
