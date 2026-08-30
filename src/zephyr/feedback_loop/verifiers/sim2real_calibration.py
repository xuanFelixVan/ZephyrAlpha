# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.verifiers.sim2real_calibration
# [DOMAIN] D_FBL_VERIFICATION
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
Sim2Real Calibration — v0.6.0 R56

Blindspot: Simulation accuracy degrades without recalibration.
Risk: R56 — Simulated repair success rate diverges from real success rate.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: sim2real_calibration.py
# 层: 算法
# - id: A1
#   name_zh: ① Sim2RealCalibration
#   name_en: Sim2RealCalibration
#   intro: class Sim2RealCalibration 源码 L55-L61
#   desc: 公共方法（定义序）: gap；源码 L55-L61
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: Sim2RealCalibration
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class Sim2RealCalibration:
    sim_accuracy: float = 0.0
    real_accuracy: float = 0.0

    @property
    def gap(self) -> float:
        return abs(self.sim_accuracy - self.real_accuracy)
