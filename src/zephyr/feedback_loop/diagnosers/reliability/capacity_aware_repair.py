# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.capacity_aware_repair
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
Capacity Aware Repair — v0.9.0 R120

Blindspot: FLE executes repairs without accounting for current resource headroom.
Risk: R120 — Repair action itself causes resource exhaustion — cascading failure.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: capacity_aware_repair.py
# 层: 算法
# - id: A1
#   name_zh: ① CapacityAwareRepair
#   name_en: CapacityAwareRepair
#   intro: class CapacityAwareRepair 源码 L55-L57
#   desc: 公共方法（定义序）: check_headroom；源码 L55-L57
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: CapacityAwareRepair
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class CapacityAwareRepair:
    def check_headroom(self, action_cost: float, available: float) -> bool:
        return available >= action_cost * 1.2
