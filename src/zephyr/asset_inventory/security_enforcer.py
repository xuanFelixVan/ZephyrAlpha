"""MOD-INF-026 §20 — 安全隐私边界强制执行器。

SecurityFilter: 六不得铁律的机械化执行。
SecurityAccessLog: 审计追踪——盘点器每次扫描的文件级访问记录。
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

SECRET_FILENAME_PATTERNS: list[str] = [
    "*.env*", "*.secrets*", "*_key*", "*_token*",
    "*credentials*", "*.pem", "*.pkcs12",
]

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024

EXCLUDED_DIR_PARTS: set[str] = {".ailocks", "session-logs", ".git", "__pycache__", "node_modules"}


def _match_pattern(name: str, pattern: str) -> bool:
    import fnmatch
    return fnmatch.fnmatch(name, pattern)


class SecurityAccessRecord(BaseModel):
    ts: str
    action: str
    path: str
    reason: Optional[str] = None
    sha256: Optional[str] = None
    size: Optional[int] = None


class SecurityFilter:

    def __init__(self, max_size_bytes: int = MAX_FILE_SIZE_BYTES,
                 secret_patterns: Optional[list[str]] = None,
                 excluded_dirs: Optional[set[str]] = None) -> None:
        self._max_size = max_size_bytes
        self._secret_patterns = secret_patterns or SECRET_FILENAME_PATTERNS
        self._excluded_dirs = excluded_dirs or EXCLUDED_DIR_PARTS

    def should_scan(self, path: Path) -> tuple[bool, Optional[str]]:
        name = path.name.lower()

        for pattern in self._secret_patterns:
            if _match_pattern(name, pattern):
                return False, "matches_secret_pattern"

        parts = set(path.parts)
        if parts & self._excluded_dirs:
            return False, f"excluded_dir: {parts & self._excluded_dirs}"

        try:
            if path.is_symlink():
                return False, "is_symlink"
        except OSError:
            return False, "os_error"

        try:
            if path.stat().st_size > self._max_size:
                return False, f"over_size_limit: {path.stat().st_size} > {self._max_size}"
        except OSError:
            return False, "stat_error"

        return True, None


class SecurityAccessLogger:

    def __init__(self, log_dir: Path) -> None:
        self._log_dir = log_dir
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._log_path = self._log_dir / "security_access_log.jsonl"

    def log_skip(self, file_path: str, reason: str) -> None:
        self._append(SecurityAccessRecord(
            ts=datetime.now(timezone.utc).isoformat(),
            action="SCAN_SKIP",
            path=file_path,
            reason=reason,
        ))

    def log_ok(self, file_path: str, sha256: str, size: int) -> None:
        self._append(SecurityAccessRecord(
            ts=datetime.now(timezone.utc).isoformat(),
            action="SCAN_OK",
            path=file_path,
            sha256=sha256,
            size=size,
        ))

    def _append(self, record: SecurityAccessRecord) -> None:
        try:
            tmp = f"{self._log_path}.{os.getpid()}.tmp"
            line = record.model_dump_json(exclude_none=True) + "\n"
            with open(tmp, "a", encoding="utf-8") as f:
                f.write(line)
            os.replace(tmp, self._log_path)
        except OSError:
            pass

    def recent_skips(self, limit: int = 50) -> list[SecurityAccessRecord]:
        if not self._log_path.exists():
            return []
        records: list[SecurityAccessRecord] = []
        try:
            for line in self._log_path.read_text(encoding="utf-8").strip().split("\n"):
                try:
                    obj = json.loads(line)
                    if obj.get("action") == "SCAN_SKIP":
                        records.append(SecurityAccessRecord(**obj))
                except (json.JSONDecodeError, ValueError):
                    continue
        except OSError:
            pass
        return records[-limit:]
