# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.evolution.online_feature_importance
# [DOMAIN] D_FEEDBACK_LOOP
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
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Online Feature Importance — v0.7.0 R73

Blindspot: Feature importance computed offline; stale in real-time.
Risk: R73 — Importance rankings lag; wrong features drive diagnosis.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: online_feature_importance.py
# 层: 算法
# - id: A1
#   name_zh: ① OnlineFeatureImportance
#   name_en: OnlineFeatureImportance
#   intro: class OnlineFeatureImportance 源码 L55-L59
#   desc: 公共方法（定义序）: update；源码 L55-L59
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: OnlineFeatureImportance
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field


@dataclass
class OnlineFeatureImportance:
    scores: dict[str, float] = field(default_factory=dict)

    def update(self, feature: str, importance: float) -> None:
        self.scores[feature] = importance
