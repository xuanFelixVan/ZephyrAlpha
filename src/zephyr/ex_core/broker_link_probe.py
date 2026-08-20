# [BLUEPRINT] MOD-L06-002 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.broker_link_probe
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib
# [CONSUMERS] 55_monitoring_review §3.2 系统健康总览看板; 调用方(健康巡检事件驱动)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 探针函数级+注入式(ping/submit/时钟全注入, 不接真实 miniQMT 连接); 只读观测不改下单链路状态; 样本有界(deque 防内存膨胀); 阈值显式注入(无隐藏常量)
# [MODIFY-GUARD] 55_monitoring_review.md §3.2; 40_execution_broker.md §6.1
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidProbeInputError(ZA-EX-0013)
# [TESTS] tests/ex_core/test_broker_link_probe.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: ping_fn(连接探活可调用, 返回 rtt 秒或抛异常) + submit_fn(下单可调用) + clock(时钟注入, 默认 time.monotonic)
# I2: warn_ms/crit_ms 延迟阈值(注入) + max_samples(样本界)
# F1: probe_connection(ping_fn)——连接状态+RTT 测量(异常=DOWN 不抛)
# F2: time_order_submission(submit_fn, *args)——下单延迟测量, 透传返回值/异常, 延迟落样本
# F3: record_fill_report_latency(submit_ts, fill_ts)——成交回报延迟登记(回报-下单时间差)
# A1: snapshot()——健康汇总: 连接状态/下单延迟(avg/max)/回报延迟(avg/max)/样本量 -> LinkHealth(HEALTHY/DEGRADED/DOWN)
# O1: ConnectionProbeResult + LinkHealthSnapshot(55 号 §3.2 健康总览消费)
# [/ALGO_FLOW]
"""D_EX_CORE — miniQMT 下单链路探针（55 号 §3.2 缺口，随 40 号 P0 清单施工）。

55 号 §3.2："miniQMT 下单链路专门探针（连接状态/下单延迟/回报延迟）——
40_execution_broker P0 缺口清单已含断线重连，探针随其一并施工"。

函数级探针、注入式：ping_fn / submit_fn / clock 全部注入，本模块不接真实
miniQMT 连接（真实接线由健康巡检批次把 MiniQmtBroker 回调适配进来）。
只读观测——不改下单链路任何状态；样本有界（deque）防内存膨胀。
"""

from __future__ import annotations

import logging
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

_DEFAULT_MAX_SAMPLES: Final[int] = 512


class InvalidProbeInputError(ZephyrBaseError):
    """探针输入非法——阈值非正/时间戳倒挂等。"""

    error_code = "ZA-EX-0013"


