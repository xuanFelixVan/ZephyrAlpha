# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md
# [MODULE] zephyr.integration.budget_enforcer.degradation_spiral_detector
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Degradation Spiral Detector — 模型幻觉-容量正反馈螺旋检测 (盲点 #19, M-29)
特性：
  - 幻觉率 > 10% + Token 消耗 > 2× baseline -> 螺旋预警
  - SLI CAP-SPI-001: spiral_coefficient > 1.5 -> 阻断

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 幻觉率与当前 token 消耗
#   fields: hallucination_rate 浮点（0~1）+ current_tokens 整数
#   code: detect(hallucination_rate, current_tokens) L46
# - id: I2
#   name: token 基线
#   fields: avg_tokens_per_request 每请求平均 token 浮点
#   code: set_baseline(avg_tokens_per_request) L42
# 层: 算法
# - id: A1
#   name_zh: ① 基线设定
#   name_en: set_baseline
#   intro: 先录一个正常时每请求平均 token 数，后面拿来做倍数比较
#   desc: 存 _baseline_tokens 并置 _baseline_set=True
#   inputs: I2
#   outputs: 基线就绪标志
# - id: A2
#   name_zh: ② 幻觉-容量螺旋检测
#   name_en: DegradationSpiralDetector.detect
#   intro: 幻觉率超 10% 且 token 超基线 2 倍就判定正反馈螺旋，系数超 1.5 要求干预
#   desc: hallucination_rate>0.10 且已设基线 → token_multiplier=current_tokens/baseline；>2.0 则 spiral_detected=True 且 spiral_coefficient=hallucination_rate×token_multiplier（保留2位小数）；coefficient>1.5 → require_intervention=True
#   inputs: I1 A1
#   outputs: 检测结果字典
#   invariant: SLI CAP-SPI-001；spiral_coefficient>1.5 触发阻断
# 层: 输出
# - id: O1
#   name_zh: 螺旋检测报告
#   name_en: detect result dict
#   intro: 含 sli_id/幻觉率/是否螺旋/螺旋系数/是否需干预/时间戳的检测结论
#   downstream: 无下游/内部使用（# [CONSUMERS] 头为空）
# [/ALGO_FLOW]
#
# 边:
# I2 --> A1
# I1 --> A2
# A1 --> A2
# A2 --> O1
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
