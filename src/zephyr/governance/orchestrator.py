# [A_module] module_id=MOD-UNK_orchestrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit-orchestrator/blueprint.md
# [MODULE] zephyr.governance.audit_trail.orchestrator
# [INVARIANTS] 审计编排器——MAPE-K 五层自治循环; 不直接实现审计写入/查询/验证
# [MODIFY-GUARD] audit-orchestrator/blueprint.md; audit-trail/__init__.py
# [CONSUMERS] 无外部消费者
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AuditOrchestratorError
# [TESTS] tests/audit-orchestrator/

"""
audit-orchestrator — MOD-INF-027 · 审计编排器
===============================================
MAPE-K 五层自治循环 / 四阶段闭环 / 三类审计分流 / 六层触发

代码已迁移回 audit-trail (MOD-INF-020)。本包仅保留重导出兼容层。
"""


from __future__ import annotations

from zephyr.governance.audit_trail.writer import AuditWriter, get_audit_writer
from zephyr.governance.audit_trail.models import (
    AuditEntryV1,
    AuditEventType,
    ProvenanceDepth,
    ProvenanceLevel,
    ProvenanceLight,
    ProvenanceStandard,
    ProvenanceFull,
    FileActionType,
    TaskAuditSummary,
    FileAuditDetail,
    LamportClock,
    audit_entry_sort_key,
    IntegrityReport,
    AuditChain,
    IntegrityRecord,
    AuditMetrics,
)
from zephyr.governance.integrity import IntegrityVerifier, MerkleAggregator
from zephyr.governance.audit_trail.query import AuditQuery
from zephyr.governance.audit_trail.anomaly import AnomalyDetector, AnomalyResult, AnomalySignature
from zephyr.governance.audit_trail.indexer import AuditIndexer
from zephyr.governance.audit_trail.self_monitor import SelfMonitor
from zephyr.governance.audit_trail.bridge import write_to_core
from zephyr.governance.audit_trail.contracts import AuditWriter as ContractAuditWriter

__all__ = [
    "AuditWriter",
    "get_audit_writer",
    "AuditEntryV1",
    "AuditEventType",
    "IntegrityVerifier",
    "MerkleAggregator",
    "AuditQuery",
    "AnomalyDetector",
    "AnomalyResult",
    "AnomalySignature",
    "AuditIndexer",
    "SelfMonitor",
    "write_to_core",
    "ContractAuditWriter",
    "ProvenanceDepth",
    "ProvenanceLevel",
    "LamportClock",
    "audit_entry_sort_key",
]
