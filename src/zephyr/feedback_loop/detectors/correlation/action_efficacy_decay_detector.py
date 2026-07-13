# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.correlation.action_efficacy_decay_detector
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-UNK_action_efficacy_decay_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R507: ActionEfficacyDecayDetector
单动作有效性EWMA衰减检测 — 斜率持续为负 = 动作变质
对标: Nonstationary RL — Environments change, actions that used to work may stop working
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ActionEfficacyRecord:
    action_type: str
    outcomes: list[float] = field(default_factory=list)
    max_outcomes: int = 50


@dataclass
class ActionEfficacyDecayDetector:
    records: dict[str, ActionEfficacyRecord] = field(default_factory=dict)
    decay_threshold: float = -0.02
    min_samples: int = 10

    def record_outcome(self, action_type: str, success: bool) -> None:
        if action_type not in self.records:
            self.records[action_type] = ActionEfficacyRecord(action_type=action_type)
        rec = self.records[action_type]
        rec.outcomes.append(1.0 if success else 0.0)
        if len(rec.outcomes) > rec.max_outcomes:
            rec.outcomes = rec.outcomes[-rec.max_outcomes :]

    def detect_decay(self) -> dict:
        findings = {}
        for action_type, rec in self.records.items():
            if len(rec.outcomes) < self.min_samples:
                continue

            ewma = self._compute_ewma(rec.outcomes, alpha=0.3)
            slope = self._compute_slope(ewma[-10:]) if len(ewma) >= 10 else 0.0
            current = ewma[-1] if ewma else 1.0

            findings[action_type] = {
                "ewma_current": round(current, 3),
                "slope": round(slope, 4),
                "is_decaying": slope < self.decay_threshold,
                "sample_count": len(rec.outcomes),
            }
        return findings

    def get_decaying_actions(self) -> list[str]:
        findings = self.detect_decay()
        return [k for k, v in findings.items() if v["is_decaying"]]

    @staticmethod
    def _compute_ewma(values: list[float], alpha: float = 0.3) -> list[float]:
        if not values:
            return []
        result = [values[0]]
        for v in values[1:]:
            result.append(alpha * v + (1 - alpha) * result[-1])
        return result

    @staticmethod
    def _compute_slope(values: list[float]) -> float:
        if len(values) < 2:
            return 0.0
        n = len(values)
        x_mean = (n - 1) / 2.0
        y_mean = sum(values) / n
        num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        den = sum((i - x_mean) ** 2 for i in range(n))
        return num / den if den != 0 else 0.0
