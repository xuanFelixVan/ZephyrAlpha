# [BLUEPRINT] MOD-SIG-070 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-14 行）
# [MODULE] zephyr.signal_ashare.limit_up_reason_attribution
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] c1_market.limit_up_down（只读）; c3_fundamental.news_data（只读）; c1_market.sector_constituent（只读）
# [CONSUMERS] （候选：板块页梯队明细"涨停原因分析"列）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 归因仅三级：个股新闻催化/板块联动/无明确归因——不出第四级伪精确；关键词命中全留痕（matched_keywords+news_id）；板块联动须满足 板块涨停家数≥阈值 且 板块有主题命中 双条件；PIT（新闻 publish_time ≤ 窗口末）；单源异常独立降级不炸整体；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-14 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询异常/客户端不可得→对应腿降级 notes 留痕不抛；trade_date 格式非法→ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_limit_up_reason_attribution.py
# [A_module] module_id=MOD-SIG-070 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-SIG-070 — 涨停原因归因（GAP-F-14，板块页梯队"涨停原因分析"列后端）。

MVP 口径（news_data × 涨停股 join，板块聚合+关键词匹配）：

1. **个股新闻催化**：新闻标题/正文直接点名涨停股（按股票名称子串匹配）→
   reason_type="个股新闻催化"，取时间最近 top-k 条留痕。
2. **板块主题聚合**：主题关键词词典（主题→别名组，常量可配）扫新闻 →
   主题命中；板块主题=该板块涨停股直命中新闻的主题 ∪ 点名板块名的新闻主题，
   按命中新闻数排序。
3. **板块联动**：个股无直命中新闻，但其所属板块 涨停家数≥sector_linkage_min_limitups
   且 板块主题命中数≥sector_linkage_min_theme_hits → reason_type="板块联动"，
   理由=板块名+领涨主题+涨停家数。
4. 以上皆无 → "无明确归因"（宁缺毋假，G4 反误导口径）。

数据真源：c1_market.limit_up_down（涨停票池）、c3_fundamental.news_data（新闻）、
c1_market.sector_constituent（SCD-2 时点板块归属）。全部只读；核函数纯函数可单测。

# [ALGO_FLOW]
# 层: 输入
# - id: I1 涨停票池 list[LimitUpStockInput]（symbol/name/pct_change/limit_type）
# - id: I2 新闻窗 list[NewsItemInput]（news_id/title/content/publish_time）
# - id: I3 板块归属映射 dict[symbol → list[(sector_code, sector_name)]]（SCD-2 时点）
# 层: 特征
# - id: F1 个股直命中（股票名 ∈ 新闻 title+content）
# - id: F2 主题命中（主题别名组 ∩ 新闻文本）
# - id: F3 板块主题聚合（板块内直命中主题 ∪ 板块名点名主题，按新闻数排序）
# 层: 算法
# - id: A1 三级归因判定（直命中→个股新闻催化；板块双条件→板块联动；否则无明确归因）
# 层: 输出
# - id: O1 LimitUpAttributionResult（items 逐股归因 + sector_themes 板块主题榜 + stats 三桶计数）
# [/ALGO_FLOW]
#
# 边:
# I1,I2 --> F1
# I2 --> F2
# F1,F2,I3 --> F3
# F1,F3,I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Final, Mapping

logger = logging.getLogger(__name__)

__all__: Final = [
    "AttributionConfig",
    "LimitUpAttributionResult",
    "LimitUpReasonItem",
    "LimitUpStockInput",
    "NewsItemInput",
    "SectorThemeItem",
    "ThemeHit",
    "attribute_limit_up_reasons",
    "attribute_stocks",
    "build_sector_themes",
    "match_stock_news",
    "match_themes",
]

# ------------------------------------------------------------------
# 常量（SQL 集中化 §5.160.2 + 主题词典可配置）
# ------------------------------------------------------------------

#: 涨停票池查询（limit_up_down 仅 涨停/跌停 两类，limit_type 过滤）
SQL_LIMIT_UP_POOL: Final = """
SELECT symbol, name, pct_change, amount
FROM c1_market.limit_up_down
WHERE trade_date = %(trade_date)s AND limit_type = %(limit_type)s
"""

