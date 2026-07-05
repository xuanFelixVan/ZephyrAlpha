# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §5.1
# [MODULE] zephyr.governance.audit_trail.retention
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] audit-orchestrator.tiered_storage; log_rotation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 冷数据保留1年; 温数据保留90天; 热数据保留7天
# [MODIFY-GUARD] 保留策略变更必须同步 log_rotation.py + tiered_storage.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 清理失败返回空结果
# [TESTS] tests/audit-orchestrator/test_retention.py
# [A_module] module_id=MOD-GOV_retention | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["RetentionPolicy"]


class RetentionPolicy:
    HOT_RETENTION_DAYS = 7
    WARM_RETENTION_DAYS = 90
    COLD_RETENTION_DAYS = 365

    def __init__(
        self,
        hot_dir: Path | None = None,
        warm_dir: Path | None = None,
        cold_dir: Path | None = None,
    ) -> None:
        self._hot_dir = Path(hot_dir or Path("data/audit_history"))
        self._warm_dir = Path(warm_dir or Path("data/audit_archive/warm"))
        self._cold_dir = Path(cold_dir or Path("data/audit_archive/cold"))

    def enforce(self, dry_run: bool = False) -> dict[str, Any]:
        result: dict[str, Any] = {"purged": 0, "errors": 0, "details": []}

        for tier_dir, max_days in [
            (self._hot_dir, self.HOT_RETENTION_DAYS),
            (self._warm_dir, self.WARM_RETENTION_DAYS),
            (self._cold_dir, self.COLD_RETENTION_DAYS),
        ]:
            if not tier_dir.exists():
                continue

            cutoff = datetime.now() - timedelta(days=max_days)
            for f in tier_dir.glob("*"):
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    if mtime < cutoff:
                        result["details"].append(
                            {
                                "file": f.name,
                                "tier": tier_dir.name,
                                "age_days": (datetime.now() - mtime).days,
                                "retention_days": max_days,
                            }
                        )
                        if not dry_run:
                            f.unlink()
                            result["purged"] += 1
                except Exception as exc:
                    logger.error("Failed to purge %s: %s", f, exc, exc_info=True)
                    result["errors"] += 1

        return result

    def audit_retention_compliance(self) -> dict[str, Any]:
        violations: list[dict[str, Any]] = []

        for tier_dir, max_days, tier_name in [
            (self._hot_dir, self.HOT_RETENTION_DAYS, "hot"),
            (self._warm_dir, self.WARM_RETENTION_DAYS, "warm"),
            (self._cold_dir, self.COLD_RETENTION_DAYS, "cold"),
        ]:
            if not tier_dir.exists():
                continue

            cutoff = datetime.now() - timedelta(days=max_days)
            for f in tier_dir.glob("*"):
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime < cutoff:
                    violations.append(
                        {
                            "file": f.name,
                            "tier": tier_name,
                            "age_days": (datetime.now() - mtime).days,
                            "retention_days": max_days,
                        }
                    )

        return {
            "compliant": len(violations) == 0,
            "violations": len(violations),
            "details": violations,
        }


class ExpiredEntry:
    def __init__(self, entry_id="", expired_at=None, reason=""):
        self.entry_id = entry_id
        self.expired_at = expired_at
        self.reason = reason


class RetentionEnforcer:
    def __init__(self, config=None):
        self.config = config or {}

    def enforce(self, entries, policy=None):
        expired = []
        return expired

    def get_expired(self, max_age_days=30):
        return []


class RetentionResult:
    def __init__(self, total_entries=0, expired_count=0, retained_count=0, errors=None):
        self.total_entries = total_entries
        self.expired_count = expired_count
        self.retained_count = retained_count
        self.errors = errors or []