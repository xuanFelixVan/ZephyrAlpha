# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.database_service
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.governance.__init__, zephyr.shared.database.database_crud_mixin, zephyr.data.ch_config
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-002 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
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
[ERROR_CONTRACT] ConnectionError; TimeoutError; RedisConfigError(Redis 配置缺失); redis.RedisError(Redis 连接异常)
[TESTS] tests/db/test_db_auto_ops.py::test_database_service_init

提供 governance.db / depgraph (PostgreSQL) / ClickHouse (c1_market) 的统一连接管理。
ClickHouse C1 行情仓库已于 2026-07-01 部署（INFRA-DB-006），get_clickhouse_conn() 已实现。
Redis H1 热缓存（INFRA-DB-007）已于 2026-08-02 部署——Redis 7.0.15 @ Hyper-V Ubuntu VM
（172.24.30.100:6379，与 ClickHouse 同 VM，D1 决策），get_redis_conn() 已实现。

注：market.duckdb（旧 DuckDB 业务时序库）已于 2026-07-05 删除（524KB 残留文件，无有价值数据）。业务行情数据已迁移至 ClickHouse c1_market。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: database_service.py
# 层: 算法
# - id: A1
#   name_zh: ① DatabaseService
#   name_en: DatabaseService
#   intro: 统一数据库服务层（治理 + 依赖图 + 业务数据库预留）
#   desc: 统一数据库服务层（治理 + 依赖图 + 业务数据库预留） P-PLAN 专项工程：CRUD 方法（get_task/create_task/get_node 等 9 个）已抽取到…；公共方法（定义序）: get_gov…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: DatabaseService
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import logging
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

logger = logging.getLogger(__name__)


# ClickHouse 连接配置：委托给 zephyr.data.ch_config（裁定 #ARCH-CH-017 / #ARCH-CH-019）
# 消除本模块的默认值 "localhost" 与 ch_writer 默认值 "172.24.30.100" 分裂，
# 统一由 ch_config.load_ch_config() 提供，真源为 config/.env.clickhouse。
from zephyr.data.ch_config import load_ch_reader_config as _load_ch_reader_config_from_ch_config


