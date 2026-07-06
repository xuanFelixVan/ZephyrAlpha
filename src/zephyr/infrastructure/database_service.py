# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.database_service
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] auto
# [MATURITY] stable
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
DatabaseService: 统一管理数据库的连接池、生命周期、健康检查

[BLUEPRINT] MOD-INF-002 | src/zephyr/infrastructure/database_service.py
[MODULE] zephyr.infrastructure.database_service
[DOMAIN] D_INFRA_RUNTIME
[INVARIANTS] 治理/依赖图连接池管理; WAL 模式启用; 健康检查机制
[MODIFY-GUARD] 修改需同步更新 tests/db/test_db_auto_ops.py
[CONSUMERS] src/zephyr/governance/; src/zephyr/infrastructure/; scripts/database/
[STABILITY] stable
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] ConnectionError; TimeoutError; NotImplementedError(Redis 预留，ClickHouse 已实现)
[TESTS] tests/db/test_db_auto_ops.py::test_database_service_init

提供 governance.db / depgraph (PostgreSQL) / ClickHouse (c1_market) 的统一连接管理。
ClickHouse C1 行情仓库已于 2026-07-01 部署（INFRA-DB-006），get_clickhouse_conn() 已实现。
Redis H1 热缓存为预留接口（抛 NotImplementedError），待 P2 实盘需求触发施工（#ARCH-048 已裁决）。

