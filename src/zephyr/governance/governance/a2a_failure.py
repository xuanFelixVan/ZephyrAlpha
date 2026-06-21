# [A_module] module_id=MOD-GOV_a2a_failure | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md

# [MODULE] zephyr.governance.governance.a2a_failure

# [INVARIANTS] 不直接import A2A模块(Protocol接口);与主模块a2a_failure.py保持一致

# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""G-CT-008 消费端 — Escalation.on_a2a_failure() 跨 agent 通信失败升级.

Protocol解耦：不直接import A2A模块，使用typing.Protocol定义接口。
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from zephyr.governance.contracts import EscalationContracts


@runtime_checkable
class _A2ACommunicationLike(Protocol):
    a2a_id: str
    from_agent_id: str
    to_agent_id: str


_escalation = EscalationContracts()


def on_a2a_failure(communication: _A2ACommunicationLike, error: str = "") -> dict[str, Any]:
    result = _escalation.on_a2a_failure(communication)
    result["error"] = error
    return result
