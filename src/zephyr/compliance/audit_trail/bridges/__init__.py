# [A_module] module_id=MOD-CMP_bridges | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [TTL] permanent
"""
Audit Trail — MOD-INF-020

不可变审计追踪：所有Agent操作记录 + 异常检测。
G-CT-001 (RBAC->Audit), G-CT-002 (Audit->Rollback).
"""

from zephyr.gov_audit.bridges.audit_anomaly import AnomalyDetector, AnomalyEvent
from zephyr.gov_audit.bridges.audit_contracts import AuditWriter
from zephyr.gov_audit.bridges.audit_delegation_bridge import AuditDelegationBridge
from zephyr.gov_audit.bridges.audit_drift_bridge import BridgeResult, DriftBridge
from zephyr.gov_audit.bridges.audit_feedback_bridge import AuditFeedbackBridge
from zephyr.gov_audit.bridges.audit_tiered_storage_bridge import AuditTieredStorageBridge
from zephyr.gov_audit.bridges.audit_trust_bridge import AuditTrustBridge

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


def __getattr__(name: str):
    # __all__ 里的子模块名（如 audit_anomaly）实际位于 zephyr.governance.audit_trail.bridges.*，
    # 用 __getattr__ 按需 lazy 加载（替代已删除的 `from . import spec_auditor`）
    import importlib

    try:
        mod = importlib.import_module(f"zephyr.governance.audit_trail.bridges.{name}")
        globals()[name] = mod
        return mod
    except ImportError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
