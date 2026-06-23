# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md
# [MODULE] zephyr.infrastructure.rollback._monitoring
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.rollback.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] backward_compat: all exports must remain available from zephyr.infrastructure.rollback
# [MODIFY-GUARD] zephyr.infrastructure.rollback.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.infrastructure.rollback"
# [A_module] module_id=MOD-RES__monitoring | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

SUBMODULES = [
    "agent_cooldown",
    "autonomy_dashboard",
    "budget_tracker",
    "commit_quality_gate",
    "complexity_budget",
    "confidence_quantifier",
    "model_drift_detector",
    "owner_absent",
    "paper_live_transition",
    "post_live_verification",
    "right_to_be_forgotten",
    "rollback_dashboard",
    "rollback_drill",
    "runbook_generator",
    "semantic_rollback_tag",
    "semantic_similar_detector",
    "temporal_context_adapter",
    "topology_change_log",
    "warm_standby",
]
