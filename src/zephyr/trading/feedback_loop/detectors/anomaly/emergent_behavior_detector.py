# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.anomaly.emergent_behavior_detector
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
# [A_module] module_id=MOD-UNK_emergent_behavior_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Emergent Behavior Detector — v0.38.0 R473

Blindspot: Multi-agent systems produce emergent behaviors — patterns that arise
from agent interactions but cannot be predicted from individual agent rules.
Phase transitions, self-organized criticality, and hysteresis effects that
traditional monitoring misses.

Risk: R473 — System silently drifts toward critical failure edge; FLE only
detects the final crash, not the gradual emergence of instability.

Mitigation: Monitor system-level entropy, coupling strength, and correlation
dimension. Detect when inter-component correlation spikes above baseline
(early signal of cascading failure). Track hysteresis — system not returning
to baseline after stress removed.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class EmergenceState(str, Enum):
    STABLE = "STABLE"
    CORRELATING = "CORRELATING"
    CRITICAL = "CRITICAL"
    HYSTERETIC = "HYSTERETIC"


@dataclass
class EmergentBehaviorDetector:
    correlation_threshold: float = 0.70
    entropy_drop_threshold: float = 0.30
    hysteresis_threshold: float = 0.15
    window_size: int = 50

    metric_history: dict[str, list[float]] = field(default_factory=dict)
    correlation_baseline: dict[str, float] = field(default_factory=dict)
    pre_stress_baseline: dict[str, float] | None = None
    state: EmergenceState = EmergenceState.STABLE
    emergence_events: list[dict] = field(default_factory=list)

    def record_metrics(self, metrics: dict[str, float]) -> None:
        for name, value in metrics.items():
            if name not in self.metric_history:
                self.metric_history[name] = []
            self.metric_history[name].append(value)
            if len(self.metric_history[name]) > self.window_size:
                self.metric_history[name] = self.metric_history[name][-self.window_size :]

    def compute_pairwise_correlations(self) -> dict[str, float]:
        names = list(self.metric_history.keys())
        correlations = {}
        for i, a in enumerate(names):
            for b in names[i + 1 :]:
                series_a = self.metric_history[a]
                series_b = self.metric_history[b]
                n = min(len(series_a), len(series_b))
                if n < 5:
                    continue
                mean_a = sum(series_a[-n:]) / n
                mean_b = sum(series_b[-n:]) / n
                cov = sum((series_a[-n:][j] - mean_a) * (series_b[-n:][j] - mean_b) for j in range(n)) / n
                std_a = (sum((x - mean_a) ** 2 for x in series_a[-n:]) / n) ** 0.5
                std_b = (sum((x - mean_b) ** 2 for x in series_b[-n:]) / n) ** 0.5
                if std_a > 0 and std_b > 0:
                    correlations[f"{a}+{b}"] = cov / (std_a * std_b)
        return correlations

    def detect_emergence(self) -> dict:
        correlations = self.compute_pairwise_correlations()
        high_corr = {k: v for k, v in correlations.items() if abs(v) > self.correlation_threshold}

        prev_state = self.state
        if len(high_corr) >= 3:
            self.state = EmergenceState.CRITICAL
        elif len(high_corr) >= 1:
            self.state = EmergenceState.CORRELATING
        elif self.pre_stress_baseline is not None:
            self.state = EmergenceState.HYSTERETIC
        else:
            self.state = EmergenceState.STABLE

        if self.state != prev_state and self.state is not EmergenceState.STABLE:
            self.emergence_events.append(
                {
                    "ts": time.time(),
                    "from_state": prev_state.value,
                    "to_state": self.state.value,
                    "high_correlations": list(high_corr.keys()),
                }
            )

        return {
            "state": self.state.value,
            "high_correlation_pairs": len(high_corr),
            "correlation_details": {k: round(v, 3) for k, v in high_corr.items()},
            "recommendation": (
                "investigate_coupling"
                if self.state is EmergenceState.CRITICAL
                else "increase_observation_frequency"
                if self.state is EmergenceState.CORRELATING
                else "continue_monitoring"
            ),
        }

    def set_pre_stress_baseline(self, metrics: dict[str, float]) -> None:
        self.pre_stress_baseline = dict(metrics)
