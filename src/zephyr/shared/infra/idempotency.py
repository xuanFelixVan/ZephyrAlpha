# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.infra.idempotency
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.io.paths; zephyr.shared.io.sqlite_factory
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
# [A_module] module_id=MOD-SHR_idempotency | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
idempotency.py —— 幂等性基础设施（Phase 8 新增 | 盲点 B15 修复）

痛点修复：cross_layer_contracts.yaml 定了 idempotency_key 字段，但没有幂等性存储/检查的实现——
  1. AI agent 重复发送相同的 API 请求 -> 重复扣费 / 重复创建资源
  2. 网络重试导致重复处理同一个事件 -> 数据不一致
  3. Stripe / AWS 等平台都内置幂等性——ZephyrAlpha 缺少这个基础设施

设计对标：
  - Stripe Idempotency-Key（最多保留 24h，相同 key 返回缓存结果）
  - AWS Lambda 幂等性（Event Source Mapping + idempotency）
  - IETF HTTP Idempotency-Key draft（I-D draft-idempotency-header-01）

设计原则：
  - key-value 存储——key -> (status, result) 映射
  - 结果缓存——相同 key 直接返回之前的结果
  - TTL——过期后清理避免内存膨胀
  - async-first

AI 施工约定：
  - 任何可能产生副作用的操作 MUST 带 idempotency_key
  - 幂等性存储 SHOULD 配置合理的 TTL（默认 24h，与 Stripe 对齐）
  - 生产环境 SHOULD 用 SQLiteIdempotencyStore（5.40.7，跨进程/重启存活），
    内存版 IdempotencyStore 仅限单进程测试/开发

SSoT: MOD-INF-016 §2.14 shared-idempotency
Version: 0.1.0
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import time
from dataclasses import dataclass, field
from enum import Enum, unique
from pathlib import Path
from typing import Any

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.paths import DB_PATH
from zephyr.shared.io.sqlite_factory import get_db_connection as _sqlite_connect

__all__ = [
    "IdempotencyError",
    "IdempotencyRecord",
    "IdempotencyStatus",
    "IdempotencyStore",
    "SQLiteIdempotencyStore",
    "build_idempotency_key",
]

logger = logging.getLogger(__name__)


class IdempotencyError(ZephyrBaseError):
    """幂等性冲突——相同 key 产生了不同结果或状态不一致。"""
    error_code = "ZA-SH-0044"


