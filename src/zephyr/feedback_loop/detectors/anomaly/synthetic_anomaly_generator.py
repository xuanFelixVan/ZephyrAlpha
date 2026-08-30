# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.anomaly.synthetic_anomaly_generator
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
Synthetic Anomaly Generator — v0.9.0 R112

Blindspot: No adversarial testing data; detectors never stress-tested.
Risk: R112 — Detectors fail under conditions never seen in training.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: synthetic_anomaly_generator.py
# 层: 算法
# - id: A1
#   name_zh: ① SyntheticAnomalyGenerator
#   name_en: SyntheticAnomalyGenerator
#   intro: class SyntheticAnomalyGenerator 源码 L55-L57
#   desc: 公共方法（定义序）: generate；源码 L55-L57
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SyntheticAnomalyGenerator
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class SyntheticAnomalyGenerator:
    def generate(self, pattern: str, count: int) -> list[dict]:
        return [{"pattern": pattern, "id": i} for i in range(count)]
