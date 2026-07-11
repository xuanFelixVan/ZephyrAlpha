# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.evolution.prompt_optimization_regression_detector
# [DOMAIN] D_FEEDBACK_LOOP
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
# [A_module] module_id=MOD-UNK_prompt_optimization_regression_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R514: PromptOptimizationRegressionDetector
提示优化前A/B验证 — 新旧提示对比held-out验证集，p<0.05才允许部署
"""

from dataclasses import dataclass, field


@dataclass
class PromptOptimizationRegressionDetector:
    old_prompt_results: list[float] = field(default_factory=list)
    new_prompt_results: list[float] = field(default_factory=list)
    min_test_samples: int = 10
    significance_level: float = 0.05

    def run_ab_test(self, old_results: list[float], new_results: list[float]) -> dict:
        self.old_prompt_results = old_results
        self.new_prompt_results = new_results

        if len(old_results) < self.min_test_samples or len(new_results) < self.min_test_samples:
            return {"status": "insufficient_samples", "decision": "REJECT"}

        old_mean = sum(old_results) / len(old_results)
        new_mean = sum(new_results) / len(new_results)
        improvement = new_mean - old_mean

        t_stat, p_value = self._welch_ttest(old_results, new_results)

        significant = p_value < self.significance_level
        improved = improvement > 0

        decision = "ALLOW" if (significant and improved) else "REJECT"

        return {
            "status": decision,
            "old_mean": round(old_mean, 4),
            "new_mean": round(new_mean, 4),
            "improvement": round(improvement, 4),
            "t_statistic": round(t_stat, 3),
            "p_value": round(p_value, 4),
            "significant": significant,
            "samples": len(old_results),
            "recommendation": "deploy_new_prompt" if decision == "ALLOW" else "keep_old_prompt",
        }

    @staticmethod
    def _welch_ttest(a: list[float], b: list[float]) -> tuple[float, float]:
        import math

        n1, n2 = len(a), len(b)
        mean1 = sum(a) / n1
        mean2 = sum(b) / n2
        var1 = sum((x - mean1) ** 2 for x in a) / (n1 - 1) if n1 > 1 else 0
        var2 = sum((x - mean2) ** 2 for x in b) / (n2 - 1) if n2 > 1 else 0

        se = math.sqrt(var1 / n1 + var2 / n2)
        if se < 1e-10:
            return 0.0, 1.0

        t_stat = (mean1 - mean2) / se

        df_num = (var1 / n1 + var2 / n2) ** 2
        df_den = (var1 / n1) ** 2 / (n1 - 1) + (var2 / n2) ** 2 / (n2 - 1) if n1 > 1 and n2 > 1 else 1
        degrees_of_freedom = df_num / df_den if df_den > 0 else 1

        effect_size = degrees_of_freedom / (degrees_of_freedom + t_stat * t_stat + 1e-10)
        import math as m

        p_value = 2.0 * (1.0 - 0.5 * (1.0 + m.erf(abs(t_stat) / m.sqrt(2.0))))

        return t_stat, min(p_value, 1.0)