#: 新闻窗查询（publish_time PIT 上限=窗口末）
SQL_NEWS_WINDOW: Final = """
SELECT news_id, publish_time, title, content
FROM c3_fundamental.news_data
WHERE publish_time >= %(start_ts)s AND publish_time <= %(end_ts)s
ORDER BY publish_time
"""

#: 板块归属（SCD-2 时点有效）
SQL_SECTOR_MAP: Final = """
SELECT stock_code, sector_code, sector_name
FROM c1_market.sector_constituent
WHERE valid_from <= %(trade_date)s AND (valid_to IS NULL OR valid_to > %(trade_date)s)
"""

#: 默认主题词典（主题 → 别名组；MVP 经验口径，可经 config.theme_keywords 覆盖）
_DEFAULT_THEME_KEYWORDS: Final[dict[str, tuple[str, ...]]] = {
    "半导体": ("半导体", "芯片", "晶圆", "存储器", "光刻", "EDA"),
    "人工智能": ("人工智能", "AI", "大模型", "算力", "AIGC", "ChatGPT"),
    "机器人": ("机器人", "人形机器人", "减速器", "伺服"),
    "新能源汽车": ("新能源汽车", "锂电", "动力电池", "充电桩", "固态电池", "锂矿"),
    "光伏": ("光伏", "硅片", "组件", "逆变器", "储能"),
    "军工": ("军工", "国防", "航母", "导弹", "低空经济", "商业航天"),
    "医药": ("医药", "创新药", "疫苗", "CXO", "医疗器械"),
    "券商金融": ("券商", "证券", "保险", "银行", "互联金融", "并购重组"),
    "消费": ("消费", "白酒", "食品", "免税", "零售", "家电"),
    "地产": ("地产", "房地产", "物业", "保障房", "城中村"),
    "有色资源": ("有色", "稀土", "黄金", "铜", "铝", "煤炭", "钢铁"),
    "数字经济": ("信创", "数据要素", "数字货币", "区块链", "东数西算", "云计算"),
    "5G通信": ("5G", "6G", "光模块", "CPO", "卫星互联网", "通信设备"),
    "游戏传媒": ("游戏", "传媒", "短剧", "影视", "电竞"),
    "政策宽松": ("降准", "降息", "MLF", "LPR", "特别国债", "刺激政策"),
    "关税贸易": ("关税", "贸易战", "出口管制", "反制", "跨境电商"),
    "业绩预告": ("业绩预告", "预增", "扭亏", "业绩快报", "净利润增长"),
    "回购增持": ("回购", "增持", "大股东增持", "员工持股"),
}

#: 归因类型枚举（三级封闭集合）
REASON_DIRECT_NEWS: Final[str] = "个股新闻催化"
REASON_SECTOR_LINKAGE: Final[str] = "板块联动"
REASON_UNATTRIBUTED: Final[str] = "无明确归因"


# ------------------------------------------------------------------
# 配置 / 输入 / 输出
# ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AttributionConfig:
    """涨停归因配置（MVP 初拍值，可配常量）。"""

    limit_type: str = "涨停"  # limit_up_down.limit_type 过滤值
    news_lookback_days: int = 2  # 新闻回溯窗（自然日，覆盖 T 日+前一日晚间）
    max_news_per_stock: int = 3  # 个股直命中留痕条数上限
    max_themes_per_sector: int = 3  # 板块主题榜长度上限
    sector_linkage_min_limitups: int = 2  # 板块联动双条件①：板块涨停家数下限
    sector_linkage_min_theme_hits: int = 1  # 板块联动双条件②：板块主题命中下限
    stock_name_min_len: int = 2  # 股票名匹配最小长度（防单字误配）
    theme_keywords: Mapping[str, tuple[str, ...]] | None = None  # None=默认词典


@dataclass(frozen=True, slots=True)
class LimitUpStockInput:
    """涨停票输入（limit_up_down 行映射）。"""

    symbol: str
    name: str
    pct_change: float = 0.0
    amount: float = 0.0  # 成交额（万元，limit_up_down 口径）


@dataclass(frozen=True, slots=True)
class NewsItemInput:
    """新闻输入（news_data 行映射）。"""

    news_id: str
    title: str
    publish_time: str  # YYYY-MM-DD HH:MM:SS
    content: str = ""


@dataclass(frozen=True, slots=True)
class ThemeHit:
    """主题命中留痕。"""

    theme: str
    hit_count: int  # 命中新闻条数
    sample_news_ids: list[str] = field(default_factory=list)  # 样本 news_id（截断留痕）


