# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.gov_audit.bridges.audit_anomaly
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
G-CT-002 Audit 异常检测器 — AnomalyEvent Pydantic V2 BaseModel.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: audit_anomaly.py
# 层: 算法
# - id: A1
#   name_zh: ① AnomalyDetector
#   name_en: AnomalyDetector
#   intro: 审计异常检测器.
#   desc: 审计异常检测器.；公共方法（定义序）: detect；源码 L69-L95
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: AnomalyDetector
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
