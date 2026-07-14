# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md
# [MODULE] zephyr.gov_audit.audit_schema
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_audit_schema | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
audit_schema — 审计视图与查询入口（SH-DB-001 v2.0）
======================================================
Task       : SH-DB-001 v2.0 | audit_schema
Safety     : M（只读查询，不修改数据）

提供审计专用的预定义视图和查询函数，供 CLI 审计面板和 compliance 报告使用。

审计视图
--------
1. v_audit_trail          — 完整审计轨迹视图（tasks × events × gates 三表 JOIN）
2. v_compensation_events  — 补偿事务视图（ATM 文件 rename 失败后的补偿记录）
3. v_schema_migrations   — Schema 迁移历史（_schema_version 表直读）
4. v_slow_queries_log     — 慢查询日志视图

审计查询
--------
- query_audit_for_session(session_id)  — 某 session 的完整审计轨迹
- query_compensation_events()          — 所有未解决的补偿事务
- query_schema_drift()                 — 检查 schema 版本是否最新

用法
----
    from zephyr.gov_audit.audit_schema import AuditQuery

    aq = AuditQuery(db_path="data/databases/governance.db")
    trail = aq.query_audit_for_session("session-20260501")
"""

from __future__ import annotations

import sqlite3
from zephyr.shared.io.sqlite_factory import get_db_connection
from pathlib import Path
from typing import Any

from zephyr.governance.persistence.sqlite_schema import init_db, schema_version
from zephyr.shared.io.paths import DB_PATH

__all__ = [
    "AuditQuery",
    "AuditTrailRow",
    "CompensationEvent",
]

AuditTrailRow = dict[str, Any]
CompensationEvent = dict[str, Any]


class AuditQuery:
    """
    审计视图查询器。

    参数
    ----
    db_path
        SQLite 数据库路径，默认 DB_PATH。
    auto_init
        True 时构造时自动 init_db()。
    """

    def __init__(
        self,
        db_path: Path | str | None = None,
        *,
        auto_init: bool = True,
    ) -> None:
        self._db_path: Path = Path(db_path) if db_path is not None else DB_PATH

        if auto_init:
            init_db(self._db_path)

    def _get_conn(self) -> sqlite3.Connection:
        conn = get_db_connection(str(self._db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ------------------------------------------------------------------
    # 审计视图查询
    # ------------------------------------------------------------------

    def query_audit_for_session(
        self,
        session_id: str,
        *,
        limit: int = 500,
    ) -> list[AuditTrailRow]:
        """查询指定 session 的完整审计轨迹：任务流转 + 事件 + 门禁记录。

        返回按时间线排序的审计条目，每条包含：
        - event_time, event_type, task_id, task_status, gate_result, note
        """
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                """
                SELECT
                    e.created_at   AS event_time,
                    e.event_type,
                    e.payload,
                    e.task_id,
                    t.status       AS task_status,
                    t.phase,
                    g.passed       AS gate_passed,
                    g.details      AS gate_details
                FROM events e
                LEFT JOIN tasks t ON e.task_id = t.task_id
                LEFT JOIN gates g ON e.task_id = g.task_id
                    AND g.created_at <= datetime(e.created_at, '+1 seconds')
                    AND g.created_at >= datetime(e.created_at, '-1 seconds')
                WHERE e.session_id = ?
                ORDER BY e.created_at ASC
                LIMIT ?
                """,
                (session_id, limit),
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def query_compensation_events(self) -> list[CompensationEvent]:
        """查询所有补偿事务事件（ATM 文件 rename 失败后写入）。"""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                """
                SELECT event_id, event_type, payload, task_id, created_at
                FROM events
                WHERE event_type = 'compensation'
                ORDER BY created_at DESC
                """
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def query_schema_drift(self) -> dict[str, Any]:
        """检查当前 schema 版本与迁移注册表是否一致。

        返回当前版本、是否为最新等信息，供 CI 或启动时的 drift detection。
        """
        ver = schema_version(self._db_path)
        current = ver if ver > 0 else abs(ver)

        conn = self._get_conn()
        try:
            cursor = conn.execute("SELECT MAX(version) as max_ver FROM _schema_version")
            row = cursor.fetchone()
            registered_max = row["max_ver"] if row else 0

            cursor = conn.execute("SELECT version, applied_at, description FROM _schema_version ORDER BY version ASC")
            migrations = [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

        return {
            "current_version": current,
            "registered_max_version": registered_max,
            "is_latest": current >= registered_max,
            "migrations_applied": len(migrations),
            "migrations": migrations,
        }

    def query_task_status_history(
        self,
        task_id: str,
        *,
        limit: int = 100,
    ) -> list[AuditTrailRow]:
        """查询指定任务的状态变更历史（通过 events 表重构）。"""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                """
                SELECT
                    e.event_id,
                    e.event_type,
                    e.payload,
                    e.created_at,
                    e.session_id
                FROM events e
                WHERE (e.task_id = ?)
                   OR (json_extract(e.payload, '$.task_id') = ?)
                ORDER BY e.created_at ASC
                LIMIT ?
                """,
                (task_id, task_id, limit),
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def query_recent_sessions_audit(
        self,
        limit: int = 10,
    ) -> list[dict]:
        """查询最近 N 个 session 的审计摘要。"""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                """
                SELECT
                    session_id,
                    COUNT(*)                                                  AS total_tasks,
                    SUM(CASE WHEN status = 'COMPLETED'   THEN 1 ELSE 0 END)  AS completed,
                    SUM(CASE WHEN status = 'VERIFIED'    THEN 1 ELSE 0 END)  AS verified,
                    SUM(CASE WHEN status = 'FAILED'      THEN 1 ELSE 0 END)  AS failed,
                    MIN(created_at)                                           AS session_start,
                    MAX(updated_at)                                           AS last_update
                FROM tasks
                WHERE session_id IS NOT NULL AND is_deleted = 0
                GROUP BY session_id
                ORDER BY last_update DESC
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
