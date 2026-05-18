# [BLUEPRINT] MOD-INF-020 | 03_modules/l01_infrastructure/audit-trail/blueprint.md | §

# [MODULE] zephyr.audit_trail.log_rotation

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
audit_trail.log_rotation — MOD-INF-020 · 日志轮转管理器
========================================================
蓝图 D-020-02 · 按日期轮转审计日志

命名规则
--------
  audit-trail-2026-05-05.jsonl
  当日活跃日志: events.jsonl

特性
----
  - 按日期自动轮转
  - 保留历史日志文件
  - 支持查询已轮转日志
"""

from __future__ import annotations

import gzip
import json
import logging
import os
import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

_logger = logging.getLogger(__name__)

DEFAULT_AUDIT_DATA_DIR: Path = Path("data/audit_trail")
ACTIVE_LOG_NAME: str = "events.jsonl"
ROTATED_PREFIX: str = "audit-trail-"


class RotationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    original_file: str = ""
    rotated_file: str = ""
    entries_rotated: int = 0
    bytes_rotated: int = 0
    compressed: bool = False
    rotated_at: str = ""


class RotatedLogInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file_name: str = ""
    date: str = ""
    size_bytes: int = 0
    compressed: bool = False
    entry_count: int = 0


class LogRotationManager:
    def __init__(
        self,
        data_dir: Path | str = DEFAULT_AUDIT_DATA_DIR,
        compress_rotated: bool = True,
        max_rotated_days: int = 90,
    ) -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._compress_rotated = compress_rotated
        self._max_rotated_days = max_rotated_days
        self._active_log = self._data_dir / ACTIVE_LOG_NAME
        self._last_rotation_date: str = ""

    def rotate(self, force: bool = False) -> RotationRecord | None:
        today = datetime.now(UTC).strftime("%Y-%m-%d")

        if not force and self._last_rotation_date == today:
            return None

        if not self._active_log.exists():
            return None

        stat = self._active_log.stat()
        if stat.st_size == 0:
            return None

        entry_count = self._count_lines(self._active_log)
        rotated_name = f"{ROTATED_PREFIX}{today}.jsonl"
        rotated_path = self._data_dir / rotated_name

        if rotated_path.exists():
            rotated_name = f"{ROTATED_PREFIX}{today}-{datetime.now(UTC).strftime('%H%M%S')}.jsonl"
            rotated_path = self._data_dir / rotated_name

        shutil.move(str(self._active_log), str(rotated_path))

        compressed = False
        if self._compress_rotated:
            gz_path = Path(str(rotated_path) + ".gz")
            with open(rotated_path, "rb") as f_in:
                with gzip.open(gz_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            rotated_path.unlink()
            rotated_path = gz_path
            compressed = True

        self._active_log.touch()
        self._last_rotation_date = today

        record = RotationRecord(
            original_file=ACTIVE_LOG_NAME,
            rotated_file=rotated_path.name,
            entries_rotated=entry_count,
            bytes_rotated=stat.st_size,
            compressed=compressed,
            rotated_at=datetime.now(UTC).isoformat(),
        )
        _logger.info(
            "LogRotationManager: rotated %s -> %s (%d entries, %d bytes, compressed=%s)",
            ACTIVE_LOG_NAME, rotated_path.name, entry_count, stat.st_size, compressed,
        )
        return record

    def get_rotated_logs(self, since: str | None = None, until: str | None = None) -> list[RotatedLogInfo]:
        logs: list[RotatedLogInfo] = []
        if not self._data_dir.exists():
            return logs

        for f in sorted(self._data_dir.glob(f"{ROTATED_PREFIX}*")):
            date_str = self._extract_date(f.name)
            if not date_str:
                continue
            if since and date_str < since:
                continue
            if until and date_str > until:
                continue

            is_compressed = f.name.endswith(".gz")
            entry_count = 0
            try:
                if is_compressed:
                    with gzip.open(f, "rb") as gz:
                        entry_count = sum(1 for _ in gz)
                else:
                    entry_count = self._count_lines(f)
            except (OSError, gzip.BadGzipFile):
                pass

            logs.append(RotatedLogInfo(
                file_name=f.name,
                date=date_str,
                size_bytes=f.stat().st_size,
                compressed=is_compressed,
                entry_count=entry_count,
            ))

        return logs

    def cleanup_old_rotations(self) -> int:
        cutoff = datetime.now(UTC) - timedelta(days=self._max_rotated_days)
        deleted = 0
        for f in self._data_dir.glob(f"{ROTATED_PREFIX}*"):
            date_str = self._extract_date(f.name)
            if not date_str:
                continue
            try:
                file_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC)
                if file_date < cutoff:
                    f.unlink()
                    deleted += 1
                    _logger.info("LogRotationManager: deleted old rotation %s", f.name)
            except ValueError:
                continue
        return deleted

    @staticmethod
    def _extract_date(file_name: str) -> str | None:
        parts = file_name.replace(".jsonl", "").replace(".gz", "").split("-")
        if len(parts) >= 4:
            try:
                return f"{parts[2]}-{parts[3]}-{parts[4].split('-')[0]}"
            except IndexError:
                return None
        return None

    @staticmethod
    def _count_lines(path: Path) -> int:
        count = 0
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
        return count
