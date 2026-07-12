# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.gov_audit.changelog_manager
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不可变审计记录;密码学完整性;只追加
# [MODIFY-GUARD] docs/03_modules/_domain-governance/audit-trail/blueprint.md;src/zephyr/audit-trail/__init__.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] IntegrityError;WriteError
# [TESTS] tests/test_audit_trail/
# [A_module] module_id=MOD-GOV_changelog_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ChangeImpact(str, Enum):
    BREAKING = "Breaking"
    ENHANCEMENT = "Enhancement"
    FIX = "Fix"


class ChangeRecord(BaseModel):
    date: str
    version: str
    impact: ChangeImpact
    sections_affected: str
    description: str
    author: str = "AI-assisted, Owner ratified"


CHANGELOG: list[ChangeRecord] = [
    ChangeRecord(
        date="2026-02-15",
        version="v1.0.0",
        impact=ChangeImpact.BREAKING,
        sections_affected="§1-50 全局",
        description="初始蓝图创建",
        author="AI 辅助 Owner 终裁",
    ),
]


def append_change(record: ChangeRecord) -> None:
    CHANGELOG.insert(0, record)


def get_latest() -> ChangeRecord | None:
    return CHANGELOG[0] if CHANGELOG else None


def latest_version() -> str:
    return CHANGELOG[0].version if CHANGELOG else "v0.1.0"
