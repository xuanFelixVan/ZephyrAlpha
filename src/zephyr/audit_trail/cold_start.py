# [BLUEPRINT] MOD-INF-020 | 03_modules/l01_infrastructure/audit-trail/blueprint.md | §

# [MODULE] zephyr.audit_trail.cold_start

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
audit_trail.cold_start — MOD-INF-020 · 冷启动引导器
=====================================================
蓝图 D-020-13 · Git 历史扫描 + 审计轨迹引导 + 覆盖率估算

特性
----
  - Git Log 扫描: 从 git log 提取历史事件
  - 审计轨迹引导: 将 git 历史事件写入审计链
  - 覆盖率估算: 估算引导覆盖的事件比例
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from zephyr.audit_trail.models import AuditEventType

_logger = logging.getLogger(__name__)

DEFAULT_REPO_ROOT: Path = Path(".")


class GitEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    commit_hash: str = ""
    author: str = ""
    timestamp: str = ""
    message: str = ""
    files_changed: list[str] = Field(default_factory=list)
    insertions: int = 0
    deletions: int = 0


class BootstrapResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_commits_scanned: int = 0
    events_bootstrapped: int = 0
    events_skipped: int = 0
    coverage_ratio: float = 0.0
    git_events: list[GitEvent] = Field(default_factory=list)
    bootstrapped_at: str = ""


class CoverageEstimate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_git_commits: int = 0
    existing_audit_entries: int = 0
    estimated_coverage: float = 0.0
    gap_count: int = 0
    estimated_at: str = ""


class ColdStartBootstrapper:
    def __init__(
        self,
        repo_root: Path | str = DEFAULT_REPO_ROOT,
        max_commits: int = 1000,
    ) -> None:
        self._repo_root = Path(repo_root)
        self._max_commits = max_commits

    def bootstrap_from_git(
        self,
        since: str | None = None,
        until: str | None = None,
        author: str | None = None,
    ) -> BootstrapResult:
        git_events = self._scan_git_log(since=since, until=until, author=author)
        events_bootstrapped = 0
        events_skipped = 0

        try:
            from zephyr.audit_trail.bridge import write_to_core
            has_writer = True
        except ImportError:
            has_writer = False

        for git_event in git_events:
            audit_event = self._git_event_to_audit(git_event)
            if has_writer:
                result = write_to_core(AuditEventType.COLD_START_BOOTSTRAP.value, audit_event)
                if result:
                    events_bootstrapped += 1
                else:
                    events_skipped += 1
            else:
                events_bootstrapped += 1

        total = len(git_events)
        coverage = events_bootstrapped / total if total > 0 else 0.0

        _logger.info(
            "ColdStartBootstrapper: bootstrapped %d/%d events (%.1f%% coverage)",
            events_bootstrapped, total, coverage * 100,
        )
        return BootstrapResult(
            total_commits_scanned=total,
            events_bootstrapped=events_bootstrapped,
            events_skipped=events_skipped,
            coverage_ratio=round(coverage, 4),
            git_events=git_events,
            bootstrapped_at=datetime.now(UTC).isoformat(),
        )

    def estimate_coverage(self) -> CoverageEstimate:
        total_commits = self._count_git_commits()
        existing_entries = self._count_audit_entries()
        gap = max(0, total_commits - existing_entries)
        coverage = existing_entries / total_commits if total_commits > 0 else 0.0

        return CoverageEstimate(
            total_git_commits=total_commits,
            existing_audit_entries=existing_entries,
            estimated_coverage=round(coverage, 4),
            gap_count=gap,
            estimated_at=datetime.now(UTC).isoformat(),
        )

    def _scan_git_log(
        self,
        since: str | None = None,
        until: str | None = None,
        author: str | None = None,
    ) -> list[GitEvent]:
        cmd = [
            "git", "-C", str(self._repo_root),
            "log", f"--max-count={self._max_commits}",
            "--pretty=format:%H|%an|%aI|%s",
            "--numstat",
        ]
        if since:
            cmd.append(f"--since={since}")
        if until:
            cmd.append(f"--until={until}")
        if author:
            cmd.append(f"--author={author}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=30)
            if result.returncode != 0:
                _logger.warning("ColdStartBootstrapper: git log failed: %s", result.stderr)
                return []
        except (subprocess.TimeoutExpired, FileNotFoundError):
            _logger.exception("ColdStartBootstrapper: git log execution failed")
            return []

        return self._parse_git_log(result.stdout)

    def _parse_git_log(self, raw: str) -> list[GitEvent]:
        events: list[GitEvent] = []
        current_event: dict[str, Any] | None = None
        files_changed: list[str] = []
        insertions = 0
        deletions = 0

        for line in raw.split("\n"):
            if "|" in line and line.count("|") >= 3:
                if current_event is not None:
                    current_event["files_changed"] = files_changed
                    current_event["insertions"] = insertions
                    current_event["deletions"] = deletions
                    events.append(GitEvent(**current_event))
                parts = line.split("|", 3)
                current_event = {
                    "commit_hash": parts[0].strip(),
                    "author": parts[1].strip(),
                    "timestamp": parts[2].strip(),
                    "message": parts[3].strip() if len(parts) > 3 else "",
                }
                files_changed = []
                insertions = 0
                deletions = 0
            elif current_event is not None and line.strip():
                parts = line.strip().split("\t")
                if len(parts) >= 3:
                    try:
                        insertions += int(parts[0]) if parts[0] != "-" else 0
                        deletions += int(parts[1]) if parts[1] != "-" else 0
                    except ValueError:
                        pass
                    files_changed.append(parts[2])

        if current_event is not None:
            current_event["files_changed"] = files_changed
            current_event["insertions"] = insertions
            current_event["deletions"] = deletions
            events.append(GitEvent(**current_event))

        return events

    def _count_git_commits(self) -> int:
        try:
            result = subprocess.run(
                ["git", "-C", str(self._repo_root), "rev-list", "--count", "HEAD"],
                capture_output=True, text=True, encoding="utf-8", timeout=10,
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass
        return 0

    def _count_audit_entries(self) -> int:
        event_log = Path("data/audit_trail/events.jsonl")
        if not event_log.exists():
            return 0
        with open(event_log, "r", encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())

    @staticmethod
    def _git_event_to_audit(event: GitEvent) -> dict[str, Any]:
        return {
            "agent_id": event.author,
            "timestamp": event.timestamp,
            "action_type": "git_commit",
            "target_path": ", ".join(event.files_changed[:5]) if event.files_changed else "",
            "operation": "commit",
            "status": "completed",
            "metadata": {
                "commit_hash": event.commit_hash,
                "message": event.message[:200],
                "files_changed": len(event.files_changed),
                "insertions": event.insertions,
                "deletions": event.deletions,
            },
        }


ColdStartBackfill = ColdStartBootstrapper
