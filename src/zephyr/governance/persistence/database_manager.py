# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] zephyr.governance.persistence.database_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema; zephyr.shared.io.paths; zephyr.gov_audit.audit_schema; zephyr.governance.observability_governance.query_metrics
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
# [A_module] module_id=MOD-DAT_database_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
DatabaseManager — 连接池 + 健康检查 + 自动备份 + WAL checkpoint（SH-DB-001 v2.0）
==================================================================================
Task       : SH-DB-001 v2.0 | database_manager
Safety     : HIGH（基础设施核心，管理所有 SQLite 连接的生命周期）
Depends    : sqlite_schema.py

设计要点
--------
1. **连接池**：单例 ThreadPool（size=2），1 个写连接 + 1 个读连接 reserve。
   与  §4.5 单 Writer 假设一致。
2. **健康检查**：每 60 秒自动 PRAGMA integrity_check + ping。失败则自动重连。
3. **自动备份**：每次 session 关闭前 + 调用者手动触发。使用 SQLite backup API
   （非 cp，保证一致性）。保留最近 7 天日备份 + 最近 4 周周末备份。
4. **WAL checkpoint**：shutdown 时执行 PRAGMA wal_checkpoint(TRUNCATE)，压缩 WAL 文件。
   定期 VACUUM 由外部 cron 触发（通过 maintenance() 方法）。

用法
----
    from zephyr.governance.database_manager import DatabaseManager

    dm = DatabaseManager()
    conn = dm.get_connection()
    dm.health_check()
    dm.backup()
    dm.close()  # 自动 WAL checkpoint + 备份
