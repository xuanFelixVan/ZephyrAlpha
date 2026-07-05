# [A_module] module_id=MOD-INF_maintenance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-115 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.maintenance
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""Re-export wrapper: true source is zephyr.shared.maintenance.

Auto-generated stub; submodules migrated to shared/maintenance/.
Uses lazy __getattr__ to avoid import errors for non-existent local submodules.
"""

_SUBMODULES = {
    "autonomy_monitor": "zephyr.shared.maintenance.autonomy_monitor",
    "dogfooding": "zephyr.shared.maintenance.dogfooding",
    "handbook": "zephyr.shared.maintenance.handbook",
    "zero_config": "zephyr.shared.maintenance.zero_config",
}


def __getattr__(name):
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(_SUBMODULES[name])
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["autonomy_monitor", "dogfooding", "handbook", "zero_config"]
