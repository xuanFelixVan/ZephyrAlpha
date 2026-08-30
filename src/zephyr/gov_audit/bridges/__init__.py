# [A_module] module_id=MOD-GOV-bridges | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [TTL] permanent
"""
Audit Trail — MOD-INF-020

不可变审计追踪：所有Agent操作记录 + 异常检测。
G-CT-001 (RBAC->Audit), G-CT-002 (Audit->Rollback).

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: AnomalyDetector, AnomalyEvent, AuditWriter, AuditDelegationBridge, Br…
#   code: __init__.py import L37
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 AnomalyDetector, AnomalyEvent, AuditDelegationBridge, AuditFeedbackBridge,…
#   desc: __init__ import L37；__all__ 16 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（16 符号）
#   name_en: __all__
#   intro: AnomalyDetector, AnomalyEvent, AuditDelegationBridge, AuditFeedbackBridge, Audi…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