@dataclass(frozen=True, slots=True)
class LimitUpReasonItem:
    """单票涨停归因条目。"""

    symbol: str
    name: str
    reason_type: str  # 三级封闭集合之一
    reason_text: str  # 中文可读理由（审计留痕）
    sector_code: str = ""
    sector_name: str = ""
    matched_news_ids: list[str] = field(default_factory=list)
    matched_keywords: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class SectorThemeItem:
    """板块主题聚合条目。"""

    sector_code: str
    sector_name: str
    limit_up_count: int
    themes: list[ThemeHit] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class LimitUpAttributionResult:
    """涨停归因输出契约（观测层消费，不接交易）。"""

    date: str  # 数据日 YYYY-MM-DD
    items: list[LimitUpReasonItem] = field(default_factory=list)
    sector_themes: list[SectorThemeItem] = field(default_factory=list)
    stats: dict[str, int] = field(default_factory=dict)  # 三桶计数
    degraded: bool = False
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 纯函数核（不触库，可单测）
# ------------------------------------------------------------------


def match_stock_news(
    stock: LimitUpStockInput,
    news_items: list[NewsItemInput],
    config: AttributionConfig | None = None,
) -> list[NewsItemInput]:
    """个股直命中：股票名出现在新闻 标题+正文（按发布时间倒序取 top-k）。"""
    cfg = config or AttributionConfig()
    name = stock.name.strip()
    if len(name) < cfg.stock_name_min_len:
        return []
    hits = [n for n in news_items if name in (n.title + n.content)]
    hits.sort(key=lambda n: n.publish_time, reverse=True)
    return hits[: cfg.max_news_per_stock]


def match_themes(
    text: str,
    theme_keywords: Mapping[str, tuple[str, ...]] | None = None,
) -> list[str]:
    """主题命中：文本命中主题别名组任一别名 → 该主题命中（返回主题名列表，确定性序）。"""
    keywords = theme_keywords or _DEFAULT_THEME_KEYWORDS
    return [theme for theme, aliases in keywords.items() if any(a in text for a in aliases)]


def build_sector_themes(
    stocks: list[LimitUpStockInput],
    news_items: list[NewsItemInput],
    sector_map: Mapping[str, list[tuple[str, str]]],
    direct_hits: Mapping[str, list[NewsItemInput]],
    config: AttributionConfig | None = None,
) -> dict[str, SectorThemeItem]:
    """板块主题聚合：板块内涨停股直命中新闻主题 ∪ 点名板块名新闻主题，按命中数排序。"""
    cfg = config or AttributionConfig()
    keywords = cfg.theme_keywords or _DEFAULT_THEME_KEYWORDS

    # 板块 → 涨停股清单
    sector_stocks: dict[str, list[LimitUpStockInput]] = {}
    sector_names: dict[str, str] = {}
    for stock in stocks:
        for sector_code, sector_name in sector_map.get(stock.symbol, []):
            sector_stocks.setdefault(sector_code, []).append(stock)
            sector_names[sector_code] = sector_name

    # 新闻 → 主题（一次扫描复用）
    news_themes: dict[str, list[str]] = {n.news_id: match_themes(n.title + n.content, keywords) for n in news_items}

    out: dict[str, SectorThemeItem] = {}
    for sector_code, members in sector_stocks.items():
        sector_name = sector_names[sector_code]
        theme_news: dict[str, list[str]] = {}  # theme → news_id 列表
        # 腿1：板块内涨停股直命中新闻的主题
        for stock in members:
            for news in direct_hits.get(stock.symbol, []):
                for theme in news_themes.get(news.news_id, []):
                    theme_news.setdefault(theme, []).append(news.news_id)
        # 腿2：点名板块名的新闻主题
        for news in news_items:
            if sector_name and sector_name in (news.title + news.content):
                for theme in news_themes.get(news.news_id, []):
                    ids = theme_news.setdefault(theme, [])
                    if news.news_id not in ids:
                        ids.append(news.news_id)
        hits = [
            ThemeHit(theme=theme, hit_count=len(ids), sample_news_ids=ids[: cfg.max_news_per_stock])
            for theme, ids in theme_news.items()
        ]
        hits.sort(key=lambda h: (-h.hit_count, h.theme))
        out[sector_code] = SectorThemeItem(
            sector_code=sector_code,
            sector_name=sector_name,
            limit_up_count=len(members),
            themes=hits[: cfg.max_themes_per_sector],
        )
    return out


