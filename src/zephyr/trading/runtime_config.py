# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.runtime_config
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.contracts.runtime_types
# [CONSUMERS] zephyr.trading.auto_runtime_core;zephyr.trading.lifecycle_manager;zephyr.trading.windows_service;zephyr.trading.__main__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] RuntimeConfig真源在zephyr.shared.contracts.runtime_types;本文件仅作向后兼容re-export
# [MODIFY-GUARD] src/zephyr/shared/contracts/runtime_types.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_runtime_config | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from zephyr.shared.contracts.runtime_types import DATA_DIR, RuntimeConfig


def ensure_runtime_dirs(config: RuntimeConfig) -> None:
    for d in [
        config.audit_log_dir,
        config.capability_card_dir,
        config.work_dag_dir,
        config.dream_archive_dir,
        config.feedback_proposal_dir,
        config.health_snapshot_dir,
        config.night_shift_storage_path.parent,
        # circadian_state_path 已移除（CircadianScheduler 废除，2026-06-26裁定）
    ]:
        d.mkdir(parents=True, exist_ok=True)


__all__ = ["DATA_DIR", "RuntimeConfig", "ensure_runtime_dirs"]
