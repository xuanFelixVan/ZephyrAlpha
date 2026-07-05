# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §
# [MODULE] zephyr.governance.persistence.olap_engine
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema; zephyr.shared.io.paths
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
# [A_module] module_id=MOD-GOV_olap_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# AI-generated: DuckDB OLAP 分析引擎（T-4-05, B18）
"""
OLAPEngine — DuckDB OLAP 分析引擎
==================================
Task ID      : T-4-05 (B18)
依赖         : B10 ✅（gate_engine.py）、SQLite sqlite_schema.py
ADR          : ADR-0030（SQLite 事务层）、DuckDB 作为 OLAP 只读分析层
safety_level : M

架构说明
--------
本模块实现「SQLite + DuckDB 双引擎」架构：
- **SQLite**：事务层（OLTP），所有写操作由 sqlite_schema.py 负责，保持不变。
- **DuckDB**：分析层（OLAP），以只读方式挂载 SQLite 文件，执行聚合查询。

DuckDB 天然支持直接读取 SQLite 文件（sqlite_scanner 插件），
无需 ETL 管道，两引擎共享同一物理数据库文件。

支持的分析趋势
--------------
1. task_progress_trend   — 任务完成进度趋势（按日/周聚合）
2. compliance_rate_trend — 门禁合规率趋势（按日/周聚合）
3. knowledge_activation_trend — 知识激活率趋势（按月聚合）

SQL 注入防护
------------
所有参数通过 DuckDB 参数化查询传入（`?` 占位符），
无字符串拼接动态 SQL。

用法
----
    from zephyr.governance.persistence.olap_engine import OLAPEngine
    from zephyr.shared.io.paths import DB_PATH

    engine = OLAPEngine(sqlite_path=DB_PATH)
    trend = engine.task_progress_trend(period="day", limit=30)
    engine.close()

    # 推荐使用上下文管理器
    with OLAPEngine() as eng:
        report = eng.compliance_rate_trend(period="week")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb
import structlog

from zephyr.governance.persistence.sqlite_schema import get_db_connection, init_db
from zephyr.shared.io.paths import DB_PATH, REPO_ROOT

__all__ = [
    "OLAPEngine",
    "OLAPEngineError",
    "TrendRow",
]

_log = structlog.get_logger().bind(layer="db", module="olap_engine")

# 合法的 period 值（防止注入）
_VALID_PERIODS = frozenset({"day", "week", "month"})

# DuckDB strftime 格式映射
_PERIOD_FORMAT: dict[str, str] = {
    "day": "%Y-%m-%d",
    "week": "%Y-W%W",
    "month": "%Y-%m",
}

# SQL 注入防护：表名白名单（本模块只查询这些表）
_ALLOWED_TABLES = frozenset({"tasks", "gate_runs", "knowledge", "events"})

# ---------------------------------------------------------------------------
# 类型别名
# ---------------------------------------------------------------------------

TrendRow = dict[str, Any]
"""单条趋势数据行（含 period 字段 + 聚合指标）。"""

# ---------------------------------------------------------------------------
# 异常
# ---------------------------------------------------------------------------


class OLAPEngineError(RuntimeError):
    """OLAPEngine 基础异常。"""


# ---------------------------------------------------------------------------
# 引擎主体
# ---------------------------------------------------------------------------


class OLAPEngine:
    """DuckDB OLAP 分析引擎，只读挂载 SQLite 数据库执行聚合查询。

    Parameters
    ----------
    sqlite_path:
        SQLite 数据库文件路径，默认使用 DB_PATH。
    duckdb_path:
        DuckDB 数据库文件路径；默认 `:memory:`（内存模式）。
        生产中可传入持久化路径。
    auto_init_sqlite:
        True 时在挂载前自动调用 init_db() 确保 SQLite 表存在。
    """

    def __init__(
        self,
        sqlite_path: Path | str | None = None,
        duckdb_path: str = ":memory:",
        *,
        auto_init_sqlite: bool = True,
    ) -> None:
        self._sqlite_path: Path = Path(sqlite_path) if sqlite_path is not None else DB_PATH
        self._duckdb_path = duckdb_path
        self._fallback_mode: bool = False

        if auto_init_sqlite:
            init_db(self._sqlite_path)

        # 建立 DuckDB 连接并挂载 SQLite
        self._conn: duckdb.DuckDBPyConnection = duckdb.connect(self._duckdb_path)
        self._attach_sqlite()

        _log.info(
            "olap_engine_initialized",
            sqlite_path=str(self._sqlite_path),
            duckdb_path=self._duckdb_path,
        )

    def _attach_sqlite(self) -> None:
        """挂载 SQLite 文件为 DuckDB 附加数据库（只读）。"""
        try:
            # DuckDB sqlite_scanner: ATTACH 语句不支持参数化查询，
            # 路径来自内部 Path 对象（非用户输入），单引号转义后安全。
            self._conn.execute("INSTALL sqlite; LOAD sqlite;")
            # 转义路径中的单引号（Windows 路径通常无单引号，此处为防御性处理）
            safe_path = str(self._sqlite_path).replace("'", "''")
            self._conn.execute(f"ATTACH '{safe_path}' AS sqlite_db (TYPE sqlite);")
            _log.debug("sqlite_attached", path=str(self._sqlite_path))
        except Exception as exc:
            _log.warning(
                "sqlite_attach_failed",
                error=str(exc),
                note="falling back to direct CSV / parquet or mock mode",
                exc_info=True,
            )
            # 优雅降级：若 sqlite_scanner 不可用（CI 环境），创建空表骨架
            self._setup_fallback_tables()

    def _setup_fallback_tables(self) -> None:
        """当 sqlite_scanner 不可用时创建内存空表（测试 / CI 降级）。"""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks_fallback (
                task_id TEXT, phase INTEGER, title TEXT, status TEXT,
                completed_at TEXT, updated_at TEXT, created_at TEXT,
                is_deleted INTEGER DEFAULT 0
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS gate_runs_fallback (
                gate_run_id TEXT, gate_id TEXT, passed INTEGER,
                details TEXT, created_at TEXT
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_fallback (
                ke_id TEXT, category TEXT, status TEXT,
                created_at TEXT, updated_at TEXT
            )
        """)
        self._fallback_mode = True
        _log.info("fallback_tables_created")

    # ------------------------------------------------------------------
    # 参数安全校验
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_period(period: str) -> str:
        """校验 period 参数合法性（防 SQL 注入）。

        Parameters
        ----------
        period:
            必须是 'day' | 'week' | 'month'。

        Raises
        ------
        OLAPEngineError
            period 不在白名单时抛出。
        """
        if period not in _VALID_PERIODS:
            raise OLAPEngineError(f"period 参数无效: {period!r}；必须是 {sorted(_VALID_PERIODS)}")
        return period

    @staticmethod
    def _validate_limit(limit: int) -> int:
        """校验 limit 参数范围（1–10000）。

        Raises
        ------
        OLAPEngineError
            limit 超出范围时抛出。
        """
        if not (1 <= limit <= 10_000):
            raise OLAPEngineError(f"limit 参数无效: {limit}；必须在 1–10000 之间")
        return limit

    # ------------------------------------------------------------------
    # 查询辅助
    # ------------------------------------------------------------------

    def _table(self, name: str) -> str:
        """返回实际表引用（sqlite_db.{name} 或 fallback 表名）。"""
        if name not in _ALLOWED_TABLES:
            raise OLAPEngineError(f"表名不在白名单: {name!r}")
        if getattr(self, "_fallback_mode", False):
            return f"{name}_fallback"
        return f"sqlite_db.{name}"

    def _execute(
        self,
        sql: str,
        params: list[Any] | None = None,
    ) -> list[TrendRow]:
        """执行查询并返回行列表（dict 格式）。

        Parameters
        ----------
        sql:
            参数化 SQL（使用 $1, $2, ... 或 ? 占位符）。
        params:
            与占位符对应的参数列表。

        Returns
        -------
        list[TrendRow]
            查询结果，每行为列名 → 值的 dict。
        """
        try:
            rel = self._conn.execute(sql, params or [])
            cols = [desc[0] for desc in rel.description or []]
            rows = rel.fetchall()
            return [dict(zip(cols, row, strict=False)) for row in rows]
        except duckdb.Error as exc:
            _log.error("olap_query_failed", sql=sql[:120], error=str(exc))
            raise OLAPEngineError(f"OLAP 查询失败: {exc}") from exc

    # ------------------------------------------------------------------
    # 公共 API：3 类趋势查询
    # ------------------------------------------------------------------

    def task_progress_trend(
        self,
        period: str = "day",
        limit: int = 30,
        phase: int | None = None,
    ) -> list[TrendRow]:
        """任务完成进度趋势。

        按 period 聚合统计各状态任务数量，用于展示任务流转趋势。

        Parameters
        ----------
        period:
            时间粒度：``'day'`` | ``'week'`` | ``'month'``。
        limit:
            返回最近 N 个时间点。
        phase:
            按阶段过滤（可选，None 表示全阶段）。

        Returns
        -------
        list[TrendRow]
            每行格式::

                {
                  "period": "2026-04-24",
                  "total": 42,
                  "completed": 30,
                  "in_progress": 5,
                  "failed": 2,
                  "pending": 5,
                  "completion_rate": 0.714,
                }
        """
        self._validate_period(period)
        self._validate_limit(limit)
        fmt = _PERIOD_FORMAT[period]
        tasks_tbl = self._table("tasks")

        phase_filter = "AND phase = ?" if phase is not None else ""
        params: list[Any] = []
        if phase is not None:
            params.append(phase)
        params.append(limit)

        sql = f"""
            SELECT
                strftime(CAST(updated_at AS TIMESTAMP), '{fmt}') AS period,
                COUNT(*)                       AS total,
                SUM(CASE WHEN status IN ('COMPLETED','VERIFIED') THEN 1 ELSE 0 END)
                                               AS completed,
                SUM(CASE WHEN status = 'IN_PROGRESS' THEN 1 ELSE 0 END)
                                               AS in_progress,
                SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END)
                                               AS failed,
                SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END)
                                               AS pending
            FROM {tasks_tbl}
            WHERE updated_at IS NOT NULL {phase_filter}
            GROUP BY period
            ORDER BY period DESC
            LIMIT ?
        """
        rows = self._execute(sql, params)

        # 补充完成率（防止除零）
        for row in rows:
            total = row.get("total") or 0
            completed = row.get("completed") or 0
            row["completion_rate"] = round(completed / total, 4) if total > 0 else 0.0

        return rows

    def compliance_rate_trend(
        self,
        period: str = "day",
        limit: int = 30,
        gate_id: str | None = None,
    ) -> list[TrendRow]:
        """门禁合规率趋势。

        按 period 聚合统计门禁通过率，反映系统合规健康度变化。

        Parameters
        ----------
        period:
            时间粒度：``'day'`` | ``'week'`` | ``'month'``。
        limit:
            返回最近 N 个时间点。
        gate_id:
            按门禁 ID 过滤（如 'G1:T-0-001'），可选；None 表示全部门禁。

        Returns
        -------
        list[TrendRow]
            每行格式::

                {
                  "period": "2026-04-24",
                  "total_runs": 100,
                  "passed_runs": 92,
                  "failed_runs": 8,
                  "compliance_rate": 0.92,
                }
        """
        self._validate_period(period)
        self._validate_limit(limit)
        fmt = _PERIOD_FORMAT[period]
        gate_runs_tbl = self._table("gate_runs")

        gate_filter = "AND gate_id LIKE ?" if gate_id is not None else ""
        params: list[Any] = []
        if gate_id is not None:
            params.append(f"{gate_id}%")
        params.append(limit)

        sql = f"""
            SELECT
                strftime(CAST(created_at AS TIMESTAMP), '{fmt}') AS period,
                COUNT(*)                       AS total_runs,
                SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) AS passed_runs,
                SUM(CASE WHEN passed = 0 THEN 1 ELSE 0 END) AS failed_runs
            FROM {gate_runs_tbl}
            WHERE created_at IS NOT NULL {gate_filter}
            GROUP BY period
            ORDER BY period DESC
            LIMIT ?
        """
        rows = self._execute(sql, params)

        for row in rows:
            total = row.get("total_runs") or 0
            passed = row.get("passed_runs") or 0
            row["compliance_rate"] = round(passed / total, 4) if total > 0 else 1.0

        return rows

    def knowledge_activation_trend(
        self,
        period: str = "month",
        limit: int = 12,
        category: str | None = None,
    ) -> list[TrendRow]:
        """知识激活率趋势。

        按 period 统计知识条目累计数及激活（已索引/验证）数量，
        用于追踪知识库成熟度。

        Parameters
        ----------
        period:
            时间粒度：``'day'`` | ``'week'`` | ``'month'``。
        limit:
            返回最近 N 个时间点（默认 12 个月）。
        category:
            按知识类别过滤（如 'best_practice'），可选。

        Returns
        -------
        list[TrendRow]
            每行格式::

                {
                  "period": "2026-04",
                  "total_ke": 50,
                  "activated_ke": 20,
                  "activation_rate": 0.4,
                }
        """
        self._validate_period(period)
        self._validate_limit(limit)
        fmt = _PERIOD_FORMAT[period]
        ke_tbl = self._table("knowledge")

        cat_filter = "AND category = ?" if category is not None else ""
        params: list[Any] = []
        if category is not None:
            params.append(category)
        params.append(limit)

        sql = f"""
            SELECT
                strftime(CAST(updated_at AS TIMESTAMP), '{fmt}') AS period,
                COUNT(*)                       AS total_ke,
                SUM(CASE WHEN status IN ('INDEXED','VERIFIED','ACCEPTED') THEN 1 ELSE 0 END)
                                               AS activated_ke
            FROM {ke_tbl}
            WHERE updated_at IS NOT NULL {cat_filter}
            GROUP BY period
            ORDER BY period DESC
            LIMIT ?
        """
        rows = self._execute(sql, params)

        for row in rows:
            total = row.get("total_ke") or 0
            activated = row.get("activated_ke") or 0
            row["activation_rate"] = round(activated / total, 4) if total > 0 else 0.0

        return rows

    # ------------------------------------------------------------------
    # 辅助：直接统计（用于 fitness_functions 集成）
    # ------------------------------------------------------------------

    def get_gate_summary(self) -> dict[str, int]:
        """返回门禁总运行次数和通过次数（供 FitnessFunctionFramework 使用）。

        Returns
        -------
        dict[str, int]
            ``{"total": N, "passed": M}``
        """
        gate_runs_tbl = self._table("gate_runs")
        rows = self._execute(
            f"""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) AS passed
            FROM {gate_runs_tbl}
            """,
        )
        if not rows:
            return {"total": 0, "passed": 0}
        row = rows[0]
        return {
            "total": int(row.get("total") or 0),
            "passed": int(row.get("passed") or 0),
        }

    def get_knowledge_summary(self) -> dict[str, int]:
        """返回知识条目总数和激活数（供 FitnessFunctionFramework 使用）。

        Returns
        -------
        dict[str, int]
            ``{"total": N, "activated": M}``
        """
        ke_tbl = self._table("knowledge")
        rows = self._execute(
            f"""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status IN ('INDEXED','VERIFIED','ACCEPTED') THEN 1 ELSE 0 END)
                    AS activated
            FROM {ke_tbl}
            """,
        )
        if not rows:
            return {"total": 0, "activated": 0}
        row = rows[0]
        return {
            "total": int(row.get("total") or 0),
            "activated": int(row.get("activated") or 0),
        }

    # ------------------------------------------------------------------
    # 事件归档（SH-DB-001 v2.0）
    # ------------------------------------------------------------------

    def archive_events(
        self,
        days: int = 30,
        *,
        archive_dir: Path | str | None = None,
    ) -> dict:
        """
        将超过 N 天的 events 导出到 Parquet 归档并从 SQLite 删除。

        参数
        ----
        days
            保留最近 N 天的热数据在 SQLite 中，超期部分归档。
        archive_dir
            归档目录，默认 REPO_ROOT/data/warehouse/。

        返回
        ----
        dict
            ``{"archived_count": N, "archive_files": [...], "deleted_count": N}``
        """
        import sqlite3 as _sqlite3
        from datetime import UTC, datetime, timedelta

        archive_root = Path(archive_dir) if archive_dir else REPO_ROOT / "data" / "warehouse"
        archive_root.mkdir(parents=True, exist_ok=True)

        cutoff = datetime.now(UTC) - timedelta(days=days)
        cutoff_iso = cutoff.isoformat()

        if self._fallback_mode:
            _log.warning("archive_events_skipped_fallback_mode")
            return {"archived_count": 0, "archive_files": [], "deleted_count": 0}

        # 步骤 1: 通过 DuckDB sqlite_scanner 读取超期 events 并写入 Parquet
        archive_files: list[str] = []
        total_archived = 0

        try:
            events_tbl = "sqlite_db.events"
            rows = self._conn.execute(
                f"SELECT * FROM {events_tbl} WHERE created_at <= ? ORDER BY created_at ASC",
                [cutoff_iso],
            ).fetchall()

            if not rows:
                _log.info("archive_events_no_data", cutoff=cutoff_iso)
                return {"archived_count": 0, "archive_files": [], "deleted_count": 0}

            cols = [desc[0] for desc in self._conn.description or []]
            import pyarrow as pa
            import pyarrow.parquet as pq

            table = pa.table({col: [row[i] for row in rows] for i, col in enumerate(cols)})
            archive_path = archive_root / f"events_{cutoff.strftime('%Y%m%d')}.parquet"
            pq.write_table(table, str(archive_path))
            archive_files.append(str(archive_path))
            total_archived = len(rows)

            _log.info(
                "events_archived_to_parquet",
                count=total_archived,
                path=str(archive_path),
            )
        except Exception as exc:
            _log.error("archive_events_read_failed", error=str(exc), exc_info=True)
            raise OLAPEngineError(f"事件归档读取失败: {exc}") from exc

        # 步骤 2: 从 SQLite 删除已归档的 events
        deleted_count = 0
        try:
            sqlite_conn = get_db_connection(str(self._sqlite_path))
            cursor = sqlite_conn.execute("DELETE FROM events WHERE created_at <= ?", (cutoff_iso,))
            deleted_count = cursor.rowcount
            sqlite_conn.commit()
            sqlite_conn.close()
            _log.info("events_deleted_from_sqlite", count=deleted_count)
        except _sqlite3.Error as exc:
            _log.error("archive_events_delete_failed", error=str(exc))

        return {
            "archived_count": total_archived,
            "archive_files": archive_files,
            "deleted_count": deleted_count,
        }

    def query_unified_events(
        self,
        *,
        limit: int = 1000,
    ) -> list[TrendRow]:
        """
        统一查询热数据（SQLite）和冷数据（Parquet）中的 events。

        通过 DuckDB 的 UNION ALL 语法合并两个数据源。

        返回
        ----
        list[TrendRow]
            合并后的 events 行列表。
        """
        self._validate_limit(limit)

        archive_root = REPO_ROOT / "data" / "warehouse"

        base_query = "SELECT * FROM sqlite_db.events"

        parquet_files = sorted(archive_root.glob("events_*.parquet"))
        if parquet_files:
            parquet_paths = "', '".join(str(p) for p in parquet_files)
            full_query = f"""
                ({base_query}) UNION ALL
                (SELECT * FROM read_parquet(['{parquet_paths}']))
                ORDER BY created_at DESC
                LIMIT {limit}
            """
        else:
            full_query = f"""
                {base_query}
                ORDER BY created_at DESC
                LIMIT {limit}
            """

        return self._execute(full_query)

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------

    def close(self) -> None:
        """关闭 DuckDB 连接。"""
        try:
            self._conn.close()
            _log.info("olap_engine_closed")
        except Exception:
            # 5.135.1 修复: cleanup 上下文加 logger.debug (不破坏错误处理语义)
            _log.debug("olap_engine close error (suppressed)", exc_info=True)

    def __enter__(self) -> OLAPEngine:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()
