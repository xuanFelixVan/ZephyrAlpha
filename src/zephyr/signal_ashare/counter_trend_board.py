# [BLUEPRINT] MOD-SIG-080 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-16 行）
# [MODULE] zephyr.signal_ashare.counter_trend_board
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.index_contribution_decomposer(resample_quotes_to_minute 复用，MOD-SIG-071); c1_market.index_quote（只读，3秒快照重采样分钟）; c1_market.kline_sector_intraday（只读，板块分钟）
# [CONSUMERS] （候选：板块页逆势榜 4 卡——逆势上涨/下跌段资金流入/率先反弹/最抗跌）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 主下跌段=指数日内峰→谷（峰须在谷前，段长 ≥down_segment_min_minutes 否则全卡降级不出伪榜）；四卡口径封闭；资金腿未供给仅该卡降级（其余三卡不受影响）；板块缺分钟计覆盖分钟数留痕；PIT（全部数据 ≤ trade_date）；输入校验 fail-closed；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-16 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] trade_date 非法→ValueError（fail-closed）；查询异常/客户端不可得→对应腿降级 notes 留痕不抛
# [TESTS] tests/signal_ashare/test_counter_trend_board.py
# [A_module] module_id=MOD-SIG-080 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-SIG-080 — 逆势榜 4 卡（GAP-F-16，板块页逆势榜后端）。

分钟级逆势识别（MVP），消费链：MOD-SIG-071 重采样口径复用（index_quote 3 秒
快照分钟末价 + kline_sector_intraday 板块分钟）。

四卡口径（写清）：
- **主下跌段**：指数日内最高价峰 → 其后最低价谷（峰须在谷前；段长≥
  down_segment_min_minutes，否则"无有效下跌段"全卡降级）。段内分钟=(峰,谷]。
- **卡1 逆势上涨**：段内板块分钟累计收益 >0 者，按累计收益降序。
- **卡2 下跌段资金流入**：fund_flow 注入位（板块→段内主力净流入）；未供给
  → 仅本卡降级（"资金流数据未供给"），正流入降序。
- **卡3 率先反弹**：谷后 rebound_window_minutes 内，板块自谷收盘累计涨幅
  首过 rebound_threshold_pct 的分钟数，升序（未过阈值不入选；谷=末日无
  观察窗→本卡降级）。MVP 口径：从低点收复速度即"率先"，不要求板块段内曾跌
  （段内抗跌未跌者谷后惯性上翘亦会入选，口径留痕）。
- **卡4 最抗跌**：段内板块最大回撤（相对峰价最低价/峰价−1）降序
  （越接近 0 越抗跌；正=段内未破峰价）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1 指数分钟序列 [(ts, price)]
# - id: I2 板块分钟序列 {code → [(ts, close)]}
# - id: I3 板块资金流 {code → 净流入}（注入位，可 None）
# 层: 算法
# - id: A1 主下跌段识别（峰→谷）
# - id: A2 四卡逐板块口径计算
# 层: 输出
# - id: O1 CounterTrendBoard（4 张 CounterTrendCard）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1,I2 --> A2
# I3 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Final, Mapping

from zephyr.signal_ashare.index_contribution_decomposer import resample_quotes_to_minute

logger = logging.getLogger(__name__)

__all__: Final = [
    "CounterTrendBoard",
    "CounterTrendCard",
    "CounterTrendCardItem",
    "CounterTrendConfig",
    "build_counter_trend_board",
    "run_counter_trend_board",
]

# ------------------------------------------------------------------
# 常量（SQL 集中化 §5.160.2；与 MOD-SIG-071 同口径）
# ------------------------------------------------------------------

SQL_INDEX_QUOTES: Final = """
SELECT timestamp, price
FROM c1_market.index_quote
WHERE trade_date = %(trade_date)s AND symbol = %(symbol)s AND quality_flag = 1
ORDER BY timestamp
"""

SQL_SECTOR_MINUTE: Final = """
SELECT trade_date, code, close
FROM c1_market.kline_sector_intraday
WHERE toDate(trade_date) = %(trade_date)s AND period = %(period)s
ORDER BY code, trade_date
"""

_CARD_TITLES: Final[dict[str, str]] = {
    "counter_rally": "逆势上涨",
    "fund_inflow": "下跌段资金流入",
    "first_rebound": "率先反弹",
    "most_resilient": "最抗跌",
}


