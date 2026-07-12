# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.gov_audit.bridges.audit_contracts
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
# [A_module] module_id=MOD-GOV_contracts_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""G-CT-001 契约消费端 — Audit.write() 公共接口.

RBAC 权限判定完成后调用，写入不可变审计记录.
委托 zephyr.governance.audit_trail.writer.AuditWriter 真实实现——
append-only JSONL + SHA-256 哈希链 + HMAC-SHA256 + Lamport 时钟 + Merkle 聚合.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from zephyr.gov_audit.writer import AuditWriter as _CoreAuditWriter

_MODULE_WRITER: _CoreAuditWriter | None = None


def _get_writer() -> _CoreAuditWriter:
    global _MODULE_WRITER
    if _MODULE_WRITER is None:
        _MODULE_WRITER = _CoreAuditWriter()
    return _MODULE_WRITER


class AuditWriter:
    """审计记录写入器 — G-CT-001 消费端（委托核心实现）."""

    @staticmethod
    def write(
        agent_id: str,
        permission: str,
        resource: str,
        decision_basis: str,
        timestamp: str = "",
        session_id: str = "",
        granted: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """写入审计记录——不可变追加到核心审计链."""
        ts = timestamp or datetime.now(UTC).isoformat()
        event = {
            "event_type": "rbac_decision",
            "agent_id": agent_id,
            "permission": permission,
            "resource": resource,
            "decision_basis": decision_basis,
            "timestamp": ts,
            "session_id": session_id,
            "granted": granted,
            "metadata": metadata or {},
        }
        writer = _get_writer()
        chain_hash = writer.write(event)
        event["chain_hash"] = chain_hash
        return event
