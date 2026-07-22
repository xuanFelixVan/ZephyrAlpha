# [BLUEPRINT] MOD-L00-005 | docs/03_modules/_domain_data/redundant_source_blueprint.md
# [A_module] module_id=MOD-L00-005 | layer=module | stability=evolving | safety=M
# [TTL] permanent
"""心跳检测模块——监测主源 tick 推送 + CH 连通性。

职责：
- 记录最后一次 tick 推送时间，主源中断 > threshold 标记不可用
- 每 N 秒 ping CH `SELECT 1`，连续 3 次失败标记 CH 不可达
- 通过 metrics 暴露心跳状态（Gauge）

Usage::

    monitor = HeartbeatMonitor()
    monitor.record_tick()  # 在 _on_tick 中调用
    monitor.start()        # 启动检测线程
    if not monitor.is_primary_alive():
        ...  # 切换备源
"""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum

from zephyr.shared.observability.metrics import get_registry

log = logging.getLogger(__name__)

_TICK_TIMEOUT = 10.0  # 主源 tick 中断阈值（秒）
_CH_PING_INTERVAL = 10.0  # CH 心跳间隔（秒）
_CH_FAIL_THRESHOLD = 3  # CH 连续失败次数阈值


class SourceState(Enum):
    """数据源状态。"""
    ALIVE = "alive"
    DEAD = "dead"
    UNKNOWN = "unknown"


@dataclass
class HeartbeatStatus:
    """心跳状态快照。"""
    primary_state: SourceState = SourceState.UNKNOWN
    ch_state: SourceState = SourceState.UNKNOWN
    last_tick_ts: float = 0.0
    last_ch_ok_ts: float = 0.0
    ch_consecutive_failures: int = 0


class HeartbeatMonitor:
    """心跳检测器——监测主源 tick 推送 + CH 连通性。

    线程安全：所有状态读写通过 _lock 保护。
    """

    def __init__(
        self,
        tick_timeout: float = _TICK_TIMEOUT,
        ch_ping_interval: float = _CH_PING_INTERVAL,
        ch_fail_threshold: int = _CH_FAIL_THRESHOLD,
        ch_ping_fn=None,
    ) -> None:
        self._tick_timeout = tick_timeout
        self._ch_ping_interval = ch_ping_interval
        self._ch_fail_threshold = ch_fail_threshold
        self._ch_ping_fn = ch_ping_fn or self._default_ch_ping

        self._lock = threading.Lock()
        self._status = HeartbeatStatus()
        self._running = False
        self._thread: threading.Thread | None = None
        self._registry = get_registry()

    def _default_ch_ping(self) -> bool:
        """默认 CH ping（SELECT 1）。"""
        try:
            from zephyr.data.ch_writer import ChWriter  # noqa: F811
            # 使用 ch_writer 的 health_check
            from zephyr.data import ch_writer
            return ch_writer.health_check()
        except Exception as e:  # noqa: BLE001
            log.debug("CH ping 失败: %s", e)
            return False

    def record_tick(self) -> None:
        """记录一次 tick 推送（在 _on_tick 中调用）。"""
        now = time.time()
        with self._lock:
            self._status.last_tick_ts = now
            self._status.primary_state = SourceState.ALIVE

    def is_primary_alive(self) -> bool:
        """主源是否存活（最近 tick_timeout 秒内有 tick）。"""
        with self._lock:
            if self._status.last_tick_ts == 0:
                return False
            alive = (time.time() - self._status.last_tick_ts) < self._tick_timeout
            if not alive:
                self._status.primary_state = SourceState.DEAD
            return alive

    def is_ch_alive(self) -> bool:
        """CH 是否存活。"""
        with self._lock:
            return self._status.ch_state == SourceState.ALIVE

    def get_status(self) -> HeartbeatStatus:
        """获取当前心跳状态快照。"""
        with self._lock:
            return HeartbeatStatus(
                primary_state=self._status.primary_state,
                ch_state=self._status.ch_state,
                last_tick_ts=self._status.last_tick_ts,
                last_ch_ok_ts=self._status.last_ch_ok_ts,
                ch_consecutive_failures=self._status.ch_consecutive_failures,
            )

    def start(self) -> None:
        """启动 CH 心跳检测线程。"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._ch_ping_loop, daemon=True, name="heartbeat-monitor"
        )
        self._thread.start()
        log.info("HeartbeatMonitor 已启动 (tick_timeout=%.0fs, ch_ping=%.0fs)",
                 self._tick_timeout, self._ch_ping_interval)

    def stop(self) -> None:
        """停止检测线程。"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None

    def _ch_ping_loop(self) -> None:
        """CH 心跳检测循环。"""
        while self._running:
            ok = self._ch_ping_fn()
            now = time.time()
            primary_alive = False
            with self._lock:
                if ok:
                    self._status.last_ch_ok_ts = now
                    self._status.ch_consecutive_failures = 0
                    self._status.ch_state = SourceState.ALIVE
                else:
                    self._status.ch_consecutive_failures += 1
                    if self._status.ch_consecutive_failures >= self._ch_fail_threshold:
                        self._status.ch_state = SourceState.DEAD
                        log.warning("CH 连续 %d 次 ping 失败，标记不可达",
                                    self._status.ch_consecutive_failures)

                # 内联计算 primary_alive（避免在持锁时调用 is_primary_alive 导致死锁）
                if self._status.last_tick_ts > 0:
                    primary_alive = (now - self._status.last_tick_ts) < self._tick_timeout
                    if not primary_alive:
                        self._status.primary_state = SourceState.DEAD

                # 暴露 metrics
                self._registry.set_gauge(
                    "zephyr_ch_heartbeat", 1.0 if ok else 0.0
                )
                self._registry.set_gauge(
                    "zephyr_primary_heartbeat", 1.0 if primary_alive else 0.0
                )

            time.sleep(self._ch_ping_interval)
