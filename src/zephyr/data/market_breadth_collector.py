# [BLUEPRINT] MOD-DATA-062 | 待统筹登记（blueprint 未建，真源=44号备忘 §2 M1-④ 行 + 92号清单 §8.2）
# [MODULE] zephyr.data.market_breadth_collector
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.table_registry; zephyr.data.ch_reader（ST 集加载，默认延迟加载可注入旁路）; zephyr.data.implementations.akshare_provider（_limit_pct_of 幅度口径复用）
# [CONSUMERS] zephyr.data.implementations.miniqmt_provider（market_breadth_snapshot capability）; tests/zephyr/data/test_market_breadth_snapshot.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 聚合纯函数无 I/O 无副作用（同输入同输出）；涨跌停幅度口径与 akshare_provider._limit_pct_of（stk_limit 日频表）同源复用不另造；价格比较一律 Decimal 量化到分（ROUND_HALF_UP，交易所口径）；无效 tick（缺昨收/最新价≤0）跳过不计入 total_count；ST 集加载失败→degraded=1 降级不炸（主板 ST 按 10% 近似，涨停计数偏紧留痕）
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/92_phase2_business_construction_order.md §8.2
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空/全非法 tick 输入→全零 BreadthAggregate+n_skipped 留痕不炸；ST 集加载异常→空集+log（fail-open）；query_fn 异常同上
# [TESTS] tests/zephyr/data/test_market_breadth_snapshot.py
# [A_module] module_id=MOD-DATA-062 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



MOD-DATA-062 — 全市场分钟级宽度快照采集纯函数（92号清单 §8.2，44号备忘 §2 M1-④ 行 + §6 数据源表）。

取数通道实证（2026-08-22 代码实证，真源=miniqmt_provider 既有实现）：
    miniqmt 实时全市场快照通道 = xtdata.get_stock_list_in_sector("沪深A股") 取全市场
    标的（auction_book/kline 族同款，~5400 只）+ xtdata.get_full_tick 分批（200 只/批，
    _fetch_auction_book 既有实证模式）取实时快照 dict——tick 字段含
    lastPrice/lastClose/high/amount/askPrice/askVol（_parse_auction_book_tick 实证键名）。
    涨跌停计数**不走 miniqmt 板块统计接口**（无该口径实证），由全市场最新价×昨收×
    板块差异化涨跌停价推导（44号 §9.1 输入 s_t=(adv,dec,lu,attempted)+total 的直接供给）。