def attribute_stocks(
    stocks: list[LimitUpStockInput],
    news_items: list[NewsItemInput],
    sector_map: Mapping[str, list[tuple[str, str]]],
    config: AttributionConfig | None = None,
) -> tuple[list[LimitUpReasonItem], dict[str, SectorThemeItem], dict[str, int]]:
    """三级归因主核（纯函数）：直命中→个股新闻催化；板块双条件→板块联动；否则无明确归因。"""
    cfg = config or AttributionConfig()
    direct_hits: dict[str, list[NewsItemInput]] = {s.symbol: match_stock_news(s, news_items, cfg) for s in stocks}
    sector_themes = build_sector_themes(stocks, news_items, sector_map, direct_hits, cfg)

    items: list[LimitUpReasonItem] = []
    stats = {REASON_DIRECT_NEWS: 0, REASON_SECTOR_LINKAGE: 0, REASON_UNATTRIBUTED: 0}
    for stock in stocks:
        hits = direct_hits[stock.symbol]
        sectors = sector_map.get(stock.symbol, [])
        if hits:
            themes = sorted({t for n in hits for t in match_themes(n.title + n.content, cfg.theme_keywords)})
            top = hits[0]
            items.append(
                LimitUpReasonItem(
                    symbol=stock.symbol,
                    name=stock.name,
                    reason_type=REASON_DIRECT_NEWS,
                    reason_text=f"新闻直命中：{top.title[:40]}（{len(hits)}条）",
                    sector_code=sectors[0][0] if sectors else "",
                    sector_name=sectors[0][1] if sectors else "",
                    matched_news_ids=[n.news_id for n in hits],
                    matched_keywords=themes,
                )
            )
            stats[REASON_DIRECT_NEWS] += 1
            continue
        # 板块联动：取 涨停家数最高（并列取主题命中最多）的归属板块
        best: SectorThemeItem | None = None
        for sector_code, _ in sectors:
            cand = sector_themes.get(sector_code)
            if cand is None:
                continue
            if best is None or (cand.limit_up_count, sum(t.hit_count for t in cand.themes)) > (
                best.limit_up_count,
                sum(t.hit_count for t in best.themes),
            ):
                best = cand
        if (
            best is not None
            and best.limit_up_count >= cfg.sector_linkage_min_limitups
            and len(best.themes) >= cfg.sector_linkage_min_theme_hits
        ):
            top_theme = best.themes[0]
            items.append(
                LimitUpReasonItem(
                    symbol=stock.symbol,
                    name=stock.name,
                    reason_type=REASON_SECTOR_LINKAGE,
                    reason_text=(
                        f"{best.sector_name}板块涨停{best.limit_up_count}家，"
                        f"主题[{top_theme.theme}]命中{top_theme.hit_count}条"
                    ),
                    sector_code=best.sector_code,
                    sector_name=best.sector_name,
                    matched_news_ids=list(top_theme.sample_news_ids),
                    matched_keywords=[top_theme.theme],
                )
            )
            stats[REASON_SECTOR_LINKAGE] += 1
            continue
        items.append(
            LimitUpReasonItem(
                symbol=stock.symbol,
                name=stock.name,
                reason_type=REASON_UNATTRIBUTED,
                reason_text="窗口内未见个股新闻/板块主题催化（宁缺毋假）",
                sector_code=sectors[0][0] if sectors else "",
                sector_name=sectors[0][1] if sectors else "",
            )
        )
        stats[REASON_UNATTRIBUTED] += 1
    return items, sector_themes, stats


# ------------------------------------------------------------------
# 加载层（薄封装，ch_client 注入可 mock；异常独立降级）
# ------------------------------------------------------------------


def _normalize_date(trade_date: str | date | datetime) -> date:
    """归一化交易日（str 须 YYYY-MM-DD，非法格式 ValueError fail-closed）。"""
    if isinstance(trade_date, datetime):
        return trade_date.date()
    if isinstance(trade_date, date):
        return trade_date
    return datetime.strptime(str(trade_date), "%Y-%m-%d").date()


