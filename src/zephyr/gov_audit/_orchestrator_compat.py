# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md
# [MODULE] zephyr.gov_audit._orchestrator_compat
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.writer; zephyr.gov_audit.models; zephyr.gov_audit.integrity; zephyr.gov_audit.query; zephyr.gov_audit.anomaly; zephyr.gov_audit.indexer; zephyr.gov_audit.self_monitor; zephyr.gov_audit.bridge; zephyr.gov_audit.contracts
# [CONSUMERS] tests/governance/audit/test_orchestrator.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 兼容重导出层——不实现审计编排逻辑，仅 re-export audit_trail 子模块符号
# [MODIFY-GUARD] audit_trail/_orchestrator_compat.py（自洽，不再依赖 __all__）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/audit/test_orchestrator.py
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

audit-orchestrator 兼容重导出层（ARCH-042 阶段4 修复双 MODULE，ARCH-043 Risk3 改名）

历史：原 audit-orchestrator (MOD-INF-027) 实现 MAPE-K 五层自治循环。
代码已迁移回 audit-trail (MOD-INF-020)，本模块仅保留 re-export 兼容层。
ARCH-043 Risk3：文件名 orchestrator.py 暗示是真正编排器，但实际是 compat 重导出层，
新 AI 可能在里面加编排逻辑。改名为 _orchestrator_compat.py 明确语义（_前缀=私有兼容层）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 审计子模块符号 模块导入
#   fields: gov_audit 9 个子模块（anomaly/bridge/contracts/indexer/integrity/models/query/self_monitor/writer）的类与函数
#   code: zephyr.gov_audit.* L27-42
# 层: 算法
# - id: A1
#   name_zh: ① 兼容重导出汇聚
#   name_en: _orchestrator_compat re-export
#   intro: 把 9 个子模块的 18 个符号原样转发，冒充旧 orchestrator 入口
#   desc: 集中 import AnomalyDetector/AuditWriter/MerkleAggregator/AuditQuery 等 18 符号并列入 __all__；不实现任何编排逻辑（原 MOD-INF-027 已迁回 audit-trail）
#   inputs: I1
#   outputs: 兼容命名空间
#   invariant: 兼容重导出层——不实现审计编排逻辑，仅 re-export
# 层: 输出
# - id: O1
#   name_zh: 兼容符号命名空间
#   name_en: compat namespace
#   intro: 旧代码 from gov_audit import X 的兼容入口，18 个符号一站可用
#   downstream: tests/governance/audit/test_orchestrator.py（[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
