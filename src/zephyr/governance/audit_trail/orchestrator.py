# [BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit-orchestrator/blueprint.md
# [MODULE] zephyr.governance.audit_trail.orchestrator
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_trail.writer; zephyr.governance.audit_trail.models; zephyr.governance.audit_trail.integrity; zephyr.governance.audit_trail.query; zephyr.governance.audit_trail.anomaly; zephyr.governance.audit_trail.indexer; zephyr.governance.audit_trail.self_monitor; zephyr.governance.audit_trail.bridge; zephyr.governance.audit_trail.contracts
# [CONSUMERS] tests.test_orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""[BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit-orchestrator/blueprint.md

[MODULE] zephyr.governance.audit_trail.orchestrator

[INVARIANTS] 审计编排器——MAPE-K 五层自治循环; 不直接实现审计写入/查询/验证

[MODIFY-GUARD] audit-orchestrator/blueprint.md; audit-trail/__init__.py

[CONSUMERS] 无外部消费者

[STABILITY] volatile

[SAFETY] M

[AI_AUTONOMY] ai_modifiable

[ERROR_CONTRACT] AuditOrchestratorError

[TESTS] tests/audit-orchestrator/

audit-orchestrator — MOD-INF-027 · 审计编排器
===============================================
MAPE-K 五层自治循环 / 四阶段闭环 / 三类审计分流 / 六层触发

代码已迁移回 audit-trail (MOD-INF-020)。本包仅保留重导出兼容层。
"""

from __future__ import annotations

from zephyr.governance.audit_trail.anomaly import AnomalyDetector, AnomalyResult, AnomalySignature
from zephyr.governance.audit_trail.bridge import write_to_core
from zephyr.governance.audit_trail.contracts import AuditWriter as ContractAuditWriter
from zephyr.governance.audit_trail.indexer import AuditIndexer
from zephyr.governance.audit_trail.integrity import IntegrityVerifier, MerkleAggregator
from zephyr.governance.audit_trail.models import (
    AuditEntryV1,
    AuditEventType,
    LamportClock,
    ProvenanceDepth,
    ProvenanceLevel,
    audit_entry_sort_key,
)
from zephyr.governance.audit_trail.query import AuditQuery
from zephyr.governance.audit_trail.self_monitor import SelfMonitor
from zephyr.governance.audit_trail.writer import AuditWriter, get_audit_writer

__all__ = [
    "AnomalyDetector",
    "AnomalyResult",
    "AnomalySignature",
    "AuditEntryV1",
    "AuditEventType",
    "AuditIndexer",
    "AuditQuery",
    "AuditWriter",
    "ContractAuditWriter",
    "IntegrityVerifier",
    "LamportClock",
    "MerkleAggregator",
    "ProvenanceDepth",
    "ProvenanceLevel",
    "SelfMonitor",
    "audit_entry_sort_key",
    "get_audit_writer",
    "write_to_core",
]
