# [BLUEPRINT] MOD-INF-018 | docs/03_modules/l01_infrastructure/agent-rbac/blueprint.md

# [MODULE] zephyr.agent_rbac.a2a_check

# [INVARIANTS] see blueprint MOD-INF-018

# [MODIFY-GUARD] __init__.py

# [CONSUMERS] zephyr.agent_rbac

# [STABILITY] stable

# [SAFETY] M

# [AI_AUTONOMY] human_gated

# [ERROR_CONTRACT] AgentRbacError

# [TESTS]

from __future__ import annotations





from typing import Any, TYPE_CHECKING





if TYPE_CHECKING:


    from zephyr.l01_infrastructure.a2a_protocol import A2ACommunication








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


