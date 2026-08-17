# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §3.1
# [MODULE] zephyr.gov_audit.cold_start
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 100 Session冷启动共享单例缓存; 缓存不可变
# [MODIFY-GUARD] 缓存Key变更必须同步 indexer.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 缓存未命中返回空字典
# [TESTS] none
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
BootstrapCache — 审计冷启动共享单例缓存。

治本(2026-07-20): SSoT 收敛——本文件原含 7 个与 gov_drift/cold_start.py 重复的符号
(ColdStartResult/init_database/init_directories/DEFAULT_DB_PATH/DRIFT_EVENTS_SCHEMA/
REQUIRED_DIRS/detect_missing_env)，已全部删除，真源统一归 gov_drift/cold_start.py。
本文件仅保留 BootstrapCache（审计专用缓存，存储审计维度/最近报告/熔断状态等，
与 drift cold start 协议无关）。调用方 zephyr.gov_audit.__init__ lazy registry
仍指向本文件。
"""
from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import REPO_ROOT  # 路径真源（SSoT）
from zephyr.shared.io.serialization import dumps
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__ = ["BootstrapCache"]

# 治本（AI-AUDIT12 路径SSoT收敛）：相对默认锚定 REPO_ROOT 真源。
CACHE_DIR = REPO_ROOT / "data" / "audit_cache"
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
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("BootstrapCache load failed: %s", exc, exc_info=True)

        self._cache = {
            "version": "1.0",
            "loaded_at": "",
            "dimensions": {},
            "recent_reports": [],
            "circuit_breaker_status": {},
        }
        self._loaded = True
        return dict(self._cache)

    def get(self, key: str, default: object = None) -> object:
        if not self._loaded:
            self.load()
        return self._cache.get(key, default)

    def set(self, key: str, value: object) -> None:
        if not self._loaded:
            self.load()
        self._cache[key] = value

    def persist(self) -> bool:
        try:
            self._cache["loaded_at"] = now_utc().isoformat()
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            self._cache_path.write_text(
                dumps(self._cache, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            return True
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("BootstrapCache persist failed: %s", exc, exc_info=True)
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
