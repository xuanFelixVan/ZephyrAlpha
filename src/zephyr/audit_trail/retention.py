"""
audit_trail.retention — MOD-INF-020 · 保留策略执行器
=====================================================
蓝图 D-020-12 · Dry-Run 模式 + Owner 审批 + 过期条目清理

策略
----
  - 默认保留期: 365 天
  - Dry-Run: 仅报告，不实际删除
  - Owner 审批: 删除操作需 Owner 确认
  - 分层保留: Hot/Warm/Cold 不同保留期
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from zephyr.audit_trail.models import AuditEventType

_logger = logging.getLogger(__name__)

DEFAULT_AUDIT_DATA_DIR: Path = Path("data/audit_trail")
DEFAULT_RETENTION_DAYS: int = 365


class RetentionPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hot_retention_days: int = 30
    warm_retention_days: int = 180
    cold_retention_days: int = 365
    require_owner_approval: bool = True


class ExpiredEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entry_id: str = ""
    timestamp: str = ""
    tier: str = ""
    age_days: int = 0
    reason: str = ""


class RetentionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dry_run: bool = True
    expired_count: int = 0
    deleted_count: int = 0
    skipped_count: int = 0
    expired_entries: list[ExpiredEntry] = Field(default_factory=list)
    enforced_at: str = ""


class RetentionEnforcer:
    def __init__(
        self,
        data_dir: Path | str = DEFAULT_AUDIT_DATA_DIR,
        policy: RetentionPolicy | None = None,
    ) -> None:
        self._data_dir = Path(data_dir)
        self._policy = policy or RetentionPolicy()
        self._approved_deletions: set[str] = set()

    def enforce(self, dry_run: bool = True, owner_approved: bool = False) -> RetentionResult:
        expired = self.get_expired()
        deleted_count = 0
        skipped_count = 0

        if not dry_run:
            if self._policy.require_owner_approval and not owner_approved:
                _logger.warning("RetentionEnforcer: deletion requires owner approval, skipping")
                return RetentionResult(
                    dry_run=False,
                    expired_count=len(expired),
                    deleted_count=0,
                    skipped_count=len(expired),
                    expired_entries=expired,
                    enforced_at=datetime.now(UTC).isoformat(),
                )

            deleted_count = self._delete_expired(expired)
            skipped_count = len(expired) - deleted_count

        _logger.info(
            "RetentionEnforcer: enforce(dry_run=%s) expired=%d deleted=%d skipped=%d",
            dry_run, len(expired), deleted_count, skipped_count,
        )
        return RetentionResult(
            dry_run=dry_run,
            expired_count=len(expired),
            deleted_count=deleted_count,
            skipped_count=skipped_count,
            expired_entries=expired,
            enforced_at=datetime.now(UTC).isoformat(),
        )

    def dry_run(self) -> RetentionResult:
        return self.enforce(dry_run=True)

    def get_expired(self) -> list[ExpiredEntry]:
        expired: list[ExpiredEntry] = []
        now = datetime.now(UTC)

        tier_days = {
            "hot": self._policy.hot_retention_days,
            "warm": self._policy.warm_retention_days,
            "cold": self._policy.cold_retention_days,
        }

        for tier_name, retention_days in tier_days.items():
            tier_dir = self._data_dir / tier_name
            if not tier_dir.exists():
                continue
            cutoff = now - timedelta(days=retention_days)
            for log_file in tier_dir.glob("*.jsonl*"):
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime, tz=UTC)
                age_days = (now - mtime).days
                if mtime < cutoff:
                    expired.append(ExpiredEntry(
                        entry_id=log_file.name,
                        timestamp=mtime.isoformat(),
                        tier=tier_name,
                        age_days=age_days,
                        reason=f"Exceeds {tier_name} retention of {retention_days} days",
                    ))

        return sorted(expired, key=lambda e: e.age_days, reverse=True)

    def approve_deletion(self, entry_ids: list[str]) -> None:
        self._approved_deletions.update(entry_ids)

    def _delete_expired(self, expired: list[ExpiredEntry]) -> int:
        deleted = 0
        for entry in expired:
            if entry.entry_id in self._approved_deletions or not self._policy.require_owner_approval:
                file_path = self._data_dir / entry.tier / entry.entry_id
                try:
                    if file_path.exists():
                        file_path.unlink()
                        deleted += 1
                        _logger.info("RetentionEnforcer: deleted %s from %s tier", entry.entry_id, entry.tier)
                except OSError:
                    _logger.exception("RetentionEnforcer: failed to delete %s", file_path)
            else:
                _logger.debug("RetentionEnforcer: skipping unapproved deletion of %s", entry.entry_id)
        return deleted
