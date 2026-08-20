# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §5.2
# [MODULE] zephyr.gov_audit.tiered_storage
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] audit-orchestrator.writer; query
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 热数据在内存/SSD; 温数据在HDD; 冷数据仅索引; 不可跨层回迁
# [MODIFY-GUARD] 存储策略变更必须同步 tiered_storage_bridge.py + retention.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 存储失败返回False
# [TESTS] tests/audit-orchestrator/test_tiered_storage.py
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import gzip
import logging
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__ = ["TieredStorage", "StorageTier", "TierConfig", "MigrationRecord", "TieredStorageManager"]


class TieredStorage:
    """旧版分层存储（保留以兼容现有调用方）。"""

    HOT_DAYS = 7
    WARM_DAYS = 30

    def __init__(
        self,
        hot_dir: Path | None = None,
        warm_dir: Path | None = None,
        cold_dir: Path | None = None,
    ) -> None:
        self._hot_dir = Path(hot_dir or Path("data/audit_history"))
        self._warm_dir = Path(warm_dir or Path("data/audit_archive/warm"))
        self._cold_dir = Path(cold_dir or Path("data/audit_archive/cold"))
        for d in (self._hot_dir, self._warm_dir, self._cold_dir):
            d.mkdir(parents=True, exist_ok=True)

    def classify(self, path: Path) -> str:
        age = now_utc() - datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
        if age.days <= self.HOT_DAYS:
            return "hot"
        if age.days <= self.WARM_DAYS:
            return "warm"
        return "cold"

    def migrate(self, dry_run: bool = False) -> dict[str, Any]:
        result: dict[str, Any] = {"migrated": 0, "errors": 0, "details": []}

        for report_path in self._hot_dir.glob("*.json"):
            tier = self.classify(report_path)
            if tier == "hot":
                continue

            target_dir = self._warm_dir if tier == "warm" else self._cold_dir
            target_path = target_dir / report_path.name
            result["details"].append(
                {
                    "file": report_path.name,
                    "from": tier_from(report_path),
                    "to": tier,
                }
            )

            if not dry_run:
                try:
                    report_path.rename(target_path)
                    result["migrated"] += 1
                except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                    logger.error("Failed to migrate %s: %s", report_path, exc, exc_info=True)
                    result["errors"] += 1
            else:
                result["migrated"] += 1

        return result

    def storage_stats(self) -> dict[str, Any]:
        return {
            "hot_count": len(list(self._hot_dir.glob("*.json"))),
            "warm_count": len(list(self._warm_dir.glob("*.json"))),
            "cold_count": len(list(self._cold_dir.glob("*.json"))),
        }

    def find_report(self, audit_id: str) -> Path | None:
        for search_dir in (self._hot_dir, self._warm_dir, self._cold_dir):
            path = search_dir / f"{audit_id}.json"
            if path.exists():
                return path
        return None


def tier_from(path: Path) -> str:
    age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
    if age.days <= TieredStorage.HOT_DAYS:
        return "hot"
    if age.days <= TieredStorage.WARM_DAYS:
        return "warm"
    return "cold"


class StorageTier:
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class TierConfig:
    def __init__(
        self,
        hot_days: int = 7,
        warm_days: int = 90,
        hot_dir: str = "hot",
        warm_dir: str = "warm",
        cold_dir: str = "cold",
    ) -> None:
        self.hot_days = hot_days
        self.warm_days = warm_days
        self.hot_dir = hot_dir
        self.warm_dir = warm_dir
        self.cold_dir = cold_dir


class MigrationRecord:
    def __init__(
        self,
        source_tier: str = StorageTier.HOT,
        target_tier: str = StorageTier.WARM,
        file_name: str = "",
        entries_migrated: int = 0,
        timestamp: str | None = None,
    ) -> None:
        self.source_tier = source_tier
        self.target_tier = target_tier
        self.file_name = file_name
        self.entries_migrated = entries_migrated
        self.timestamp = timestamp or now_utc().isoformat()


class TieredStorageManager:
    """分层存储管理器（补全测试期望接口）。

    管理 hot/warm/cold 三层存储，支持基于时间的分层和迁移。
    """

    def __init__(
        self,
        data_dir: Path | None = None,
        config: TierConfig | None = None,
    ) -> None:
        # 治本（AI-AUDIT12 路径SSoT收敛）：相对默认锚定 REPO_ROOT 真源。
        from zephyr.shared.io.paths import REPO_ROOT

        self._data_dir = Path(data_dir) if data_dir is not None else REPO_ROOT / "data" / "audit_history"
        self._config = config or TierConfig()
        self._hot_dir = self._data_dir / self._config.hot_dir
        self._warm_dir = self._data_dir / self._config.warm_dir
        self._cold_dir = self._data_dir / self._config.cold_dir
        for d in (self._hot_dir, self._warm_dir, self._cold_dir):
            d.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def count_jsonl_lines(path: Path) -> int:
        try:
            with open(path, encoding="utf-8") as f:
                return sum((1 for line in f if line.strip()))
        except Exception:
            return 0

    def get_tier(self, timestamp: str | None) -> str:
        if not timestamp:
            return StorageTier.HOT
        try:
            ts = datetime.fromisoformat(timestamp)
        except (TypeError, ValueError):
            return StorageTier.HOT
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=UTC)
        age = now_utc() - ts
        if age.days <= self._config.hot_days:
            return StorageTier.HOT
        if age.days <= self._config.warm_days:
            return StorageTier.WARM
        return StorageTier.COLD

    def migrate(
        self,
        source_tier: str,
        target_tier: str,
        file_name: str | None = None,
    ) -> list[MigrationRecord]:
        source_dir = self._tier_dir(source_tier)
        target_dir = self._tier_dir(target_tier)
        if not source_dir.exists():
            return []

        records: list[MigrationRecord] = []
        files = [source_dir / file_name] if file_name else list(source_dir.glob("*"))
        for f in files:
            if not f.exists() or not f.is_file():
                continue
            try:
                if f.suffix == ".jsonl":
                    entries = self._count_jsonl_lines(f)
                    target_path = target_dir / f"{f.name}.gz"
                    with open(f, "rb") as src, gzip.open(target_path, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    f.unlink()
                else:
                    entries = 0
                    target_path = target_dir / f.name
                    f.rename(target_path)
                records.append(
                    MigrationRecord(
                        source_tier=source_tier,
                        target_tier=target_tier,
                        file_name=f.name,
                        entries_migrated=entries,
                    )
                )
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.error("Failed to migrate %s: %s", f, exc, exc_info=True)
        return records

    def auto_migrate(self) -> list[MigrationRecord]:
        records: list[MigrationRecord] = []
        if self._hot_dir.exists():
            now = now_utc()
            for f in self._hot_dir.glob("*"):
                if not f.is_file():
                    continue
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=UTC)
                    age_days = (now - mtime).days
                    if age_days > self._config.hot_days:
                        records.extend(self.migrate(StorageTier.HOT, StorageTier.WARM, file_name=f.name))
                except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                    logger.error("Failed to auto-migrate %s: %s", f, exc, exc_info=True)
        return records

    def _tier_dir(self, tier: str) -> Path:
        if tier == StorageTier.HOT:
            return self._hot_dir
        if tier == StorageTier.WARM:
            return self._warm_dir
        if tier == StorageTier.COLD:
            return self._cold_dir
        return self._hot_dir

    @staticmethod
    def _count_jsonl_lines(path: Path) -> int:
        """向后兼容 thin wrapper（Stage 4 公共化，反向层级）。"""
        return TieredStorageManager.count_jsonl_lines(path)
