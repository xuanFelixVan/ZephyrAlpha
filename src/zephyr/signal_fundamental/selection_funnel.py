# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.6
# [MODULE] zephyr.signal_fundamental.selection_funnel
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] (待 G08/G09/G10 sleeve 接线)
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 漏斗单调收敛：BM-SEL-16 输出 ⊇ BM-SEL-17 输出 ⊇ BM-SEL-18 输出；精筛输出 ≤ top_n
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 记录字段缺失由 dataclass 默认值兜底；降级路径以 degraded=True 显式标记
# [TESTS] tests/signal_fundamental/test_selection_funnel.py
# [TTL] permanent
#
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: FunnelSymbolRecord 候选标的记录
#   fields: 物理标记(涨跌停/停牌/ST) + 上市天数 + 流动性(日均成交额/AUM) + 弃庄概率
#           + 五维初筛输入(技术/量比/换手/板块排名/主力/状态) + 六要素评分输入
# 层: 算法
# - id: A1
#   name: BM-SEL-16 分级指标过滤 filter_graded_indicators（~7000→~1200）
#   desc: 四排除机制——物理排除(涨跌停/停牌/ST) / 门禁排除(上市<30天) / 分级排除(成交额<500万、AUM≤100万) / 概率排除(弃庄概率>95%)；降级=仅排除涨跌停/停牌
# - id: A2
#   name: BM-SEL-17 五维初筛 screen_preliminary（~1200→~300）
#   desc: 技术(布尔) + 量价(量比>1.5、换手率门槛) + 板块(强度排名前30%) + 主力(C-011布尔) + 状态(C-021布尔)；降级=全量放行
# - id: A3
#   name: BM-SEL-18 六要素精筛评分 score_fine_selection（~300→~50）
#   desc: 基础评分(价值40/动量30/质量20/情绪10)×(1+状态偏移±10%) + 主力×0.20 - 拥挤×0.10 - 密度×0.15（8态修正置0，90号§7暂缓）→ 横截面 Z-score 降序 Top-N；降级=等权综合
# 层: 输出
# - id: O1
#   name: GradedFilterResult / PreliminaryScreenResult / FineSelectionResult
#   intro: 三级结果含保留/排除清单、排除归因、降级标记；Z-score 排名 Top-N 喂 sleeve 排序
# [/ALGO_FLOW]
"""选股漏斗三层级（21 号 memo §3.6，BM-SEL-16/17/18，规则层批处理模块）。

执行频率裁定（memo v1.1.19）：日线级选股盘前批处理；作战地图 trigger 的
"3 秒 Tick / 60 秒级"语义登记远期，盘中不滚动。

降级链路：
- BM-SEL-16 未就绪 → 仅排除涨跌停/停牌，其余放行（degraded=True）
- BM-SEL-17 未就绪 → 全量进精筛（算力风险告警由调用方负责）
- BM-SEL-18 未就绪 → 等权综合评分

权重说明：BM-SEL-18 六要素合成权重（主力 0.20 / 拥挤 0.10 / 密度 0.15）为经验初值，
与 memo §3.4 6 维权重同属"经验设定 → 待 G09 回测校准"口径；8 态修正项按 90 号 §7
暂缓裁定置 0 不参与（等效五要素），重评条件满足后恢复接入。
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

# ------------------------------------------------------------------
# BM-SEL-16 分级指标过滤阈值（memo §3.6 ① 契约——四排除机制语义）
# ------------------------------------------------------------------
NEW_STOCK_MIN_LIST_DAYS = 30  # 门禁排除：次新上市 <30 天绝对排除
MIN_AVG_DAILY_AMOUNT = 5_000_000.0  # 分级排除：日均成交额 <500 万剔除（元）
MIN_AUM = 1_000_000.0  # 分级排除：AUM≤100 万级剔除（元）
DEALER_ABANDON_PROB_MAX = 0.95  # 概率排除：庄家弃庄概率 >95% 剔除

# ------------------------------------------------------------------
# BM-SEL-17 初筛阈值（memo §3.6 ② 契约——五维构成）
# ------------------------------------------------------------------
VOLUME_RATIO_MIN = 1.5  # 量比 >1.5
TURNOVER_RATE_MIN_PCT = 0.0  # 换手率门槛（memo 未定值，默认 0=不强制，G09 校准）
SECTOR_STRENGTH_RANK_MAX_PCT = 0.30  # 板块强度排名前 30%

# ------------------------------------------------------------------
# BM-SEL-18 精筛评分权重（memo §3.6 ③ 契约——六要素构成）
# ------------------------------------------------------------------
BASE_SCORE_WEIGHTS = {"value": 0.40, "momentum": 0.30, "quality": 0.20, "sentiment": 0.10}
REGIME_SHIFT_MAX = 0.10  # 状态偏移 ±10% 修正
MAIN_FORCE_WEIGHT = 0.20  # 主力评分合成权重（经验初值，G09 校准）
CROWDING_WEIGHT = 0.10  # 拥挤度扣分权重（经验初值，G09 校准）
DENSITY_WEIGHT = 0.15  # 密度要素扣分权重 15%（memo 定值）
EIGHT_STATE_WEIGHT = 0.0  # 8 态修正：90 号 §7 暂缓 → 置 0 不参与
DEFAULT_TOP_N = 50  # 漏斗容量链：精筛 Top ~50


@dataclass(frozen=True)
class FunnelSymbolRecord:
    """漏斗候选标的记录——三级共用一份记录，各级只消费自身字段。"""

    symbol: str
    # ── BM-SEL-16 输入 ──
    is_limit_locked: bool = False  # 涨跌停封死（当日无法交易）
    is_suspended: bool = False  # 停牌
    is_st: bool = False  # ST/*ST/退市风险
    list_days: int = 9999  # 上市天数
    avg_daily_amount: float = 1e12  # 日均成交额（元）
    aum: float = 1e12  # 资产规模 AUM（元）
    dealer_abandon_prob: float = 0.0  # 庄家弃庄概率 [0,1]（BM-SEL-05 输出）
    # ── BM-SEL-17 输入 ──
    technical_pass: bool = True  # 技术形态初筛（均线/KDJ/MACD，BM-SEL-02）
    volume_ratio: float = 999.0  # 量比
    turnover_rate_pct: float = 999.0  # 换手率（%）
    sector_strength_rank_pct: float = 0.0  # 板块强度排名前百分位 [0,1]
    main_force_pass: bool = True  # C-011 主力阶段（BM-SEL-05）
    market_state_pass: bool = True  # C-021 市场状态（BM-SEL-03）
    # ── BM-SEL-18 输入（各维 0-100）──
    base_value_score: float = 50.0  # 价值分
    base_momentum_score: float = 50.0  # 动量分
    base_quality_score: float = 50.0  # 质量分
    base_sentiment_score: float = 50.0  # 情绪分
    regime_shift: float = 0.0  # 状态偏移修正 [-0.10, +0.10]（C-021）
    main_force_score: float = 50.0  # 主力评分（C-034/C-035）
    crowding_score: float = 0.0  # 拥挤度（越高越扣分，C-045）
    neg_skewness: float = 0.0  # 负偏度幅度 max(0,-skew)（密度要素）
    excess_kurtosis: float = 0.0  # 超额峰度 max(0,kurtosis-3)（密度要素）
    forward_var_pct: float = 0.0  # 前瞻 VaR 幅度 %（密度要素，正数=亏损幅度）
    eight_state_score: float = 0.0  # 8 态修正（暂缓，置 0 不参与）


@dataclass(frozen=True)
class GradedFilterResult:
    """BM-SEL-16 输出。"""

    kept: tuple[str, ...]  # 保留标的
    excluded: dict[str, str] = field(default_factory=dict)  # {symbol: 排除原因}
    degraded: bool = False  # True=降级路径（仅排除涨跌停/停牌）


@dataclass(frozen=True)
class PreliminaryScreenResult:
    """BM-SEL-17 输出。"""

    kept: tuple[str, ...]
    excluded: dict[str, str] = field(default_factory=dict)
    degraded: bool = False  # True=降级路径（全量进精筛）


@dataclass(frozen=True)
class ScoredSymbol:
    """BM-SEL-18 单标的评分结果。"""

    symbol: str
    raw_score: float  # 六要素合成原始分
    z_score: float  # 横截面 Z-score 标准化分
    rank: int  # 降序排名（1 起）


@dataclass(frozen=True)
class FineSelectionResult:
    """BM-SEL-18 输出。"""

    top: tuple[ScoredSymbol, ...]  # Top-N（按 z_score 降序）
    degraded: bool = False  # True=降级路径（等权综合评分）


@dataclass(frozen=True)
class SelectionFunnelResult:
    """漏斗三级串联输出。"""

    graded: GradedFilterResult
    screened: PreliminaryScreenResult
    scored: FineSelectionResult


# ------------------------------------------------------------------
# BM-SEL-16 分级指标过滤（~7000→~1200）
# ------------------------------------------------------------------
def filter_graded_indicators(
    records: list[FunnelSymbolRecord],
    *,
    degraded: bool = False,
) -> GradedFilterResult:
    """四排除机制批处理过滤。只排除不评分，廉价规则先砍量。

    degraded=True（过滤模块未就绪）：仅排除涨跌停/停牌，其余放行。
    """
    kept: list[str] = []
    excluded: dict[str, str] = {}
    for rec in records:
        # 物理排除（降级路径也保留：涨跌停/停牌硬剔除）
        if rec.is_limit_locked:
            excluded[rec.symbol] = "physical:limit_locked"
            continue
        if rec.is_suspended:
            excluded[rec.symbol] = "physical:suspended"
            continue
        if degraded:
            kept.append(rec.symbol)
            continue
        if rec.is_st:
            excluded[rec.symbol] = "physical:st"
            continue
        # 门禁排除
        if rec.list_days < NEW_STOCK_MIN_LIST_DAYS:
            excluded[rec.symbol] = f"gate:new_stock({rec.list_days}d<{NEW_STOCK_MIN_LIST_DAYS}d)"
            continue
        # 分级排除（流动性失效保护）
        if rec.avg_daily_amount < MIN_AVG_DAILY_AMOUNT:
            excluded[rec.symbol] = "tier:low_amount"
            continue
        if rec.aum <= MIN_AUM:
            excluded[rec.symbol] = "tier:low_aum"
            continue
        # 概率排除
        if rec.dealer_abandon_prob > DEALER_ABANDON_PROB_MAX:
            excluded[rec.symbol] = "prob:dealer_abandon"
            continue
        kept.append(rec.symbol)
    return GradedFilterResult(kept=tuple(kept), excluded=excluded, degraded=degraded)


# ------------------------------------------------------------------
# BM-SEL-17 五维初筛（~1200→~300）
# ------------------------------------------------------------------
def screen_preliminary(
    records: list[FunnelSymbolRecord],
    *,
    degraded: bool = False,
    volume_ratio_min: float = VOLUME_RATIO_MIN,
    turnover_rate_min_pct: float = TURNOVER_RATE_MIN_PCT,
    sector_rank_max_pct: float = SECTOR_STRENGTH_RANK_MAX_PCT,
) -> PreliminaryScreenResult:
    """五维布尔/门槛式初筛：技术 + 量价 + 板块 + 主力 + 状态。

    degraded=True（初筛未就绪）：全量放行进精筛。
    """
    if degraded:
        return PreliminaryScreenResult(
            kept=tuple(r.symbol for r in records), excluded={}, degraded=True,
        )
    kept: list[str] = []
    excluded: dict[str, str] = {}
    for rec in records:
        if not rec.technical_pass:
            excluded[rec.symbol] = "dim:technical"
            continue
        if rec.volume_ratio <= volume_ratio_min:
            excluded[rec.symbol] = f"dim:volume_ratio({rec.volume_ratio:.2f}<={volume_ratio_min})"
            continue
        if rec.turnover_rate_pct < turnover_rate_min_pct:
            excluded[rec.symbol] = "dim:turnover_rate"
            continue
        if rec.sector_strength_rank_pct > sector_rank_max_pct:
            excluded[rec.symbol] = "dim:sector_rank"
            continue
        if not rec.main_force_pass:
            excluded[rec.symbol] = "dim:main_force"
            continue
        if not rec.market_state_pass:
            excluded[rec.symbol] = "dim:market_state"
            continue
        kept.append(rec.symbol)
    return PreliminaryScreenResult(kept=tuple(kept), excluded=excluded, degraded=False)


# ------------------------------------------------------------------
# BM-SEL-18 六要素精筛评分（~300→~50）
# ------------------------------------------------------------------
def _composite_raw_score(rec: FunnelSymbolRecord, *, degraded: bool) -> float:
    """六要素合成原始分。degraded=True → 等权综合评分。"""
    if degraded:
        return (
            rec.base_value_score
            + rec.base_momentum_score
            + rec.base_quality_score
            + rec.base_sentiment_score
            + rec.main_force_score
        ) / 5.0
    base = (
        BASE_SCORE_WEIGHTS["value"] * rec.base_value_score
        + BASE_SCORE_WEIGHTS["momentum"] * rec.base_momentum_score
        + BASE_SCORE_WEIGHTS["quality"] * rec.base_quality_score
        + BASE_SCORE_WEIGHTS["sentiment"] * rec.base_sentiment_score
    )
    shift = max(-REGIME_SHIFT_MAX, min(REGIME_SHIFT_MAX, rec.regime_shift))
    density_penalty = rec.neg_skewness * 10.0 + rec.excess_kurtosis * 5.0 + rec.forward_var_pct
    return (
        base * (1.0 + shift)
        + MAIN_FORCE_WEIGHT * rec.main_force_score
        - CROWDING_WEIGHT * rec.crowding_score
        - DENSITY_WEIGHT * density_penalty
        + EIGHT_STATE_WEIGHT * rec.eight_state_score
    )


def score_fine_selection(
    records: list[FunnelSymbolRecord],
    *,
    top_n: int = DEFAULT_TOP_N,
    degraded: bool = False,
) -> FineSelectionResult:
    """六要素综合评分 → 横截面 Z-score 标准化 → 降序取 Top-N。

    Z-score：std=0（全体同分）时全部置 0（无区分度，按 raw 降序兜底排名）。
    top_n<=0 或空输入 → 空结果。
    """
    if not records or top_n <= 0:
        return FineSelectionResult(top=(), degraded=degraded)
    raws = {r.symbol: _composite_raw_score(r, degraded=degraded) for r in records}
    values = list(raws.values())
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    std = math.sqrt(var)
    zs = {
        s: (0.0 if std < 1e-12 else (v - mean) / std) for s, v in raws.items()
    }
    ordered = sorted(raws, key=lambda s: (zs[s], raws[s]), reverse=True)[:top_n]
    top = tuple(
        ScoredSymbol(symbol=s, raw_score=raws[s], z_score=zs[s], rank=i + 1)
        for i, s in enumerate(ordered)
    )
    return FineSelectionResult(top=top, degraded=degraded)


# ------------------------------------------------------------------
# 三级串联便捷入口
# ------------------------------------------------------------------
def run_selection_funnel(
    records: list[FunnelSymbolRecord],
    *,
    top_n: int = DEFAULT_TOP_N,
    graded_degraded: bool = False,
    screen_degraded: bool = False,
    score_degraded: bool = False,
) -> SelectionFunnelResult:
    """BM-SEL-16 → 17 → 18 盘前批处理串联。"""
    by_symbol = {r.symbol: r for r in records}
    graded = filter_graded_indicators(records, degraded=graded_degraded)
    stage2 = [by_symbol[s] for s in graded.kept]
    screened = screen_preliminary(stage2, degraded=screen_degraded)
    stage3 = [by_symbol[s] for s in screened.kept]
    scored = score_fine_selection(stage3, top_n=top_n, degraded=score_degraded)
    return SelectionFunnelResult(graded=graded, screened=screened, scored=scored)
