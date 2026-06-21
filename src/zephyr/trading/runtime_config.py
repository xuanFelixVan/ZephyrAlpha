# [A_module] module_id=MOD-ORC_runtime_config | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md
# [MODULE] zephyr.trading.runtime_config
# [INVARIANTS] RuntimeConfig真源在zephyr.integration.shared_08.contracts.runtime_types;本文件仅作向后兼容re-export
# [MODIFY-GUARD] src/zephyr/shared/contracts/runtime_types.py
# [CONSUMERS] zephyr.trading.auto_runtime_core;zephyr.trading.lifecycle_manager;zephyr.trading.windows_service;zephyr.trading.__main__
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]

from zephyr.integration.shared_08.contracts.runtime_types import RuntimeConfig, DATA_DIR

def ensure_runtime_dirs(config: RuntimeConfig) -> None:
    for d in [
        config.audit_log_dir,
        config.capability_card_dir,
        config.work_dag_dir,
        config.dream_archive_dir,
        config.feedback_proposal_dir,
        config.health_snapshot_dir,
        config.night_shift_storage_path.parent,
        config.circadian_state_path.parent,
    ]:
        d.mkdir(parents=True, exist_ok=True)

__all__ = ["RuntimeConfig", "DATA_DIR", "ensure_runtime_dirs"]