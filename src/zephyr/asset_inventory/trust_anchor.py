"""MOD-INF-026 §26 — 三重信任锚验证门 R20。

TripleTrustAnchorGate: Git clean + pytest green + audit continuity → trust level。
对标 TUF 信任根模型 + Bitcoin "不信任，验证" 原则。
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TrustLevel(str, Enum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    BROKEN = "BROKEN"


class TrustAnchorResult(BaseModel):
    git_ok: bool = False
    test_ok: bool = False
    audit_ok: bool = False
    trust_level: TrustLevel = TrustLevel.BROKEN
    recommendation: str = ""
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TripleTrustAnchorGate:

    SELF_SRC_SEARCH = "src/zephyr/asset_inventory/"
    MAX_AUDIT_GAP_HOURS = 24
    MAX_CACHE_AGE_MINUTES = 5

    def __init__(self, project_root: Path) -> None:
        self._root = project_root
        self._cache: Optional[TrustAnchorResult] = None

    def verify(self, force: bool = False) -> TrustAnchorResult:
        if not force and self._cache and self._cache_age_minutes() < self.MAX_CACHE_AGE_MINUTES:
            return self._cache

        git_ok = self._check_git_clean()
        test_ok = self._run_pytest()
        audit_ok = self._check_audit_continuity()

        trust_level = self._calculate_trust(git_ok, test_ok, audit_ok)

        self._cache = TrustAnchorResult(
            git_ok=git_ok,
            test_ok=test_ok,
            audit_ok=audit_ok,
            trust_level=trust_level,
            recommendation=self._recommend(trust_level),
        )
        return self._cache

    def _check_git_clean(self) -> bool:
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain", "--", self.SELF_SRC_SEARCH],
                capture_output=True, text=True, cwd=str(self._root),
                timeout=10,
            )
            return result.stdout.strip() == ""
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _run_pytest(self) -> bool:
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/asset_inventory/", "-q", "--tb=line", "-x"],
                capture_output=True, text=True, cwd=str(self._root),
                timeout=180,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _check_audit_continuity(self) -> bool:
        log_path = self._root / "data" / "reports" / "security_access_log.jsonl"
        if not log_path.exists():
            return True

        try:
            lines = log_path.read_text(encoding="utf-8").strip().split("\n")
            if not lines or all(l.strip() == "" for l in lines):
                return True

            if len(lines) < 2:
                return True

            import json
            timestamps: list[datetime] = []
            for line in lines:
                try:
                    obj = json.loads(line)
                    ts = obj.get("ts")
                    if ts:
                        timestamps.append(datetime.fromisoformat(ts))
                except (json.JSONDecodeError, ValueError):
                    continue

            if len(timestamps) < 2:
                return False

            timestamps.sort()
            max_gap_h = max(
                (timestamps[i + 1] - timestamps[i]).total_seconds() / 3600
                for i in range(len(timestamps) - 1)
            )
            return max_gap_h < self.MAX_AUDIT_GAP_HOURS
        except (OSError, PermissionError):
            return False

    @staticmethod
    def _calculate_trust(git_ok: bool, test_ok: bool, audit_ok: bool) -> TrustLevel:
        green_count = sum([git_ok, test_ok, audit_ok])
        if green_count == 3:
            return TrustLevel.FULL
        if green_count == 2:
            return TrustLevel.PARTIAL
        return TrustLevel.BROKEN

    @staticmethod
    def _recommend(trust_level: TrustLevel) -> str:
        if trust_level == TrustLevel.FULL:
            return "盘点器完全可信——正常运行：索引更新、对账、自愈全部开启"
        if trust_level == TrustLevel.PARTIAL:
            return "盘点器部分可信——正常运行，Dashboard 标记 trust_level=partial"
        return "盘点器不可信——停止自愈，仅作只读扫描+报告"

    def _cache_age_minutes(self) -> float:
        if not self._cache:
            return float("inf")
        return (datetime.now(timezone.utc) - self._cache.checked_at).total_seconds() / 60
