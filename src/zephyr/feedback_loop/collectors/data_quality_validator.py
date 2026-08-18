# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.collectors.data_quality_validator
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
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

"""Data Quality Validator — v0.9.0 R110

Blindspot: Corrupt data enters FLE pipeline undetected.
Risk: R110 — Diagnosis on garbage data; repair targets wrong system.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 待校验数据点
#   fields: data_point dict（字段名 → 值）
#   code: DataQualityValidator.validate
# 层: 算法
# - id: A1
#   name_zh: 全数值类型校验
#   name_en: all_numeric_type_check
#   intro: data_point 所有值均为 int/float 才返回 True，任一非数值则判为脏数据
#   code: DataQualityValidator.validate
# 层: 输出
# - id: O1
#   name_zh: 数据质量结论
#   name_en: data_quality_verdict
#   intro: bool——数据点是否获准进入 FLE 流水线
#   downstream: FLE 诊断流水线（仅消费通过校验的数据）
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class DataQualityValidator:
    def validate(self, data_point: dict) -> bool:
        return all(isinstance(v, (int, float)) for v in data_point.values())
