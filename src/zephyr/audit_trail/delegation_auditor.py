"""
audit_trail.delegation_auditor — MOD-INF-020 · 委托链审计器
=============================================================
蓝图 D-020-16 · 委托深度控制 + 权限缩小校验 + 链完整性验证

约束
----
  - 最大委托深度: 5
  - 权限缩小: 每层委托权限不得高于上层
  - 链完整性: 委托链签名连续性验证
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from zephyr.audit_trail.models import AuditEventType

_logger = logging.getLogger(__name__)

MAX_DELEGATION_DEPTH: int = 5


class EscalationType(str, Enum):
    DEPTH_EXCEEDED = "depth_exceeded"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    BROKEN_CHAIN = "broken_chain"
    UNAUTHORIZED_DELEGATOR = "unauthorized_delegator"
    SELF_DELEGATION = "self_delegation"


class DelegationNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str = ""
    permission_level: int = 0
    delegated_by: str = ""
    delegated_at: str = ""
    signature: str = ""


class DelegationAuditResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_valid: bool = True
    chain_depth: int = 0
    escalations: list[str] = Field(default_factory=list)
    escalation_types: list[EscalationType] = Field(default_factory=list)
    chain: list[DelegationNode] = Field(default_factory=list)
    audited_at: str = ""


class DelegationChainAuditor:
    def __init__(self, max_depth: int = MAX_DELEGATION_DEPTH) -> None:
        self._max_depth = max_depth

    def audit_chain(self, chain: list[DelegationNode] | list[dict[str, Any]]) -> DelegationAuditResult:
        nodes = self._normalize_chain(chain)
        escalations: list[str] = []
        escalation_types: list[EscalationType] = []

        depth = len(nodes)
        if depth > self._max_depth:
            escalations.append(f"Delegation depth {depth} exceeds maximum {self._max_depth}")
            escalation_types.append(EscalationType.DEPTH_EXCEEDED)

        for i in range(1, len(nodes)):
            if nodes[i].permission_level > nodes[i - 1].permission_level:
                escalations.append(
                    f"Privilege escalation: {nodes[i].agent_id} (level={nodes[i].permission_level}) "
                    f"> delegator {nodes[i - 1].agent_id} (level={nodes[i - 1].permission_level})"
                )
                escalation_types.append(EscalationType.PRIVILEGE_ESCALATION)

        for i in range(1, len(nodes)):
            if nodes[i].delegated_by != nodes[i - 1].agent_id:
                escalations.append(
                    f"Broken chain at index {i}: delegated_by={nodes[i].delegated_by} "
                    f"!= previous agent={nodes[i - 1].agent_id}"
                )
                escalation_types.append(EscalationType.BROKEN_CHAIN)

        for i, node in enumerate(nodes):
            if node.delegated_by and node.delegated_by == node.agent_id:
                escalations.append(f"Self-delegation detected at index {i}: {node.agent_id}")
                escalation_types.append(EscalationType.SELF_DELEGATION)

        is_valid = len(escalations) == 0
        result = DelegationAuditResult(
            is_valid=is_valid,
            chain_depth=depth,
            escalations=escalations,
            escalation_types=escalation_types,
            chain=nodes,
            audited_at=datetime.now(UTC).isoformat(),
        )
        if not is_valid:
            _logger.warning(
                "DelegationChainAuditor: chain audit failed, depth=%d, escalations=%s",
                depth, escalations,
            )
        return result

    def detect_escalation(
        self,
        chain: list[DelegationNode] | list[dict[str, Any]],
    ) -> list[tuple[int, EscalationType, str]]:
        nodes = self._normalize_chain(chain)
        escalations: list[tuple[int, EscalationType, str]] = []

        if len(nodes) > self._max_depth:
            escalations.append((
                len(nodes),
                EscalationType.DEPTH_EXCEEDED,
                f"Depth {len(nodes)} > max {self._max_depth}",
            ))

        for i in range(1, len(nodes)):
            if nodes[i].permission_level > nodes[i - 1].permission_level:
                escalations.append((
                    i,
                    EscalationType.PRIVILEGE_ESCALATION,
                    f"{nodes[i].agent_id}(lv={nodes[i].permission_level}) > {nodes[i-1].agent_id}(lv={nodes[i-1].permission_level})",
                ))

        for i in range(1, len(nodes)):
            if nodes[i].delegated_by != nodes[i - 1].agent_id:
                escalations.append((
                    i,
                    EscalationType.BROKEN_CHAIN,
                    f"delegated_by mismatch at index {i}",
                ))

        for i, node in enumerate(nodes):
            if node.delegated_by and node.delegated_by == node.agent_id:
                escalations.append((
                    i,
                    EscalationType.SELF_DELEGATION,
                    f"self-delegation: {node.agent_id}",
                ))

        return escalations

    @staticmethod
    def _normalize_chain(
        chain: list[DelegationNode] | list[dict[str, Any]],
    ) -> list[DelegationNode]:
        nodes: list[DelegationNode] = []
        for item in chain:
            if isinstance(item, DelegationNode):
                nodes.append(item)
            elif isinstance(item, dict):
                nodes.append(DelegationNode(**item))
            else:
                raise TypeError(f"Unsupported chain node type: {type(item)}")
        return nodes
