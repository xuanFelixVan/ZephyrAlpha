# [BLUEPRINT] MOD-L00-007 | docs/03_modules/_domain_data/redundant_source_blueprint.md
# [A_module] module_id=MOD-L00-007 | layer=module | stability=evolving | safety=M
# [TTL] permanent
"""

备源 Tick 轮询器——主源中断时自动切换到 TDX 备源（P1-3）。

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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: TDX 备源 Provider 实例
#   fields: tdx_provider——已连接或待连接的 TDXProvider，提供 fetch_tick_snapshot 拉实时快照
#   code: BackupTickPoller.__init__ L79-94
# - id: I2
#   name: 订阅标的列表 symbols
#   fields: QMT 格式标的列表，如 ["000001.SZ", "600000.SH"]
#   code: BackupTickPoller.__init__ L82,95
# - id: I3
#   name: tick 回调函数
#   fields: on_tick_callback，签名 (symbol: str, tick: dict) → None，喂入 TickSubscriber 队列
#   code: BackupTickPoller.__init__ L83,96
# - id: I4
#   name: QMT 主源订阅器
#   fields: subscriber——TickSubscriber 实例，适配器透传其 _running 状态
#   code: QMTSourceAdapter.__init__ L51-52
# 层: 算法
# - id: A1
#   name_zh: ① TDX 备源轮询
#   name_en: BackupTickPoller
#   intro: 主源中断时起后台线程每 3 秒从 TDX 拉快照，伪装成 QMT tick 喂进队列
#   desc: start 先确保 TDX 已连接（未连则 connect，失败 return False）→起 daemon 线程 _poll_loop：fetch_tick_snapshot(symbols)→逐只 self._on_tick(symbol, tick)，回调异常只 log 不中断→按 max(0.1, interval-elapsed) 精确间隔 sleep（L104-156）；stop 只停线程 join 5s 不断 TDX 连接便于快速重启（L124-130）
#   inputs: I1 I2 I3
#   outputs: 备源 tick 流（经回调入队）
#   invariant: 轮询间隔默认 3.0s；_running 标志 + 线程协调保证线程安全
# - id: A2
#   name_zh: ② QMT 主源被动适配
#   name_en: QMTSourceAdapter
#   intro: 把 TickSubscriber 包成 SourceProvider 接口给切换器用，stop 是空操作保持订阅
#   desc: name()="qmt"；start() no-op 返回 True（QMT 订阅由 TickSubscriber.start 管理）；stop() no-op——保持 QMT 订阅活跃让 HeartbeatMonitor 检测主源恢复；is_running 透传 subscriber._running（L43-66）
#   inputs: I4
#   outputs: SourceProvider 接口视图（主源侧）
#   invariant: stop=no-op，保持订阅用于恢复检测
# 层: 输出
# - id: O1
#   name_zh: 备源 tick 喂入流
#   name_en: on_tick(symbol, tick) 回调流
#   intro: TDX 快照转成 QMT tick dict 喂进 TickSubscriber 队列，主源中断时数据面无缝接管
#   downstream: zephyr.data.tick_subscriber MOD-L00-001（P1-3 接入点 L775-786）
# - id: O2
#   name_zh: SourceProvider 双源适配器
#   name_en: BackupTickPoller + QMTSourceAdapter（SourceProvider 接口）
#   intro: 备源轮询器与主源适配器成对提供给 SourceSwitcher 统一调度主备切换
#   downstream: 同包 source_switcher.SourceSwitcher；zephyr.data.tick_subscriber MOD-L00-001
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A2
# A1 --> O1
# A1 --> O2
# A2 --> O2
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
        self._thread = threading.Thread(target=self._poll_loop, daemon=True, name="tdx-backup-poller")
        self._thread.start()
        log.info("BackupTickPoller 已启动 (symbols=%d, interval=%.1fs)", len(self._symbols), self._poll_interval)
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
