# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.symlink_checker
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_scanners.py; tests/audit/test_symlink_checker.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 软链接检查不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_symlink_checker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Symlink Integrity Checker — 软链接完整性检测 §6.29。





module_id: MOD-INF-023


broken_symlinks: 目标不存在或删除的文件


circular_symlinks: A->B->A


symlink_to_outside: VCS边界外的文件链接


dead_reference_pages: symlink引用已被清理的文档页面


对标 blueprint.md §6.29。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class SymlinkIssue:
    issue_id: str

    symlink_path: str

    target_path: str

    issue_type: str
    description: str = ""
    severity: str = "MAJOR"

    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))


def check_broken_symlinks(project_root: str) -> list[SymlinkIssue]:
    issues: list[SymlinkIssue] = []

    if not os.path.exists(project_root):
        return issues

    for root, dirs, files in os.walk(project_root):
        for name in dirs + files:
            full_path = os.path.join(root, name)

            if os.path.islink(full_path):
                target = os.readlink(full_path) if hasattr(os, "readlink") else ""

                if not target:
                    issues.append(
                        SymlinkIssue(
                            issue_id=f"symlink-broken-{name}",
                            symlink_path=full_path,
                            target_path=target,
                            issue_type="broken_symlink",
                            description=f"Symlink {full_path} has no target",
                        )
                    )

                elif not os.path.exists(target):
                    issues.append(
                        SymlinkIssue(
                            issue_id=f"symlink-broken-{name}",
                            symlink_path=full_path,
                            target_path=target,
                            issue_type="broken_symlink",
                            description=f"Symlink {name} -> {target} (missing)",
                        )
                    )

    return issues
