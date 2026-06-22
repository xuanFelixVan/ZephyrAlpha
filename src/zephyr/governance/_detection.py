# [A_module] module_id=MOD-UNK__detection | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain-governance/code-dedup-engine/blueprint.md
# [MODULE] zephyr.testing.code_dedup._detection
# [INVARIANTS] backward_compat: all exports must remain available from code_dedup_engine
# [MODIFY-GUARD] zephyr.testing.code_dedup.__init__
# [CONSUMERS] zephyr.testing.code_dedup.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.testing.code_dedup"

SUBMODULES = [
    "annotations",
    "cache_manager",
    "canary_manager",
    "canary_register",
    "code_analyzer_runner",
    "code_simulator",
    "path_index_validator",
    "symbol_index",
]
