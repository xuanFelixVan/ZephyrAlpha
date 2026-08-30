# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.verifiers.verification_engine
# [DOMAIN] D_FBL_VERIFICATION
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: verification_engine.py
# 层: 算法
# - id: A1
#   name_zh: ① VerificationEngine
#   name_en: VerificationEngine
#   intro: class VerificationEngine 源码 L69-L91
#   desc: 公共方法（定义序）: verify；源码 L69-L91
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: VerificationEngine
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass
from enum import Enum


class Verdict(str, Enum):
    EFFECTIVE = "EFFECTIVE"
    INEFFECTIVE = "INEFFECTIVE"
    HARMFUL = "HARMFUL"


@dataclass
class VerificationResult:
    anomaly_id: str
    pre_value: float
    post_value: float
    delta: float
    verdict: Verdict
    timestamp: float


@dataclass
class VerificationEngine:
    def verify(
        self,
        anomaly_id: str,
        pre_value: float,
        post_value: float,
        timestamp: float,
    ) -> VerificationResult:
        delta = post_value - pre_value
        if delta < -0.01:
            verdict = Verdict.HARMFUL
        elif abs(delta) < 0.01:
            verdict = Verdict.INEFFECTIVE
        else:
            verdict = Verdict.EFFECTIVE
        return VerificationResult(
            anomaly_id=anomaly_id,
            pre_value=pre_value,
            post_value=post_value,
            delta=delta,
            verdict=verdict,
            timestamp=timestamp,
        )
