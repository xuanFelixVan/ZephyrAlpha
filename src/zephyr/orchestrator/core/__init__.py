# [DOMAIN] D_ORCHESTRATOR

# [A_module] module_id=MOD-INF-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md

# [MODULE] zephyr.orchestrator.core

# [INVARIANTS] pending_review

# [MODIFY-GUARD] no structural changes without owner approval

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [CONSUMERS]

# [ERROR_CONTRACT]

# [TESTS]

# [TTL] permanent

"""
orchestrator.core — auto-generated package init.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: __init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 agent_orchestrator, task_queue, wave_generator（共 3 符号）
#   desc: __init__ import L0；__all__ 3 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（3 符号）
#   name_en: __all__
#   intro: agent_orchestrator, task_queue, wave_generator
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = ["agent_orchestrator", "task_queue", "wave_generator"]
