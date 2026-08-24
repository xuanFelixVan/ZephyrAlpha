# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.daban_board_event_deriver
# [DOMAIN] D_DATA
# [DEPENDENCIES] tushare SDK（stk_limit 每日涨跌停价格，延迟 import，token 读 TUSHARE_TOKEN）; clickhouse-driver（kline_daily/kline_1min/tick_data/stk_limit/st_stock_list 只读 SELECT）
# [CONSUMERS] （STR-DABAN-022 打板 sleeve 回测数据腿：封板时间/开板次数/封单代理/涨停池连板；tasks.yaml 接线待 DDL 建表后排期）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 匿名/只读访问（CH 全程 SELECT 零写入，落地产出=CSV 中间层）；涨停价解析链=库内 stk_limit→tushare stk_limit→规则推导，逐行 limit_src 留痕；规则口径=主板 10%/ST 5%、科创创业 20%、北证 30%，Decimal ROUND_HALF_UP 到分（经库内 stk_limit 重叠窗 88445 样本 100% 验证）；触板判定 eps=0.001；开板次数=分钟级下限口径（分钟内快开快合漏计）；封单代理=miniqmt tick 尾盘买一档（2026-07 起可得）；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] .runtime/construction_20260823/reports/BTRUN_report.md §3.2（STR-DABAN-022 数据缺口）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tushare 单日拉取异常→log warning+该日空列表（规则推导兜底）；trade_date 格式非法/日期窗倒置→ValueError（调用方契约违例）；DDL 未建表不落库（本模块只产 CSV，table 写库属 Owner 窗口）
# [TESTS] tests/zephyr/data/test_daban_board_event_deriver.py
# [A_module] module_id=MOD-DAT-daban_board_event_derive | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-DAT-daban_board_event_derive — 打板回测历史事件推导器（STR-DABAN-022 缺口）。

背景（BTRUN 报告 §3.2，2026-08-23 实证）：
    打板 sleeve 回测需要 封单金额 seal_amount / 封板时间 seal_time / 开板次数
    open_board_count——**无表无历史**；涨停池（limit_up_down/stk_limit）与竞价
    历史 ≤3 周。源调查（2026-08-24，probe1~8 留痕 .runtime/construction_20260825/）：
    - akshare stock_zt_pool_em（封板资金/首封/炸板）源侧仅保留最近约 30 个
      交易日，更早静默空帧 → 历史不可得（前瞻增量采集器=GAP-F-13
      limit_up_pool_collector 已在，testing）。
    - tushare limit_list_d（fd_amount/first_time/open_times）本机 token 无
      接口权限 → 不可得（实证异常留痕）。
    - **kline_daily 全史（1990+）+ kline_1min（2021-09 起，~5200 标的/日）+
      tick_data miniqmt 盘口量（2026-07 起 100% 非空）+ tushare stk_limit
      官方涨跌停价（2020+ 全市场）** → 三缺口历史可推导（代理口径）。

推导口径（全量经 probe 验证）：
    - 触板 touched：当日 high ≥ limit_up − 0.001；封住 close_sealed：close 同判；
      一字 is_one_word：low ≥ limit_up − 0.001。连板 consec_limit：封住日链式计数。
    - 首次触板 first_touch_time：kline_1min 首个 high ≥ 涨停价 的分钟（分钟级代理）。
    - 开板次数 open_board_count：分钟 walk——封板分钟（bar.low ≥ 涨停价）后
      每次 封→开 转换 +1（下限口径，分钟内快开快合漏计）。
    - 封单代理：tick_data 尾盘最后一笔 bid_price ≥ 涨停价 的 bid_volume（手），
      seal_amount_proxy = bid_volume × 100 × bid_price（元）；2026-07 前无盘口量
      → None（如实空缺不硬造）。
    - 涨停价解析链：①库内 c1_market.stk_limit（2026-08-03 起）②tushare
      stk_limit（2020+ 官方）③规则推导（st_stock_list SCD-2 + 昨收链）。

裁定（对齐 2026-08-23 SECTOR / 2026-08-24 D3FUND 先例）：**不直建表**。
本模块=推导器+CSV 中间层先行；DDL 建表（c1_market.daban_board_event，
apply_schema.py）+ business_data_categories.yaml 品类登记 + tasks.yaml 接线
三件为 Owner 窗口待办（DDL 申请草稿见
.runtime/construction_20260825/fragments/DABAN_data_ddl_draft.yaml）。

