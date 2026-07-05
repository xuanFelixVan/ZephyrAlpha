# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.agent_spec.a2a_failure
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.services.adapter
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] A2A失败必须触发升级;升级不可跳过;不直接import A2A模块(Protocol接口)
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_a2a_failure | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

G-CT-008 消费端 — Escalation.on_a2a_failure() 跨 agent 通信失败升级.
使用 Protocol 接口解耦，不直接 import zephyr.infrastructure.a2a_protocol。
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from zephyr.governance.escalation.contracts import EscalationContracts


@runtime_checkable
class CommunicationFailureEvent(Protocol):
    a2a_id: str
    from_agent_id: str
    to_agent_id: str


_escalation = EscalationContracts()


def on_a2a_failure(communication: CommunicationFailureEvent, error: str = "") -> dict[str, Any]:
    result = _escalation.on_a2a_failure(communication)
    result["error"] = error
    return result


class _A2ACommunicationLike:
    def __init__(self, protocol="", endpoint="", timeout=30):
        self.protocol = protocol
        self.endpoint = endpoint
        self.timeout = timeout

    def is_available(self):
        return True
