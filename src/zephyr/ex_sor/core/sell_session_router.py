# [BLUEPRINT] MOD-XS-016 | docs/03_modules/_domain_ex_sor/sell_session_router/blueprint.md
# [MODULE] zephyr.ex_sor.core.sell_session_router
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] 无（纯函数核，零 IO 零时钟依赖）
# [CONSUMERS] TDM-X-S2-03（时段通道分裂路由）；卖出决策执行链（S2-02 限价策略→S2-03 时段路由→SOR 下单）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 盘外时刻恒 NO_ROUTE(fail-closed); 非法 hhmm/交易所 fail-closed 抛错; ESCAPE=竞价时段走跌停价逃命单其余走急单市价; 深市收盘竞价不可撤(节点真源)沪市默认可撤 config 可调; 同输入必同输出(frozen); 纯路由不下单
# [MODIFY-GUARD] docs/03_modules/_domain_ex_sor/sell_session_router/blueprint.md + 地图节点 TDM-X-S2-03
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非法时刻串/未知交易所/未知紧急度 → SellSessionRouterError（fail-closed）
# [TESTS] tests/ex_sor/test_sell_session_router.py
# [TTL] permanent
"""SellSessionRouter — 卖出单时段通道分裂路由（MOD-XS-016）。

A 股微观结构的卖出时刻决定成交质量：同样一笔卖单，开盘竞价挂跌停价按开盘价
成交排队最优先，14:57 后深市集合竞价不可撤单，14:30-14:45 跳水窗挂单要谨慎。
本模块把"现在是什么时段、该走哪条卖出通道"变成可回测的纯函数：

- classify_session(hhmm, exchange) → SessionWindow（时段窗口判定）
- route_sell(hhmm, exchange, urgency, t0_closing_pending) → SellRouteDecision（通道+可撤性+谨慎旗标）

节点语义逐条吸收（真源=TDM-X-S2-03）：
- 深市 14:57 后集合竞价不可撤单（要卖赶在 14:57 前挂）；沪市尾盘可撤可改。
- 竞价逃命单=9:15 后挂跌停价（按开盘价成交，排队最优先）。
- 14:30-14:45 跳水窗谨慎挂单；14:50 决策窗处理做T收口。

通用规则补充（经典 A 股交易规则）：开盘集合竞价 9:15-9:20 可撤单、9:20-9:25
不可撤单；9:25-9:30 接受申报但不撮合。

查重分工（蓝图 §1）：execution_scheduler=子订单参与率切片调度（时间均匀性）；
本件=A 股时段×紧急度→通道的一次性路由判定，不切单、不管参与率。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

_MORNING_OPEN = 9 * 60 + 15  # 9:15 开盘集合竞价开始
_OPEN_AUCTION_NO_CANCEL = 9 * 60 + 20  # 9:20-9:25 竞价不可撤（A股通用规则）
_OPEN_AUCTION_END = 9 * 60 + 25  # 9:25
_PRE_OPEN_GAP_END = 9 * 60 + 30  # 9:30
_MORNING_END = 11 * 60 + 30  # 11:30
_AFTERNOON_OPEN = 13 * 60  # 13:00
_DIVE_CAUTION_START = 14 * 60 + 30  # 14:30 跳水谨慎窗
_DECISION_WINDOW_START = 14 * 60 + 45  # 14:45 决策窗（14:50 做T收口）
_CLOSE_AUCTION_START = 14 * 60 + 57  # 14:57 收盘集合竞价
_MARKET_CLOSE = 15 * 60  # 15:00


class SellSessionRouterError(ValueError):
    """非法输入（fail-closed）：时刻串/交易所/紧急度不合法。"""


class Exchange(str, Enum):
    """交易所（收盘集合竞价撤单规则按节点口径区分沪深）。"""

    SH = "SH"
    SZ = "SZ"


class RouteUrgency(str, Enum):
    """紧急度：ESCAPE=逃命（跌停价竞价/急单市价），NORMAL=常规。"""

    NORMAL = "NORMAL"
    ESCAPE = "ESCAPE"


class SessionWindow(str, Enum):
    """A 股交易日时段窗口。"""

    CLOSED = "CLOSED"  # 盘外（<9:15 或 ≥15:00）
    OPENING_AUCTION = "OPENING_AUCTION"  # 9:15-9:25 集合竞价
    PRE_OPEN_GAP = "PRE_OPEN_GAP"  # 9:25-9:30 已受理未撮合
    MORNING_SESSION = "MORNING_SESSION"  # 9:30-11:30
    LUNCH_BREAK = "LUNCH_BREAK"  # 11:30-13:00
    AFTERNOON_SESSION = "AFTERNOON_SESSION"  # 13:00-14:30
    DIVE_CAUTION = "DIVE_CAUTION"  # 14:30-14:45 跳水谨慎窗
    DECISION_WINDOW = "DECISION_WINDOW"  # 14:45-14:57 决策窗（做T收口）
    CLOSING_AUCTION = "CLOSING_AUCTION"  # 14:57-15:00 收盘集合竞价


class SellChannel(str, Enum):
    """卖出通道（动作语义给执行层）。"""

    ESCAPE_AUCTION_LIMIT_DOWN = "ESCAPE_AUCTION_LIMIT_DOWN"  # 竞价逃命：挂跌停价按开盘价成交
    LIMIT_INTRADAY = "LIMIT_INTRADAY"  # 盘中限价（含竞价限价参与）
    LIMIT_CAUTIOUS = "LIMIT_CAUTIOUS"  # 跳水窗谨慎限价
    T0_CLOSING = "T0_CLOSING"  # 做T收口
    CLOSING_AUCTION = "CLOSING_AUCTION"  # 尾盘集合竞价
    MARKET_URGENT = "MARKET_URGENT"  # 急单走市价（对手方最优）
    NO_ROUTE = "NO_ROUTE"  # 盘外无通道（fail-closed）


@dataclass(frozen=True)
class SellRouteDecision:
    """时段路由裁决（frozen，可回测重放）。"""

    window: SessionWindow
    channel: SellChannel
    cancelable: bool
    caution: bool  # 谨慎旗标（跳水窗/未撮合时段）
    order_style_hint: str  # 给执行层的挂单风格提示
    note: str


@dataclass(frozen=True)
class SessionRouterConfig:
    """路由配置（收盘竞价撤单规则按节点口径，config 可调）。"""

    sz_close_auction_cancelable: bool = False  # 节点真源：深市 14:57 后集合竞价不可撤单
    sh_close_auction_cancelable: bool = True  # 节点口径：沪市尾盘可撤可改


def get_default_router_config() -> SessionRouterConfig:
    """默认配置惰性工厂（S4-C 模块导入零副作用：不做模块级急切实例化）。"""
    return SessionRouterConfig()


def parse_hhmm(hhmm: str) -> int:
    """把 "HH:MM" 解析为当日分钟数（非法输入 fail-closed 抛错）。"""
    if not isinstance(hhmm, str) or ":" not in hhmm:
        raise SellSessionRouterError(f"时刻必须为 HH:MM 字符串: {hhmm!r}")
    parts = hhmm.split(":")
    if len(parts) != 2:
        raise SellSessionRouterError(f"时刻必须为 HH:MM 格式: {hhmm!r}")
    try:
        hour, minute = int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise SellSessionRouterError(f"时刻分量必须为整数: {hhmm!r}") from exc
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise SellSessionRouterError(f"时刻超出 00:00-23:59: {hhmm!r}")
    return hour * 60 + minute


def classify_session(hhmm: str, exchange: Exchange | str = Exchange.SZ) -> SessionWindow:
    """时段窗口判定（纯函数；交易所参数保留——当前窗口边界沪深一致）。"""
    ex = _to_exchange(exchange)
    minute = parse_hhmm(hhmm)
    del ex  # 当前全部窗口边界沪深一致；保留参数防未来分层漂移
    if minute < _MORNING_OPEN or minute >= _MARKET_CLOSE:
        return SessionWindow.CLOSED
    if minute < _OPEN_AUCTION_END:
        return SessionWindow.OPENING_AUCTION
    if minute < _PRE_OPEN_GAP_END:
        return SessionWindow.PRE_OPEN_GAP
    if minute < _MORNING_END:
        return SessionWindow.MORNING_SESSION
    if minute < _AFTERNOON_OPEN:
        return SessionWindow.LUNCH_BREAK
    if minute < _DIVE_CAUTION_START:
        return SessionWindow.AFTERNOON_SESSION
    if minute < _DECISION_WINDOW_START:
        return SessionWindow.DIVE_CAUTION
    if minute < _CLOSE_AUCTION_START:
        return SessionWindow.DECISION_WINDOW
    return SessionWindow.CLOSING_AUCTION


def _route_closed(urg: RouteUrgency) -> SellRouteDecision:
    """盘外：恒 NO_ROUTE（fail-closed，不给默认通道）。"""
    return SellRouteDecision(
        window=SessionWindow.CLOSED,
        channel=SellChannel.NO_ROUTE,
        cancelable=False,
        caution=False,
        order_style_hint="no_order",
        note="盘外时刻不给通道（fail-closed）",
    )


def _route_open_auction(hhmm: str, urg: RouteUrgency) -> SellRouteDecision:
    """开盘集合竞价：逃命=挂跌停价按开盘价成交；普通=限价参与竞价。9:20-9:25 不可撤（A股通用规则）。"""
    minute = parse_hhmm(hhmm)
    if urg is RouteUrgency.ESCAPE:
        return SellRouteDecision(
            window=SessionWindow.OPENING_AUCTION,
            channel=SellChannel.ESCAPE_AUCTION_LIMIT_DOWN,
            cancelable=minute < _OPEN_AUCTION_NO_CANCEL,
            caution=False,
            order_style_hint="limit_at_lower_limit_price",
            note="竞价逃命：挂跌停价按开盘价成交，排队最优先"
            + ("" if minute < _OPEN_AUCTION_NO_CANCEL else "；9:20-9:25 竞价不可撤单"),
        )
    return SellRouteDecision(
        window=SessionWindow.OPENING_AUCTION,
        channel=SellChannel.LIMIT_INTRADAY,
        cancelable=minute < _OPEN_AUCTION_NO_CANCEL,
        caution=False,
        order_style_hint="limit_join_auction",
        note="限价参与开盘集合竞价",
    )


def _route_accepted(hhmm: str) -> SellRouteDecision:
    """已受理未撮合时段（9:25-9:30 / 午休）：限价挂单+谨慎旗标。"""
    window = classify_session(hhmm)
    note = "已受理未撮合（9:25-9:30）" if window is SessionWindow.PRE_OPEN_GAP else "午休挂单，13:00 后进入撮合"
    return SellRouteDecision(
        window=window,
        channel=SellChannel.LIMIT_INTRADAY,
        cancelable=True,
        caution=True,
        order_style_hint="limit_queued",
        note=note,
    )


def _route_continuous(hhmm: str, ex: Exchange, urg: RouteUrgency, window: SessionWindow) -> SellRouteDecision:
    """连续交易时段（早盘/午盘/跳水窗）：ESCAPE 走急单市价，常规走限价（跳水窗谨慎）。"""
    if urg is RouteUrgency.ESCAPE:
        return SellRouteDecision(
            window=window,
            channel=SellChannel.MARKET_URGENT,
            cancelable=False,
            caution=window is SessionWindow.DIVE_CAUTION,
            order_style_hint="market_opposite_best",
            note="急单走市价（对手方最优）"
            + ("；紧急度优先于谨慎通道" if window is SessionWindow.DIVE_CAUTION else ""),
        )
    if window is SessionWindow.DIVE_CAUTION:
        return SellRouteDecision(
            window=window,
            channel=SellChannel.LIMIT_CAUTIOUS,
            cancelable=True,
            caution=True,
            order_style_hint="limit_tight_small_clip",
            note="跳水窗谨慎挂单：小单+限价收紧",
        )
    return SellRouteDecision(
        window=window,
        channel=SellChannel.LIMIT_INTRADAY,
        cancelable=True,
        caution=False,
        order_style_hint="limit_normal",
        note="盘中常规限价",
    )


def _route_decision_window(hhmm: str, urg: RouteUrgency, t0_closing_pending: bool) -> SellRouteDecision:
    """决策窗（14:45-14:57）：逃命>做T收口>常规限价；深市要卖赶在 14:57 前挂。"""
    if urg is RouteUrgency.ESCAPE:
        return SellRouteDecision(
            window=SessionWindow.DECISION_WINDOW,
            channel=SellChannel.MARKET_URGENT,
            cancelable=False,
            caution=True,
            order_style_hint="market_opposite_best",
            note="决策窗急单走市价；深市 14:57 后只能进收盘竞价",
        )
    if t0_closing_pending:
        return SellRouteDecision(
            window=SessionWindow.DECISION_WINDOW,
            channel=SellChannel.T0_CLOSING,
            cancelable=True,
            caution=False,
            order_style_hint="limit_close_t0_pair",
            note="14:50 决策窗处理做T收口；深市要卖赶在 14:57 前挂",
        )
    return SellRouteDecision(
        window=SessionWindow.DECISION_WINDOW,
        channel=SellChannel.LIMIT_INTRADAY,
        cancelable=True,
        caution=False,
        order_style_hint="limit_before_close_auction",
        note="常规限价；深市要卖赶在 14:57 前挂",
    )


def _route_close_auction(ex: Exchange, urg: RouteUrgency, cfg: SessionRouterConfig) -> SellRouteDecision:
    """收盘集合竞价（14:57-15:00）：撤单规则按节点口径区分沪深。"""
    cancelable = (
        cfg.sh_close_auction_cancelable
        if ex is Exchange.SH
        else cfg.sz_close_auction_cancelable
    )
    return SellRouteDecision(
        window=SessionWindow.CLOSING_AUCTION,
        channel=SellChannel.CLOSING_AUCTION,
        cancelable=cancelable,
        caution=False,
        order_style_hint="limit_join_close_auction",
        note="尾盘集合竞价" + ("；沪市可撤可改" if ex is Exchange.SH else "；深市不可撤单"),
    )


def route_sell(
    hhmm: str,
    exchange: Exchange | str = Exchange.SZ,
    urgency: RouteUrgency | str = RouteUrgency.NORMAL,
    *,
    t0_closing_pending: bool = False,
    config: SessionRouterConfig | None = None,
) -> SellRouteDecision:
    """卖出单时段路由（纯函数，同输入必同输出）。

    Args:
        hhmm: 当前时刻 "HH:MM"（调用方注入，可回测）。
        exchange: 交易所（收盘竞价撤单规则区分沪深）。
        urgency: ESCAPE=逃命单；NORMAL=常规。
        t0_closing_pending: 决策窗内是否有做T收口待处理。
        config: 沪深收盘竞价撤单规则配置。

    Returns:
        SellRouteDecision：盘外恒 NO_ROUTE（fail-closed）。
    """
    ex = _to_exchange(exchange)
    urg = _to_urgency(urgency)
    cfg = config if config is not None else get_default_router_config()
    window = classify_session(hhmm, ex)

    if window is SessionWindow.CLOSED:
        return _route_closed(urg)
    if window is SessionWindow.OPENING_AUCTION:
        return _route_open_auction(hhmm, urg)
    if window in (SessionWindow.PRE_OPEN_GAP, SessionWindow.LUNCH_BREAK):
        return _route_accepted(hhmm)
    if window in (SessionWindow.MORNING_SESSION, SessionWindow.AFTERNOON_SESSION, SessionWindow.DIVE_CAUTION):
        return _route_continuous(hhmm, ex, urg, window)
    if window is SessionWindow.DECISION_WINDOW:
        return _route_decision_window(hhmm, urg, t0_closing_pending)
    return _route_close_auction(ex, urg, cfg)


def _to_exchange(value: Exchange | str) -> Exchange:
    try:
        return Exchange(value)
    except ValueError as exc:
        raise SellSessionRouterError(f"未知交易所: {value!r}") from exc


def _to_urgency(value: RouteUrgency | str) -> RouteUrgency:
    try:
        return RouteUrgency(value)
    except ValueError as exc:
        raise SellSessionRouterError(f"未知紧急度: {value!r}") from exc
