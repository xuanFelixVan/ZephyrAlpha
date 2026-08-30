# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.commit_quality_gate
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CommitQualityGate — Commit 质量基础设施。

依据: 蓝图 MOD-INF-021 §7 Phase 9 + §6.16 B118

每条 revert commit message 必须通过 Lint 检查:
    格式: "Rollback: <reason> to {commit_sha}"
    最小长度 20 字符 / 含 commit_sha / 首字母大写

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: commit_quality_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① CommitQualityGate
#   name_en: CommitQualityGate
#   intro: class CommitQualityGate 源码 L77-L112
#   desc: 公共方法（定义序）: lint_message, generate_revert_message；源码 L77-L112
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: CommitQualityGate
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class CommitQualityReport:
    hash: str
    message: str
    passes_lint: bool
    issues: list[str] = field(default_factory=list)


COMMIT_MSG_REQUIREMENTS = {
    "min_length": 20,
    "must_start_with": "Rollback",
    "must_contain_sha": True,
    "capitalize_first": True,
}


class CommitQualityGate:
    def __init__(self) -> None:
        pass

    def lint_message(self, commit_hash: str, message: str) -> CommitQualityReport:
        issues: list[str] = []

        if len(message.strip()) < COMMIT_MSG_REQUIREMENTS["min_length"]:
            issues.append(
                f"Message too short: {len(message.strip())} chars (min {COMMIT_MSG_REQUIREMENTS['min_length']})"
            )

        if not message.strip().startswith(COMMIT_MSG_REQUIREMENTS["must_start_with"]):
            issues.append("Must start with 'Rollback'")

        if COMMIT_MSG_REQUIREMENTS["capitalize_first"]:
            first_char = message.strip()[0] if message.strip() else ""
            if first_char and not first_char.isupper():
                issues.append("First letter must be uppercase")

        if COMMIT_MSG_REQUIREMENTS["must_contain_sha"]:
            sha_pattern = re.compile(r"[0-9a-f]{7,40}", re.IGNORECASE)
            if not sha_pattern.search(message):
                issues.append("Must contain commit SHA")

        return CommitQualityReport(
            hash=commit_hash,
            message=message,
            passes_lint=len(issues) == 0,
            issues=issues,
        )

    def generate_revert_message(self, commit_sha: str, reason: str = "") -> str:
        if reason:
            return f"Rollback: {reason} to {commit_sha}"
        return f"Rollback: automated revert to {commit_sha}"
