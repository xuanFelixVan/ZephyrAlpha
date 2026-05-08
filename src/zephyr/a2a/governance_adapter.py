"""A2A GovernanceAdapter — Phase 4 治理集成桥接器

G-CT-008: A2A → RBAC + Escalation
触发条件：Phase 4 激活后，A2A 通信需要经过 RBAC 验证 + Escalation 升级。
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any

__all__ = ["GovernanceAdapter", "A2AGovernanceRecord"]

_log = logging.getLogger(__name__)

_lsg_gateway = None


def _get_lsg():
    global _lsg_gateway
    if _lsg_gateway is not None:
        return _lsg_gateway
    try:
        from zephyr.llm_security.gateway import LSGSecurityGateway
        _lsg_gateway = LSGSecurityGateway()
        return _lsg_gateway
    except Exception:
        _log.debug("LSG not available for A2A governance")
        return None


def _lsg_scan_a2a_sync(from_agent: str, to_agent: str, content: str) -> str | None:
    gw = _get_lsg()
    if gw is None:
        return None
    try:
        from zephyr.llm_security.protocol import SecurityDecision
        result = asyncio.run(
            gw.scan_agent_action(
                text=content,
                tool_name="a2a_communication",
                tool_params={"from_agent": from_agent, "to_agent": to_agent},
                metadata={"source": "a2a_governance"},
            )
        )
        if result.decision in (SecurityDecision.DENY, SecurityDecision.BLOCK):
            return result.blocked_by or "lsg_agent_scan"
    except RuntimeError:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return None
            result = loop.run_until_complete(
                gw.scan_agent_action(
                    text=content,
                    tool_name="a2a_communication",
                    tool_params={"from_agent": from_agent, "to_agent": to_agent},
                    metadata={"source": "a2a_governance"},
                )
            )
            from zephyr.llm_security.protocol import SecurityDecision
            if result.decision in (SecurityDecision.DENY, SecurityDecision.BLOCK):
                return result.blocked_by or "lsg_agent_scan"
        except Exception:
            pass
    except Exception:
        pass
    return None


@dataclass
class A2AGovernanceRecord:
    agent_pair: tuple[str, str]
    action: str
    granted: bool = False
    escalation_level: str = ""
    audit_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class GovernanceAdapter:
    """A2A GovernanceAdapter — G-CT-008 消费端.

    Phase 4 激活后，A2A 通信对在执行前 MUST 通过此适配器：
    1. verify_a2a_pair()  — 验证 Agent 对是否合法
    2. escalate_if_needed() — 必要时触发升级
    """

    ALLOWED_PAIRS: set[tuple[str, str]] = {
        ("orchestrator", "worker"),
        ("reviewer", "builder"),
        ("auditor", "any"),
    }

    def verify_pair(self, agent_a: str, agent_b: str, content: str = "") -> A2AGovernanceRecord:
        pair = (agent_a, agent_b)
        reverse = (agent_b, agent_a)
        granted = pair in self.ALLOWED_PAIRS or reverse in self.ALLOWED_PAIRS

        lsg_blocked_by = None
        if content:
            lsg_blocked_by = _lsg_scan_a2a_sync(agent_a, agent_b, content)
        if lsg_blocked_by:
            granted = False

        return A2AGovernanceRecord(
            agent_pair=(agent_a, agent_b),
            action="verify_pair",
            granted=granted,
            metadata={
                "allowed_pairs": list(self.ALLOWED_PAIRS),
                "lsg_blocked_by": lsg_blocked_by,
            },
        )

    def escalate_if_needed(
        self, record: A2AGovernanceRecord, severity: str = "WARN"
    ) -> A2AGovernanceRecord:
        if not record.granted:
            record.escalation_level = severity
        return record

    def audit_communication(
        self, record: A2AGovernanceRecord, session_id: str = ""
    ) -> A2AGovernanceRecord:
        record.audit_id = f"a2a-{hash(record.agent_pair)}-{session_id}"
        return record
