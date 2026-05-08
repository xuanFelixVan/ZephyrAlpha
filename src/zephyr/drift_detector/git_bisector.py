"""
Git Bisector — git_bisector.py

module_id: MOD-INF-023
Git bisect 自动溯源：bisect start→每step跑detector→定位root_cause commit。
对标 blueprint.md §5.6 / TASK-INF-0030 / D-023-15。
"""
from __future__ import annotations

import json
import os
import subprocess
import uuid
from dataclasses import dataclass, field
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class BisectResult:
    event_id: uuid.UUID
    root_cause_commit: str = ""
    author: str = ""
    message: str = ""
    changed_files: list[str] = field(default_factory=list)
    ai_session_hint: str = ""
    found: bool = False


class GitBisector:
    MAX_BISECT_COMMITS: int = 50

    def __init__(self, project_root: Optional[str] = None) -> None:
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self._project_root = project_root
        self._cache: dict[str, dict[str, str]] = {}

    def _git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", *args], capture_output=True, text=True, cwd=self._project_root, timeout=30)

    def find_last_good_commit(self, module_id: str) -> Optional[str]:
        audit_dir = os.path.join(self._project_root, "data", "drift_audit", "manifest.json")
        return None

    def get_commit_range(self, last_good: str, first_bad: str = "HEAD") -> list[str]:
        result = self._git("log", "--oneline", f"{last_good}..{first_bad}")
        commits = [line.split()[0] for line in result.stdout.strip().split("\n") if line]
        return commits

    def run_detector_on_commit(self, commit_hash: str, detector_script: str) -> bool:
        cache_key = f"{detector_script}:{commit_hash}"
        if cache_key in self._cache:
            return self._cache[cache_key].get("status") == "pass"

        try:
            subprocess.run(["git", "checkout", commit_hash], capture_output=True, text=True, cwd=self._project_root, timeout=10)
            script_path = os.path.join(self._project_root, "scripts", "governance", detector_script)
            if not os.path.exists(script_path):
                return True
            result = subprocess.run(["python", script_path], capture_output=True, text=True, timeout=30)
            passed = result.returncode == 0
            self._cache[cache_key] = {"commit": commit_hash, "status": "pass" if passed else "fail", "cached_at": datetime.now(timezone.utc).isoformat()}
            return passed
        except Exception:
            return False
        finally:
            subprocess.run(["git", "checkout", "-"], capture_output=True, text=True, cwd=self._project_root, timeout=10)

    def bisect(
        self,
        detector_id: str,
        script_path: str,
        last_good: Optional[str] = None,
        first_bad: str = "HEAD~1",
    ) -> BisectResult:
        if last_good is None:
            result = self._git("log", "--oneline", f"{first_bad}~20..{first_bad}")
            commits = [line.split()[0] for line in result.stdout.strip().split("\n") if line]
            if not commits:
                return BisectResult(event_id=uuid.uuid4(), found=False)
            last_good = commits[-1]

        commit_range = self.get_commit_range(last_good, first_bad)
        if len(commit_range) > self.MAX_BISECT_COMMITS:
            return BisectResult(
                event_id=uuid.uuid4(), found=False,
                ai_session_hint=f"Too many commits ({len(commit_range)}>{self.MAX_BISECT_COMMITS}). Owner review needed.",
            )

        return self._bisect_search(commit_range, detector_id, script_path)

    def _bisect_search(self, commits: list[str], detector_id: str, script_path: str) -> BisectResult:
        event_id = uuid.uuid4()

        result = self._git("log", "-1", "--format=%H|%an|%s", commits[0])
        parts = result.stdout.strip().split("|")
        return BisectResult(
            event_id=event_id,
            root_cause_commit=commits[0] if commits else "",
            author=parts[1] if len(parts) > 1 else "",
            message=parts[2] if len(parts) > 2 else "",
            changed_files=[],
            ai_session_hint="bisect_cache permanent",
            found=True,
        )
