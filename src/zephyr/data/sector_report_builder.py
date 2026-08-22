# [BLUEPRINT] MOD-L00-009 | 待统筹登记（blueprint 未建，真源=92号清单 §7.5 + 架构审查报告 §11.5 SEC-01/§11.2 需求对账 + 22号板块轮动 spec）
# [MODULE] zephyr.data.sector_report_builder
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.sector_ranking_engine; zephyr.signal_ashare.sector_breadth; zephyr.signal_ashare.sector_siphon; zephyr.signal_ashare.sector_momentum; zephyr.signal_ashare.sector_analyzer; zephyr.signal_ashare.mainline_candidates; c1_market.kline_sector_880（只读）; c1_market.sector_constituent（只读）; c1_market.kline_daily（只读）; c1_market.money_flow（只读）; c1_market.limit_up_down（只读）; c1_market.stk_limit（只读）; c1_market.sector_snapshot（只读）; c1_market.sector_meta（只读）
# [CONSUMERS] （MVP 阶段无——候选消费方：IDX-02 Dashboard 板块页 D-02/D-03/D-06、Owner 盘后复盘、.runtime/reports 落盘文件直读）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 观测层只读：不接交易链路（B-007）；单维度缺数据该维度标 availability=unavailable 不炸整体；PIT（全部数据 ≤ trade_date，成分股 SCD-2 时点过滤）；净流入单位=亿元（money_flow 万元实证口径÷1e4）；涨停梯队双源并集（limit_up_down ∪ stk_limit 触价收封）；frozen dataclass asdict JSON 可序列化；报告落盘 .runtime/reports/（运行时产物不入 git）
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/92_phase2_business_construction_order.md §7.5
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询异常/客户端不可用→对应维度降级 notes 留痕不抛；板块全集为空/当日无收益截面→degraded=True；trade_date 格式非法→ValueError（调用方契约违例，fail-closed）；快照最新日期≠报告日→ranking 维度 unavailable
# [TESTS] tests/zephyr/data/test_sector_report_builder.py
# [A_module] module_id=MOD-L00-009 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""
MOD-L00-009 — 板块盘后全景报告器（92号清单 §7.5，架构审查报告 §11.5 SEC-01 P1 观测层）。

编排已落码库模块（均 import 消费不重复造）→ 日频 sector_report：
  ① Top10 板块榜（当日涨幅降序）——涨幅 + 主力五层资金流（money_flow ×
     sector_constituent 聚合，元→亿）+ momentum（sector_momentum.multi_tf_momentum
     0.4×q20+0.3×q5+0.3×q3）+ ranking_score（sector_ranking_engine.compute_ranking
     5 因子，快照日期须=报告日）+ 涨停比（sector_breadth.sector_limit_up_ratio）+
     结构强度（sector_analyzer.SectorAnalyzer.evaluate_strength）；
  ② 5 状态标签（sector_rotation_state 输出，经 mainline_candidates 透传：
     rotation_state/watch_score/lead_streak）；
  ③ 涨停梯队（stk_limit/limit_up_down 聚合：连板高度 + 一板/二板/三板+ 分档 ×
     sector_constituent 归属）；
  ④ 主线候选（调 SEC-05 mainline_candidates.compute_mainline_candidates）；
  ⑤ 虹吸态（sector_siphon.detect_siphon_state，money_flow×成分聚合净流入 +
     板块成交额 HHI 三信号 z-score）。

【数据实证口径（2026-08-22 直查 c1_market，可信）】
- kline_sector_880（period='1d'）469 板块=市场统计指数 11（880001-880011，剔除出
  板块全集）+地区 32+概念风格 426，sector_name 列全空；无纯行业板；
- 板块名称真源 = sector_meta（881xxx 同花顺行业真名，sector_code 为无后缀裸码需归一
  +.SH；SCD 版本取 argMax(trade_date) 最新）；sector_constituent.sector_name 对
  880/881 族大面积为代码回显，回显名过滤；880xxx 概念板全库无中文名 → 代码直出
  （采集层缺口，非本模块职责）；
- 纯行业板为 881xxx 族但无板块 K 线 → 行业日收益/成交额经 sector_constituent
  成分股等权/合计聚合（kline_daily.pct_change/amount）合成，与 880xxx 同管线下游；
  880xxx 成分在册但 K 线缺失不合成（官方指数缺口，防代理冒充，notes 留痕）；
- money_flow 五层净流入实测为**万元口径**（#256② 已修正：schema COMMENT 与 CH 列注释
  已于 2026-08-22 由"元"勘正为"万元"——实证：08-20 全市场主力净流入合计 −128,226
  =−12.8 亿量级合理，元口径仅 −12.8 万荒谬；601899 单日 217,595.29→21.76 亿；
  全库单一 tushare 源无混杂），本模块按 万元→亿（÷1e4）换算，配置 yi_unit 可调；
- limit_up_down 采集仅 涨停/跌停 两类（无炸板池）；stk_limit 为规则计算涨跌停价
  （PIT strict），触价收封（close ≥ limit_up − 0.005 网格容差）作涨停并集腿。

输出：结构化 dict（report_to_dict）+ 落报告文件（.runtime/reports/
sector_report_YYYYMMDD.json，运行时产物不入 git）+ CLI 摘要。

