# [A_module] module_id=MOD-ORC__infrastructure | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-008 | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core._infrastructure
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新__init__.py的__all__
# [CONSUMERS] zephyr.autonomy_core.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_context_engine_imports.py

_SUBMODULES = [
    "budget_forecaster",
    "cache_invalidation",
    "ce_bootstrap",
    "checkpoint_manager",
    "cold_start_booster",
    "dependency_tracker",
    "domain_decay_config",
    "embedding_version_lock",
    "fallback_staleness_gate",
    "host_resource_governor",
    "mcp_adapter",
    "otel_instrumentation",
    "pipeline_orchestrator",
    "session_learner",
    "vector_bridge",
]
