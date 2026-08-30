"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: _operational_gates.py
# 层: 算法
# - id: A1
#   name_zh: ① 模块占位（无公共定义）
#   name_en: placeholder
#   intro: _operational_gates.py 无顶层公共函数/类/再导出（AST 事实）
#   desc: 源码 L1-L58；包结构占位或纯内部模块
#   inputs: I1
#   outputs: 无（占位）
# 层: 输出
# - id: O1
#   name_zh: 无输出（占位模块）
#   name_en: none
#   intro: 无公共定义无再导出（AST 事实）
#   downstream: zephyr.feedback_loop.gates.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.feedback_loop.gates._operational_gates
# [DOMAIN] D_FBL_VERIFICATION
# [DEPENDENCIES] zephyr.feedback_loop.gates.__init__
# [CONSUMERS] zephyr.feedback_loop.gates.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] backward_compat: all exports must remain available from feedback-loop.gates
# [MODIFY-GUARD] zephyr.feedback_loop.gates.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.feedback_loop.gates"
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

SUBMODULES: Final[list] = [
    "action_reversibility",
    "data_quality_gate",
    "db_integrity",
    "dynamic_llm_cost_router",
    "flag_lifecycle_manager",
    "llm_cost_router",
    "meta_performance_gate",
]
