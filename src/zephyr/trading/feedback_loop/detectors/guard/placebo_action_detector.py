# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.guard.placebo_action_detector
# [DOMAIN] D_FEEDBACK_LOOP
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
# [A_module] module_id=MOD-UNK_placebo_action_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R508: PlaceboActionDetector
伪有效动作统计检验 — Mann-Whitney U test 区分因果 vs 随机
对标: Causal Inference (Pearl) — distinguish real effect from regression to mean
"""

import math
from dataclasses import dataclass, field


@dataclass
class PlaceboActionDetector:
    action_outcomes: dict[str, list[float]] = field(default_factory=dict)
    control_outcomes: list[float] = field(default_factory=list)
    min_samples_per_group: int = 8
    significance_level: float = 0.05

    def record_action_outcome(self, action_type: str, outcome: float) -> None:
        if action_type not in self.action_outcomes:
            self.action_outcomes[action_type] = []
        self.action_outcomes[action_type].append(outcome)
        if len(self.action_outcomes[action_type]) > 100:
            self.action_outcomes[action_type] = self.action_outcomes[action_type][-100:]

    def record_control_outcome(self, outcome: float) -> None:
        self.control_outcomes.append(outcome)
        if len(self.control_outcomes) > 100:
            self.control_outcomes = self.control_outcomes[-100:]

    def detect_placebo_actions(self) -> dict:
        if len(self.control_outcomes) < self.min_samples_per_group:
            return {"status": "insufficient_control_data", "placebo_actions": []}

        results = {}
        for action_type, outcomes in self.action_outcomes.items():
            if len(outcomes) < self.min_samples_per_group:
                continue

            u_stat, p_value = self._mann_whitney_u(outcomes, self.control_outcomes)
            is_placebo = p_value > self.significance_level

            results[action_type] = {
                "u_statistic": round(u_stat, 2),
                "p_value": round(p_value, 4),
                "is_placebo": is_placebo,
                "action_samples": len(outcomes),
                "control_samples": len(self.control_outcomes),
            }
        return results

    def get_placebo_actions(self) -> list[str]:
        findings = self.detect_placebo_actions()
        if "status" in findings:
            return []
        return [k for k, v in findings.items() if v["is_placebo"]]

    @staticmethod
    def _mann_whitney_u(group_a: list[float], group_b: list[float]) -> tuple[float, float]:
        combined = [(v, "a") for v in group_a] + [(v, "b") for v in group_b]
        combined.sort(key=lambda x: x[0])

        ranks = {}
        i = 0
        while i < len(combined):
            j = i
            while j < len(combined) and combined[j][0] == combined[i][0]:
                j += 1
            avg_rank = (i + j - 1) / 2.0 + 1.0
            for k in range(i, j):
                ranks[(combined[k][0], k)] = avg_rank
            i = j

        rank_sum_a = 0.0
        a_count = 0
        for idx, item in enumerate(combined):
            if item[1] == "a":
                rank_sum_a += ranks[(item[0], idx)]
                a_count += 1
        b_count = len(combined) - a_count

        u_a = rank_sum_a - a_count * (a_count + 1) / 2.0
        expected_u = a_count * b_count / 2.0

        z = (
            (u_a - expected_u) / math.sqrt(a_count * b_count * (a_count + b_count + 1) / 12.0)
            if a_count * b_count > 0
            else 0.0
        )

        p_value = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(z) / math.sqrt(2.0))))

        return u_a, max(p_value, 1e-10)
