# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.correlation.cross_signal_validator
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Cross-Signal Validator — v0.6.0 R63

Blindspot: Single-signal anomaly may be noise; cross-signal validation missing.
Risk: R63 — Noise spike triggers repair on healthy system.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: cross_signal_validator.py
# 层: 算法
# - id: A1
#   name_zh: ① CrossSignalValidator
#   name_en: CrossSignalValidator
#   intro: class CrossSignalValidator 源码 L55-L57
#   desc: 公共方法（定义序）: validate；源码 L55-L57
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: CrossSignalValidator
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class CrossSignalValidator:
    def validate(self, primary: float, corroborating: list[float]) -> bool:
        return all(abs(primary - c) < primary * 0.5 for c in corroborating)
