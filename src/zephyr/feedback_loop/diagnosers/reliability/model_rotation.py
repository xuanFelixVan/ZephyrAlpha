# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.model_rotation
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
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
Model Rotation — v0.9.0 R125

Blindspot: Single model reliance creates SPOF in diagnosis pipeline.
Risk: R125 — Model degradation without rotation causes systemic diagnosis failure.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: model_rotation.py
# 层: 算法
# - id: A1
#   name_zh: ① ModelRotation
#   name_en: ModelRotation
#   intro: class ModelRotation 源码 L55-L64
#   desc: 公共方法（定义序）: rotate；源码 L55-L64
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ModelRotation
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field


@dataclass
class ModelRotation:
    models: list[str] = field(default_factory=list)
    active: str = ""

    def rotate(self) -> str:
        if not self.models:
            return self.active
        idx = (self.models.index(self.active) + 1) % len(self.models) if self.active in self.models else 0
        self.active = self.models[idx]
        return self.active
