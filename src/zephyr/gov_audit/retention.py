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
# [A_module] module_id=MOD-GOV_retention | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Final
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__ = ["MCP_AUDIT_LOG_DIR", "RetentionPolicy"]

# 5.37.12：MCP 审计日志目录（logs/mcp_audit/tools_call.jsonl）纳入保留策略覆盖
MCP_AUDIT_LOG_DIR: Final[Path] = Path("logs/mcp_audit")


class RetentionPolicy:
    HOT_RETENTION_DAYS = 7
    WARM_RETENTION_DAYS = 90
    COLD_RETENTION_DAYS = 365
    # 5.37.12：运行态审计日志（MCP 等 logs/ 下 .jsonl）保留期——独立档位，
    # 不套用 HOT(7d) 过短保留（审计问责需要更长窗口），不覆盖核心不可变链
    # data/audit_trail/events.jsonl（删除会破坏 hash chain）。
    LOG_RETENTION_DAYS = 30

    def __init__(
        self,
        hot_dir: Path | None = None,
        warm_dir: Path | None = None,
        cold_dir: Path | None = None,
        logs_dir: Path | None = None,
    ) -> None:
        self._hot_dir = Path(hot_dir or Path("data/audit_history"))
        self._warm_dir = Path(warm_dir or Path("data/audit_archive/warm"))
        self._cold_dir = Path(cold_dir or Path("data/audit_archive/cold"))
        # 5.37.12：默认覆盖 MCP 审计日志目录；传 logs_dir 可重定向（测试隔离）
        self._logs_dir = Path(logs_dir) if logs_dir is not None else MCP_AUDIT_LOG_DIR

    def _tier_dirs(self) -> list[tuple[Path, int, str]]:
        """保留档位清单（5.37.12：追加 logs 档；glob("*") 已覆盖 .json/.jsonl/.gz）。"""
        return [
            (self._hot_dir, self.HOT_RETENTION_DAYS, "hot"),
            (self._warm_dir, self.WARM_RETENTION_DAYS, "warm"),
            (self._cold_dir, self.COLD_RETENTION_DAYS, "cold"),
            (self._logs_dir, self.LOG_RETENTION_DAYS, "logs"),
        ]

    def enforce(self, dry_run: bool = False) -> dict[str, Any]:
        result: dict[str, Any] = {"purged": 0, "errors": 0, "details": []}

        for tier_dir, max_days, _tier_name in self._tier_dirs():
            if not tier_dir.exists():
                continue

            cutoff = now_utc() - timedelta(days=max_days)
            for f in tier_dir.glob("*"):
                if not f.is_file():
                    continue
                try:
                    # tz=UTC：与 now_utc() 同为 aware datetime，避免 naive/aware 比较 TypeError
                    mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=UTC)
                    if mtime < cutoff:
                        result["details"].append(
                            {
                                "file": f.name,
                                "tier": tier_dir.name,
                                "age_days": (now_utc() - mtime).days,
                                "retention_days": max_days,
                            }
                        )
                        if not dry_run:
                            f.unlink()
                            result["purged"] += 1
                except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                    logger.error("Failed to purge %s: %s", f, exc, exc_info=True)
                    result["errors"] += 1

        return result

    def audit_retention_compliance(self) -> dict[str, Any]:
        violations: list[dict[str, Any]] = []

        for tier_dir, max_days, tier_name in self._tier_dirs():
            if not tier_dir.exists():
                continue

            cutoff = now_utc() - timedelta(days=max_days)
            for f in tier_dir.glob("*"):
                if not f.is_file():
                    continue
                # tz=UTC：与 now_utc() 同为 aware datetime，避免 naive/aware 比较 TypeError
                mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=UTC)
                if mtime < cutoff:
                    violations.append(
                        {
                            "file": f.name,
                            "tier": tier_name,
                            "age_days": (now_utc() - mtime).days,
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