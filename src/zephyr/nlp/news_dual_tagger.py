# [BLUEPRINT] MOD-NLP-DUALTAG-001 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-21 行 + GAP-F-D1 核查）
# [MODULE] zephyr.nlp.news_dual_tagger
# [DOMAIN] D_DATA
# [DEPENDENCIES] c3_fundamental.news_data（只读）; c3_fundamental.analyst_forecast（只读，GAP-F-D1 已核：53,918行/2,519标的/2026-07-22~08-21）; event_calendar_registry（事件类型关键词，注入位）
# [CONSUMERS] （候选：新闻页双标签列、45号 W1 事件条联动）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 双标签封闭集合：可预测性∈{可预测-日历,可预测-资金痕迹,可预测-日历+资金,突发-不可预测}；预期差∈{超预期,符合预期,低于预期,无锚未定}；锚缺失→无锚未定+anchor_missing 留痕（不出伪预期差）；actual 值为注入位（新闻→实际值的 NLP 抽取为后续件）；PIT（锚 report_date ≤ 数据日）；单腿异常独立降级；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-21 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 锚加载异常→锚腿降级 notes 留痕不抛；trade_date 格式非法→ValueError（fail-closed）
# [TESTS] tests/nlp/test_news_dual_tagger.py
# [A_module] module_id=MOD-NLP-DUALTAG-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-NLP-DUALTAG-001 — 新闻双标签生成器（GAP-F-21，新闻页"可预测性+预期差"双标签列）。

**标签① 可预测性**（这事能不能提前知道）：
- 日历匹配：新闻文本命中事件日历规则关键词（业绩预告/解禁/分红/宏观发布等有
  提前披露纪律的事件类型）→ 可预测-日历。规则=EventKeywordRule 注入位，
  默认规则组对齐 event_calendar_registry（REG-EVT-001）事件类型别名。
- 资金痕迹：新闻提及标的事前资金净流入超阈值（capital_traces 注入位，
  如 T-3~T-1 主力净流入）→ 可预测-资金痕迹。
- 双命中 → 可预测-日历+资金；皆无 → 突发-不可预测。

**标签② 预期差**（实际 vs 一致预期锚）：
- 锚=分析师一致预期（c3_fundamental.analyst_forecast：forecast_eps/forecast_pe/
  rating/analyst_count，GAP-F-D1 核查实证有数据）；
- 实际值=注入位（news.actual_value；新闻→实际值抽取 NLP 件为后续工作）；
- gap_pct=(actual-anchor)/|anchor|×100；|gap|≤容差→符合预期，>容差→超预期，<-容差→低于预期；
- 锚/实际值缺 → 无锚未定（anchor_missing 留痕，宁缺毋假）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1 新闻 list[NewsTagInput]（news_id/title/content/symbols/actual_value）
# - id: I2 日历规则组 list[EventKeywordRule]（事件类型+关键词+提前披露标记）
# - id: I3 资金痕迹 dict[symbol → 净流入]（注入位）
# - id: I4 一致预期锚 dict[symbol → ConsensusAnchor]（analyst_forecast 或注入位）
# 层: 特征
# - id: F1 日历关键词命中
# - id: F2 资金痕迹阈值判定
# - id: F3 预期差 gap_pct
# 层: 算法
# - id: A1 双标签封闭集合判定（可预测性四态 × 预期差四态）
# 层: 输出
# - id: O1 NewsDualTagResult（items 逐条双标签 + counts 计数 + 降级留痕）
# [/ALGO_FLOW]
#
# 边:
# I1,I2 --> F1
# I1,I3 --> F2
# I1,I4 --> F3
# F1,F2,F3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Callable, Final, Mapping

logger = logging.getLogger(__name__)

__all__: Final = [
    "ConsensusAnchor",
    "DualTagConfig",
    "EventKeywordRule",
    "NewsDualTagResult",
    "NewsTagInput",
    "NewsTagItem",
    "classify_expectation_gap",
    "classify_predictability",
    "load_consensus_anchors",
    "match_calendar_rules",
    "tag_news_dual",
]

