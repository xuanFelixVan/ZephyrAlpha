# [A_module] module_id=MOD-GOV_bridges | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [TTL] permanent
"""
Audit Trail — MOD-INF-020

不可变审计追踪：所有Agent操作记录 + 异常检测。
G-CT-001 (RBAC->Audit), G-CT-002 (Audit->Rollback).
"""

from zephyr.governance.audit_trail.bridges.audit_anomaly import AnomalyDetector, AnomalyEvent
from zephyr.governance.audit_trail.bridges.audit_contracts import AuditWriter
from zephyr.governance.audit_trail.bridges.audit_delegation_bridge import AuditDelegationBridge
from zephyr.governance.audit_trail.bridges.audit_drift_bridge import BridgeResult, DriftBridge
from zephyr.governance.audit_trail.bridges.audit_feedback_bridge import AuditFeedbackBridge
from zephyr.governance.audit_trail.bridges.audit_tiered_storage_bridge import AuditTieredStorageBridge
from zephyr.governance.audit_trail.bridges.audit_trust_bridge import AuditTrustBridge


__all__ = [
    "AnomalyDetector",
    "AnomalyEvent",
    "AuditDelegationBridge",
    "AuditFeedbackBridge",
    "AuditTieredStorageBridge",
    "AuditTrustBridge",
    "AuditWriter",
    "BridgeResult",
    "DriftBridge",
    "audit_anomaly",
    "audit_contracts",
    "audit_delegation_bridge",
    "audit_drift_bridge",
    "audit_feedback_bridge",
    "audit_tiered_storage_bridge",
    "audit_trust_bridge",
]

__version__ = "0.1.0"
__module_id__ = "MOD-INF-020"
