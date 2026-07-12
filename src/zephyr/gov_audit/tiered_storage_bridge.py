# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §12
# [MODULE] zephyr.gov_audit.tiered_storage_bridge
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.tiered_storage
# [CONSUMERS] audit-orchestrator.bridge; retention
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不实现存储逻辑; 仅桥接TieredStorage
# [MODIFY-GUARD] TieredStorage API变更时同步此桥接
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回空结果
# [TESTS] tests/audit-orchestrator/test_tiered_storage_bridge.py
# [A_module] module_id=MOD-GOV_tiered_storage_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["TieredStorageBridge"]


class TieredStorageBridge:
    def __init__(self) -> None:
        self._storage = None
        self._available = False
        try:
            from zephyr.gov_audit.tiered_storage import TieredStorage

            self._storage = TieredStorage()
            self._available = True
        except ImportError:
            logger.warning("TieredStorage not available")
        except Exception as exc:
            logger.warning("TieredStorage init failed: %s", exc, exc_info=True)

    def find_report(self, audit_id: str) -> dict[str, Any] | None:
        if not self._available or self._storage is None:
            return None
        try:
            report_path = self._storage.find_report(audit_id)
            if report_path is None:
                return None
            import json

            data = json.loads(report_path.read_text(encoding="utf-8"))
            data["_storage_tier"] = self._storage.classify(report_path)
            return data
        except Exception as exc:
            logger.error("TieredStorageBridge.find_report failed: %s", exc, exc_info=True)
            return None

    def migrate(self, dry_run: bool = False) -> dict[str, Any]:
        if not self._available or self._storage is None:
            return {"migrated": 0, "errors": 0, "available": False}
        try:
            result = self._storage.migrate(dry_run=dry_run)
            result["available"] = True
            return result
        except Exception as exc:
            logger.error("TieredStorageBridge.migrate failed: %s", exc, exc_info=True)
            return {"migrated": 0, "errors": 1, "available": False}

    def stats(self) -> dict[str, Any]:
        if not self._available or self._storage is None:
            return {"available": False}
        try:
            stats = self._storage.storage_stats()
            stats["available"] = True
            return stats
        except Exception as exc:
            logger.error("TieredStorageBridge.stats failed: %s", exc, exc_info=True)
            return {"available": False}

    def is_available(self) -> bool:
        return self._available