def _load_clickhouse_config() -> dict[str, str]:
    """从 config/.env.clickhouse 加载 ClickHouse 只读连接参数（audit 9.4 RBAC #ARCH-CH-027）。

    委托给 zephyr.data.ch_config.load_ch_reader_config()，使用 zephyr_reader 账号
    （DB 级 SELECT-only），而非 application-level readonly=1。
    优先级：os.environ > config/.env.clickhouse > 抛 CHConfigError（fail-closed）。
    未配置 CLICKHOUSE_READER_USER 时回退到 CLICKHOUSE_USER（向后兼容）。
    """
    cfg = _load_ch_reader_config_from_ch_config()
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
        # 5.64.2 修复：PG 连接改为 per-thread（threading.local）——psycopg2 connection
        # 非线程安全，单一连接跨线程共享会产生交错执行/状态损坏竞态。
        # 每线程惰性创建独立连接（读写/只读各一），注册到 _live_pg_conns 供 close_all 统一关闭。
        self._pg_tls = threading.local()
        self._live_pg_conns: list[psycopg2.extensions.connection] = []
        self._live_pg_lock = threading.Lock()
        self._clickhouse_conn: Any | None = None  # clickhouse_driver.Client (C1行情仓库)
        self._redis_conn: Any | None = None  # redis.Redis (H1热缓存, INFRA-DB-007)
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
        tls_attr = "depgraph_conn_readonly" if read_only else "depgraph_conn"
        conn = getattr(self._pg_tls, tls_attr, None)
        if conn is None or conn.closed:
            conn = get_depgraph_pg_connection(autocommit=True)
            conn.cursor_factory = RealDictCursor
            if read_only:
                with conn.cursor() as cur:
                    cur.execute("SET default_transaction_read_only = on")
            setattr(self._pg_tls, tls_attr, conn)
            with self._live_pg_lock:
                self._live_pg_conns.append(conn)
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
                        settings={"readonly": 1},
                    )
        return self._clickhouse_conn

    def get_redis_conn(self):
        """获取 Redis 连接（业务数据库 H1 热缓存，INFRA-DB-007）

        Redis 7.0.15 部署在 Hyper-V Ubuntu VM（172.24.30.100:6379），与 ClickHouse
        同 VM 共存（D1 决策 2026-08-02）。归属 MOD-INF-002（D2 决策：本方法在此模块）。

        配置真源：config/.env.redis（仿 ch_config.py 模式，裁定 #ARCH-CH-017 同源思想）。
        连接参数由 redis_config.load_redis_config() 提供，fail-closed（缺配置抛 RedisConfigError）。

        D3 决策（2026-08-02）：单实例 + DB 号隔离——
            db0=模拟盘（sim）、db1=实盘（live）、db2=治理缓存（INFRA-CACHE-001 预留）。
            升级触发条件见蓝图 §8.3（T1-T4），任一命中即启动拆分评估。

        线程安全：redis-py 内置 ConnectionPool（线程安全），单例连接跨线程共享，
        无需像 psycopg2 那样 per-thread 持有。惰性初始化 + 双重检查锁同 get_clickhouse_conn。

        Returns:
            redis.Redis 连接实例（decode_responses=True，业务代码直接拿 str 而非 bytes）。

        Raises:
            RedisConfigError: config/.env.redis 配置缺失（由 load_redis_config 抛出）。
        """
        if self._redis_conn is None:
            with self._lock:
                if self._redis_conn is None:
                    import redis as redis_lib

                    from zephyr.infrastructure.redis_config import load_redis_config

                    cfg = load_redis_config()
                    self._redis_conn = redis_lib.Redis(**cfg)
                    logger.info(
                        "Redis H1 热缓存连接已建立: %s:%s db=%s",
                        cfg["host"],
                        cfg["port"],
                        cfg["db"],
                    )
        return self._redis_conn

    def health_check(self) -> dict[str, bool]:
        """健康检查"""
        result = {}

        try:
            conn = self.get_governance_conn(read_only=True)
            conn.execute("SELECT 1").fetchone()
            result["governance"] = True
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            result["governance"] = False

        try:
            conn = self.get_depgraph_conn(read_only=True)
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            result["depgraph"] = True
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            result["depgraph"] = False

        try:
            conn = self.get_clickhouse_conn()
            conn.execute("SELECT 1")
            result["clickhouse"] = True
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            result["clickhouse"] = False

        try:
            r = self.get_redis_conn()
            r.ping()
            result["redis"] = True
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            result["redis"] = False

        return result

    def close_all(self):
        """关闭所有连接。

        5.64.5 修复：每个 close 独立 try/except 记录后继续——单个连接关闭失败
        不再中断其余连接的清理。
        5.64.2 修复：PG 连接为 per-thread 持有，从 _live_pg_conns 注册表统一关闭；
        各线程下次 get_depgraph_conn() 时按 conn.closed 惰性重建。
        """
        for attr in ("_governance_conn", "_governance_conn_readonly"):
            conn = getattr(self, attr)
            if conn:
                try:
                    conn.close()
                except Exception:  # noqa: BLE001 — 5.64.5：异常隔离，记录后继续
                    logger.warning("close_all: failed to close %s", attr, exc_info=True)
                setattr(self, attr, None)

        with self._live_pg_lock:
            pg_conns, self._live_pg_conns = self._live_pg_conns, []
        for conn in pg_conns:
            try:
                conn.close()
            except Exception:  # noqa: BLE001 — 5.64.5：异常隔离，记录后继续
                logger.warning("close_all: failed to close depgraph conn", exc_info=True)
        # 清理当前线程的线程局部引用（其他线程的引用按 conn.closed 惰性重建）
        for tls_attr in ("depgraph_conn", "depgraph_conn_readonly"):
            if hasattr(self._pg_tls, tls_attr):
                setattr(self._pg_tls, tls_attr, None)

        # clickhouse_driver.Client: 显式 disconnect() 关闭底层 socket，
        # 避免 ResourceWarning（GC 关闭会导致 pytest PytestUnraisableExceptionWarning）
        if self._clickhouse_conn is not None:
            try:
                self._clickhouse_conn.disconnect()
            except Exception:  # noqa: BLE001 — 5.64.5：异常隔离
                logger.warning("close_all: failed to disconnect ClickHouse", exc_info=True)
        self._clickhouse_conn = None

        # redis.Redis: close() 关闭连接池（线程安全，幂等）
        if self._redis_conn is not None:
            try:
                self._redis_conn.close()
            except Exception:  # noqa: BLE001 — 5.64.5：异常隔离
                logger.warning("close_all: failed to close Redis", exc_info=True)
        self._redis_conn = None

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
