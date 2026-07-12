# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.gov_audit.bridges.audit_anomaly
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-GOV_anomaly | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""G-CT-002 Audit 异常检测器 — AnomalyEvent Pydantic V2 BaseModel."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class AnomalyEvent(BaseModel):
    """审计异常事件 — G-CT-002 事件格式."""

    agent_id: str
    operation_signature: str
    resource_path: str
    severity: str = "WARN"
    event_type: str = "anomaly_detected"
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    session_id: str = ""
    detail: str = ""


class AnomalyDetector:
    """审计异常检测器."""

    _SUSPICIOUS_OPERATIONS: set[str] = {
        "delete",
        "truncate",
        "drop",
        "revoke",
        "sudo",
        "root",
    }

    def detect(self, audit_record: dict) -> AnomalyEvent | None:
        """检测审计记录中的异常操作签名."""
        permission = audit_record.get("permission", "").lower()
        granted = audit_record.get("granted", False)

        if permission in self._SUSPICIOUS_OPERATIONS and granted:
            return AnomalyEvent(
                agent_id=audit_record.get("agent_id", "unknown"),
                operation_signature=f"permission={permission}",
                resource_path=audit_record.get("resource", ""),
                severity="HIGH" if permission in {"delete", "truncate"} else "WARN",
                session_id=audit_record.get("session_id", ""),
                detail=f"Suspicious operation: {permission} on {audit_record.get('resource', '?')}",
            )
        return None