# ------------------------------------------------------------------
# 配置 / 输出
# ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CounterTrendConfig:
    """逆势榜配置（MVP 初拍值）。"""

    index_symbol: str = "000001.SH"
    sector_period: str = "1m"
    down_segment_min_minutes: int = 3  # 主下跌段最小分钟数
    rebound_threshold_pct: float = 0.3  # 反弹确认阈值（自谷累计涨幅 %）
    rebound_window_minutes: int = 30  # 谷后反弹观察窗（分钟）
    top_n: int = 10
    sector_names: Mapping[str, str] | None = None


@dataclass(frozen=True, slots=True)
class CounterTrendCardItem:
    """逆势榜单条目。"""

    sector_code: str
    sector_name: str
    metric_value: float  # 口径随卡：累计收益%/净流入/分钟数/回撤%
    metric_label: str
    covered_minutes: int = 0


@dataclass(frozen=True, slots=True)
class CounterTrendCard:
    """单张逆势卡。"""

    card: str  # counter_rally/fund_inflow/first_rebound/most_resilient
    title: str
    items: list[CounterTrendCardItem] = field(default_factory=list)
    degraded: bool = False
    note: str = ""


@dataclass(frozen=True, slots=True)
class CounterTrendBoard:
    """逆势榜输出（观测层消费，不接交易）。"""

    date: str
    index_symbol: str
    down_start_ts: str = ""
    down_end_ts: str = ""
    index_down_pct: float = 0.0
    cards: list[CounterTrendCard] = field(default_factory=list)
    degraded: bool = False
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 纯函数核
# ------------------------------------------------------------------


def _minute_returns(series: list[tuple[str, float]]) -> dict[str, float]:
    out: dict[str, float] = {}
    for i in range(1, len(series)):
        prev = series[i - 1][1]
        if prev:
            out[series[i][0]] = (series[i][1] / prev - 1.0) * 100.0
    return out


def _degraded_board(date_str: str, symbol: str, note: str) -> CounterTrendBoard:
    cards = [
        CounterTrendCard(card=k, title=v, degraded=True, note=note)
        for k, v in _CARD_TITLES.items()
    ]
    return CounterTrendBoard(date=date_str, index_symbol=symbol, cards=cards, degraded=True, notes=[note])