class LinkHealth(str, Enum):
    """链路健康三档。"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


@dataclass(frozen=True)
class ConnectionProbeResult:
    """单次连接探活结果。"""

    connected: bool
    rtt_ms: float | None  # 未连接为 None
    detail: str


@dataclass(frozen=True)
class LinkHealthSnapshot:
    """链路健康汇总（55 号 §3.2 健康总览消费）。"""

    health: LinkHealth
    consecutive_connect_failures: int
    order_latency_avg_ms: float | None
    order_latency_max_ms: float | None
    fill_report_latency_avg_ms: float | None
    fill_report_latency_max_ms: float | None
    order_samples: int
    fill_report_samples: int


class BrokerLinkProbe:
    """miniQMT 下单链路探针（连接状态/下单延迟/回报延迟）。

    Args:
        warn_latency_ms: 延迟预警线（超过→DEGRADED）。
        crit_latency_ms: 延迟严重线（超过→DEGRADED 重侧；连续连接失败→DOWN）。
        max_consecutive_failures: 连续连接失败多少次判 DOWN（默认 3，对齐
            HealthMonitor 压力四级"自动重启≤3 次"口径，55 号 §3.1A）。
        clock: 时钟注入（默认 time.monotonic，测试可注入假钟）。
        max_samples: 延迟样本界（deque，超出丢最旧）。
    """

    def __init__(
        self,
        *,
        warn_latency_ms: float = 500.0,
        crit_latency_ms: float = 2000.0,
        max_consecutive_failures: int = 3,
        clock: Callable[[], float] = time.monotonic,
        max_samples: int = _DEFAULT_MAX_SAMPLES,
    ) -> None:
        if warn_latency_ms <= 0 or crit_latency_ms <= 0 or warn_latency_ms > crit_latency_ms:
            raise InvalidProbeInputError(
                "延迟阈值必须为正且 warn ≤ crit",
                details={"warn_ms": warn_latency_ms, "crit_ms": crit_latency_ms},
            )
        if max_consecutive_failures <= 0 or max_samples <= 0:
            raise InvalidProbeInputError(
                "max_consecutive_failures/max_samples 必须为正",
                details={"max_consecutive_failures": max_consecutive_failures, "max_samples": max_samples},
            )
        self._warn_ms = warn_latency_ms
        self._crit_ms = crit_latency_ms
        self._max_failures = max_consecutive_failures
        self._clock = clock
        self._consecutive_failures = 0
        self._order_latencies_ms: deque[float] = deque(maxlen=max_samples)
        self._fill_report_latencies_ms: deque[float] = deque(maxlen=max_samples)

    # ── ① 连接状态探活 ──

    def probe_connection(self, ping_fn: Callable[[], Any]) -> ConnectionProbeResult:
        """探活一次。ping_fn 返回 RTT 秒（float/int）或真值；抛异常=未连接。

        探活本身不抛——DOWN 也是合法探测结果（监控不阻断主链路）。
        """
        start = self._clock()
        try:
            outcome = ping_fn()
        except Exception as exc:  # noqa: BLE001 —— 探活失败=DOWN 证据，不抛
            self._consecutive_failures += 1
            _logger.warning("链路探活失败(第 %d 次): %s", self._consecutive_failures, type(exc).__name__)
            return ConnectionProbeResult(connected=False, rtt_ms=None, detail=type(exc).__name__)
        elapsed_ms = (self._clock() - start) * 1000.0
        if outcome is False:
            self._consecutive_failures += 1
            return ConnectionProbeResult(connected=False, rtt_ms=None, detail="ping_fn 返回 False")
        self._consecutive_failures = 0
        rtt_ms = float(outcome) * 1000.0 if isinstance(outcome, (int, float)) and outcome is not True else elapsed_ms
        return ConnectionProbeResult(connected=True, rtt_ms=rtt_ms, detail="ok")

    # ── ② 下单延迟测量 ──

    def time_order_submission(self, submit_fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """包裹一次下单调用：测量延迟落样本，透传返回值/异常（不改链路语义）。"""
        start = self._clock()
        try:
            return submit_fn(*args, **kwargs)
        finally:
            self._order_latencies_ms.append((self._clock() - start) * 1000.0)

    # ── ③ 成交回报延迟登记 ──

    def record_fill_report_latency(self, submit_ts: float, fill_report_ts: float) -> float:
        """登记一笔成交回报延迟（秒级时间戳差 → 毫秒样本）。返回本次延迟 ms。"""
        if fill_report_ts < submit_ts:
            raise InvalidProbeInputError(
                "回报时间早于下单时间（时钟倒挂）",
                details={"submit_ts": submit_ts, "fill_report_ts": fill_report_ts},
            )
        latency_ms = (fill_report_ts - submit_ts) * 1000.0
        self._fill_report_latencies_ms.append(latency_ms)
        return latency_ms

    # ── 健康汇总 ──

    def snapshot(self) -> LinkHealthSnapshot:
        """当前链路健康汇总。"""
        health = self._derive_health()
        return LinkHealthSnapshot(
            health=health,
            consecutive_connect_failures=self._consecutive_failures,
            order_latency_avg_ms=_avg(self._order_latencies_ms),
            order_latency_max_ms=_max(self._order_latencies_ms),
            fill_report_latency_avg_ms=_avg(self._fill_report_latencies_ms),
            fill_report_latency_max_ms=_max(self._fill_report_latencies_ms),
            order_samples=len(self._order_latencies_ms),
            fill_report_samples=len(self._fill_report_latencies_ms),
        )

    def _derive_health(self) -> LinkHealth:
        if self._consecutive_failures >= self._max_failures:
            return LinkHealth.DOWN
        worst = max(
            _max(self._order_latencies_ms) or 0.0,
            _max(self._fill_report_latencies_ms) or 0.0,
        )
        if worst >= self._crit_ms or self._consecutive_failures > 0:
            return LinkHealth.DEGRADED
        if worst >= self._warn_ms:
            return LinkHealth.DEGRADED
        return LinkHealth.HEALTHY


def _avg(samples: deque[float]) -> float | None:
    return (sum(samples) / len(samples)) if samples else None


def _max(samples: deque[float]) -> float | None:
    return max(samples) if samples else None


__all__ = [
    "BrokerLinkProbe",
    "ConnectionProbeResult",
    "InvalidProbeInputError",
    "LinkHealth",
    "LinkHealthSnapshot",
]