DDL 草稿（待统筹 CTR 评审后 apply_schema 执行）::

    CREATE TABLE IF NOT EXISTS c1_market.daban_board_event
    (
        trade_date        Date,
        symbol            String,
        board             LowCardinality(String),   -- sh_main/sz_main/star/chinext/bj
        st_flag           UInt8,                    -- 库内 stk_limit 源直给；其余源推断
        pre_close         Nullable(Decimal(18, 4)), -- kline 昨收链（原始价口径）
        limit_up_price    Decimal(18, 4),
        open              Decimal(18, 4),
        high              Decimal(18, 4),
        low               Decimal(18, 4),
        close             Decimal(18, 4),
        touched           UInt8,                    -- 盘中触板
        close_sealed      UInt8,                    -- 收盘封住
        is_one_word       UInt8,                    -- 一字板
        first_touch_time  Nullable(String),         -- HH:MM:SS 分钟级首触（kline_1min）
        open_board_count  Nullable(UInt16),         -- 开板次数（分钟级下限口径）
        seal_bid_volume   Nullable(UInt64),         -- 尾盘买一封单（手，tick 代理 2026-07 起）
        seal_amount_proxy Nullable(Decimal(20, 2)), -- 封单金额代理（元）
        consec_limit      UInt16,                   -- 连板数（封住日链）
        limit_src         LowCardinality(String),   -- ch_stk_limit/tushare_stk_limit/rule_derived
        data_source       LowCardinality(String) DEFAULT 'derived_kline',
        derive_version    LowCardinality(String) DEFAULT 'v1',
        ingest_ts         DateTime64(3, 'UTC') DEFAULT now()
    )
    ENGINE = ReplacingMergeTree
    PARTITION BY toYYYYMM(trade_date)
    ORDER BY (trade_date, symbol)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: c1_market.kline_daily 日 K（全史）+ stk_limit 涨停价（库内/tushare/规则三级解析）
#   fields: trade_date/symbol/open/high/low/close；limit_up/limit_down/st_flag
# - id: I2
#   name: c1_market.kline_1min 分钟 K（2021-09 起；仅触板候选 symbol-day 拉取）
# - id: I3
#   name: c1_market.tick_data miniqmt 盘口（2026-07 起；仅封住候选 symbol-day 拉取）
# 层: 算法
# - id: A1
#   name_zh: 日频事件推导（纯函数）
#   desc: derive_daily_events 触板/封住/一字判定 + 连板链 + 昨收链
# - id: A2
#   name_zh: 分钟级富化（纯函数）
#   desc: enrich_intraday 首触时刻 + 开板次数（封→开转换计数，下限口径）
# - id: A3
#   name_zh: 封单代理富化（纯函数）
#   desc: enrich_seal_ticks 尾盘最后一笔达标买一档 → 封单手数/金额代理
# - id: A4
#   name_zh: 编排采集
#   desc: collect_derived_events 窗口拉数（lookback 保连板链）→ 推导 → 富化 → CSV
# 层: 输出
# - id: O1
#   name_zh: DabanBoardEvent 行集 / CSV 路径
#   intro: 21 列 INSERT_COLUMNS 对齐 DDL 草稿列序；frozen dataclass asdict JSON 可序列化
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# I3 --> A3
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import csv
import logging
import re
import time
from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any, Callable, Final, Iterable, Mapping, Sequence

logger = logging.getLogger(__name__)

__all__: Final = [
    "CATEGORY_ID",
    "INSERT_COLUMNS",
    "LIMIT_EPS",
    "LP_INSERT_COLUMNS",
    "DabanBoardEvent",
    "LimitPriceRow",
    "board_of",
    "collect_derived_events",
    "derive_daily_events",
    "enrich_intraday",
    "enrich_seal_ticks",
    "fetch_stk_limit_tushare",
    "limit_prices_to_csv",
    "rule_limit_price",
    "to_csv",
]

#: 品类真源 category_id（business_data_categories.yaml 登记=Owner 窗口待办）
CATEGORY_ID: Final = "market_daban_board_event"