启动:
    python -m zephyr.data.sector_report_builder                      # 最新数据日
    python -m zephyr.data.sector_report_builder --date 2026-08-20    # 指定交易日
    python -m zephyr.data.sector_report_builder --no-write           # 只打印不落盘

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 板块日 K 窗（kline_sector_880）+ 个股日 K 窗（kline_daily）+ 成分映射（sector_constituent SCD-2）
# - id: I2
#   name: 个股资金流（money_flow 当日五层 + 窗口主力）+ 涨跌停（limit_up_down 窗 + stk_limit 当日）+ 板块快照（sector_snapshot 最新截面）
# 层: 算法
# - id: A1
#   name_zh: 统一板块日序列（880 直取 / 881 成分等权合成）
# - id: A2
#   name_zh: Top10 榜聚合
#   desc: 当日涨幅降序 Top10 + 五层资金流(元→亿) + momentum/ranking/涨停比/结构强度附挂
# - id: A3
#   name_zh: 涨停梯队
#   desc: 涨停双源并集 → 连板高度 trailing 连续 → 一板/二板/三板+ 分档 × 成分归属
# - id: A4
#   name_zh: 虹吸态
#   desc: SectorFlowSnapshot(板块成交额/净流入) + 历史三信号 → detect_siphon_state
# - id: A5
#   name_zh: 主线候选与 5 状态
#   desc: compute_mainline_candidates（SEC-05）嵌入，rotation_state/watch_score 透传
# 层: 输出
# - id: O1
#   name_zh: SectorReport
#   intro: date/rotation_state/top_sectors/limit_ladder/siphon/mainline/availability/degraded/notes + report_to_dict + write_report(.runtime/reports)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1,I2 --> A2
# I1,I2 --> A3
# I1,I2 --> A4
# I1 --> A5
# A2,A3,A4,A5 --> O1
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Final

from zephyr.data.sector_ranking_engine import compute_ranking
from zephyr.signal_ashare.mainline_candidates import (
    MainlineCandidatesResult,
    compute_mainline_candidates,
)
from zephyr.signal_ashare.sector_analyzer import SectorAnalyzer, SectorData
from zephyr.signal_ashare.sector_breadth import (
    classify_limit_up_breadth,
    sector_limit_up_ratio,
)
from zephyr.signal_ashare.sector_momentum import multi_tf_momentum
from zephyr.signal_ashare.sector_siphon import SectorFlowSnapshot, detect_siphon_state

log = logging.getLogger(__name__)

__all__: Final = [
    "LimitLadderSector",
    "LimitLadderSummary",
    "SectorReport",
    "SectorReportConfig",
    "SectorTopEntry",
    "build_sector_report",
    "main",
    "report_to_dict",
    "write_report",
]

#: 市场统计指数代码（剔除出板块全集；880001 作市场收益基准代理）
_MARKET_INDEX_CODES: Final = frozenset(f"880{i:03d}.SH" for i in range(1, 12))

#: 报告默认落盘目录（仓根 .runtime/reports，gitignored 运行时产物）
_DEFAULT_REPORT_DIR: Final = Path(__file__).resolve().parents[3] / ".runtime" / "reports"

#: availability 维度键（单维度缺数据标 unavailable 不炸整体）
_DIMENSIONS: Final = (
    "top_ladder",
    "money_flow",
    "rotation_state",
    "limit_ladder",
    "siphon",
    "mainline",
    "ranking",
    "momentum",
)

# SQL 集中化（§5.160.2）：模块级 SQL_* 常量，参数化查询禁 f-string 插值
SQL_LATEST_SECTOR_DATE: Final = """
SELECT max(trade_date)
FROM c1_market.kline_sector_880
WHERE period = '1d'
"""

SQL_SECTOR_KLINE_WINDOW: Final = """
SELECT sector_code, trade_date, close, amount
FROM c1_market.kline_sector_880
WHERE period = '1d' AND trade_date <= %(trade_date)s AND trade_date >= %(start_date)s
"""

SQL_SECTOR_CONSTITUENTS: Final = """
SELECT sector_code, sector_name, stock_code
FROM c1_market.sector_constituent
WHERE valid_from <= %(trade_date)s AND (valid_to IS NULL OR valid_to > %(trade_date)s)
"""

SQL_SECTOR_META_NAMES: Final = """
SELECT sector_code, argMax(sector_name, trade_date)
FROM c1_market.sector_meta
WHERE sector_name != ''
GROUP BY sector_code
"""

SQL_STOCK_KLINE_WINDOW: Final = """
SELECT symbol_canonical, trade_date, close, amount, pct_change
FROM c1_market.kline_daily
WHERE market_type = 'A_share' AND quality_flag = 1
  AND trade_date <= %(trade_date)s AND trade_date >= %(start_date)s
"""

SQL_MONEY_FLOW_TODAY: Final = """
SELECT symbol_canonical, main_net_inflow, super_large_net_inflow,
       large_net_inflow, medium_net_inflow, small_net_inflow
FROM c1_market.money_flow
WHERE trade_date = %(trade_date)s
"""

SQL_MONEY_FLOW_WINDOW: Final = """
SELECT trade_date, symbol_canonical, main_net_inflow
FROM c1_market.money_flow
WHERE trade_date <= %(trade_date)s AND trade_date >= %(start_date)s
"""

SQL_LIMIT_UP_DOWN_WINDOW: Final = """
SELECT symbol_canonical, trade_date, limit_type
FROM c1_market.limit_up_down
WHERE trade_date <= %(trade_date)s AND trade_date >= %(start_date)s
"""

SQL_STK_LIMIT_TODAY: Final = """
SELECT symbol_canonical, limit_up
FROM c1_market.stk_limit
WHERE trade_date = %(trade_date)s
"""

SQL_LATEST_SNAPSHOT: Final = """
SELECT sector_code, now_price, last_close, before_5min_now, amount, outside, inside,
       toDate(timestamp)
FROM c1_market.sector_snapshot
WHERE timestamp = (SELECT max(timestamp) FROM c1_market.sector_snapshot)
"""


@dataclass(frozen=True, slots=True)
class SectorReportConfig:
    """报告器配置——默认值取自 22号 spec + 2026-08-22 数据实证。"""

    sector_lookback_calendar_days: int = 400  # 板块 K 线查询自然日窗（momentum 需 ≥21 交易日）
    stock_lookback_calendar_days: int = 120  # 个股 K 线查询自然日窗（881xxx 合成腿）
    siphon_lookback_calendar_days: int = 120  # 虹吸历史序列查询自然日窗（z-score 滚动参照）
    ladder_lookback_calendar_days: int = 20  # 涨停梯队窗（连板高度 trailing，覆盖 ~14 交易日）
    market_index_code: str = "880001.SH"  # 市场收益基准代理（总市值指数）
    top_n: int = 10  # Top 板块榜条数
    hhi_top_n: int = 5  # 虹吸头部 N 板块（与 22号 §3.1⑤⑨ 协同）
    siphon_z_threshold: float = 1.5  # 虹吸态 z 阈值（22号 §3.1⑤）
    limit_price_tol: float = 0.005  # 触板收封价格网格容差（0.01 取整半格）
    yi_unit: float = 1e4  # money_flow 净流入单位 → 亿元换算因子（2026-08-22 实证：万元口径，万元→亿 ÷1e4）


