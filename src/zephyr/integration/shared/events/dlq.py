# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared.events.dlq
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.infra.observer
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""
dlq.py —— ZephyrAlpha 死信队列（Dead Letter Queue）

Phase 6 新增（盲点 B6）——解决 observer.emit() 静默吞 handler 异常导致
事件丢失的问题。

问题:
  observer.py emit() 在 handler 抛出 Exception 时执行 `pass`（L76-L77），
  事件和异常信息全部丢失。异步事件失败后无任何线索。

设计原则：
  - DeadLetter CLOCK——Subscribe 到 Observer，拦截失败事件（不修改 observer 源码）
  - SQLite 持久化——利用项目已有的 data/databases/governance.db（共用 DB_PATH）
  - 保留策略——max_age 自动清理过期死信
  - 定时重试——可配置 retry_interval，将死信重新推送回事件总线
  - 零侵入——Observer 本身不需要修改，DLQ 作为外部 subscriber 挂载

对标：
  - Kafka Dead Letter Queue: failed messages -> DLQ topic
  - Azure Service Bus: dead-letter queue with TTL + retry
  - AWS SQS: dead-letter queue + redrive policy

SSoT: MOD-INF-016 §2.14 shared-events-dlq
Version: 0.1.0
"""

from __future__ import annotations
from zephyr.shared.io.serialization import dumps

import json
import logging
import re
import sqlite3
from zephyr.shared.io.sqlite_factory import get_db_connection
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from zephyr.shared.infra.observer import EventType, Observer

_logger = logging.getLogger(__name__)

__all__ = [
    "DeadLetter",
    "DeadLetterQueue",
    "attach_dlq_to_observer",
]


# 5.63.2 修复：traceback 脱敏防止敏感信息写入 DLQ
# 敏感模式列表（顺序无关，均使用 re.sub 替换为占位符）：
#   - PostgreSQL DSN: postgres://user:password@host -> postgres://user:***@host
#   - Bearer token:   Bearer sk-xxx -> Bearer ***
#   - API key:        sk-[a-zA-Z0-9]{20,} -> sk-***
#   - 密码赋值:        password=xxx -> password=***
_SENSITIVE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # PostgreSQL / 通用 DB DSN: scheme://user:password@host
    (re.compile(r"((?:postgres|postgresql|mysql|redis|mongodb)://[^:/:@]+):[^@/]+@"), r"\1:***@"),
    # Bearer token（HTTP Authorization 头）
    (re.compile(r"(Bearer\s+)[^\s,]+"), r"\1***"),
    # OpenAI 风格 API key: sk- + 至少 20 个字母数字
    (re.compile(r"sk-[a-zA-Z0-9]{20,}"), "sk-***"),
    # key=value 形式的密码赋值（password=xxx / passwd=xxx / pwd=xxx）
    (re.compile(r"((?:password|passwd|pwd|secret|api_key|apikey|token)=)[^\s,;\"')&]+", re.IGNORECASE), r"\1***"),
]


def _sanitize_traceback(text: str) -> str:
    """5.63.2 修复：对 traceback / error 字符串脱敏，防止敏感信息写入 DLQ。

    替换 DSN 密码、Bearer token、API key、password=xxx 等敏感值，
    保留堆栈结构与错误类型，仅抹除敏感字面量。
    """
    if not text:
        return text
    sanitized = text
    for pattern, replacement in _SENSITIVE_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS dead_letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            payload_json TEXT NOT NULL DEFAULT '{}',
            error_type TEXT NOT NULL DEFAULT '',
            error_message TEXT NOT NULL DEFAULT '',
            error_traceback TEXT NOT NULL DEFAULT '',
            attempt_count INTEGER NOT NULL DEFAULT 0,
            max_attempts INTEGER NOT NULL DEFAULT 3,
            created_at TEXT NOT NULL,
            next_retry_at TEXT,
            resolved INTEGER NOT NULL DEFAULT 0,
            resolved_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_dl_next_retry
        ON dead_letters (next_retry_at) WHERE resolved = 0
        """
    )
    conn.commit()


@dataclass
class DeadLetter:
    """一条死信记录。"""

    event_type: EventType
    payload: dict[str, Any] = field(default_factory=dict)
    error_type: str = ""
    error_message: str = ""
    error_traceback: str = ""
    attempt_count: int = 0
    max_attempts: int = 3
    created_at: str = ""
    next_retry_at: str | None = None
    resolved: bool = False
    resolved_at: str | None = None
    db_id: int | None = None


def _utc_iso() -> str:
    return datetime.now(UTC).isoformat()


