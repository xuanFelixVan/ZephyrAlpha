# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §8
# [MODULE] zephyr.gov_audit.delegation_auditor
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.delegation_bridge
# [CONSUMERS] audit-orchestrator.integrity(完整性校验子流程)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 审计委托事件链完整性; 检测循环委托/深度溢出/死锁
# [MODIFY-GUARD] DelegationEngine API变更时同步此审计器
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 审计失败返回空结果
# [TESTS] tests/governance/audit/test_delegation_auditor.py
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Final

logger = logging.getLogger(__name__)

__all__ = [
    "DelegationAuditResult",
    "DelegationChainAuditor",
    "DelegationNode",
    "EscalationType",
    "MAX_DELEGATION_DEPTH",
]

MAX_DELEGATION_DEPTH: Final[int] = 5


class EscalationType(str, Enum):
    """委托链升级类型 -- str+Enum 使 == "string_value" 可用."""

    DEPTH_EXCEEDED = "depth_exceeded"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    BROKEN_CHAIN = "broken_chain"
    UNAUTHORIZED_DELEGATOR = "unauthorized_delegator"
    SELF_DELEGATION = "self_delegation"


@dataclass
class DelegationNode:
    """委托链节点 -- 对齐 test_delegation_auditor.py."""

    agent_id: str = ""
    permission_level: int = 0
    delegated_by: str = ""
    delegated_at: str = ""
    signature: str = ""


@dataclass
class DelegationAuditResult:
    """委托链审计结果 -- 对齐 test_delegation_auditor.py."""

    is_valid: bool = True
    chain_depth: int = 0
    escalations: list[tuple[int, EscalationType, str]] = field(default_factory=list)
    escalation_types: list[EscalationType] = field(default_factory=list)


class DelegationChainAuditor:
    """委托链审计器 -- 对齐 test_delegation_auditor.py.

    audit_chain(chain) accepts list[DelegationNode | dict], returns DelegationAuditResult.
    detect_escalation(chain) returns list[tuple[int, EscalationType, str]].
    """

    def __init__(self, max_depth: int = MAX_DELEGATION_DEPTH, config: dict[str, Any] | None = None) -> None:
        self.max_depth = max_depth
        self.config = config or {}

    def _normalize_chain(self, chain: list) -> list[DelegationNode]:
        nodes: list[DelegationNode] = []
        for item in chain:
            if isinstance(item, DelegationNode):
                nodes.append(item)
            elif isinstance(item, dict):
                nodes.append(DelegationNode(
                    agent_id=item.get("agent_id", ""),
                    permission_level=item.get("permission_level", 0),
                    delegated_by=item.get("delegated_by", ""),
                    delegated_at=item.get("delegated_at", ""),
                    signature=item.get("signature", ""),
                ))
            else:
                raise TypeError(
                    f"Chain element must be DelegationNode or dict, got {type(item).__name__}"
                )
        return nodes

    def detect_escalation(
        self, chain: list
    ) -> list[tuple[int, EscalationType, str]]:
        nodes = self._normalize_chain(chain)
        escalations: list[tuple[int, EscalationType, str]] = []

        for i, node in enumerate(nodes):
            if i > 0 and node.permission_level > nodes[i - 1].permission_level:
                escalations.append((
                    i,
                    EscalationType.PRIVILEGE_ESCALATION,
                    f"Node {i} permission_level={node.permission_level} > "
                    f"previous={nodes[i-1].permission_level}",
                ))

            if i >= self.max_depth:
                escalations.append((
                    i,
                    EscalationType.DEPTH_EXCEEDED,
                    f"Chain depth {i + 1} exceeds max_depth={self.max_depth}",
                ))

            if i > 0:
                prev = nodes[i - 1]
                if node.delegated_by and node.delegated_by != prev.agent_id:
                    escalations.append((
                        i,
                        EscalationType.BROKEN_CHAIN,
                        f"Node {i} delegated_by='{node.delegated_by}' != "
                        f"previous agent_id='{prev.agent_id}'",
                    ))
                if node.agent_id and node.agent_id == node.delegated_by:
                    escalations.append((
                        i,
                        EscalationType.SELF_DELEGATION,
                        f"Node {i} agent_id='{node.agent_id}' == delegated_by",
                    ))

        return escalations

    def audit_chain(self, chain: list) -> DelegationAuditResult:
        nodes = self._normalize_chain(chain)
        escalations = self.detect_escalation(nodes)
        escalation_types = list({esc[1] for esc in escalations})
        is_valid = len(escalations) == 0
        return DelegationAuditResult(
            is_valid=is_valid,
            chain_depth=len(nodes),
            escalations=escalations,
            escalation_types=escalation_types,
        )


# --- backward compat: old DelegationAuditor class ---

class DelegationAuditor:
    """Legacy delegation auditor -- backward compat."""

    def __init__(self) -> None:
        self._bridge = None
        self._available = False
        try:
            from zephyr.gov_audit.delegation_bridge import DelegationBridge

            self._bridge = DelegationBridge()
            self._available = self._bridge.is_available()
        except ImportError:
            logger.warning("DelegationBridge not available")
        except Exception as exc:  # noqa: BLE001
            logger.warning("DelegationBridge init failed: %s", exc, exc_info=True)

    def audit_delegation_chain(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        if not self._available:
            return {"status": "skipped", "reason": "DelegationBridge unavailable", "findings": []}

        findings: list[dict[str, Any]] = []
        visited: set[str] = set()
        chain: list[str] = []

        for event in events:
            chain.append(event.get("target", ""))
            target = event.get("target", "")

            if target in visited:
                findings.append({
                    "severity": "RED",
                    "type": "circular_delegation",
                    "target": target,
                    "detail": f"Circular delegation detected: {' -> '.join(chain)}",
                })

            visited.add(target)

            depth = event.get("depth", 0)
            if depth > MAX_DELEGATION_DEPTH:
                findings.append({
                    "severity": "YELLOW",
                    "type": "depth_overflow",
                    "target": target,
                    "depth": depth,
                    "detail": f"Delegation depth {depth} exceeds max {MAX_DELEGATION_DEPTH}",
                })

            if event.get("deadlock", False):
                findings.append({
                    "severity": "RED",
                    "type": "deadlock",
                    "target": target,
                    "detail": "Potential deadlock detected in delegation chain",
                })
                if self._bridge:
                    self._bridge.report_delegation_failure(target, "deadlock detected")

        return {
            "status": "completed",
            "events_scanned": len(events),
            "findings": findings,
            "pass": len([f for f in findings if f["severity"] == "RED"]) == 0,
        }

    def is_available(self) -> bool:
        return self._available
