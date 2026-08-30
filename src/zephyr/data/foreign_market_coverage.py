# [BLUEPRINT] MOD-DAT-foreign_coverage | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-23 行 + GAP-F-D3 核查）
# [MODULE] zephyr.data.foreign_market_coverage
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader（只读查询层）; c1_market.us_index / us_futures_intraday / kline_us_daily（只读探测）
# [CONSUMERS] （候选：外盘 12 迷你卡数据健康条、GAP-F-24 对A股影响判定引擎前置）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 只读核查（SELECT 探测，禁写库）；禁真连外网采集（缺口标的仅留采集配置位 FOREIGN_COLLECTOR_SLOTS，接线走 tasks.yaml CTR 流程）；状态三态封闭 covered/stale/missing；表不存在/查询异常→该探测点 error 留痕不误判 covered；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-23 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询函数异常→探测点 error 记录不抛；日期解析失败→stale 判定保守化（按 missing 口径报）
# [TESTS] tests/zephyr/data/test_foreign_market_coverage.py
# [A_module] module_id=MOD-DAT-foreign_coverage | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-DAT-foreign_coverage — 外盘 12 标的数据覆盖核查器（GAP-F-23 / GAP-F-D3）。

外盘页 12 迷你卡标的：道指/纳指/标普/恒生/日经/KOSPI/A50/美元指数/离岸人民币/
WTI/黄金/美债10Y。本模块职责：

1. **只读核查**（GAP-F-D3 内容）：按 FOREIGN_WATCHLIST 探测配置逐标的
   SELECT symbol/count/min/max(trade_date)，判定 covered/stale/missing 三态。
2. **缺口采集配置位**：缺口标的只留 FOREIGN_COLLECTOR_SLOTS 采集配置草案
   （provider/capability/schedule 建议），本模块**禁真连外网采集**——
   接线走 tasks.yaml + CTR 流程，Owner 窗口执行。

GAP-F-D3 实测（2026-08-23，本模块核查函数产出）：us_index=DJI/IXIC/SPX
（各 29 行，2026-07-14~08-21）；us_futures_intraday=ES/NQ/CHA50CFD（各 1 行，
2026-08-22 单日快照）；kline_us_daily 仅 1 个空 symbol 19 行（垃圾数据）；
kline_index 1,097 只无全球指数；macro_data 无 DXY/USDCNH/WTI/黄金/美债10Y；
FRED/EIA 在 ClickHouse 无落库表。→ 4/12 有覆盖（A50 仅单日盘中快照），8 缺口。

2026-08-30 接线落地（designmemos 清单 #6）：kline_global 新表承载
HSI/N225/KOSPI/CL/GC（首采 9,967 行）；DXY/美债10Y 由 macro_data FRED 通道
承载（FRED_DXY/FRED_DGS10_US 已刷新）；USDCNH 免费日频源全失效登记跳过。
FOREIGN_WATCHLIST 探针已挂接实绩表——本核查器 missing 口径随接线实时反映。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Callable, Final

logger = logging.getLogger(__name__)

__all__: Final = [
    "FOREIGN_COLLECTOR_SLOTS",
    "FOREIGN_WATCHLIST",
    "ForeignCoverageItem",
    "ForeignCoverageReport",
    "ForeignTarget",
    "TableProbe",
    "TableProbeSpec",
    "check_foreign_coverage",
    "gap_collector_slots",
]

#: 覆盖状态三态（封闭集合）
STATUS_COVERED: Final[str] = "covered"
STATUS_STALE: Final[str] = "stale"
STATUS_MISSING: Final[str] = "missing"


@dataclass(frozen=True, slots=True)
class TableProbeSpec:
    """探测配置：候选表 + 标的一组。"""

    table: str  # 全限定表名
    symbols: tuple[str, ...]  # 候选 symbol（IN 查询）
    symbol_col: str = "symbol"  # 标的列名（macro_data=indicator_name）
    date_col: str = "trade_date"  # 日期列名（macro_data=report_date）


@dataclass(frozen=True, slots=True)
class ForeignTarget:
    """外盘标的观察清单条目。"""

    key: str  # 英文键（dow_jones 等）
    name_zh: str  # 中文名（道指等）
    asset_class: str  # index/futures/forex/commodity/bond
    probes: tuple[TableProbeSpec, ...]  # 探测点（空=库内无表，直接缺口）
    collector_slot: str  # 缺口采集配置位键（FOREIGN_COLLECTOR_SLOTS）


