# [A_module] module_id=MOD-RES__infrastructure | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md
# [MODULE] zephyr.infrastructure.rollback._infrastructure
# [INVARIANTS] backward_compat: all exports must remain available from zephyr.infrastructure.rollback
# [MODIFY-GUARD] zephyr.infrastructure.rollback.__init__
# [CONSUMERS] zephyr.infrastructure.rollback.__init__
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "import zephyr.infrastructure.rollback"

SUBMODULES = [
    'checkpoint_gc',
    'cross_platform_shell',
    'down_migration_generator',
    'env_watcher',
    'external_merkle_proof',
    'git_infra_snapshot',
    's3_snapshot_lifecycle',
    'startup_shutdown',
    'startup_shutdown_cli',
    'submodule_sync',
    'venv_sync',
]
