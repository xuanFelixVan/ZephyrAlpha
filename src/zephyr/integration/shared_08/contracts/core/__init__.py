# [A_module] module_id=MOD-INT_core | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-158 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.core
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
"""shared.contracts.core — auto-generated package init."""

from . import base_event, gate_types

__all__ = [
    "base_event",
    "enforcer",
    "factories",
    "gate_types",
    "registry",
    "runtime_plane_tag",
    "system_configuration",
    "telemetry_emitter",
    "timestamp",
    "trace_context",
]
