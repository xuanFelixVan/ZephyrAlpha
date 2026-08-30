# [BLUEPRINT] MOD-L00-005 | docs/03_modules/_domain_data/redundant_source_blueprint.md
# [A_module] module_id=MOD-L00-005 | layer=module | stability=evolving | safety=M
# [TTL] permanent
"""
心跳检测模块——监测主源 tick 推送 + CH 连通性。

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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: tick_timeout 参数
#   fields: 参数 tick_timeout（无注解）
#   code: heartbeat_monitor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: ch_ping_interval 参数
#   fields: 参数 ch_ping_interval（无注解）
#   code: heartbeat_monitor.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: ch_fail_threshold 参数
#   fields: 参数 ch_fail_threshold（无注解）
#   code: heartbeat_monitor.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: ch_ping_fn 参数
#   fields: 参数 ch_ping_fn（无注解）
#   code: heartbeat_monitor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① HeartbeatMonitor
#   name_en: HeartbeatMonitor
#   intro: 心跳检测器——监测主源 tick 推送 + CH 连通性。
#   desc: 心跳检测器——监测主源 tick 推送 + CH 连通性。 线程安全：所有状态读写通过 _lock 保护。；公共方法（定义序）: record_tick, is_primary_alive, is_ch_alive,…
#   inputs: tick_timeout ch_ping_interval ch_fail_threshold ch_ping_fn alerter
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: HeartbeatMonitor
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
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
        alerter=None,
    ) -> None:
        self._tick_timeout = tick_timeout
        self._ch_ping_interval = ch_ping_interval
        self._ch_fail_threshold = ch_fail_threshold
        self._ch_ping_fn = ch_ping_fn or self._default_ch_ping
        # 告警器（惰性创建，避免 import 循环 + 未配置通道时静默）
        self._alerter = alerter

        self._lock = threading.Lock()
        self._status = HeartbeatStatus()
        self._running = False
        self._thread: threading.Thread | None = None
        self._registry = get_registry()

    def _default_ch_ping(self) -> bool:
        """默认 CH ping（SELECT 1，走 ch_reader 只读探活路径）。

        治本（2026-08-17 AI-04 审计）：原实现 `from ch_writer import ChWriter`
        引用不存在类每次 ImportError → 恒返回 False（CH 恒误判 DEAD 触发虚假
        CRITICAL 告警）；且 ch_writer.health_check() 返回 dict 非 bool。
        改为 ch_reader.query("SELECT 1")：成功返回 "1"，失败返回 ""，语义恰为 bool。
        """
        try:
            from zephyr.data import ch_reader

            # 短超时：心跳周期 10s，默认 600s 超时会让黑洞主机卡死探测线程
            return bool(ch_reader.query("SELECT 1", timeout=10).strip())
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
        self._thread = threading.Thread(target=self._ch_ping_loop, daemon=True, name="heartbeat-monitor")
        self._thread.start()
        log.info(
            "HeartbeatMonitor 已启动 (tick_timeout=%.0fs, ch_ping=%.0fs)", self._tick_timeout, self._ch_ping_interval
        )

    def stop(self) -> None:
        """停止检测线程。"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None

    def _ch_ping_loop(self) -> None:
        """CH 心跳检测循环。

        状态变化时触发告警（R4a，#ARCH-DR-CH-RESTART-001）：
        - ALIVE→DEAD：CRITICAL 告警（CH 不可达，灾时数据中断风险）
        - DEAD→ALIVE：INFO 恢复通知（CH 已恢复）
        告警在锁外发送，避免 alerter 内部锁与 _lock 嵌套死锁。
        """
        prev_ch_state = SourceState.UNKNOWN
        while self._running:
            state_changed_to = self._ping_once(prev_ch_state)
            prev_ch_state = self._status.ch_state
            # 锁外发送告警（alerter 内部自带锁，避免与 _lock 嵌套）
            if state_changed_to is not None and self._alerter is not None:
                self._fire_ch_state_alert(state_changed_to)
            time.sleep(self._ch_ping_interval)

    def _ping_once(self, prev_ch_state: SourceState) -> SourceState | None:
        """执行单次 CH 心跳探测 + 状态更新（_ch_ping_loop 的可测单轮）。

        Args:
            prev_ch_state: 上一轮的 CH 状态（用于检测状态变化）。

        Returns:
            状态变化后的新状态（仅跨过阈值时返回，否则 None）；同时更新 self._status。
        """
        ok = self._ch_ping_fn()
        now = time.time()
        primary_alive = False
        state_changed_to: SourceState | None = None
        with self._lock:
            if ok:
                self._status.last_ch_ok_ts = now
                self._status.ch_consecutive_failures = 0
                new_state = SourceState.ALIVE
            else:
                self._status.ch_consecutive_failures += 1
                if self._status.ch_consecutive_failures >= self._ch_fail_threshold:
                    new_state = SourceState.DEAD
                    log.warning("CH 连续 %d 次 ping 失败，标记不可达", self._status.ch_consecutive_failures)
                else:
                    new_state = self._status.ch_state  # 未达阈值，保持原状态

            # 检测状态变化（仅在跨过阈值时触发，避免每轮重复告警）
            if new_state != prev_ch_state and prev_ch_state is not SourceState.UNKNOWN:
                state_changed_to = new_state
            self._status.ch_state = new_state

            # 内联计算 primary_alive（避免在持锁时调用 is_primary_alive 导致死锁）
            if self._status.last_tick_ts > 0:
                primary_alive = (now - self._status.last_tick_ts) < self._tick_timeout
                if not primary_alive:
                    self._status.primary_state = SourceState.DEAD

            # 暴露 metrics
            self._registry.set_gauge("zephyr_ch_heartbeat", 1.0 if ok else 0.0)
            self._registry.set_gauge("zephyr_primary_heartbeat", 1.0 if primary_alive else 0.0)
        return state_changed_to

    def _fire_ch_state_alert(self, new_state: SourceState) -> None:
        """CH 状态变化时发送告警（R4a，#ARCH-DR-CH-RESTART-001）。

        - DEAD：CRITICAL（CH 不可达，灾时数据中断风险）
        - ALIVE：INFO 恢复通知
        告警失败不影响主流程（alerter 内部吞异常）。
        """
        try:
            if new_state == SourceState.DEAD:
                self._alerter.notify(
                    task_id="ch_heartbeat",
                    error=f"CH 连续 {self._ch_fail_threshold} 次 ping 失败，已标记为不可达（DEAD）。"
                    f"灾时若在实盘运行期将导致数据中断，请立即检查 CH 服务状态。",
                    level="CRITICAL",
                    source="clickhouse",
                )
            elif new_state == SourceState.ALIVE:
                self._alerter.notify(
                    task_id="ch_heartbeat",
                    error="CH 已恢复连通（ALIVE），ping 成功。",
                    level="INFO",
                    source="clickhouse",
                )
        except Exception as e:  # noqa: BLE001 — 告警失败不应影响心跳检测主流程
            log.error("CH 状态告警发送异常: %s", e)
