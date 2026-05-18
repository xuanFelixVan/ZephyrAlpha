# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.governance_bridges.a2a_check

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""G-CT-008 — RBAC.verify_a2a_pair() 验证 agent 间通信权限."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from zephyr.l01_infrastructure.a2a_protocol.governance.protocol import A2ACommunication  # G-CT-008 bridge


ALLOWED_TALK_PAIRS: set[tuple[str, str]] = {
    ("orchestrator", "worker"),
    ("worker", "orchestrator"),
    ("auditor", "orchestrator"),
    ("superadmin", "*"),
    ("*", "superadmin"),
}


def verify_a2a_pair(from_agent: str, to_agent: str) -> dict[str, Any]:
    if (from_agent, to_agent) in ALLOWED_TALK_PAIRS:
        return {"approved": True, "from": from_agent, "to": to_agent}

    if ("superadmin", "*") in ALLOWED_TALK_PAIRS and from_agent == "superadmin":
        return {"approved": True, "from": from_agent, "to": to_agent}

    if ("*", "superadmin") in ALLOWED_TALK_PAIRS and to_agent == "superadmin":
        return {"approved": True, "from": from_agent, "to": to_agent}

    if from_agent == to_agent:
        return {"approved": True, "from": from_agent, "to": to_agent, "reason": "self_communication"}

    return {"approved": False, "from": from_agent, "to": to_agent, "reason": "pair_not_allowed"}
