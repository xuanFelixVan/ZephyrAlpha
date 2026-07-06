# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.governance.financial_governance.atomic_transaction_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-DAT_atomic_transaction_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""AtomicTransactionManager — SQLite + 文件系统的跨介质原子事务管理器 v2.0（ATM）。

Task       : T-2-30 | SH-DB-001 v2.0
Safety     : HIGH（涉及数据库事务 + 文件系统落盘 + 路径安全校验）
Depends    : T-1-23 (InputSanitizer) ✅
References :


设计要点 v2.0（见 SH-DB-001 blueprint v2.0）：

1. **两阶段提交（2PC 简化版）**：
   - 阶段 1（in-transaction）：
     * SQLite 执行 ``BEGIN IMMEDIATE`` + 若干 ``execute()``
     * 文件操作写入临时文件 ``<target>.atm-<tx_id>.tmp``，并 ``fsync``
     * 在 tx_idempotency 表登记为 PREPARED（防止重复提交）
   - 阶段 2（commit）：
     * 预验证所有 tmp 文件存在且可读
     * SQLite ``COMMIT``
     * 对所有 staged 文件执行 ``os.replace(tmp, target)``
     * 对目录 ``fsync``（POSIX）
     * 更新 tx_idempotency 为 COMMITTED
   - 任一阶段失败 → SQLite ``ROLLBACK`` + 删除 tmp + bak 恢复
   - 文件 rename 失败但 SQLite 已 COMMIT → 写 compensation event + 标记 COMPENSATED

2. **事务超时**：每个 transaction 有超时限制（默认 30s）。超时自动 ROLLBACK。

3. **幂等保证**：同一 tx_id 重复调用 commit() 抛 TransactionError（tx_idempotency 去重）。

4. **路径守卫**：所有 write_file(path, ...) 必须通过 InputSanitizer.validate_path。

Usage::

    from zephyr.governance.financial_governance.atomic_transaction_manager import AtomicTransactionManager

    atm = AtomicTransactionManager(
        db_path="data/databases/governance.db",
        root="D:/ZephyrAlpha",
    )
    with atm.transaction() as tx:
        tx.execute("UPDATE tasks SET status=? WHERE task_id=?", ("VERIFIED", "T-1-01"))
        tx.write_file("docs/02_enterprise_architecture/architecture-rationale-log.md", content)