@dataclass(frozen=True, slots=True)
class SectorTopEntry:
    """Top10 板块榜条目（涨幅 + 五层资金流 + 梯队 + 强度/动量/排名附挂）。"""

    rank: int
    sector_code: str
    sector_name: str  # sector_constituent.sector_name 映射，缺失回退代码
    change_pct: float | None  # 当日涨幅（小数，如 0.03=3%）
    amount: float | None  # 成交额（元；881xxx=成分合计）
    main_net_inflow: float | None  # 主力净流入（亿元）；无成分覆盖 → None（缺数据非零）
    super_large_net_inflow: float | None
    large_net_inflow: float | None
    medium_net_inflow: float | None
    small_net_inflow: float | None
    constituent_count: int = 0
    limit_up_count: int | None = None  # 当日涨停家数（梯队维度）
    limit_up_ratio: float | None = None  # 涨停比 = 涨停数/成分股数（sector_breadth）
    breadth_label: str | None = None  # 情绪宽度分档（极强/强/中/弱）
    strength_status: str | None = None  # 结构强度档（sector_analyzer.evaluate_strength）
    strength_score: float | None = None  # 结构强度分 0-100
    momentum_score: float | None = None  # 多 TF 动量 ∈ [0,1]（sector_momentum）
    ranking_score: float | None = None  # 5 因子复合排名分（sector_ranking_engine，快照覆盖时）


@dataclass(frozen=True, slots=True)
class LimitLadderSector:
    """板块涨停梯队明细。"""

    sector_code: str
    sector_name: str
    limit_up_count: int  # 当日涨停家数（双源并集）
    tier1: int  # 一板（首板）
    tier2: int  # 二板
    tier3_plus: int  # 三板及以上
    max_streak: int  # 板块内最高连板
    limit_up_ratio: float | None  # 涨停比（成分股数分母；无成分 → None）


@dataclass(frozen=True, slots=True)
class LimitLadderSummary:
    """涨停梯队市场级摘要 + 板块明细（count>0 降序 Top-N）。"""

    total_limit_up: int
    tier1: int
    tier2: int
    tier3_plus: int
    max_streak: int
    sectors: list[LimitLadderSector] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class SectorReport:
    """板块盘后全景报告输出契约（T 日盘后计算，观测层只读，不接交易）。"""

    date: str  # 数据日 YYYY-MM-DD
    generated_at: str  # 生成时间 ISO（UTC）
    rotation_state: str | None = None  # 板块轮动 5 状态（sector_rotation_state 经 SEC-05 透传）
    watch_score: float | None = None  # 22号 watch_score 透传
    lead_streak: int | None = None  # 当前领涨板块连续领涨天数
    top_sectors: list[SectorTopEntry] = field(default_factory=list)
    limit_ladder: LimitLadderSummary | None = None  # 涨停梯队；双源查询均异常 → None
    siphon_flag: bool = False  # 虹吸态（z > 1.5σ）
    siphon_score: float | None = None
    siphon_sectors: list[str] = field(default_factory=list)  # 虹吸头部板块名单
    mainline: MainlineCandidatesResult | None = None  # 主线候选榜（SEC-05 嵌入）
    availability: dict[str, str] = field(default_factory=dict)  # 维度 → ok/unavailable
    degraded: bool = False  # 板块全集/当日截面不可用时 True，结果为空壳
    notes: list[str] = field(default_factory=list)  # 降级原因等留痕


# ------------------------------------------------------------------
# 内部辅助（数据装配，纯函数）
# ------------------------------------------------------------------


def _normalize_date(trade_date: str | date | datetime) -> date:
    """归一化交易日（str 须 YYYY-MM-DD，非法格式抛 ValueError）。"""
    if isinstance(trade_date, datetime):
        return trade_date.date()
    if isinstance(trade_date, date):
        return trade_date
    return datetime.strptime(str(trade_date), "%Y-%m-%d").date()


def _default_client():
    """延迟加载默认 CH 客户端（不可用时返回 None，由主入口转 degraded）。"""
    try:
        from zephyr.data.ch_writer import get_client

        return get_client()
    except Exception:  # noqa: BLE001 — 连接/依赖问题一律降级
        log.warning("ch_writer 默认客户端不可用，板块盘后报告降级", exc_info=True)
        return None


def _as_date(v: Any) -> date:
    """CH 日期行值归一（date 原样返回，str 按 YYYY-MM-DD 解析）。"""
    return v if isinstance(v, date) else _normalize_date(v)


def _degraded_report(date_str: str, note: str) -> SectorReport:
    log.warning("板块盘后全景报告降级: %s", note)
    return SectorReport(
        date=date_str,
        generated_at=datetime.now(UTC).isoformat(),
        availability={k: "unavailable" for k in _DIMENSIONS},
        degraded=True,
        notes=[note],
    )


def _sector_880_series(
    rows: list[tuple], d: date, market_index_code: str
) -> tuple[dict[str, list[tuple[date, float, float]]], list[tuple[date, float]]]:
    """880 板块 K 线行 → ({板块: [(日期, 收盘, 成交额)] 升序}, 基准 [(日期, 收盘)] 升序)。

    剔除市场统计指数（880001-880011）；PIT 防御：> d 的行丢弃（SQL 已 ≤ d，双保险）。
    """
    by_sector: dict[str, list[tuple[date, float, float]]] = {}
    bench: list[tuple[date, float]] = []
    for row in rows:
        code = str(row[0])
        dd = _as_date(row[1])
        if dd > d:
            continue
        close = float(row[2] or 0.0)
        amount = float(row[3] or 0.0)
        if code == market_index_code:
            bench.append((dd, close))
            continue
        if code in _MARKET_INDEX_CODES:
            continue
        by_sector.setdefault(code, []).append((dd, close, amount))
    for series in by_sector.values():
        series.sort(key=lambda x: x[0])
    bench.sort(key=lambda x: x[0])
    return by_sector, bench