# ------------------------------------------------------------------
# 常量（标签封闭集合 + SQL 集中化 + 默认日历规则）
# ------------------------------------------------------------------

#: 可预测性标签（封闭四态）
PRED_CALENDAR: Final[str] = "可预测-日历"
PRED_CAPITAL: Final[str] = "可预测-资金痕迹"
PRED_BOTH: Final[str] = "可预测-日历+资金"
PRED_SURPRISE: Final[str] = "突发-不可预测"

#: 预期差标签（封闭四态）
GAP_BEAT: Final[str] = "超预期"
GAP_MEET: Final[str] = "符合预期"
GAP_MISS: Final[str] = "低于预期"
GAP_NO_ANCHOR: Final[str] = "无锚未定"

#: 一致预期锚查询（analyst_forecast；PIT：report_date ≤ 数据日，取最新一条）
SQL_CONSENSUS_ANCHOR: Final = """
SELECT symbol, forecast_year, forecast_eps, forecast_pe, rating, analyst_count, report_date
FROM c3_fundamental.analyst_forecast
WHERE symbol IN %(symbols)s AND report_date <= %(trade_date)s
ORDER BY symbol, report_date DESC
"""


@dataclass(frozen=True, slots=True)
class EventKeywordRule:
    """事件日历规则（对齐 event_calendar_registry 事件类型，注入位）。"""

    event_type_id: str  # 如 EVT-EARN-002
    name_zh: str  # 事件类型中文名
    keywords: tuple[str, ...]  # 命中关键词组
    advance_notice: bool = True  # 有提前披露纪律（False 的规则不参与可预测-日历）


#: 默认日历规则组（对齐 REG-EVT-001 事件类型别名；MVP 经验口径，可注入覆盖）
_DEFAULT_CALENDAR_RULES: Final[tuple[EventKeywordRule, ...]] = (
    EventKeywordRule("EVT-EARN-001", "财报披露计划", ("预约披露", "披露日期", "年报预约", "季报预约")),
    EventKeywordRule("EVT-EARN-002", "业绩预告", ("业绩预告", "预增", "预减", "扭亏", "首亏")),
    EventKeywordRule("EVT-EARN-003", "业绩快报", ("业绩快报",)),
    EventKeywordRule("EVT-CA-001", "除权除息", ("除权除息", "分红派息", "送转")),
    EventKeywordRule("EVT-CA-002", "限售解禁", ("限售解禁", "解禁")),
    EventKeywordRule("EVT-CA-003", "停复牌", ("停牌", "复牌")),
    EventKeywordRule("EVT-MACRO-001", "宏观发布", ("CPI", "PPI", "PMI", "社融", "MLF", "LPR", "议息")),
    EventKeywordRule("EVT-MKT-001", "指数成分调整", ("指数调整", "成分股调整", "调入", "调出")),
)


# ------------------------------------------------------------------
# 配置 / 输入 / 输出
# ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class DualTagConfig:
    """双标签配置（MVP 初拍值，可配常量）。"""

    capital_inflow_threshold: float = 1000.0  # 资金痕迹阈值（万元，T-3~T-1 主力净流入）
    gap_tolerance_pct: float = 5.0  # 预期差容差 %（|gap|≤容差=符合预期）
    anchor_field: str = "forecast_eps"  # 锚标量字段（forecast_eps/forecast_pe）
    calendar_rules: tuple[EventKeywordRule, ...] | None = None  # None=默认规则组


@dataclass(frozen=True, slots=True)
class NewsTagInput:
    """单条新闻打标输入。"""

    news_id: str
    title: str
    publish_time: str
    content: str = ""
    symbols: tuple[str, ...] = ()  # 新闻提及标的（注入位；NLP 抽取为后续件）
    actual_value: float | None = None  # 实际值（注入位，如业绩预告净利润/EPS）
    actual_symbol: str | None = None  # 实际值对应标的（None=取 symbols[0]）


@dataclass(frozen=True, slots=True)
class ConsensusAnchor:
    """一致预期锚（analyst_forecast 行映射；GAP-F-D1 已核数据源）。"""

    symbol: str
    forecast_year: str
    forecast_eps: float | None
    forecast_pe: float | None
    rating: str
    analyst_count: int
    report_date: str