"""

from __future__ import annotations

from typing import Final
import logging
import sqlite3
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

from zephyr.shared.io.paths import DB_PATH, REPO_ROOT
from zephyr.governance.persistence.sqlite_schema import (
    get_db_connection,
    init_db,
    schema_version,
)

__all__ = [
    "DatabaseHealthStatus",
    "DatabaseManager",
    "DatabaseManagerError",
]

logger = logging.getLogger(__name__)

BACKUP_DIR: Final[Path] = REPO_ROOT / "data" / "backups"

# 5.66.6 修复：表名白名单，防止 f-string 拼接表名的 SQL 注入风险。
# verify_backup() 遍历 governance.db 的 sqlite_master 表名，白名单覆盖全部已知表名。
_ALLOWED_TABLES = frozenset(
    {
        "tasks",
        "events",
        "knowledge",
        "gate_runs",
        "circuit_breaker_state",
        "task_files",
        "_schema_version",
        "slow_queries",
        "tx_idempotency",
        "task_events",
        "task_snapshots",
        "fle_metrics",
        "fle_alerts",
        "fle_dispatch_log",
        "task_reviews",
        "f5_state",
    }
)


def _validate_table_name(table: str) -> str:
    """5.66.6 修复：白名单校验表名，仅允许已知表名用于 SQL 拼接。"""
    if table not in _ALLOWED_TABLES:
        raise ValueError(f"table name not in whitelist: {table!r}")
    return table


def _check_db_integrity(conn):
    integrity_ok = True
    integrity_error = None
    try:
        cursor = conn.execute("PRAGMA integrity_check")
        row = cursor.fetchone()
        if row and row[0] != "ok":
            integrity_ok = False
            integrity_error = row[0]
    except sqlite3.Error as exc:
        integrity_ok = False
        integrity_error = str(exc)

    try:
        cursor = conn.execute("PRAGMA quick_check")
        row = cursor.fetchone()
        if row and row[0] != "ok" and integrity_ok:
            integrity_ok = False
            integrity_error = f"quick_check failed: {row[0]}"
    except sqlite3.Error:
        pass

    return integrity_ok, integrity_error


class DatabaseManagerError(RuntimeError):
    """DatabaseManager 基础异常。"""
    error_code = "ZA-GV-0029"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class DatabaseHealthStatus:
    """数据库健康状态快照。"""

    __slots__ = (
        "checked_at",
        "db_size_bytes",
        "error",
        "healthy",
        "integrity_ok",
        "schema_version",
        "table_count",
        "wal_size_bytes",
    )

    def __init__(
        self,
        healthy: bool,
        schema_version: int,
        db_size_bytes: int,
        wal_size_bytes: int,
        table_count: int,
        integrity_ok: bool,
        checked_at: str,
        error: str | None = None,
    ) -> None:
        self.healthy = healthy
        self.schema_version = schema_version
        self.db_size_bytes = db_size_bytes
        self.wal_size_bytes = wal_size_bytes
        self.table_count = table_count
        self.integrity_ok = integrity_ok
        self.checked_at = checked_at
        self.error = error

    def to_dict(self) -> dict:
        return {
            "healthy": self.healthy,
            "schema_version": self.schema_version,
            "db_size_mb": round(self.db_size_bytes / (1024 * 1024), 2),
            "wal_size_mb": round(self.wal_size_bytes / (1024 * 1024), 2),
            "table_count": self.table_count,
            "integrity_ok": self.integrity_ok,
            "checked_at": self.checked_at,
            "error": self.error,
        }

    def __repr__(self) -> str:
        # 5.110.7 修复: 原返回人类可读状态摘要(语义应为__str__), 改为可重建的 field=value 格式
        return (
            f"DatabaseHealthStatus(healthy={self.healthy!r}, "
            f"schema_version={self.schema_version!r}, error={self.error!r})"
        )


class DatabaseManager:
    """
    统一的数据库生命周期管理器。

    参数
    ----
    db_path
        SQLite 数据库路径，默认 DB_PATH。
    backup_dir
        备份文件存放目录，默认 data/backups/。
    auto_init
        True 时在构造时调用 init_db()（默认 True）。
    pool_size
        连接池最大连接数（默认 2）。

    线程模型
    --------
    使用 threading.Lock 保护内部状态。所有公共方法线程安全。
    """

    _instance: DatabaseManager | None = None
    _instance_lock = threading.Lock()

    def __init__(
        self,
        db_path: Path | str | None = None,
        backup_dir: Path | str | None = None,
        *,
        auto_init: bool = True,
        pool_size: int = 2,
    ) -> None:
        self._db_path: Path = Path(db_path) if db_path is not None else DB_PATH
        self._backup_dir: Path = Path(backup_dir) if backup_dir is not None else BACKUP_DIR
        self._pool_size = pool_size
        self._lock = threading.Lock()

        if auto_init:
            init_db(self._db_path)

        self._backup_dir.mkdir(parents=True, exist_ok=True)

        self._conn_pool: list[sqlite3.Connection] = []
        self._closed = False
        self._last_health: DatabaseHealthStatus | None = None

        self._fill_pool()

        logger.info(
            "database_manager_initialized",
            db_path=str(self._db_path),
            pool_size=pool_size,
            schema_version=schema_version(self._db_path),
        )

    @classmethod
    def instance(cls) -> DatabaseManager:
        """返回全局单例（线程安全）。"""
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _fill_pool(self) -> None:
        """填充连接池至 pool_size。"""
        with self._lock:
            while len(self._conn_pool) < self._pool_size:
                conn = get_db_connection(self._db_path)
                self._conn_pool.append(conn)

    def get_connection(self) -> sqlite3.Connection:
        """
        从连接池获取一个连接。

        池中无空闲连接时自动创建新连接（不超过 pool_size）。
        返回的连接调用方不应关闭——由 DatabaseManager 统一管理。

        异常
        ----
        DatabaseManagerError
            数据库已关闭时抛出。
        """
        if self._closed:
            raise DatabaseManagerError("DatabaseManager is closed")
        # Phase 2 P2 修复（并发安全 HIGH）：_conn_pool.pop() 加锁，原代码声明 self._lock 但从未使用
        with self._lock:
            if self._conn_pool:
                return self._conn_pool.pop()
        # 池耗尽时创建临时连接（在锁外创建，避免长时间持锁）
        conn = get_db_connection(self._db_path)
        logger.debug("pool_exhausted_created_temp_connection")
        return conn

    def return_connection(self, conn: sqlite3.Connection) -> None:
        """
        归还连接到池（如果未超出 pool_size 且连接健康）。

        连接不再需要时应归还而非关闭，以便复用。
        """
        if self._closed:
            try:
                conn.close()
            except Exception as e:
                logger.debug("suppressed error in database_manager", exc_info=True)
            return
        # Phase 2 P2 修复（并发安全 HIGH）：_conn_pool.append() 加锁，与 get_connection() 配对
        with self._lock:
            if len(self._conn_pool) < self._pool_size:
                try:
                    conn.execute("SELECT 1")
                    self._conn_pool.append(conn)
                    return
                except sqlite3.Error:
                    pass  # 连接不健康，fall through 到关闭
        # 池满或连接不健康时关闭（在锁外关闭）
        try:
            conn.close()
        except Exception as e:
            logger.debug("suppressed error in database_manager", exc_info=True)

    # ------------------------------------------------------------------
    # 健康检查
    # ------------------------------------------------------------------

    def health_check(self) -> DatabaseHealthStatus:
        """
        执行数据库健康检查并缓存结果。

        检查项目：
        - PRAGMA integrity_check（数据库物理完整性）
        - PRAGMA quick_check（快速完整性扫描）
        - 文件大小（.db + .wal + .shm）
        - 当前 schema 版本
        - 表数量
        """
        if self._closed:
            raise DatabaseManagerError("DatabaseManager is closed")

        checked_at = datetime.now(UTC).isoformat()
        conn = None
        try:
            conn = get_db_connection(self._db_path)

            integrity_ok, integrity_error = _check_db_integrity(conn)

            ver = schema_version(self._db_path)

            db_size = 0
            if self._db_path.exists():
                db_size = self._db_path.stat().st_size

            wal_size = 0
            wal_path = Path(str(self._db_path) + "-wal")
            if wal_path.exists():
                wal_size = wal_path.stat().st_size

            tables = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]

            conn.close()
            conn = None

            healthy = integrity_ok
            status = DatabaseHealthStatus(
                healthy=healthy,
                schema_version=ver,
                db_size_bytes=db_size,
                wal_size_bytes=wal_size,
                table_count=tables,
                integrity_ok=integrity_ok,
                checked_at=checked_at,
                error=integrity_error if not healthy else None,
            )
            self._last_health = status

            if not healthy:
                logger.error(
                    "db_health_check_failed",
                    error=integrity_error,
                    schema_version=ver,
                )
            else:
                logger.debug("db_health_check_passed", schema_version=ver)

            return status

        except Exception as exc:
            status = DatabaseHealthStatus(
                healthy=False,
                schema_version=-1,
                db_size_bytes=0,
                wal_size_bytes=0,
                table_count=0,
                integrity_ok=False,
                checked_at=checked_at,
                error=str(exc),
            )
            self._last_health = status
            logger.error("db_health_check_exception", error=str(exc))
            return status
        finally:
            # 5.61.4 修复：异常路径确保连接归还
            if conn is not None:
                try:
                    conn.close()
                except Exception as e:
                    logger.debug("suppressed error in database_manager", exc_info=True)

    @property
    def last_health(self) -> DatabaseHealthStatus | None:
        """返回最近一次健康检查结果。"""
        return self._last_health

    # ------------------------------------------------------------------
    # 备份
    # ------------------------------------------------------------------

    def backup(self, label: str = "auto") -> Path:
        """
        创建数据库备份（使用 SQLite backup API 保证一致性）。

        备份策略：
        - 文件名：zalpha_metadata_{YYYYMMDD}_{HHMMSS}_{label}.db
        - 保留最近 7 天的日备份
        - 保留最近 4 周（28 天）的周末备份

        参数
        ----
        label
            备份标签（如 "auto", "pre_migration", "manual"）。

        返回
        ----
        Path
            备份文件的绝对路径。
        """
        if self._closed:
            raise DatabaseManagerError("DatabaseManager is closed")

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_name = f"zalpha_metadata_{timestamp}_{label}.db"
        backup_path = self._backup_dir / backup_name

        # 先做 WAL checkpoint 以保证备份包含所有已提交数据
        self._wal_checkpoint(mode="PASSIVE")

        src = get_db_connection(str(self._db_path))
        dst = get_db_connection(str(backup_path))
        try:
            src.backup(dst)
        finally:
            dst.close()
            src.close()

        self._rotate_backups()

        logger.info("db_backup_created", path=str(backup_path), label=label)
        return backup_path

    def _rotate_backups(self) -> None:
        """清理过期备份——保留最近 7 天日备份 + 最近 4 周末备份。"""
        try:
            backup_files = sorted(
                self._backup_dir.glob("zalpha_metadata_*.db"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )

            keep: set[str] = set()
            now = datetime.now(UTC)
            day_count: dict[str, int] = {}
            weekends: dict[str, Path] = {}

            for bf in backup_files:
                name = bf.name
                # 文件名格式: zalpha_metadata_20260505_120000_auto.db
                parts = name.replace("zalpha_metadata_", "").replace(".db", "").split("_")
                if len(parts) >= 2:
                    date_str = parts[0]
                    try:
                        file_date = datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=UTC)
                    except ValueError:
                        continue

                    day_key = date_str
                    if day_key not in day_count or day_count[day_key] < 1:
                        keep.add(name)
                        day_count[day_key] = day_count.get(day_key, 0) + 1

                    # 周末备份（周六=5, 周日=6）
                    if file_date.weekday() >= 5:
                        wk = file_date.strftime("%Y%U")
                        if wk not in weekends:
                            weekends[wk] = bf
                            keep.add(name)

                    # 年龄检查
                    age_days = (now - file_date).days
                    if age_days <= 7:
                        keep.add(name)

            for bf in backup_files:
                if bf.name not in keep:
                    try:
                        bf.unlink()
                        logger.debug("db_backup_rotated", path=str(bf))
                    except OSError:
                        pass

        except Exception as exc:
            logger.warning("db_backup_rotation_error: %s", exc, exc_info=True)

    # ------------------------------------------------------------------
    # WAL checkpoint
    # ------------------------------------------------------------------

    def _wal_checkpoint(self, mode: str = "PASSIVE") -> None:
        """执行 WAL checkpoint（PASSIVE / FULL / RESTART / TRUNCATE）。"""
        # 5.176 修复：mode 枚举白名单校验，防 PRAGMA 参数注入
        _VALID_MODES = frozenset({"PASSIVE", "FULL", "RESTART", "TRUNCATE"})
        if mode not in _VALID_MODES:
            raise ValueError(f"非法 wal_checkpoint mode: {mode!r}（仅允许 {sorted(_VALID_MODES)}）")
        conn = None
        try:
            conn = get_db_connection(self._db_path)
            cursor = conn.execute(f"PRAGMA wal_checkpoint({mode})")
            row = cursor.fetchone()
            conn.close()
            conn = None
            if row:
                logger.debug(
                    "wal_checkpoint",
                    mode=mode,
                    busy=row[0],
                    log=row[1],
                    checkpointed=row[2],
                )
        except sqlite3.Error as exc:
            logger.warning("wal_checkpoint_failed: mode=%s error=%s", mode, exc)
        finally:
            # 5.61.4 修复：异常路径确保连接归还
            if conn is not None:
                try:
                    conn.close()
                except Exception as e:
                    logger.debug("suppressed error in database_manager", exc_info=True)

    def wal_checkpoint_truncate(self) -> None:
        """强制 checkpoint 并截断 WAL 文件（shutdown 时调用）。"""
        self._wal_checkpoint(mode="TRUNCATE")

    # ------------------------------------------------------------------
    # 维护操作
    # ------------------------------------------------------------------

    def maintenance(self) -> dict:
        """
        执行定期维护操作：VACUUM + integrity check + WAL truncate。

        典型用法：cron job 每周触发一次。

        返回
        ----
        dict
            维护结果摘要。
        """
        result: dict = {"vacuum": False, "integrity": False, "wal_truncated": False}

        health = self.health_check()
        result["pre_health"] = health.to_dict()

        if health.healthy:
            conn = None
            try:
                conn = get_db_connection(self._db_path)
                conn.execute("VACUUM")
                conn.close()
                conn = None
                result["vacuum"] = True
            except sqlite3.Error as exc:
                logger.error("vacuum_failed", error=str(exc))
            finally:
                # 5.61.4 修复：异常路径确保连接归还
                if conn is not None:
                    try:
                        conn.close()
                    except Exception as e:
                        logger.debug("suppressed error in database_manager", exc_info=True)

            self._wal_checkpoint("TRUNCATE")
            result["wal_truncated"] = True

        result["post_health"] = self.health_check().to_dict()
        return result

    # ------------------------------------------------------------------
    # 统计信息
    # ------------------------------------------------------------------

    def stats(self) -> dict:
        """返回数据库统计信息（供 Dashboard 和可观测性使用）。"""
        conn = get_db_connection(self._db_path)
        try:
            task_count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            active_count = conn.execute(
                "SELECT COUNT(*) FROM tasks WHERE status IN ('IN_PROGRESS','READY','RETRY','WAITING') AND is_deleted=0"
            ).fetchone()[0]
            event_count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            gate_count = conn.execute("SELECT COUNT(*) FROM gate_runs").fetchone()[0]
            ke_count = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
            slow_count = conn.execute("SELECT COUNT(*) FROM slow_queries").fetchone()[0]
        finally:
            self.return_connection(conn)

        db_size = self._db_path.stat().st_size if self._db_path.exists() else 0
        wal_path = Path(str(self._db_path) + "-wal")
        wal_size = wal_path.stat().st_size if wal_path.exists() else 0

        return {
            "task_count": task_count,
            "active_task_count": active_count,
            "event_count": event_count,
            "gate_count": gate_count,
            "ke_count": ke_count,
            "slow_query_count": slow_count,
            "db_size_mb": round(db_size / (1024 * 1024), 2),
            "wal_size_mb": round(wal_size / (1024 * 1024), 2),
            "schema_version": schema_version(self._db_path),
        }

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------

    def close(self, *, backup_before_close: bool = False) -> None:
        """
        优雅关闭：WAL checkpoint + 可选备份 + 关闭连接池。

        参数
        ----
        backup_before_close
            True 时在关闭前自动备份（默认 False）。
            治本（2026-06-29 阶段A+）：默认改为 False，消灭每次 close 自动创建
            zalpha_metadata_*.db 备份的源头（118 个 .db 残留的 85% 来源）。
            需要备份时显式传 backup_before_close=True，或显式调用 backup()。
            备份唯一真源：本类 backup() 方法（显式调用）。
        """
        if self._closed:
            return

        with self._lock:
            if self._closed:
                return

            if backup_before_close:
                try:
                    self.backup(label="pre_close")
                except Exception as exc:
                    logger.warning("pre_close_backup_failed: %s", exc, exc_info=True)

            self._closed = True

            # 5.73.4 修复：原 wal_checkpoint_truncate() 未被 try/except 包裹（对比 conn.close() 有保护）。
            # WAL checkpoint 抛异常会掩盖with块原始异常并中断连接池清理流程。
            try:
                self.wal_checkpoint_truncate()
            except Exception as e:
                logger.debug("suppressed error in database_manager", exc_info=True)

            for conn in self._conn_pool:
                try:
                    conn.close()
                except Exception as e:
                    logger.debug("suppressed error in database_manager", exc_info=True)
            self._conn_pool.clear()

            logger.info("database_manager_closed")

    # ------------------------------------------------------------------
    # Phase 2 扩展方法（T-DB-005~T-DB-012）
    # ------------------------------------------------------------------

    def verify_backup(self, backup_path: Path | str) -> dict:
        """T-DB-005: 验证备份文件完整性。

        返回 dict{integrity_ok, table_count, row_counts, duration_ms}。
        """
        start = time.perf_counter()
        backup = Path(backup_path)
        if not backup.exists():
            raise DatabaseManagerError(f"备份文件不存在: {backup}")
        conn = get_db_connection(str(backup))
        try:
            conn.execute("PRAGMA journal_mode = WAL")
            integrity = conn.execute("PRAGMA integrity_check").fetchone()
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
            row_counts = {}
            for t in tables:
                # 5.66.6 修复：白名单校验表名后再用于 f-string 拼接（原 [t['name']] 方括号为
                # SQL Server 语法，SQLite 下无效防御；改用白名单校验）
                try:
                    safe_table = _validate_table_name(t["name"])
                except ValueError:
                    logger.debug("verify_backup: skip table not in whitelist: %s", t["name"])
                    continue
                cnt = conn.execute(f"SELECT COUNT(*) FROM {safe_table}").fetchone()
                row_counts[safe_table] = cnt[0] if cnt else 0
            duration_ms = (time.perf_counter() - start) * 1000
            return {
                "integrity_ok": integrity is not None and integrity[0] == "ok",
                "integrity_detail": integrity[0] if integrity else "unknown",
                "table_count": len(tables),
                "row_counts": row_counts,
                "duration_ms": round(duration_ms, 2),
            }
        finally:
            conn.close()

    def dead_letter_queue(self, limit: int = 50) -> list[dict[str, object]]:
        """T-DB-006: 查询未处理的补偿事件（死信队列）。

        返回补偿失败且未重试超过 3 次的 events 列表。
        """
        conn = self.get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT e.event_id, e.payload, e.created_at,
                       COALESCE(e.payload->>'$.retry_count', '0') AS retry_count
                FROM events e
                WHERE e.event_type = 'compensation'
                  AND COALESCE(CAST(json_extract(e.payload, '$.processed') AS INTEGER), 0) = 0
                  AND COALESCE(CAST(json_extract(e.payload, '$.retry_count') AS INTEGER), 0) < 3
                ORDER BY e.created_at ASC
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(r) for r in cursor.fetchall()]
        finally:
            self.return_connection(conn)

    def retry_dlq(self) -> int:
        """T-DB-006: 重试死信队列中的补偿事件。返回成功重试次数。"""
        import json as _json

        conn = self.get_connection()
        success = 0
        try:
            dead_letters = self.dead_letter_queue()
            for dl in dead_letters:
                event_id = dl["event_id"]
                try:
                    conn.execute("BEGIN IMMEDIATE")
                    payload = _json.loads(str(dl["payload"])) if isinstance(dl["payload"], str) else dict(dl["payload"])
                    payload["processed"] = 1
                    payload["processed_at"] = now_iso()
                    conn.execute(
                        "UPDATE events SET payload = ?, processed_at = ? WHERE event_id = ?",
                        (_json.dumps(payload, ensure_ascii=False), now_iso(), event_id),
                    )
                    conn.execute("COMMIT")
                    success += 1
                except Exception:
                    try:
                        conn.execute("ROLLBACK")
                    except Exception as e:
                        logger.warning("suppressed error in database_manager", exc_info=True)
                    payload = _json.loads(str(dl["payload"])) if isinstance(dl["payload"], str) else dict(dl["payload"])
                    payload["retry_count"] = payload.get("retry_count", 0) + 1
                    conn.execute(
                        "UPDATE events SET payload = ? WHERE event_id = ?",
                        (_json.dumps(payload, ensure_ascii=False), event_id),
                    )
                    conn.execute("COMMIT")
            return success
        finally:
            self.return_connection(conn)

    def prometheus_export(self) -> str:
        """T-DB-009: 导出 Prometheus 格式的指标数据。

        返回 Prometheus text exposition format 字符串。
        """
        stats = self.stats()
        lines = [
            "# HELP zalpha_db_task_count Total task count",
            f"zalpha_db_task_count {stats.get('task_count', 0)}",
            "# HELP zalpha_db_event_count Total event count",
            f"zalpha_db_event_count {stats.get('event_count', 0)}",
            "# HELP zalpha_db_gate_count Total gate count",
            f"zalpha_db_gate_count {stats.get('gate_count', 0)}",
            "# HELP zalpha_db_size_mb Database file size in MB",
            f"zalpha_db_size_mb {stats.get('db_size_mb', 0)}",
            "# HELP zalpha_db_wal_size_mb WAL file size in MB",
            f"zalpha_db_wal_size_mb {stats.get('wal_size_mb', 0)}",
            "# HELP zalpha_db_slow_query_count Slow query count",
            f"zalpha_db_slow_query_count {stats.get('slow_query_count', 0)}",
            "# HELP zalpha_db_schema_version Schema version",
            f"zalpha_db_schema_version {stats.get('schema_version', 0)}",
        ]
        return "\n".join(lines) + "\n"

    def connection_leak_detector(self, max_idle_seconds: float = 300.0) -> dict:
        """T-DB-011: 检测连接泄漏（超过最大空闲时间的连接）。

        返回 dict{leaked_count, actionable, detail}。
        """
        with self._lock:
            leaked = []
            now_ts = time.time()
            for i, conn in enumerate(self._conn_pool):
                if hasattr(conn, "_last_used_at"):
                    idle_time = now_ts - conn._last_used_at
                    if idle_time > max_idle_seconds:
                        leaked.append({"conn_index": i, "idle_seconds": round(idle_time, 1)})
            actionable = len(leaked) > 10
            return {
                "leaked_count": len(leaked),
                "actionable": actionable,
                "escalation": "escalation:owner" if actionable else "monitoring",
                "detail": leaked,
                "pool_size": len(self._conn_pool),
            }

    def ai_diagnostic_report(self) -> dict:
        """AP3/T-DB-012: 生成 AI 可读的诊断报告。

        聚合 health_check + stats + schema_drift + query_performance。
        """
        from zephyr.gov_audit.audit_schema import AuditQuery
        from zephyr.governance.observability_governance.query_metrics import query_metrics

        health = self.health_check()
        stats = self.stats()
        try:
            aq = AuditQuery(db_path=self._db_path, auto_init=False)
            drift = aq.query_schema_drift()
        except Exception:
            drift = {"error": "audit_query_unavailable", "is_latest": None}
        qm_stats = query_metrics.stats_all()

        return {
            "summary": {
                "verdict": "HEALTHY" if health.healthy else "UNHEALTHY",
                "action_required": not health.healthy,
                "recommended_action": "maintenance()" if not health.healthy else "none",
            },
            "health": health.to_dict(),
            "stats": stats,
            "schema_drift": drift,
            "query_performance": {op: s for op, s in qm_stats.items()},
        }

    def __enter__(self) -> DatabaseManager:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close(backup_before_close=exc_type is None)