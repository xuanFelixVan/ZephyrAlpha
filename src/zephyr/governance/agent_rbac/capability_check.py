"""G-CT-007 — RBAC.verify_capability_scope() 验证 claimed_capabilities 权限范围."""
from __future__ import annotations

from typing import Any

from zephyr.governance.agent_spec.registry import AgentCapability


MAX_CAPABILITIES = 10
RESTRICTED_CAPABILITIES = {"destroy", "meltdown", "purge", "sudo", "root", "admin_override"}


def verify_capability_scope(capability: AgentCapability) -> dict[str, Any]:
    caps = getattr(capability, "capabilities", getattr(capability, "claimed_capabilities", []))
    if len(caps) > MAX_CAPABILITIES:
        return {"approved": False, "agent_id": capability.agent_id, "reason": f"too_many_capabilities: {len(caps)} > {MAX_CAPABILITIES}"}

    restricted = [c for c in caps if c in RESTRICTED_CAPABILITIES]
    if restricted:
        return {"approved": False, "agent_id": capability.agent_id, "reason": f"restricted_capabilities_claimed: {restricted}"}

    if not caps:
        return {"approved": False, "agent_id": capability.agent_id, "reason": "no_capabilities_claimed"}

    return {"approved": True, "agent_id": capability.agent_id, "capabilities": caps}