@dataclass(frozen=True, slots=True)
class NewsTagItem:
    """单条新闻双标签条目。"""

    news_id: str
    title: str
    predictability_label: str  # 可预测性四态之一
    predictability_reasons: list[str] = field(default_factory=list)
    expectation_label: str = GAP_NO_ANCHOR  # 预期差四态之一
    expectation_gap_pct: float | None = None
    anchor_symbol: str = ""
    anchor_missing: bool = True  # 锚/实际值缺失留痕


@dataclass(frozen=True, slots=True)
class NewsDualTagResult:
    """双标签输出契约（观测层消费，不接交易）。"""

    date: str
    items: list[NewsTagItem] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)  # 标签计数
    degraded: bool = False
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 纯函数核
# ------------------------------------------------------------------


def match_calendar_rules(
    text: str,
    rules: tuple[EventKeywordRule, ...] | list[EventKeywordRule] | None = None,
) -> list[EventKeywordRule]:
    """日历关键词命中：文本命中规则任一关键词且规则有提前披露纪律 → 命中。"""
    effective = rules if rules is not None else _DEFAULT_CALENDAR_RULES
    return [
        r for r in effective if r.advance_notice and any(k in text for k in r.keywords)
    ]


def classify_predictability(calendar_hit: bool, capital_hit: bool) -> str:
    """可预测性四态判定（封闭集合）。"""
    if calendar_hit and capital_hit:
        return PRED_BOTH
    if calendar_hit:
        return PRED_CALENDAR
    if capital_hit:
        return PRED_CAPITAL
    return PRED_SURPRISE


def classify_expectation_gap(
    actual: float | None,
    anchor: float | None,
    tolerance_pct: float = 5.0,
) -> tuple[str, float | None]:
    """预期差四态判定：gap_pct=(actual-anchor)/|anchor|×100。

    anchor 为 0/None 或 actual None → (无锚未定, None)（不出伪预期差）。
    """
    if actual is None or anchor is None or anchor == 0:
        return GAP_NO_ANCHOR, None
    gap_pct = (actual - anchor) / abs(anchor) * 100.0
    if gap_pct > tolerance_pct:
        return GAP_BEAT, round(gap_pct, 2)
    if gap_pct < -tolerance_pct:
        return GAP_MISS, round(gap_pct, 2)
    return GAP_MEET, round(gap_pct, 2)


def _anchor_value(anchor: ConsensusAnchor, field_name: str) -> float | None:
    """取锚标量（config.anchor_field 指定；非法字段名 ValueError fail-closed）。"""
    if field_name == "forecast_eps":
        return anchor.forecast_eps
    if field_name == "forecast_pe":
        return anchor.forecast_pe
    raise ValueError(f"非法 anchor_field: {field_name}")


