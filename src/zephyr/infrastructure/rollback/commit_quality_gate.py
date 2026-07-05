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
# [A_module] module_id=MOD-INF_commit_quality_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CommitQualityGate — Commit 质量基础设施。

依据: 蓝图 MOD-INF-021 §7 Phase 9 + §6.16 B118

每条 revert commit message 必须通过 Lint 检查:
    格式: "Rollback: <reason> to {commit_sha}"
    最小长度 20 字符 / 含 commit_sha / 首字母大写
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
