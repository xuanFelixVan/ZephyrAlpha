# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md
# [MODULE] zephyr.governance.observability_governance.query_metrics
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_query_metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
QueryMetrics — SQL 查询性能监控装饰器（SH-DB-001 v2.0）
==========================================================
Task       : SH-DB-001 v2.0 | query_metrics
Safety     : M（监控组件，不影响主流程）

设计要点
--------
1. **轻量装饰器**：包装 sqlite3.execute / executemany，记录每次查询的耗时。
2. **延迟采样**：P50/P95/P99 使用 t-digest 简化版（保留最近 1000 个样本）。
3. **慢查询记录**：>500ms 的查询写入 slow_queries 表。
4. **零侵入**：不影响原始查询流程——装饰器返回原始 cursor。

用法
----
    from zephyr.governance.observability_governance.query_metrics import QueryMetrics

    qm = QueryMetrics(db_path="data/databases/governance.db")

    @qm.track("list_tasks")
    def list_tasks(conn):
        return conn.execute("SELECT * FROM tasks").fetchall()

    # 或直接包装
    cursor = qm.execute(conn, "SELECT * FROM tasks WHERE status=?", ("READY",))
"""

from __future__ import annotations

import functools
import logging
import sqlite3
import threading
import time
from collections import deque
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, TypeVar

from zephyr.shared.io.paths import DB_PATH

__all__ = [
    "QueryMetrics",
    "query_metrics",
]

logger = logging.getLogger(__name__)

_SLOW_THRESHOLD_MS: float = 500.0
_MAX_SAMPLES: int = 1000

F = TypeVar("F", bound=Callable[..., Any])


class PercentileTracker:
    """轻量延迟百分位追踪器（保留最近 N 个样本）。"""

    __slots__ = ("_lock", "_max_size", "_samples")

    def __init__(self, max_size: int = _MAX_SAMPLES) -> None:
        self._samples: deque[float] = deque(maxlen=max_size)
        self._max_size = max_size
        self._lock = threading.Lock()

    def record(self, value_ms: float) -> None:
        with self._lock:
            self._samples.append(value_ms)

    def p50(self) -> float:
        with self._lock:
            if not self._samples:
                return 0.0
            return self._percentile(50.0)

    def p95(self) -> float:
        with self._lock:
            if not self._samples:
                return 0.0
            return self._percentile(95.0)

    def p99(self) -> float:
        with self._lock:
            if not self._samples:
                return 0.0
            return self._percentile(99.0)

    def stats(self) -> dict:
        with self._lock:
            if not self._samples:
                return {"count": 0, "p50_ms": 0, "p95_ms": 0, "p99_ms": 0}
            return {
                "count": len(self._samples),
                "p50_ms": round(self._percentile(50.0), 2),
                "p95_ms": round(self._percentile(95.0), 2),
                "p99_ms": round(self._percentile(99.0), 2),
                "max_ms": round(max(self._samples), 2) if self._samples else 0,
            }

    def _percentile(self, p: float) -> float:
        if not self._samples:
            return 0.0
        sorted_samples = sorted(self._samples)
        k = (p / 100.0) * (len(sorted_samples) - 1)
        f = int(k)
        c = k - f
        if f + 1 < len(sorted_samples):
            return sorted_samples[f] + c * (sorted_samples[f + 1] - sorted_samples[f])
        return sorted_samples[f]


class QueryMetrics:
    """
    SQL 查询性能监控器。

    参数
    ----
    db_path
        SQLite 数据库路径，默认 DB_PATH。slow_queries 表写入此库。
    slow_threshold_ms
        慢查询阈值（毫秒），默认 500ms。
    """

    _instance: QueryMetrics | None = None
    _instance_lock = threading.Lock()

    def __init__(
        self,
        db_path: Path | str | None = None,
        *,
        slow_threshold_ms: float = _SLOW_THRESHOLD_MS,
    ) -> None:
        self._db_path: Path = Path(db_path) if db_path is not None else DB_PATH
        self._slow_threshold_ms = slow_threshold_ms
        self._trackers: dict[str, PercentileTracker] = {}
        self._lock = threading.Lock()
        self._enabled = True

    @classmethod
    def instance(cls) -> QueryMetrics:
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @property
    def enabled(self) -> bool:
        return self._enabled

    def disable(self) -> None:
        self._enabled = False

    def enable(self) -> None:
        self._enabled = True

    def _get_tracker(self, operation: str) -> PercentileTracker:
        with self._lock:
            if operation not in self._trackers:
                self._trackers[operation] = PercentileTracker()
            return self._trackers[operation]

    def _record_slow_query(
        self,
        operation: str,
        duration_ms: float,
        sql: str,
        params: Any = None,
    ) -> None:
        if not self._enabled:
            return
        params_preview = str(params)[:200] if params is not None else None
        explain_rows = []
        try:
            from zephyr.shared.io.paths import DB_PATH as schema_db_path

            explain_conn = get_db_connection(str(schema_db_path))
            try:
                # 5.176 修复：EXPLAIN QUERY PLAN 仅允许 SELECT/WITH 语句，防御纵深防注入
                sql_stripped = sql.lstrip().upper()
                if not (sql_stripped.startswith("SELECT") or sql_stripped.startswith("WITH")):
                    explain_rows = [{"error": "explain_rejected_non_select"}]
                else:
                    explain_result = explain_conn.execute(f"EXPLAIN QUERY PLAN {sql}", params if params else ())
                    explain_rows = [dict(r) for r in explain_result.fetchall()]
            except Exception:
                explain_rows = [{"error": "explain_failed"}]
            finally:
                explain_conn.close()
        except Exception:
            explain_rows = [{"error": "explain_unavailable"}]
        import json as _json

        explain_json = _json.dumps(explain_rows, ensure_ascii=False, default=str)
        try:
            conn = get_db_connection(str(self._db_path))
            from datetime import UTC, datetime

            conn.execute(
                """
                INSERT INTO slow_queries (operation, duration_ms, sql_preview, params_preview, explain_plan, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    operation,
                    round(duration_ms, 4),
                    sql[:500],
                    params_preview,
                    explain_json,
                    datetime.now(UTC).isoformat(),
                ),
            )
            conn.commit()
            conn.close()
        except sqlite3.Error:
            pass

    def track(self, operation: str) -> Callable[[F], F]:
        """装饰器工厂：包裹一个使用 conn.execute() 的函数并追踪耗时。"""

        def decorator(func: F) -> F:
            tracker = self._get_tracker(operation)

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                if not self._enabled:
                    return func(*args, **kwargs)

                start = time.perf_counter()
                try:
                    return func(*args, **kwargs)
                finally:
                    duration_ms = (time.perf_counter() - start) * 1000
                    tracker.record(duration_ms)

                    if duration_ms > self._slow_threshold_ms:
                        sql_preview = ""
                        if args:
                            sql_preview = str(args[0])[:500] if isinstance(args[0], str) else ""
                        self._record_slow_query(
                            operation,
                            duration_ms,
                            sql_preview,
                        )
                        logger.warning(
                            "slow_query_detected",
                            operation=operation,
                            duration_ms=round(duration_ms, 2),
                            threshold_ms=self._slow_threshold_ms,
                        )

            return wrapper  # type: ignore[return-value]

        return decorator

    def execute(
        self,
        conn: sqlite3.Connection,
        operation: str,
        sql: str,
        params: Sequence[Any] | dict[str, Any] = (),
    ) -> sqlite3.Cursor:
        """带监控的 sqlite3.execute 包装。"""
        if not self._enabled:
            return conn.execute(sql, params)

        tracker = self._get_tracker(operation)
        start = time.perf_counter()
        try:
            return conn.execute(sql, params)
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            tracker.record(duration_ms)

            if duration_ms > self._slow_threshold_ms:
                self._record_slow_query(operation, duration_ms, sql, params)

    def stats_all(self) -> dict[str, dict]:
        """返回所有操作的延迟统计（供 Dashboard 查询）。"""
        with self._lock:
            return {op: tracker.stats() for op, tracker in self._trackers.items()}

    def reset(self) -> None:
        """清空所有采样数据（测试用）。"""
        with self._lock:
            self._trackers.clear()


query_metrics = QueryMetrics.instance()
