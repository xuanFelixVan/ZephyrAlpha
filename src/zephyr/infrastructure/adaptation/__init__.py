# [A_module] module_id=MOD-INF_adaptation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-082 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.adaptation
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""Re-export wrapper: true source is zephyr.shared.adaptation.

Auto-generated stub; submodules migrated to shared/adaptation/.
Uses lazy __getattr__ to avoid import errors for non-existent local submodules.
"""

_SUBMODULES = {
    "execution_tuner": "zephyr.shared.adaptation.execution_tuner",
    "prompt_version_manager": "zephyr.shared.adaptation.prompt_version_manager",
}


def __getattr__(name):
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(_SUBMODULES[name])
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["execution_tuner", "prompt_version_manager"]
