# [A_module] module_id=MOD-SEC_deprecation_tracker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""[BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan-judge/blueprint.md | §deprecation

[MODULE] zephyr.security.access_control.orphan_judge.deprecation_tracker

[INVARIANTS] DeprecationRecord.expires_at = deprecated_at + ttl_days; storage in .aideprecations/ JSON; expired records eligible for removal

[MODIFY-GUARD] orphan-judge/blueprint.md; orphan-judge/__init__.py __all__

[CONSUMERS] orphan-judge.orphan_collector; circadian_scheduler._deprecation_scan

[STABILITY] evolving

[SAFETY] L

[AI_AUTONOMY] ai_modifiable

[ERROR_CONTRACT] DeprecationTrackerError on I/O failure; returns empty list on read failure

[TESTS] tests/orphan-judge/test_deprecation_tracker.py
"""
# [MODULE] zephyr.security.access_control.orphan_judge.deprecation_tracker
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

_DEPRECATIONS_DIR = ".aideprecations"


class DeprecationRecord(BaseModel):
    path: str
    deprecated_at: str
    ttl_days: int = 30
    expires_at: str
    reason: str = ""


class DeprecationTrackerError(Exception):
    pass


class DeprecationTracker:
    """废弃文件追踪器——标记和追踪废弃文件的生命周期。

    存储到 .aideprecations/ 目录下的 JSON 文件，
    每个废弃文件一条记录，过期后可批量移除。
    """

    def __init__(self, project_root: str | Path | None = None) -> None:
        if project_root is None:
            self._root = Path.cwd()
        else:
            self._root = Path(project_root).resolve()
        self._deprecations_dir = self._root / _DEPRECATIONS_DIR

    def deprecate(self, path: str, ttl_days: int = 30, reason: str = "") -> DeprecationRecord:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=ttl_days)
        record = DeprecationRecord(
            path=path,
            deprecated_at=now.isoformat(),
            ttl_days=ttl_days,
            expires_at=expires.isoformat(),
            reason=reason,
        )
        self._write_record(record)
        logger.info("Deprecated %s (TTL=%d days, expires=%s)", path, ttl_days, expires.isoformat())
        return record

    def check_deprecated(self) -> list[DeprecationRecord]:
        records = self._read_all_records()
        now = datetime.now(timezone.utc)
        expired: list[DeprecationRecord] = []
        for record in records:
            try:
                expires_dt = datetime.fromisoformat(record.expires_at)
                if expires_dt.tzinfo is None:
                    expires_dt = expires_dt.replace(tzinfo=timezone.utc)
                if now >= expires_dt:
                    expired.append(record)
            except (ValueError, TypeError):
                logger.warning("Invalid expires_at in record for %s", record.path)
        return expired

    def is_deprecated(self, path: str) -> bool:
        record_file = self._record_path(path)
        return record_file.exists()

    def remove_deprecated(self) -> list[str]:
        expired = self.check_deprecated()
        removed: list[str] = []
        for record in expired:
            record_file = self._record_path(record.path)
            try:
                if record_file.exists():
                    record_file.unlink()
                    removed.append(record.path)
                    logger.info("Removed deprecation record for %s", record.path)
            except OSError as exc:
                logger.error("Failed to remove deprecation record for %s: %s", record.path, exc)
        return removed

    def get_record(self, path: str) -> DeprecationRecord | None:
        record_file = self._record_path(path)
        if not record_file.exists():
            return None
        try:
            data = json.loads(record_file.read_text(encoding="utf-8"))
            return DeprecationRecord.model_validate(data)
        except (json.JSONDecodeError, OSError, ValueError) as exc:
            logger.error("Failed to read deprecation record for %s: %s", path, exc)
            return None

    def list_all(self) -> list[DeprecationRecord]:
        return self._read_all_records()

    def _write_record(self, record: DeprecationRecord) -> None:
        self._ensure_dir()
        record_file = self._record_path(record.path)
        tmp_path = f"{record_file}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(record.model_dump_json(indent=2))
            os.replace(tmp_path, record_file)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise DeprecationTrackerError(f"Permission denied writing deprecation record for {record.path}")
        except OSError as exc:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise DeprecationTrackerError(f"I/O error writing deprecation record for {record.path}: {exc}")

    def _read_all_records(self) -> list[DeprecationRecord]:
        if not self._deprecations_dir.exists():
            return []
        records: list[DeprecationRecord] = []
        for json_file in self._deprecations_dir.glob("*.json"):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                records.append(DeprecationRecord.model_validate(data))
            except (json.JSONDecodeError, OSError, ValueError) as exc:
                logger.error("Failed to read deprecation record %s: %s", json_file, exc)
        return records

    def _record_path(self, original_path: str) -> Path:
        safe_name = original_path.replace("/", "_").replace("\\", "_").replace(":", "_")
        return self._deprecations_dir / f"{safe_name}.json"

    def _ensure_dir(self) -> None:
        self._deprecations_dir.mkdir(parents=True, exist_ok=True)
