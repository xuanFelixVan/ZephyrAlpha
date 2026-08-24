# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.6
# [MODULE] zephyr.signal_fundamental.selection_funnel
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.selection_funnel_skeleton（MOD-SIG-086 共享骨架）
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
#   desc: 委托骨架 run_graded_exclusion；四排除机制——物理(涨跌停/停牌/ST)/门禁(上市<30天)/分级(成交额<500万、AUM≤100万经 extra_tier_checks 注入)/概率(弃庄>95%)；降级=仅排除涨跌停/停牌
# - id: A2
#   name: BM-SEL-17 五维初筛 screen_preliminary（~1200→~300）
#   desc: 委托骨架 run_preliminary_gates（不注入容量截断）；技术+量价+板块+主力+状态五维；降级=全量放行
# - id: A3
#   name: BM-SEL-18 六要素精筛评分 score_fine_selection（~300→~50）
#   desc: 委托骨架 run_fine_scoring（tie_break=stable 同分保持输入序）；密度扣分直取记录字段同式计算；降级=等权综合
# 层: 输出
# - id: O1
#   name: GradedFilterResult / PreliminaryScreenResult / FineSelectionResult
#   intro: 三级结果含保留/排除清单、排除归因、降级标记；Z-score 排名 Top-N 喂 sleeve 排序
# [/ALGO_FLOW]
"""选股漏斗三层级——基本面信号域薄适配层（21 号 memo §3.6，BM-SEL-16/17/18）。

SIGNAL-ARCH-001 归并裁定落地：层序/接口/数据流唯一真源为
zephyr.signal_ashare.selection_funnel_skeleton（MOD-SIG-086 共享骨架），
本模块只保留本域记录/结果类型、阈值常量与钩子装配，全部过滤/初筛/评分
执行委托骨架，对外公开 API 签名不变（既有调用方/测试零适配）。

本域注入特性：
- 涨跌停封死消费**预计算** is_limit_locked 布尔标记（A 股域为板块幅度自推导）。
- AUM≤100 万分级排除经骨架 extra_tier_checks 注入（位于成交额与弃庄概率之间）。
- 密度扣分直取记录字段（neg_skewness×10 + excess_kurtosis×5 + forward_var_pct）。
- 精筛同分保持输入序（骨架 tie_break="stable"）。

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

from dataclasses import dataclass, field
from operator import attrgetter
from typing import Final

from zephyr.signal_ashare.selection_funnel_skeleton import (
    FineScoreHooks,
    FineScoreWeights,
    GradedExclusionHooks,
    GradedFilterThresholds,
    PreliminaryGateHooks,
    PreliminaryThresholds,
    run_fine_scoring,
    run_funnel_chain,
    run_graded_exclusion,
    run_preliminary_gates,
)

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
# 本域钩子/阈值装配（骨架注入件，模块级单例）
# ------------------------------------------------------------------
_SYMBOL_OF: Final = attrgetter("symbol")

_GRADED_THRESHOLDS: Final = GradedFilterThresholds(
    new_stock_min_list_days=NEW_STOCK_MIN_LIST_DAYS,
    min_avg_daily_amount=MIN_AVG_DAILY_AMOUNT,
    dealer_abandon_prob_max=DEALER_ABANDON_PROB_MAX,
)

_GRADED_HOOKS: Final = GradedExclusionHooks(
    is_limit_locked=attrgetter("is_limit_locked"),  # 预计算布尔标记（区别于 A 股域板块幅度自推导）
    is_suspended=attrgetter("is_suspended"),
    is_st=attrgetter("is_st"),
    list_days=attrgetter("list_days"),
    avg_daily_amount=attrgetter("avg_daily_amount"),
    dealer_abandon_prob=attrgetter("dealer_abandon_prob"),
    extra_tier_checks=(
        lambda rec: "tier:low_aum" if rec.aum <= MIN_AUM else None,  # 本域特有 AUM 分级排除
    ),
)

_SCREEN_THRESHOLDS: Final = PreliminaryThresholds(
    volume_ratio_min=VOLUME_RATIO_MIN,
    turnover_rate_min_pct=TURNOVER_RATE_MIN_PCT,
    sector_rank_max_pct=SECTOR_STRENGTH_RANK_MAX_PCT,
)

_SCREEN_HOOKS: Final = PreliminaryGateHooks(
    technical_pass=attrgetter("technical_pass"),
    volume_ratio=attrgetter("volume_ratio"),
    turnover_rate_pct=attrgetter("turnover_rate_pct"),
    sector_strength_rank_pct=attrgetter("sector_strength_rank_pct"),
    main_force_pass=attrgetter("main_force_pass"),
    market_state_pass=attrgetter("market_state_pass"),
)

_SCORE_WEIGHTS: Final = FineScoreWeights(
    value=BASE_SCORE_WEIGHTS["value"],
    momentum=BASE_SCORE_WEIGHTS["momentum"],
    quality=BASE_SCORE_WEIGHTS["quality"],
    sentiment=BASE_SCORE_WEIGHTS["sentiment"],
    regime_shift_max=REGIME_SHIFT_MAX,
    main_force=MAIN_FORCE_WEIGHT,
    crowding=CROWDING_WEIGHT,
    density=DENSITY_WEIGHT,
    eight_state=EIGHT_STATE_WEIGHT,
)

_SCORE_HOOKS: Final = FineScoreHooks(
    base_value_score=attrgetter("base_value_score"),
    base_momentum_score=attrgetter("base_momentum_score"),
    base_quality_score=attrgetter("base_quality_score"),
    base_sentiment_score=attrgetter("base_sentiment_score"),
    regime_shift=attrgetter("regime_shift"),
    main_force_score=attrgetter("main_force_score"),
    crowding_score=attrgetter("crowding_score"),
    density_penalty=lambda rec: rec.neg_skewness * 10.0 + rec.excess_kurtosis * 5.0 + rec.forward_var_pct,
    eight_state_score=attrgetter("eight_state_score"),
)


def _wrap_scored(items: tuple) -> tuple[ScoredSymbol, ...]:
    """骨架 ScoredItem → 本域 ScoredSymbol 包装。"""
    return tuple(ScoredSymbol(symbol=t.symbol, raw_score=t.raw_score, z_score=t.z_score, rank=t.rank) for t in items)


# ------------------------------------------------------------------
# BM-SEL-16 分级指标过滤（~7000→~1200）——委托骨架
# ------------------------------------------------------------------
def filter_graded_indicators(
    records: list[FunnelSymbolRecord],
    *,
    degraded: bool = False,
) -> GradedFilterResult:
    """四排除机制批处理过滤。只排除不评分，廉价规则先砍量。

    degraded=True（过滤模块未就绪）：仅排除涨跌停/停牌，其余放行。
    """
    out = run_graded_exclusion(
        records,
        symbol_of=_SYMBOL_OF,
        hooks=_GRADED_HOOKS,
        thresholds=_GRADED_THRESHOLDS,
        degraded=degraded,
    )
    return GradedFilterResult(kept=out.kept, excluded=out.excluded, degraded=degraded)


# ------------------------------------------------------------------
# BM-SEL-17 五维初筛（~1200→~300）——委托骨架（不注入容量截断）
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
    out = run_preliminary_gates(
        records,
        symbol_of=_SYMBOL_OF,
        hooks=_SCREEN_HOOKS,
        thresholds=PreliminaryThresholds(
            volume_ratio_min=volume_ratio_min,
            turnover_rate_min_pct=turnover_rate_min_pct,
            sector_rank_max_pct=sector_rank_max_pct,
        ),
        degraded=degraded,
    )
    return PreliminaryScreenResult(kept=out.kept, excluded=out.excluded, degraded=degraded)


# ------------------------------------------------------------------
# BM-SEL-18 六要素精筛评分（~300→~50）——委托骨架（tie_break=stable）
# ------------------------------------------------------------------
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
    items = run_fine_scoring(
        records,
        symbol_of=_SYMBOL_OF,
        hooks=_SCORE_HOOKS,
        weights=_SCORE_WEIGHTS,
        top_n=top_n,
        degraded=degraded,
        tie_break="stable",
    )
    return FineSelectionResult(top=_wrap_scored(items), degraded=degraded)


# ------------------------------------------------------------------
# 三级串联便捷入口——委托骨架 run_funnel_chain
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
    chain = run_funnel_chain(
        records,
        symbol_of=_SYMBOL_OF,
        run_graded=lambda recs: run_graded_exclusion(
            recs,
            symbol_of=_SYMBOL_OF,
            hooks=_GRADED_HOOKS,
            thresholds=_GRADED_THRESHOLDS,
            degraded=graded_degraded,
        ),
        run_screen=lambda recs: run_preliminary_gates(
            recs,
            symbol_of=_SYMBOL_OF,
            hooks=_SCREEN_HOOKS,
            thresholds=_SCREEN_THRESHOLDS,
            degraded=screen_degraded,
        ),
        run_score=lambda recs: run_fine_scoring(
            recs,
            symbol_of=_SYMBOL_OF,
            hooks=_SCORE_HOOKS,
            weights=_SCORE_WEIGHTS,
            top_n=top_n,
            degraded=score_degraded,
            tie_break="stable",
        ),
    )
    return SelectionFunnelResult(
        graded=GradedFilterResult(kept=chain.graded.kept, excluded=chain.graded.excluded, degraded=graded_degraded),
        screened=PreliminaryScreenResult(kept=chain.screened.kept, excluded=chain.screened.excluded, degraded=screen_degraded),
        scored=FineSelectionResult(top=_wrap_scored(chain.scored), degraded=score_degraded),
    )