@unique
class IdempotencyStatus(str, Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class IdempotencyRecord:
    key: str
    status: IdempotencyStatus
    result: Any = None
    created_at: float = field(default_factory=time.monotonic)
    completed_at: float = 0.0


class IdempotencyStore:
    """幂等性 key-value 存储——防止重复操作。

    对标 Stripe Idempotency-Key：24h TTL，相同 key 返回缓存结果。

    Usage::

        store = IdempotencyStore(default_ttl_seconds=86400)

        async with store.operation("req-abc123") as record:
            if record.status == IdempotencyStatus.COMPLETED:
                return record.result  # 直接返回缓存结果

            result = await do_work()
            record.result = result
            record.status = IdempotencyStatus.COMPLETED
            return result
    """

    def __init__(self, default_ttl_seconds: int = 86400) -> None:
        self._records: dict[str, IdempotencyRecord] = {}
        self._default_ttl = default_ttl_seconds

    def _cleanup_expired(self) -> None:
        now = time.monotonic()
        expired = [
            k
            for k, rec in self._records.items()
            if rec.completed_at > 0 and (now - rec.completed_at) > self._default_ttl
        ]
        for k in expired:
            del self._records[k]
        if expired:
            logger.debug("idempotency: cleaned up %d expired records", len(expired))

    def get(self, key: str) -> IdempotencyRecord | None:
        self._cleanup_expired()
        record = self._records.get(key)
        if record is None:
            return None
        if record.status == IdempotencyStatus.COMPLETED:
            elapsed = time.monotonic() - record.completed_at
            if elapsed > self._default_ttl:
                del self._records[key]
                return None
        return record

    def start(self, key: str) -> IdempotencyRecord:
        self._cleanup_expired()

        existing = self._records.get(key)
        if existing is not None:
            if existing.status == IdempotencyStatus.PROCESSING:
                raise IdempotencyError(
                    f"idempotency key '{key}' is already being processed",
                    details={"key": key, "status": existing.status.value},
                )
            return existing

        record = IdempotencyRecord(key=key, status=IdempotencyStatus.PROCESSING)
        self._records[key] = record
        return record

    def complete(self, key: str, result: object) -> IdempotencyRecord:
        record = self._records.get(key)
        if record is None:
            raise IdempotencyError(
                f"idempotency key '{key}' not found—call start() first",
                details={"key": key},
            )
        record.status = IdempotencyStatus.COMPLETED
        record.result = result
        record.completed_at = time.monotonic()
        return record

    def fail(self, key: str) -> IdempotencyRecord:
        record = self._records.get(key)
        if record is None:
            raise IdempotencyError(
                f"idempotency key '{key}' not found—call start() first",
                details={"key": key},
            )
        record.status = IdempotencyStatus.FAILED
        record.completed_at = time.monotonic()
        return record

    @property
    def size(self) -> int:
        self._cleanup_expired()
        return len(self._records)


# ── SQL 集中化（NO-BARE-SQL gate §5.160.2：裸 SQL 字面量必须提取为 _SQL_* 模块常量）──
_SQL_CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS idempotency_records (
            key TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            result_json TEXT,
            created_at REAL NOT NULL,
            completed_at REAL NOT NULL DEFAULT 0
        )
        """
_SQL_DELETE_EXPIRED = "DELETE FROM idempotency_records WHERE completed_at > 0 AND (? - completed_at) > ?"
_SQL_SELECT_BY_KEY = "SELECT key, status, result_json, created_at, completed_at FROM idempotency_records WHERE key = ?"
_SQL_DELETE_BY_KEY = "DELETE FROM idempotency_records WHERE key = ?"
_SQL_INSERT_PROCESSING = (
    "INSERT INTO idempotency_records (key, status, result_json, created_at, completed_at) VALUES (?, ?, NULL, ?, 0)"
)
_SQL_UPDATE_COMPLETE = "UPDATE idempotency_records SET status = ?, result_json = ?, completed_at = ? WHERE key = ?"
_SQL_UPDATE_FAIL = "UPDATE idempotency_records SET status = ?, completed_at = ? WHERE key = ?"
_SQL_COUNT = "SELECT COUNT(*) FROM idempotency_records"


def _ensure_idempotency_table(conn: sqlite3.Connection) -> None:
    conn.execute(_SQL_CREATE_TABLE)
    conn.commit()


class SQLiteIdempotencyStore:
    """5.40.7 修复：SQLite 持久化幂等存储——与 IdempotencyStore 同接口。

    内存版 IdempotencyStore 进程重启即丢，无法兑现"24h 内同 key 去重"的契约。
    本实现默认落 governance.db（`zephyr.shared.io.paths.DB_PATH`）的
    `idempotency_records` 表，记录跨进程/重启存活。

    与内存版的差异：
      - 时间戳用 `time.time()`（墙钟，跨进程可比较）；内存版用 `time.monotonic()`
        （仅进程内有效，不适合持久化）。
      - result 以 JSON 序列化存储（`default=str` 兜底不可序列化对象）。
      - 每次操作独立开/关连接（对齐 shared/events/dlq.py 的既有模式），
        复用 sqlite_factory 的 PRAGMA 基线（WAL/busy_timeout）。

    Usage::

        store = SQLiteIdempotencyStore()  # 或 SQLiteIdempotencyStore(db_path=":memory:")
        rec = store.start("api:abc123")
        result = do_work()
        store.complete("api:abc123", {"status_code": 200})
    """

    def __init__(self, db_path: str | Path | None = None, default_ttl_seconds: int = 86400) -> None:
        self._db_path = str(db_path) if db_path is not None else str(DB_PATH)
        self._default_ttl = default_ttl_seconds

    def _connect(self) -> sqlite3.Connection:
        conn = _sqlite_connect(self._db_path)
        _ensure_idempotency_table(conn)
        return conn

    def _cleanup_expired(self, conn: sqlite3.Connection) -> None:
        cur = conn.execute(_SQL_DELETE_EXPIRED, (time.time(), float(self._default_ttl)))
        if cur.rowcount:
            logger.debug("idempotency(sqlite): cleaned up %d expired records", cur.rowcount)
        conn.commit()

    @staticmethod
    def _row_to_record(row: tuple) -> IdempotencyRecord:
        key, status, result_json, created_at, completed_at = row
        result: Any = None
        if result_json:
            try:
                result = json.loads(result_json)
            except (json.JSONDecodeError, TypeError):
                result = None
        return IdempotencyRecord(
            key=key,
            status=IdempotencyStatus(status),
            result=result,
            created_at=created_at,
            completed_at=completed_at,
        )

    def get(self, key: str) -> IdempotencyRecord | None:
        conn = self._connect()
        try:
            self._cleanup_expired(conn)
            row = conn.execute(_SQL_SELECT_BY_KEY, (key,)).fetchone()
            if row is None:
                return None
            record = self._row_to_record(row)
            if record.status == IdempotencyStatus.COMPLETED and (time.time() - record.completed_at) > self._default_ttl:
                conn.execute(_SQL_DELETE_BY_KEY, (key,))
                conn.commit()
                return None
            return record
        finally:
            conn.close()

    def start(self, key: str) -> IdempotencyRecord:
        conn = self._connect()
        try:
            self._cleanup_expired(conn)
            row = conn.execute(_SQL_SELECT_BY_KEY, (key,)).fetchone()
            if row is not None:
                record = self._row_to_record(row)
                if record.status == IdempotencyStatus.PROCESSING:
                    raise IdempotencyError(
                        f"idempotency key '{key}' is already being processed",
                        details={"key": key, "status": record.status.value},
                    )
                if record.status == IdempotencyStatus.COMPLETED and (
                    time.time() - record.completed_at
                ) > self._default_ttl:
                    # 过期 COMPLETED 记录——删除后按新操作重新登记
                    conn.execute(_SQL_DELETE_BY_KEY, (key,))
                else:
                    return record

            now = time.time()
            conn.execute(_SQL_INSERT_PROCESSING, (key, IdempotencyStatus.PROCESSING.value, now))
            conn.commit()
            return IdempotencyRecord(key=key, status=IdempotencyStatus.PROCESSING, created_at=now)
        finally:
            conn.close()

    def complete(self, key: str, result: object) -> IdempotencyRecord:
        conn = self._connect()
        try:
            now = time.time()
            cur = conn.execute(
                _SQL_UPDATE_COMPLETE,
                (
                    IdempotencyStatus.COMPLETED.value,
                    json.dumps(result, ensure_ascii=False, default=str),
                    now,
                    key,
                ),
            )
            conn.commit()
            if cur.rowcount == 0:
                raise IdempotencyError(
                    f"idempotency key '{key}' not found—call start() first",
                    details={"key": key},
                )
            return IdempotencyRecord(
                key=key,
                status=IdempotencyStatus.COMPLETED,
                result=result,
                completed_at=now,
            )
        finally:
            conn.close()

    def fail(self, key: str) -> IdempotencyRecord:
        conn = self._connect()
        try:
            now = time.time()
            cur = conn.execute(_SQL_UPDATE_FAIL, (IdempotencyStatus.FAILED.value, now, key))
            conn.commit()
            if cur.rowcount == 0:
                raise IdempotencyError(
                    f"idempotency key '{key}' not found—call start() first",
                    details={"key": key},
                )
            return IdempotencyRecord(key=key, status=IdempotencyStatus.FAILED, completed_at=now)
        finally:
            conn.close()

    @property
    def size(self) -> int:
        conn = self._connect()
        try:
            self._cleanup_expired(conn)
            row = conn.execute(_SQL_COUNT).fetchone()
            return row[0] if row else 0
        finally:
            conn.close()


def build_idempotency_key(prefix: str, *parts: str) -> str:
    """构建确定性幂等键——前缀 + SHA256 前 16 字符。

    同一业务操作重试 = 同一键（parts 由业务字段派生），不同操作 = 不同键。
    5.40.7 修复：提升为公共 API（原 `_build_idempotency_key` 零调用），
    供 api_client 等入口层使用。
    """
    raw = "|".join(parts)
    digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"{prefix}:{digest}"


# 向后兼容别名（tests/infrastructure/test_infra_idempotency.py 引用）
_build_idempotency_key = build_idempotency_key
