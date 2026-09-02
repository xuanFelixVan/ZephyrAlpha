# [BLUEPRINT] MOD-SIG-061 | 待统筹登记（blueprint 未建，真源=92号清单 §7.8 + 架构审查报告 §11.5 SEC-05 + 22号板块轮动 spec §3.1⑧⑨④）
# [MODULE] zephyr.signal_ashare.mainline_candidates
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.sector_rotation_state; zephyr.signal_ashare.sector_momentum; zephyr.signal_ashare.sector_rrg; c1_market.kline_sector_880（只读）; c1_market.sector_constituent（只读）; c1_market.kline_daily（只读）; c1_market.sector_meta（只读）
# [CONSUMERS] zephyr.data.sector_report_builder（SEC-01 板块盘后全景报告器主线候选维度）; （远期 IDX-02 Dashboard 板块页 D-06）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 不预测纪律：只出候选榜+理由标签，不出方向/点位；候选数 ∈ [0, top_k]；q3 分位 ∈ [0,1]；无主线混沌（连续领涨<2 日）→ 空榜+注解；PIT（全部数据 ≤ trade_date，成分股 SCD-2 时点过滤）；各数据维度独立降级互不累及；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/92_phase2_business_construction_order.md §7.8
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询异常/客户端不可用→对应维度降级 notes 留痕不抛；板块全集为空/当日无收益截面→degraded=True；trade_date 格式非法→ValueError（调用方契约违例，fail-closed）；单板块 K 线不足 62 日→该板块 rrg_quadrant=None 不炸整体
# [TESTS] tests/signal_ashare/test_mainline_candidates.py
# [A_module] module_id=MOD-SIG-061 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""
MOD-SIG-061 — 主线候选榜（92号清单 §7.8，架构审查报告 §11.5 SEC-05，22号 spec 消费层）。

最可能成主线的板块 Top3-5，盘后出榜（T 日收盘后批量，T+1 开盘可消费）：
  ① HEALTHY_MAINLINE 判定——import 消费 sector_rotation_state（classify_rotation_state
     /top_n_hhi/watch_score，5 状态规则映射），市场级状态快照；
  ② lead_streak 连续领涨天数——逐日领涨板块（当日收益最高者）连续领涨日数；
  ③ q3 动量前排——import 消费 sector_momentum（n_day_return/percentile_ranks），
     3 日累计涨跌幅截面分位 ≥0.80 为前排（22号 §3.1⑧ 一日游应对因子）；
  ④ RRG 改善/领先象限——import 消费 sector_rrg（compute_rrg_series JdK DualEma 10/26
     + confirm_quadrant_series whipsaw 连续 2 日确认），象限=接棒/布局信号。

评分（规则层 if-else，无 ML，可审计）：健康主线领涨 +3 / 连续领涨≥2 日 +2 /
当日涨幅居首 +1 / q3 前排 +1 / RRG 领先或改善象限 +1；score≥2 入榜，
按 (score, q3 分位, 代码) 排序取 top_k。无主线混沌（lead_streak<2，22号 §2.3
一日游约束/44号 §9.13 口径）→ 空榜+注解，不强行出榜。

【数据实证口径（2026-08-22 直查 c1_market，可信）】
- kline_sector_880（period='1d'）469 板块=市场统计指数 11（880001-880011，剔除出
  板块全集，880001 作 RRG 基准/市场收益代理）+地区 32+概念风格 426，sector_name
  列全空；
- 板块名称真源 = sector_meta（881xxx 同花顺行业真名，sector_code 为无后缀裸码需归一
  +.SH；SCD 版本取 argMax(trade_date) 最新）；sector_constituent.sector_name 对
  880/881 族大面积为代码回显（如 881386.SH 的名即 "881386.SH"），回显名过滤；
  880xxx 概念板全库无中文名 → 代码直出（采集层缺口，非本模块职责）；
- 纯行业板为 881xxx 族但无板块 K 线 → 行业日收益经 sector_constituent 成分股
  等权聚合（kline_daily.pct_change 均值）合成价格指数，与 880xxx 同管线下游；
- 板块 K 线历史自 2026-06 起采（~52 交易日）：RRG 最小 62 日在数据积累期常态
  降级（该维度 rrg_quadrant=None + notes 留痕），属设计内行为，不炸整体。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 板块日 K 历史窗（kline_sector_880，period=1d）
