# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §5.2
# [MODULE] zephyr.governance.audit_trail.tiered_storage
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
# [A_module] module_id=MOD-GOV_tiered_storage | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["TieredStorage"]


class TieredStorage:
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
        age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
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
                except Exception as exc:
                    logger.error("Failed to migrate %s: %s", report_path, exc)
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


class MigrationRecord:
    def __init__(self, record_id: str = "", source_tier: str = "", target_tier: str = "", entry_id: str = "", timestamp: str | None = None, status: str = "pending") -> None:
        self.record_id = record_id
        self.source_tier = source_tier
        self.target_tier = target_tier
        self.entry_id = entry_id
        self.timestamp = timestamp
        self.status = status


class StorageTier:
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"
    ARCHIVE = "ARCHIVE"


class TierConfig:
    def __init__(self, tier: str = "", max_age_days: int = 365, max_size_mb: int = 1024, compression: bool = False) -> None:
        self.tier = tier
        self.max_age_days = max_age_days
        self.max_size_mb = max_size_mb
        self.compression = compression


class TieredStorageManager:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}

    def migrate(self, entry: Any, target_tier: str) -> MigrationRecord:
        return MigrationRecord(target_tier=target_tier, entry_id=getattr(entry, "entry_id", ""))

    def get_tier(self, entry_id: str) -> str:
        return StorageTier.HOT
