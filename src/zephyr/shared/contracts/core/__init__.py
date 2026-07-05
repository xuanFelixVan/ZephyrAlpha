# [A_module] module_id=MOD-SHR_core | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [TTL] permanent
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