#   fields: sector_code/trade_date/close/amount
# - id: I2
#   name: 板块成分股映射（sector_constituent，SCD-2 时点有效）
#   fields: sector_code/sector_name/stock_code
# - id: I3
#   name: 个股日 K（kline_daily，881xxx 行业合成腿）
#   fields: symbol_canonical/trade_date/close/amount/pct_change
# 层: 算法
# - id: A1
#   name_zh: 统一板块日序列
#   desc: 880xxx 直取 K 线；881xxx 成分等权 pct_change 合成价格指数（cumprod）
# - id: A2
#   name_zh: 5 状态与连续领涨
#   desc: up_ratio/hhi_top5/lead_streak/disp/fast_rotation → classify_rotation_state（sector_rotation_state 消费）
# - id: A3
#   name_zh: q3 动量前排
#   desc: n_day_return(closes,3) → percentile_ranks 截面分位（sector_momentum 消费）
# - id: A4
#   name_zh: RRG 已确认象限
#   desc: compute_rrg_series → confirm_quadrant_series → 最新已确认象限（sector_rrg 消费，62 日守卫）
# - id: A5
#   name_zh: 候选评分与空榜判定
#   desc: 规则加分（3/2/1/1/1），score≥2 入榜 Top-k；lead_streak<2 → 无主线混沌空榜+注解
# 层: 输出
# - id: O1
#   name_zh: MainlineCandidatesResult
#   intro: date/rotation_state/watch_score/leader/lead_streak/no_mainline_flag/candidates(理由标签链)/annotations/degraded/notes
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2,I3 --> A1
# A1 --> A2
# A1 --> A3
# A1 --> A4
# A2,A3,A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Final

from zephyr.signal_ashare.sector_momentum import n_day_return, percentile_ranks
from zephyr.signal_ashare.sector_rotation_state import (
    classify_rotation_state,
    top_n_hhi,
    watch_score,
)
from zephyr.signal_ashare.sector_rrg import compute_rrg_series, confirm_quadrant_series

logger = logging.getLogger(__name__)

__all__: Final = [
    "MainlineCandidate",
    "MainlineCandidatesConfig",
    "MainlineCandidatesResult",
    "compute_mainline_candidates",
    "select_mainline_candidates",
]

#: 市场统计指数代码（剔除出板块全集；880001 作 RRG 基准/市场收益代理）
_MARKET_INDEX_CODES: Final = frozenset(f"880{i:03d}.SH" for i in range(1, 12))

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


@dataclass(frozen=True, slots=True)
class MainlineCandidatesConfig:
    """阈值配置——默认值取自 22号 spec §3.1⑧⑨ + 44号 §9.13 + 2026-08-22 数据实证。"""

    sector_lookback_calendar_days: int = 400  # 板块 K 线查询自然日窗（覆盖 RRG 62 交易日最小量）
    stock_lookback_calendar_days: int = 120  # 个股 K 线查询自然日窗（881xxx 合成腿）
    market_index_code: str = "880001.SH"  # RRG 基准/市场收益代理（总市值指数）
    top_k: int = 5  # 候选榜上限（Top3-5）
    min_score: int = 2  # 入榜门槛（至少两个支撑维度或连续领涨）
    q3_front_percentile: float = 0.80  # q3 动量前排分位阈值（前 20%）
    no_mainline_streak: int = 2  # 无主线判定：当前领涨连续领涨 <2 日（44号 §9.13）
    fast_rotation_window: int = 90  # 快轮动标志 P90 参照窗（交易日）
    fast_rotation_min_periods: int = 10  # P90 最小样本（不足 → fast_rotation=False）
    hhi_top_n: int = 5  # 5 状态 hhi_top5 头部板块数
    rrg_min_days: int = 62  # RRG 最小数据量（long×2+short，sector_rrg 契约）


