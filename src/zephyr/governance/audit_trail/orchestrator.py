# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md
# [MODULE] zephyr.governance.audit_trail.orchestrator
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_trail.writer; zephyr.governance.audit_trail.models; zephyr.governance.audit_trail.integrity; zephyr.governance.audit_trail.query; zephyr.governance.audit_trail.anomaly; zephyr.governance.audit_trail.indexer; zephyr.governance.audit_trail.self_monitor; zephyr.governance.audit_trail.bridge; zephyr.governance.audit_trail.contracts
# [CONSUMERS] tests/governance/audit/test_orchestrator.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 兼容重导出层——不实现审计编排逻辑，仅 re-export audit_trail 子模块符号
# [MODIFY-GUARD] audit_trail/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/audit/test_orchestrator.py
# [TTL] task_bound
"""audit-orchestrator 兼容重导出层（ARCH-042 阶段4 修复双 MODULE）

历史：原 audit-orchestrator (MOD-INF-027) 实现 MAPE-K 五层自治循环。
代码已迁移回 audit-trail (MOD-INF-020)，本模块仅保留 re-export 兼容层。
移除 docstring 中的 [BLUEPRINT] MOD-INF-027 标签——双 MODULE 引起 SSoT 分裂。
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
