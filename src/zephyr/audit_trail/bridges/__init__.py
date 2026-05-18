# [BLUEPRINT] MOD-INF-020 | 03_modules/l01_infrastructure/audit-trail/blueprint.md | §
"""
Audit Trail — MOD-INF-020

不可变审计追踪：所有Agent操作记录 + 异常检测。
G-CT-001 (RBAC→Audit), G-CT-002 (Audit→Rollback).
"""
from . import spec_auditor

from zephyr.audit_trail.bridges.contracts import AuditWriter
from zephyr.audit_trail.bridges.anomaly import AnomalyEvent, AnomalyDetector
from zephyr.audit_trail.bridges.drift_bridge import DriftBridge, BridgeResult
from zephyr.audit_trail.bridges.tiered_storage_bridge import AuditTieredStorageBridge
from zephyr.audit_trail.bridges.trust_bridge import AuditTrustBridge
from zephyr.audit_trail.bridges.feedback_bridge import AuditFeedbackBridge
from zephyr.audit_trail.bridges.delegation_bridge import AuditDelegationBridge

__all__ = [
    'anomaly', 'contracts', 'drift_bridge', 'spec_auditor', 'feedback_bridge',
    'tiered_storage_bridge', 'trust_bridge', 'delegation_bridge',
    'AuditWriter', 'AnomalyEvent', 'AnomalyDetector',
    'DriftBridge', 'BridgeResult', 'AuditTieredStorageBridge',
    'AuditTrustBridge', 'AuditFeedbackBridge', 'AuditDelegationBridge',
]


__version__ = "0.1.0"
__module_id__ = "MOD-INF-020"
