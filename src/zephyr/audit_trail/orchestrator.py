"""[BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit-orchestrator/blueprint.md

[MODULE] zephyr.audit_trail.orchestrator

[INVARIANTS] 审计编排器——MAPE-K 五层自治循环; 不直接实现审计写入/查询/验证

[MODIFY-GUARD] audit-orchestrator/blueprint.md; audit_trail/__init__.py

[CONSUMERS] 无外部消费者

[STABILITY] volatile

[SAFETY] M

[AI_AUTONOMY] ai_modifiable

[ERROR_CONTRACT] AuditOrchestratorError

[TESTS] tests/audit_orchestrator/

audit_orchestrator — MOD-INF-027 · 审计编排器
===============================================
MAPE-K 五层自治循环 / 四阶段闭环 / 三类审计分流 / 六层触发

代码已迁移回 audit_trail (MOD-INF-020)。本包仅保留重导出兼容层。
"""

from __future__ import annotations

from zephyr.audit_trail.writer import AuditWriter, get_audit_writer
from zephyr.audit_trail.models import (
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
from zephyr.audit_trail.integrity import IntegrityVerifier, MerkleAggregator
from zephyr.audit_trail.query import AuditQuery
from zephyr.audit_trail.anomaly import AnomalyDetector, AnomalyResult, AnomalySignature
from zephyr.audit_trail.indexer import AuditIndexer
from zephyr.audit_trail.self_monitor import SelfMonitor
from zephyr.audit_trail.bridge import write_to_core
from zephyr.audit_trail.contracts import AuditWriter as ContractAuditWriter

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
