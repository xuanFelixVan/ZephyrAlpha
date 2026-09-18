# [A_module] module_id=MOD-INF-compensation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.compensation
# [DOMAIN] D_INFRA_RUNTIME
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
Re-export wrapper: true source is zephyr.shared.compensation.

Auto-generated stub; submodules migrated to shared/compensation/.
Uses lazy __getattr__ to avoid import errors for non-existent local submodules.

# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure/algo_flow/compensation/compensation__init__.yaml
"""

_SUBMODULES = {
    "saga_compensator": "zephyr.shared.compensation.saga_compensator",
}


def __getattr__(name):
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(_SUBMODULES[name])
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["saga_compensator"]
