"""G-CT-007 — Audit.record_agent_spec() 记录 Agent Spec 注册与变更."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from zephyr.governance.agent_spec.registry import AgentCapability


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
