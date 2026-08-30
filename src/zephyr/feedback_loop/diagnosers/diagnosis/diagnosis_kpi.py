# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.diagnosis.diagnosis_kpi
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
Diagnosis KPI — v0.9.0 R116

Blindspot: No metrics on how often diagnoses lead to effective repairs.
Risk: R116 — Broken diagnosis pipeline invisible — repair feedback loop severed.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: diagnosis_kpi.py
# 层: 算法
# - id: A1
#   name_zh: ① DiagnosisKPI
#   name_en: DiagnosisKPI
#   intro: class DiagnosisKPI 源码 L55-L61
#   desc: 公共方法（定义序）: effectiveness_rate；源码 L55-L61
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: DiagnosisKPI
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class DiagnosisKPI:
    total: int = 0
    effective: int = 0

    @property
    def effectiveness_rate(self) -> float:
        return self.effective / max(self.total, 1)