注：market.duckdb（旧 DuckDB 业务时序库）已于 2026-07-05 删除（524KB 残留文件，无有价值数据）。业务行情数据已迁移至 ClickHouse c1_market。
"""

import sqlite3
import threading
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.governance.persistence.sqlite_schema import get_db_connection
from zephyr.shared.io.paths import DB_PATH


class DatabaseService:
    """统一数据库服务层（治理 + 依赖图 + 业务数据库预留）"""

    def __init__(self):
        # 治本(2026-06-30): 消除硬编码绝对路径, 改用 SSoT 源
        self.governance_db = str(DB_PATH)

        self._governance_conn: sqlite3.Connection | None = None
        self._depgraph_conn: psycopg2.extensions.connection | None = None  # psycopg2 connection (P2迁移后)
        self._clickhouse_conn: Any | None = None  # clickhouse_driver.Client (C1行情仓库)
        self._lock = threading.Lock()  # Phase 2 P2 修复（并发安全 HIGH）：lazy init 线程安全

    def get_governance_conn(self, read_only: bool = False) -> sqlite3.Connection:
        """获取 governance.db 连接（保持 SQLite）

        复用 sqlite_schema.get_db_connection() 确保 PRAGMA 基线（WAL/busy_timeout 等）一致，
        避免 DatabaseService 自行 sqlite3.connect() 导致连接行为漂移。

        :param read_only: True=只读连接（PRAGMA query_only=1）。
                          安全约束：业务数据库查询MUST显式 read_only=True（project_memory 硬约束）。
                          read_only 仅在连接首次创建时生效（lazy init 缓存机制）。
        """
        if self._governance_conn is None:
            with self._lock:
                if self._governance_conn is None:
                    self._governance_conn = get_db_connection(self.governance_db)
                    if read_only:
                        self._governance_conn.execute("PRAGMA query_only = 1")
        return self._governance_conn

    def get_depgraph_conn(self, read_only: bool = False) -> psycopg2.extensions.connection:
        """获取 depgraph (PostgreSQL) 连接（P2迁移后从 SQLite 切换到 PostgreSQL）

        返回 psycopg2 connection，cursor_factory=RealDictCursor 以兼容原 sqlite3.Row 的 dict(row) 用法。

        :param read_only: True=只读连接（SET default_transaction_read_only=on）。
                          安全约束：业务数据库查询MUST显式 read_only=True（project_memory 硬约束）。
                          read_only 仅在连接首次创建时生效（lazy init 缓存机制）。
        """
        if self._depgraph_conn is None:
            with self._lock:
                if self._depgraph_conn is None:
                    self._depgraph_conn = get_depgraph_pg_connection(autocommit=True)
                    self._depgraph_conn.cursor_factory = RealDictCursor
                    if read_only:
                        with self._depgraph_conn.cursor() as cur:
                            cur.execute("SET default_transaction_read_only = on")
        return self._depgraph_conn

    def get_clickhouse_conn(self):
        """获取 ClickHouse 连接（C1 行情仓库 c1_market）

        配置来源：tmp/import_intraday.py（数据导入脚本，另一个AI对话创建）
        host=localhost port=9000 user=default password='' database=c1_market
        """
        if self._clickhouse_conn is None:
            with self._lock:
                if self._clickhouse_conn is None:
                    from clickhouse_driver import Client
                    self._clickhouse_conn = Client(
                        host='localhost', port=9000, user='default', password='',
                        database='c1_market',
                        settings={'readonly': 1},
                    )
        return self._clickhouse_conn

    def get_redis_conn(self):
        """获取 Redis 连接（业务数据库 H1 热缓存）

        TODO: Spiral 2 业务数据库子蓝图施工时实现。
        """
        raise NotImplementedError("Redis连接待Spiral 2业务数据库施工时实现")

    def health_check(self) -> dict[str, bool]:
        """健康检查"""
        result = {}

        try:
            conn = self.get_governance_conn()
            conn.execute("SELECT 1").fetchone()
            result["governance"] = True
        except Exception:
            result["governance"] = False

        try:
            conn = self.get_depgraph_conn()
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            result["depgraph"] = True
        except Exception:
            result["depgraph"] = False

        try:
            conn = self.get_clickhouse_conn()
            conn.execute("SELECT 1")
            result["clickhouse"] = True
        except Exception:
            result["clickhouse"] = False

        return result

    def close_all(self):
        """关闭所有连接"""
        if self._governance_conn:
            self._governance_conn.close()
            self._governance_conn = None

        if self._depgraph_conn:
            self._depgraph_conn.close()
            self._depgraph_conn = None

        # clickhouse_driver.Client 无 close()，断开由 GC 处理
        self._clickhouse_conn = None

    # ========== governance.db 方法 ==========

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        """获取任务"""
        conn = self.get_governance_conn()
        row = conn.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        return dict(row) if row else None

    # 5.176 修复：tasks 表列名白名单，防止 SQL 注入（f-string 拼接列名的治本）
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
        # 5.176 修复：列名白名单校验，阻断 f-string SQL 注入路径
        invalid_cols = set(task_data.keys()) - self._TASK_COLUMNS
        if invalid_cols:
            raise ValueError(f"Invalid task columns: {invalid_cols}. Allowed: {sorted(self._TASK_COLUMNS)}")
        columns = ", ".join(task_data.keys())
        placeholders = ", ".join(["?" for _ in task_data])
        conn.execute(f"INSERT INTO tasks ({columns}) VALUES ({placeholders})", list(task_data.values()))
        conn.commit()
        return task_id

    def update_task_status(self, task_id: str, status: str):
        """更新任务状态"""
        conn = self.get_governance_conn()
        conn.execute("UPDATE tasks SET status=?, updated_at=datetime('now') WHERE task_id=?", (status, task_id))
        conn.commit()

    def log_rule_enforcement(self, rule_id: str, operation: str, target: str, result: str, details: str = ""):
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
        conn = self.get_depgraph_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM nodes WHERE node_id=%s", (node_id,))
            row = cur.fetchone()
        return dict(row) if row else None

    def get_nodes_by_domain(self, domain_id: str) -> list:
        """按域获取节点"""
        conn = self.get_depgraph_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM nodes WHERE domain_id=%s", (domain_id,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]

    def get_nodes_by_type(self, node_type: str) -> list:
        """按类型获取节点"""
        conn = self.get_depgraph_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM nodes WHERE node_type=%s", (node_type,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]

    def get_rule_bindings_by_function(self, function_name: str) -> list:
        """按函数名获取规则绑定"""
        conn = self.get_depgraph_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM rule_bindings WHERE function_name=%s", (function_name,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]

    def get_edges_from_node(self, from_node: str) -> list:
        """获取节点的出边"""
        conn = self.get_depgraph_conn()
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
