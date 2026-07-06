from typing import Final

# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.gates._governance_gates
# [DOMAIN] D_GOVERNANCE
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
# [A_module] module_id=MOD-UNK__governance_gates | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

SUBMODULES: Final[list] = [
    "autonomy_credit",
    "autonomy_maturity",
    "blueprint_code_reconciler",
    "blueprint_validator",
    "checkpoint_manager",
    "config_complexity_budget",
    "config_governance",
    "conflict_arbitration",
    "scope_creep_monitor",
]
