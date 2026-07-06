# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] zephyr.governance.persistence.database_service
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
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
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.shared.io.paths import DB_PATH


class DatabaseService:
    """统一数据库服务层"""

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

    # ========== governance.db 方法 ==========

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        """获取任务"""
        conn = self.get_governance_conn(read_only=True)
        row = conn.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        return dict(row) if row else None

    # 5.66.1 修复：tasks 表列名白名单，防止 SQL 注入（f-string 拼接列名的治本）
    _TASK_COLUMNS = frozenset({
        "task_id", "title", "description", "status", "priority", "assignee",
        "created_at", "updated_at", "due_date", "completed_at", "parent_id",
        "module_id", "blueprint_id", "decomposition_id", "task_type",
        "estimated_hours", "actual_hours", "tags", "metadata", "is_deleted",
        "deleted_at", "depends_on", "blocks", "labels", "story_points",
        "sprint_id", "epic_id", "assignee_ai", "source", "difficulty",
        "verification_status", "verification_notes", "review_status",
        "review_notes", "creation_tokens", "related_arch_issues",
    })

    def create_task(self, task_data: dict[str, Any]) -> str:
        """创建任务"""
        conn = self.get_governance_conn()
        task_id = task_data["task_id"]
        # 5.66.1 修复：列名白名单校验，阻断 f-string SQL 注入路径
        invalid_cols = set(task_data.keys()) - self._TASK_COLUMNS
        if invalid_cols:
            raise ValueError(f"Invalid task columns: {invalid_cols}. Allowed: {sorted(self._TASK_COLUMNS)}")
        columns = ", ".join(task_data.keys())
        placeholders = ", ".join(["?" for _ in task_data])
        conn.execute(f"INSERT INTO tasks ({columns}) VALUES ({placeholders})", list(task_data.values()))
        conn.commit()
        return task_id

    def update_task_status(self, task_id: str, status: str) -> None:
        """更新任务状态"""
        conn = self.get_governance_conn()
        conn.execute("UPDATE tasks SET status=?, updated_at=datetime('now') WHERE task_id=?", (status, task_id))
        conn.commit()

    def log_rule_enforcement(self, rule_id: str, operation: str, target: str, result: str, details: str = "") -> None:
        """记录规则执行日志"""
        conn = self.get_governance_conn()
        conn.execute(
            """INSERT INTO rule_enforcement_log
            (rule_id, operation, target, result, details, enforced_at, enforced_by)
            VALUES (?, ?, ?, ?, ?, datetime('now'), ?)""",
            (rule_id, operation, target, result, details, "DatabaseService"),
        )
        conn.commit()

    # ========== depgraph 方法 ==========
    # P2迁移后：depgraph 已切换到 PostgreSQL，使用 psycopg2 cursor 模式
    # cursor_factory=RealDictCursor 使每行返回 RealDictRow，dict(row) 兼容原 sqlite3.Row 用法

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        """获取节点"""
        conn = self.get_depgraph_conn(read_only=True)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM nodes WHERE node_id=%s", (node_id,))
            row = cur.fetchone()
        return dict(row) if row else None

    def get_nodes_by_domain(self, domain_id: str) -> list[dict[str, Any]]:
        """按域获取节点"""
        conn = self.get_depgraph_conn(read_only=True)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM nodes WHERE domain_id=%s", (domain_id,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]

    def get_nodes_by_type(self, node_type: str) -> list[dict[str, Any]]:
        """按类型获取节点"""
        conn = self.get_depgraph_conn(read_only=True)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM nodes WHERE node_type=%s", (node_type,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]

    def get_rule_bindings_by_function(self, function_name: str) -> list[dict[str, Any]]:
        """按函数名获取规则绑定"""
        conn = self.get_depgraph_conn(read_only=True)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM rule_bindings WHERE function_name=%s", (function_name,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]

    def get_edges_from_node(self, from_node: str) -> list[dict[str, Any]]:
        """获取节点的出边"""
        conn = self.get_depgraph_conn(read_only=True)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM edges WHERE from_node=%s", (from_node,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]


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