@dataclass(frozen=True, slots=True)
class MainlineCandidate:
    """主线候选条目（理由标签链可追溯）。"""

    sector_code: str
    sector_name: str  # sector_constituent.sector_name 映射，缺失回退代码
    score: int  # 规则加分合计
    reasons: list[str] = field(default_factory=list)  # 理由标签清单（中文，消费方直读）
    lead_streak: int = 0  # 该板块截至当日连续领涨天数（非当日领涨=0）
    q3_percentile: float | None = None  # 3 日涨幅截面分位 ∈ [0,1]；序列不足 → None
    rrg_quadrant: str | None = None  # 已确认 RRG 象限（LEADING/IMPROVING/WEAKENING/LAGGING）；数据不足 → None


@dataclass(frozen=True, slots=True)
class MainlineCandidatesResult:
    """主线候选榜输出契约（T 日盘后计算，观测层消费，不接交易）。"""

    date: str  # 数据日 YYYY-MM-DD
    rotation_state: str | None = None  # 板块轮动 5 状态（RotationState 值）
    watch_score: float | None = None  # 22号 watch_score 透传
    leader_code: str | None = None  # 当日领涨板块代码
    leader_name: str | None = None
    lead_streak: int | None = None  # 当前领涨板块连续领涨天数
    no_mainline_flag: bool = False  # 无主线混沌（lead_streak<2）→ 空榜
    candidates: list[MainlineCandidate] = field(default_factory=list)
    annotations: list[str] = field(default_factory=list)  # 中文注解文本链
    degraded: bool = False  # 板块全集/当日截面不可用时 True，结果不可用于决策
    notes: list[str] = field(default_factory=list)  # 降级原因等留痕


# ------------------------------------------------------------------
# 纯函数评分核心（不触库，可单测）
# ------------------------------------------------------------------


def select_mainline_candidates(
    *,
    rotation_state: str | None,
    leader_code: str | None,
    lead_streak: int | None,
    sector_streaks: dict[str, int],
    q3_percentiles: dict[str, float],
    rrg_quadrants: dict[str, str | None],
    sector_names: dict[str, str],
    config: MainlineCandidatesConfig | None = None,
) -> tuple[list[MainlineCandidate], bool, list[str]]:
    """主线候选评分核心：四维规则加分 → Top-k 候选榜。

    加分规则（可审计 if-else）：健康主线领涨 +3 / 连续领涨≥2 日 +2 /
    当日涨幅居首 +1 / q3 动量前排（分位≥q3_front_percentile）+1 /
    RRG 领先或改善象限 +1；score≥min_score 入榜。

    Args:
        rotation_state: 当日板块轮动 5 状态（RotationState 值）；None=未知。
        leader_code: 当日领涨板块代码；None=无领涨截面。
        lead_streak: 当前领涨板块连续领涨天数；None=未知（不判混沌）。
        sector_streaks: 各板块连续领涨天数（非当日领涨=0）。
        q3_percentiles: 各板块 3 日涨幅截面分位 ∈ [0,1]。
        rrg_quadrants: 各板块已确认 RRG 象限（None=数据不足）。
        sector_names: 板块代码 → 中文名。
        config: 阈值配置（None 用默认）。

    Returns:
        (candidates, no_mainline_flag, annotations)：
        无主线混沌（lead_streak<no_mainline_streak）→ 空榜 + 混沌注解；
        非混沌但无板块过门槛 → 空榜 + 门槛注解。
    """
    cfg = config or MainlineCandidatesConfig()
    if lead_streak is not None and lead_streak < cfg.no_mainline_streak:
        return (
            [],
            True,
            [
                f"无主线混沌：当前领涨板块连续领涨{lead_streak}日<{cfg.no_mainline_streak}日"
                "（22号一日游约束，混沌/下跌中继，不强行出榜）"
            ],
        )

    universe = set(sector_streaks) | set(q3_percentiles) | set(rrg_quadrants)
    candidates: list[MainlineCandidate] = []
    for code in universe:
        score = 0
        reasons: list[str] = []
        streak = sector_streaks.get(code, 0)
        if (
            code == leader_code
            and rotation_state == "HEALTHY_MAINLINE"
            and lead_streak is not None
            and lead_streak >= 3
        ):
            score += 3
            reasons.append(f"健康主线领涨（5状态=HEALTHY_MAINLINE，连续领涨{lead_streak}日）")
        elif streak >= 2:
            score += 2
            reasons.append(f"连续领涨{streak}日")
        elif streak == 1 and code == leader_code:
            score += 1
            reasons.append("当日涨幅居首")
        q3 = q3_percentiles.get(code)
        if q3 is not None and q3 >= cfg.q3_front_percentile:
            score += 1
            reasons.append(f"q3动量前排（3日涨幅分位{q3:.0%}）")
        quad = rrg_quadrants.get(code)
        if quad == "LEADING":
            score += 1
            reasons.append("RRG领先象限（接棒中）")
        elif quad == "IMPROVING":
            score += 1
            reasons.append("RRG改善象限（提前布局）")
        if score < cfg.min_score:
            continue
        candidates.append(
            MainlineCandidate(
                sector_code=code,
                sector_name=sector_names.get(code, code),
                score=score,
                reasons=reasons,
                lead_streak=streak,
                q3_percentile=q3,
                rrg_quadrant=quad,
            )
        )

    candidates.sort(
        key=lambda c: (-c.score, -(c.q3_percentile if c.q3_percentile is not None else -1.0), c.sector_code)
    )
    candidates = candidates[: cfg.top_k]
    if not candidates:
        return [], False, [f"无任何板块满足主线候选门槛（score≥{cfg.min_score}）：主线混沌/观察期"]
    return candidates, False, []


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
        logger.warning("ch_writer 默认客户端不可用，主线候选榜降级", exc_info=True)
        return None


