# [BLUEPRINT] MOD-INF-020 | 03_modules/l01_infrastructure/audit-trail/blueprint.md | §

# [MODULE] zephyr.audit_trail.spec_auditor

# [INVARIANTS] see blueprint MOD-INF-020

# [MODIFY-GUARD] __init__.py

# [CONSUMERS] zephyr.audit_trail

# [STABILITY] stable

# [SAFETY] M

# [AI_AUTONOMY] human_gated

# [ERROR_CONTRACT] AuditTrailError

# [TESTS]

from __future__ import annotations





from datetime import datetime, timezone


from typing import Any





from zephyr.agent_spec.registry import AgentCapability








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