def tag_news_dual(
    news_items: list[NewsTagInput],
    capital_traces: Mapping[str, float] | None = None,
    anchors: Mapping[str, ConsensusAnchor] | None = None,
    config: DualTagConfig | None = None,
    trade_date: str | date | datetime | None = None,
) -> NewsDualTagResult:
    """双标签主核（纯函数，不触库）。

    Args:
        news_items: 新闻清单（symbols/actual_value 为注入位）。
        capital_traces: 资金痕迹 {symbol: 净流入万元}（None=无痕迹腿）。
        anchors: 一致预期锚 {symbol: ConsensusAnchor}（None=全 无锚未定）。
        config: 配置（None 用默认）。
        trade_date: 数据日（结果 date 字段；None=空串）。
    """
    cfg = config or DualTagConfig()
    traces = capital_traces or {}
    anchor_map = anchors or {}
    rules = cfg.calendar_rules if cfg.calendar_rules is not None else _DEFAULT_CALENDAR_RULES

    items: list[NewsTagItem] = []
    counts: dict[str, int] = {}
    for news in news_items:
        text = news.title + news.content
        # 标签①：日历 + 资金痕迹
        cal_hits = match_calendar_rules(text, rules)
        cap_symbols = [
            s for s in news.symbols if abs(traces.get(s, 0.0)) >= cfg.capital_inflow_threshold
        ]
        pred_label = classify_predictability(bool(cal_hits), bool(cap_symbols))
        reasons: list[str] = []
        if cal_hits:
            reasons.append(f"日历命中：{'/'.join(r.name_zh for r in cal_hits)}")
        if cap_symbols:
            reasons.append(
                f"资金痕迹：{'/'.join(cap_symbols)} 净流入超阈值{cfg.capital_inflow_threshold:.0f}万"
            )
        if not reasons:
            reasons.append("无日历命中且无资金痕迹")

        # 标签②：预期差（锚/实际值缺 → 无锚未定）
        anchor_symbol = news.actual_symbol or (news.symbols[0] if news.symbols else "")
        anchor = anchor_map.get(anchor_symbol)
        anchor_val = _anchor_value(anchor, cfg.anchor_field) if anchor is not None else None
        gap_label, gap_pct = classify_expectation_gap(news.actual_value, anchor_val, cfg.gap_tolerance_pct)

        items.append(
            NewsTagItem(
                news_id=news.news_id,
                title=news.title,
                predictability_label=pred_label,
                predictability_reasons=reasons,
                expectation_label=gap_label,
                expectation_gap_pct=gap_pct,
                anchor_symbol=anchor_symbol,
                anchor_missing=gap_label == GAP_NO_ANCHOR,
            )
        )
        counts[pred_label] = counts.get(pred_label, 0) + 1
        counts[gap_label] = counts.get(gap_label, 0) + 1

    date_str = ""
    if trade_date is not None:
        if isinstance(trade_date, datetime):
            date_str = trade_date.date().isoformat()
        elif isinstance(trade_date, date):
            date_str = trade_date.isoformat()
        else:
            date_str = datetime.strptime(str(trade_date), "%Y-%m-%d").date().isoformat()
    return NewsDualTagResult(date=date_str, items=items, counts=counts)


# ------------------------------------------------------------------
# 锚加载层（analyst_forecast，GAP-F-D1 已核数据源；注入位可 mock）
# ------------------------------------------------------------------


def load_consensus_anchors(
    symbols: list[str],
    trade_date: str | date | datetime,
    ch_client: Any | None = None,
) -> dict[str, ConsensusAnchor]:
    """从 analyst_forecast 加载一致预期锚（每标的取 PIT 最新一条）。

    Args:
        symbols: 标的清单（空列表 → 空映射）。
        trade_date: 数据日（PIT 上限，report_date ≤ 该日）。
        ch_client: clickhouse-driver 鸭子类型；None 延迟取 ch_writer 默认客户端，
            不可得 → RuntimeError（调用方捕获降级）。

    Returns:
        {symbol: ConsensusAnchor}；无锚标的不出现在映射中。
    """
    if not symbols:
        return {}
    if isinstance(trade_date, datetime):
        current = trade_date.date()
    elif isinstance(trade_date, date):
        current = trade_date
    else:
        current = datetime.strptime(str(trade_date), "%Y-%m-%d").date()  # ValueError fail-closed
    client = ch_client
    if client is None:
        from zephyr.data.ch_writer import get_client

        client = get_client()
    rows = client.execute(SQL_CONSENSUS_ANCHOR, {"symbols": tuple(symbols), "trade_date": current})
    out: dict[str, ConsensusAnchor] = {}
    for r in rows:  # ORDER BY symbol, report_date DESC → 首见即最新
        symbol = str(r[0])
        if symbol in out:
            continue
        out[symbol] = ConsensusAnchor(
            symbol=symbol,
            forecast_year=str(r[1]),
            forecast_eps=float(r[2]) if r[2] is not None else None,
            forecast_pe=float(r[3]) if r[3] is not None else None,
            rating=str(r[4] or ""),
            analyst_count=int(r[5] or 0),
            report_date=str(r[6]),
        )
    return out


#: 锚供给器协议（注入位/mock 位）：symbols + date → 锚映射
AnchorProvider = Callable[[list[str], "str | date | datetime"], Mapping[str, ConsensusAnchor]]
