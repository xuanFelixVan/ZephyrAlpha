# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.a2a_failure

# [INVARIANTS] A2A失败必须触发升级;升级不可跳过;不直接import A2A模块(Protocol接口)

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine.adapter

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

G-CT-008 消费端 — Escalation.on_a2a_failure() 跨 agent 通信失败升级.
使用 Protocol 接口解耦，不直接 import zephyr.l01_infrastructure.a2a_protocol。
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from zephyr.escalation_engine.contracts import EscalationContracts


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