@dataclass(frozen=True, slots=True)
class TableProbe:
    """单探测点结果。"""

    table: str
    symbol: str
    rows: int
    first_date: str
    last_date: str
    error: str = ""  # 查询异常留痕（表不存在等）


@dataclass(frozen=True, slots=True)
class ForeignCoverageItem:
    """单标的覆盖判定。"""

    key: str
    name_zh: str
    asset_class: str
    status: str  # covered/stale/missing
    probes: list[TableProbe] = field(default_factory=list)
    collector_slot: str = ""
    note: str = ""


@dataclass(frozen=True, slots=True)
class ForeignCoverageReport:
    """外盘覆盖核查报告（GAP-F-D3 核查产出形态）。"""

    check_date: str
    items: list[ForeignCoverageItem] = field(default_factory=list)
    covered_count: int = 0
    stale_count: int = 0
    missing_count: int = 0
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 观察清单（12 标的；探测配置=GAP-F-D3 实证可探测表）
# ------------------------------------------------------------------

FOREIGN_WATCHLIST: Final[tuple[ForeignTarget, ...]] = (
    ForeignTarget("dow_jones", "道琼斯", "index", (TableProbeSpec("c1_market.us_index", ("DJI", ".DJI")),), ""),
    ForeignTarget("nasdaq", "纳斯达克", "index", (TableProbeSpec("c1_market.us_index", ("IXIC", ".IXIC")),), ""),
    ForeignTarget("sp500", "标普500", "index", (TableProbeSpec("c1_market.us_index", ("SPX", ".INX")),), ""),
    ForeignTarget("hsi", "恒生指数", "index", (TableProbeSpec("c1_market.kline_global", ("HSI",)),), "hsi_index"),
    ForeignTarget("nikkei", "日经225", "index", (TableProbeSpec("c1_market.kline_global", ("N225",)),), "nikkei_index"),
    ForeignTarget("kospi", "KOSPI", "index", (TableProbeSpec("c1_market.kline_global", ("KOSPI",)),), "kospi_index"),
    ForeignTarget("a50", "富时A50", "futures", (TableProbeSpec("c1_market.us_futures_intraday", ("CHA50CFD",)),), ""),
    ForeignTarget("dxy", "美元指数", "forex",
                  (TableProbeSpec("c1_market.macro_data", ("FRED_DXY",), "indicator_name", "report_date"),),
                  "dxy_forex"),
    ForeignTarget("usdcnh", "离岸人民币", "forex", (), "usdcnh_forex"),
    ForeignTarget("wti", "WTI原油", "commodity", (TableProbeSpec("c1_market.kline_global", ("CL",)),), "wti_commodity"),
    ForeignTarget("gold", "黄金", "commodity", (TableProbeSpec("c1_market.kline_global", ("GC",)),), "gold_commodity"),
    ForeignTarget("ust10y", "美债10Y", "bond",
                  (TableProbeSpec("c1_market.macro_data", ("FRED_DGS10_US",), "indicator_name", "report_date"),),
                  "ust10y_bond"),
)

