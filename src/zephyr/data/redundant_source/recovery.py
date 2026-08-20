# [BLUEPRINT] MOD-L00-005 | docs/03_modules/_domain_data/redundant_source_blueprint.md
# [A_module] module_id=MOD-L00-005 | layer=module | stability=evolving | safety=M
# [TTL] permanent
"""CH 恢复后 SQLite→CH 回灌管理器。

设计：
- 监听 HeartbeatMonitor 的 CH 状态变化
- CH 恢复后，按 batch 从 SQLiteFallback 读取数据回灌到 CH
- 回灌成功后删除 SQLite 中已回灌的批次
- 回灌失败指数退避（2s→4s→...→60s 封顶）

Usage::

    recovery = RecoveryManager(sqlite_fallback, heartbeat_monitor)
    recovery.start()  # CH 恢复后自动回灌
"""

from __future__ import annotations

import logging
import threading
import time

from zephyr.data.redundant_source.heartbeat_monitor import HeartbeatMonitor
from zephyr.data.redundant_source.sqlite_fallback import SQLiteFallback
from zephyr.shared.observability.metrics import get_registry

log = logging.getLogger(__name__)

_RECOVERY_CHECK_INTERVAL = 10.0  # CH 恢复检测间隔（秒）
_BATCH_SIZE = 1000  # 每次回灌的行数
_BACKOFF_INIT = 2.0  # 初始退避（秒）
_BACKOFF_MAX = 60.0  # 最大退避（秒）
_TABLES_TO_RECOVER = ["tick_data"]  # 需要回灌的表


class RecoveryManager:
    """CH 恢复后 SQLite→CH 回灌管理器。

    线程安全：回灌操作在独立线程中执行，通过 _running 标志控制。
    """

    def __init__(
        self,
        sqlite_fallback: SQLiteFallback,
        heartbeat: HeartbeatMonitor,
        tables: list[str] | None = None,
        batch_size: int = _BATCH_SIZE,
        check_interval: float = _RECOVERY_CHECK_INTERVAL,
    ) -> None:
        self._sqlite = sqlite_fallback
        self._heartbeat = heartbeat
        self._tables = tables or list(_TABLES_TO_RECOVER)
        self._batch_size = batch_size
        self._check_interval = check_interval

        self._running = False
        self._thread: threading.Thread | None = None
        self._recovering = False
        self._registry = get_registry()

    def start(self) -> None:
        """启动回灌检测线程。"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._recovery_loop, daemon=True, name="recovery-manager")
        self._thread.start()
        log.info("RecoveryManager 已启动 (tables=%s)", self._tables)

    def stop(self) -> None:
        """停止回灌检测线程。"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10.0)
            self._thread = None

    def is_recovering(self) -> bool:
        """是否正在回灌中。"""
        return self._recovering

    def _recovery_loop(self) -> None:
        """回灌检测循环。"""
        while self._running:
            try:
                if self._heartbeat.is_ch_alive():
                    self._do_recovery()
                else:
                    self._recovering = False
            except Exception as e:  # noqa: BLE001
                log.error("RecoveryManager 异常: %s", e, exc_info=True)
                self._recovering = False
            time.sleep(self._check_interval)

    def _do_recovery(self) -> None:
        """执行回灌（CH 可达时）。"""
        any_pending = any(self._sqlite.get_pending_count(t) > 0 for t in self._tables)
        if not any_pending:
            self._recovering = False
            return

        self._recovering = True
        log.info("CH 已恢复，开始 SQLite→CH 回灌")

        backoff = _BACKOFF_INIT
        for table in self._tables:
            self._recover_table(table, backoff)

        self._recovering = False

    def _recover_table(self, table: str, backoff: float) -> None:
        """回灌单个表。"""
        from zephyr.data import ch_writer

        consecutive_failures = 0
        while self._running:
            cols, rows = self._sqlite.get_pending_batch(table, self._batch_size)
            if not rows:
                log.info("表 %s 回灌完成", table)
                break

            try:
                # 构造 TSV 并写入 CH
                tsv_lines = []
                for row in rows:
                    tsv_lines.append("\t".join(str(v) if v is not None else "\\N" for v in row))
                tsv_bytes = ("\n".join(tsv_lines) + "\n").encode("utf-8")
                cols_clause = "(" + ", ".join(cols) + ")"
                ok = ch_writer.write_tsv(f"c1_market.{table}", cols_clause, tsv_bytes)

                if ok:
                    deleted = self._sqlite.delete_batch(table, len(rows))
                    self._registry.inc("zephyr_recovery_replayed_total", n=deleted)
                    backoff = _BACKOFF_INIT
                    consecutive_failures = 0
                    log.info("表 %s 回灌 %d 行成功", table, deleted)
                else:
                    consecutive_failures += 1
                    backoff = min(backoff * 2, _BACKOFF_MAX)
                    log.warning("表 %s 回灌失败 %d 次，退避 %.1fs", table, consecutive_failures, backoff)
                    self._registry.inc("zephyr_recovery_failed_total")
                    time.sleep(backoff)
            except Exception as e:  # noqa: BLE001
                consecutive_failures += 1
                backoff = min(backoff * 2, _BACKOFF_MAX)
                log.error("表 %s 回灌异常: %s，退避 %.1fs", table, e, backoff)
                self._registry.inc("zephyr_recovery_failed_total")
                time.sleep(backoff)