def _default_client() -> Any | None:
    """延迟加载默认 CH 客户端（不可用 → None 转降级）。"""
    try:
        from zephyr.data.ch_writer import get_client

        return get_client()
    except Exception:  # noqa: BLE001 — 连接/依赖问题一律降级
        logger.warning("ch_writer 默认客户端不可用，涨停归因降级", exc_info=True)
        return None


def _load_limit_up_stocks(client: Any, current: date, cfg: AttributionConfig) -> list[LimitUpStockInput]:
    rows = client.execute(SQL_LIMIT_UP_POOL, {"trade_date": current, "limit_type": cfg.limit_type})
    return [
        LimitUpStockInput(symbol=str(r[0]), name=str(r[1]), pct_change=float(r[2] or 0.0), amount=float(r[3] or 0.0))
        for r in rows
    ]


def _load_news(client: Any, current: date, cfg: AttributionConfig) -> list[NewsItemInput]:
    start = datetime.combine(current - timedelta(days=cfg.news_lookback_days), datetime.min.time())
    end = datetime.combine(current, datetime.max.time().replace(microsecond=0))
    rows = client.execute(SQL_NEWS_WINDOW, {"start_ts": start, "end_ts": end})
    return [
        NewsItemInput(news_id=str(r[0]), publish_time=str(r[1]), title=str(r[2] or ""), content=str(r[3] or ""))
        for r in rows
    ]


def _load_sector_map(client: Any, current: date) -> dict[str, list[tuple[str, str]]]:
    rows = client.execute(SQL_SECTOR_MAP, {"trade_date": current})
    out: dict[str, list[tuple[str, str]]] = {}
    for r in rows:
        out.setdefault(str(r[0]), []).append((str(r[1]), str(r[2])))
    return out


# ------------------------------------------------------------------
# 主入口
# ------------------------------------------------------------------


def attribute_limit_up_reasons(
    trade_date: str | date | datetime,
    ch_client: Any | None = None,
    config: AttributionConfig | None = None,
    stocks: list[LimitUpStockInput] | None = None,
    news_items: list[NewsItemInput] | None = None,
    sector_map: Mapping[str, list[tuple[str, str]]] | None = None,
) -> LimitUpAttributionResult:
    """涨停原因归因主入口。

    Args:
        trade_date: 数据日（YYYY-MM-DD，PIT 上限）。
        ch_client: clickhouse-driver 鸭子类型；None 延迟取默认客户端，不可得→degraded。
        config: 归因配置（None 用默认）。
        stocks/news_items/sector_map: 测试/编排注入位；None 时经 client 现查。
            三腿各自独立降级（异常 → 该腿空集 + notes 留痕，不炸整体）。

    Returns:
        LimitUpAttributionResult；票池为空 → items 空 + notes 留痕（非 degraded）。
    """
    cfg = config or AttributionConfig()
    current = _normalize_date(trade_date)  # ValueError fail-closed
    date_str = current.isoformat()
    notes: list[str] = []

    need_client = stocks is None or news_items is None or sector_map is None
    client = ch_client if ch_client is not None else (_default_client() if need_client else None)
    if need_client and client is None:
        return LimitUpAttributionResult(date=date_str, degraded=True, notes=["CH 客户端不可得，涨停归因整体降级"])

    if stocks is None:
        try:
            stocks = _load_limit_up_stocks(client, current, cfg)
        except Exception as e:  # noqa: BLE001 — 数据层异常独立降级
            stocks = []
            notes.append(f"limit_up_down 查询异常，票池腿降级: {e!r}")
    if news_items is None:
        try:
            news_items = _load_news(client, current, cfg)
        except Exception as e:  # noqa: BLE001
            news_items = []
            notes.append(f"news_data 查询异常，新闻腿降级: {e!r}")
    if sector_map is None:
        try:
            sector_map = _load_sector_map(client, current)
        except Exception as e:  # noqa: BLE001
            sector_map = {}
            notes.append(f"sector_constituent 查询异常，板块腿降级: {e!r}")

    if not stocks:
        notes.append("当日涨停票池为空")
        return LimitUpAttributionResult(date=date_str, stats={}, notes=notes)

    items, sector_themes, stats = attribute_stocks(stocks, news_items, sector_map, cfg)
    themes_board = sorted(sector_themes.values(), key=lambda s: (-s.limit_up_count, s.sector_code))
    return LimitUpAttributionResult(
        date=date_str,
        items=items,
        sector_themes=themes_board,
        stats=stats,
        notes=notes,
    )