#: 缺口标的采集配置位（2026-08-30 接线落地：草案 hint 已按实证裁定修订为实绩口径——
#: 5 只价格型落 c1_market.kline_global，DXY/美债10Y 走 macro_data FRED 既有通道，
#: USDCNH 免费日频源全失效登记跳过；tasks.yaml 已登记，详见 .runtime/foreign8_wiring/20260830_report.md）
FOREIGN_COLLECTOR_SLOTS: Final[dict[str, dict[str, str]]] = {
    "hsi_index": {
        "target": "恒生指数",
        "provider_hint": "akshare stock_hk_index_daily_sina(HSI)（index_global_em 已于 1.18.75 下架，实证不可用）",
        "capability_hint": "global_index_daily（新品类；provider 接线待 akshare 窗口，tasks.yaml 已 disabled 登记）",
        "table_hint": "c1_market.kline_global（已建，CTR 2026-08-30）",
        "schedule_hint": "daily_kline",
    },
    "nikkei_index": {
        "target": "日经225",
        "provider_hint": "akshare index_global_hist_sina(日经225指数)（sina 全球指数历史，实测 1000 行上限≈4年）",
        "capability_hint": "global_index_daily（同上品类复用）",
        "table_hint": "c1_market.kline_global（同表，symbol=N225）",
        "schedule_hint": "daily_kline",
    },
    "kospi_index": {
        "target": "KOSPI",
        "provider_hint": "akshare index_global_hist_sina(首尔综合指数)（源末日常见 close=0 坏点，采集端已过滤）",
        "capability_hint": "global_index_daily（同上品类复用）",
        "table_hint": "c1_market.kline_global（同表，symbol=KOSPI）",
        "schedule_hint": "daily_kline",
    },
    "dxy_forex": {
        "target": "美元指数",
        "provider_hint": "fred_provider DTWEXBGS（sina DINIW/DX 实证失效、东财不可达；FRED 广义美元指数为项目既有命名口径）",
        "capability_hint": "macro_fred（既有能力，macro_fred_incremental 任务承载）",
        "table_hint": "c1_market.macro_data（indicator_name=FRED_DXY）",
        "schedule_hint": "daily_capital",
    },
    "usdcnh_forex": {
        "target": "离岸人民币",
        "provider_hint": "无可用免费日频历史源（sina forex JSONP 404 / hf null / 东财不可达 / FRED 无 CNH / currencyscoop 需付费 key）——登记跳过",
        "capability_hint": "forex_daily（待有源后登记）",
        "table_hint": "c1_market.kline_global（预留，symbol=USDCNH）",
        "schedule_hint": "daily_kline",
    },
    "wti_commodity": {
        "target": "WTI原油",
        "provider_hint": "akshare futures_foreign_hist(CL)（sina hf 外盘期货日K，实测 2016 起可用）",
        "capability_hint": "a50_futures_daily（provider 既有通用机制：payload.symbols 覆盖默认品种直写 kline_global）",
        "table_hint": "c1_market.kline_global（已建，symbol=CL）",
        "schedule_hint": "pre_market",
    },
    "gold_commodity": {
        "target": "黄金",
        "provider_hint": "akshare futures_foreign_hist(GC)（COMEX 黄金期货，sina hf 同上通道）",
        "capability_hint": "a50_futures_daily（同上通用机制复用）",
        "table_hint": "c1_market.kline_global（已建，symbol=GC）",
        "schedule_hint": "pre_market",
    },
    "ust10y_bond": {
        "target": "美债10Y",
        "provider_hint": "fred_provider DGS10（prod 现成，macro_fred_incremental 承载；2026-08-30 已一次性刷新至 2026-08-27）",
        "capability_hint": "macro_fred（既有能力）",
        "table_hint": "c1_market.macro_data（indicator_name=FRED_DGS10_US）",
        "schedule_hint": "daily_capital",
    },
}

#: 探测 SQL（§5.160.2 集中化；symbol IN 列表由代码内部转义构造；列名经 TableProbeSpec 注入，默认 symbol/trade_date）
_SQL_PROBE_TEMPLATE: Final = (
    "SELECT {symbol_col}, count(), min({date_col}), max({date_col}) FROM {table} "
    "WHERE {symbol_col} IN ({symbols}) GROUP BY {symbol_col}"
)


# ------------------------------------------------------------------
# 核查核（query_fn 注入，测试全 mock；默认 ch_reader 只读）
# ------------------------------------------------------------------


def _default_query(sql: str) -> str:
    from zephyr.data import ch_reader

    return ch_reader.query(sql)


def _escape_symbols(symbols: tuple[str, ...]) -> str:
    """symbol 白名单转义（仅允许字母数字/点/下划线，防注入）。"""
    import re

    out: list[str] = []
    for s in symbols:
        if not re.fullmatch(r"[A-Za-z0-9._]+", s):
            raise ValueError(f"非法 symbol 字符: {s}")
        out.append(f"'{s}'")
    return ", ".join(out)


def _parse_probe_rows(tsv: str) -> list[TableProbe]:
    """解析探测 TSV：symbol \\t rows \\t first \\t last。"""
    probes: list[TableProbe] = []
    for line in (tsv or "").splitlines():
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        try:
            rows = int(parts[1])
        except ValueError:
            continue
        probes.append(
            TableProbe(
                table="", symbol=parts[0], rows=rows,
                first_date=parts[2][:10], last_date=parts[3][:10],
            )
        )
    return probes