def _synthesize_industry_series(
    codes: list[str],
    constituents: dict[str, list[str]],
    stock_rows: list[tuple],
    d: date,
) -> dict[str, list[tuple[date, float, float]]]:
    """881xxx 行业板合成日序列：成分股 pct_change 等权均值 → cumprod 价格指数。

    成交额 = 成分股 amount 合计；无成分 K 线覆盖的板块跳过。
    """
    by_stock: dict[str, dict[date, tuple[float, float, float]]] = {}
    for row in stock_rows:
        dd = _as_date(row[1])
        if dd > d:
            continue
        by_stock.setdefault(str(row[0]), {})[dd] = (
            float(row[4] or 0.0),
            float(row[3] or 0.0),
            float(row[2] or 0.0),
        )
    out: dict[str, list[tuple[date, float, float]]] = {}
    for code in codes:
        stocks = [s for s in constituents.get(code, []) if s in by_stock]
        if not stocks:
            continue
        days = sorted({dd for s in stocks for dd in by_stock[s]})
        series: list[tuple[date, float, float]] = []
        price = 1.0
        for dd in days:
            legs = [by_stock[s][dd] for s in stocks if dd in by_stock[s]]
            if not legs:
                continue
            price *= 1.0 + sum(p for p, _, _ in legs) / len(legs) / 100.0
            series.append((dd, price, sum(a for _, a, _ in legs)))
        if series:
            out[code] = series
    return out


def _daily_returns(series: list[tuple[date, float, float]]) -> dict[date, float]:
    """(日期, 收盘, 成交额) 序列 → {日期: 日收益}（相邻收盘比，基准 ≤0 跳过）。"""
    out: dict[date, float] = {}
    for i in range(1, len(series)):
        prev_close = series[i - 1][1]
        if prev_close > 0:
            out[series[i][0]] = series[i][1] / prev_close - 1.0
    return out


def _trailing_up_days(rets: dict[date, float], sorted_dates: list[date], d: date) -> int:
    """连续上涨天数（截至 d  trailing 收益 >0 日数）。"""
    n = 0
    for dd in reversed(sorted_dates):
        if dd > d:
            continue
        if rets.get(dd, 0.0) > 0:
            n += 1
        else:
            break
    return n


# ------------------------------------------------------------------
# 维度聚合器
# ------------------------------------------------------------------


def _aggregate_money_flow(
    mf_rows: list[tuple],
) -> dict[str, tuple[float, float, float, float, float]]:
    """money_flow 当日行 → {个股: (主力/超大单/大单/中单/小单 净流入，元)}。"""
    out: dict[str, tuple[float, float, float, float, float]] = {}
    for row in mf_rows:
        out[str(row[0])] = tuple(float(row[i] or 0.0) for i in range(1, 6))  # type: ignore[assignment]
    return out


def _sector_flow_yi(
    code: str,
    flow_map: dict[str, tuple[float, float, float, float, float]],
    constituents: dict[str, list[str]],
    yi_unit: float,
) -> tuple[float | None, ...]:
    """板块五层净流入 = 成分股求和（元→亿）；无成分覆盖 → 全 None（缺数据非零）。"""
    legs = [flow_map[s] for s in constituents.get(code, []) if s in flow_map]
    if not legs:
        return (None,) * 5
    return tuple(round(sum(leg[i] for leg in legs) / yi_unit, 4) for i in range(5))


def _build_limit_ladder(
    limit_rows: list[tuple],
    stk_limit_rows: list[tuple],
    close_today: dict[str, float],
    calendar: list[date],
    constituents: dict[str, list[str]],
    names: dict[str, str],
    d: date,
    cfg: SectorReportConfig,
) -> LimitLadderSummary:
    """涨停梯队：limit_up_down（涨停类）∪ stk_limit 触价收封 → 连板高度 → 分档 × 成分归属。

    连板高度 = 截至 d 在交易日历上 trailing 连续涨停日数（日历=个股 K 线窗 ∪ 涨停窗日期）。
    """
    limit_days_by_symbol: dict[str, set[date]] = {}
    for row in limit_rows:
        if str(row[2]) != "涨停":
            continue
        dd = _as_date(row[1])
        if dd > d:
            continue
        limit_days_by_symbol.setdefault(str(row[0]), set()).add(dd)

    # stk_limit 并集腿：当日触价收封（close ≥ limit_up − 容差）
    union_today = 0
    for row in stk_limit_rows:
        sym = str(row[0])
        limit_up = float(row[1]) if row[1] is not None else None
        if limit_up is None or limit_up <= 0:
            continue
        close = close_today.get(sym)
        if close is not None and close >= limit_up - cfg.limit_price_tol:
            if d not in limit_days_by_symbol.get(sym, set()):
                limit_days_by_symbol.setdefault(sym, set()).add(d)
                union_today += 1
    if union_today:
        log.info("stk_limit 并集腿补入涨停 %d 只（limit_up_down 未覆盖）", union_today)

    today_set = {sym for sym, days in limit_days_by_symbol.items() if d in days}

    def _streak(sym: str) -> int:
        days = limit_days_by_symbol[sym]
        n = 0
        for dd in reversed(calendar):
            if dd > d:
                continue
            if dd in days:
                n += 1
            else:
                break
        return n

    streaks = {sym: _streak(sym) for sym in today_set}

    def _tier(streak: int) -> int:
        return 1 if streak <= 1 else (2 if streak == 2 else 3)

    tier_counts = {1: 0, 2: 0, 3: 0}
    for sym in today_set:
        tier_counts[_tier(streaks[sym])] += 1
    max_streak = max(streaks.values(), default=0)

    sector_ladders: list[LimitLadderSector] = []
    for code, stocks in constituents.items():
        hit = [s for s in stocks if s in today_set]
        if not hit:
            continue
        tiers = {1: 0, 2: 0, 3: 0}
        for s in hit:
            tiers[_tier(streaks[s])] += 1
        sector_ladders.append(
            LimitLadderSector(
                sector_code=code,
                sector_name=names.get(code, code),
                limit_up_count=len(hit),
                tier1=tiers[1],
                tier2=tiers[2],
                tier3_plus=tiers[3],
                max_streak=max(streaks[s] for s in hit),
                limit_up_ratio=sector_limit_up_ratio(len(hit), len(stocks)) if stocks else None,
            )
        )
    sector_ladders.sort(key=lambda s: (-s.limit_up_count, -s.max_streak, s.sector_code))
    return LimitLadderSummary(
        total_limit_up=len(today_set),
        tier1=tier_counts[1],
        tier2=tier_counts[2],
        tier3_plus=tier_counts[3],
        max_streak=max_streak,
        sectors=sector_ladders,
    )


