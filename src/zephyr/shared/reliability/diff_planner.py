# [BLUEPRINT] SRC-135 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.reliability.diff_planner
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.reliability.retry_handler
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_diff_planner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Diff Planner — 最小增量变更规划器。

依据：
    蓝图 MOD-TASK_SYSTEM §6.2.3 + v0.6.0
    任务卡 TASK-INF-0108 (Part 3/4)

功能：
    - 文件差异计算（行级 diff）
    - 最小改动集生成（只生成需变更的部分）
    - 与重写操作分离——避免全量无意义重写
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class DiffHunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    old_lines: list[str]
    new_lines: list[str]


@dataclass
class FileDiff:
    file_path: str
    exists: bool
    hunks: list[DiffHunk]
    added_lines: int = 0
    removed_lines: int = 0
    changed_lines: int = 0


@dataclass
class ChangePlan:
    files_to_create: list[str]
    files_to_modify: list[FileDiff]
    total_changes: int
    recommendation: str


class DiffPlanner:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def compute_diff(self, file_path: str, new_content: str) -> FileDiff:
        full_path = self._project_root / file_path

        if not full_path.exists():
            new_lines = new_content.splitlines(keepends=True)
            return FileDiff(
                file_path=file_path,
                exists=False,
                hunks=[
                    DiffHunk(
                        old_start=0,
                        old_count=0,
                        new_start=1,
                        new_count=len(new_lines),
                        old_lines=[],
                        new_lines=new_lines,
                    )
                ],
                added_lines=len(new_lines),
            )

        old_lines = full_path.read_text(encoding="utf-8").splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        diff = list(
            difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile=file_path,
                tofile=file_path,
            )
        )

        hunks = self._parse_diff_hunks(old_lines, new_lines)

        added = sum(h.new_count - h.old_count for h in hunks if h.new_count > h.old_count)
        removed = sum(h.old_count - h.new_count for h in hunks if h.old_count > h.new_count)

        return FileDiff(
            file_path=file_path,
            exists=True,
            hunks=hunks,
            added_lines=max(0, added),
            removed_lines=max(0, removed),
            changed_lines=len(diff),
        )

    def plan_changes(self, downstream_outputs: list[dict[str, Any]]) -> ChangePlan:
        files_to_create: list[str] = []
        files_to_modify: list[FileDiff] = []

        for output in downstream_outputs:
            path_str = output.get("path", "")
            full_path = self._project_root / path_str

            if not full_path.exists():
                files_to_create.append(path_str)
            else:
                files_to_modify.append(
                    FileDiff(
                        file_path=path_str,
                        exists=True,
                        hunks=[],
                    )
                )

        total = len(files_to_create) + len(files_to_modify)

        recommendation = "ALL_CREATE" if not files_to_modify else ("MIXED" if files_to_create else "ALL_MODIFY")

        return ChangePlan(
            files_to_create=files_to_create,
            files_to_modify=files_to_modify,
            total_changes=total,
            recommendation=recommendation,
        )

    @staticmethod
    def _parse_diff_hunks(old_lines: list[str], new_lines: list[str]) -> list[DiffHunk]:
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
        hunks: list[DiffHunk] = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue
            hunks.append(
                DiffHunk(
                    old_start=i1 + 1 if i1 < len(old_lines) else 0,
                    old_count=i2 - i1,
                    new_start=j1 + 1 if j1 < len(new_lines) else 0,
                    new_count=j2 - j1,
                    old_lines=list(old_lines[i1:i2]),
                    new_lines=list(new_lines[j1:j2]),
                )
            )

        return hunks
