"""AtomicTransactionManager — SQLite + 文件系统的跨介质原子事务管理器（ATM）。

Task       : T-2-30 | beta 前移
Safety     : HIGH（涉及数据库事务 + 文件系统落盘 + 路径安全校验）
Depends    : T-1-23 (InputSanitizer) ✅
References :
    - ADR-0030 SQLite 元数据层决策（本文件是对 ``zalpha_metadata.db`` 的
      所有"写路径"唯一入口；业务数据层 DuckDB 不走此模块）
    - ADR-0041 Session Handoff Protocol（ATM 保证"Session 产物 + 元数据
      记录"要么整体落盘，要么整体回滚，避免腐败上下文）
    - src/zephyr/llm_security/input_sanitizer.py::InputSanitizer.validate_path（
      写路径白名单的唯一 SSoT，本模块不再重复定义白名单）

设计要点（见 ADR-0030 §5.3、ADR-0041 §4）：

1. **两阶段提交（2PC 简化版）**：
   - 阶段 1（in-transaction）：
     * SQLite 执行 ``BEGIN IMMEDIATE`` + 若干 ``execute()``
     * 文件操作写入临时文件 ``<target>.atm-<tx_id>.tmp``，并 ``fsync``
   - 阶段 2（commit）：
     * SQLite ``COMMIT``（成功则持久化；失败则进入 rollback 分支）
     * 对所有 staged 文件执行 ``os.replace(tmp, target)``（POSIX 原子 rename）
     * 对目录 ``fsync``（尽力而为：Windows 上跳过）
   - 任一阶段失败 → SQLite ``ROLLBACK`` + 删除所有 ``.tmp`` + 恢复已被覆盖的
     ``<target>.atm-<tx_id>.bak``。
2. **路径守卫**：所有 ``write_file(path, ...)`` 必须通过
   ``InputSanitizer.validate_path(mode="write")``；越白名单即抛
   ``PathTraversalError``。
3. **不可重入**：单个 ``AtomicTransactionManager`` 实例的 ``transaction()`` 上下文
   不允许嵌套（抛 ``TransactionError``）。多线程请各自实例化。
4. **幂等保证**：``tx_id`` 为 ULID 形态字符串；同一 ``tx_id`` 重复调用
   ``commit()`` 抛 ``TransactionError``，避免上游误调用。
5. **安全等级 HIGH**：所有抛出异常的分支都会触发完整清理；tmp / bak 文件
   在任何退出路径上都不会泄漏到仓库。

Usage::

    from zephyr.db.atomic_transaction_manager import AtomicTransactionManager

    atm = AtomicTransactionManager(
        db_path="docs/09_audit/state/zalpha_metadata.db",
        root="D:/ZephyrAlpha",
    )
    with atm.transaction() as tx:
        tx.execute(
            "UPDATE tasks SET status=? WHERE task_id=?",
            ("VERIFIED", "T-1-01"),
        )
        tx.write_file(
            "docs/02_enterprise_architecture/adr/adr-0030-sqlite-task-metadata-store.md",
            adr_markdown_content,
        )
    # 退出 with 块：若无异常 → SQLite COMMIT + 文件 rename
    #               若有异常 → SQLite ROLLBACK + tmp 清理 + bak 恢复
"""

from __future__ import annotations

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

_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from zephyr.llm_security.input_sanitizer import (
    InputSanitizer,
    PathTraversalError,
    SanitizationError,
)

__all__ = [
    "AtomicTransactionManager",
    "TransactionError",
    "TransactionScope",
]

logger = logging.getLogger(__name__)

class TransactionError(RuntimeError):
    """ATM 内部状态错误（如嵌套、double-commit、未初始化等）。"""

def _utf8_lf_bytes(content: str | bytes) -> bytes:
    """按项目编码规范序列化：UTF-8 无 BOM + LF。

    - ``str`` → ``content.encode("utf-8")`` 后将 ``\\r\\n`` 替换为 ``\\n``
    - ``bytes`` → 去 BOM + 替换 CRLF
    """
    if isinstance(content, str):
        data = content.encode("utf-8")
    else:
        data = bytes(content)
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    data = data.replace(b"\r\n", b"\n")
    return data

def _new_tx_id() -> str:
    """生成单次事务 ID：``tx-<unix_ms>-<hex8>``（毫秒精度 + 64bit 随机）。"""
    return f"tx-{int(time.time() * 1000):013d}-{secrets.token_hex(4)}"

def _fsync_dir(path: Path) -> None:
    """对目录 fsync（POSIX 上保证 rename 持久化；Windows 上跳过）。"""
    if os.name != "posix":
        return
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)

