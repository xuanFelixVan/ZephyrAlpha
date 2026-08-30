# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.confidence_estimator
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 置信度评估必须基于历史数据;校准不可跳过
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Confidence Estimator — D-022-05 置信度评估器: certainty×evidence×risk三维评估。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: confidence_estimator.py
# 层: 算法
# - id: A1
#   name_zh: ① ConfidenceEstimator
#   name_en: ConfidenceEstimator
#   intro: class ConfidenceEstimator 源码 L58-L68
#   desc: 公共方法（定义序）: evaluate, should_auto_execute；源码 L58-L68
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ConfidenceEstimator
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class ConfidenceLevel:
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConfidenceEstimator:
    def evaluate(self, certainty: float, evidence: float, risk: float) -> str:
        score = certainty * 0.4 + evidence * 0.35 + (1.0 - risk) * 0.25
        if score >= 0.7:
            return ConfidenceLevel.HIGH
        if score >= 0.4:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW

    def should_auto_execute(self, certainty: float, evidence: float, risk: float) -> bool:
        return self.evaluate(certainty, evidence, risk) is ConfidenceLevel.HIGH and risk < 0.3