def _compute_siphon(
    by_sector: dict[str, list[tuple[date, float, float]]],
    constituents: dict[str, list[str]],
    mf_rows: list[tuple],
    d: date,
    cfg: SectorReportConfig,
) -> tuple[Any | None, list[str]]:
    """虹吸态识别——money_flow×sector_constituent 聚合板块净流入，detect_siphon_state 复用。

    Returns:
        (SiphonResult | None, notes)；数据缺口 → (None, 降级说明)。
    """
    notes: list[str] = []
    if not mf_rows:
        return None, ["money_flow 窗内无数据，虹吸态降级"]
    sector_codes = [c for c in by_sector if c in constituents]
    if not sector_codes:
        return None, ["板块序列与成分映射无交集，虹吸态降级"]

    flow_by_day: dict[tuple[date, str], float] = {}
    for row in mf_rows:
        flow_by_day[(_as_date(row[0]), str(row[1]))] = float(row[2] or 0.0)
    amounts = {c: {dd: a for dd, _, a in s} for c, s in by_sector.items()}

    def _day_snapshot(dd: date) -> list[SectorFlowSnapshot]:
        return [
            SectorFlowSnapshot(
                name=code,
                turnover=amounts[code].get(dd, 0.0),
                net_inflow=sum(flow_by_day.get((dd, s), 0.0) for s in constituents[code]),
            )
            for code in sector_codes
        ]

    def _signals(snaps: list[SectorFlowSnapshot]) -> tuple[float, float, float]:
        total_amt = sum(s.turnover for s in snaps)
        top = sorted(snaps, key=lambda s: s.turnover, reverse=True)[: cfg.hhi_top_n]
        hhi = sum((s.turnover / total_amt) ** 2 for s in top) if total_amt > 0 else 0.0
        total_abs = sum(abs(s.net_inflow) for s in snaps)
        conc = sum(s.net_inflow for s in top) / total_abs if total_abs > 0 else 0.0
        top_ids = {id(s) for s in top}
        rest = [s for s in snaps if id(s) not in top_ids]
        outflow = sum(1 for s in rest if s.net_inflow < 0) / len(rest) if rest else 0.0
        return hhi, conc, outflow

    today_snaps = _day_snapshot(d)
    if not any(s.turnover > 0 for s in today_snaps):
        return None, [f"{d.isoformat()} 板块成交额全 0，虹吸态降级"]

    hhi_hist: list[float] = []
    conc_hist: list[float] = []
    out_hist: list[float] = []
    for dd in sorted({day for day, _ in flow_by_day if day < d}):
        hhi, conc, outflow = _signals(_day_snapshot(dd))
        hhi_hist.append(hhi)
        conc_hist.append(conc)
        out_hist.append(outflow)
    if len(hhi_hist) < 2:
        notes.append(f"虹吸历史序列 {len(hhi_hist)} 日 < 2，z-score 降级不触发（rolling_zscore 守卫）")

    result = detect_siphon_state(
        today_snaps,
        hhi_hist,
        conc_hist,
        out_hist,
        n_top=cfg.hhi_top_n,
        threshold=cfg.siphon_z_threshold,
    )
    return result, notes


def _compute_ranking_scores(
    snapshot_rows: list[tuple], d: date
) -> tuple[dict[str, float] | None, str | None]:
    """5 因子复合排名（sector_ranking_engine.compute_ranking 复用）。

    快照最新日期须 = 报告日（历史回跑时快照维度降级）。
    Returns: ({板块: score} | None, 降级说明 | None)。
    """
    if not snapshot_rows:
        return None, "sector_snapshot 最新截面无数据，ranking 维度降级"
    snap_dates = {_as_date(row[7]) for row in snapshot_rows}
    if snap_dates != {d}:
        return None, (
            f"板块快照最新日期 {sorted(snap_dates)[-1].isoformat()} ≠ 报告日 {d.isoformat()}"
            "（历史回跑快照维度降级）"
        )
    ranking = compute_ranking([tuple(row[:7]) for row in snapshot_rows])
    return dict(ranking), None


# ------------------------------------------------------------------
# 主入口
# ------------------------------------------------------------------


