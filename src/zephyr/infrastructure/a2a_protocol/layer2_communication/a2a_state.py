# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md

# [MODULE] zephyr.infrastructure.a2a_protocol.layer2_communication.a2a_state

# [DOMAIN] D_INFRA_A2A

# [DEPENDENCIES] zephyr.shared.protocols.a2a.a2a_schemas

# [CONSUMERS]

# [STARTUP] imported

# [MATURITY] production

# [INVARIANTS] core types imported from zephyr.shared.protocols.a2a; no duplicate definitions

# [MODIFY-GUARD] none

# [STABILITY] stable

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

# [A_module] module_id=MOD-INF-025 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

# [TTL] permanent


"""
A2A Task 状态机 — Layer 2 Communication



Core types (A2ATaskStatus, A2ATask, A2AStateMachine) are imported from

zephyr.shared.protocols.a2a.a2a_schemas.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: a2a_state.py
# 层: 算法
# - id: A1
#   name_zh: ① 模块占位（无公共定义）
#   name_en: placeholder
#   intro: a2a_state.py 无顶层公共函数/类/再导出（AST 事实）
#   desc: 源码 L1-L70；包结构占位或纯内部模块
#   inputs: I1
#   outputs: 无（占位）
# 层: 输出
# - id: O1
#   name_zh: 无输出（占位模块）
#   name_en: none
#   intro: 无公共定义无再导出（AST 事实）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.shared.protocols.a2a.a2a_schemas import A2AStateMachine, A2ATask, A2ATaskStatus  # noqa: F401
