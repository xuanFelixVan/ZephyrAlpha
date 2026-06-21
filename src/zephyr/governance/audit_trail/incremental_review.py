# [A_module] module_id=MOD-GOV_incremental_review | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.governance.audit_trail
# [INVARIANTS] 不可变审计记录;密码学完整性;只追加
# [MODIFY-GUARD] docs/03_modules/_domain-governance/audit-trail/blueprint.md;src/zephyr/audit-trail/__init__.py
# [CONSUMERS] MOD-INF-027;MOD-INF-015;MOD-INF-010
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] IntegrityError;WriteError
# [TESTS] tests/test_audit_trail/

from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class ReviewChunk:
    level: str
    chunk_id: str
    time_budget_minutes: int = 30

REVIEW_DIMENSIONS: dict[str, str] = {
    "consistency": "语义割裂检测",
    "accuracy": "数字引用验证",
    "completeness": "context manifest字段全",
    "traceability": "正反向链路",
    "token_efficiency": "审查Token/成果",
    "no_regression": "无下降→对比上次",
}