def _as_date(v: Any) -> date:
    """CH 日期行值归一（date 原样返回，str 按 YYYY-MM-DD 解析）。"""
    return v if isinstance(v, date) else _normalize_date(v)


def _degraded_result(date_str: str, note: str) -> MainlineCandidatesResult:
    logger.warning("主线候选榜降级: %s", note)
    return MainlineCandidatesResult(date=date_str, degraded=True, notes=[note])


def _sector_880_series(
    rows: list[tuple], d: date, market_index_code: str
) -> tuple[dict[str, list[tuple[date, float, float]]], list[tuple[date, float]]]:
    """880 板块 K 线行 → ({板块: [(日期, 收盘, 成交额)] 升序}, 基准 [(日期, 收盘)] 升序)。

    剔除市场统计指数（880001-880011）；基准=market_index_code 单独返回；
    PIT 防御：> d 的行丢弃（SQL 已 ≤ d，此处双保险）。
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

    成交额 = 成分股 amount 合计（HHI/放量滞涨共用）；无成分 K 线覆盖的板块跳过。
    """
    by_stock: dict[str, dict[date, tuple[float, float]]] = {}
    for row in stock_rows:
        dd = _as_date(row[1])
        if dd > d:
            continue
        by_stock.setdefault(str(row[0]), {})[dd] = (float(row[4] or 0.0), float(row[3] or 0.0))
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
            price *= 1.0 + sum(p for p, _ in legs) / len(legs) / 100.0
            series.append((dd, price, sum(a for _, a in legs)))
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


def _lead_streaks(leaders: dict[date, str], sorted_dates: list[date]) -> dict[date, int]:
    """逐日连续领涨天数（同一板块截至当日连续领涨日数；当日无领涨 → 不出键）。"""
    streaks: dict[date, int] = {}
    prev_leader: str | None = None
    streak = 0
    for dd in sorted_dates:
        leader = leaders.get(dd)
        if leader is None:
            prev_leader = None
            streak = 0
            continue
        streak = streak + 1 if leader == prev_leader else 1
        prev_leader = leader
        streaks[dd] = streak
    return streaks


def _rotation_speeds(amounts: dict[str, dict[date, float]], sorted_dates: list[date]) -> dict[date, float]:
    """逐日轮动速度 = 0.5 × Σ|今日成交额占比 − 昨日占比|（22号 §3.1⑨ fast_rotation 口径）。"""
    speeds: dict[date, float] = {}
    prev_shares: dict[str, float] | None = None
    for dd in sorted_dates:
        today = {c: amap[dd] for c, amap in amounts.items() if dd in amap}
        total = sum(today.values())
        shares = {c: a / total for c, a in today.items()} if total > 0 else {}
        if prev_shares is not None and shares:
            codes = set(shares) | set(prev_shares)
            speeds[dd] = 0.5 * sum(abs(shares.get(c, 0.0) - prev_shares.get(c, 0.0)) for c in codes)
        prev_shares = shares
    return speeds


