# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain-governance/code-dedup-engine/blueprint.md
# [MODULE] zephyr.testing.code_dedup._cli_and_tools
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.testing.code_dedup.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] backward_compat: all exports must remain available from code_dedup_engine
# [MODIFY-GUARD] zephyr.testing.code_dedup.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.testing.code_dedup"
# [A_module] module_id=MOD-UNK__cli_and_tools | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

SUBMODULES = [
    "cli",
    "debt_projector",
    "mock_duplicate_generator",
]