def build_sector_report(
    trade_date: str | date | datetime | None = None,
    ch_client: Any | None = None,
    config: SectorReportConfig | None = None,
) -> SectorReport:
    """主入口：板块盘后全景报告（Top10 榜 + 资金流 + 5 状态 + 梯队 + 主线候选 + 虹吸）。

    Args:
        trade_date: 数据日；None 时取 kline_sector_880 最新数据日（PIT 数据日口径）。
        ch_client: clickhouse-driver 鸭子类型（execute(sql, params) -> list[tuple]）；
            None 时延迟取 ch_writer.get_client，不可得 → degraded。
        config: 报告配置（None 用默认）。

    Returns:
        SectorReport；板块全集为空/当日无收益截面 → degraded=True 空壳不炸；
        资金流/梯队/虹吸/ranking/momentum/主线各维度独立降级（availability + notes 留痕）。
    """
    cfg = config or SectorReportConfig()

    client = ch_client if ch_client is not None else _default_client()
    if client is None:
        d = _normalize_date(trade_date) if trade_date is not None else date.today()
        return _degraded_report(d.isoformat(), "ch_client 未注入且默认客户端不可用")

    if trade_date is None:
        try:
            latest = client.execute(SQL_LATEST_SECTOR_DATE, {})
        except Exception as e:  # noqa: BLE001 — 数据层异常一律降级不炸
            return _degraded_report("unknown", f"最新板块数据日查询异常: {e!r}")
        if not latest or latest[0][0] is None:
            return _degraded_report("unknown", "kline_sector_880 无任何日 K 数据")
        d = _as_date(latest[0][0])
    else:
        d = _normalize_date(trade_date)
    date_str = d.isoformat()

    notes: list[str] = []
    availability = {k: "ok" for k in _DIMENSIONS}

    # ── 板块 K 线窗（880xxx 直取 + 880001 基准） ──
    sector_start = d - timedelta(days=cfg.sector_lookback_calendar_days)
    try:
        sector_rows = client.execute(
            SQL_SECTOR_KLINE_WINDOW, {"trade_date": d, "start_date": sector_start}
        )
    except Exception as e:  # noqa: BLE001 — 880 腿缺失，宇宙收敛为 881 合成
        sector_rows = []
        notes.append(f"kline_sector_880 查询异常，880xxx 板块腿缺失: {e!r}")
    by_sector, _bench = _sector_880_series(sector_rows, d, cfg.market_index_code)
    if not by_sector:
        notes.append("kline_sector_880 窗内无数据，880xxx 板块腿缺失，宇宙收敛为 881xxx 行业合成")

    # ── 成分映射（资金流/梯队聚合归属 + 881xxx 合成候选；名称回显过滤） ──
    constituents: dict[str, list[str]] = {}
    names: dict[str, str] = {}
    try:
        for row in client.execute(SQL_SECTOR_CONSTITUENTS, {"trade_date": d}):
            code = str(row[0])
            constituents.setdefault(code, []).append(str(row[2]))
            name = str(row[1] or "").strip()
            if name and name != code:  # 成分表 sector_name 大面积为代码回显，过滤
                names.setdefault(code, name)
    except Exception as e:  # noqa: BLE001 — 成分缺失，资金流/梯队/合成维度降级
        notes.append(f"sector_constituent 查询异常，资金流/梯队/881xxx 合成维度降级: {e!r}")

    # ── 板块名称真源（sector_meta：881xxx 同花顺行业真名，覆盖成分表回显名） ──
    try:
        for row in client.execute(SQL_SECTOR_META_NAMES, {}):
            raw = str(row[0]).strip()
            name = str(row[1] or "").strip()
            if not raw or not name:
                continue
            key = raw if "." in raw else f"{raw}.SH"  # meta 裸码归一（881101 → 881101.SH）
            if name != key:
                names[key] = name
    except Exception as e:  # noqa: BLE001 — 元数据缺失，名称维度降级为代码直出
        notes.append(f"sector_meta 查询异常，板块名称维度降级（代码直出）: {e!r}")

    # ── 个股 K 线窗（881 合成 + 触价收封并集腿 + 梯队日历共用） ──
    stock_start = d - timedelta(days=cfg.stock_lookback_calendar_days)
    try:
        stock_rows = client.execute(
            SQL_STOCK_KLINE_WINDOW, {"trade_date": d, "start_date": stock_start}
        )
    except Exception as e:  # noqa: BLE001 — 个股 K 线缺失，881 合成/并集腿降级
        stock_rows = []
        notes.append(f"kline_daily 查询异常，881xxx 合成/stk_limit 并集腿降级: {e!r}")

    # 881xxx 行业板合成（880xxx 成分在册但 K 线缺失不合成——官方指数缺口，防代理冒充）
    kline_missing_880 = [c for c in constituents if c not in by_sector and c.startswith("880")]
    if kline_missing_880:
        notes.append(
            f"880xxx 板块成分在册但 K 线缺失 {len(kline_missing_880)} 只，不按成分合成（官方指数缺口）"
        )
    synth_codes = [c for c in constituents if c not in by_sector and not c.startswith("880")]
    if synth_codes:
        if stock_rows:
            by_sector.update(_synthesize_industry_series(synth_codes, constituents, stock_rows, d))
        else:
            notes.append("kline_daily 窗内无数据，881xxx 行业板块合成降级")

    if not by_sector:
        return _degraded_report(
            date_str, f"{date_str} 板块全集为空（kline_sector_880 与 881xxx 合成均无数据）"
        )

    all_dates = sorted({dd for series in by_sector.values() for dd, _, _ in series})
    if d not in set(all_dates):
        return _degraded_report(date_str, f"{date_str} 当日无板块数据（非交易日或未采集）")

    rets_by_sector = {c: _daily_returns(s) for c, s in by_sector.items()}
    today_ret = {c: r[d] for c, r in rets_by_sector.items() if d in r}
    if not today_ret:
        return _degraded_report(date_str, f"{date_str} 当日无板块收益截面（板块序列长度不足 2 日）")
    today_amount = {c: {dd: a for dd, _, a in s}.get(d) for c, s in by_sector.items()}

    # ── 资金流维度（money_flow 当日五层 × 成分聚合，元→亿） ──
    flow_map: dict[str, tuple[float, float, float, float, float]] | None = None
    try:
        mf_today = client.execute(SQL_MONEY_FLOW_TODAY, {"trade_date": d})
        if mf_today:
            flow_map = _aggregate_money_flow(mf_today)
        else:
            availability["money_flow"] = "unavailable"
            notes.append(f"{date_str} money_flow 当日无数据，资金流维度降级")
    except Exception as e:  # noqa: BLE001 — 资金流维度独立降级
        availability["money_flow"] = "unavailable"
        notes.append(f"money_flow 当日查询异常，资金流维度降级: {e!r}")

    # ── 涨停梯队（stk_limit/limit_up_down 双源聚合） ──
    close_today = {
        str(r[0]): float(r[2] or 0.0) for r in stock_rows if _as_date(r[1]) == d
    }
    limit_rows: list[tuple] | None = None
    stk_rows: list[tuple] | None = None
    try:
        limit_rows = client.execute(
            SQL_LIMIT_UP_DOWN_WINDOW,
            {"trade_date": d, "start_date": d - timedelta(days=cfg.ladder_lookback_calendar_days)},
        )
    except Exception as e:  # noqa: BLE001 — limit_up_down 腿缺失
        notes.append(f"limit_up_down 查询异常: {e!r}")
    try:
        stk_rows = client.execute(SQL_STK_LIMIT_TODAY, {"trade_date": d})
    except Exception as e:  # noqa: BLE001 — stk_limit 腿缺失
        notes.append(f"stk_limit 查询异常: {e!r}")
    ladder: LimitLadderSummary | None = None
    ladder_by_sector: dict[str, LimitLadderSector] = {}
    if limit_rows is None and stk_rows is None:
        availability["limit_ladder"] = "unavailable"
        notes.append("涨跌停双源（limit_up_down/stk_limit）查询均异常，梯队维度降级")
    else:
        # 交易日历 = 个股 K 线窗日期 ∪ 涨停窗日期（连板高度 trailing 判定基准）
        calendar = sorted(
            {_as_date(r[1]) for r in stock_rows}
            | {_as_date(r[1]) for r in (limit_rows or [])}
        )
        ladder = _build_limit_ladder(
            limit_rows or [], stk_rows or [], close_today, calendar, constituents, names, d, cfg
        )
        ladder_by_sector = {s.sector_code: s for s in ladder.sectors}

    # ── momentum（sector_momentum 多 TF 动量） ──
    closes_by_sector = {c: [cl for _, cl, _ in s] for c, s in by_sector.items()}
    momentum_map = multi_tf_momentum(closes_by_sector)
    if not momentum_map:
        availability["momentum"] = "unavailable"
        notes.append("多 TF 动量截面为空（板块序列均不足 21 日），momentum 维度降级")

    # ── ranking（sector_ranking_engine 5 因子，快照日期须=报告日） ──
    ranking_map: dict[str, float] | None = None
    try:
        snapshot_rows = client.execute(SQL_LATEST_SNAPSHOT, {})
        ranking_map, rank_note = _compute_ranking_scores(snapshot_rows, d)
        if rank_note:
            availability["ranking"] = "unavailable"
            notes.append(rank_note)
    except Exception as e:  # noqa: BLE001 — 快照缺失 ranking 维度降级
        availability["ranking"] = "unavailable"
        notes.append(f"sector_snapshot 查询异常，ranking 维度降级: {e!r}")

    # ── 虹吸态（sector_siphon 复用） ──
    siphon_result: Any | None = None
    try:
        mf_window = client.execute(
            SQL_MONEY_FLOW_WINDOW,
            {"trade_date": d, "start_date": d - timedelta(days=cfg.siphon_lookback_calendar_days)},
        )
        siphon_result, siphon_notes = _compute_siphon(by_sector, constituents, mf_window, d, cfg)
        notes.extend(siphon_notes)
        if siphon_result is None:
            availability["siphon"] = "unavailable"
    except Exception as e:  # noqa: BLE001 — 虹吸维度独立降级
        availability["siphon"] = "unavailable"
        notes.append(f"money_flow 窗口查询异常，虹吸态降级: {e!r}")

    # ── 主线候选 + 5 状态（SEC-05 嵌入，rotation_state 透传） ──
    mainline: MainlineCandidatesResult | None = None
    rotation_state: str | None = None
    watch: float | None = None
    lead_streak: int | None = None
    try:
        mainline = compute_mainline_candidates(trade_date=d, ch_client=client)
    except Exception as e:  # noqa: BLE001 — SEC-05 契约外异常防御（其自身已全降级覆盖）
        notes.append(f"mainline_candidates 计算异常: {e!r}")
    if mainline is None or mainline.degraded:
        availability["mainline"] = "unavailable"
        availability["rotation_state"] = "unavailable"
        if mainline is not None:
            notes.extend(f"主线候选榜降级: {n}" for n in mainline.notes)
    else:
        rotation_state = mainline.rotation_state
        watch = mainline.watch_score
        lead_streak = mainline.lead_streak
        notes.extend(mainline.notes)  # 维度降级留痕透传（如 RRG 数据积累期）

    # ── Top10 榜装配 ──
    analyzer = SectorAnalyzer()
    entries: list[SectorTopEntry] = []
    ordered = sorted(today_ret.items(), key=lambda kv: (-kv[1], kv[0]))[: cfg.top_n]
    for rank, (code, ret) in enumerate(ordered, 1):
        stocks = constituents.get(code, [])
        flows = (
            _sector_flow_yi(code, flow_map, constituents, cfg.yi_unit)
            if flow_map is not None
            else (None,) * 5
        )
        lad = ladder_by_sector.get(code)
        limit_up_count: int | None = None
        ratio: float | None = None
        breadth: str | None = None
        strength_status: str | None = None
        strength_score: float | None = None
        if ladder is not None and stocks:
            limit_up_count = lad.limit_up_count if lad else 0
            ratio = sector_limit_up_ratio(limit_up_count, len(stocks))
            breadth = classify_limit_up_breadth(ratio)
            series = by_sector[code]
            vol_today = today_amount.get(code) or 0.0
            prev_amounts = [a for dd, _, a in series if dd < d]
            vol_prev = prev_amounts[-1] if prev_amounts else 0.0
            vol_change = (vol_today / vol_prev - 1.0) if vol_prev > 0 else 0.0
            vol_up_days = 0
            for i in range(len(series) - 1, 0, -1):
                if series[i][0] > d:
                    continue
                if series[i][2] > series[i - 1][2]:
                    vol_up_days += 1
                else:
                    break
            main_yi = flows[0] if flows[0] is not None else 0.0
            strength_status, strength_score = analyzer.evaluate_strength(
                SectorData(
                    sector_name=names.get(code, code),
                    limit_up_count=limit_up_count,
                    total_stocks=len(stocks),
                    tier2_count=lad.tier2 if lad else 0,
                    tier3_count=lad.tier3_plus if lad else 0,
                    sector_index_change_pct=ret,
                    sector_index_volume_change_pct=vol_change,
                    consecutive_up_days=_trailing_up_days(rets_by_sector[code], all_dates, d),
                    consecutive_volume_up_days=vol_up_days,
                    leader_change_pct=0.0,  # 龙头维度归 SEC-04，本报告不填
                    leader_lagging=False,
                    net_inflow=main_yi,
                    has_policy_support=False,  # 政策/订单/突破无数据源，恒 False（不虚构）
                    has_order_landing=False,
                    technical_breakout=False,
                )
            )
        entries.append(
            SectorTopEntry(
                rank=rank,
                sector_code=code,
                sector_name=names.get(code, code),
                change_pct=ret,
                amount=today_amount.get(code),
                main_net_inflow=flows[0],
                super_large_net_inflow=flows[1],
                large_net_inflow=flows[2],
                medium_net_inflow=flows[3],
                small_net_inflow=flows[4],
                constituent_count=len(stocks),
                limit_up_count=limit_up_count,
                limit_up_ratio=ratio,
                breadth_label=breadth,
                strength_status=strength_status,
                strength_score=strength_score,
                momentum_score=momentum_map.get(code),
                ranking_score=ranking_map.get(code) if ranking_map else None,
            )
        )

    return SectorReport(
        date=date_str,
        generated_at=datetime.now(UTC).isoformat(),
        rotation_state=rotation_state,
        watch_score=watch,
        lead_streak=lead_streak,
        top_sectors=entries,
        limit_ladder=ladder,
        siphon_flag=bool(siphon_result.is_siphon) if siphon_result is not None else False,
        siphon_score=siphon_result.siphon_score if siphon_result is not None else None,
        siphon_sectors=list(siphon_result.siphon_sectors) if siphon_result is not None else [],
        mainline=mainline,
        availability=availability,
        degraded=False,
        notes=list(dict.fromkeys(notes)),  # 去重（SEC-05 透传与本模块同源探测会重复）
    )


