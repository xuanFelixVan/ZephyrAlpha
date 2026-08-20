# [BLUEPRINT] MOD-L00-005 | docs/03_modules/_domain_data/redundant_source_blueprint.md
# [A_module] module_id=MOD-L00-005 | layer=module | stability=evolving | safety=M
# [TTL] permanent
"""数据源切换控制器——主源中断时自动切换备源，恢复后切回。

设计：
- SourceProvider 抽象接口：主源和备源都实现此接口
- SourceSwitcher 管理切换状态机：PRIMARY → BACKUP → PRIMARY
- 防抖：主源恢复后等 stable_period 秒稳定期再切回

Usage::

    primary = QMTSourceProvider()
    backup = TDXSourceProvider()
    switcher = SourceSwitcher(primary, backup, heartbeat_monitor)
    switcher.start()
    provider = switcher.get_active_provider()
    ticks = provider.fetch_ticks()
"""

from __future__ import annotations

import abc
import logging
import threading
import time
from dataclasses import dataclass

from zephyr.data.redundant_source.heartbeat_monitor import HeartbeatMonitor
from zephyr.shared.observability.metrics import get_registry

log = logging.getLogger(__name__)

_SWITCH_CHECK_INTERVAL = 5.0  # 切换检查间隔（秒）
_RECOVERY_STABLE_PERIOD = 30.0  # 主源恢复后稳定期（秒）


class SourceProvider(abc.ABC):
    """数据源提供者抽象接口。

    主源（QMT）和备源（通达信/其他）都实现此接口。
    """

    @abc.abstractmethod
    def name(self) -> str:
        """数据源名称。"""

    @abc.abstractmethod
    def start(self) -> bool:
        """启动数据源。Returns True if started successfully."""

    @abc.abstractmethod
    def stop(self) -> None:
        """停止数据源。"""

    @abc.abstractmethod
    def is_running(self) -> bool:
        """数据源是否在运行。"""


@dataclass
class SwitchEvent:
    """切换事件记录。"""

    ts: float
    from_source: str
    to_source: str
    reason: str


class SourceSwitcher:
    """数据源切换控制器。

    状态机：
    - PRIMARY: 主源活跃
    - BACKUP: 备源活跃（主源中断）
    - RECOVERY_WAIT: 主源恢复，等待稳定期
    """

    def __init__(
        self,
        primary: SourceProvider,
        backup: SourceProvider,
        heartbeat: HeartbeatMonitor,
        check_interval: float = _SWITCH_CHECK_INTERVAL,
        recovery_stable_period: float = _RECOVERY_STABLE_PERIOD,
    ) -> None:
        self._primary = primary
        self._backup = backup
        self._heartbeat = heartbeat
        self._check_interval = check_interval
        self._recovery_stable_period = recovery_stable_period

        self._lock = threading.Lock()
        self._active_is_primary = True
        self._primary_recover_ts: float | None = None
        self._switch_history: list[SwitchEvent] = []
        self._running = False
        self._thread: threading.Thread | None = None
        self._registry = get_registry()

    def start(self) -> None:
        """启动切换控制器（启动主源 + 检测线程）。"""
        if self._running:
            return
        ok = self._primary.start()
        if not ok:
            log.error("主源 %s 启动失败，尝试备源", self._primary.name())
            self._backup.start()
            with self._lock:
                self._active_is_primary = False
        self._running = True
        self._thread = threading.Thread(target=self._switch_loop, daemon=True, name="source-switcher")
        self._thread.start()
        log.info("SourceSwitcher 已启动 (primary=%s, backup=%s)", self._primary.name(), self._backup.name())

    def stop(self) -> None:
        """停止切换控制器。"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None
        self._primary.stop()
        self._backup.stop()

    def get_active_provider(self) -> SourceProvider:
        """获取当前活跃的数据源。"""
        with self._lock:
            return self._primary if self._active_is_primary else self._backup

    def is_primary_active(self) -> bool:
        """当前是否使用主源。"""
        with self._lock:
            return self._active_is_primary

    def get_switch_history(self) -> list[SwitchEvent]:
        """获取切换历史。"""
        with self._lock:
            return list(self._switch_history)

    def _switch_loop(self) -> None:
        """切换检测循环。"""
        while self._running:
            try:
                self._check_and_switch()
            except Exception as e:  # noqa: BLE001
                log.error("SourceSwitcher 检测异常: %s", e, exc_info=True)
            time.sleep(self._check_interval)

    def _check_and_switch(self) -> None:
        """检查心跳并执行切换。"""
        primary_alive = self._heartbeat.is_primary_alive()
        with self._lock:
            if self._active_is_primary:
                if not primary_alive:
                    self._do_switch(to_primary=False, reason="主源 tick 中断")
            else:
                # 在备源模式
                if primary_alive:
                    if self._primary_recover_ts is None:
                        self._primary_recover_ts = time.time()
                        log.info("主源恢复，等待 %.0fs 稳定期", self._recovery_stable_period)
                    elif time.time() - self._primary_recover_ts >= self._recovery_stable_period:  # noqa: m46-time — 主备恢复间隔比较与时区无关
                        self._do_switch(to_primary=True, reason="主源恢复且稳定")
                        self._primary_recover_ts = None
                else:
                    self._primary_recover_ts = None

            # 暴露 metrics
            self._registry.set_gauge("zephyr_source_active", 1.0 if self._active_is_primary else 0.0)

    def _do_switch(self, to_primary: bool, reason: str) -> None:
        """执行切换。调用方已持锁。"""
        from_name = self._primary.name() if self._active_is_primary else self._backup.name()
        to_name = self._primary.name() if to_primary else self._backup.name()

        log.warning("数据源切换: %s → %s (原因: %s)", from_name, to_name, reason)

        # 启动目标源
        target = self._primary if to_primary else self._backup
        if not target.is_running():
            ok = target.start()
            if not ok:
                log.error("切换到 %s 失败，保持当前源 %s", to_name, from_name)
                return

        # 停止旧源
        old = self._backup if to_primary else self._primary
        old.stop()

        self._active_is_primary = to_primary
        self._switch_history.append(
            SwitchEvent(ts=time.time(), from_source=from_name, to_source=to_name, reason=reason)  # noqa: m46-time — 切换事件 ts 同进程度量内部自洽
        )
