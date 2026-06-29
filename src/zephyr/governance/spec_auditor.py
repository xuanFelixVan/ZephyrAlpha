# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.governance.audit_trail.spec_auditor
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.contracts.protocols
# [CONSUMERS] zephyr.governance.audit_trail
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] see blueprint MOD-INF-020
# [MODIFY-GUARD] __init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AuditTrailError
# [TESTS]
# [A_module] module_id=MOD-UNK_spec_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from datetime import UTC, datetime
from typing import Any

from zephyr.shared.contracts.protocols import AgentCapability


def record_agent_spec(capability: AgentCapability) -> dict[str, Any]:
    caps = getattr(capability, "capabilities", getattr(capability, "claimed_capabilities", []))

    return {
        "event_type": "AGENT_SPEC_REGISTERED",
        "agent_id": capability.agent_id,
        "claimed_capabilities": caps,
        "model_provider": getattr(capability, "model_provider", "unknown"),
        "version": getattr(capability, "version", "0.0.0"),
        "timestamp": datetime.now(UTC).isoformat(),
    }
