"""G-CT-008 消费端 — Escalation.on_a2a_failure() 跨 agent 通信失败升级."""
from __future__ import annotations

from typing import Any

from zephyr.governance.a2a.protocol import A2ACommunication
from zephyr.governance.escalation.contracts import EscalationContracts


_escalation = EscalationContracts()


def on_a2a_failure(communication: A2ACommunication, error: str = "") -> dict[str, Any]:
    result = _escalation.on_a2a_failure(communication)
    result["error"] = error
    return result
