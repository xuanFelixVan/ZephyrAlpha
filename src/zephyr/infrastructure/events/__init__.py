# [A_module] module_id=MOD-INF_events | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.events
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""core.events — event infrastructure.

event_store: local implementation.
event_reactor, hook_dispatcher, event_bus: re-exported from zephyr.shared.events (true source).
"""

from . import event_store

_LAZY_SUBMODULES = {
    "event_bus": "zephyr.shared.event_bus",
    "event_reactor": "zephyr.shared.events.event_reactor",
    "hook_dispatcher": "zephyr.shared.events.hook_dispatcher",
}


def __getattr__(name):
    if name in _LAZY_SUBMODULES:
        import importlib

        mod = importlib.import_module(_LAZY_SUBMODULES[name])
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["event_bus", "event_reactor", "event_store", "hook_dispatcher"]


class DriftEvent:
    def __init__(
        self, event_id="", drift_type="", severity="medium", description="", timestamp=None, source="", target=""
    ):
        self.event_id = event_id
        self.drift_type = drift_type
        self.severity = severity
        self.description = description
        self.timestamp = timestamp
        self.source = source
        self.target = target


class DriftType:
    SCHEMA = "SCHEMA"
    CONTRACT = "CONTRACT"
    BEHAVIORAL = "BEHAVIORAL"
    CONFIGURATION = "CONFIGURATION"
    DEPENDENCY = "DEPENDENCY"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    UNKNOWN = "UNKNOWN"


class DriftState:
    DETECTED = "DETECTED"
    ANALYZING = "ANALYZING"
    FIXING = "FIXING"
    VERIFIED = "VERIFIED"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"
