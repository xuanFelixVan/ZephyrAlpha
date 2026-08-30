# [BLUEPRINT] MOD-SIG-086 | docs/03_modules/_domain_signal/selection_funnel_skeleton/blueprint.md
# [MODULE] zephyr.signal_ashare.selection_funnel_skeleton
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.signal_fundamental.selection_funnel; zephyr.signal_ashare.tiered_screening_filter
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 漏斗单调收敛：各层 kept ⊆ 输入；一层只排除不评分/三层只评分不排除；降级语义骨架统一（一层仅物理排除、二层全量放行、三层等权综合）；纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] capacity.target<=0 → ValueError（降级路径同效）；tie_break 非法值 → ValueError；密度摘要鸭子类型缺字段 → AttributeError 由调用方（装配层）兜底
# [TESTS] tests/signal_ashare/test_selection_funnel_skeleton.py
# [A_module] module_id=MOD-SIG-086 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 漏斗候选标的记录（泛型 RecT）
#   fields: 字段语义不固化——符号/物理标记/门禁/流动性/五维初筛/六要素评分全部经钩子闭包注入
# 层: 算法
# - id: A1
#   name: BM-SEL-16 run_graded_exclusion（~7000→~1200）
#   desc: 物理排除(涨跌停封死/停牌/ST)→门禁排除(次新<N天)→分级排除(日均成交额+extra_tier_checks 注入位)→概率排除(弃庄)；降级=仅物理排除
# - id: A2
#   name: BM-SEL-17 run_preliminary_gates（~1200→~300）
#   desc: 五维门槛初筛(技术/量比/换手/板块排名/主力/状态)+可选 CapacityTruncation 容量截断（liquidity_score 降序、同分 symbol 字典序）；降级=全量放行
# - id: A3
#   name: BM-SEL-18 run_fine_scoring（~300→~50）
#   desc: 六要素合成(基础四维×(1+状态偏移截断)+主力−拥挤−密度钩子+8态) → 横截面 Z-score → tie_break(stable/symbol) Top-N；降级=等权综合
# - id: A4
#   name: run_funnel_chain 三层串联
#   desc: 层序与数据流唯一真源：kept 子集逐层传递（graded→screened→scored）
# 层: 输出
# - id: O1
#   name: ExclusionOutcome / GateOutcome / ScoredItem / FunnelChainResult
#   intro: 域适配层把骨架输出包装为本域结果类型（kept/excluded/degraded/truncated/raw/z/rank）
# [/ALGO_FLOW]
"""
选股漏斗共享骨架（MOD-SIG-086，SIGNAL-ARCH-001 归并裁定落地）。

21 号 memo §3.6（BM-SEL-16/17/18，容量链 ~7000→~1200→~300→~50）四层容量链的
层序、接口与数据流唯一真源。双域原实现（signal_fundamental/selection_funnel.py
与 signal_ashare/tiered_screening_filter.py）改为薄适配层：委托本骨架 + 注入
本域参数/钩子，对外 API 签名不变。

域特性注入位（不丢特性）：
- 板块幅度自推导（A 股域）：第一层 is_limit_locked 钩子以闭包注入
  （board→limit_pct→close/prev_close 推导），骨架不感知板块枚举。
- 容量截断（A 股域 MOD-SIG-047 语义）：第二层 capacity=CapacityTruncation(
  target, liquidity_score_of) 参数注入；不传则不截断（fundamental 语义）。
- 密度鸭子类型（A 股域 MOD-SIG-048 语义）：第三层 density_penalty 钩子注入，
  density_penalty_from_summary 提供鸭子类型摘要（neg_skewness/excess_kurtosis/
  forward_var_pct，None→0）的规范取法，骨架不 import 密度预测实现。
- fundamental 特有：AUM 分级排除经 extra_tier_checks 注入（位于成交额与弃庄
  概率之间）；精筛同分保持输入序（tie_break="stable"，A 股域 048 为 "symbol"）。

降级链路（memo 既定）：一层未就绪→仅物理排除；二层未就绪→全量放行；
三层未就绪→等权综合评分。执行频率按 memo v1.1.19：盘前批处理，盘中不滚动。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: records 参数
#   fields: 参数 records，类型注解 Sequence[RecT]
#   code: selection_funnel_skeleton.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: symbol_of 参数
#   fields: 参数 symbol_of（无注解）
#   code: selection_funnel_skeleton.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: hooks 参数
#   fields: 参数 hooks（无注解）
#   code: selection_funnel_skeleton.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: thresholds 参数
#   fields: 参数 thresholds（无注解）
#   code: selection_funnel_skeleton.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① run_graded_exclusion
#   name_en: run_graded_exclusion
#   intro: 四排除机制批处理过滤（~7000→~1200）。
#   desc: 四排除机制批处理过滤（~7000→~1200）。只排除不评分，廉价规则先砍量。 排除优先级（先命中先生效）：物理排除（涨跌停封死/停牌/ST）→ 门禁排除（次新） → 分级排除（…；源码 L256-L309
#   inputs: records symbol_of hooks thresholds degraded
#   outputs: ExclusionOutcome
# - id: A2
#   name_zh: ② run_preliminary_gates
#   name_en: run_preliminary_gates
#   intro: 五维门槛初筛 + 可选容量收敛（~1200→~300）。
#   desc: 五维门槛初筛 + 可选容量收敛（~1200→~300）。 五维顺序执行（先命中先排除）：技术 → 量比 → 换手率 → 板块排名 → 主力 → 状态。 degraded=True…；源码 L348-L397
#   inputs: records symbol_of hooks thresholds capacity degraded
#   outputs: GateOutcome
# - id: A3
#   name_zh: ③ density_penalty_from_summary
#   name_en: density_penalty_from_summary
#   intro: 密度要素扣分项规范取法 = 负偏度幅度×10 + 超额峰度×5 + 前瞻 VaR 幅度%（memo §3.6 ③）。
#   desc: 密度要素扣分项规范取法 = 负偏度幅度×10 + 超额峰度×5 + 前瞻 VaR 幅度%（memo §3.6 ③）。 鸭子类型消费：任何带 neg_skewness / exce…；源码 L442-L453
#   inputs: density
#   outputs: float
# - id: A4
#   name_zh: ④ run_fine_scoring
#   name_en: run_fine_scoring
#   intro: 六要素综合评分 → 横截面 Z-score 标准化 → 降序取 Top-N（~300→~50）。
#   desc: 六要素综合评分 → 横截面 Z-score 标准化 → 降序取 Top-N（~300→~50）。 Z-score：std≈0（全体同分）时 Z 全部置 0（无区分度，按 raw…；源码 L482-L516
#   inputs: records symbol_of hooks weights top_n degraded tie_break
#   outputs: tuple[ScoredItem, ...]
# - id: A5
#   name_zh: ⑤ subset_by_kept
#   name_en: subset_by_kept
#   intro: 按上一层 kept 清单取记录子集（保持 kept 顺序；同名标的后出现记录覆盖）。
#   desc: 按上一层 kept 清单取记录子集（保持 kept 顺序；同名标的后出现记录覆盖）。；源码 L522-L530
#   inputs: records symbol_of kept
#   outputs: list[RecT]
# - id: A6
#   name_zh: ⑥ run_funnel_chain
#   name_en: run_funnel_chain
#   intro: BM-SEL-16 → 17 → 18 盘前批处理串联（层序/数据流骨架）。
#   desc: BM-SEL-16 → 17 → 18 盘前批处理串联（层序/数据流骨架）。 各层执行体由域适配层以 partial/闭包注入（绑定本域钩子、阈值与降级标记）； 骨架只保证层序与…；源码 L533-L550
#   inputs: records symbol_of run_graded run_screen run_score
#   outputs: FunnelChainResult
#   （注：A6 之后另有 11 个公共定义未列入（含 11 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ExclusionOutcome
#   name_en: ExclusionOutcome
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.signal_fundamental.selection_funnel; zephyr.signal_ashare.tiered_screeni…
# - id: O2
#   name_zh: GateOutcome
#   name_en: GateOutcome
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.signal_fundamental.selection_funnel; zephyr.signal_ashare.tiered_screeni…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Final, Generic, TypeVar

__all__: Final = [
    "CapacityTruncation",
    "ExclusionOutcome",
    "FineScoreHooks",
    "FineScoreWeights",
    "FunnelChainResult",
    "GateOutcome",
    "GradedExclusionHooks",
    "GradedFilterThresholds",
    "PreliminaryGateHooks",
    "PreliminaryThresholds",
    "ScoredItem",
    "density_penalty_from_summary",
    "run_fine_scoring",
    "run_funnel_chain",
    "run_graded_exclusion",
    "run_preliminary_gates",
    "subset_by_kept",
]

RecT = TypeVar("RecT")

#: Z-score 标准差退化阈值（全体同分 → 无区分度，Z 置 0 按 raw 兜底排名）
_STD_EPS: Final = 1e-12
#: 精筛 tie_break 合法口径：stable=同分保持输入序（fundamental 语义）；symbol=同分按代码字典序（A 股域语义）
_TIE_BREAKS: Final = ("stable", "symbol")


# ------------------------------------------------------------------
# 共享结果类型（骨架输出；域适配层负责包装为本域结果）
# ------------------------------------------------------------------
@dataclass(frozen=True)
class ExclusionOutcome:
    """第一层输出：保留清单 + 排除归因。"""

    kept: tuple[str, ...]
    excluded: dict[str, str] = field(default_factory=dict)  # {symbol: 排除原因}


@dataclass(frozen=True)
class GateOutcome:
    """第二层输出：保留清单 + 排除归因 + 容量截断标记。"""

    kept: tuple[str, ...]
    excluded: dict[str, str] = field(default_factory=dict)
    truncated: bool = False  # True=通过数超容量目标已截断（被截断标的不计入 excluded）


@dataclass(frozen=True)
class ScoredItem:
    """第三层单标的评分结果。"""

    symbol: str
    raw_score: float  # 六要素合成原始分
    z_score: float  # 横截面 Z-score 标准化分
    rank: int  # 降序排名（1 起）


@dataclass(frozen=True)
class FunnelChainResult:
    """漏斗三层串联输出（骨架级；域适配层包装为本域链式结果）。"""

    graded: ExclusionOutcome
    screened: GateOutcome
    scored: tuple[ScoredItem, ...]


# ------------------------------------------------------------------
# BM-SEL-16 第一层：分级指标排除（阈值 + 钩子注入）
# ------------------------------------------------------------------
@dataclass(frozen=True)
class GradedFilterThresholds:
    """第一层排除阈值（21 号 memo §3.6 ① 契约值，G09 校准前初拟）。"""

    new_stock_min_list_days: int = 30  # 门禁排除：次新上市 <N 天绝对排除
    min_avg_daily_amount: float = 5_000_000.0  # 分级排除：日均成交额 <N 元剔除
    dealer_abandon_prob_max: float = 0.95  # 概率排除：庄家弃庄概率 >N 剔除


@dataclass(frozen=True)
class GradedExclusionHooks(Generic[RecT]):
    """第一层字段语义钩子（域适配层以闭包/attrgetter 注入）。

    is_limit_locked 为板块幅度自推导注入位：A 股域注入
    ``is_limit_locked_price(close, prev_close, limit_pct_for(board, is_st=...), eps=...) is True``
    闭包（状态不明 None→不排除）；fundamental 域直取预计算布尔字段。
    extra_tier_checks 为附加分级排除注入位（位于成交额排除之后、弃庄概率排除之前），
    每项返回排除原因或 None（fundamental 域注入 AUM 排除）。
    """

    is_limit_locked: Callable[[RecT], bool]
    is_suspended: Callable[[RecT], bool]
    is_st: Callable[[RecT], bool]
    list_days: Callable[[RecT], int]
    avg_daily_amount: Callable[[RecT], float]
    dealer_abandon_prob: Callable[[RecT], float]
    extra_tier_checks: tuple[Callable[[RecT], str | None], ...] = ()


def run_graded_exclusion(
    records: Sequence[RecT],
    *,
    symbol_of: Callable[[RecT], str],
    hooks: GradedExclusionHooks[RecT],
    thresholds: GradedFilterThresholds,
    degraded: bool = False,
) -> ExclusionOutcome:
    """四排除机制批处理过滤（~7000→~1200）。只排除不评分，廉价规则先砍量。

    排除优先级（先命中先生效）：物理排除（涨跌停封死/停牌/ST）→ 门禁排除（次新）
    → 分级排除（成交额 → extra_tier_checks）→ 概率排除（弃庄）。
    degraded=True：仅排除涨跌停封死/停牌，其余放行（memo 既定降级路径）。
    """
    kept: list[str] = []
    excluded: dict[str, str] = {}
    for rec in records:
        sym = symbol_of(rec)
        # 物理排除（降级路径也保留：涨跌停封死/停牌硬剔除）
        if hooks.is_limit_locked(rec):
            excluded[sym] = "physical:limit_locked"
            continue
        if hooks.is_suspended(rec):
            excluded[sym] = "physical:suspended"
            continue
        if degraded:
            kept.append(sym)
            continue
        if hooks.is_st(rec):
            excluded[sym] = "physical:st"
            continue
        # 门禁排除
        list_days = hooks.list_days(rec)
        if list_days < thresholds.new_stock_min_list_days:
            excluded[sym] = f"gate:new_stock({list_days}d<{thresholds.new_stock_min_list_days}d)"
            continue
        # 分级排除（流动性失效保护）
        if hooks.avg_daily_amount(rec) < thresholds.min_avg_daily_amount:
            excluded[sym] = "tier:low_amount"
            continue
        tier_reason: str | None = None
        for check in hooks.extra_tier_checks:
            tier_reason = check(rec)
            if tier_reason is not None:
                break
        if tier_reason is not None:
            excluded[sym] = tier_reason
            continue
        # 概率排除
        if hooks.dealer_abandon_prob(rec) > thresholds.dealer_abandon_prob_max:
            excluded[sym] = "prob:dealer_abandon"
            continue
        kept.append(sym)
    return ExclusionOutcome(kept=tuple(kept), excluded=excluded)


# ------------------------------------------------------------------
# BM-SEL-17 第二层：五维初筛 + 可选容量截断
# ------------------------------------------------------------------
@dataclass(frozen=True)
class PreliminaryThresholds:
    """第二层初筛阈值（21 号 memo §3.6 ② 契约值，G09 校准前初拟）。"""

    volume_ratio_min: float = 1.5  # 量比下限（>1.5 为放量关注线）
    turnover_rate_min_pct: float = 0.0  # 换手率下限（%，memo 未定值默认 0=不强制）
    sector_rank_max_pct: float = 0.30  # 板块强度排名前百分位上限（前 30%）


@dataclass(frozen=True)
class PreliminaryGateHooks(Generic[RecT]):
    """第二层五维字段语义钩子。"""

    technical_pass: Callable[[RecT], bool]  # 技术形态初筛（BM-SEL-02）
    volume_ratio: Callable[[RecT], float]  # 量比
    turnover_rate_pct: Callable[[RecT], float]  # 换手率（%）
    sector_strength_rank_pct: Callable[[RecT], float]  # 板块强度排名前百分位 [0,1]（0=最强）
    main_force_pass: Callable[[RecT], bool]  # C-011 主力阶段（BM-SEL-05）
    market_state_pass: Callable[[RecT], bool]  # C-021 市场状态（BM-SEL-03）


@dataclass(frozen=True)
class CapacityTruncation(Generic[RecT]):
    """容量截断注入件（A 股域 MOD-SIG-047 语义；不注入则不截断）。

    通过数超过 target 时按 liquidity_score 降序截断（同分 symbol 字典序保证
    确定性），被截断标的不计入 excluded（非规则排除）。
    """

    target: int  # 漏斗容量目标（~300）
    liquidity_score_of: Callable[[RecT], float]  # 流动性综合分（越大越优先保留）


def run_preliminary_gates(
    records: Sequence[RecT],
    *,
    symbol_of: Callable[[RecT], str],
    hooks: PreliminaryGateHooks[RecT],
    thresholds: PreliminaryThresholds,
    capacity: CapacityTruncation[RecT] | None = None,
    degraded: bool = False,
) -> GateOutcome:
    """五维门槛初筛 + 可选容量收敛（~1200→~300）。

    五维顺序执行（先命中先排除）：技术 → 量比 → 换手率 → 板块排名 → 主力 → 状态。
    degraded=True（初筛未就绪）：全量放行进精筛（算力风险告警由调用方负责）。
    capacity.target<=0 → ValueError（降级路径同效，与 MOD-SIG-047 口径一致）。
    """
    if capacity is not None and capacity.target <= 0:
        raise ValueError(f"capacity_target 必须为正: {capacity.target}")
    if degraded:
        return GateOutcome(kept=tuple(symbol_of(r) for r in records))
    kept_records: list[RecT] = []
    excluded: dict[str, str] = {}
    for rec in records:
        sym = symbol_of(rec)
        if not hooks.technical_pass(rec):
            excluded[sym] = "dim:technical"
            continue
        volume_ratio = hooks.volume_ratio(rec)
        if volume_ratio <= thresholds.volume_ratio_min:
            excluded[sym] = f"dim:volume_ratio({volume_ratio:.2f}<={thresholds.volume_ratio_min})"
            continue
        if hooks.turnover_rate_pct(rec) < thresholds.turnover_rate_min_pct:
            excluded[sym] = "dim:turnover_rate"
            continue
        if hooks.sector_strength_rank_pct(rec) > thresholds.sector_rank_max_pct:
            excluded[sym] = "dim:sector_rank"
            continue
        if not hooks.main_force_pass(rec):
            excluded[sym] = "dim:main_force"
            continue
        if not hooks.market_state_pass(rec):
            excluded[sym] = "dim:market_state"
            continue
        kept_records.append(rec)
    truncated = False
    if capacity is not None and len(kept_records) > capacity.target:
        kept_records = sorted(kept_records, key=lambda r: (-capacity.liquidity_score_of(r), symbol_of(r)))[
            : capacity.target
        ]
        truncated = True
    return GateOutcome(kept=tuple(symbol_of(r) for r in kept_records), excluded=excluded, truncated=truncated)


# ------------------------------------------------------------------
# BM-SEL-18 第三层：六要素精筛评分
# ------------------------------------------------------------------
@dataclass(frozen=True)
class FineScoreWeights:
    """六要素合成权重（memo §3.6 ③ 契约值；主力/拥挤为经验初值，G09 校准）。

    eight_state=0.0：8 态修正按 90 号 §7 暂缓裁定置 0 不参与（等效五要素），
    重评条件满足后恢复接入。
    """

    value: float = 0.40
    momentum: float = 0.30
    quality: float = 0.20
    sentiment: float = 0.10
    regime_shift_max: float = 0.10  # 状态偏移修正截断幅度（±10%，C-021）
    main_force: float = 0.20  # 主力评分合成权重（C-034/C-035）
    crowding: float = 0.10  # 拥挤度扣分权重（C-045）
    density: float = 0.15  # 密度要素扣分权重（memo 定值 15%）
    eight_state: float = 0.0  # 8 态修正（90 号 §7 暂缓 → 0.0）


@dataclass(frozen=True)
class FineScoreHooks(Generic[RecT]):
    """第三层字段语义钩子。

    density_penalty 为密度鸭子类型注入位：A 股域注入
    ``lambda rec: density_penalty_from_summary(rec.density)``（鸭子类型消费密度摘要，
    与 conditional_density_predictor 解耦）；fundamental 域注入直取字段同式计算。
    """

    base_value_score: Callable[[RecT], float]  # 价值分（0-100）
    base_momentum_score: Callable[[RecT], float]  # 动量分
    base_quality_score: Callable[[RecT], float]  # 质量分
    base_sentiment_score: Callable[[RecT], float]  # 情绪分
    regime_shift: Callable[[RecT], float]  # 状态偏移修正（合成前截断 ±regime_shift_max）
    main_force_score: Callable[[RecT], float]  # 主力评分
    crowding_score: Callable[[RecT], float]  # 拥挤度（越高越扣分）
    density_penalty: Callable[[RecT], float]  # 密度要素扣分项（≥0，越高越扣分）
    eight_state_score: Callable[[RecT], float] = lambda rec: 0.0  # 8 态修正（暂缓，默认 0）


def density_penalty_from_summary(density: Any) -> float:
    """密度要素扣分项规范取法 = 负偏度幅度×10 + 超额峰度×5 + 前瞻 VaR 幅度%（memo §3.6 ③）。

    鸭子类型消费：任何带 neg_skewness / excess_kurtosis / forward_var_pct 三属性的
    摘要对象均可（BM-SEL-13 conditional_density_predictor 的分布派生量是其一），
    骨架不 import 密度预测实现，保持漏斗层与模型层解耦。
    density 为 None 时返回 0.0（密度预测未就绪 → 密度要素不参与扣分，
    与 memo"8 态置 0"同构的缺省处理）；缺字段 → AttributeError（装配层职责）。
    """
    if density is None:
        return 0.0
    return float(density.neg_skewness) * 10.0 + float(density.excess_kurtosis) * 5.0 + float(density.forward_var_pct)


def _composite_score(rec: RecT, *, hooks: FineScoreHooks[RecT], weights: FineScoreWeights, degraded: bool) -> float:
    """六要素合成原始分。degraded=True → 等权综合（四维基础分+主力五维等权）。"""
    if degraded:
        return (
            hooks.base_value_score(rec)
            + hooks.base_momentum_score(rec)
            + hooks.base_quality_score(rec)
            + hooks.base_sentiment_score(rec)
            + hooks.main_force_score(rec)
        ) / 5.0
    base = (
        weights.value * hooks.base_value_score(rec)
        + weights.momentum * hooks.base_momentum_score(rec)
        + weights.quality * hooks.base_quality_score(rec)
        + weights.sentiment * hooks.base_sentiment_score(rec)
    )
    shift = max(-weights.regime_shift_max, min(weights.regime_shift_max, hooks.regime_shift(rec)))
    return (
        base * (1.0 + shift)
        + weights.main_force * hooks.main_force_score(rec)
        - weights.crowding * hooks.crowding_score(rec)
        - weights.density * hooks.density_penalty(rec)
        + weights.eight_state * hooks.eight_state_score(rec)
    )


def run_fine_scoring(
    records: Sequence[RecT],
    *,
    symbol_of: Callable[[RecT], str],
    hooks: FineScoreHooks[RecT],
    weights: FineScoreWeights,
    top_n: int = 50,
    degraded: bool = False,
    tie_break: str = "stable",
) -> tuple[ScoredItem, ...]:
    """六要素综合评分 → 横截面 Z-score 标准化 → 降序取 Top-N（~300→~50）。

    Z-score：std≈0（全体同分）时 Z 全部置 0（无区分度，按 raw 降序兜底排名）。
    top_n<=0 或空输入 → 空结果。同名标的按后出现记录覆盖（两域原实现同口径）。
    tie_break：stable=同分保持输入序（fundamental 语义）；symbol=同分按标的代码
    字典序（A 股域 MOD-SIG-048 语义）。
    """
    if tie_break not in _TIE_BREAKS:
        raise ValueError(f"非法 tie_break: {tie_break!r}（合法值: {list(_TIE_BREAKS)}）")
    if not records or top_n <= 0:
        return ()
    raws: dict[str, float] = {}
    for rec in records:
        raws[symbol_of(rec)] = _composite_score(rec, hooks=hooks, weights=weights, degraded=degraded)
    values = list(raws.values())
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    std = math.sqrt(var)
    zs = {s: (0.0 if std < _STD_EPS else (v - mean) / std) for s, v in raws.items()}
    if tie_break == "symbol":
        ordered = sorted(raws, key=lambda s: (-zs[s], -raws[s], s))[:top_n]
    else:
        position = {s: i for i, s in enumerate(raws)}
        ordered = sorted(raws, key=lambda s: (-zs[s], -raws[s], position[s]))[:top_n]
    return tuple(ScoredItem(symbol=s, raw_score=raws[s], z_score=zs[s], rank=i + 1) for i, s in enumerate(ordered))


# ------------------------------------------------------------------
# 三层串联：层序与数据流唯一真源
# ------------------------------------------------------------------
def subset_by_kept(
    records: Sequence[RecT],
    *,
    symbol_of: Callable[[RecT], str],
    kept: Sequence[str],
) -> list[RecT]:
    """按上一层 kept 清单取记录子集（保持 kept 顺序；同名标的后出现记录覆盖）。"""
    by_symbol = {symbol_of(r): r for r in records}
    return [by_symbol[s] for s in kept]


def run_funnel_chain(
    records: Sequence[RecT],
    *,
    symbol_of: Callable[[RecT], str],
    run_graded: Callable[[list[RecT]], ExclusionOutcome],
    run_screen: Callable[[list[RecT]], GateOutcome],
    run_score: Callable[[list[RecT]], tuple[ScoredItem, ...]],
) -> FunnelChainResult:
    """BM-SEL-16 → 17 → 18 盘前批处理串联（层序/数据流骨架）。

    各层执行体由域适配层以 partial/闭包注入（绑定本域钩子、阈值与降级标记）；
    骨架只保证层序与 kept 子集逐层传递的数据流契约。
    """
    stage1 = list(records)
    graded = run_graded(stage1)
    screened = run_screen(subset_by_kept(stage1, symbol_of=symbol_of, kept=graded.kept))
    scored = run_score(subset_by_kept(stage1, symbol_of=symbol_of, kept=screened.kept))
    return FunnelChainResult(graded=graded, screened=screened, scored=scored)
