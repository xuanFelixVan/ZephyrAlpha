# [BLUEPRINT] MOD-L00-007 | docs/03_modules/_domain_data/redundant_source_blueprint.md
# [A_module] module_id=MOD-L00-007 | layer=module | stability=evolving | safety=M
# [TTL] permanent
"""备源 Tick 轮询器——主源中断时自动切换到 TDX 备源（P1-3）。

设计：
- TDXBackupProvider 实现 SourceProvider 接口，封装 TDXProvider.fetch_tick_snapshot
- 轮询线程定期拉取 TDX 实时快照，转换为 QMT tick dict 喂入 TickSubscriber 队列
- QMTSourceProvider 是 QMT 主源的被动适配器（stop=no-op，保持订阅用于恢复检测）
- SourceSwitcher 基于 HeartbeatMonitor 自动切换主源/备源

架构：
    QMT (push) ──→ _on_tick ──→ queue ──→ _drain_batch ──→ WalWriter
                                    ↑
    TDX (poll) ──→ fetch_tick_snapshot ──→ callback ──→ queue

Usage::

    from zephyr.data.redundant_source.backup_tick_poller import (
        BackupTickPoller, QMTSourceAdapter,
    )
    backup = BackupTickPoller(tdx_provider, symbols, on_tick_callback)
    switcher = SourceSwitcher(QMTSourceAdapter(sub), backup, heartbeat)
    switcher.start()
"""
from __future__ import annotations

import logging
import threading
import time
from typing import TYPE_CHECKING

from zephyr.data.redundant_source.source_switcher import SourceProvider

if TYPE_CHECKING:
    from zephyr.data.implementations.tdx_provider import TDXProvider

log = logging.getLogger(__name__)

_BACKUP_POLL_INTERVAL = 3.0  # 备源轮询间隔（秒）


class QMTSourceAdapter(SourceProvider):
    """QMT 主源被动适配器——SourceSwitcher 用。

    QMT 订阅由 TickSubscriber.start() 管理，本适配器仅向 SourceSwitcher
    暴露 SourceProvider 接口。stop() 为 no-op（保持 QMT 订阅活跃，
    让 HeartbeatMonitor 检测主源恢复）。
    """

    def __init__(self, subscriber) -> None:
        self._sub = subscriber

    def name(self) -> str:
        return "qmt"

    def start(self) -> bool:
        # QMT 订阅由 TickSubscriber.start() 管理，此处 no-op
        return True

    def stop(self) -> None:
        # no-op: 保持 QMT 订阅活跃，让 heartbeat 检测恢复
        log.info("QMTSourceAdapter.stop() no-op (保持 QMT 订阅活跃用于恢复检测)")

    def is_running(self) -> bool:
        return getattr(self._sub, "_running", False)


class BackupTickPoller(SourceProvider):
    """TDX 备源轮询器——实现 SourceProvider 接口。

    start() 启动轮询线程，定期调用 TDXProvider.fetch_tick_snapshot
    获取实时快照，通过回调喂入 TickSubscriber 队列。
    stop() 停止轮询线程（不断开 TDX 连接，便于快速重启）。

    线程安全：_running 标志 + Event 协调。
    """

    def __init__(
        self,
        tdx_provider: "TDXProvider",
        symbols: list[str],
        on_tick_callback,
        poll_interval: float = _BACKUP_POLL_INTERVAL,
    ) -> None:
        """初始化备源轮询器。

        Args:
            tdx_provider: TDXProvider 实例（已连接或待连接）
            symbols: QMT 格式标的列表，如 ["000001.SZ", "600000.SH"]
            on_tick_callback: 回调函数，签名 (symbol: str, tick: dict) -> None
            poll_interval: 轮询间隔（秒，默认 3.0）
        """
        self._tdx = tdx_provider
        self._symbols = symbols
        self._on_tick = on_tick_callback
        self._poll_interval = poll_interval
        self._running = False
        self._thread: threading.Thread | None = None

    def name(self) -> str:
        return "tdx"

    def start(self) -> bool:
        """启动轮询线程。Returns True if started successfully."""
        if self._running:
            return True
        # 确保 TDX 已连接
        if not self._tdx._connected:
            try:
                self._tdx.connect()
            except Exception as e:  # noqa: BLE001
                log.error("TDX 备源连接失败: %s", e)
                return False
        self._running = True
        self._thread = threading.Thread(
            target=self._poll_loop, daemon=True, name="tdx-backup-poller"
        )
        self._thread.start()
        log.info("BackupTickPoller 已启动 (symbols=%d, interval=%.1fs)",
                 len(self._symbols), self._poll_interval)
        return True

    def stop(self) -> None:
        """停止轮询线程（不断开 TDX 连接）。"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None
        log.info("BackupTickPoller 已停止")

    def is_running(self) -> bool:
        return self._running and self._thread is not None and self._thread.is_alive()

    def _poll_loop(self) -> None:
        """轮询循环——定期拉取 TDX 快照喂入回调。"""
        while self._running:
            t0 = time.time()
            try:
                results = self._tdx.fetch_tick_snapshot(self._symbols)
                for symbol, tick in results:
                    if not self._running:
                        break
                    try:
                        self._on_tick(symbol, tick)
                    except Exception as e:  # noqa: BLE001
                        log.error("备源 tick 回调失败 symbol=%s: %s", symbol, e)
                if results:
                    log.debug("BackupTickPoller: 喂入 %d 条 tick", len(results))
            except Exception as e:  # noqa: BLE001
                log.error("BackupTickPoller 轮询异常: %s", e, exc_info=True)

            # 等待下一轮（精确间隔）
            elapsed = time.time() - t0
            sleep_sec = max(0.1, self._poll_interval - elapsed)
            time.sleep(sleep_sec)