#: 事件表 INSERT 列序（对齐模块 docstring DDL 草稿；ingest_ts 为 DEFAULT 列不入列）
INSERT_COLUMNS: Final = (
    "trade_date",
    "symbol",
    "board",
    "st_flag",
    "pre_close",
    "limit_up_price",
    "open",
    "high",
    "low",
    "close",
    "touched",
    "close_sealed",
    "is_one_word",
    "first_touch_time",
    "open_board_count",
    "seal_bid_volume",
    "seal_amount_proxy",
    "consec_limit",
    "limit_src",
    "data_source",
    "derive_version",
)

#: 涨停价行 CSV 列序（stk_limit 历史补缺载荷，供 Owner 窗口回填既有表评审）
LP_INSERT_COLUMNS: Final = (
    "trade_date",
    "symbol",
    "pre_close",
    "limit_up",
    "limit_down",
    "board",
    "st_flag",
    "data_source",
)

#: 触板/封住判定容差（Decimal(18,4) 价格浮点安全边）
LIMIT_EPS: Final = 0.001

#: tushare 拉取限速（秒/日，对齐项目反爬护栏口径）
_TUSHARE_SLEEP: Final = 1.2

#: tick 盘口量可得起点（probe E2 实证：2026-07 起 bid_volume/ask_volume 100% 非空）
DEFAULT_TICKS_FROM: Final = date(2026, 7, 1)

#: 连板链/昨收链 lookback（自然日；≈28 交易日，覆盖现实连板长度）
_LOOKBACK_DAYS: Final = 40

_BOARD_PCT: Final = {
    ("sh_main", False): Decimal("0.10"),
    ("sh_main", True): Decimal("0.05"),
    ("sz_main", False): Decimal("0.10"),
    ("sz_main", True): Decimal("0.05"),
    ("star", False): Decimal("0.20"),
    ("star", True): Decimal("0.20"),  # 科创/创业 ST 不打折（20% 不变）
    ("chinext", False): Decimal("0.20"),
    ("chinext", True): Decimal("0.20"),
    ("bj", False): Decimal("0.30"),
    ("bj", True): Decimal("0.30"),
}


@dataclass(frozen=True, slots=True)
class LimitPriceRow:
    """涨停价行（三级解析链统一形态；pre_close/st_flag 源无则 None）。"""

    trade_date: str  # YYYY-MM-DD
    symbol: str  # 6 位裸码
    pre_close: float | None
    limit_up: float
    limit_down: float | None
    board: str
    st_flag: int | None
    data_source: str  # ch_stk_limit / tushare_stk_limit / rule_derived


@dataclass(frozen=True, slots=True)
class DabanBoardEvent:
    """打板事件行（触板 symbol-day；封板时间/开板次数/封单代理/连板 推导口径）。"""

    trade_date: str  # YYYY-MM-DD
    symbol: str  # 6 位裸码
    board: str  # sh_main/sz_main/star/chinext/bj
    st_flag: int  # 库内 stk_limit 源直给；tushare/规则源按有效幅度推断
    pre_close: float | None  # kline 昨收链（原始价口径，除权日不作复权调整）
    limit_up_price: float
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    touched: int  # 盘中触板（high ≥ limit−eps）
    close_sealed: int  # 收盘封住（close ≥ limit−eps）
    is_one_word: int  # 一字板（low ≥ limit−eps）
    first_touch_time: str | None  # HH:MM:SS 分钟级首触（kline_1min 推导；无分钟数据 None）
    open_board_count: int | None  # 开板次数（分钟级下限口径；无分钟数据 None）
    seal_bid_volume: int | None  # 尾盘买一封单（手；tick 代理，2026-07 起，否则 None）
    seal_amount_proxy: float | None  # 封单金额代理（元）= bid_volume×100×bid_price
    consec_limit: int  # 连板数（封住日链；未封住=0）
    limit_src: str  # 涨停价来源（ch_stk_limit/tushare_stk_limit/rule_derived）
    data_source: str = "derived_kline"
    derive_version: str = "v1"


# ---------------------------------------------------------------------------
# 纯函数层
# ---------------------------------------------------------------------------


def board_of(symbol: str) -> str:
    """板块分类（6 位裸码前缀）：sh_main/sz_main/star/chinext/bj/other。"""
    s = str(symbol or "")
    if s.startswith("60"):
        return "sh_main"
    if s.startswith("68"):
        return "star"
    if s.startswith(("000", "001", "002", "003")):
        return "sz_main"
    if s.startswith("30"):
        return "chinext"
    if s[:1] in ("4", "8") or s.startswith("92"):
        return "bj"
    return "other"