def _fast_rotation(
    amounts: dict[str, dict[date, float]], sorted_dates: list[date], cfg: MainlineCandidatesConfig
) -> bool:
    """快轮动标志：当日轮动速度 > 前 fast_rotation_window 日 P90（样本不足 → False 不放宽）。"""
    speeds = _rotation_speeds(amounts, sorted_dates)
    d = sorted_dates[-1]
    if d not in speeds:
        return False
    hist = [speeds[dd] for dd in sorted_dates[-(cfg.fast_rotation_window + 1) : -1] if dd in speeds]
    if len(hist) < cfg.fast_rotation_min_periods:
        return False
    p90 = sorted(hist)[min(len(hist) - 1, math.ceil(0.9 * len(hist)) - 1)]
    return speeds[d] > p90


def _disp_signal(
    d: date,
    leader: str | None,
    by_sector: dict[str, list[tuple[date, float, float]]],
    amounts: dict[str, dict[date, float]],
    cross: dict[date, dict[str, float]],
) -> int:
    """领涨板块放量滞涨：成交额 > 5 日均额 ×1.2 且 当日涨幅 < 前日涨幅 ×0.5（22号 §3.1⑨ 口径）。"""
    if leader is None:
        return 0
    series = by_sector.get(leader)
    amt_map = amounts.get(leader)
    if not series or not amt_map:
        return 0
    idx = next((i for i, (dd, _, _) in enumerate(series) if dd == d), None)
    if idx is None or idx == 0:
        return 0
    prev_days = [series[i][0] for i in range(max(0, idx - 5), idx)]
    prev5 = [amt_map[dd] for dd in prev_days if amt_map.get(dd, 0.0) > 0]
    if len(prev5) < 2:
        return 0
    amount_today = amt_map.get(d, 0.0)
    ret_today = cross.get(d, {}).get(leader)
    ret_prev = cross.get(series[idx - 1][0], {}).get(leader)
    if ret_today is None or ret_prev is None:
        return 0
    mean_amt = sum(prev5) / len(prev5)
    return 1 if amount_today > mean_amt * 1.2 and ret_today < ret_prev * 0.5 else 0


def _fallback_bench(by_sector: dict[str, list[tuple[date, float, float]]]) -> list[tuple[date, float]]:
    """基准缺失回退：全板块收盘价逐日均值（22号 spec §3.1④ 口径，与 ranking_engine 同源）。"""
    per_date: dict[date, list[float]] = {}
    for series in by_sector.values():
        for dd, close, _ in series:
            per_date.setdefault(dd, []).append(close)
    return sorted(((dd, sum(v) / len(v)) for dd, v in per_date.items()), key=lambda x: x[0])


def _q3_percentiles(by_sector: dict[str, list[tuple[date, float, float]]]) -> dict[str, float]:
    """q3 截面分位：3 日累计涨跌幅 → percentile_ranks（序列 <4 日的板块不出键）。"""
    rets: dict[str, float] = {}
    for code, series in by_sector.items():
        closes = [c for _, c, _ in series]
        if len(closes) < 4:
            continue
        try:
            rets[code] = n_day_return(closes, 3)
        except ValueError:
            continue
    return percentile_ranks(rets)


def _rrg_quadrants(
    by_sector: dict[str, list[tuple[date, float, float]]],
    bench_series: list[tuple[date, float]],
    cfg: MainlineCandidatesConfig,
) -> tuple[dict[str, str | None], list[str]]:
    """逐板块已确认 RRG 象限（whipsaw 连续 2 日确认后取最新值）。

    单板块对齐基准后序列 < rrg_min_days（62）或计算异常 → None 不炸整体；
    全宇宙零成功 → notes 汇总留痕（数据积累期常态降级）。
    """
    notes: list[str] = []
    bench_map = {dd: c for dd, c in bench_series if c > 0}
    out: dict[str, str | None] = {}
    n_ok = 0
    for code, series in by_sector.items():
        common = [(dd, close) for dd, close, _ in series if dd in bench_map]
        if len(common) < cfg.rrg_min_days:
            out[code] = None
            continue
        p_sector = [c for _, c in common]
        p_bench = [bench_map[dd] for dd, _ in common]
        try:
            points = compute_rrg_series(p_sector, p_bench)
            confirmed = confirm_quadrant_series([p.quadrant for p in points])
        except ValueError:
            out[code] = None
            continue
        out[code] = confirmed[-1].value if confirmed else None
        if confirmed:
            n_ok += 1
    if by_sector and n_ok == 0:
        notes.append(
            f"RRG 维度降级：全 {len(by_sector)} 板块对齐基准后 K 线不足 {cfg.rrg_min_days} 日"
            "（数据积累期），象限维度按不可用处理"
        )
    return out, notes


