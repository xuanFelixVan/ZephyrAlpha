# [A_module] module_id=MOD-UNK_spec_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md

# [MODULE] zephyr.governance.audit_trail.spec_auditor

# [INVARIANTS] see blueprint MOD-INF-020

# [MODIFY-GUARD] __init__.py

# [CONSUMERS] zephyr.governance.audit_trail

# [STABILITY] stable

# [SAFETY] M

# [AI_AUTONOMY] human_gated

# [ERROR_CONTRACT] AuditTrailError

# [TESTS]

from datetime import datetime, timezone

from typing import Any

from zephyr.integration.shared_08.contracts.protocols import AgentCapability

def record_agent_spec(capability: AgentCapability) -> dict[str, Any]:

    caps = getattr(capability, "capabilities", getattr(capability, "claimed_capabilities", []))

    return {

        "event_type": "AGENT_SPEC_REGISTERED",

        "agent_id": capability.agent_id,

        "claimed_capabilities": caps,

        "model_provider": getattr(capability, "model_provider", "unknown"),

        "version": getattr(capability, "version", "0.0.0"),

        "timestamp": datetime.now(timezone.utc).isoformat(),

    }