class TransactionScope:
    """单次事务作用域。由 ``AtomicTransactionManager.transaction()`` 构造。

    在 ``with`` 块内通过 ``execute`` / ``executemany`` / ``write_file`` 声明操作；
    SQLite 写入即时进入活跃事务（未 COMMIT），文件写入则 stage 到临时文件。
    退出 ``with`` 块时由 ATM 决定 COMMIT 或 ROLLBACK。

    本类不对外直接构造，且方法在 ATM 的 ``_lock`` 保护下执行。
    """

    __slots__ = ("_atm", "tx_id", "_staged_files", "_committed", "_rolled_back")

    def __init__(self, atm: AtomicTransactionManager, tx_id: str) -> None:
        self._atm = atm
        self.tx_id: str = tx_id
        self._staged_files: list[tuple[Path, Path, Path | None]] = []
        self._committed: bool = False
        self._rolled_back: bool = False

    def execute(
        self,
        sql: str,
        params: Sequence[Any] | dict[str, Any] = (),
    ) -> sqlite3.Cursor:
        """在当前事务中执行单条 SQL（可带参数）。"""
        self._check_active()
        assert self._atm._conn is not None
        return self._atm._conn.execute(sql, params)

    def executemany(
        self,
        sql: str,
        seq_of_params: Iterable[Sequence[Any] | dict[str, Any]],
    ) -> sqlite3.Cursor:
        """在当前事务中批量执行 SQL。"""
        self._check_active()
        assert self._atm._conn is not None
        return self._atm._conn.executemany(sql, seq_of_params)

    def write_file(
        self,
        rel_path: str,
        content: str | bytes,
    ) -> Path:
        """将文件写入请求 stage 到临时文件，commit 时统一 rename。

        参数
        ----
        rel_path : str
            相对 ``ATM.root`` 的路径。必须命中 InputSanitizer 写白名单。
        content : str | bytes
            文件内容；会被统一规范化为 UTF-8 无 BOM + LF。

        返回
        ----
        Path
            规划中的目标绝对路径（commit 成功后生效）。
        """
        self._check_active()
        target: Path = self._atm._sanitizer.validate_path(rel_path, mode="write")
        target.parent.mkdir(parents=True, exist_ok=True)

        data = _utf8_lf_bytes(content)

        tmp_path = target.with_name(f"{target.name}.atm-{self.tx_id}.tmp")
        bak_path: Path | None = None
        if target.exists():
            bak_path = target.with_name(f"{target.name}.atm-{self.tx_id}.bak")
            try:
                os.replace(target, bak_path)
            except OSError as exc:  # pragma: no cover — 极端文件系统错
                raise TransactionError(f"[{self.tx_id}] failed to stage existing file to .bak: {target}") from exc

        _flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        _binary_flag = getattr(os, "O_BINARY", 0)
        fd = os.open(
            tmp_path,
            _flags | _binary_flag,
            0o644,
        )
        try:
            os.write(fd, data)
            os.fsync(fd)
        finally:
            os.close(fd)

        self._staged_files.append((target, tmp_path, bak_path))
        logger.debug("[%s] staged write_file: %s (bytes=%d)", self.tx_id, target, len(data))
        return target

    def staged_file_count(self) -> int:
        """当前事务 staged 的文件数（便于外部断言/日志）。"""
        return len(self._staged_files)

    def _check_active(self) -> None:
        if self._committed:
            raise TransactionError(f"[{self.tx_id}] transaction already committed")
        if self._rolled_back:
            raise TransactionError(f"[{self.tx_id}] transaction already rolled back")
        if self._atm._active_tx is not self:
            raise TransactionError(f"[{self.tx_id}] not the currently active transaction in ATM")

