# [BLUEPRINT] MOD-INF-020 | 03_modules/l01_infrastructure/audit-trail/blueprint.md | §

# [MODULE] zephyr.audit_trail.contracts

# [INVARIANTS] audit contracts must not be bypassed

# [MODIFY-GUARD] writer.py; __init__.py

# [CONSUMERS] zephyr.audit_trail

# [STABILITY] evolving

# [SAFETY] H

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] ContractViolationError

# [TESTS]

from __future__ import annotations





from datetime import datetime, timezone


from typing import Any





from zephyr.audit_trail.writer import AuditWriter as _CoreAuditWriter
from zephyr.audit_trail.writer import get_audit_writer as _get_audit_writer





def _get_writer() -> _CoreAuditWriter:


    return _get_audit_writer()








class AuditWriter:


    """审计记录写入器 -- G-CT-001 消费端（委托核心实现）.

    推荐使用 bridge.write_to_core() 或 bridge.write_rbac_decision() 作为新代码入口。
    本类保留用于向后兼容。
    """





    @staticmethod


    def write(


        agent_id: str,


        permission: str,


        resource: str,


        decision_basis: str,


        event_type: str = "rbac_decision",


        timestamp: str = "",


        session_id: str = "",


        granted: bool = False,


        metadata: dict[str, Any] | None = None,


    ) -> dict[str, Any]:


        """写入审计记录——不可变追加到核心审计链."""


        ts = timestamp or datetime.now(timezone.utc).isoformat()


        event = {


            "event_type": event_type,


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


