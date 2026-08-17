# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.lifecycle
# [DOMAIN] D_ORCHESTRATOR
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""lifecycle — orchestrator lifecycle subpackage."""

__all__: list[str] = [
    "housekeeping",
    "incident_postmortem",
    "rolling_upgrade",
    "session_conflict",
    "startup_sequencer",
    "state_propagation",
    "state_synchronizer",
    "system_transfer",
    "teardown_manager",
]
