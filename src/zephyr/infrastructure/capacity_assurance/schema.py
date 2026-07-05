# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.schema
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.capacity_assurance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_schema | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
SchemaManager — 容量保障体系数据库 Schema 管理器
依据：蓝图 MOD-INF-001 §5.2 数据库 Schema

管理 5 张核心表：
  1. ai_provenance          — Immutable Core，hash 链完整性
  2. capacity_metrics        — AI-Modifiable，7 天 TTL
  3. error_budget            — 五级响应追踪
  4. token_budget_usage      — 多级 Token 消耗，7 天 TTL
  5. capacity_metrics_hourly — 压缩聚合表（v2.3.0）

PRAGMA 基线：
  journal_mode = WAL
  synchronous = NORMAL
  foreign_keys = ON
  busy_timeout = 5000

用法：
    from zephyr.infrastructure.capacity_assurance.schema import SchemaManager

    mgr = SchemaManager()
    mgr.init_db("path/to/capacity.db")
    mgr.verify()
"""

import hashlib
import os
import sqlite3
from zephyr.shared.io.sqlite_factory import get_db_connection


class SchemaManager:
    """容量保障数据库 Schema 的完整生命周期管理器。"""

    TTL_DAYS = 7
    SCHEMA_VERSION = "2.6.0"

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or get_db_path()
        self._ddl_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ddl.sql")

    def init_db(self, db_path: str | None = None) -> sqlite3.Connection:
        target = db_path or self.db_path
        os.makedirs(os.path.dirname(target) or ".", exist_ok=True)

        conn = get_db_connection(target)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")

        ddl = self._load_ddl()
        conn.executescript(ddl)
        self._ensure_schema_version(conn)
        conn.commit()
        return conn

    def _load_ddl(self) -> str:
        if os.path.exists(self._ddl_path):
            with open(self._ddl_path, encoding="utf-8") as f:
                return f.read()
        return self._inline_ddl()

    def _inline_ddl(self) -> str:
        return """
CREATE TABLE IF NOT EXISTS ai_provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module TEXT NOT NULL,
    field TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    author_agent TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    audit_result TEXT NOT NULL,
    prev_hash TEXT,
    curr_hash TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_prov_module ON ai_provenance(module);
CREATE INDEX IF NOT EXISTS idx_prov_agent ON ai_provenance(author_agent);