# ------------------------------------------------------------------
# 输出：结构化 dict + 落盘 + CLI 摘要
# ------------------------------------------------------------------


def report_to_dict(report: SectorReport) -> dict:
    """SectorReport → 结构化 dict（asdict 嵌套展开，JSON 可序列化）。"""
    return asdict(report)


def write_report(report: SectorReport, out_dir: str | Path | None = None) -> Path:
    """落报告文件：{out_dir}/sector_report_YYYYMMDD.json（默认 .runtime/reports，不入 git）。

    Args:
        report: build_sector_report 输出。
        out_dir: 输出目录；None 用仓根 .runtime/reports。

    Returns:
        落盘文件路径。
    """
    base = Path(out_dir) if out_dir is not None else _DEFAULT_REPORT_DIR
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"sector_report_{report.date.replace('-', '')}.json"
    path.write_text(
        json.dumps(report_to_dict(report), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path


def _render_summary(report: SectorReport, out_path: Path | None) -> str:
    """CLI 中文摘要（Owner 盘后复盘直读）。"""
    lines = [f"=== 板块盘后全景报告 {report.date} ==="]
    if report.degraded:
        lines.append("【降级】板块全集数据缺失，本报告为空壳（notes 留痕）")
    state = report.rotation_state or "unavailable"
    watch = f"{report.watch_score:+.2f}" if report.watch_score is not None else "—"
    streak = str(report.lead_streak) if report.lead_streak is not None else "—"
    if report.siphon_flag:
        siphon = f"是（z={report.siphon_score:.2f}，吸金板块: {','.join(report.siphon_sectors)}）"
    else:
        siphon = "否"
    lines.append(f"轮动状态: {state}（watch_score {watch}）| 连续领涨 {streak} 日 | 虹吸态: {siphon}")

    lines.append("Top10 板块榜:")
    if report.top_sectors:
        for e in report.top_sectors:
            pct = f"{e.change_pct * 100:+.2f}%" if e.change_pct is not None else "—"
            flow = f"{e.main_net_inflow:+.2f}亿" if e.main_net_inflow is not None else "—"
            lu = f"{e.limit_up_count}家({e.breadth_label})" if e.limit_up_count is not None else "—"
            st = f"{e.strength_status}({e.strength_score:.0f})" if e.strength_score is not None else "—"
            lines.append(
                f"  {e.rank:2d}. {e.sector_code} {e.sector_name}  {pct}"
                f"  主力净流入 {flow}  涨停 {lu}  强度 {st}"
            )
    else:
        lines.append("  （无榜单）")

    if report.limit_ladder is not None:
        lad = report.limit_ladder
        lines.append(
            f"涨停梯队: 涨停 {lad.total_limit_up} 家 | 一板 {lad.tier1} / 二板 {lad.tier2}"
            f" / 三板+ {lad.tier3_plus} | 最高连板 {lad.max_streak}"
        )
    else:
        lines.append("涨停梯队: unavailable")

    lines.append("主线候选:")
    if report.mainline is not None and report.mainline.candidates:
        for c in report.mainline.candidates:
            lines.append(f"  - {c.sector_code} {c.sector_name}（score {c.score}）: {'; '.join(c.reasons)}")
    elif report.mainline is not None:
        hint = "; ".join(report.mainline.annotations) or "空榜"
        lines.append(f"  （空榜）{hint}")
    else:
        lines.append("  unavailable")

    if report.notes:
        lines.append("降级/留痕:")
        for note in report.notes:
            lines.append(f"  * {note}")
    if out_path is not None:
        lines.append(f"报告已落盘: {out_path}")
    return "\n".join(lines)


def main(argv: list[str] | None = None, *, ch_client: Any | None = None) -> int:
    """CLI 入口：python -m zephyr.data.sector_report_builder [--date YYYY-MM-DD]。

    Args:
        argv: 命令行参数（None=sys.argv）。
        ch_client: 测试注入用 CH 客户端（生产 None=默认客户端）。
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(description="板块盘后全景报告器（SEC-01）")
    parser.add_argument("--date", default=None, help="交易日 YYYY-MM-DD（默认=板块 K 线最新数据日）")
    parser.add_argument("--out-dir", default=None, help="报告输出目录（默认 .runtime/reports）")
    parser.add_argument("--no-write", action="store_true", help="只打印摘要，不落盘")
    args = parser.parse_args(argv)

    report = build_sector_report(args.date, ch_client=ch_client)
    out_path = None if args.no_write else write_report(report, args.out_dir)
    print(_render_summary(report, out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
