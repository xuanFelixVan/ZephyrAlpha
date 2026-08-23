# [BLUEPRINT] MOD-EX-058 | docs/03_modules/MOD-EX-058/ | §supplement（下单链路探针）
# [MODULE] zephyr.reporting.miniqmt_order_link_probe
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.shared.utils.time_utils
# [CONSUMERS] 系统健康总览看板(55号§3.2, 持仓监控 Tab 旁) ; 运维自治(下单链路健康查询面)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 探针只读通道状态（消费 MiniQmtChannelManager.is_ready/status() 鸭型快照），不触发连接/下单/心跳动作；非交易时段未就绪=closed 正常态不误报；交易时段判定未注入/异常→保守按交易时段口径判定（down，fail-visible 宁误报不漏报）；延迟探针走注入位（latency_probe 可调用），未注入/异常仅 notes 留痕不炸探针；通道状态读取异常→status=error 不抛；frozen dataclass to_dict JSON 可序列化；输出字段对齐 source_health 族口径（source/status/timestamp）
# [MODIFY-GUARD] 55_monitoring_review.md §3.2/§6
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 探针自身不抛（读取/判定/延迟异常全内化为 status/notes）；裸 ValueError 不使用——无 fail-closed 入参（channel_manager 鸭型缺失属性按读取异常处理）
# [TESTS] tests/reporting/test_miniqmt_order_link_probe.py
# [A_module] module_id=MOD-EX-058_probe | layer=module | stability=testing | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""miniQMT 下单链路探针（55 号 §3.2 缺口，MOD-EX-058 伴随件，source_health 族）。

55 号 §3.2："缺口待施工：miniQMT 下单链路专门探针（连接状态/下单延迟/回报延迟）"。
本探针消费 MiniQmtChannelManager（MOD-EX-058）``is_ready``/``status()`` 快照输出
健康状态，纳入 source_health 族结果口径（source/status/timestamp + 明细，
对齐 data/source_health_check.py 查询面）。

状态映射（连接状态维）：
  | 条件 | status | 口径 |
  |---|---|---|
  | ready 且连续心跳/调用失败=0 | healthy | 通道可下单 |
  | ready 但连续心跳/调用失败>0 | degraded | 临近断线预警 |
  | 未就绪且交易时段 | down | 告警态（下单链路中断） |
  | 未就绪且非交易时段 | closed | 正常态不误报（休市通道断开是预期） |
  | 通道状态读取异常 | error | 探针级故障（告警态） |

交易时段判定走注入位（``is_trading_time: () -> bool``，生产接 market_trade_calendar
口径闭包）；未注入/异常 → 保守按交易时段判定（监控哲学：缺接线宁误报不漏报，
notes 留痕）。下单/回报延迟走 ``latency_probe`` 注入位（生产接线
execution_quality_scorer/algo_trading_engine 延迟源，本批零真实下单，测试 mock）。
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Protocol

from zephyr.shared.utils.time_utils import now_utc

_logger = logging.getLogger(__name__)

__all__: Final = [
    "STATUS_CLOSED",
    "STATUS_DEGRADED",
    "STATUS_DOWN",
    "STATUS_ERROR",
    "STATUS_HEALTHY",
    "OrderLinkChannel",
    "OrderLinkHealth",
    "probe_order_link",
]

#: 健康状态封闭集（source_health 族口径对齐）
STATUS_HEALTHY: Final[str] = "healthy"
STATUS_DEGRADED: Final[str] = "degraded"
STATUS_CLOSED: Final[str] = "closed"
STATUS_DOWN: Final[str] = "down"
STATUS_ERROR: Final[str] = "error"

#: 默认源名（source_health 族 source 字段）
_DEFAULT_SOURCE: Final[str] = "miniqmt_order_link"


class OrderLinkChannel(Protocol):
    """下单通道鸭型协议（MiniQmtChannelManager 消费面，只读）。"""

    @property
    def is_ready(self) -> bool:
        """通道可下单唯一判据（CONNECTED）。"""
        ...

    def status(self) -> Any:
        """通道状态快照（state/consecutive_heartbeat_failures/reconnect_attempts/ready）。"""
        ...


