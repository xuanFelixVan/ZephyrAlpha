# [A_module] module_id=MOD-SHARED-002 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SHARED-002 | docs/03_modules/_domain_shared_services/io_layer/blueprint.md
# [MODULE] zephyr.shared.io.sqlite_factory
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.io.paths
# [CONSUMERS] zephyr.governance.persistence.sqlite_schema; zephyr.shared.events.dlq; zephyr.infrastructure.*; zephyr.gov_drift.*
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 所有SQLite连接必须通过get_db_connection工厂创建,确保PRAGMA基线一致
# [MODIFY-GUARD] governance/persistence/sqlite_schema.py re-export shim
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] sqlite3.Error 透传
# [TESTS] tests/db/test_db_auto_ops.py
# [TTL] permanent

"""


SQLite 连接工厂真源（SSoT）

提供统一的 SQLite 连接工厂函数，确保所有 SQLite 连接都应用一致的 PRAGMA 基线
（KBG-0030 §4.3：WAL/synchronous/foreign_keys/busy_timeout/temp_store/wal_autocheckpoint）。

[SSoT] get_db_connection / _apply_pragmas / _PRAGMAS 的 canonical 文件。
governance/persistence/sqlite_schema.py 为 re-export shim（保持向后兼容）。

治本(2026-07-06): 从 governance/persistence/sqlite_schema.py 迁移到 shared/io/sqlite_factory.py，
消除 shared/ 和 infrastructure/ 层对 governance/ 的逆向依赖（5.133.7 专项工程）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 数据库文件路径 db_path
#   fields: Path|str 可选, 默认 DB_PATH(governance.db)
#   code: get_db_connection(db_path) 默认 zephyr.shared.io.paths.DB_PATH
# - id: I2
#   name: 连接参数
#   fields: check_same_thread(默认False允许跨线程读) + timeout(busy等待秒数,默认30.0)
#   code: get_db_connection 关键字参数
# 层: 算法
# - id: A1
#   name_zh: ① SQLite连接创建
#   name_en: get_db_connection
#   intro: 统一入口建SQLite连接，自动提交模式+按列名取值的Row工厂，再套上PRAGMA基线
#   desc: 解析db_path(默认governance.db) → sqlite3.connect(isolation_level=None自动提交, check_same_thread, timeout=30s) → conn.row_factory=sqlite3.Row → _apply_pragmas
#   inputs: I1 I2
#   outputs: 配置完成的 sqlite3.Connection
#   invariant: 所有SQLite连接必须通过get_db_connection工厂创建,确保PRAGMA基线一致
# - id: A2
#   name_zh: ② PRAGMA基线应用 KBG-0030 §4.3
#   name_en: _apply_pragmas
#   intro: 对每条新连接刷6条PRAGMA，保证WAL模式、外键、忙等超时的行为全库一致
#   desc: 逐条execute: journal_mode=WAL / synchronous=NORMAL / foreign_keys=ON / busy_timeout=5000 / temp_store=MEMORY / wal_autocheckpoint=4096
#   inputs: A1
#   outputs: PRAGMA已生效的连接
# 层: 输出
# - id: O1
#   name_zh: 配置好PRAGMA的SQLite连接
#   name_en: sqlite3.Connection
#   intro: 自动提交、Row工厂、6条PRAGMA基线就绪的统一连接，全项目SQLite都经此工厂
#   invariant: PRAGMA基线一致(WAL/synchronous/foreign_keys/busy_timeout/temp_store/wal_autocheckpoint)
#   downstream: zephyr.governance.persistence.sqlite_schema(re-export shim) ; zephyr.shared.events.dlq ; zephyr.infrastructure.* ; zephyr.gov_drift.*
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from zephyr.shared.io.paths import DB_PATH as _DB_PATH

# ---------------------------------------------------------------------------
# PRAGMA 配置（KBG-0030 §4.3）
# ---------------------------------------------------------------------------

_PRAGMAS = [
    "PRAGMA journal_mode = WAL",
    "PRAGMA synchronous = NORMAL",
    "PRAGMA foreign_keys = ON",
    "PRAGMA busy_timeout = 5000",
    "PRAGMA temp_store = MEMORY",
    "PRAGMA wal_autocheckpoint = 4096",
]


def _apply_pragmas(conn: sqlite3.Connection) -> None:
    """对连接应用 KBG-0030 §4.3 PRAGMA 基线。"""
    for pragma in _PRAGMAS:
        conn.execute(pragma)


# ---------------------------------------------------------------------------
# 公共 API
# ---------------------------------------------------------------------------


def get_db_connection(
    db_path: Path | str | None = None,
    *,
    check_same_thread: bool = False,
    timeout: float = 30.0,
) -> sqlite3.Connection:
    """
    返回配置好 PRAGMA 的 SQLite 连接。

    参数
    ----
    db_path
        数据库文件路径，默认 DB_PATH（governance.db）。
    check_same_thread
        传给 sqlite3.connect；默认 False 允许跨线程读（单 Writer 假设下安全）。
    timeout
        busy 等待超时（秒），默认 30s。

    返回
    ----
    sqlite3.Connection
        row_factory 已设为 sqlite3.Row，可按列名索引。
        isolation_level=None（自动提交模式），DML 语句立即提交。
    """
    resolved: Path = Path(db_path) if db_path is not None else _DB_PATH
    conn = sqlite3.connect(
        str(resolved),
        isolation_level=None,
        check_same_thread=check_same_thread,
        timeout=timeout,
    )
    conn.row_factory = sqlite3.Row
    _apply_pragmas(conn)
    return conn


__all__ = [
    "get_db_connection",
    "_apply_pragmas",
    "_PRAGMAS",
]
