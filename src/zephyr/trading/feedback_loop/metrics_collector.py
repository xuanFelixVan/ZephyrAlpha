# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.metrics_collector
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_metrics_collector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""MetricsCollector: append-only metrics recording.

Records 5 metric types into a SQLite metrics table for CLI reporting
and Evolution Engine consumption.

Task: T-1-19 | experimental | GLM-5.1
Depends: sqlite_schema.py (T-1-04), task_repo.py (T-1-04)
"""

from __future__ import annotations

import json
import sqlite3
from zephyr.shared.io.sqlite_factory import get_db_connection
import time
import uuid
from enum import Enum, unique
from typing import Any


@unique
class MetricType(str, Enum):
    TASK_DURATION_MS = "task_duration_ms"
    TOKEN_COST_USD = "token_cost_usd"
    TASK_COUNT = "task_count"
    FAILURE_RATE = "failure_rate"
    SESSION_ELAPSED_MS = "session_elapsed_ms"


class MetricsCollector:
    """Append-only metrics recorder backed by SQLite.

    Usage::

        mc = MetricsCollector(db_path="metrics.db")
        mc.record(MetricType.TASK_DURATION_MS, 150.0, tags={"task": "T-1-08"})
        mc.bulk_record([
            {"metric_type": MetricType.TASK_COUNT, "value": 5, "tags": {"phase": 1}},
        ])
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = get_db_connection(self._db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_db(self) -> None:
        conn = self._get_conn()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                metric_id TEXT PRIMARY KEY,
                metric_type TEXT NOT NULL,
                value REAL NOT NULL,
                tags TEXT,
                created_at REAL NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(metric_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_created ON metrics(created_at)")
        conn.commit()

    def record(
        self,
        metric_type: MetricType,
        value: float,
        tags: dict[str, Any] | None = None,
    ) -> str:
        metric_id = str(uuid.uuid4())
        tags_json = json.dumps(tags) if tags else None
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO metrics (metric_id, metric_type, value, tags, created_at) VALUES (?, ?, ?, ?, ?)",
            (metric_id, metric_type.value, value, tags_json, time.time()),
        )
        conn.commit()
        return metric_id

    def bulk_record(self, records: list[dict[str, Any]]) -> list[str]:
        # 5.24.3 修复：N+1 INSERT -> executemany 批量插入
        ids = []
        conn = self._get_conn()
        now = time.time()
        batch: list[tuple] = []
        for r in records:
            metric_id = str(uuid.uuid4())
            mt = r["metric_type"]
            if isinstance(mt, MetricType):
                mt = mt.value
            tags = r.get("tags")
            tags_json = json.dumps(tags) if tags else None
            batch.append((metric_id, mt, r["value"], tags_json, now))
            ids.append(metric_id)
        conn.executemany(
            "INSERT INTO metrics (metric_id, metric_type, value, tags, created_at) VALUES (?, ?, ?, ?, ?)",
            batch,
        )
        conn.commit()
        return ids

    def query(
        self,
        metric_type: MetricType | None = None,
        since: float | None = None,
        until: float | None = None,
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        conn = self._get_conn()
        clauses: list[str] = []
        params: list[Any] = []

        if metric_type is not None:
            clauses.append("metric_type = ?")
            params.append(metric_type.value)
        if since is not None:
            clauses.append("created_at >= ?")
            params.append(since)
        if until is not None:
            clauses.append("created_at <= ?")
            params.append(until)

        where = " AND ".join(clauses) if clauses else "1=1"
        sql = f"SELECT * FROM metrics WHERE {where} ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def aggregate(
        self,
        metric_type: MetricType,
        since: float | None = None,
        until: float | None = None,
    ) -> dict[str, float]:
        conn = self._get_conn()
        clauses = ["metric_type = ?"]
        params: list[Any] = [metric_type.value]

        if since is not None:
            clauses.append("created_at >= ?")
            params.append(since)
        if until is not None:
            clauses.append("created_at <= ?")
            params.append(until)

        where = " AND ".join(clauses)
        sql = f"SELECT COUNT(*) as cnt, SUM(value) as total, AVG(value) as avg_val, MIN(value) as min_val, MAX(value) as max_val FROM metrics WHERE {where}"
        cursor = conn.execute(sql, params)
        row = cursor.fetchone()
        return {
            "count": row["cnt"] or 0,
            "total": row["total"] or 0.0,
            "average": row["avg_val"] or 0.0,
            "min": row["min_val"] or 0.0,
            "max": row["max_val"] or 0.0,
        }

    def collect_from_telemetry(
        self,
        since: str | None = None,
        until: str | None = None,
        sources: list[str] | None = None,
    ) -> dict[str, Any]:
        """从 telemetry_metrics 表读取增量指标（CT-TELE-FLE-001 消费者）。

        参数
        ----
        since / until : str | None
            ISO8601 时间范围。
        sources : list[str] | None
            只采集指定 source_system 的指标；None = 全部。

        返回
        ----
        dict: {by_source: {source: [MetricPoint dict]}, window_aggregates: {avg, p99, count}}
        """
        from zephyr.governance.persistence.sqlite_schema import get_db_connection

        conn = get_db_connection()
        try:
            clauses: list[str] = []
            params: list[Any] = []

            if since is not None:
                clauses.append("timestamp >= ?")
                params.append(since)
            if until is not None:
                clauses.append("timestamp <= ?")
                params.append(until)
            if sources is not None and len(sources) > 0:
                placeholders = ",".join(["?" for _ in sources])
                clauses.append(f"source_system IN ({placeholders})")
                params.extend(sources)

            where = " AND ".join(clauses) if clauses else "1=1"
            sql = f"SELECT * FROM telemetry_metrics WHERE {where} ORDER BY timestamp DESC LIMIT 50000"
            cursor = conn.execute(sql, params)
            rows = [dict(r) for r in cursor.fetchall()]

            by_source: dict[str, list[dict[str, Any]]] = {}
            for row in rows:
                src = row["source_system"]
                by_source.setdefault(src, []).append(row)

            values = [r["value"] for r in rows]
            n = len(values)
            if n > 0:
                values.sort()
                avg = sum(values) / n
                p99_idx = max(0, int(n * 0.99) - 1)
                p99 = values[p99_idx]
                window_aggregates = {"avg": round(avg, 4), "p99": p99, "count": n}
            else:
                window_aggregates = {"avg": 0.0, "p99": 0.0, "count": 0}

            return {
                "by_source": by_source,
                "total_count": n,
                "window_aggregates": window_aggregates,
            }
        finally:
            conn.close()

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None


class MetricSnapshot:
    def __init__(self, metric_name="", value=0.0, timestamp=None, tags=None):
        self.metric_name = metric_name
        self.value = value
        self.timestamp = timestamp
        self.tags = tags or {}


class EMABaseline:
    def __init__(self, alpha=0.3, initial_value=None):
        self.alpha = alpha
        self.value = initial_value

    def update(self, new_value):
        if self.value is None:
            self.value = new_value
        else:
            self.value = self.alpha * new_value + (1 - self.alpha) * self.value
        return self.value