@dataclass(frozen=True, slots=True)
class OrderLinkHealth:
    """下单链路健康快照（source_health 族结果口径，JSON 可序列化）。"""

    source: str
    status: str  # healthy/degraded/closed/down/error
    channel_state: str
    ready: bool
    trading_time: bool | None  # None=交易时段判定未注入/异常
    consecutive_heartbeat_failures: int
    reconnect_attempts: int
    latency_ms: dict[str, float] = field(default_factory=dict)
    timestamp: str = ""
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def probe_order_link(
    channel_manager: OrderLinkChannel,
    *,
    is_trading_time: Callable[[], bool] | None = None,
    latency_probe: Callable[[], Mapping[str, float]] | None = None,
    clock: Callable[[], Any] | None = None,
    source: str = _DEFAULT_SOURCE,
) -> OrderLinkHealth:
    """探测一次下单链路健康状态（只读，不触发连接/下单/心跳）。

    Args:
        channel_manager: MiniQmtChannelManager 鸭型（is_ready + status()）。
        is_trading_time: 交易时段判定注入位；None=未注入（未就绪保守判 down）。
        latency_probe: 下单/回报延迟测量注入位（返回 {"order_ms": …, …}）；
            None=未测量（notes 留痕）。
        clock: 时钟注入位（默认 now_utc，测试注入确定性时钟）。
        source: 源名（source_health 族 source 字段）。

    Returns:
        OrderLinkHealth（任何单点故障不抛——内化为 status/notes）。
    """
    notes: list[str] = []
    tick = clock or now_utc
    timestamp = tick().isoformat() if hasattr(tick(), "isoformat") else str(tick())

    # ── 通道状态读取（异常 → error，不抛） ──
    try:
        ready = bool(channel_manager.is_ready)
        status_fn = getattr(channel_manager, "status", None)
        if callable(status_fn):
            snap = status_fn()
            raw_state = getattr(snap, "state", "unknown")
            channel_state = str(getattr(raw_state, "value", raw_state))
            hb_failures = int(getattr(snap, "consecutive_heartbeat_failures", 0))
            reconnect_attempts = int(getattr(snap, "reconnect_attempts", 0))
        else:
            channel_state = "unknown"
            hb_failures = 0
            reconnect_attempts = 0
            notes.append("通道无 status() 快照（仅 is_ready 口径）")
    except Exception as exc:  # noqa: BLE001 — 探针红线：通道读取故障不炸监控面
        _logger.error("ORDER_LINK_PROBE_READ_ERROR error=%s", exc)
        return OrderLinkHealth(
            source=source,
            status=STATUS_ERROR,
            channel_state="unknown",
            ready=False,
            trading_time=None,
            consecutive_heartbeat_failures=0,
            reconnect_attempts=0,
            timestamp=timestamp,
            notes=(f"通道状态读取异常（{type(exc).__name__}）",),
        )

    # ── 交易时段判定（未注入/异常 → None=保守口径） ──
    trading: bool | None
    if is_trading_time is None:
        trading = None
        notes.append("交易时段判定未注入（未就绪按交易时段保守判定）")
    else:
        try:
            trading = bool(is_trading_time())
        except Exception as exc:  # noqa: BLE001 — 判定异常不炸探针，保守口径
            _logger.warning("ORDER_LINK_TRADING_TIME_ERROR error=%s", exc)
            trading = None
            notes.append(f"交易时段判定异常（{type(exc).__name__}，保守判定）")

    # ── 下单/回报延迟（注入位，未注入/异常仅留痕） ──
    latency_ms: dict[str, float] = {}
    if latency_probe is None:
        notes.append("延迟探针未注入（下单/回报延迟未测量）")
    else:
        try:
            latency_ms = {str(k): float(v) for k, v in dict(latency_probe()).items()}
        except Exception as exc:  # noqa: BLE001 — 延迟测量故障不炸探针
            _logger.warning("ORDER_LINK_LATENCY_ERROR error=%s", exc)
            notes.append(f"延迟探针异常（{type(exc).__name__}）")

    # ── 状态映射 ──
    if ready:
        if hb_failures > 0:
            status = STATUS_DEGRADED
            notes.append(f"连续心跳/调用失败 {hb_failures} 次（临近断线预警）")
        else:
            status = STATUS_HEALTHY
    elif trading is False:
        status = STATUS_CLOSED
        notes.append("非交易时段通道未连接（正常态，不误报）")
    else:
        status = STATUS_DOWN  # 交易时段（含保守口径）未就绪=告警态

    return OrderLinkHealth(
        source=source,
        status=status,
        channel_state=channel_state,
        ready=ready,
        trading_time=trading,
        consecutive_heartbeat_failures=hb_failures,
        reconnect_attempts=reconnect_attempts,
        latency_ms=latency_ms,
        timestamp=timestamp,
        notes=tuple(notes),
    )