# ------------------------------------------------------------------
# 主入口
# ------------------------------------------------------------------


def compute_mainline_candidates(
    trade_date: str | date | datetime | None = None,
    ch_client: Any | None = None,
    config: MainlineCandidatesConfig | None = None,
) -> MainlineCandidatesResult:
    """主入口：主线候选榜（HEALTHY_MAINLINE 判定 + lead_streak + q3 前排 + RRG 象限）。

    Args:
        trade_date: 数据日；None 时取 kline_sector_880 最新数据日（PIT 数据日口径）。
        ch_client: clickhouse-driver 鸭子类型（execute(sql, params) -> list[tuple]）；
            None 时延迟取 ch_writer.get_client，不可得 → degraded。
        config: 阈值配置（None 用默认 22号/44号 + 实证口径）。

    Returns:
        MainlineCandidatesResult；板块全集为空/当日无收益截面/查询异常 → degraded=True
        空榜不炸；881 合成/RRG/q3 各维度独立降级互不累及（notes 留痕）。
    """
    cfg = config or MainlineCandidatesConfig()

    client = ch_client if ch_client is not None else _default_client()
    if client is None:
        d = _normalize_date(trade_date) if trade_date is not None else date.today()
        return _degraded_result(d.isoformat(), "ch_client 未注入且默认客户端不可用")

    if trade_date is None:
        try:
            latest = client.execute(SQL_LATEST_SECTOR_DATE, {})
        except Exception as e:  # noqa: BLE001 — 数据层异常一律降级不炸
            return _degraded_result("unknown", f"最新板块数据日查询异常: {e!r}")
        if not latest or latest[0][0] is None:
            return _degraded_result("unknown", "kline_sector_880 无任何日 K 数据")
        d = _as_date(latest[0][0])
    else:
        d = _normalize_date(trade_date)
    date_str = d.isoformat()

    # ── 板块 K 线窗（880xxx 直取 + 880001 基准） ──
    sector_start = d - timedelta(days=cfg.sector_lookback_calendar_days)
    try:
        sector_rows = client.execute(SQL_SECTOR_KLINE_WINDOW, {"trade_date": d, "start_date": sector_start})
    except Exception as e:  # noqa: BLE001 — 数据层异常一律降级不炸
        return _degraded_result(date_str, f"kline_sector_880 查询异常: {e!r}")
    by_sector, bench_series = _sector_880_series(sector_rows, d, cfg.market_index_code)

    notes: list[str] = []

    # ── 成分映射（881xxx 合成候选；名称回显过滤——成分表 sector_name 大面积=代码回显） ──
    constituents: dict[str, list[str]] = {}
    names: dict[str, str] = {}
    try:
        for row in client.execute(SQL_SECTOR_CONSTITUENTS, {"trade_date": d}):
            code = str(row[0])
            constituents.setdefault(code, []).append(str(row[2]))
            name = str(row[1] or "").strip()
            if name and name != code:
                names.setdefault(code, name)
    except Exception as e:  # noqa: BLE001 — 成分缺失，名称/881 维度独立降级
        notes.append(f"sector_constituent 查询异常，名称/881xxx 合成维度降级: {e!r}")

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

    # ── 881xxx 行业板合成（成分等权聚合，无 K 线实证裁定） ──
    # 合成路径仅服务 881xxx 族：880xxx 有官方 K 线真源，成分在册但 K 线缺失属数据缺口，
    # 不按成分合成（防代理指数冒充官方指数），notes 留痕。
    kline_missing_880 = [c for c in constituents if c not in by_sector and c.startswith("880")]
    if kline_missing_880:
        notes.append(f"880xxx 板块成分在册但 K 线缺失 {len(kline_missing_880)} 只，不按成分合成（官方指数缺口）")
    synth_codes = [c for c in constituents if c not in by_sector and not c.startswith("880")]
    if synth_codes:
        stock_start = d - timedelta(days=cfg.stock_lookback_calendar_days)
        try:
            stock_rows = client.execute(SQL_STOCK_KLINE_WINDOW, {"trade_date": d, "start_date": stock_start})
        except Exception as e:  # noqa: BLE001 — 个股 K 线缺失，881 维度独立降级
            stock_rows = []
            notes.append(f"kline_daily 查询异常，881xxx 行业板块合成降级: {e!r}")
        if stock_rows:
            by_sector.update(_synthesize_industry_series(synth_codes, constituents, stock_rows, d))
        else:
            notes.append("kline_daily 窗内无数据，881xxx 行业板块合成降级")

    if not by_sector:
        return _degraded_result(date_str, f"{date_str} 板块全集为空（kline_sector_880 与 881xxx 合成均无数据）")

    all_dates = sorted({dd for series in by_sector.values() for dd, _, _ in series})
    if d not in set(all_dates):
        return _degraded_result(date_str, f"{date_str} 当日无板块数据（非交易日或未采集）")

    # ── 市场级截面：领涨序列 / 连续领涨 / 5 状态输入 ──
    amounts_map = {c: {dd: a for dd, _, a in s} for c, s in by_sector.items()}
    cross: dict[date, dict[str, float]] = {}
    for code, series in by_sector.items():
        for dd, ret in _daily_returns(series).items():
            cross.setdefault(dd, {})[code] = ret
    leaders = {dd: max(day.items(), key=lambda kv: kv[1])[0] for dd, day in cross.items() if day}
    sorted_dates = [dd for dd in all_dates if dd in cross]
    streaks = _lead_streaks(leaders, sorted_dates)

    day = cross.get(d)
    if not day:
        return _degraded_result(date_str, f"{date_str} 当日无板块收益截面（板块序列长度不足 2 日）")
    leader = leaders.get(d)
    lead_streak = streaks.get(d)
    up_ratio = sum(1 for r in day.values() if r > 0) / len(day)
    day_amounts = [amounts_map[c][d] for c in day if d in amounts_map.get(c, {})]
    hhi = top_n_hhi(day_amounts, n=cfg.hhi_top_n)
    disp = _disp_signal(d, leader, by_sector, amounts_map, cross)
    fast = _fast_rotation(amounts_map, sorted_dates, cfg)
    state = classify_rotation_state(
        up_ratio=up_ratio,
        hhi_top5=hhi,
        lead_streak=lead_streak if lead_streak is not None else 1,
        disp_signal=disp,
        fast_rotation=fast,
    )
    ws = watch_score(state)
    annotations: list[str] = [f"板块 5 状态={state.value}（watch_score {ws:+.2f}）"]

    # ── q3 动量前排（sector_momentum 消费） ──
    q3_pct = _q3_percentiles(by_sector)

    # ── RRG 已确认象限（sector_rrg 消费，基准缺失回退全板块均值） ──
    if not bench_series:
        bench_series = _fallback_bench(by_sector)
        notes.append(f"{cfg.market_index_code} 基准缺失，RRG 基准回退全板块均值（22号 spec 口径）")
    rrg_quadrants, rrg_notes = _rrg_quadrants(by_sector, bench_series, cfg)
    notes.extend(rrg_notes)

    # ── 候选评分与空榜判定（纯函数核心） ──
    sector_streaks = {c: (lead_streak or 0) if c == leader else 0 for c in by_sector}
    candidates, no_mainline, sel_annotations = select_mainline_candidates(
        rotation_state=state.value,
        leader_code=leader,
        lead_streak=lead_streak,
        sector_streaks=sector_streaks,
        q3_percentiles=q3_pct,
        rrg_quadrants=rrg_quadrants,
        sector_names=names,
        config=cfg,
    )
    annotations.extend(sel_annotations)

    return MainlineCandidatesResult(
        date=date_str,
        rotation_state=state.value,
        watch_score=ws,
        leader_code=leader,
        leader_name=names.get(leader) if leader is not None else None,
        lead_streak=lead_streak,
        no_mainline_flag=no_mainline,
        candidates=candidates,
        annotations=annotations,
        degraded=False,
        notes=notes,
    )
