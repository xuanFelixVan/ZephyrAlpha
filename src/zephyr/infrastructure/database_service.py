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
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.governance.persistence.sqlite_schema import get_db_connection
from zephyr.shared.io.paths import DB_PATH, REPO_ROOT
from zephyr.shared.security.secrets import get_secret_from_file_or_default


# ClickHouse 连接配置文件路径（P1-7 修复：消除硬编码，与 .env.postgres 同模式）
_CH_ENV_PATH: Path = REPO_ROOT / "config" / ".env.clickhouse"


def _load_clickhouse_config() -> dict[str, str]:
    """从 config/.env.clickhouse 加载 ClickHouse 连接参数。

    P1-7 修复：消除 host/port/user/password/database 硬编码。
    优先级：os.environ > config/.env.clickhouse > 默认值（localhost:9000/default/空/c1_market）。
    文件不存在时全走默认值（开发环境友好），生产环境应创建该文件覆盖默认值。
    """
    return {
        "host": get_secret_from_file_or_default("CLICKHOUSE_HOST", _CH_ENV_PATH, "localhost"),
        "port": get_secret_from_file_or_default("CLICKHOUSE_PORT", _CH_ENV_PATH, "9000"),
        "user": get_secret_from_file_or_default("CLICKHOUSE_USER", _CH_ENV_PATH, "default"),
        "password": get_secret_from_file_or_default("CLICKHOUSE_PASSWORD", _CH_ENV_PATH, ""),
        "database": get_secret_from_file_or_default("CLICKHOUSE_DATABASE", _CH_ENV_PATH, "c1_market"),
    }


class DatabaseService:
    """统一数据库服务层（治理 + 依赖图 + 业务数据库预留）"""

    def __init__(self):
        # 治本(2026-06-30): 消除硬编码绝对路径, 改用 SSoT 源
        self.governance_db = str(DB_PATH)

        self._governance_conn: sqlite3.Connection | None = None  # 读写连接
        self._governance_conn_readonly: sqlite3.Connection | None = None  # P-REVIEW-3 双连接：只读连接
        self._depgraph_conn: psycopg2.extensions.connection | None = None  # psycopg2 读写连接 (P2迁移后)
        self._depgraph_conn_readonly: psycopg2.extensions.connection | None = None  # P-REVIEW-3 双连接：只读连接
        self._clickhouse_conn: Any | None = None  # clickhouse_driver.Client (C1行情仓库)
        self._lock = threading.Lock()  # Phase 2 P2 修复（并发安全 HIGH）：lazy init 线程安全

    def get_governance_conn(self, read_only: bool = False) -> sqlite3.Connection:
        """获取 governance.db 连接（保持 SQLite）

        复用 sqlite_schema.get_db_connection() 确保 PRAGMA 基线（WAL/busy_timeout 等）一致，
        避免 DatabaseService 自行 sqlite3.connect() 导致连接行为漂移。

        P-REVIEW-3 双连接机制：read_only=True 返回独立的只读连接，read_only=False 返回读写连接。
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
                    if read_only:
                        conn.execute("PRAGMA query_only = 1")
                    setattr(self, target_attr, conn)
        return conn

    def get_depgraph_conn(self, read_only: bool = False) -> psycopg2.extensions.connection:
        """获取 depgraph (PostgreSQL) 连接（P2迁移后从 SQLite 切换到 PostgreSQL）

        返回 psycopg2 connection，cursor_factory=RealDictCursor 以兼容原 sqlite3.Row 的 dict(row) 用法。

        P-REVIEW-3 双连接机制：read_only=True 返回独立的只读连接，read_only=False 返回读写连接。
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

    def get_clickhouse_conn(self):
        """获取 ClickHouse 连接（C1 行情仓库 c1_market）

        P1-7 修复：配置改为从 config/.env.clickhouse 加载（os.environ > 文件 > 默认值）。
        安全约束：settings={'readonly': 1} 确保只读（业务数据库连接必须显式指定 read_only）。
        """
        if self._clickhouse_conn is None:
            with self._lock:
                if self._clickhouse_conn is None:
                    from clickhouse_driver import Client
                    cfg = _load_clickhouse_config()
                    self._clickhouse_conn = Client(
                        host=cfg["host"],
                        port=int(cfg["port"]),
                        user=cfg["user"],
                        password=cfg["password"],
                        database=cfg["database"],
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

        try:
            conn = self.get_clickhouse_conn()
            conn.execute("SELECT 1")
            result["clickhouse"] = True
        except Exception:
            result["clickhouse"] = False

        return result

    def close_all(self):
        """关闭所有连接（P-REVIEW-3 双连接：关闭 4 个连接）"""
        for attr in ("_governance_conn", "_governance_conn_readonly",
                     "_depgraph_conn", "_depgraph_conn_readonly"):
            conn = getattr(self, attr)
            if conn:
                conn.close()
                setattr(self, attr, None)

        # clickhouse_driver.Client 无 close()，断开由 GC 处理
        self._clickhouse_conn = None

    # ========== governance.db 方法 ==========

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        """获取任务"""
        conn = self.get_governance_conn(read_only=True)
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
        conn = self.get_depgraph_conn(read_only=True)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM nodes WHERE node_id=%s", (node_id,))
            row = cur.fetchone()
        return dict(row) if row else None

    def get_nodes_by_domain(self, domain_id: str) -> list:
        """按域获取节点"""
        conn = self.get_depgraph_conn(read_only=True)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM nodes WHERE domain_id=%s", (domain_id,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]

    def get_nodes_by_type(self, node_type: str) -> list:
        """按类型获取节点"""
        conn = self.get_depgraph_conn(read_only=True)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM nodes WHERE node_type=%s", (node_type,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]

    def get_rule_bindings_by_function(self, function_name: str) -> list:
        """按函数名获取规则绑定"""
        conn = self.get_depgraph_conn(read_only=True)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM rule_bindings WHERE function_name=%s", (function_name,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]

    def get_edges_from_node(self, from_node: str) -> list:
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
