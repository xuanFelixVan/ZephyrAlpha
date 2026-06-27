# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core._injection
# [DOMAIN] D-AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS] zephyr.autonomy_core.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] _SUBMODULES列表不变
# [MODIFY-GUARD] 新增子模块须同步更新__init__.py的__all__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_context_engine_imports.py
# [A_module] module_id=MOD-ORC__injection | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

_SUBMODULES = [
    "atomic_injector",
    "diff_injector",
    "progressive_disclosure_injector",
    "contextual_fetch_api",
    "prompt_registry",
    "knowledge_distiller",
    "citation_walker",
    "ce_vibe_shortcuts",
    "ce_playground_v2",
    "context_playground",
    "ce_explain_cli",
]