def rule_limit_price(
    pre_close: float | None,
    board: str,
    st_flag: bool,
) -> tuple[float, float] | None:
    """规则涨停价：昨收×(1±幅度) Decimal ROUND_HALF_UP 到分（交易所四舍五入口径）。

    幅度：主板 10%/ST 5%；科创/创业 20%（ST 不打折）；北证 30%。
    pre_close 缺失/非正 或 board 未知 → None（新股无涨跌幅限制日等场景跳过）。
    """
    if pre_close is None or pre_close <= 0:
        return None
    pct = _BOARD_PCT.get((board, bool(st_flag)))
    if pct is None:
        return None
    base = Decimal(str(pre_close))
    up = (base * (1 + pct)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    down = (base * (1 - pct)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(up), float(down)


def _normalize_date(trade_date: str | date | datetime) -> date:
    """归一化交易日（str 须 YYYY-MM-DD，非法格式抛 ValueError fail-closed）。"""
    if isinstance(trade_date, datetime):
        return trade_date.date()
    if isinstance(trade_date, date):
        return trade_date
    return datetime.strptime(str(trade_date), "%Y-%m-%d").date()


def _iso(d: Any) -> str:
    """date/datetime/'YYYY-MM-DD' 归一为 ISO 字符串（CH Date 列驱动返回 date 对象）。"""
    if isinstance(d, datetime):
        return d.date().isoformat()
    if isinstance(d, date):
        return d.isoformat()
    return str(d)[:10]


def _f(v: Any) -> float | None:
    """宽松浮点（None/NaN/非法 → None）。"""
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if f != f else f


def _hhmmss(t: Any) -> str | None:
    """trade_time/timestamp 归一 HH:MM:SS（str 尾部取时间；datetime 直取）。"""
    if isinstance(t, (datetime,)):
        return t.strftime("%H:%M:%S")
    s = str(t or "").strip()
    m = re.search(r"(\d{2}:\d{2}:\d{2})\s*$", s)
    return m.group(1) if m else None


def derive_daily_events(
    kline_rows: Iterable[Mapping[str, Any]],
    limit_price_map: Mapping[tuple[str, str], LimitPriceRow],
) -> list[DabanBoardEvent]:
    """日频事件推导（纯函数不触网不触库）。

    Args:
        kline_rows: 日 K 行迭代（trade_date/symbol/open/high/low/close）；
            调用方应给 lookback 延展窗口以保连板链/昨收链正确。
        limit_price_map: (iso_date, symbol) → LimitPriceRow（三级解析链产物）。

    Returns:
        触板 symbol-day 事件列表（未触板日不出行），按 (trade_date, symbol) 排序；
        涨停价缺失的 symbol-day 跳过（无法判定，不出伪事件）。
    """
    by_sym: dict[str, list[Mapping[str, Any]]] = {}
    for r in kline_rows:
        sym = str(r.get("symbol") or "")
        if sym:
            by_sym.setdefault(sym, []).append(r)
    out: list[DabanBoardEvent] = []
    for sym, rows in by_sym.items():
        rows = sorted(rows, key=lambda r: _iso(r.get("trade_date")))
        board = board_of(sym)
        prev_close: float | None = None
        consec = 0
        for r in rows:
            d = _iso(r.get("trade_date"))
            o, h, l, c = (_f(r.get(k)) for k in ("open", "high", "low", "close"))
            lp = limit_price_map.get((d, sym))
            if lp is not None:
                up = _f(lp.limit_up)
            else:
                up = None
            if up is not None and h is not None and c is not None and l is not None:
                touched = 1 if h >= up - LIMIT_EPS else 0
                if touched:
                    sealed = 1 if c >= up - LIMIT_EPS else 0
                    one_word = 1 if l >= up - LIMIT_EPS else 0
                    consec = consec + 1 if sealed else 0
                    st = lp.st_flag if lp.st_flag is not None else (
                        1 if (board in ("sh_main", "sz_main") and prev_close and up / prev_close <= 1.07) else 0
                    )
                    out.append(
                        DabanBoardEvent(
                            trade_date=d,
                            symbol=sym,
                            board=board,
                            st_flag=int(st),
                            pre_close=prev_close,
                            limit_up_price=up,
                            open=o,
                            high=h,
                            low=l,
                            close=c,
                            touched=1,
                            close_sealed=sealed,
                            is_one_word=one_word,
                            first_touch_time=None,
                            open_board_count=None,
                            seal_bid_volume=None,
                            seal_amount_proxy=None,
                            consec_limit=consec,
                            limit_src=lp.data_source,
                        )
                    )
                else:
                    consec = 0
            else:
                consec = 0
            prev_close = c if c is not None else prev_close
    out.sort(key=lambda e: (e.trade_date, e.symbol))
    return out


def enrich_intraday(
    events: Sequence[DabanBoardEvent],
    minute_rows: Iterable[Mapping[str, Any]],
) -> list[DabanBoardEvent]:
    """分钟级富化（纯函数）：首触时刻 + 开板次数（下限口径）。

    首触=首个 high ≥ 涨停价−eps 的分钟；开板=封板分钟（bar.low ≥ 涨停价−eps）
    之后的每次 封→开 转换（分钟内快开快合不可见=下限；从未出现封板分钟 → 0）。
    分钟数据缺失的事件字段保持 None（如实空缺）。
    """
    idx: dict[tuple[str, str], list[tuple[str, float | None, float | None]]] = {}
    for r in minute_rows:
        key = (_iso(r.get("trade_date")), str(r.get("symbol") or ""))
        idx.setdefault(key, []).append(
            (_hhmmss(r.get("trade_time")) or "", _f(r.get("high")), _f(r.get("low")))
        )
    for bars in idx.values():
        bars.sort(key=lambda b: b[0])
    out: list[DabanBoardEvent] = []
    for e in events:
        bars = idx.get((e.trade_date, e.symbol))
        if not bars:
            out.append(e)
            continue
        limit = e.limit_up_price
        first_touch: str | None = None
        seen_seal = False
        prev_sealed = False
        opens = 0
        for t, h, l in bars:
            if first_touch is None and h is not None and h >= limit - LIMIT_EPS:
                first_touch = t or None
            bar_sealed = l is not None and l >= limit - LIMIT_EPS
            if seen_seal and prev_sealed and not bar_sealed:
                opens += 1
            if bar_sealed:
                seen_seal = True
            prev_sealed = bar_sealed
        out.append(replace(e, first_touch_time=first_touch, open_board_count=opens))
    return out


def enrich_seal_ticks(
    events: Sequence[DabanBoardEvent],
    tick_rows: Iterable[Mapping[str, Any]],
) -> list[DabanBoardEvent]:
    """封单代理富化（纯函数）：收盘封住事件的尾盘买一挂单一档。

    取全日**最后一笔** bid_price ≥ 涨停价−eps 且 bid_volume 非空的 tick：
    seal_bid_volume=bid_volume（手），seal_amount_proxy=bid_volume×100×bid_price（元）。
    仅处理 close_sealed=1 事件（炸板未回封无收盘封单语义）；无达标 tick → None。
    """
    idx: dict[tuple[str, str], tuple[str, float, int]] = {}
    for r in tick_rows:
        bp = _f(r.get("bid_price"))
        bv = r.get("bid_volume")
        if bp is None or bv is None:
            continue
        try:
            bvi = int(bv)
        except (TypeError, ValueError):
            continue
        key = (_iso(r.get("trade_date")), str(r.get("symbol") or ""))
        t = _hhmmss(r.get("timestamp")) or ""
        cur = idx.get(key)
        if cur is None or t >= cur[0]:
            idx[key] = (t, bp, bvi)
    out: list[DabanBoardEvent] = []
    for e in events:
        if not e.close_sealed:
            out.append(e)
            continue
        hit = idx.get((e.trade_date, e.symbol))
        if hit is None or hit[1] < e.limit_up_price - LIMIT_EPS:
            out.append(e)
            continue
        _, bp, bv = hit
        out.append(
            replace(e, seal_bid_volume=bv, seal_amount_proxy=round(bv * 100 * bp, 2))
        )
    return out


# ---------------------------------------------------------------------------
# 源层（延迟 import / 注入位）
# ---------------------------------------------------------------------------


def fetch_stk_limit_tushare(
    trade_date: str | date | datetime,
    pro: Any | None = None,
) -> list[LimitPriceRow]:
    """tushare stk_limit 单日全市场涨跌停价格（官方口径，2020+ 深史）。

    源异常/空帧 → log warning + 空列表（对齐 _collect_limit_rows 容错口径；
    调用方 collect 以规则推导兜底，limit_src 逐行留痕）。
    """
    d = _normalize_date(trade_date)
    if pro is None:
        import os

        import tushare as ts

        token = os.environ.get("TUSHARE_TOKEN")
        if not token:
            logger.warning("TUSHARE_TOKEN 未设置，stk_limit(%s) 不可得", d.isoformat())
            return []
        ts.set_token(token)
        pro = ts.pro_api()
    try:
        df = pro.stk_limit(trade_date=d.strftime("%Y%m%d"))
    except Exception as e:  # noqa: BLE001 — 源失败容错不抛
        logger.warning("tushare stk_limit(%s) 失败: %s", d.isoformat(), e)
        return []
    if df is None or len(df) == 0:
        return []
    out: list[LimitPriceRow] = []
    for _, row in df.iterrows():
        sym = str(row.get("ts_code") or "")[:6]
        up = _f(row.get("up_limit"))
        if not sym or up is None:
            continue
        out.append(
            LimitPriceRow(
                trade_date=d.isoformat(),
                symbol=sym,
                pre_close=None,  # tushare stk_limit 无昨收列；昨收走 kline 链
                limit_up=up,
                limit_down=_f(row.get("down_limit")),
                board=board_of(sym),
                st_flag=None,  # 官方价已含 ST/除权效应，无需显式 ST 标记
                data_source="tushare_stk_limit",
            )
        )
    return out


def _tushare_pro() -> Any | None:
    """惰性构造 tushare pro 客户端；token 缺失/导入失败 → None（降级规则推导）。"""
    import os

    token = os.environ.get("TUSHARE_TOKEN")
    if not token:
        return None
    try:
        import tushare as ts

        ts.set_token(token)
        return ts.pro_api()
    except Exception as e:  # noqa: BLE001 — 降级容错
        logger.warning("tushare 初始化失败（降级规则推导）: %s", e)
        return None


def _load_ch_stk_limit(ch_client: Any, start: date, end: date) -> dict[tuple[str, str], LimitPriceRow]:
    """库内 stk_limit（2026-08-03 起覆盖）→ (date,symbol) 映射。"""
    rows = ch_client.execute(
        "SELECT trade_date, symbol, pre_close, limit_up, limit_down, st_flag "
        "FROM c1_market.stk_limit "
        f"WHERE trade_date >= toDate('{start.isoformat()}') AND trade_date <= toDate('{end.isoformat()}') "
        "AND limit_up IS NOT NULL"
    )
    out: dict[tuple[str, str], LimitPriceRow] = {}
    for d, sym, pre, up, down, st in rows:
        upf = _f(up)
        if upf is None:
            continue
        out[(_iso(d), str(sym))] = LimitPriceRow(
            trade_date=_iso(d),
            symbol=str(sym),
            pre_close=_f(pre),
            limit_up=upf,
            limit_down=_f(down),
            board=board_of(str(sym)),
            st_flag=int(st) if st is not None else None,
            data_source="ch_stk_limit",
        )
    return out


def _load_st_intervals(ch_client: Any, start: date, end: date) -> list[tuple[str, date, date | None]]:
    """st_stock_list SCD-2 区间（规则推导兜底的 ST 判定输入）。"""
    rows = ch_client.execute(
        "SELECT symbol, valid_from, valid_to FROM c1_market.st_stock_list "
        f"WHERE valid_from <= toDate('{end.isoformat()}') "
        f"AND (valid_to IS NULL OR valid_to > toDate('{start.isoformat()}'))"
    )
    return [(str(s), _normalize_date(_iso(vf)), (_normalize_date(_iso(vt)) if vt else None)) for s, vf, vt in rows]


def _st_at(intervals: list[tuple[str, date, date | None]], sym: str, d: date) -> bool:
    for s, vf, vt in intervals:
        if s == sym and vf <= d and (vt is None or vt > d):
            return True
    return False


# ---------------------------------------------------------------------------
# 编排层
# ---------------------------------------------------------------------------


def collect_derived_events(
    start: str | date | datetime,
    end: str | date | datetime,
    ch_client: Any,
    pro: Any | None = None,
    symbols: set[str] | None = None,
    intraday: bool = True,
    seal_ticks: bool = True,
    ticks_from: date = DEFAULT_TICKS_FROM,
    lookback_days: int = _LOOKBACK_DAYS,
    sleep: Callable[[float], None] = time.sleep,
) -> list[DabanBoardEvent]:
    """窗口打板事件推导编排（CH 只读；CSV 由 to_csv 另行落地）。

    Args:
        start/end: 事件窗口（含端点；lookback 自动前延展保连板链）。
        ch_client: clickhouse-driver 鸭子类型（必需，只读 SELECT）。
        pro: tushare pro 注入位（测试）；None 时惰性构造，不可用时降级规则推导。
        symbols: 可选标的过滤（None=全市场含北证）。
        intraday: True 时 kline_1min 富化首触/开板（仅触板候选 symbol-day）。
        seal_ticks: True 时 tick_data 富化封单代理（仅封住且 trade_date ≥ ticks_from）。
        ticks_from: tick 盘口量可得起点（probe 实证 2026-07-01）。
        lookback_days: 连板链/昨收链 lookback（自然日）。
        sleep: 限速注入位（tushare 拉取间隔；测试注 noop）。

    Returns:
        窗口内触板事件列表（按 trade_date, symbol 排序）。

    Raises:
        ValueError: 日期格式非法或窗口倒置（调用方契约违例）。
    """
    d0 = _normalize_date(start)
    d1 = _normalize_date(end)
    if d0 > d1:
        raise ValueError(f"窗口倒置: start={d0} > end={d1}")
    lb_start = d0 - timedelta(days=lookback_days)

    # 1) 日 K（lookback 延展窗）
    # kline_daily 存在 (symbol,trade_date) 重复行（ReplacingMergeTree 未收敛批次 +
    # 再 ingestion，probe H1 实证 002815@2026-08-21 两行）→ PIT 口径按 ingest_ts
    # 取最新行去重；同 ingest_ts 并列时保持后到行（驱动返回序）。
    kline_raw = ch_client.execute(
        "SELECT trade_date, symbol, open, high, low, close, ingest_ts FROM c1_market.kline_daily "
        f"WHERE trade_date >= toDate('{lb_start.isoformat()}') AND trade_date <= toDate('{d1.isoformat()}')"
    )
    dedup: dict[tuple[str, str], tuple[Any, dict]] = {}
    for d, s, o, h, l, c, its in kline_raw:
        sym = str(s)
        if board_of(sym) == "other" or (symbols is not None and sym not in symbols):
            continue
        key = (_iso(d), sym)
        row = {"trade_date": key[0], "symbol": sym, "open": o, "high": h, "low": l, "close": c}
        cur = dedup.get(key)
        if cur is None or str(its) >= str(cur[0]):
            dedup[key] = (its, row)
    kline_rows = [v[1] for v in dedup.values()]
    if not kline_rows:
        return []

    # 2) 涨停价三级解析：库内 → tushare（缺失交易日）→ 规则兜底
    lp_map = _load_ch_stk_limit(ch_client, lb_start, d1)
    trade_days = sorted({_iso(r["trade_date"]) for r in kline_rows})
    missing_days = [d for d in trade_days if not any(k[0] == d for k in lp_map)]
    if missing_days:
        if pro is None:
            pro = _tushare_pro()
        if pro is not None:
            first = True
            for ds in missing_days:
                if not first:
                    sleep(_TUSHARE_SLEEP)
                first = False
                for row in fetch_stk_limit_tushare(ds, pro=pro):
                    lp_map[(row.trade_date, row.symbol)] = row
    # 规则兜底：kline 有但两级源均缺的 (date,symbol)
    have = set(lp_map)
    need_rule = {
        (_iso(r["trade_date"]), str(r["symbol"]))
        for r in kline_rows
        if (_iso(r["trade_date"]), str(r["symbol"])) not in have
    }
    if need_rule:
        st_intervals = _load_st_intervals(ch_client, lb_start, d1)
        prev: dict[str, float] = {}
        for r in sorted(kline_rows, key=lambda x: (x["symbol"], _iso(x["trade_date"]))):
            sym = str(r["symbol"])
            ds = _iso(r["trade_date"])
            key = (ds, sym)
            c = _f(r["close"])
            if key in need_rule:
                pc = prev.get(sym)
                got = rule_limit_price(pc, board_of(sym), _st_at(st_intervals, sym, _normalize_date(ds)))
                if got is not None:
                    lp_map[key] = LimitPriceRow(
                        trade_date=ds,
                        symbol=sym,
                        pre_close=pc,
                        limit_up=got[0],
                        limit_down=got[1],
                        board=board_of(sym),
                        st_flag=1 if _st_at(st_intervals, sym, _normalize_date(ds)) else 0,
                        data_source="rule_derived",
                    )
            if c is not None:
                prev[sym] = c

    # 3) 日频推导 → 窗口过滤
    events = [
        e for e in derive_daily_events(kline_rows, lp_map)
        if d0.isoformat() <= e.trade_date <= d1.isoformat()
    ]
    if not events:
        return []

    # 4) 分钟级富化（按日分批，仅触板候选）
    if intraday:
        by_date: dict[str, set[str]] = {}
        for e in events:
            by_date.setdefault(e.trade_date, set()).add(e.symbol)
        min_rows: list[Mapping[str, Any]] = []
        for ds in sorted(by_date):
            syms = ",".join(f"'{s}'" for s in sorted(by_date[ds]))
            for d, s, t, h, l in ch_client.execute(
                "SELECT trade_date, symbol, trade_time, high, low FROM c1_market.kline_1min "
                f"WHERE trade_date = toDate('{ds}') AND symbol IN ({syms})"
            ):
                min_rows.append({"trade_date": _iso(d), "symbol": str(s), "trade_time": t, "high": h, "low": l})
        events = enrich_intraday(events, min_rows)

    # 5) tick 封单代理（按日分批，仅封住且 ≥ ticks_from）
    if seal_ticks:
        sealed_by_date: dict[str, set[str]] = {}
        for e in events:
            if e.close_sealed and _normalize_date(e.trade_date) >= ticks_from:
                sealed_by_date.setdefault(e.trade_date, set()).add(e.symbol)
        tick_rows: list[Mapping[str, Any]] = []
        for ds in sorted(sealed_by_date):
            syms = ",".join(f"'{s}'" for s in sorted(sealed_by_date[ds]))
            for s, t, bp, bv in ch_client.execute(
                "SELECT symbol, timestamp, bid_price, bid_volume FROM c1_market.tick_data "
                f"WHERE trade_date = toDate('{ds}') AND market_type = 'stock' AND symbol IN ({syms})"
            ):
                tick_rows.append({"trade_date": ds, "symbol": str(s), "timestamp": t, "bid_price": bp, "bid_volume": bv})
        events = enrich_seal_ticks(events, tick_rows)

    return events


# ---------------------------------------------------------------------------
# CSV 中间层
# ---------------------------------------------------------------------------


def _write_csv(rows: list[Mapping[str, Any]], columns: Sequence[str], path: str | Path, append: bool) -> str:
    if not rows:
        return ""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    write_header = not (append and p.exists())
    with p.open("a" if append else "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(columns))
        if write_header:
            writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return str(p)


def to_csv(
    events: Iterable[DabanBoardEvent],
    path: str | Path,
    append: bool = False,
) -> str:
    """事件 CSV 中间层（DDL 建表前的落地通道；幂等追加，header 不重复）。

    Returns:
        写入的文件路径；events 空 → 空串不建文件。
    """
    rows = [{c: getattr(e, c) for c in INSERT_COLUMNS} for e in events]
    return _write_csv(rows, INSERT_COLUMNS, path, append)


def limit_prices_to_csv(
    rows: Iterable[LimitPriceRow],
    path: str | Path,
    append: bool = False,
) -> str:
    """涨停价行 CSV（stk_limit 历史 ≤3 周缺口的补缺载荷，供 Owner 回填评审）。"""
    out = [{c: getattr(r, c) for c in LP_INSERT_COLUMNS} for r in rows]
    return _write_csv(out, LP_INSERT_COLUMNS, path, append)


def main() -> None:
    """入口——待 tasks.yaml 接线（DDL 建表后）。"""


if __name__ == "__main__":
    main()