def build_counter_trend_board(
    index_series: list[tuple[str, float]],
    sector_series: Mapping[str, list[tuple[str, float]]],
    fund_flow: Mapping[str, float] | None,
    config: CounterTrendConfig | None = None,
) -> CounterTrendBoard:
    """逆势榜主核（纯函数，不触库）。

    Args:
        index_series: 指数分钟序列 [(ts, price)] 升序（ts='YYYY-MM-DD HH:MM'）。
        sector_series: 板块分钟序列 {code: [(ts, close)]} 升序。
        fund_flow: 板块下跌段净流入注入位 {code: 金额}；None → 卡2 降级。
        config: 配置（None 用默认）。

    Returns:
        CounterTrendBoard；无有效下跌段/指数序列不足 → 全卡降级。
    """
    cfg = config or CounterTrendConfig()
    date_str = index_series[0][0][:10] if index_series else ""
    names = cfg.sector_names or {}
    if len(index_series) < cfg.down_segment_min_minutes + 1:
        return _degraded_board(date_str, cfg.index_symbol, "指数分钟序列不足，不出伪榜")

    # ---- 主下跌段：峰（谷前最高）→ 谷（峰后最低）----
    prices = [p for _, p in index_series]
    trough_idx = min(range(len(prices)), key=lambda i: (prices[i], i))
    if trough_idx == 0:
        return _degraded_board(date_str, cfg.index_symbol, "全天无有效下跌段（谷在起点）")
    peak_idx = max(range(trough_idx + 1), key=lambda i: (prices[i], -i))
    if prices[peak_idx] <= prices[trough_idx] or trough_idx - peak_idx < cfg.down_segment_min_minutes:
        return _degraded_board(date_str, cfg.index_symbol, "全天无有效下跌段（峰谷不成立或段长不足）")
    seg_ts = [index_series[i][0] for i in range(peak_idx + 1, trough_idx + 1)]  # (峰,谷]
    down_pct = (prices[trough_idx] / prices[peak_idx] - 1.0) * 100.0
    notes: list[str] = []

    index_ret = _minute_returns(index_series)
    sector_ret = {s: _minute_returns(series) for s, series in sector_series.items()}
    seg_set = set(seg_ts)

    # ---- 卡1 逆势上涨：段内累计收益 >0 降序 ----
    rally_items: list[CounterTrendCardItem] = []
    for s in sorted(sector_series):
        rets = [r for ts, r in sector_ret[s].items() if ts in seg_set]
        cum = sum(rets)
        if cum > 0:
            rally_items.append(
                CounterTrendCardItem(
                    sector_code=s, sector_name=names.get(s, ""),
                    metric_value=round(cum, 4), metric_label="段内累计收益%",
                    covered_minutes=len(rets),
                )
            )
    rally_items.sort(key=lambda i: (-i.metric_value, i.sector_code))
    card1 = CounterTrendCard(
        card="counter_rally", title=_CARD_TITLES["counter_rally"],
        items=rally_items[: cfg.top_n],
        degraded=not rally_items,
        note="" if rally_items else "段内无正收益板块",
    )

    # ---- 卡2 下跌段资金流入（注入位）----
    if fund_flow is None:
        card2 = CounterTrendCard(
            card="fund_inflow", title=_CARD_TITLES["fund_inflow"],
            degraded=True, note="资金流数据未供给（注入位 None），本卡降级",
        )
        notes.append("资金腿未供给，下跌段资金流入卡降级")
    else:
        flow_items = [
            CounterTrendCardItem(
                sector_code=s, sector_name=names.get(s, ""),
                metric_value=round(float(v), 2), metric_label="段内净流入",
            )
            for s, v in fund_flow.items()
            if float(v) > 0
        ]
        flow_items.sort(key=lambda i: (-i.metric_value, i.sector_code))
        card2 = CounterTrendCard(
            card="fund_inflow", title=_CARD_TITLES["fund_inflow"],
            items=flow_items[: cfg.top_n],
            degraded=not flow_items,
            note="" if flow_items else "段内无正净流入板块",
        )

    # ---- 卡3 率先反弹：谷后首过阈值分钟数升序 ----
    rebound_items: list[CounterTrendCardItem] = []
    if trough_idx >= len(index_series) - 1:
        card3 = CounterTrendCard(
            card="first_rebound", title=_CARD_TITLES["first_rebound"],
            degraded=True, note="谷底为最新分钟，无反弹观察窗，本卡降级",
        )
    else:
        win_end = min(trough_idx + cfg.rebound_window_minutes, len(index_series) - 1)
        win_ts = [index_series[i][0] for i in range(trough_idx + 1, win_end + 1)]
        for s in sorted(sector_series):
            series = sector_series[s]
            if trough_idx >= len(series):
                continue
            base = series[trough_idx][1]
            if base <= 0:
                continue
            ts_to_close = dict(series)
            elapsed: int | None = None
            for k, ts in enumerate(win_ts, start=1):
                close = ts_to_close.get(ts)
                if close is None:
                    continue
                if (close / base - 1.0) * 100.0 >= cfg.rebound_threshold_pct:
                    elapsed = k
                    break
            if elapsed is not None:
                rebound_items.append(
                    CounterTrendCardItem(
                        sector_code=s, sector_name=names.get(s, ""),
                        metric_value=float(elapsed), metric_label="谷后过阈分钟数",
                    )
                )
        rebound_items.sort(key=lambda i: (i.metric_value, i.sector_code))
        card3 = CounterTrendCard(
            card="first_rebound", title=_CARD_TITLES["first_rebound"],
            items=rebound_items[: cfg.top_n],
            degraded=not rebound_items,
            note="" if rebound_items else "观察窗内无板块反弹过阈",
        )

    # ---- 卡4 最抗跌：段内最大回撤降序（越近 0 越抗跌）----
    resilient_items: list[CounterTrendCardItem] = []
    peak_price = prices[peak_idx]
    for s in sorted(sector_series):
        ts_to_close = dict(sector_series[s])
        base = ts_to_close.get(index_series[peak_idx][0])
        if base is None or base <= 0:
            continue  # 峰时点无板块价 → 不入榜（覆盖留痕）
        seg_closes = [ts_to_close[ts] for ts in seg_ts if ts in ts_to_close]
        if not seg_closes:
            continue
        dd = (min(seg_closes) / base - 1.0) * 100.0
        resilient_items.append(
            CounterTrendCardItem(
                sector_code=s, sector_name=names.get(s, ""),
                metric_value=round(dd, 4), metric_label="段内最大回撤%",
                covered_minutes=len(seg_closes),
            )
        )
    resilient_items.sort(key=lambda i: (-i.metric_value, i.sector_code))
    card4 = CounterTrendCard(
        card="most_resilient", title=_CARD_TITLES["most_resilient"],
        items=resilient_items[: cfg.top_n],
        degraded=not resilient_items,
        note="" if resilient_items else "段内无覆盖板块",
    )
    _ = index_ret  # 指数分钟收益口径留痕（段识别已含峰谷价差）
    _ = peak_price

    return CounterTrendBoard(
        date=date_str,
        index_symbol=cfg.index_symbol,
        down_start_ts=index_series[peak_idx][0],
        down_end_ts=index_series[trough_idx][0],
        index_down_pct=round(down_pct, 4),
        cards=[card1, card2, card3, card4],
        degraded=False,
        notes=notes,
    )


