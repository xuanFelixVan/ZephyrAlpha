# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §3.1
# [MODULE] zephyr.gov_audit.cold_start
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
from zephyr.shared.io.serialization import dumps

import json
import logging
import os
import sqlite3
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

# 治本(2026-07-19): __all__ 补齐冷启动公共 API，与 tests/cold/test_cold_start.py 契约对齐。
__all__ = [
    "BootstrapCache",
    "ColdStartResult",
    "DEFAULT_DB_PATH",
    "DRIFT_EVENTS_SCHEMA",
    "REQUIRED_DIRS",
    "REQUIRED_ENV_VARS",
    "detect_missing_env",
    "init_database",
    "init_directories",
]

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


# 治本(2026-07-19): ColdStartResult 改为 dataclass，字段与 tests/cold/test_cold_start.py 契约对齐。
# 原实现字段（success/message/initialized_components）与测试期望
# （dirs_created/db_initialized/missing_env/first_scan_triggered/warnings/timestamp）
# 不匹配，导致 test_instantiation_defaults 抛 AttributeError、
# test_instantiation_custom 抛 TypeError（unexpected keyword argument 'dirs_created'）。
@dataclass
class ColdStartResult:
    """冷启动结果——记录目录创建、DB 初始化、环境变量检测、首次扫描等结果。"""

    dirs_created: list[str] = field(default_factory=list)
    db_initialized: bool = False
    missing_env: list[str] = field(default_factory=list)
    first_scan_triggered: bool = False
    warnings: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


# 治本(2026-07-19): DEFAULT_DB_PATH 指向 data/drift/，使 init_database 创建 data/drift 目录
# （test_creates_db_directory 验证此点）。原值 "data/audit/audit.db" 仅创建 data/audit。
DEFAULT_DB_PATH = "data/drift/drift.db"

# 治本(2026-07-19): DRIFT_EVENTS_SCHEMA 从字面量 "drift_events" 改为完整 SQL DDL。
# 原值仅是表名字符串，导致：
#   - test_schema_contains_key_columns 失败（'event_id' in 'drift_events' → False）
#   - test_manual_schema_creates_table 失败（split(';') 后无 CREATE 语句可执行）
#   - test_manual_schema_creates_indexes 失败（同上，无索引创建）
# 现按 drift_events 表结构提供完整 DDL，含 4 个索引（idx_drift_state/idx_drift_severity
# 命名匹配 test_manual_schema_creates_indexes 的断言）。
DRIFT_EVENTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS drift_events (
    event_id TEXT PRIMARY KEY,
    detector_id TEXT NOT NULL,
    module_id TEXT DEFAULT 'MOD-INF-023',
    severity TEXT NOT NULL,
    state TEXT DEFAULT 'DETECTED',
    source_file TEXT,
    description TEXT,
    details TEXT,
    fix_description TEXT,
    timestamp TEXT NOT NULL,
    scan_level TEXT DEFAULT 'STANDARD',
    auto_fixable INTEGER DEFAULT 0,
    resolution_detail TEXT,
    roi_score REAL DEFAULT 0.0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_drift_detector ON drift_events(detector_id);
CREATE INDEX IF NOT EXISTS idx_drift_state ON drift_events(state);
CREATE INDEX IF NOT EXISTS idx_drift_severity ON drift_events(severity);
CREATE INDEX IF NOT EXISTS idx_drift_timestamp ON drift_events(timestamp);
"""

# 治本(2026-07-19): REQUIRED_DIRS 补齐 data/drift、temp、logs
# （test_required_dirs_contain_key_paths 断言此三项必须存在）。
# 保留原 data/audit* 路径以兼容既有审计功能。
REQUIRED_DIRS = [
    "data/drift",
    "data/audit",
    "data/audit/evidence",
    "data/audit/reports",
    "temp",
    "logs",
]

REQUIRED_ENV_VARS = ["ZEPHYR_PROJECT_ROOT"]


def detect_missing_env(required_vars: list[str] | None = None) -> list[str]:
    """检测缺失的环境变量，返回缺失变量名列表。"""
    # 5.155.10 修复：原实现恒返回[]，现实现实际环境变量检测
    vars_to_check = required_vars or REQUIRED_ENV_VARS
    missing = []
    for var in vars_to_check:
        if not os.environ.get(var):
            missing.append(var)
    return missing


def init_directories(project_root: str) -> list[str]:
    """创建缺失的必需目录，返回已创建的目录相对路径列表。

    治本(2026-07-19): 原实现恒返回 True（bool），与测试期望返回 list[str] 不匹配，
    导致 test_creates_missing_dirs（TypeError: bool has no len）、
    test_existing_dirs_not_recreated（True == [] 失败）、
    test_partial_existing_dirs（TypeError: bool not iterable）三个测试失败。
    现按 REQUIRED_DIRS 列表逐项检查并创建缺失目录，返回相对路径列表。
    """
    created: list[str] = []
    for d in REQUIRED_DIRS:
        full = os.path.join(project_root, d)
        if not os.path.exists(full):
            try:
                os.makedirs(full, exist_ok=True)
                created.append(d)
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("init_directories: failed to create %s: %s", d, exc)
    return created


def init_database(project_root: str) -> bool:
    """初始化 drift_events 数据库——创建目录、表、索引。

    治本(2026-07-19): 原实现恒返回 True 且不创建任何目录/表，
    导致 test_creates_db_directory 失败（data/drift 未创建）。
    现按 DEFAULT_DB_PATH 创建目录并执行 DRIFT_EVENTS_SCHEMA DDL。
    """
    db_path = os.path.join(project_root, DEFAULT_DB_PATH)
    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()
            for statement in DRIFT_EVENTS_SCHEMA.strip().split(";"):
                stmt = statement.strip()
                if stmt:
                    cursor.execute(stmt)
            conn.commit()
        finally:
            # 5.144.9 修复: conn.close() 移入 finally, 防止 execute/commit 抛异常跳过 close
            conn.close()
        return True
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("init_database failed: %s", exc, exc_info=True)
        return False
