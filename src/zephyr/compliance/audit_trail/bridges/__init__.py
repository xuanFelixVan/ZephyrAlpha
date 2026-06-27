# [A_module] module_id=MOD-CMP_bridges | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [TTL] task_bound
"""
Audit Trail — MOD-INF-020

不可变审计追踪：所有Agent操作记录 + 异常检测。
G-CT-001 (RBAC→Audit), G-CT-002 (Audit→Rollback).
"""

from zephyr.governance.audit_trail.bridges.anomaly import AnomalyDetector, AnomalyEvent
from zephyr.governance.audit_trail.bridges.contracts import AuditWriter
from zephyr.governance.audit_trail.bridges.delegation_bridge import AuditDelegationBridge
from zephyr.governance.audit_trail.bridges.drift_bridge import BridgeResult, DriftBridge
from zephyr.governance.audit_trail.bridges.feedback_bridge import AuditFeedbackBridge
from zephyr.governance.audit_trail.bridges.tiered_storage_bridge import AuditTieredStorageBridge
from zephyr.governance.audit_trail.bridges.trust_bridge import AuditTrustBridge

from . import spec_auditor

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
    "anomaly",
    "contracts",
    "delegation_bridge",
    "drift_bridge",
    "feedback_bridge",
    "spec_auditor",
    "tiered_storage_bridge",
    "trust_bridge",
]

__version__ = "0.1.0"
__module_id__ = "MOD-INF-020"
