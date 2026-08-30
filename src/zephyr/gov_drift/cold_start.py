# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.cold_start
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.gov_drift.drift_engine
# [CONSUMERS] src/zephyr/compliance/behavioral_auditor/__init__.py; src/zephyr/gov_drift/_infrastructure.py; src/zephyr/gov_drift/brain_integration.py; src/zephyr/integration/mcp/governance_server.py; tests/cold/test_cold_start.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 冷启动必须完整
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/cold/test_cold_start.py
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Cold Start Bootstrapper — 冷启动引导 §6.31。

init_dirs: 需要物理目录的模块先创建(temp/log/data/cache/checkpoints)
init_db: 需要空表的初始化DDL
detect_missing_env: 缺失的环境变量
first_scan_seed: 首次运行空目录时产生占位扫描
auto_config: 需要config但.env/config.yaml不存在建议

对标 blueprint.md §6.31。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root，类型注解 str
#   code: cold_start.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: required_vars 参数
#   fields: 参数 required_vars，类型注解 list[str] | None
#   code: cold_start.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① init_directories
#   name_en: init_directories
#   intro: 创建缺失的必需目录，返回已创建的目录相对路径列表。
#   desc: 创建缺失的必需目录，返回已创建的目录相对路径列表。；源码 L197-L208
#   inputs: project_root
#   outputs: list[str]
# - id: A2
#   name_zh: ② init_database
#   name_en: init_database
#   intro: 初始化 drift_events 数据库——创建目录、表、索引。
#   desc: 初始化 drift_events 数据库——创建目录、表、索引。；源码 L211-L230
#   inputs: project_root
#   outputs: bool
# - id: A3
#   name_zh: ③ detect_missing_env
#   name_en: detect_missing_env
#   intro: 检测缺失的环境变量，返回缺失变量名列表。
#   desc: 检测缺失的环境变量，返回缺失变量名列表。 可选参数 required_vars 允许调用方覆盖默认检测变量集 （与 gov_audit 旧版签名对齐，向后兼容无参调用）。；源码 L233-L244
#   inputs: required_vars
#   outputs: list[str]
# - id: A4
#   name_zh: ④ bootstrap
#   name_en: bootstrap
#   intro: bootstrap(project_root) 源码 L247-L268
#   desc: 源码 L247-L268
#   inputs: project_root
#   outputs: ColdStartResult
# - id: A5
#   name_zh: ⑤ session_entry_activate
#   name_en: session_entry_activate
#   intro: STEP 4.9: 每次 session 进入时触发的冷启动激活。
#   desc: STEP 4.9: 每次 session 进入时触发的冷启动激活。 1. 确保目录和DB存在 2. 触发 LIGHT 扫描 3. 检查预算状态；源码 L285-L305
#   inputs: project_root
#   outputs: ColdStartResult
#   （注：A5 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: list[str]
#   name_en: list[str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/compliance/behavioral_auditor/__init__.py; src/zephyr/gov_drift/_inf…
# - id: O2
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/compliance/behavioral_auditor/__init__.py; src/zephyr/gov_drift/_inf…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import logging
import os
import sqlite3
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

logger = logging.getLogger(__name__)

# 治本(2026-07-20): SSoT 收敛——本文件为 cold_start 协议唯一真源。
# 原 gov_audit/cold_start.py 重复定义 7 个同符号集
# (ColdStartResult/init_database/init_directories/DEFAULT_DB_PATH/DRIFT_EVENTS_SCHEMA/
# REQUIRED_DIRS/detect_missing_env)，已全部删除，BootstrapCache 保留在 gov_audit/cold_start.py
# （审计专用缓存，与 drift cold start 协议无关）。
# 原 gov_drift 版本 init_database 用 split("\\n\\n") 切 DDL 产生不完整 SQL 片段，
# 永远静默返回 False；DEFAULT_DB_PATH 用 DB_PATH 绝对路径导致 project_root 被忽略，
# test_default_db_path_is_under_data 与 test_creates_db_directory 失败。
# 现采用 gov_audit 版本的修复实现（已通过 19 个测试验证）。
__all__ = [
    "ColdStartResult",
    "DEFAULT_DB_PATH",
    "DRIFT_EVENTS_SCHEMA",
    "REQUIRED_DIRS",
    "REQUIRED_ENV_VARS",
    "bootstrap",
    "detect_missing_env",
    "init_database",
    "init_directories",
    "session_entry_activate",
]

REQUIRED_DIRS: Final[list[str]] = [
    "data/drift",
    "data/audit",
    "data/audit/evidence",
    "data/audit/reports",
    "data/checkpoints",
    "temp",
    "logs",
    "cache",
]


REQUIRED_ENV_VARS: Final[list[str]] = [
    "ZEPHYR_PROJECT_ROOT",
]


# 治本(2026-07-19): DEFAULT_DB_PATH 指向 data/drift/，使 init_database 创建 data/drift 目录
# （test_creates_db_directory 验证此点）。原值 str(DB_PATH) 是绝对路径，
# 会导致 test_default_db_path_is_under_data 失败 + project_root 被忽略。
DEFAULT_DB_PATH: Final[str] = "data/drift/drift.db"

# 治本(2026-07-19): DRIFT_EVENTS_SCHEMA 提供完整 SQL DDL（含 4 个索引）。
# 原版本在每行间插入空行 + init_database 用 split("\\n\\n") 切 DDL 产生不完整 SQL 片段，
# 导致 init_database 永远静默返回 False。现采用紧凑 DDL + split(";") 切分。
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
    """冷启动结果——记录目录创建、DB 初始化、环境变量检测、首次扫描等结果。"""

    dirs_created: list[str] = field(default_factory=list)
    db_initialized: bool = False
    missing_env: list[str] = field(default_factory=list)
    first_scan_triggered: bool = False
    warnings: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


def init_directories(project_root: str) -> list[str]:
    """创建缺失的必需目录，返回已创建的目录相对路径列表。"""
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
    """初始化 drift_events 数据库——创建目录、表、索引。"""
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


def detect_missing_env(required_vars: list[str] | None = None) -> list[str]:
    """检测缺失的环境变量，返回缺失变量名列表。

    可选参数 required_vars 允许调用方覆盖默认检测变量集
    （与 gov_audit 旧版签名对齐，向后兼容无参调用）。
    """
    vars_to_check = required_vars or REQUIRED_ENV_VARS
    missing: list[str] = []
    for var in vars_to_check:
        if not os.environ.get(var):
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
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            result.warnings.append(f"Cold-start scan exception: {exc}")

    return result


def _trigger_light_scan(project_root: str) -> bool:
    from zephyr.shared.utils.async_utils import run_sync

    from .drift_engine import ScanLevel, scan

    try:
        # 5.100.16 治本: 替换手动 new_event_loop + set_event_loop + run_until_complete，
        # 改用 canonical run_sync()——自动处理有无运行 loop 两种场景
        result = run_sync(scan(level=ScanLevel.LIGHT))
        return result.detectors_run > 0
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return False


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
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("session_entry_activate scan failed: %s", exc, exc_info=True)

    return result
