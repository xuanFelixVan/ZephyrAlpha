# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.shared.utils.db_utils
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema
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
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""
db_utils.py — SQLite 连接公共 API（SSoT: zephyr.governance.persistence.sqlite_schema）

真源声明：
  - DB_PATH 真源为 zephyr.shared.io.paths（治本 2026-06-30：删除 re-export，
    用 _DB_PATH 别名阻断 IDE organize imports 自动加回 from db_utils import DB_PATH。
    18 个下游文件已改为从 zephyr.shared.io.paths 直接导入 DB_PATH）
  - get_db_connection / init_db 真源为 zephyr.governance.persistence.sqlite_schema
  - 本文件是公共 API 层，供 gates/orchestrator/kb 等上层模块使用
  - 禁止在本文件中重复定义 DB_PATH / get_db_connection / _PRAGMAS / _apply_pragmas
"""

from __future__ import annotations

import importlib as _il

_mod = _il.import_module("zephyr.governance.persistence.sqlite_schema")
get_db_connection = _mod.get_db_connection
init_db = _mod.init_db

__all__ = [
    "ensure_schema",
    "get_db_connection",
    "init_db",
]


def ensure_schema(db_path=None) -> None:
    """确保数据库 schema 已初始化（委托给 sqlite_schema.init_db）。"""
    init_db(db_path)
