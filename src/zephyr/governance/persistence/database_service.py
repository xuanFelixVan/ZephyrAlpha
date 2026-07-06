# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] zephyr.governance.persistence.database_service
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__, zephyr.shared.database.database_crud_mixin
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
DatabaseService: 统一管理两个数据库的连接池、生命周期、健康检查

[BLUEPRINT] DM-100022 | src/zephyr/governance/persistence/database_service.py | §22
[MODULE] zephyr.governance.persistence.database_service
[INVARIANTS] 两库连接池管理(governance.db + depgraph); WAL 模式启用; 健康检查机制
[MODIFY-GUARD] 修改需同步更新 tests/test_db_auto_ops.py
[CONSUMERS] src/zephyr/governance/; scripts/database/
[STABILITY] stable
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] ConnectionError; TimeoutError
[TESTS] tests/test_db_auto_ops.py::test_database_service_init

提供 governance.db / depgraph 的统一连接管理。
"""

import sqlite3
from zephyr.governance.persistence.sqlite_schema import get_db_connection
import threading

import psycopg2
from psycopg2.extras import RealDictCursor

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.shared.database.database_crud_mixin import DatabaseCRUDMixin
from zephyr.shared.io.paths import DB_PATH


class DatabaseService(DatabaseCRUDMixin):
    """统一数据库服务层

    P-PLAN 专项工程：CRUD 方法（get_task/create_task/get_node 等 9 个）已抽取到
    DatabaseCRUDMixin（zephyr.shared.database.database_crud_mixin），本类仅保留
    连接管理（get_governance_conn/get_depgraph_conn/close_all）和健康检查（health_check）。
    """

    def __init__(self) -> None:
        # 治本(2026-06-30): 消除硬编码绝对路径, 改用 SSoT 源
        self.governance_db = str(DB_PATH)

        self._governance_conn: sqlite3.Connection | None = None  # 读写连接
        self._governance_conn_readonly: sqlite3.Connection | None = None  # P-PLAN-1 双连接：只读连接
        self._depgraph_conn: psycopg2.extensions.connection | None = None  # psycopg2 读写连接 (P2迁移后)
        self._depgraph_conn_readonly: psycopg2.extensions.connection | None = None  # P-PLAN-1 双连接：只读连接
        # Phase 2 P2 修复（并发安全 HIGH）：lazy 连接初始化加双重检查锁，防多线程首次调用创建多个连接
        self._lock = threading.Lock()

    def get_governance_conn(self, read_only: bool = False) -> sqlite3.Connection:
        """获取 governance.db 连接（保持 SQLite）

        复用 sqlite_schema.get_db_connection() 确保 PRAGMA 基线（WAL/busy_timeout 等）一致。

        P-PLAN-1 双连接机制：read_only=True 返回独立的只读连接，read_only=False 返回读写连接。
        两个连接相互独立，只读查询不会阻断写操作。

        :param read_only: True=只读连接（PRAGMA query_only=1，独立连接）。
                          安全约束：业务数据库查询MUST显式 read_only=True（project_memory 硬约束）。
                          False=读写连接（用于 INSERT/UPDATE/DELETE）。
        """
        target_attr = "_governance_conn_readonly" if read_only else "_governance_conn"
        conn = getattr(self, target_attr)
        if conn is None:
            with self._lock:
                conn = getattr(self, target_attr)
                if conn is None:
                    conn = get_db_connection(self.governance_db)
                    conn.row_factory = sqlite3.Row
                    if read_only:
                        conn.execute("PRAGMA query_only = 1")
                    setattr(self, target_attr, conn)
        return conn

    def get_depgraph_conn(self, read_only: bool = False) -> psycopg2.extensions.connection:
        """获取 depgraph (PostgreSQL) 连接（P2迁移后从 SQLite 切换到 PostgreSQL）

        返回 psycopg2 connection，cursor_factory=RealDictCursor 以兼容原 sqlite3.Row 的 dict(row) 用法。

        P-PLAN-1 双连接机制：read_only=True 返回独立的只读连接，read_only=False 返回读写连接。
        两个连接相互独立，只读查询不会阻断写操作。

        :param read_only: True=只读连接（SET default_transaction_read_only=on，独立连接）。
                          安全约束：业务数据库查询MUST显式 read_only=True（project_memory 硬约束）。
                          False=读写连接（用于 INSERT/UPDATE/DELETE）。
        """
        target_attr = "_depgraph_conn_readonly" if read_only else "_depgraph_conn"
        conn = getattr(self, target_attr)
        if conn is None:
            with self._lock:
                conn = getattr(self, target_attr)
                if conn is None:
                    conn = get_depgraph_pg_connection(autocommit=True)
                    conn.cursor_factory = RealDictCursor
                    if read_only:
                        with conn.cursor() as cur:
                            cur.execute("SET default_transaction_read_only = on")
                    setattr(self, target_attr, conn)
        return conn

    def health_check(self) -> dict[str, bool]:
        """健康检查"""
        result = {}

        try:
            conn = self.get_governance_conn(read_only=True)
            conn.execute("SELECT 1").fetchone()
            result["governance"] = True
        except Exception:
            result["governance"] = False

        try:
            conn = self.get_depgraph_conn(read_only=True)
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            result["depgraph"] = True
        except Exception:
            result["depgraph"] = False

        return result

    def close_all(self) -> None:
        """关闭所有连接（P-PLAN-1 双连接：关闭 4 个连接）"""
        for attr in ("_governance_conn", "_governance_conn_readonly",
                     "_depgraph_conn", "_depgraph_conn_readonly"):
            conn = getattr(self, attr)
            if conn:
                conn.close()
                setattr(self, attr, None)

    # ========== governance.db + depgraph CRUD 方法 ==========
    # P-PLAN 专项工程：以下 9 个 CRUD 方法已抽取到 DatabaseCRUDMixin：
    #   get_task / create_task / update_task_status / log_rule_enforcement
    #   get_node / get_nodes_by_domain / get_nodes_by_type
    #   get_rule_bindings_by_function / get_edges_from_node
    # 通过 class DatabaseService(DatabaseCRUDMixin) 自动继承，无需在此重复定义。


if __name__ == "__main__":
    # 测试
    ds = DatabaseService()
    print("Health check:", ds.health_check())

    # 测试 governance.db
    conn = ds.get_governance_conn()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"governance.db: {len(tables)} tables")

    # 测试 depgraph
    conn = ds.get_depgraph_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM nodes")
        nodes = cur.fetchone()["count"]
    print(f"depgraph: {nodes} nodes")

    ds.close_all()
    print("All connections closed")