CREATE TABLE IF NOT EXISTS capacity_metrics (
    ts TEXT NOT NULL,
    sli_id TEXT NOT NULL,
    value REAL NOT NULL,
    governance_layer TEXT,
    runtime_plane TEXT,
    compensated INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_metrics_ts ON capacity_metrics(ts);
CREATE INDEX IF NOT EXISTS idx_metrics_sli ON capacity_metrics(sli_id);

CREATE TABLE IF NOT EXISTS error_budget (
    slo_id TEXT NOT NULL,
    window_start TEXT NOT NULL,
    window_end TEXT NOT NULL,
    budget_total REAL NOT NULL,
    budget_consumed REAL NOT NULL,
    budget_remaining REAL NOT NULL,
    response_tier TEXT NOT NULL,
    last_updated TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_eb_slo ON error_budget(slo_id);

CREATE TABLE IF NOT EXISTS token_budget_usage (
    ts TEXT NOT NULL,
    budget_level TEXT NOT NULL,
    level_id TEXT NOT NULL,
    tokens_consumed INTEGER NOT NULL,
    tokens_remaining INTEGER NOT NULL,
    model_name TEXT,
    cost_usd REAL
);
CREATE INDEX IF NOT EXISTS idx_tbu_ts ON token_budget_usage(ts);

CREATE TABLE IF NOT EXISTS capacity_metrics_hourly (
    slo_id TEXT NOT NULL,
    hour_bucket TEXT NOT NULL,
    avg_value REAL,
    p99_value REAL,
    max_value REAL,
    sample_count INTEGER,
    governance_layer TEXT,
    runtime_plane TEXT
);
CREATE INDEX IF NOT EXISTS idx_cmh_slo_hour ON capacity_metrics_hourly(slo_id, hour_bucket);
"""

    def _ensure_schema_version(self, conn: sqlite3.Connection):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS _capacity_schema_version (  version TEXT NOT NULL, applied_at TEXT NOT NULL)"
        )
        row = conn.execute("SELECT COUNT(*) FROM _capacity_schema_version").fetchone()
        if row[0] == 0:
            conn.execute(
                "INSERT INTO _capacity_schema_version (version, applied_at) VALUES (?, datetime('now'))",
                (self.SCHEMA_VERSION,),
            )

    def migrate(self, db_path: str | None = None):
        target = db_path or self.db_path
        conn = get_db_connection(target)
        existing = self._existing_tables(conn)
        required = {
            "ai_provenance",
            "capacity_metrics",
            "error_budget",
            "token_budget_usage",
            "capacity_metrics_hourly",
        }
        missing = required - existing
        if missing:
            ddl = self._load_ddl()
            conn.executescript(ddl)
            self._ensure_schema_version(conn)
        conn.commit()
        conn.close()

    def _existing_tables(self, conn: sqlite3.Connection) -> set:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        return {r[0] for r in rows}

    def verify(self, db_path: str | None = None) -> dict:
        target = db_path or self.db_path
        conn = get_db_connection(target)
        result = {
            "all_tables_exist": True,
            "hash_chain_valid": True,
            "missing_tables": [],
            "hash_chain_errors": [],
            "ttl_eligible_rows": 0,
        }

        required_tables = {
            "ai_provenance": [
                "id",
                "module",
                "field",
                "old_value",
                "new_value",
                "author_agent",
                "timestamp",
                "audit_result",
                "prev_hash",
                "curr_hash",
            ],
            "capacity_metrics": ["ts", "sli_id", "value", "governance_layer", "runtime_plane", "compensated"],
            "error_budget": [
                "slo_id",
                "window_start",
                "window_end",
                "budget_total",
                "budget_consumed",
                "budget_remaining",
                "response_tier",
                "last_updated",
            ],
            "token_budget_usage": [
                "ts",
                "budget_level",
                "level_id",
                "tokens_consumed",
                "tokens_remaining",
                "model_name",
                "cost_usd",
            ],
            "capacity_metrics_hourly": [
                "slo_id",
                "hour_bucket",
                "avg_value",
                "p99_value",
                "max_value",
                "sample_count",
                "governance_layer",
                "runtime_plane",
            ],
        }

        for table, expected_cols in required_tables.items():
            try:
                cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
                col_names = {c[1] for c in cols}
                missing_cols = set(expected_cols) - col_names
                if missing_cols:
                    result["all_tables_exist"] = False
                    result["missing_tables"].append(f"{table}: 缺列 {missing_cols}")
            except sqlite3.OperationalError:
                result["all_tables_exist"] = False
                result["missing_tables"].append(table)

        # Verify hash chain
        try:
            rows = conn.execute(
                "SELECT id, prev_hash, curr_hash, module, field, old_value, new_value, "
                "author_agent, timestamp FROM ai_provenance ORDER BY id"
            ).fetchall()
            expected_prev = None
            for row in rows:
                rec_id, prev_hash, curr_hash = row[0], row[1], row[2]
                if expected_prev is not None and prev_hash != expected_prev:
                    result["hash_chain_valid"] = False
                    result["hash_chain_errors"].append(f"id={rec_id}: prev_hash={prev_hash}, expected={expected_prev}")
                expected_prev = curr_hash
        except sqlite3.OperationalError:
            pass

        # TTL check
        try:
            cutoff = f"datetime('now', '-{self.TTL_DAYS} days')"
            count = conn.execute(f"SELECT COUNT(*) FROM capacity_metrics WHERE ts < {cutoff}").fetchone()[0]
            result["ttl_eligible_rows"] = count
        except sqlite3.OperationalError:
            pass

        conn.close()
        return result

    def ttl_cleanup(self, db_path: str | None = None) -> int:
        target = db_path or self.db_path
        conn = get_db_connection(target)
        cutoff = f"datetime('now', '-{self.TTL_DAYS} days')"
        total = 0
        try:
            cur = conn.execute(f"DELETE FROM capacity_metrics WHERE ts < {cutoff}")
            total += cur.rowcount
            cur = conn.execute(f"DELETE FROM token_budget_usage WHERE ts < {cutoff}")
            total += cur.rowcount
            conn.commit()
        except sqlite3.OperationalError:
            pass
        conn.close()
        return total

    @staticmethod
    def compute_hash(
        module: str,
        field: str,
        old_value: str | None,
        new_value: str | None,
        author_agent: str,
        timestamp: str,
        prev_hash: str | None,
    ) -> str:
        payload = "|".join([module, field, old_value or "", new_value or "", author_agent, timestamp, prev_hash or ""])
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class MetricsWriteBuffer:
    """Metrics 写入缓冲层（盲点 #20 实现）。
    批量写入 capacity_metrics，事务包裹，防止逐行写入锁竞争。"""

    BATCH_SIZE = 100

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or get_db_path()
        self._buffer: list[tuple] = []

    def add(
        self,
        ts: str,
        sli_id: str,
        value: float,
        governance_layer: str | None = None,
        runtime_plane: str | None = None,
        compensated: int = 0,
    ):
        self._buffer.append((ts, sli_id, value, governance_layer, runtime_plane, compensated))
        if len(self._buffer) >= self.BATCH_SIZE:
            self.flush()

    def flush(self) -> int:
        if not self._buffer:
            return 0
        conn = get_db_connection(self.db_path)
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.executemany(
                "INSERT INTO capacity_metrics (ts, sli_id, value, governance_layer, runtime_plane, compensated) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                self._buffer,
            )
            conn.commit()
            count = len(self._buffer)
            self._buffer.clear()
            return count
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.flush()


def get_db_path() -> str:
    for var in ["CAPACITY_METRICS_DB_PATH", "AI_AUDIT_PROVENANCE_DB_PATH"]:
        env_val = os.environ.get(var)
        if env_val:
            path = os.path.abspath(env_val)
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            return path

    default = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "capacity.db"
    )
    return default
