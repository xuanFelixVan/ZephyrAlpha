# [BLUEPRINT] MOD-INF-023 | 03_modules/l01_infrastructure/drift-detector/blueprint.md | §

# [MODULE] zephyr.drift_detector.symlink_checker

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Symlink Integrity Checker — 软链接完整性检测 §6.29。

module_id: MOD-INF-023
broken_symlinks: 目标不存在或删除的文件
circular_symlinks: A→B→A
symlink_to_outside: VCS边界外的文件链接
dead_reference_pages: symlink引用已被清理的文档页面
对标 blueprint.md §6.29。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class SymlinkIssue:
    issue_id: str
    symlink_path: str
    target_path: str
    issue_type: str
    severity: str = "MAJOR"
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


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
                            description=f"Symlink {name} → {target} (missing)",
                        )
                    )

    return issues