计数口径（写清）：
    - advancing/declining/flat：最新价 vs 昨收（float 同源小数直接比较）。
    - 涨跌停价=昨收×(1±幅度) 四舍五入到分（Decimal ROUND_HALF_UP，交易所口径）；
      幅度=主板 10%（ST/*ST 5%）/创业板/科创板 20%/北交所 30%——复用
      AkshareIngestProvider._limit_pct_of（stk_limit DS-082 同口径，单一真源不另造）。
    - limit_up=最新价达涨停价；attempted=日内最高曾触及涨停价（含炸板）；
      sealed=涨停且卖一无量（ask1 价≤0 或量=0，封单形态）；limit_down 对称。
    - 新股无涨跌幅限制期/未知板块：_limit_pct_of 返回 None → 只计涨跌家数不计涨跌停
      （近似口径，留痕待首交易日实盘标定）。
    - total_amount=个股 tick amount（当日累计成交额，元）求全市场求和。
    - 停牌/无昨收/最新价≤0 tick 跳过不计入 total_count。

fail-open 纪律：
    本模块所有 I/O 边界（ST 集加载）异常→空集+log.warning，不抛——单次失败留痕
    不炸调度（调度器FetchResult error 通道在 miniqmt_provider 侧兜底）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ticks 参数
#   fields: 参数 ticks，类型注解 Mapping[str, Mapping[str, Any]]
#   code: market_breadth_collector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: st_codes 参数
#   fields: 参数 st_codes，类型注解 frozenset[str] | set[str] | None
#   code: market_breadth_collector.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: trade_date 参数
#   fields: 参数 trade_date（无注解）
#   code: market_breadth_collector.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: agg 参数
#   fields: 参数 agg，类型注解 BreadthAggregate
#   code: market_breadth_collector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① aggregate_market_ticks
#   name_en: aggregate_market_ticks
#   intro: 全市场 tick 字典 → 单分钟宽度聚合（纯函数，无 I/O）。
#   desc: 全市场 tick 字典 → 单分钟宽度聚合（纯函数，无 I/O）。 Args: ticks: xtdata.get_full_tick 返回的 {stock_code: tick…；源码 L208-L290
#   inputs: ticks st_codes trade_date
#   outputs: BreadthAggregate
# - id: A2
#   name_zh: ② build_insert_row
#   name_en: build_insert_row
#   intro: 聚合结果 → market_breadth_snapshot INSERT 行（列序=schemas INSERT_C…
#   desc: 聚合结果 → market_breadth_snapshot INSERT 行（列序=schemas INSERT_COLUMNS 真源）。 Args: agg: aggrega…；源码 L293-L327
#   inputs: agg trade_date ts data_source degraded
#   outputs: tuple
# - id: A3
#   name_zh: ③ load_current_st_codes
#   name_en: load_current_st_codes
#   intro: 加载当前有效 ST/*ST 裸码集合（fail-open：异常→(空集, False)+log，由调用方置 degra…
#   desc: 加载当前有效 ST/*ST 裸码集合（fail-open：异常→(空集, False)+log，由调用方置 degraded=1）。 Args: query_fn: CH 查询函…；源码 L330-L364
#   inputs: query_fn as_of
#   outputs: tuple[set[str], bool]
#   （注：A3 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: BreadthAggregate
#   name_en: BreadthAggregate
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.data.implementations.miniqmt_provider（market_breadth_snapshot capability…
# - id: O2
#   name_zh: tuple
#   name_en: tuple
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.data.implementations.miniqmt_provider（market_breadth_snapshot capability…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Callable, Final, Mapping

from zephyr.data.table_registry import get_registry as _get_table_registry

log = logging.getLogger(__name__)

__all__: Final = [
    "INSERT_COLUMN_NAMES",
    "BreadthAggregate",
    "aggregate_market_ticks",
    "build_insert_row",
    "load_current_st_codes",
]

# 表名真源：business_data_categories.yaml via table_registry（裁定 #ARCH-CH-024 同族模式）
_TBL_ST_STOCK_LIST: Final = _get_table_registry().table("market_st_stock_list")

# SQL 集中化（NO-BARE-SQL gate 豁免 SQL_ 前缀；f-string 仅表名真源插值，日期参数化占位）
# 当前有效 ST 集=最近可得（≤查询日）全量快照口径（PIT 严格，对齐 akshare_provider._st_flag_at 语义）
SQL_CURRENT_ST_CODES: Final = (
    f"SELECT symbol FROM {_TBL_ST_STOCK_LIST} "
    f"WHERE trade_date = (SELECT max(trade_date) FROM {_TBL_ST_STOCK_LIST} WHERE trade_date <= '{{as_of}}')"
)

_PRICE_TICK: Final = Decimal("0.01")

# INSERT 列名清单（与 schemas/categories/market_breadth_snapshot.py INSERT_COLUMNS 列序一一对应；
# 本模块为采集侧列序真源——schemas 目录不在 provider 运行 sys.path 时不可导入，
# 列序漂移由 tests/zephyr/data/test_market_breadth_snapshot.py 对账断言兜底）
INSERT_COLUMN_NAMES: Final = [
    "trade_date",
    "ts",
    "advancing",
    "declining",
    "flat",
    "limit_up",
    "limit_down",
    "sealed",
    "attempted",
    "total_count",
    "total_amount",
    "data_source",
    "degraded",
]


@dataclass(frozen=True, slots=True)
class BreadthAggregate:
    """全市场单分钟宽度聚合结果（一行 market_breadth_snapshot 的业务字段）。"""

    advancing: int = 0  # 上涨家数（最新价>昨收）
    declining: int = 0  # 下跌家数（最新价<昨收）
    flat: int = 0  # 平盘家数
    limit_up: int = 0  # 涨停家数（最新价达涨停价）
    limit_down: int = 0  # 跌停家数
    sealed: int = 0  # 封住涨停家数（涨停且卖一无量）
    attempted: int = 0  # 曾涨停家数（日内最高触及涨停价，含炸板）
    total_count: int = 0  # 参与统计标的数（有效 tick）
    total_amount: float = 0.0  # 全市场累计成交额（元）
    n_skipped: int = 0  # 无效 tick 跳过数（缺昨收/最新价≤0）


def _to_float(v: object) -> float | None:
    """安全转 float（None/非法/NaN → None）。"""
    if v is None:
        return None
    try:
        f = float(v)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return None
    return f if f == f else None  # NaN 剔除


def _round_price(v: float) -> Decimal:
    """价格量化到分（Decimal ROUND_HALF_UP，交易所四舍五入口径）。"""
    return Decimal(str(v)).quantize(_PRICE_TICK, rounding=ROUND_HALF_UP)


def _limit_pct_of(code: str, trade_date: date, st_flag: bool) -> float | None:
    """涨跌停幅度（小数）——转调 AkshareIngestProvider._limit_pct_of（stk_limit 同口径单一真源）。

    延迟导入避免与 implementations 包加载顺序耦合；导入失败（极端部署裁剪）
    → None 按未知板块处理（只计涨跌家数，不计涨跌停，留痕）。
    """
    try:
        from zephyr.data.implementations.akshare_provider import AkshareIngestProvider
    except ImportError:
        log.warning("akshare_provider 不可用，%s 涨跌停幅度未知跳过", code)
        return None
    return AkshareIngestProvider._limit_pct_of(code, trade_date, st_flag)


def aggregate_market_ticks(
    ticks: Mapping[str, Mapping[str, Any]],
    st_codes: frozenset[str] | set[str] | None = None,
    *,
    trade_date: date | None = None,
) -> BreadthAggregate:
    """全市场 tick 字典 → 单分钟宽度聚合（纯函数，无 I/O）。

    Args:
        ticks: xtdata.get_full_tick 返回的 {stock_code: tick_dict}（stock_code 带
            交易所后缀如 "600000.SH"；tick 键名实证=lastPrice/lastClose/high/amount/
            askPrice/askVol）。
        st_codes: 当前 ST/*ST 裸码集合（None/空=全部按非 ST 幅度——调用方加载失败
            降级路径，此时调用方须置 degraded=1 留痕）。
        trade_date: 交易日（幅度口径的日期参数；None=今日）。

    Returns:
        BreadthAggregate；空/全非法输入 → 全零 + n_skipped 留痕（不炸）。
    """
    st_set = st_codes or frozenset()
    td = trade_date or date.today()

    advancing = declining = flat = 0
    limit_up = limit_down = sealed = attempted = 0
    total_count = n_skipped = 0
    total_amount = 0.0

    for stock_code, tick in ticks.items():
        if not isinstance(tick, Mapping):
            n_skipped += 1
            continue
        last = _to_float(tick.get("lastPrice"))
        pre_close = _to_float(tick.get("lastClose"))
        if last is None or last <= 0 or pre_close is None or pre_close <= 0:
            n_skipped += 1
            continue
        total_count += 1
        total_amount += _to_float(tick.get("amount")) or 0.0

        if last > pre_close:
            advancing += 1
        elif last < pre_close:
            declining += 1
        else:
            flat += 1

        bare = str(stock_code).split(".")[0]
        pct = _limit_pct_of(bare, td, bare in st_set)
        if pct is None:
            continue  # 未知板块/无限制期：只计涨跌家数（口径留痕见模块 docstring）

        up_price = _round_price(pre_close * (1.0 + pct))
        down_price = _round_price(pre_close * (1.0 - pct))
        last_q = _round_price(last)
        high = _to_float(tick.get("high"))
        high_q = _round_price(high) if high is not None and high > 0 else last_q

        if high_q >= up_price:
            attempted += 1
        if last_q >= up_price:
            limit_up += 1
            # 封住涨停=涨停且卖一无量（ask1 价≤0 或量=0，封单形态）
            ask_prices = tick.get("askPrice") or []
            ask_vols = tick.get("askVol") or []
            ask1_price = _to_float(ask_prices[0]) if len(ask_prices) > 0 else None
            ask1_vol = _to_float(ask_vols[0]) if len(ask_vols) > 0 else None
            if (ask1_price is None or ask1_price <= 0) or (ask1_vol is None or ask1_vol == 0):
                sealed += 1
        elif last_q <= down_price:
            limit_down += 1

    return BreadthAggregate(
        advancing=advancing,
        declining=declining,
        flat=flat,
        limit_up=limit_up,
        limit_down=limit_down,
        sealed=sealed,
        attempted=attempted,
        total_count=total_count,
        total_amount=round(total_amount, 2),
        n_skipped=n_skipped,
    )


def build_insert_row(
    agg: BreadthAggregate,
    trade_date: str,
    ts: str,
    *,
    data_source: str = "miniqmt",
    degraded: int = 0,
) -> tuple:
    """聚合结果 → market_breadth_snapshot INSERT 行（列序=schemas INSERT_COLUMNS 真源）。

    Args:
        agg: aggregate_market_ticks 输出。
        trade_date: 交易日 "YYYY-MM-DD"。
        ts: 快照时间戳 "YYYY-MM-DD HH:MM:SS"（分钟截断，Asia/Shanghai 口径）。
        data_source: 数据来源标记。
        degraded: 降级标记（0=正常，1=ST 集缺失按非 ST 幅度近似）。

    Returns:
        tuple，列序对齐 schemas/categories/market_breadth_snapshot.py INSERT_COLUMNS。
    """
    return (
        trade_date,
        ts,
        agg.advancing,
        agg.declining,
        agg.flat,
        agg.limit_up,
        agg.limit_down,
        agg.sealed,
        agg.attempted,
        agg.total_count,
        agg.total_amount,
        data_source,
        degraded,
    )


def load_current_st_codes(
    query_fn: Callable[[str], str] | None = None,
    as_of: date | None = None,
) -> tuple[set[str], bool]:
    """加载当前有效 ST/*ST 裸码集合（fail-open：异常→(空集, False)+log，由调用方置 degraded=1）。

    Args:
        query_fn: CH 查询函数（TSV 字符串返回）；None 时延迟取 ch_reader.query。
        as_of: 查询日（None=今日；PIT 严格=最近可得 ≤as_of 快照）。

    Returns:
        (ST 裸码集合, loaded_ok)——loaded_ok=False 表示加载失败降级（空集可能是
        真空也可能是失败，调用方据此置 degraded=1 留痕）。
    """
    fn = query_fn
    if fn is None:
        try:
            from zephyr.data import ch_reader

            fn = ch_reader.query
        except Exception:  # noqa: BLE001 — 数据层异常一律降级不炸
            log.warning("ch_reader 不可用，ST 集按空集降级")
            return set(), False
    d = (as_of or date.today()).isoformat()
    try:
        tsv = fn(SQL_CURRENT_ST_CODES.format(as_of=d))
    except Exception:  # noqa: BLE001 — fail-open
        log.warning("st_stock_list 当前快照加载失败，ST 集按空集降级", exc_info=True)
        return set(), False
    codes: set[str] = set()
    for line in (tsv or "").strip().split("\n"):
        code = line.strip().split("\t")[0].split(".")[0]
        if code:
            codes.add(code)
    return codes, True