class DeadLetterQueue:
    """死信队列——拦截 observer 失败事件并持久化。

    Usage:
        from zephyr.shared.infra.observer import global_observer
        dlq = DeadLetterQueue(db_path="data/databases/governance.db")
        dlq.attach(global_observer)

        # 任何 handler 失败 -> 自动写入 dead_letters 表
        # 定时重试:
        pending = dlq.pop_retryable()
        for dl in pending:
            global_observer.emit(dl.event_type, dl.payload)
            # 成功 -> dlq.mark_resolved(dl.db_id)
            # 失败 -> dlq.record_failure(dl)

        # 清理:
        dlq.purge_expired(max_age_hours=168)
    """

    def __init__(
        self,
        db_path: str,
        *,
        retry_interval: float = 60.0,
        max_attempts: int = 3,
        max_age_hours: float = 168.0,
    ) -> None:
        self._db_path = db_path
        self._retry_interval = retry_interval
        self._max_attempts = max_attempts
        self._max_age_seconds = max_age_hours * 3600.0

    def attach(self, observer: Observer) -> None:
        """挂载 DLQ 到 Observer——自动拦截所有事件失败。

        Args:
            observer: 全局事件总线实例
        """
        for event_type in EventType:
            observer.subscribe(event_type, self._failure_handler)

    def _failure_handler(self, event_type: EventType, payload: dict[str, Any]) -> None:
        """DLQ 内部的 handler 不应抛异常——避免无限递归。"""
        # 5.151.4 修复: 原 raise+except pass 完全静默, 该 handler 已注册到事件总线,
        # 所有 DLQ 事件在此处被完全静默丢弃。改为记录 warning 日志使丢弃可见
        _logger.warning(
            "DLQ _failure_handler called directly (should use capture() instead): "
            "event_type=%s payload_keys=%s",
            event_type,
            list(payload.keys()) if isinstance(payload, dict) else "N/A",
        )

    def capture(
        self,
        event_type: EventType,
        payload: dict[str, Any],
        error: Exception,
        traceback_str: str = "",
    ) -> int:
        """捕获一次失败事件到死信表。

        应由 observer 的 emit() 调用方或 wrapper 在 catch 块中调用。

        Args:
            event_type: 事件类型
            payload: 事件负载（dict）
            error: 捕获的异常
            traceback_str: traceback 字符串（可选）

        Returns:
            新记录的 db id
        """
        now = _utc_iso()
        next_retry = _utc_iso()  # 立即可重试

        # 5.63.2 修复：traceback 脱敏防止敏感信息写入 DLQ
        # error_message 与 error_traceback 均可能含 DSN/Bearer/API key/密码等
        # 敏感字面量，入库前统一脱敏（仅替换敏感值，保留堆栈结构）。
        sanitized_error_message = _sanitize_traceback(str(error))
        sanitized_traceback = _sanitize_traceback(traceback_str)

        conn = get_db_connection(self._db_path)
        try:
            _ensure_table(conn)
            cur = conn.execute(
                """INSERT INTO dead_letters
                   (event_type, payload_json, error_type, error_message,
                    error_traceback, attempt_count, max_attempts,
                    created_at, next_retry_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event_type.value,
                    dumps(payload, ensure_ascii=False),
                    type(error).__name__,
                    sanitized_error_message,
                    sanitized_traceback,
                    1,
                    self._max_attempts,
                    now,
                    next_retry,
                ),
            )
            conn.commit()
            return cur.lastrowid or 0
        finally:
            conn.close()

    def pop_retryable(self) -> list[DeadLetter]:
        """取出所有待重试的死信（到达重试时间的 + 未超过最大尝试次数的）。

        Returns:
            DeadLetter 列表
        """
        now = _utc_iso()
        conn = get_db_connection(self._db_path)
        try:
            _ensure_table(conn)
            rows = conn.execute(
                """SELECT id, event_type, payload_json, error_type,
                          error_message, error_traceback, attempt_count,
                          max_attempts, created_at, next_retry_at
                   FROM dead_letters
                   WHERE resolved = 0
                     AND attempt_count < max_attempts
                     AND next_retry_at <= ?
                   ORDER BY created_at ASC
                   LIMIT 100""",
                (now,),
            ).fetchall()

            result: list[DeadLetter] = []
            for row in rows:
                (
                    db_id,
                    event_type_str,
                    payload_json,
                    error_type,
                    error_message,
                    error_traceback,
                    attempt_count,
                    max_attempts,
                    created_at,
                    next_retry_at,
                ) = row
                try:
                    event_type = EventType(event_type_str)
                except ValueError:
                    event_type = EventType.METRIC_EVENT
                try:
                    payload = json.loads(payload_json)
                except (json.JSONDecodeError, TypeError):
                    payload = {}
                result.append(
                    DeadLetter(
                        event_type=event_type,
                        payload=payload,
                        error_type=error_type or "",
                        error_message=error_message or "",
                        error_traceback=error_traceback or "",
                        attempt_count=attempt_count or 0,
                        max_attempts=max_attempts or 3,
                        created_at=created_at or "",
                        next_retry_at=next_retry_at,
                        db_id=db_id,
                    )
                )
            return result
        finally:
            conn.close()

    def record_failure(self, dl: DeadLetter) -> None:
        """更新死信的失败计数和下次重试时间。

        Args:
            dl: 从 pop_retryable 取出的 DeadLetter（必须有 db_id）
        """
        if dl.db_id is None:
            return

        next_retry_at = _utc_iso()
        retry_ts = time.time() + self._retry_interval
        next_retry_at = datetime.fromtimestamp(retry_ts, tz=UTC).isoformat()

        conn = get_db_connection(self._db_path)
        try:
            _ensure_table(conn)
            conn.execute(
                """UPDATE dead_letters
                   SET attempt_count = attempt_count + 1,
                       next_retry_at = ?
                   WHERE id = ?""",
                (next_retry_at, dl.db_id),
            )
            conn.commit()
        finally:
            conn.close()

    def mark_resolved(self, db_id: int) -> None:
        """标记死信已解决（重试成功）。"""
        conn = get_db_connection(self._db_path)
        try:
            _ensure_table(conn)
            conn.execute(
                """UPDATE dead_letters
                   SET resolved = 1, resolved_at = ?
                   WHERE id = ?""",
                (_utc_iso(), db_id),
            )
            conn.commit()
        finally:
            conn.close()

    def mark_exhausted(self, db_id: int) -> None:
        """标记死信已耗尽重试次数（不再重试）。"""
        conn = get_db_connection(self._db_path)
        try:
            _ensure_table(conn)
            conn.execute(
                """UPDATE dead_letters
                   SET attempt_count = max_attempts, resolved = 1,
                       resolved_at = ?
                   WHERE id = ?""",
                (_utc_iso(), db_id),
            )
            conn.commit()
        finally:
            conn.close()

    def stats(self) -> dict[str, Any]:
        """查询死信队列统计信息。"""
        conn = get_db_connection(self._db_path)
        try:
            _ensure_table(conn)
            total = conn.execute("SELECT COUNT(*) FROM dead_letters").fetchone()[0]
            unresolved = conn.execute("SELECT COUNT(*) FROM dead_letters WHERE resolved = 0").fetchone()[0]
            retryable = conn.execute(
                """SELECT COUNT(*) FROM dead_letters
                   WHERE resolved = 0 AND attempt_count < max_attempts"""
            ).fetchone()[0]
            exhausted = conn.execute(
                """SELECT COUNT(*) FROM dead_letters
                   WHERE resolved = 0 AND attempt_count >= max_attempts"""
            ).fetchone()[0]
            return {
                "total": total,
                "unresolved": unresolved,
                "retryable": retryable,
                "exhausted": exhausted,
                "resolved": total - unresolved,
            }
        finally:
            conn.close()

    def purge_expired(self, *, max_age_hours: float | None = None) -> int:
        """清理过期的死信记录。

        Args:
            max_age_hours: 过期时间（小时）。None = 使用构造时设置的默认值

        Returns:
            清理的记录数
        """
        age_seconds = (max_age_hours or (self._max_age_seconds / 3600.0)) * 3600.0
        cutoff = datetime.fromtimestamp(time.time() - age_seconds, tz=UTC).isoformat()

        conn = get_db_connection(self._db_path)
        try:
            _ensure_table(conn)
            cur = conn.execute(
                """DELETE FROM dead_letters
                   WHERE created_at < ? AND resolved = 1""",
                (cutoff,),
            )
            conn.commit()
            return cur.rowcount
        finally:
            conn.close()


def attach_dlq_to_observer(
    observer: Observer,
    db_path: str,
    *,
    retry_interval: float = 60.0,
    max_attempts: int = 3,
) -> DeadLetterQueue:
    """将死信队列挂载到事件总线的辅助函数。

    用法:
        from zephyr.shared.infra.observer import global_observer
        from zephyr.integration.shared.events.dlq import attach_dlq_to_observer

        dlq = attach_dlq_to_observer(global_observer, "data/databases/governance.db")
    """
    dlq = DeadLetterQueue(
        db_path,
        retry_interval=retry_interval,
        max_attempts=max_attempts,
    )

    original_emit = observer.emit

    def _wrapped_emit(
        event_type: EventType,
        payload: dict[str, Any] | None = None,
    ) -> int:
        """包装 emit——捕获 handler 异常并写入 DLQ。

        不修改 observer 源码，仅在调用层拦截。
        """
        import traceback as tb_module

        payload = payload or {}
        handlers_called = 0
        with observer._lock:
            handlers = list(observer._subscribers[event_type])
            once_flags = set(observer._once_flags[event_type])

        for handler in handlers:
            try:
                handler(event_type, payload)
                handlers_called += 1
            except Exception as exc:
                dlq.capture(
                    event_type,
                    payload,
                    exc,
                    tb_module.format_exc(),
                )
            finally:
                if handler in once_flags:
                    observer.unsubscribe(event_type, handler)

        return handlers_called

    observer.emit = _wrapped_emit  # type: ignore[method-assign]
    return dlq
