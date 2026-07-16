# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.database_service
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.governance.__init__, zephyr.shared.database.database_crud_mixin, zephyr.data.ch_config
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
from zephyr.shared.database.database_crud_mixin import DatabaseCRUDMixin
from zephyr.shared.io.paths import DB_PATH


# ClickHouse 连接配置：委托给 zephyr.data.ch_config（裁定 #ARCH-CH-017 / #ARCH-CH-019）
# 消除本模块的默认值 "localhost" 与 ch_writer 默认值 "172.24.30.100" 分裂，
# 统一由 ch_config.load_ch_config() 提供，真源为 config/.env.clickhouse。
from zephyr.data.ch_config import load_ch_config as _load_ch_config_from_ch_config


def _load_clickhouse_config() -> dict[str, str]:
    """从 config/.env.clickhouse 加载 ClickHouse 连接参数（裁定 #ARCH-CH-017/#ARCH-CH-019）。

    委托给 zephyr.data.ch_config.load_ch_config()，消除本模块与 ch_writer 的默认值分裂。
    优先级：os.environ > config/.env.clickhouse > 抛 CHConfigError（fail-closed）。
    CLICKHOUSE_HOST 缺失时抛 CHConfigError，禁止静默用 localhost 默认值。
    """
    cfg = _load_ch_config_from_ch_config()
    # ch_config 返回 http_port，database_service 不需要它，但保留其余字段
    return {
        "host": cfg["host"],
        "port": cfg["port"],
        "user": cfg["user"],
        "password": cfg["password"],
        "database": cfg["database"],
    }


class DatabaseService(DatabaseCRUDMixin):
    """统一数据库服务层（治理 + 依赖图 + 业务数据库预留）

    P-PLAN 专项工程：CRUD 方法（get_task/create_task/get_node 等 9 个）已抽取到
    DatabaseCRUDMixin（zephyr.shared.database.database_crud_mixin），本类仅保留
    连接管理（get_governance_conn/get_depgraph_conn/get_clickhouse_conn/close_all）和健康检查（health_check）。
    """

    def __init__(self):
        # 治本(2026-06-30): 消除硬编码绝对路径, 改用 SSoT 源
        self.governance_db = str(DB_PATH)

        self._governance_conn: sqlite3.Connection | None = None  # 读写连接
        self._governance_conn_readonly: sqlite3.Connection | None = None  # P-PLAN-1 双连接：只读连接
        self._depgraph_conn: psycopg2.extensions.connection | None = None  # psycopg2 读写连接 (P2迁移后)
        self._depgraph_conn_readonly: psycopg2.extensions.connection | None = None  # P-PLAN-1 双连接：只读连接
        self._clickhouse_conn: Any | None = None  # clickhouse_driver.Client (C1行情仓库)
        self._lock = threading.Lock()  # Phase 2 P2 修复（并发安全 HIGH）：lazy init 线程安全

    def get_governance_conn(self, read_only: bool = False) -> sqlite3.Connection:
        """获取 governance.db 连接（保持 SQLite）

        复用 sqlite_schema.get_db_connection() 确保 PRAGMA 基线（WAL/busy_timeout 等）一致，
        避免 DatabaseService 自行 sqlite3.connect() 导致连接行为漂移。

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
                    conn.row_factory = sqlite3.Row  # P-PLAN-2 统一 row_factory（与 governance 版对齐）
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
        """关闭所有连接（P-PLAN-1 双连接：关闭 4 个连接）"""
        for attr in ("_governance_conn", "_governance_conn_readonly",
                     "_depgraph_conn", "_depgraph_conn_readonly"):
            conn = getattr(self, attr)
            if conn:
                conn.close()
                setattr(self, attr, None)

        # clickhouse_driver.Client 无 close()，断开由 GC 处理
        self._clickhouse_conn = None

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
