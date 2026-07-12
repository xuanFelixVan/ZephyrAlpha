# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.gov_audit.bridges.audit_delegation_bridge
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.writer
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_delegation_bridge_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Audit ↔ DelegationManager 委托链审计桥接.

蓝图 D-020-16 — 委托链审计（深度控制 + 权限缩小）。
集成 infrastructure/escalation_protocol/delegation_manager.py。
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

_logger = logging.getLogger(__name__)

_MAX_DELEGATION_DEPTH = 5


class AuditDelegationBridge:
    """审计↔委托链桥接器.

    将委托操作写入审计日志，
    并在委托深度超限或权限扩大时触发异常。
    """

    def record_delegation(
        self,
        from_agent: str,
        to_agent: str,
        task_id: str,
        capability: str = "",
        depth: int = 0,
    ) -> dict[str, Any]:
        """记录委托操作到审计日志.

        Args:
            from_agent: 委托发起方
            to_agent: 委托接收方
            task_id: 任务标识
            capability: 委托的能力
            depth: 当前委托深度

        Returns:
            审计记录字典
        """
        record = {
            "event_type": "delegation_create",
            "from_agent": from_agent,
            "to_agent": to_agent,
            "task_id": task_id,
            "capability": capability,
            "delegation_depth": depth,
            "timestamp": datetime.now(UTC).isoformat(),
            "provenance": "delegation_bridge",
        }

        try:
            from pathlib import Path

            from zephyr.gov_audit.writer import AuditWriter

            writer = AuditWriter(Path("data/audit-trail"))
            chain_hash = writer.write(record)
            record["chain_hash"] = chain_hash
            _logger.info(
                "Delegation audit: %s -> %s (depth=%d, task=%s)",
                from_agent,
                to_agent,
                depth,
                task_id,
            )
        except Exception:
            _logger.exception("Failed to persist delegation audit record")

        return record

    def check_depth_anomaly(self, depth: int, agent_id: str = "") -> dict[str, Any] | None:
        """检测委托深度异常.

        Args:
            depth: 当前委托深度
            agent_id: Agent 标识

        Returns:
            异常事件字典，或 None 如果深度正常
        """
        if depth >= _MAX_DELEGATION_DEPTH:
            return {
                "signature_id": "ANM-010",
                "severity": "CRITICAL",
                "agent_id": agent_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "details": {
                    "delegation_depth": depth,
                    "max_allowed": _MAX_DELEGATION_DEPTH,
                    "anomaly": "delegation_depth_exceeded",
                },
            }
        if depth >= _MAX_DELEGATION_DEPTH - 1:
            return {
                "signature_id": "ANM-010",
                "severity": "HIGH",
                "agent_id": agent_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "details": {
                    "delegation_depth": depth,
                    "max_allowed": _MAX_DELEGATION_DEPTH,
                    "anomaly": "delegation_depth_warning",
                },
            }
        return None

    def audit_delegation_chain(
        self,
        chain: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """审计整条委托链.

        Args:
            chain: 委托链列表，每项含 from_agent, to_agent, capability, depth

        Returns:
            异常事件列表
        """
        anomalies: list[dict[str, Any]] = []

        for i, step in enumerate(chain):
            depth = step.get("depth", i)
            anomaly = self.check_depth_anomaly(depth, step.get("to_agent", ""))
            if anomaly:
                anomalies.append(anomaly)

            from_cap = set(step.get("from_capabilities", []))
            to_cap = set(step.get("to_capabilities", []))
            if from_cap and to_cap and to_cap - from_cap:
                anomalies.append(
                    {
                        "signature_id": "ANM-005",
                        "severity": "CRITICAL",
                        "agent_id": step.get("to_agent", ""),
                        "timestamp": datetime.now(UTC).isoformat(),
                        "details": {
                            "anomaly": "privilege_escalation_via_delegation",
                            "escalated_capabilities": sorted(to_cap - from_cap),
                            "from_agent": step.get("from_agent", ""),
                            "to_agent": step.get("to_agent", ""),
                        },
                    }
                )

        return anomalies

    def verify_delegation_integrity(
        self,
        delegation_records: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """验证委托链完整性.

        Args:
            delegation_records: 审计日志中的委托记录列表

        Returns:
            {"valid": bool, "issues": list[str]}
        """
        issues: list[str] = []
        seen_pairs: set[str] = set()

        for rec in delegation_records:
            pair = f"{rec.get('from_agent', '')}->{rec.get('to_agent', '')}"
            if pair in seen_pairs:
                issues.append(f"重复委托: {pair}")
            seen_pairs.add(pair)

            depth = rec.get("delegation_depth", 0)
            if depth >= _MAX_DELEGATION_DEPTH:
                issues.append(f"委托深度超限: depth={depth} agent={rec.get('to_agent', '')}")

        return {"valid": len(issues) == 0, "issues": issues}
