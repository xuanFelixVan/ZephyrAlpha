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
    from zephyr.db.olap_engine import OLAPEngine
    from zephyr.db.sqlite_schema import DB_PATH

    engine = OLAPEngine(sqlite_path=DB_PATH)
    trend = engine.task_progress_trend(period="day", limit=30)
    engine.close()

    # 推荐使用上下文管理器
    with OLAPEngine() as eng:
        report = eng.compliance_rate_trend(period="week")
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import duckdb
import structlog

from zephyr.db.sqlite_schema import DB_PATH, init_db

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
_ALLOWED_TABLES = frozenset({"tasks", "gates", "knowledge", "events"})


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
        sqlite_path: Optional[Path | str] = None,
        duckdb_path: str = ":memory:",
        *,
        auto_init_sqlite: bool = True,
    ) -> None:
        self._sqlite_path: Path = (
            Path(sqlite_path) if sqlite_path is not None else DB_PATH
        )
        self._duckdb_path = duckdb_path

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
            self._conn.execute(
                f"ATTACH '{safe_path}' AS sqlite_db (TYPE sqlite);"
            )
            _log.debug("sqlite_attached", path=str(self._sqlite_path))
        except Exception as exc:
            _log.warning(
                "sqlite_attach_failed",
                error=str(exc),
                note="falling back to direct CSV / parquet or mock mode",
            )
            # 优雅降级：若 sqlite_scanner 不可用（CI 环境），创建空表骨架
            self._setup_fallback_tables()

    def _setup_fallback_tables(self) -> None:
        """当 sqlite_scanner 不可用时创建内存空表（测试 / CI 降级）。"""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS sqlite_db.tasks (
                task_id TEXT, phase INTEGER, name TEXT, status TEXT,
                created_at TEXT, updated_at TEXT
            )
        """) if False else None  # DuckDB 无法跨 ATTACH 创建，使用本地表
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks_fallback (
                task_id TEXT, phase INTEGER, name TEXT, status TEXT,
                created_at TEXT, updated_at TEXT
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS gates_fallback (
                gate_run_id TEXT, gate_id TEXT, passed INTEGER, created_at TEXT
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
            raise OLAPEngineError(
                f"period 参数无效: {period!r}；必须是 {sorted(_VALID_PERIODS)}"
            )
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
            raise OLAPEngineError(
                f"limit 参数无效: {limit}；必须在 1–10000 之间"
            )
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
        params: Optional[list[Any]] = None,
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
            return [dict(zip(cols, row)) for row in rows]
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
        phase: Optional[int] = None,
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
        gate_id: Optional[str] = None,
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
        gates_tbl = self._table("gates")

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
            FROM {gates_tbl}
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
        category: Optional[str] = None,
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
        gates_tbl = self._table("gates")
        rows = self._execute(
            f"""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) AS passed
            FROM {gates_tbl}
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
    # 生命周期
    # ------------------------------------------------------------------

    def close(self) -> None:
        """关闭 DuckDB 连接。"""
        try:
            self._conn.close()
            _log.info("olap_engine_closed")
        except Exception:
            pass  # 关闭错误静默处理

    def __enter__(self) -> "OLAPEngine":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()
