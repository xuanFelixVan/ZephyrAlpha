# [A_module] module_id=MOD-INF_knowledge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-103 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.knowledge
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""Re-export wrapper: true source is zephyr.shared.knowledge.

Auto-generated stub; submodules migrated to shared/knowledge/.
Uses lazy __getattr__ to avoid import errors for non-existent local submodules.
"""

_SUBMODULES = {
    "ke_linker": "zephyr.shared.knowledge.ke_linker",
    "ke_structurer": "zephyr.shared.knowledge.ke_structurer",
    "kms_interface": "zephyr.shared.knowledge.kms_interface",
}


def __getattr__(name):
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(_SUBMODULES[name])
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["ke_linker", "ke_structurer", "kms_interface"]
