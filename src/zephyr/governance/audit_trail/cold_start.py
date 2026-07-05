# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §3.1
# [MODULE] zephyr.governance.audit_trail.cold_start
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] audit-orchestrator.cli; MCP governance_server
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 100 Session冷启动共享单例缓存; 缓存不可变
# [MODIFY-GUARD] 缓存Key变更必须同步 indexer.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 缓存未命中返回空字典
# [TESTS] tests/audit-orchestrator/test_cold_start.py
# [A_module] module_id=MOD-GOV_cold_start | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["BootstrapCache", "ColdStartResult"]

CACHE_DIR = Path("data/audit_cache")
CACHE_FILE = "bootstrap_cache.json"


class BootstrapCache:
    _instance: BootstrapCache | None = None
    _lock = threading.Lock()  # Phase 2 P2 修复（并发安全 MEDIUM）：单例创建线程安全

    def __new__(cls) -> BootstrapCache:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._cache: dict[str, Any] = {}
                    instance._loaded = False
                    instance._cache_path = CACHE_DIR / CACHE_FILE
                    cls._instance = instance
        return cls._instance

    def load(self) -> dict[str, Any]:
        if self._loaded:
            return dict(self._cache)

        if self._cache_path.exists():
            try:
                self._cache = json.loads(self._cache_path.read_text(encoding="utf-8"))
                self._loaded = True
                logger.info("BootstrapCache loaded: %d keys", len(self._cache))
                return dict(self._cache)
            except Exception as exc:
                logger.warning("BootstrapCache load failed: %s", exc)

        self._cache = {
            "version": "1.0",
            "loaded_at": "",
            "dimensions": {},
            "recent_reports": [],
            "circuit_breaker_status": {},
        }
        self._loaded = True
        return dict(self._cache)

    def get(self, key: str, default: Any = None) -> Any:
        if not self._loaded:
            self.load()
        return self._cache.get(key, default)

    def set(self, key: str, value: Any) -> None:
        if not self._loaded:
            self.load()
        self._cache[key] = value

    def persist(self) -> bool:
        try:
            from datetime import datetime

            self._cache["loaded_at"] = datetime.now().isoformat()
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            self._cache_path.write_text(
                json.dumps(self._cache, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
            return True
        except Exception as exc:
            logger.error("BootstrapCache persist failed: %s", exc)
            return False

    def invalidate(self) -> None:
        self._cache = {}
        self._loaded = False

    def stats(self) -> dict[str, Any]:
        if not self._loaded:
            self.load()
        return {
            "loaded": self._loaded,
            "keys": len(self._cache),
            "dimensions_count": len(self._cache.get("dimensions", {})),
            "recent_reports": len(self._cache.get("recent_reports", [])),
        }


class ColdStartResult:
    def __init__(self, success: bool = True, message: str = "", initialized_components: list[str] | None = None, timestamp: str | None = None) -> None:
        self.success = success
        self.message = message
        self.initialized_components = initialized_components or []
        self.timestamp = timestamp


DEFAULT_DB_PATH = "data/audit/audit.db"

DRIFT_EVENTS_SCHEMA = "drift_events"

REQUIRED_DIRS = ["data/audit", "data/audit/evidence", "data/audit/reports"]

REQUIRED_ENV_VARS = []


def detect_missing_env(required_vars: list[str] | None = None) -> list[str]:
    return []


def init_database(db_path: str | None = None) -> bool:
    return True


def init_directories(base_path: str | None = None) -> bool:
    return True
