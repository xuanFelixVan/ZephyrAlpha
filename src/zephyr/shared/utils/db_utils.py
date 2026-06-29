# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.shared.utils.db_utils
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.governance.sqlite_schema
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_db_utils | layer=module | stability=stable | safety=L | ai_autonomy=human_gated
# [TTL] task_bound

"""
db_utils.py — SQLite 连接公共 API（SSoT: zephyr.governance.sqlite_schema）

真源声明：
  - DB_PATH / get_db_connection / init_db 真源为 zephyr.governance.sqlite_schema
  - 本文件是公共 API 层，供 gates/orchestrator/kb 等上层模块使用
  - 禁止在本文件中重复定义 DB_PATH / get_db_connection / _PRAGMAS / _apply_pragmas
"""

from __future__ import annotations

import importlib as _il

_mod = _il.import_module("zephyr.governance.sqlite_schema")
DB_PATH = _mod.DB_PATH
get_db_connection = _mod.get_db_connection
init_db = _mod.init_db

__all__ = [
    "DB_PATH",
    "ensure_schema",
    "get_db_connection",
    "init_db",
]


def ensure_schema(db_path=None) -> None:
    """确保数据库 schema 已初始化（委托给 sqlite_schema.init_db）。"""
    init_db(db_path)
