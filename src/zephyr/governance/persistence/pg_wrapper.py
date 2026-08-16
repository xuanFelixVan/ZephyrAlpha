# [BLUEPRINT] SH-DB-002 | docs/03_modules/_cross_layer/database/blueprint.md | §pg_wrapper
# [MODULE] zephyr.governance.persistence.pg_wrapper
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] psycopg2（外部驱动，persistence 层合法持有）
# [CONSUMERS] zephyr.governance.persistence.depgraph_reader; zephyr.governance.persistence.decision_graph_reader; zephyr.gov_enforcement.rule_enforcement.rule_engine.rule_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 单一规范副本——消除 depgraph_reader / decision_graph_reader / rule_engine 三处重复定义；execute() 每次创建新 RealDictCursor（线程安全语义由调用方 per-thread 管理连接保证）
# [MODIFY-GUARD] 修改需同步三处 consumer 与 tests
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] execute() 透传 psycopg2.Error 给调用方；close() 永不抛异常
# [TESTS] tests/test_depgraph_db.py（间接 via DepgraphReader）
# [TTL] permanent
"""

pg_wrapper.py — psycopg2 connection 的 sqlite3 兼容 execute() 包装器（单一规范副本）。

治本背景（#ARCH-098 / R3，2026-07-28）
-----------------------------------------------
P2 迁移后 psycopg2 connection 没有 execute() 方法，原 SQLite 代码需通过包装器
兼容。此前 `_PgConnExecuteWrapper` 在三处重复定义：

1. ``depgraph_reader.py``        — 最完整版（含 ``closed`` 属性，5.64.2 per-thread 重建）
2. ``decision_graph_reader.py``  — 基础版（仅 ``close()``）
3. ``rule_engine.py``            — 基础版（仅 ``close()``，且使业务模块顶层硬 import psycopg2）

三份副本语义同源但实现漂移（``closed`` 属性缺失），违反 DRY。本模块将规范副本
下沉到 ``governance.persistence`` 子包——psycopg2 是 persistence 层的合法依赖，
业务模块（rule_engine）应依赖此抽象而非直接 import psycopg2，符合 DIP。

设计
----
- ``execute(sql, params)``：每次创建新 ``RealDictCursor``，与原 sqlite3.Row 的
  ``dict(row)`` / ``row['col']`` 用法等价。
- ``closed``：底层 PG 连接是否已关闭，供 per-thread 连接池惰性重建（5.64.2）。
- ``close()``：透传底层 close()，由调用方在 try/except 中隔离异常。

Usage::

    from zephyr.governance.persistence.pg_wrapper import _PgConnExecuteWrapper
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    conn = _PgConnExecuteWrapper(get_depgraph_pg_connection(autocommit=True))
    cursor = conn.execute("SELECT * FROM nodes WHERE node_id = %s", (node_id,))
    row = cursor.fetchone()
    conn.close()

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: psycopg2 PG 连接 外部驱动对象
#   fields: get_depgraph_pg_connection() 返回的原生 psycopg2 connection
#   code: __init__(pg_conn) L76
# - id: I2
#   name: SQL 执行请求 参数组
#   fields: sql 语句（%s 占位）+ params 参数元组
#   code: execute(sql, params) L79
# 层: 算法
# - id: A1
#   name_zh: ① sqlite3 兼容 execute 包装
#   name_en: _PgConnExecuteWrapper.execute
#   intro: 给没有 execute() 的 psycopg2 连接包一层，让老 SQLite 代码一行不改照跑
#   desc: 每次调用新建 RealDictCursor → cur.execute(sql, params) → 返回游标；RealDictCursor 行等价 sqlite3.Row 的 dict(row)/row['col'] 用法
#   inputs: I1 I2
#   outputs: RealDictCursor 游标（fetchone/fetchall 取字典行）
#   invariant: execute() 每次创建新 RealDictCursor；psycopg2.Error 透传给调用方
# - id: A2
#   name_zh: ② 连接状态与关闭管理
#   name_en: closed 属性 + close()
#   intro: 暴露底层连接是否已关，供 per-thread 连接池惰性重建；关闭透传底层
#   desc: closed 属性读 self._pg_conn.closed（5.64.2 per-thread 重建依据）；close() 透传底层 close()，调用方 try/except 隔离异常
#   inputs: I1
#   outputs: closed 布尔 / 连接关闭
#   invariant: close() 异常由调用方隔离
# 层: 输出
# - id: O1
#   name_zh: 字典行查询游标
#   name_en: RealDictCursor
#   intro: 查询结果按字典行返回，与原 sqlite3.Row 用法完全等价
#   downstream: depgraph_reader; decision_graph_reader; rule_engine（[CONSUMERS]）
# - id: O2
#   name_zh: PG 错误别名
#   name_en: PgError
#   intro: psycopg2.Error 的 DIP 重导出，业务模块靠它捕异常就不用顶层 import psycopg2
#   invariant: isinstance 语义与 MRO 透传，零运行时开销
#   downstream: rule_engine 等业务模块（DIP 抽象依赖）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I1 --> A2
# A1 --> O1
# A2 --> O1
# A1 --> O2
"""

from __future__ import annotations

import psycopg2
from psycopg2.extras import RealDictCursor

# DIP 重导出（#ARCH-098 / R3）：业务模块（rule_engine 等）通过本别名
# 捕获 PG 错误，避免顶层 ``import psycopg2``，使业务逻辑仅依赖 persistence 抽象。
# psycopg2.Error 是所有 psycopg2 异常的基类（含 OperationalError / DatabaseError 等），
# 别名透传 isinstance 语义与 MRO，零运行时开销。
PgError = psycopg2.Error

__all__ = ["_PgConnExecuteWrapper", "PgError"]


class _PgConnExecuteWrapper:
    """兼容 sqlite3.Connection.execute() 接口的 psycopg2 connection 包装器。

    psycopg2 connection 没有 execute() 方法，此包装器使原 SQLite 代码无需修改。
    每次调用 execute() 创建一个新的 RealDictCursor（与原 sqlite3.Row 的
    dict(row) / row['col'] 用法等价）。

    规范副本（R3 治本，2026-07-28）：取代 depgraph_reader / decision_graph_reader /
    rule_engine 三处重复定义。本类含 ``closed`` 属性（5.64.2 per-thread 重建所需），
    是三份副本的超集——旧 consumer 切换到本类后行为不变（未调用 ``closed`` 的
    consumer 不受影响）。
    """

    def __init__(self, pg_conn: psycopg2.extensions.connection) -> None:
        self._pg_conn = pg_conn

    def execute(self, sql: str, params: tuple = ()) -> object:
        """执行 SQL，返回 RealDictCursor（调用方 fetchone/fetchall）。"""
        cur = self._pg_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, params)
        return cur

    @property
    def closed(self) -> bool:
        """底层 PG 连接是否已关闭（5.64.2：close() 后各线程据此惰性重建）。"""
        return bool(self._pg_conn.closed)

    def close(self) -> None:
        """关闭底层 PG 连接。调用方应在 try/except 中隔离异常（见 DepgraphReader.close）。"""
        self._pg_conn.close()
