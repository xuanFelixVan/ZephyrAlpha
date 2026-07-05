# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.governance.bridges.spec_auditor
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.contracts.protocols
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_spec_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""G-CT-007 — Audit.record_agent_spec() 记录 Agent Spec 注册与变更."""

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
