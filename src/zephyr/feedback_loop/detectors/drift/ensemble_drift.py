# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.drift.ensemble_drift
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
Ensemble Drift — v0.5.0 R43

Blindspot: Ensemble model agreement drifts toward uniformity or chaos.
Risk: R43 — Unanimous agreement masks model monoculture.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: ensemble_drift.py
# 层: 算法
# - id: A1
#   name_zh: ① EnsembleDrift
#   name_en: EnsembleDrift
#   intro: class EnsembleDrift 源码 L55-L61
#   desc: 公共方法（定义序）: monitor；源码 L55-L61
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: EnsembleDrift
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class EnsembleDrift:
    agreement_rate: float = 0.0

    def monitor(self, new_rate: float) -> bool:
        drift = abs(new_rate - self.agreement_rate)
        self.agreement_rate = new_rate
        return drift > 0.2
