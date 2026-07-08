# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
# [MODULE] zephyr.integration.budget_enforcer.degradation_spiral_detector
# [DOMAIN] D_INTEGRATION
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
# [A_module] module_id=MOD-INT_degradation_spiral_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Degradation Spiral Detector — 模型幻觉-容量正反馈螺旋检测 (盲点 #19, M-29)
特性：
  - 幻觉率 > 10% + Token 消耗 > 2× baseline -> 螺旋预警
  - SLI CAP-SPI-001: spiral_coefficient > 1.5 -> 阻断
"""

import time


class DegradationSpiralDetector:
    """
    正反馈螺旋检测器 (M-29, 盲点 #19)
    """

    SLI_ID = "CAP-SPI-001"
    HALLUCINATION_THRESHOLD = 0.10
    TOKEN_MULTIPLIER_THRESHOLD = 2.0
    SPIRAL_COEFFICIENT_THRESHOLD = 1.5

    def __init__(self):
        self._baseline_tokens = 0
        self._baseline_set = False

    def set_baseline(self, avg_tokens_per_request: float):
        self._baseline_tokens = avg_tokens_per_request
        self._baseline_set = True

    def detect(self, hallucination_rate: float, current_tokens: int) -> dict:
        spiral_detected = False
        spiral_coefficient = 1.0

        if hallucination_rate > self.HALLUCINATION_THRESHOLD:
            if self._baseline_set and self._baseline_tokens > 0:
                token_multiplier = current_tokens / self._baseline_tokens
                if token_multiplier > self.TOKEN_MULTIPLIER_THRESHOLD:
                    spiral_detected = True
                    spiral_coefficient = hallucination_rate * token_multiplier

        return {
            "sli_id": self.SLI_ID,
            "hallucination_rate": hallucination_rate,
            "spiral_detected": spiral_detected,
            "spiral_coefficient": round(spiral_coefficient, 2),
            "require_intervention": spiral_coefficient > self.SPIRAL_COEFFICIENT_THRESHOLD,
            "timestamp": time.time(),
        }
