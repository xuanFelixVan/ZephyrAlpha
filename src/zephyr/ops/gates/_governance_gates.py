# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.observability.feedback_loop.gates._governance_gates
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.ops.gates.__init__
# [CONSUMERS] zephyr.observability.feedback_loop.gates.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] backward_compat: all exports must remain available from feedback-loop.gates
# [MODIFY-GUARD] zephyr.observability.feedback_loop.gates.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.ops.gates"
# [A_module] module_id=MOD-UNK__governance_gates | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

SUBMODULES = [
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
