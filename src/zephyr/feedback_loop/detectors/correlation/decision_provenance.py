# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.correlation.decision_provenance
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Decision Provenance — v0.12.0 R166

Blindspot: FLE decisions lack audit trail of contributing factors.
Risk: R166 — Why was this repair chosen?  Invisible after the fact.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: decision_provenance.py
# 层: 算法
# - id: A1
#   name_zh: ① DecisionProvenance
#   name_en: DecisionProvenance
#   intro: class DecisionProvenance 源码 L55-L59
#   desc: 公共方法（定义序）: record；源码 L55-L59
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: DecisionProvenance
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field


@dataclass
class DecisionProvenance:
    decisions: list[dict] = field(default_factory=list)

    def record(self, decision: dict) -> None:
        self.decisions.append(decision)