"""

from __future__ import annotations

from typing import Final
import importlib
import json
import logging
import os
import secrets
import sqlite3
import sys
import time
from collections.abc import Iterable, Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from typing import Any, Literal, cast

from zephyr.shared.io.paths import REPO_ROOT
_SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

_SECURITY_SANITIZER_NAMES = {
    "InputSanitizer",
    "PathTraversalError",
    "SanitizationError",
}


def __getattr__(name):
    if name in _SECURITY_SANITIZER_NAMES:
        _mod = importlib.import_module("zephyr.security.llm_defense.llm_security.input_sanitizer")
        _val = getattr(_mod, name)
        globals()[name] = _val
        return _val
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AtomicTransactionManager",
    "TransactionError",
    "TransactionScope",
    "TransactionTimeoutError",
]

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS: Final[float] = 30.0


class TransactionError(RuntimeError):
    """ATM 内部状态错误（嵌套、double-commit、未初始化等）。

    5.99.20 修复：tx_id 和文件路径移至 details 字段，不暴露在消息中。
    """
    error_code = "ZA-GV-0021"

    def __init__(self, message: str, *, details: dict[str, Any] | None = None, error_code: str | None = None) -> None:
        super().__init__(message)
        self.details: dict[str, Any] = details or {}
        if error_code is not None:
            self.error_code = error_code


class TransactionTimeoutError(TransactionError):
    """事务超时。"""
    error_code = "ZA-GV-0022"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


def _utf8_lf_bytes(content: str | bytes) -> bytes:
    """序列化为 UTF-8 无 BOM + LF。"""
    if isinstance(content, str):
        data = content.encode("utf-8")
    else:
        data = bytes(content)
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    data = data.replace(b"\r\n", b"\n")
    return data


def _new_tx_id() -> str:
    """生成单次事务 ID：tx-<unix_ms>-<hex8>。"""
    return f"tx-{int(time.time() * 1000):013d}-{secrets.token_hex(4)}"


def _fsync_dir(path: Path) -> None:
    """对目录 fsync（POSIX；Windows 跳过）。"""
    if os.name != "posix":
        return
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _now_iso() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat()


class TransactionScope:
    """单次事务作用域。对 ATM 外部不可直接构造。"""

    __slots__ = (
        "_atm",
        "_committed",
        "_rolled_back",
        "_staged_files",
        "_started_at",
        "_timeout",
        "tx_id",
    )

    def __init__(
        self,
        atm: AtomicTransactionManager,
        tx_id: str,
        timeout: float,
    ) -> None:
        self._atm = atm
        self.tx_id: str = tx_id
        self._staged_files: list[tuple[Path, Path, Path | None]] = []
        self._committed: bool = False
        self._rolled_back: bool = False
        self._started_at: float = time.monotonic()
        self._timeout: float = timeout

    def _check_timeout(self) -> None:
        elapsed = time.monotonic() - self._started_at
        if elapsed > self._timeout:
            raise TransactionTimeoutError(
                f"transaction timeout ({elapsed:.1f}s > {self._timeout}s)",
                details={"tx_id": self.tx_id},
            )

    def execute(
        self,
        sql: str,
        params: Sequence[Any] | dict[str, Any] = (),
    ) -> sqlite3.Cursor:
        """在当前事务中执行单条 SQL（参数化查询）。"""
        self._check_active()
        self._check_timeout()
        if self._atm._conn is None: raise RuntimeError("connection not established")  # 5.88.1 修复: assert→if/raise
        return self._atm._conn.execute(sql, params)

    def executemany(
        self,
        sql: str,
        seq_of_params: Iterable[Sequence[Any] | dict[str, Any]],
    ) -> sqlite3.Cursor:
        """在当前事务中批量执行 SQL。"""
        self._check_active()
        self._check_timeout()
        if self._atm._conn is None: raise RuntimeError("connection not established")  # 5.88.1 修复: assert→if/raise
        return self._atm._conn.executemany(sql, seq_of_params)

    def write_file(
        self,
        rel_path: str,
        content: str | bytes,
    ) -> Path:
        """将文件写入 stage 到临时文件，commit 时统一 rename。

        参数
        ----
        rel_path : str
            相对 ATM.root 的路径。必须命中 InputSanitizer 写白名单。
        content : str | bytes
            文件内容；统一规范化为 UTF-8 无 BOM + LF。

        返回
        ----
        Path
            规划中的目标绝对路径（commit 成功后生效）。
        """
        self._check_active()
        self._check_timeout()
        target: Path = self._atm._sanitizer.validate_path(rel_path, mode="write")
        target.parent.mkdir(parents=True, exist_ok=True)

        data = _utf8_lf_bytes(content)

        tmp_path = target.with_name(f"{target.name}.atm-{self.tx_id}.tmp")
        bak_path: Path | None = None
        if target.exists():
            bak_path = target.with_name(f"{target.name}.atm-{self.tx_id}.bak")
            try:
                os.replace(target, bak_path)
            except OSError as exc:
                raise TransactionError(
                    "failed to stage existing file to .bak",
                    details={"tx_id": self.tx_id, "target": str(target)},
                ) from exc

        _flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        _binary_flag = getattr(os, "O_BINARY", 0)
        fd = os.open(tmp_path, _flags | _binary_flag, 0o600)  # 5.17.12 修复：事务临时文件权限收紧至 0o600
        try:
            os.write(fd, data)
            os.fsync(fd)
        finally:
            os.close(fd)

        self._staged_files.append((target, tmp_path, bak_path))
        logger.debug("[%s] staged write_file: %s (bytes=%d)", self.tx_id, target, len(data))
        return target

    def staged_file_count(self) -> int:
        """当前事务 staged 的文件数。"""
        return len(self._staged_files)

    def _check_active(self) -> None:
        if self._committed:
            raise TransactionError(
                "transaction already committed",
                details={"tx_id": self.tx_id},
            )
        if self._rolled_back:
            raise TransactionError(
                "transaction already rolled back",
                details={"tx_id": self.tx_id},
            )
        if self._atm._active_tx is not self:
            raise TransactionError(
                "not the currently active transaction in ATM",
                details={"tx_id": self.tx_id},
            )


class AtomicTransactionManager:
    """对 SQLite + 文件系统的原子事务封装 v2.0。

    参数
    ----
    db_path
        SQLite 数据库相对路径（相对 root），由 InputSanitizer 校验。
    root
        项目根目录绝对路径。
    isolation_level
        sqlite3.connect 的隔离等级，默认 None（手动 BEGIN）。
    timeout
        sqlite3.connect 的 busy_timeout，默认 30s。
    tx_timeout
        事务级超时（秒），默认 30s。超时自动 ROLLBACK。
    sanitizer
        可注入自定义 InputSanitizer（便于测试）。

    线程模型
    --------
    单实例内部使用 threading.RLock 串行化所有 transaction()。
    跨线程复用安全。高并发建议每线程一个 ATM 实例。
    """

    def __init__(
        self,
        db_path: str,
        root: str,
        *,
        isolation_level: Literal["DEFERRED", "EXCLUSIVE", "IMMEDIATE"] | None = None,
        timeout: float = 30.0,
        tx_timeout: float = DEFAULT_TIMEOUT_SECONDS,
        sanitizer: InputSanitizer | None = None,
    ) -> None:
        self._root: Path = Path(root).resolve()
        self._sanitizer: InputSanitizer = sanitizer or InputSanitizer(root=str(self._root))

        self._db_abs_path: Path = self._sanitizer.validate_path(db_path, mode="write")
        self._db_abs_path.parent.mkdir(parents=True, exist_ok=True)

        self._isolation_level = isolation_level
        self._timeout = timeout
        self._tx_timeout = tx_timeout
        self._conn: sqlite3.Connection | None = None
        self._active_tx: TransactionScope | None = None
        self._lock = RLock()

        self._open_connection()
        self._ensure_tx_idempotency_table()

    def _open_connection(self) -> None:
        conn = sqlite3.connect(
            str(self._db_abs_path),
            isolation_level=self._isolation_level,
            timeout=self._timeout,
            check_same_thread=False,
        )
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 5000")
        conn.execute("PRAGMA wal_autocheckpoint = 4096")
        self._conn = conn

    def _ensure_tx_idempotency_table(self) -> None:
        """确保 tx_idempotency 表存在（幂等）。"""
        if self._conn is None: raise RuntimeError("connection not established")  # 5.88.1 修复: assert→if/raise
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tx_idempotency (
                tx_id           TEXT PRIMARY KEY,
                status          TEXT NOT NULL CHECK(status IN ('PREPARED','COMMITTED','ROLLED_BACK','COMPENSATED')),
                started_at      TEXT NOT NULL,
                committed_at    TEXT,
                rolled_back_at  TEXT,
                compensation_at TEXT,
                note            TEXT NOT NULL DEFAULT ''
            )
            """
        )

    @property
    def db_path(self) -> Path:
        return self._db_abs_path

    @property
    def root(self) -> Path:
        return self._root

    @contextmanager
    def transaction(self) -> Iterator[TransactionScope]:
        """进入一次事务作用域。

        异常语义
        --------
        - with 块内抛任何异常 → ROLLBACK + 文件清理 + 重新抛出
        - with 块正常退出 → COMMIT
        - commit 过程中失败 → ROLLBACK（尽力）+ compensating event + re-raise
        - 超时 → ROLLBACK + TransactionTimeoutError
        """
        with self._lock:
            if self._active_tx is not None:
                raise TransactionError(
                    "nested transactions not supported",
                    details={"active_tx_id": self._active_tx.tx_id},
                )
            if self._conn is None:
                self._open_connection()

            tx = TransactionScope(atm=self, tx_id=_new_tx_id(), timeout=self._tx_timeout)
            self._active_tx = tx

            if self._conn is None: raise RuntimeError("connection not established")  # 5.88.1 修复: assert→if/raise
            self._conn.execute("BEGIN IMMEDIATE")

            # 登记到幂等去重表
            self._conn.execute(
                "INSERT OR IGNORE INTO tx_idempotency (tx_id, status, started_at, note) VALUES (?, 'PREPARED', ?, '')",
                (tx.tx_id, _now_iso()),
            )
            # 检查是否重复（tx_id 已存在 → 重复提交）
            row = self._conn.execute("SELECT status FROM tx_idempotency WHERE tx_id = ?", (tx.tx_id,)).fetchone()
            if row and row[0] != "PREPARED":
                self._conn.execute("ROLLBACK")
                self._active_tx = None
                raise TransactionError(
                    f"duplicate transaction: already {row[0]}",
                    details={"tx_id": tx.tx_id, "status": row[0]},
                )

            logger.debug("[%s] BEGIN IMMEDIATE + PREPARED", tx.tx_id)

            try:
                yield tx
            except BaseException:
                self._rollback(tx)
                raise

            # 超时检查
            elapsed = time.monotonic() - tx._started_at
            if elapsed > self._tx_timeout:
                self._rollback(tx)
                raise TransactionTimeoutError(
                    f"transaction timeout ({elapsed:.1f}s > {self._tx_timeout}s)",
                    details={"tx_id": tx.tx_id},
                )

            try:
                self._commit(tx)
            except BaseException:
                self._rollback(tx)
                raise

    def _pre_commit_verify(self, tx: TransactionScope) -> None:
        """预验证所有 staged 的 tmp 文件存在且可读。"""
        for target, tmp, _bak in tx._staged_files:
            if not tmp.exists():
                raise TransactionError(
                    "pre-commit verify failed: tmp file missing",
                    details={"tx_id": tx.tx_id, "tmp_file": str(tmp)},
                )
            if tmp.stat().st_size == 0:
                raise TransactionError(
                    "pre-commit verify failed: tmp file empty",
                    details={"tx_id": tx.tx_id, "tmp_file": str(tmp)},
                )

    def _write_compensation_event(self, tx: TransactionScope) -> None:
        """SQLite COMMIT 已成功但文件 rename 失败时，写入补偿事件。"""
        if self._conn is None: raise RuntimeError("connection not established")  # 5.88.1 修复: assert→if/raise
        try:
            self._conn.execute(
                """
                INSERT INTO events
                    (event_id, event_type, payload, task_id, session_id, created_at)
                VALUES (?, 'compensation', ?, ?, ?, ?)
                """,
                (
                    f"ev-{tx.tx_id}",
                    json.dumps(
                        {
                            "action": "compensating_transaction",
                            "tx_id": tx.tx_id,
                            "note": "SQLite committed but file rename failed",
                        },
                        ensure_ascii=False,
                    ),
                    None,
                    None,
                    _now_iso(),
                ),
            )
            self._conn.execute(
                "UPDATE tx_idempotency SET status='COMPENSATED', compensation_at=? WHERE tx_id=?",
                (_now_iso(), tx.tx_id),
            )
        except sqlite3.Error as exc:
            logger.error("[%s] failed to write compensation event: %s", tx.tx_id, exc)

    def _commit(self, tx: TransactionScope) -> None:
        if self._conn is None: raise RuntimeError("connection not established")  # 5.88.1 修复: assert→if/raise

        self._pre_commit_verify(tx)

        try:
            self._conn.execute("COMMIT")
        except sqlite3.Error as exc:
            raise TransactionError(
                "SQLite COMMIT failed",
                details={"tx_id": tx.tx_id, "error": str(exc)},
            ) from exc

        try:
            self._conn.execute(
                "UPDATE tx_idempotency SET status='COMMITTED', committed_at=? WHERE tx_id=?",
                (_now_iso(), tx.tx_id),
            )
        except sqlite3.Error:
            pass  # 尽力更新，失败不影响事务已提交的事实

        # 文件 rename 阶段
        renamed: list[tuple[Path, Path, Path | None]] = []
        try:
            for target, tmp, bak in tx._staged_files:
                os.replace(tmp, target)
                renamed.append((target, tmp, bak))

            dirs_to_fsync = {t.parent for t, _, _ in renamed}
            for d in dirs_to_fsync:
                try:
                    _fsync_dir(d)
                except OSError:
                    pass

            for _, _, bak in renamed:
                if bak is not None and bak.exists():
                    try:
                        bak.unlink()
                    except OSError:
                        logger.warning("[%s] failed to unlink .bak: %s", tx.tx_id, bak)

        except OSError as exc:
            logger.error(
                "[%s] post-COMMIT file rename failed; writing compensation event: %s",
                tx.tx_id,
                exc,
            )
            self._write_compensation_event(tx)
            for target, _tmp, bak in renamed:
                if bak is not None and bak.exists():
                    try:
                        os.replace(bak, target)
                    except OSError:
                        pass
            raise TransactionError(
                "file rename phase failed after SQLite COMMIT",
                details={"tx_id": tx.tx_id, "error": str(exc)},
            ) from exc

        tx._committed = True
        self._active_tx = None
        logger.info(
            "[%s] committed (files=%d)",
            tx.tx_id,
            len(tx._staged_files),
        )

    def _rollback(self, tx: TransactionScope) -> None:
        if tx._rolled_back:
            return

        if self._conn is None: raise RuntimeError("connection not established")  # 5.88.1 修复: assert→if/raise
        try:
            self._conn.execute("ROLLBACK")
        except sqlite3.Error as exc:
            logger.error("[%s] SQLite ROLLBACK failed: %s", tx.tx_id, exc)

        try:
            self._conn.execute(
                "UPDATE tx_idempotency SET status='ROLLED_BACK', rolled_back_at=? WHERE tx_id=?",
                (_now_iso(), tx.tx_id),
            )
        except sqlite3.Error:
            pass

        for target, tmp, bak in tx._staged_files:
            if tmp.exists():
                try:
                    tmp.unlink()
                except OSError:
                    logger.warning("[%s] failed to unlink tmp: %s", tx.tx_id, tmp)
            if bak is not None and bak.exists():
                try:
                    if target.exists():
                        target.unlink()
                    os.replace(bak, target)
                except OSError:
                    logger.error("[%s] failed to restore bak: %s", tx.tx_id, bak)

        tx._rolled_back = True
        if self._active_tx is tx:
            self._active_tx = None
        logger.info("[%s] rolled back", tx.tx_id)

    def close(self) -> None:
        """关闭底层 SQLite 连接。有活跃事务则先 rollback。"""
        with self._lock:
            if self._active_tx is not None:
                self._rollback(self._active_tx)
            if self._conn is not None:
                self._conn.close()
                self._conn = None

    def __enter__(self) -> AtomicTransactionManager:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def validate_write_path(self, rel_path: str) -> Path:
        """对外暴露的路径守卫快捷方法（与 write_file 内部逻辑一致）。"""
        try:
            return cast(Path, self._sanitizer.validate_path(rel_path, mode="write"))
        except SanitizationError:
            raise
        except PathTraversalError:
            raise
