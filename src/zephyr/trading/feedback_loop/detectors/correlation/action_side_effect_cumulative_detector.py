# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.correlation.action_side_effect_cumulative_detector
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
# [A_module] module_id=MOD-UNK_action_side_effect_cumulative_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R526: ActionSideEffectCumulativeDetector
动作微副作用累积漂移检测 — 多次循环后微小副作用累积
"""

from dataclasses import dataclass, field


@dataclass
class ActionSideEffectCumulativeDetector:
    baseline_metrics: dict[str, float] = field(default_factory=dict)
    cumulative_effects: dict[str, list[float]] = field(default_factory=dict)
    max_effects_per_metric: int = 200
    drift_threshold: float = 0.15

    def set_baseline(self, metrics: dict[str, float]) -> None:
        self.baseline_metrics = dict(metrics)

    def record_side_effect(self, metric_name: str, delta: float) -> None:
        if metric_name not in self.cumulative_effects:
            self.cumulative_effects[metric_name] = []
        self.cumulative_effects[metric_name].append(delta)
        if len(self.cumulative_effects[metric_name]) > self.max_effects_per_metric:
            self.cumulative_effects[metric_name] = self.cumulative_effects[metric_name][-self.max_effects_per_metric :]

    def detect_cumulative_drift(self) -> dict:
        findings = {}
        for metric, effects in self.cumulative_effects.items():
            cumulative = sum(effects)
            baseline = self.baseline_metrics.get(metric, 0.0)

            if abs(baseline) < 1e-10:
                findings[metric] = {
                    "cumulative_delta": round(cumulative, 4),
                    "is_significant": abs(cumulative) > 0.1,
                }
                continue

            drift_ratio = abs(cumulative / baseline)
            findings[metric] = {
                "baseline": round(baseline, 4),
                "cumulative_delta": round(cumulative, 4),
                "drift_ratio": round(drift_ratio, 4),
                "is_drifted": drift_ratio > self.drift_threshold,
                "direction": "increase" if cumulative > 0 else "decrease",
                "effect_count": len(effects),
            }

        drifted = {k: v for k, v in findings.items() if v.get("is_drifted")}
        return {
            "drifted_metrics": list(drifted.keys()),
            "findings": findings,
            "cumulative_drift_detected": len(drifted) > 0,
        }

    def get_total_cumulative_effects(self) -> dict[str, float]:
        return {metric: sum(effects) for metric, effects in self.cumulative_effects.items()}