# ------------------------------------------------------------------
# 主入口（薄加载层，ch_client 注入可 mock；序列注入位测试直注）
# ------------------------------------------------------------------


def _normalize_dt(trade_date: str | date | datetime) -> date:
    if isinstance(trade_date, datetime):
        return trade_date.date()
    if isinstance(trade_date, date):
        return trade_date
    try:
        return datetime.strptime(str(trade_date), "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"trade_date 非真实日期（须 YYYY-MM-DD）: {trade_date!r}") from exc


def _default_client() -> Any | None:
    try:
        from zephyr.data.ch_writer import get_client

        return get_client()
    except Exception:  # noqa: BLE001 — 连接/依赖问题一律降级
        logger.warning("ch_writer 默认客户端不可用，逆势榜降级", exc_info=True)
        return None


def run_counter_trend_board(
    trade_date: str | date | datetime,
    ch_client: Any | None = None,
    config: CounterTrendConfig | None = None,
    index_series: list[tuple[str, float]] | None = None,
    sector_series: Mapping[str, list[tuple[str, float]]] | None = None,
    fund_flow: Mapping[str, float] | None = None,
) -> CounterTrendBoard:
    """主入口：逆势榜 4 卡（分钟级）。

    Args:
        trade_date: 数据日（PIT 上限）。
        ch_client: clickhouse-driver 鸭子类型；None 延迟取默认客户端。
        config: 配置（None 用默认）。
        index_series/sector_series: 测试/编排注入位；None 时经 client 现查
            （指数腿=index_quote 重采样，复用 MOD-SIG-071 口径；板块腿=
            kline_sector_intraday）。
        fund_flow: 板块下跌段净流入注入位；None → 卡2 降级。

    Returns:
        CounterTrendBoard；单腿异常独立降级（notes 留痕）。
    """
    cfg = config or CounterTrendConfig()
    current = _normalize_dt(trade_date)  # ValueError fail-closed
    date_str = current.isoformat()
    notes: list[str] = []

    need_client = index_series is None or sector_series is None
    client = ch_client if ch_client is not None else (_default_client() if need_client else None)
    if need_client and client is None:
        return _degraded_board(date_str, cfg.index_symbol, "CH 客户端不可得，逆势榜整体降级")

    if index_series is None:
        try:
            rows = client.execute(SQL_INDEX_QUOTES, {"trade_date": current, "symbol": cfg.index_symbol})
            index_series = resample_quotes_to_minute([(r[0], float(r[1])) for r in rows])
        except Exception as e:  # noqa: BLE001 — 指数腿降级
            index_series = []
            notes.append(f"index_quote 查询异常，指数腿降级: {e!r}")
    if sector_series is None:
        try:
            rows = client.execute(SQL_SECTOR_MINUTE, {"trade_date": current, "period": cfg.sector_period})
            by_sector: dict[str, list[tuple[str, float]]] = {}
            for r in rows:
                by_sector.setdefault(str(r[1]), []).append((str(r[0])[:16], float(r[2])))
            sector_series = by_sector
        except Exception as e:  # noqa: BLE001 — 板块腿降级
            sector_series = {}
            notes.append(f"kline_sector_intraday 查询异常，板块腿降级: {e!r}")

    board = build_counter_trend_board(index_series, sector_series, fund_flow, cfg)
    if not notes:
        return board
    return CounterTrendBoard(
        date=board.date, index_symbol=board.index_symbol,
        down_start_ts=board.down_start_ts, down_end_ts=board.down_end_ts,
        index_down_pct=board.index_down_pct, cards=board.cards,
        degraded=board.degraded, notes=notes + board.notes,
    )
