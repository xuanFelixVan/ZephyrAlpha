# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.cold_start
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.gov_drift.drift_engine
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_infrastructure.py; src/zephyr/governance/drift_detection/brain_integration.py (+2 more)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 冷启动必须完整
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_cold_start | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Cold Start Bootstrapper — 冷启动引导 §6.31。





module_id: MOD-INF-023


init_dirs: 需要物理目录的模块先创建(temp/log/data/cache/checkpoints)


init_db: 需要空表的初始化DLL


detect_missing_env: 缺失的环境变量


first_scan_seed: 首次运行空目录时产生占位扫描


auto_config: 需要config但.env/config.yaml不存在建议


对标 blueprint.md §6.31。"""

from __future__ import annotations

from typing import Final
import logging

logger = logging.getLogger(__name__)

import os
import sqlite3
from zephyr.governance.persistence.sqlite_schema import get_db_connection
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from zephyr.shared.io.paths import DB_PATH

REQUIRED_DIRS: Final[list[str]] = [
    "data/drift",
    "data/checkpoints",
    "temp",
    "logs",
    "cache",
]


REQUIRED_ENV_VARS: Final[list[str]] = [
    "ZEPHYR_PROJECT_ROOT",
]


DEFAULT_DB_PATH: Final[str] = str(DB_PATH)

DRIFT_EVENTS_SCHEMA: Final[str] = """


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


@dataclass
class ColdStartResult:
    dirs_created: list[str] = field(default_factory=list)

    db_initialized: bool = False

    missing_env: list[str] = field(default_factory=list)

    first_scan_triggered: bool = False

    warnings: list[str] = field(default_factory=list)

    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


def init_directories(project_root: str) -> list[str]:
    created: list[str] = []

    for d in REQUIRED_DIRS:
        full = os.path.join(project_root, d)

        if not os.path.exists(full):
            try:
                os.makedirs(full, exist_ok=True)

                created.append(d)

            except Exception as e:
                logger.warning("suppressed error in cold_start", exc_info=True)

    return created


def init_database(project_root: str) -> bool:
    db_path = os.path.join(project_root, DEFAULT_DB_PATH)

    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        conn = get_db_connection(db_path)

        try:
            cursor = conn.cursor()

            for statement in DRIFT_EVENTS_SCHEMA.strip().split("\n\n"):
                cursor.execute(statement)

            conn.commit()
        finally:
            # 5.144.9 修复: conn.close() 移入 finally, 防止 execute/commit 抛异常跳过 close
            conn.close()

        return True

    except Exception:
        return False


def detect_missing_env() -> list[str]:
    missing: list[str] = []

    for var in REQUIRED_ENV_VARS:
        if var not in os.environ:
            missing.append(var)

    return missing


def bootstrap(project_root: str) -> ColdStartResult:
    result = ColdStartResult()

    result.dirs_created = init_directories(project_root)

    result.db_initialized = init_database(project_root)

    result.missing_env = detect_missing_env()

    src_root = Path(project_root) / "src"

    if not src_root.exists() or not list(src_root.iterdir()):
        result.warnings.append("src/ directory appears empty — first scan seed recommended")

    if result.missing_env:
        result.warnings.append(f"Missing env vars: {result.missing_env} — create .env file with required values")

    if result.db_initialized:
        try:
            result.first_scan_triggered = _trigger_light_scan(project_root)

            if not result.first_scan_triggered:
                result.warnings.append("Cold-start LIGHT scan did not trigger — manual scan recommended")

        except Exception as exc:
            result.warnings.append(f"Cold-start scan exception: {exc}")

    return result


def _trigger_light_scan(project_root: str) -> bool:
    import asyncio

    from .drift_engine import ScanLevel, scan

    loop = asyncio.new_event_loop()

    try:
        asyncio.set_event_loop(loop)

        result = loop.run_until_complete(scan(level=ScanLevel.LIGHT))

        return result.detectors_run > 0

    except Exception:
        return False

    finally:
        loop.close()


def session_entry_activate(project_root: str) -> ColdStartResult:
    """STEP 4.9: 每次 session 进入时触发的冷启动激活。





    1. 确保目录和DB存在


    2. 触发 LIGHT 扫描


    3. 检查预算状态


    """

    result = ColdStartResult()

    result.dirs_created = init_directories(project_root)

    if init_database(project_root):
        result.db_initialized = True

    result.missing_env = detect_missing_env()

    try:
        result.first_scan_triggered = _trigger_light_scan(project_root)

    except Exception as e:
        logger.warning("suppressed error in cold_start", exc_info=True)

    return result
