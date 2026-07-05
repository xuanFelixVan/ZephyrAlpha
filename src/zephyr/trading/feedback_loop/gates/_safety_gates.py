# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.gates._safety_gates
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.gates.__init__
# [CONSUMERS] zephyr.trading.feedback_loop.gates.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] backward_compat: all exports must remain available from feedback-loop.gates
# [MODIFY-GUARD] zephyr.trading.feedback_loop.gates.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.trading.feedback_loop.gates"
# [A_module] module_id=MOD-UNK__safety_gates | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

SUBMODULES = [
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
