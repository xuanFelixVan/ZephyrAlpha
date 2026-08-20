# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §5.1
# [MODULE] zephyr.gov_audit.retention
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] audit-orchestrator.tiered_storage; log_rotation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 冷数据保留1年; 温数据保留90天; 热数据保留7天; logs档(MCP等.jsonl)保留30天; 不碰核心不可变链data/audit_trail/events.jsonl
# [MODIFY-GUARD] 保留策略变更必须同步 log_rotation.py + tiered_storage.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 清理失败返回空结果
# [TESTS] tests/audit-orchestrator/test_retention.py
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Final

from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__ = ["MCP_AUDIT_LOG_DIR", "RetentionPolicy", "ExpiredEntry", "RetentionResult", "RetentionEnforcer"]

MCP_AUDIT_LOG_DIR: Final[Path] = Path("logs/mcp_audit")


class RetentionPolicy:
    """保留策略（补全测试期望接口）。

    保留旧版 HOT/WARM/COLD/LOG_RETENTION_DAYS 类属性以兼容现有调用方。
    """

    HOT_RETENTION_DAYS = 7
    WARM_RETENTION_DAYS = 90
    COLD_RETENTION_DAYS = 365
    LOG_RETENTION_DAYS = 30

    def __init__(
        self,
        hot_retention_days: int = 30,
        warm_retention_days: int = 180,
        cold_retention_days: int = 365,
        require_owner_approval: bool = True,
    ) -> None:
        self.hot_retention_days = hot_retention_days
        self.warm_retention_days = warm_retention_days
        self.cold_retention_days = cold_retention_days
        self.require_owner_approval = require_owner_approval

    def _tier_dirs(self) -> list[tuple[str, int]]:
        return [
            ("hot", self.hot_retention_days),
            ("warm", self.warm_retention_days),
            ("cold", self.cold_retention_days),
        ]


class ExpiredEntry:
    def __init__(
        self,
        entry_id: str = "",
        tier: str = "",
        age_days: int = 0,
        reason: str = "",
    ) -> None:
        self.entry_id = entry_id
        self.tier = tier
        self.age_days = age_days
        self.reason = reason


class RetentionResult:
    def __init__(
        self,
        dry_run: bool = True,
        expired_count: int = 0,
        deleted_count: int = 0,
        skipped_count: int = 0,
        errors: list[str] | None = None,
    ) -> None:
        self.dry_run = dry_run
        self.expired_count = expired_count
        self.deleted_count = deleted_count
        self.skipped_count = skipped_count
        self.errors = errors if errors is not None else []


class RetentionEnforcer:
    """保留策略执行器（补全测试期望接口）。

    扫描 data_dir 下的 hot/warm/cold 子目录，识别过期文件并根据策略删除。
    require_owner_approval=True 时，删除需要显式 approve_deletion 才会执行。
    """

    def __init__(
        self,
        data_dir: Path | None = None,
        policy: RetentionPolicy | None = None,
    ) -> None:
        # 治本（AI-AUDIT12 路径SSoT收敛）：相对默认锚定 REPO_ROOT 真源。
        from zephyr.shared.io.paths import REPO_ROOT

        self._data_dir = Path(data_dir) if data_dir is not None else REPO_ROOT / "data" / "audit_history"
        self._policy = policy or RetentionPolicy()
        self._approved_deletions: set[str] = set()

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def approved_deletions(self) -> set[str]:
        """只读：approved_deletions（Stage 4 公共化）。"""
        return self._approved_deletions

    @approved_deletions.setter
    def approved_deletions(self, value):
        """写入：approved_deletions（Stage 4 公共化）。"""
        self._approved_deletions = value

    @property
    def policy(self):
        """只读：policy（Stage 4 公共化）。"""
        return self._policy

    @policy.setter
    def policy(self, value):
        """写入：policy（Stage 4 公共化）。"""
        self._policy = value

    def _iter_files(self) -> list[tuple[Path, str, int]]:
        result: list[tuple[Path, str, int]] = []
        for tier, retention_days in self._policy._tier_dirs():
            tier_dir = self._data_dir / tier
            if not tier_dir.exists():
                continue
            for f in tier_dir.glob("*"):
                if f.is_file():
                    result.append((f, tier, retention_days))
        return result

    def get_expired(self) -> list[ExpiredEntry]:
        expired: list[ExpiredEntry] = []
        now = now_utc()
        for f, tier, retention_days in self._iter_files():
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=UTC)
                age_days = (now - mtime).days
                if age_days > retention_days:
                    expired.append(
                        ExpiredEntry(
                            entry_id=f.name,
                            tier=tier,
                            age_days=age_days,
                            reason=f"Exceeds {tier} retention ({retention_days} days)",
                        )
                    )
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.error("Failed to stat %s: %s", f, exc, exc_info=True)
        expired.sort(key=lambda e: e.age_days, reverse=True)
        return expired

    def approve_deletion(self, entry_ids: list[str]) -> None:
        for entry_id in entry_ids:
            self._approved_deletions.add(entry_id)

    def dry_run(self) -> RetentionResult:
        expired = self.get_expired()
        return RetentionResult(
            dry_run=True,
            expired_count=len(expired),
            deleted_count=0,
            skipped_count=len(expired),
        )

    def enforce(self, dry_run: bool = False, owner_approved: bool = False) -> RetentionResult:
        expired = self.get_expired()
        deleted = 0
        skipped = 0
        errors: list[str] = []

        approval_required = self._policy.require_owner_approval
        can_delete = (not approval_required) or owner_approved

        for entry in expired:
            if not can_delete:
                skipped += 1
                continue
            if approval_required and entry.entry_id not in self._approved_deletions:
                skipped += 1
                continue
            if dry_run:
                skipped += 1
                continue
            file_path = self._data_dir / entry.tier / entry.entry_id
            try:
                if file_path.exists():
                    file_path.unlink()
                    deleted += 1
                else:
                    skipped += 1
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                errors.append(f"Failed to delete {entry.entry_id}: {exc}")
                skipped += 1

        return RetentionResult(
            dry_run=dry_run,
            expired_count=len(expired),
            deleted_count=deleted,
            skipped_count=skipped,
            errors=errors,
        )
