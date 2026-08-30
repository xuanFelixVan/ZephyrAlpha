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
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: record 参数
#   fields: 参数 record，类型注解 ChangeRecord
#   code: changelog_manager.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① append_change
#   name_en: append_change
#   intro: append_change(record) 源码 L104-L105
#   desc: 源码 L104-L105
#   inputs: record
#   outputs: 返回值
# - id: A2
#   name_zh: ② get_latest
#   name_en: get_latest
#   intro: get_latest() 源码 L108-L109
#   desc: 源码 L108-L109
#   inputs: 无参数
#   outputs: ChangeRecord | None
# - id: A3
#   name_zh: ③ latest_version
#   name_en: latest_version
#   intro: latest_version() 源码 L112-L113
#   desc: 源码 L112-L113
#   inputs: 无参数
#   outputs: str
#   （注：A3 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ChangeRecord | None
#   name_en: ChangeRecord | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# - id: O2
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

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
