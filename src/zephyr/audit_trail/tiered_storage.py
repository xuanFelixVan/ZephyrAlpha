# [BLUEPRINT] MOD-INF-020 | 03_modules/l01_infrastructure/audit-trail/blueprint.md | §

# [MODULE] zephyr.audit_trail.tiered_storage

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
audit_trail.tiered_storage — MOD-INF-020 · 三层存储管理器
============================================================
蓝图 D-020-10 · Hot/Warm/Cold 分层存储 + 自动迁移

存储层级
--------
  Hot  : <=7 天  — JSONL 原始格式，高频查询
  Warm : 8-90 天 — gzip 压缩，低频查询
  Cold : >90 天  — 归档存储，仅审计/合规查询
"""

from __future__ import annotations

import gzip
import json
import logging
import shutil
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from zephyr.audit_trail.models import AuditEventType

_logger = logging.getLogger(__name__)

DEFAULT_AUDIT_DATA_DIR: Path = Path("data/audit_trail")


class StorageTier(str, Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class TierConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hot_days: int = 7
    warm_days: int = 90
    hot_dir: str = "hot"
    warm_dir: str = "warm"
    cold_dir: str = "cold"


class MigrationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_tier: StorageTier = StorageTier.HOT
    target_tier: StorageTier = StorageTier.WARM
    file_name: str = ""
    entries_migrated: int = 0
    bytes_before: int = 0
    bytes_after: int = 0
    migrated_at: str = ""


class TieredStorageManager:
    def __init__(
        self,
        data_dir: Path | str = DEFAULT_AUDIT_DATA_DIR,
        config: TierConfig | None = None,
    ) -> None:
        self._data_dir = Path(data_dir)
        self._config = config or TierConfig()
        self._hot_dir = self._data_dir / self._config.hot_dir
        self._warm_dir = self._data_dir / self._config.warm_dir
        self._cold_dir = self._data_dir / self._config.cold_dir
        for d in (self._hot_dir, self._warm_dir, self._cold_dir):
            d.mkdir(parents=True, exist_ok=True)

    def get_tier(self, event_timestamp: str) -> StorageTier:
        try:
            ts = datetime.fromisoformat(event_timestamp)
        except (ValueError, TypeError):
            return StorageTier.HOT
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=UTC)
        age = datetime.now(UTC) - ts
        if age.days <= self._config.hot_days:
            return StorageTier.HOT
        if age.days <= self._config.warm_days:
            return StorageTier.WARM
        return StorageTier.COLD

    def migrate(
        self,
        source_tier: StorageTier,
        target_tier: StorageTier,
        file_name: str | None = None,
    ) -> list[MigrationRecord]:
        records: list[MigrationRecord] = []
        src_dir = self._tier_dir(source_tier)
        dst_dir = self._tier_dir(target_tier)
        if not src_dir.exists():
            return records

        files = sorted(src_dir.glob("*.jsonl")) if source_tier == StorageTier.HOT else sorted(src_dir.glob("*.jsonl.gz"))
        if file_name:
            files = [f for f in files if f.name == file_name]

        for src_file in files:
            try:
                record = self._migrate_file(src_file, src_dir, dst_dir, source_tier, target_tier)
                if record is not None:
                    records.append(record)
            except Exception:
                _logger.exception("TieredStorageManager: failed to migrate %s", src_file)
        return records

    def auto_migrate(self) -> list[MigrationRecord]:
        records: list[MigrationRecord] = []
        now = datetime.now(UTC)

        hot_to_warm = self._find_expired_in_tier(
            self._hot_dir, "*.jsonl", now - timedelta(days=self._config.hot_days)
        )
        for src_file in hot_to_warm:
            try:
                record = self._migrate_file(src_file, self._hot_dir, self._warm_dir, StorageTier.HOT, StorageTier.WARM)
                if record is not None:
                    records.append(record)
            except Exception:
                _logger.exception("auto_migrate: hot->warm failed for %s", src_file)

        warm_to_cold = self._find_expired_in_tier(
            self._warm_dir, "*.jsonl.gz", now - timedelta(days=self._config.warm_days)
        )
        for src_file in warm_to_cold:
            try:
                record = self._migrate_file(src_file, self._warm_dir, self._cold_dir, StorageTier.WARM, StorageTier.COLD)
                if record is not None:
                    records.append(record)
            except Exception:
                _logger.exception("auto_migrate: warm->cold failed for %s", src_file)

        if records:
            _logger.info("TieredStorageManager: auto_migrate completed, %d files migrated", len(records))
        return records

    def _migrate_file(
        self,
        src_file: Path,
        src_dir: Path,
        dst_dir: Path,
        source_tier: StorageTier,
        target_tier: StorageTier,
    ) -> MigrationRecord | None:
        bytes_before = src_file.stat().st_size
        entries_count = 0
        dst_dir.mkdir(parents=True, exist_ok=True)

        if source_tier == StorageTier.HOT and target_tier == StorageTier.WARM:
            dst_file = dst_dir / (src_file.name + ".gz")
            with open(src_file, "rb") as f_in:
                with gzip.open(dst_file, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            entries_count = self._count_jsonl_lines(src_file)
            src_file.unlink()

        elif source_tier == StorageTier.WARM and target_tier == StorageTier.COLD:
            dst_file = dst_dir / src_file.name
            shutil.move(str(src_file), str(dst_file))
            with gzip.open(dst_file, "rb") as f:
                entries_count = sum(1 for _ in f)

        else:
            dst_file = dst_dir / src_file.name
            shutil.move(str(src_file), str(dst_file))
            entries_count = 0

        bytes_after = dst_file.stat().st_size if dst_file.exists() else 0
        record = MigrationRecord(
            source_tier=source_tier,
            target_tier=target_tier,
            file_name=src_file.name,
            entries_migrated=entries_count,
            bytes_before=bytes_before,
            bytes_after=bytes_after,
            migrated_at=datetime.now(UTC).isoformat(),
        )
        _logger.info(
            "TieredStorageManager: migrated %s %s->%s (%d entries, %d->%d bytes)",
            src_file.name, source_tier.value, target_tier.value,
            entries_count, bytes_before, bytes_after,
        )
        return record

    def _find_expired_in_tier(self, tier_dir: Path, pattern: str, cutoff: datetime) -> list[Path]:
        expired: list[Path] = []
        if not tier_dir.exists():
            return expired
        for f in tier_dir.glob(pattern):
            if f.stat().st_mtime < cutoff.timestamp():
                expired.append(f)
        return sorted(expired)

    def _tier_dir(self, tier: StorageTier) -> Path:
        mapping = {
            StorageTier.HOT: self._hot_dir,
            StorageTier.WARM: self._warm_dir,
            StorageTier.COLD: self._cold_dir,
        }
        return mapping[tier]

    @staticmethod
    def _count_jsonl_lines(path: Path) -> int:
        count = 0
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
        return count
