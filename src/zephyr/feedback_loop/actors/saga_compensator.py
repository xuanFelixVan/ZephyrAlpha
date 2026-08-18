# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.actors.saga_compensator
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

"""Saga Compensator — v0.3.0 R19b

Blindspot: Multi-step repairs fail mid-way; partial state inconsistent.
Risk: R19b — Half-executed repair leaves system worse than before.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 已完成步骤清单
#   fields: completed_steps: list[str]（多步修复中已成功的步骤）
#   code: SagaCompensator.compensate
# 层: 算法
# - id: A1
#   name_zh: 逆序补偿动作生成
#   name_en: reverse_compensation_generation
#   intro: 将已完成步骤逆序映射为 undo_<step> 补偿动作序列
#   code: SagaCompensator.compensate
# 层: 输出
# - id: O1
#   name_zh: 补偿动作序列
#   name_en: compensation_steps
#   intro: list[str]——按逆序排列的 undo 动作，用于回滚半成品修复
#   downstream: FLE 修复执行器（saga 回滚执行）
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class SagaCompensator:
    def compensate(self, completed_steps: list[str]) -> list[str]:
        return [f"undo_{step}" for step in reversed(completed_steps)]
