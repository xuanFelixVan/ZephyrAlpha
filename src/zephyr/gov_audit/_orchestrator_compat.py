# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md
# [MODULE] zephyr.gov_audit._orchestrator_compat
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.writer; zephyr.gov_audit.models; zephyr.gov_audit.integrity; zephyr.gov_audit.query; zephyr.gov_audit.anomaly; zephyr.gov_audit.indexer; zephyr.gov_audit.self_monitor; zephyr.gov_audit.bridge; zephyr.gov_audit.contracts
# [CONSUMERS] tests/governance/audit/test_orchestrator.py
# [STARTUP] imported
# [MATURITY] compat
# [INVARIANTS] 兼容重导出层——不实现审计编排逻辑，仅 re-export audit_trail 子模块符号
# [MODIFY-GUARD] audit_trail/_orchestrator_compat.py（自洽，不再依赖 __all__）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/audit/test_orchestrator.py
# [TTL] permanent
"""audit-orchestrator 兼容重导出层（ARCH-042 阶段4 修复双 MODULE，ARCH-043 Risk3 改名）

历史：原 audit-orchestrator (MOD-INF-027) 实现 MAPE-K 五层自治循环。
代码已迁移回 audit-trail (MOD-INF-020)，本模块仅保留 re-export 兼容层。
ARCH-043 Risk3：文件名 orchestrator.py 暗示是真正编排器，但实际是 compat 重导出层，
新 AI 可能在里面加编排逻辑。改名为 _orchestrator_compat.py 明确语义（_前缀=私有兼容层）。
"""

from __future__ import annotations

from zephyr.gov_audit.anomaly import AnomalyDetector, AnomalyResult, AnomalySignature
from zephyr.gov_audit.bridge import write_to_core
from zephyr.gov_audit.contracts import AuditWriter as ContractAuditWriter
from zephyr.gov_audit.indexer import AuditIndexer
from zephyr.gov_audit.integrity import IntegrityVerifier, MerkleAggregator
from zephyr.gov_audit.models import (
    AuditEntryV1,
    AuditEventType,
    LamportClock,
    ProvenanceDepth,
    ProvenanceLevel,
    audit_entry_sort_key,
)
from zephyr.gov_audit.query import AuditQuery
from zephyr.gov_audit.self_monitor import SelfMonitor
from zephyr.gov_audit.writer import AuditWriter, get_audit_writer

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