def _is_fresh(last_date: str, today: date, stale_calendar_days: int) -> bool:
    """新鲜度判定：last_date 距 today ≤ stale_calendar_days 自然日。"""
    try:
        last = datetime.strptime(last_date, "%Y-%m-%d").date()
    except ValueError:
        return False
    return (today - last).days <= stale_calendar_days


def check_foreign_coverage(
    query_fn: Callable[[str], str] | None = None,
    check_date: str | date | datetime | None = None,
    stale_calendar_days: int = 10,
    watchlist: tuple[ForeignTarget, ...] | list[ForeignTarget] | None = None,
) -> ForeignCoverageReport:
    """外盘 12 标的覆盖核查（只读；query_fn 注入位，测试全 mock）。

    Args:
        query_fn: SQL→TSV 查询函数（None=ch_reader 只读默认）。
        check_date: 核查日（新鲜度基准；None=今日）。
        stale_calendar_days: 新鲜度窗（自然日，默认 10——覆盖周末+小长假）。
        watchlist: 观察清单（None=FOREIGN_WATCHLIST 12 标的）。

    Returns:
        ForeignCoverageReport；单探测点异常 → error 留痕不误判 covered。
    """
    run_query = query_fn or _default_query
    if check_date is None:
        today = date.today()
    elif isinstance(check_date, datetime):
        today = check_date.date()
    elif isinstance(check_date, date):
        today = check_date
    else:
        today = datetime.strptime(str(check_date), "%Y-%m-%d").date()  # ValueError fail-closed

    targets = watchlist if watchlist is not None else FOREIGN_WATCHLIST
    items: list[ForeignCoverageItem] = []
    notes: list[str] = []
    for target in targets:
        probes: list[TableProbe] = []
        for spec in target.probes:
            sql = _SQL_PROBE_TEMPLATE.format(
                table=spec.table, symbols=_escape_symbols(spec.symbols),
                symbol_col=spec.symbol_col, date_col=spec.date_col,
            )
            try:
                tsv = run_query(sql)
            except Exception as e:  # noqa: BLE001 — 探测异常留痕不误判
                probes.append(TableProbe(table=spec.table, symbol="", rows=0, first_date="", last_date="", error=repr(e)))
                continue
            for p in _parse_probe_rows(tsv):
                probes.append(
                    TableProbe(table=spec.table, symbol=p.symbol, rows=p.rows,
                               first_date=p.first_date, last_date=p.last_date)
                )
        valid = [p for p in probes if not p.error and p.rows > 0 and p.symbol]
        if not valid:
            status = STATUS_MISSING
            note = "库内无有效数据" if target.probes else "库内无探测表（缺口标的，走采集配置位）"
        else:
            latest = max(p.last_date for p in valid)
            if _is_fresh(latest, today, stale_calendar_days):
                status = STATUS_COVERED
                note = f"最新数据 {latest}"
            else:
                status = STATUS_STALE
                note = f"数据陈旧（最新 {latest}，超 {stale_calendar_days} 天窗）"
        items.append(
            ForeignCoverageItem(
                key=target.key, name_zh=target.name_zh, asset_class=target.asset_class,
                status=status, probes=probes, collector_slot=target.collector_slot, note=note,
            )
        )

    covered = sum(1 for i in items if i.status == STATUS_COVERED)
    stale = sum(1 for i in items if i.status == STATUS_STALE)
    missing = sum(1 for i in items if i.status == STATUS_MISSING)
    notes.append(f"覆盖 {covered}/12，陈旧 {stale}，缺口 {missing}")
    return ForeignCoverageReport(
        check_date=today.isoformat(), items=items,
        covered_count=covered, stale_count=stale, missing_count=missing, notes=notes,
    )


def gap_collector_slots(
    report: ForeignCoverageReport,
) -> dict[str, dict[str, str]]:
    """缺口标的采集配置位：missing 标的 → FOREIGN_COLLECTOR_SLOTS 草案子集。"""
    out: dict[str, dict[str, str]] = {}
    for item in report.items:
        if item.status == STATUS_MISSING and item.collector_slot:
            slot = FOREIGN_COLLECTOR_SLOTS.get(item.collector_slot)
            if slot:
                out[item.collector_slot] = slot
    return out
