"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: _safety_gates.py
# 层: 算法
# - id: A1
#   name_zh: ① 模块占位（无公共定义）
#   name_en: placeholder
#   intro: _safety_gates.py 无顶层公共函数/类/再导出（AST 事实）
#   desc: 源码 L1-L70；包结构占位或纯内部模块
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
# [MODULE] zephyr.feedback_loop.gates._safety_gates
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
    "parameterized_safety_gate",
    "safety_gate_L1_L27",
    "safety_gate_L28_L29",
    "safety_gate_L36_L37",
    "safety_gate_L38_L39",
    "safety_gate_L40_L41",
    "safety_gate_L42_L43",
    "safety_gate_L44_L45",
    "safety_gate_L46_L47",
    "safety_gate_L48_L49",
    "safety_gate_L50_L51",
    "safety_gate_L52_L53",
    "safety_gate_L54_L55",
    "safety_gate_L56_L57",
    "safety_gate_L58_L59",
    "safety_gate_L60_L61",
    "safety_gate_L62_L63",
    "safety_gate_L64_L65",
    "safety_gate_L66_L67",
]