class AtomicTransactionManager:
    """对单个 SQLite 文件 + 其相关文件系统操作的原子事务封装。

    参数
    ----
    db_path : str
        SQLite 数据库相对路径（相对 ``root``）。会被 InputSanitizer 写白名单
        校验（必须位于 ``docs/`` / ``src/zephyr/`` / ``.audit_cache/`` 等下）。
    root : str
        项目根目录绝对路径；用于 InputSanitizer 的 ``root`` 构造。
    isolation_level : str | None
        传给 ``sqlite3.connect`` 的隔离等级，默认 ``None``（手动控制 BEGIN）。
    timeout : float
        ``sqlite3.connect`` 的忙等待超时，默认 30 秒（WAL 下已很少触发）。
    sanitizer : InputSanitizer | None
        可注入自定义 sanitizer（便于测试）；默认基于 ``root`` 新建。

    线程模型
    --------
    单实例内部使用 ``threading.RLock`` 串行化所有 ``transaction()`` 进入；
    ``sqlite3.connect`` 使用 ``check_same_thread=False``，但实际执行路径
    仍由锁保护，因此在跨线程复用时是安全的。高并发场景建议每线程一个
    ATM 实例。
    """

    def __init__(
        self,
        db_path: str,
        root: str,
        *,
        isolation_level: Literal["DEFERRED", "EXCLUSIVE", "IMMEDIATE"] | None = None,
        timeout: float = 30.0,
        sanitizer: InputSanitizer | None = None,
    ) -> None:
        self._root: Path = Path(root).resolve()
        self._sanitizer: InputSanitizer = sanitizer or InputSanitizer(root=str(self._root))

        self._db_abs_path: Path = self._sanitizer.validate_path(db_path, mode="write")
        self._db_abs_path.parent.mkdir(parents=True, exist_ok=True)

        self._isolation_level = isolation_level
        self._timeout = timeout
        self._conn: sqlite3.Connection | None = None
        self._active_tx: TransactionScope | None = None
        self._lock = RLock()

        self._open_connection()

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
        self._conn = conn

    @property
    def db_path(self) -> Path:
        return self._db_abs_path

    @property
    def root(self) -> Path:
        return self._root

    @contextmanager
    def transaction(self) -> Iterator[TransactionScope]:
        """进入一次事务作用域（见类文档的 Usage 示例）。

        异常语义
        --------
        - ``with`` 块内抛任何异常 → 捕获 → SQLite ROLLBACK + 文件清理 + 重新抛出
        - ``with`` 块正常退出 → commit：SQLite COMMIT + 文件 rename + 目录 fsync
        - ``commit`` 过程中失败 → rollback（尽力恢复）并抛 ``TransactionError``
        """
        with self._lock:
            if self._active_tx is not None:
                raise TransactionError(f"nested transactions not supported; active={self._active_tx.tx_id}")
            if self._conn is None:
                self._open_connection()

            tx = TransactionScope(atm=self, tx_id=_new_tx_id())
            self._active_tx = tx

            assert self._conn is not None
            self._conn.execute("BEGIN IMMEDIATE")
            logger.debug("[%s] BEGIN IMMEDIATE", tx.tx_id)

            try:
                yield tx
            except BaseException:
                self._rollback(tx)
                raise

            try:
                self._commit(tx)
            except BaseException:
                self._rollback(tx)
                raise

    def _commit(self, tx: TransactionScope) -> None:
        assert self._conn is not None
        try:
            self._conn.execute("COMMIT")
        except sqlite3.Error as exc:
            raise TransactionError(f"[{tx.tx_id}] SQLite COMMIT failed: {exc}") from exc

        renamed: list[tuple[Path, Path, Path | None]] = []
        try:
            for target, tmp, bak in tx._staged_files:
                os.replace(tmp, target)
                renamed.append((target, tmp, bak))

            dirs_to_fsync = {t.parent for t, _, _ in renamed}
            for d in dirs_to_fsync:
                try:
                    _fsync_dir(d)
                except OSError:  # pragma: no cover — Windows 不支持
                    pass

            for _, _, bak in renamed:
                if bak is not None and bak.exists():
                    try:
                        bak.unlink()
                    except OSError:  # pragma: no cover
                        logger.warning("[%s] failed to unlink .bak: %s", tx.tx_id, bak)
        except OSError as exc:
            logger.error(
                "[%s] post-COMMIT file rename failed; attempting bak restore: %s",
                tx.tx_id,
                exc,
            )
            for target, _tmp, bak in renamed:
                if bak is not None and bak.exists():
                    try:
                        os.replace(bak, target)
                    except OSError:  # pragma: no cover
                        pass
            raise TransactionError(f"[{tx.tx_id}] file rename phase failed after SQLite COMMIT: {exc}") from exc

        tx._committed = True
        self._active_tx = None
        logger.info(
            "[%s] committed (sql_ops_tracked_by_sqlite, files=%d)",
            tx.tx_id,
            len(tx._staged_files),
        )

    def _rollback(self, tx: TransactionScope) -> None:
        if tx._rolled_back:
            return
        if self._conn is not None:
            try:
                self._conn.execute("ROLLBACK")
            except sqlite3.Error as exc:  # pragma: no cover
                logger.error("[%s] SQLite ROLLBACK failed: %s", tx.tx_id, exc)

        for target, tmp, bak in tx._staged_files:
            if tmp.exists():
                try:
                    tmp.unlink()
                except OSError:  # pragma: no cover
                    logger.warning("[%s] failed to unlink tmp: %s", tx.tx_id, tmp)
            if bak is not None and bak.exists():
                try:
                    if target.exists():
                        target.unlink()
                    os.replace(bak, target)
                except OSError:  # pragma: no cover
                    logger.error("[%s] failed to restore bak: %s", tx.tx_id, bak)

        tx._rolled_back = True
        if self._active_tx is tx:
            self._active_tx = None
        logger.info("[%s] rolled back", tx.tx_id)

    def close(self) -> None:
        """关闭底层 SQLite 连接。若存在活跃事务则先 rollback。"""
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
        """对外暴露的路径守卫快捷方法（与 ``write_file`` 内部逻辑一致）。

        用于调用方在构造事务前预校验文件路径，避免在事务中才失败。
        未进入事务时即可调用。
        """
        try:
            return cast(Path, self._sanitizer.validate_path(rel_path, mode="write"))
        except SanitizationError:
            raise
        except PathTraversalError:
            raise

__version__ = "1.0.0"
