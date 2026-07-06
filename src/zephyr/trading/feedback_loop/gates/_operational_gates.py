from typing import Final

# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.gates._operational_gates
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
# [A_module] module_id=MOD-UNK__operational_gates | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
