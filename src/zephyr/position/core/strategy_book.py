# [BLUEPRINT] MOD-POS-020 | docs/03_modules/_domain_position/strategy_book/blueprint.md
# [MODULE] zephyr.position.core.strategy_book
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.core.drawdown_controller; zephyr.position.core.capital_curve_manager
# [CONSUMERS] MOD-POS-021(FirmRiskAggregator消费TargetPortfolio); MOD-PA-007(RegimeMetaAllocator收PerformanceScore反馈)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] total_weight≤budget(粗仓位不经Kelly); sizing_method∈{equal_weight,risk_parity,custom}禁用Kelly/MVO; 策略不知道市场态只收budget数字; rebalance_to_budget必须返回适配portfolio(策略不能说"我不卖"); DrawdownProtocol四级回撤触发独立收缩; target_portfolio权重口径=相对strategy_budget占比(非绝对总资金权重); σ_i异常(缺失/样本<30/>150%/上市<60日)→该标的部分降级等权w=1/N(31号§2.2.2,其余标的仍inverse-vol)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] StrategySelectionError(ZA-POS-0020); BudgetExceededError(ZA-POS-0021); RebalanceRefusedError(ZA-POS-0022)
# [TESTS] tests/position/test_strategy_book.py
# [A_module] module_id=MOD-POS-020 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
StrategyBook — 独立策略账本 (MOD-POS-020)

A 模型（30_multi_strategy_concurrency §2.1）的核心实体。每个策略是一个自洽的 StrategyBook，
自带选股 + 粗仓位（等权/risk parity，**不用 Kelly，不用 MVO**）+ 独立风控，
输出 target_portfolio（标的 + 目标权重）。

分层边界（方案 A，2026-08-06）：
    策略层 StrategyBook（本模块）—— 选股 + 粗仓位
    组合汇总层 FirmRiskAggregator (MOD-POS-021) —— 求和 + 组合级硬裁剪
    组合裁决层 MOD-POS-001 position_sizing_engine —— Kelly + 13 约束

数据流：StrategyBook → FirmRiskAggregator → MOD-POS-001 → 下单

不做什么：Kelly 精裁（归 MOD-POS-001）/ 组合级约束（归 MOD-POS-021）/
         MVO（30_multi_strategy_concurrency §3.1 拒绝）/ 知道市场态（只收 budget 数字）

权重口径声明（30号 v2.2.0 链路6缺口1修复）：
    target_portfolio 中每个 target_weight 是**相对 strategy_budget 的占比**
    （非相对总资金的绝对权重）。FirmRiskAggregator §2.2 据此做 budget 口径归一化：
    account_weight = tp_weight × budget_used / total_budget。
    若误输出绝对权重将导致 32号 double-count。

依据: 30_multi_strategy_concurrency §2.2/§2.4/§2.5 + blueprint §2.3
SSoT: depgraph MOD-POS-020
Version: 1.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: alpha 选股信号 alpha_signals
#   fields: 策略 specific 信号字典（子类定义格式）
#   code: build_target_portfolio L294
# - id: I2
#   name: 波动率输入 volatility_data
#   fields: symbol → 年化波动率 float 或 VolatilityInfo(sigma/valid_samples/listing_days)
#   code: VolatilityInfo L159
# - id: I3
#   name: 资金预算 budget（RegimeMetaAllocator 分配）+ 策略 PnL 历史 + 情绪周期信号
#   fields: budget 占比 / pnl 日收益序列 / SentimentStageSignal(stage/confidence/retreat_weight)
#   code: build_target_portfolio L294
# 层: 特征
# - id: F1
#   name_zh: inverse-vol 权重
#   name_en: inverse_vol_weight
#   intro: w_i=(1/σ_i)/Σ(1/σ_j)，只估 σ 不估协方差（30号 §3.1 拒绝 MVO）
#   formula: w_i = budget × (1/σ_i) / Σ_j(1/σ_j)，σ_i=60日年化波动率
#   code: _size_risk_parity L628
#   registry: 无
# - id: F2
#   name_zh: σ_i 异常判定 4 检查链
#   name_en: sigma_anomaly_check
#   intro: 任一触发→该标的部分降级等权（缺失/样本<30/年化>150%/上市<60日），非阻断
#   formula: σ∈{NaN,None,≤0} ∨ valid_samples<30 ∨ σ>1.50 ∨ listing_days<60 → 降级
#   code: _is_vol_anomaly L699
#   registry: 无
# - id: F3
#   name_zh: 60 日滚动 Sortino 绩效分
#   name_en: performance_score
#   intro: Sortino→[0.5,1.5] 线性映射，供 RegimeMetaAllocator 后验分配
#   formula: Sortino=mean(excess)×252/(downside_dev×√252) → clip([0.5,1.5])
#   code: compute_performance_score L474
#   registry: 无
# 层: 算法
# - id: A1
#   name_zh: 粗仓位三段流水线
#   name_en: sizing_pipeline
#   intro: 选股→粗仓位(等权/inverse-vol)→回撤Protocol缩放→budget裁剪
#   formula: positions=size_positions(selected)→×L1/L2 scalar→pro-rata clip(Σ≤budget)
#   code: build_target_portfolio L294
# - id: A2
#   name_zh: σ_i 异常部分降级
#   name_en: partial_equal_weight_fallback
#   intro: 异常标的取等权份额 budget/N，正常标的按 inverse-vol 瓜分剩余 budget×N_ok/N
#   formula: w_bad=budget/N; w_ok=budget×(N_ok/N)×(1/σ_j)/Σ_ok(1/σ)
#   code: _size_risk_parity L628
# - id: A3
#   name_zh: 四级回撤 Protocol
#   name_en: drawdown_protocol
#   intro: 回撤>8/15/20/25% → L1缩放/L2减仓/L3停仓/L4清仓+强制休息5天
#   formula: dd≥0.08→×0.75新仓; dd≥0.15→×0.75全部; dd≥0.20→停新开; dd≥0.25→清仓+休息5日
#   code: _update_drawdown_level L776
# 层: 输出
# - id: O1
#   name: TargetPortfolio 策略目标组合（CTR-POS-020）
#   fields: strategy_id/positions(symbol→TargetWeight)/total_weight/budget/cash_ratio/sizing_method/idempotency_key
#   code: TargetPortfolio L185
#   consumers: MOD-POS-021 FirmRiskAggregator 求和→MOD-POS-001 Kelly 精裁决
# [/ALGO_FLOW]
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

# ── 常量（参数来源：30_multi_strategy_concurrency §2.5 + §2.2）──

# 四级回撤阈值（§2.5.1 行业基准 LedgerMind/ARKA/Sina FOF 2026）
DRAWDOWN_L1_WARN = 0.08       # Level 1 警告：回撤 > 8%
DRAWDOWN_L2_REDUCE = 0.15     # Level 2 减仓：回撤 > 15%
DRAWDOWN_L3_HALT = 0.20       # Level 3 停仓：回撤 > 20%
DRAWDOWN_L4_LIQUIDATE = 0.25  # Level 4 清仓：回撤 > 25%

# 各级别动作参数（§2.5.1）
L1_RISK_SCALAR = 0.75         # Level 1：新仓风险敞口降至 75%
L2_POSITION_SCALAR = 0.75     # Level 2：仓位缩减至 75%
# Level 3：停开新仓（仅允许平仓调仓）
# Level 4：关闭所有仓位 + 强制休息 5 天

# PerformanceScore 映射参数（§2.2 RegimeMetaAllocator 配套）
PERF_SCORE_FLOOR = 0.5        # PerformanceScore 下限（防饿死）
PERF_SCORE_CAP = 1.5          # PerformanceScore 上限（防集中）
PERF_SCORE_LOOKBACK = 60      # 60 日滚动 Sortino（§2.2 口径对齐 34号 §3.1）
# Sortino → [0.5, 1.5] 线性映射基准点
SORTINO_LOW = 0.0             # Sortino=0 → score=0.5
SORTINO_HIGH = 2.0            # Sortino≥2 → score=1.5

# 退潮加权系数默认值（28号 §3.5 → 30号 链路2）
RETREAT_WEIGHT_DEFAULT = 1.5
RETREAT_WEIGHT_BY_TYPE = {    # 按策略类型差异化（28号 §3.5）
    "打板": 1.5,
    "事件驱动": 1.3,
    "多因子": 1.2,
}
SENTIMENT_DEGRADE_THRESHOLD = 0.6  # confidence < 0.6 触发降级（28号 §3.5）

# 单策略单日亏损熔断（§2.5.1 日度熔断补充）
STRATEGY_DAILY_LOSS_HALT = 0.05  # 单策略单日亏损 > 5% → 暂停 1 天

# σ_i 异常判定阈值（31_position_sizing §2.2.2，2026-08-10 施工流程补充）
VOL_WINDOW_DAYS = 60             # inverse-vol 波动率窗口（60 日，与 RegimeMetaAllocator 口径对齐）
MIN_VALID_SAMPLES = 30           # 规则2 样本量门控：窗口内有效交易日 < 30 → 降级
SIGMA_EXTREME_CAP = 1.50         # 规则3 极端值检查：年化波动率 > 150% → 降级
MIN_LISTING_DAYS = 60            # 规则4 新股冷启：上市 < 60 个交易日 → 降级

# 策略级冷启动执行比例（30_multi_strategy_concurrency §6.7 MVP 基线，v2.1.0 裁定）
COLD_START_RATIO_COLD = 0.30     # 冷启动期 ×30%（单策略故障不致命 + PnL 信号可观测）
COLD_START_RATIO_HALF = 0.60     # 半仓期 ×60%
COLD_START_STAGE1_DAYS = 30      # 上线 <30 天 → 冷启动 ×30%
COLD_START_STAGE2_DAYS = 60      # 30≤上线<60 天 → 半仓 ×60%；≥60 天 → 满仓 ×100%
COLD_START_PERF_STABLE_OBS = 40  # 60 日窗口有效观测 ≥40 → PerformanceScore 稳定 → 锁定满仓

# score→weight 转换契约（30号 §2.2 契约③：25号 IC 合成评分归一化区间）
SCORE_MIN = -3.0                 # 复合因子评分下界（21号 §3.3 归一化 [-3,3]）
SCORE_MAX = 3.0                  # 复合因子评分上界


@dataclass(frozen=True)
class VolatilityInfo:
    """波动率元数据（31号 §2.2.2 σ_i 异常判定输入）。

    sigma 必填；valid_samples / listing_days 为 None 时对应规则不判定
    （元数据缺失≠异常，信息不足不降级，仅规则1/3始终可判）。
    """

    sigma: float                      # 年化波动率（60 日窗口，日收益标准差×√252）
    valid_samples: int | None = None  # 60 日窗口内有效交易日数（None=未知，跳过规则2）
    listing_days: int | None = None   # 上市交易日数（None=未知，跳过规则4）


@dataclass(frozen=True)
class TargetWeight:
    """单标的粗仓位权重。

    target_weight 口径：相对 strategy_budget 的占比（非绝对总资金权重）。
    FirmRiskAggregator §2.2 据此做 budget 口径归一化。
    """

    target_weight: float   # 目标权重（粗仓位，未经 Kelly，相对 strategy_budget）
    reason: str            # 选入理由
    confidence: float      # 策略自信度 [0, 1]


@dataclass(frozen=True)
class TargetPortfolio:
    """单策略目标组合（CTR-POS-020）。

    粗仓位未经 Kelly，权重和 ≤ budget。与 MOD-POS-001 PositionPlan 的区别：
    TargetPortfolio 是"策略想买什么"，PositionPlan 是"组合最终能买什么"。

    权重口径：positions 中 target_weight 是相对 strategy_budget 的占比。
    """

    strategy_id: str
    positions: dict[str, TargetWeight]
    total_weight: float                       # ≤ budget，未满部分为现金
    budget: float                             # 当前资金预算占比（来自 RegimeMetaAllocator）
    cash_ratio: float                         # = budget − total_weight
    sizing_method: str                        # equal_weight / risk_parity / custom
    created_at: datetime = field(default_factory=datetime.now)
    idempotency_key: str = ""
    schema_version: str = "1.0"


@dataclass(frozen=True)
class SentimentStageSignal:
    """情绪周期阶段信号（28号 → 30号 StrategyBook，链路2接口契约）。

    28号定义 5 阶段情绪周期（冰点/反核/主升/疯狂/退潮）+ BOCPD/CUSUM 检测。
    退潮阶段触发卖出信号加权（retreat_weight > 1.0）。

    降级路径：28号未就绪或 confidence<0.6 时，StrategyBook 降级为
    regime ⑧加速下跌信号，retreat_weight 回退为 1.0（不加权）。
    """

    stage: str             # 当前情绪阶段 ∈ {冰点, 反核, 主升, 疯狂, 退潮}
    confidence: float      # BOCPD 后验概率 [0,1]，<0.6 触发降级
    retreat_weight: float  # 退潮加权系数，仅退潮阶段非 1.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class DrawdownLevel:
    """单策略回撤级别（§2.5.3 单策略层面，独立于组合层 drawdown_controller）。"""

    level: int             # 0=正常, 1=警告, 2=减仓, 3=停仓, 4=清仓
    drawdown: float        # 当前回撤比例
    action: str            # 动作描述


@dataclass(frozen=True)
class ColdStartState:
    """策略级冷启动状态（30号 §6.7 三段式 + 31号 §2.4.1 冷启动 ×30% 执行时机）。

    冷启动是策略级灰度迁移（与 53号 PARALLEL→SHADOW→GRAY_RAMP 同构的渐进放大哲学）。
    执行比例在策略层 budget 分配时即生效（31号 §2.4.1：strategy_budget_cold =
    strategy_budget × ratio），由 RegimeMetaAllocator.allocate() 的 cold_start_ratios
    参数消费——求和/Kelly/裁剪全链路基于已缩减值运行，归因清晰。
    """

    stage: str             # cold_start(×0.3) / half_position(×0.6) / full_position(×1.0)
    ratio: float           # 冷启动执行比例 ∈ (0, 1]
    days_live: int | None  # 已上线自然日数（None=非冷启动模式，未传 live_start_date）
    locked_full: bool      # True=PerformanceScore 稳定（有效观测≥40）锁定满仓，或满仓毕业


def scores_to_weights(
    scores: dict[str, float],
    budget: float,
    top_n: int | None = None,
    method: str = "proportional",
) -> dict[str, float]:
    """score→weight 显式转换（30号 §2.2 契约③，函数级形式化）。

    25号 IC 加权合成产出复合因子评分（21号 §3.3 归一化 [-3,3]），非仓位权重。
    本函数是评分→粗仓位权重的显式映射，三维度解耦中的一环（选股=评分排序
    top-N / 仓位=本函数 / 风控=独立参数）。策略子类可在 select_stocks 后调用。

    权重口径：相对 strategy_budget 的占比（与 TargetWeight.target_weight 一致），
    返回权重和 = budget。

    Args:
        scores: symbol → 复合因子评分，契约区间 [-3, 3]（越界 ValueError）
        budget: 策略资金预算占比（权重总和目标）
        top_n: 评分降序取前 N（None=全部入选）
        method: "proportional"=线性平移 (s−SCORE_MIN)≥0 后按比例分配；
                "equal"=入选标的等权 budget/N

    Returns:
        symbol → 权重（相对 strategy_budget 占比），Σ=budget；空输入 → {}

    Raises:
        ValueError: budget<0 / top_n≤0 / method 未知 / 评分越出 [-3,3] 契约区间
    """
    if budget < 0:
        raise ValueError(f"budget 必须 ≥0，got {budget}")
    if top_n is not None and top_n <= 0:
        raise ValueError(f"top_n 必须为正整数，got {top_n}")
    if method not in ("proportional", "equal"):
        raise ValueError(f"未知 score→weight method: {method}（仅 proportional/equal）")
    if not scores:
        return {}

    # 契约区间校验（21号 §3.3 归一化 [-3,3]，浮点容差 1e-9）
    for sym, s in scores.items():
        if s < SCORE_MIN - 1e-9 or s > SCORE_MAX + 1e-9:
            raise ValueError(
                f"{sym} 评分 {s} 越出契约区间 [{SCORE_MIN}, {SCORE_MAX}]（21号 §3.3 归一化口径）"
            )

    # 评分降序 top-N 选股
    selected = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    if top_n is not None:
        selected = selected[:top_n]
    if not selected:
        return {}

    n = len(selected)
    if method == "equal":
        w = budget / n
        return {sym: w for sym, _ in selected}

    # proportional：线性平移 s−SCORE_MIN ∈ [0, 6] 后按比例（负分标的仍得小权重，不剔除）
    shifted = {sym: s - SCORE_MIN for sym, s in selected}
    total = sum(shifted.values())
    if total <= 0:
        # 全部评分=SCORE_MIN 的退化场景 → 等权兜底
        w = budget / n
        return {sym: w for sym, _ in selected}
    return {sym: budget * v / total for sym, v in shifted.items()}


class StrategyBook:
    """独立策略账本（MOD-POS-020）。

    每个策略继承本类，实现 select_stocks() 提供 alpha 信号。粗仓位由本类按
    sizing_method 计算（等权/risk parity/custom，**不用 Kelly，不用 MVO**）。

    核心职责（30_multi_strategy_concurrency §2.2）：
        1. select_stocks(): 子类实现 alpha 选股
        2. size_positions(): 粗仓位（equal_weight/risk_parity/custom）
        3. build_target_portfolio(): 选股+粗仓位+budget裁剪+回撤Protocol+情绪周期
        4. rebalance_to_budget(): budget 适配（砍最不自信仓位/自然部署新资金）
        5. compute_performance_score(): 60 日滚动 Sortino → [0.5, 1.5]

    不做什么：
        - Kelly 精裁（归 MOD-POS-001）
        - 组合级约束（归 MOD-POS-021 FirmRiskAggregator）
        - MVO（§3.1 拒绝——协方差矩阵 5000×5000 是研究课题非工程任务）
        - 知道市场态（只收 budget 数字，regime 通过 Shrinkage 节流不重定向资金）

    回撤 Protocol（§2.5 单策略层面，独立于组合层 drawdown_controller）：
        Level 1 (回撤>8%): 新仓风险敞口降至 75%
        Level 2 (回撤>15%): 仓位缩减至 75%，停开新仓
        Level 3 (回撤>20%): 停止所有新开仓
        Level 4 (回撤>25%): 关闭所有仓位 + 强制休息 5 天
    """

    def __init__(
        self,
        strategy_id: str,
        sizing_method: str = "equal_weight",
        strategy_type: str = "多因子",
        live_start_date: date | None = None,
    ) -> None:
        """初始化 StrategyBook。

        Args:
            strategy_id: 策略唯一标识（如 "daban_001" / "multifactor_002"）
            sizing_method: 粗仓位方法，equal_weight/risk_parity/custom
                （禁用 Kelly/MVO——A 模型不允许）
            strategy_type: 策略类型，用于退潮加权系数差异化
                （打板/事件驱动/多因子，28号 §3.5）
            live_start_date: 策略上线日期（30号 §6.7 冷启动状态机锚点）。
                None=非冷启动模式（既有策略，执行比例恒 1.0，零行为变化）
        """
        if sizing_method not in ("equal_weight", "risk_parity", "custom"):
            raise ValueError(
                f"sizing_method 禁用 {sizing_method}（A 模型不允许 Kelly/MVO）"
            )
        self.strategy_id = strategy_id
        self.sizing_method = sizing_method
        self.strategy_type = strategy_type
        self._live_start_date = live_start_date
        self._current_budget: float = 1.0  # Phase 1 等权占位，Phase 2 来自 RegimeMetaAllocator

        # 回撤状态（§2.5 单策略层面）
        self._drawdown_level: int = 0
        self._current_drawdown: float = 0.0
        self._force_rest_days: int = 0  # Level 4 强制休息剩余天数

        # 情绪周期信号缓存（28号 → 30号 链路2）
        self._sentiment_signal: SentimentStageSignal | None = None

        # 持仓快照缓存（rebalance_to_budget 用）
        self._last_target_portfolio: TargetPortfolio | None = None

    # ══ 公共接口 ══════════════════════════════════════════════════════

    def build_target_portfolio(
        self,
        alpha_signals: dict[str, Any],
        position_snapshot: dict[str, Any] | None = None,
        budget: float | None = None,
        sentiment_signal: SentimentStageSignal | None = None,
        strategy_pnl_history: list[float] | None = None,
        volatility_data: dict[str, float | VolatilityInfo] | None = None,
    ) -> TargetPortfolio:
        """主入口：选股 + 粗仓位 + budget 裁剪 + 回撤 Protocol → TargetPortfolio。

        流程（30_multi_strategy_concurrency §2.2）：
            1. 缓存情绪周期信号（退潮加权用）
            2. 回撤 Protocol 检查（Level 4 强制休息 / Level 3 停开新仓）
            3. select_stocks(): alpha 选股
            4. size_positions(): 粗仓位（equal_weight/risk_parity/custom）
            5. 回撤 Protocol 仓位缩放（Level 1/2）
            6. budget 裁剪（total_weight ≤ budget）
            7. cash_ratio 计算

        Args:
            alpha_signals: 策略 alpha 信号（策略 specific，子类定义格式）
            position_snapshot: 当前持仓快照 {symbol: weight}（风控用）
            budget: 资金预算占比（来自 RegimeMetaAllocator），None=用 _current_budget
            sentiment_signal: 情绪周期阶段信号（28号 → 30号 链路2），None=无情绪加权
            strategy_pnl_history: 策略 PnL 历史（用于回撤计算），None=无回撤检查
            volatility_data: symbol → 年化波动率（risk_parity 用），None=等权降级

        Returns:
            TargetPortfolio（粗仓位，未经 Kelly，total_weight ≤ budget）

        Raises:
            StrategySelectionError: select_stocks 返回无效结果
        """
        # 更新 budget
        if budget is not None:
            self._current_budget = budget

        # 缓存情绪周期信号
        if sentiment_signal is not None:
            self._sentiment_signal = sentiment_signal

        # 回撤 Protocol 更新（§2.5 单策略层面）
        if strategy_pnl_history is not None:
            self._update_drawdown_level(strategy_pnl_history)

        # Level 4 强制休息期：返回空仓
        if self._force_rest_days > 0:
            self._force_rest_days -= 1
            return self._build_empty_portfolio(reason="Level4 强制休息期")

        # Level 4 清仓：返回空仓并启动强制休息
        if self._drawdown_level >= 4:
            self._force_rest_days = 5  # §2.5.2 强制休息 5 个交易日
            return self._build_empty_portfolio(reason="Level4 清仓")

        # Level 3 停仓：停止所有新开仓（仅允许平仓调仓）
        if self._drawdown_level >= 3:
            return self._build_empty_portfolio(reason="Level3 停仓")

        # 选股 + 粗仓位
        selected = self.select_stocks(alpha_signals)
        if not selected:
            return self._build_empty_portfolio(reason="无选股信号")

        positions = self.size_positions(selected, volatility_data)

        # 回撤 Protocol 仓位缩放（Level 1/2）
        positions = self._apply_drawdown_protocol(positions)

        # budget 裁剪（total_weight ≤ budget）
        positions = self._clip_to_budget(positions)

        # 计算 total_weight 和 cash_ratio
        total_weight = sum(tw.target_weight for tw in positions.values())
        cash_ratio = self._current_budget - total_weight
        if cash_ratio < 0:
            # 浮点精度兜底
            cash_ratio = 0.0

        portfolio = TargetPortfolio(
            strategy_id=self.strategy_id,
            positions=positions,
            total_weight=total_weight,
            budget=self._current_budget,
            cash_ratio=cash_ratio,
            sizing_method=self.sizing_method,
            idempotency_key=f"{self.strategy_id}_{int(datetime.now().timestamp())}",
        )
        self._last_target_portfolio = portfolio
        return portfolio

    def rebalance_to_budget(self, new_budget: float) -> TargetPortfolio:
        """适配新 budget（30_multi_strategy_concurrency §2.4，三级升级 Tier 2 调用）。

        策略自主决定砍哪些仓位——**策略不能说"我不卖"**。
        budget 上调时通过买入信号自然部署（不强制买入，现金拖累可接受）；
        budget 下调时砍最不自信的仓位。

        Args:
            new_budget: 新的资金预算占比

        Returns:
            适配新 budget 的 TargetPortfolio

        Raises:
            RebalanceRefusedError: 无上次 portfolio 可适配（首次调用须先 build）
        """
        old_budget = self._current_budget
        self._current_budget = new_budget

        if self._last_target_portfolio is None:
            # 无上次 portfolio：返回空仓（等下次 build_target_portfolio 部署）
            return self._build_empty_portfolio(reason="首次调用无持仓可适配")

        old_positions = dict(self._last_target_portfolio.positions)

        if new_budget >= old_budget:
            # Budget 上调：不强制买入，现金拖累可接受（§2.4 Budget 增加——简单）
            # 仅更新 budget 字段，仓位自然部署留给下次 build_target_portfolio
            total_weight = sum(tw.target_weight for tw in old_positions.values())
            # 上调后若仓位未满，cash_ratio 自然增大
            cash_ratio = new_budget - total_weight
            if cash_ratio < 0:
                cash_ratio = 0.0
            portfolio = TargetPortfolio(
                strategy_id=self.strategy_id,
                positions=old_positions,
                total_weight=total_weight,
                budget=new_budget,
                cash_ratio=cash_ratio,
                sizing_method=self.sizing_method,
                idempotency_key=f"{self.strategy_id}_rebalance_{int(datetime.now().timestamp())}",
            )
            self._last_target_portfolio = portfolio
            return portfolio

        # Budget 下调：砍最不自信的仓位（§2.4 Budget 减少 Tier 2——策略自主）
        # 按 confidence 降序排列，从最自信的开始保留，最不自信的被砍
        sorted_positions = sorted(
            old_positions.items(), key=lambda x: x[1].confidence, reverse=True
        )

        new_positions: dict[str, TargetWeight] = {}
        accumulated = 0.0

        for symbol, tw in sorted_positions:
            if accumulated + tw.target_weight <= new_budget:
                # 保留
                new_positions[symbol] = tw
                accumulated += tw.target_weight
            else:
                # 需要砍这个仓位：部分保留 or 全砍
                remaining = new_budget - accumulated
                if remaining > 0.001:  # 还有剩余空间，部分保留
                    new_positions[symbol] = TargetWeight(
                        target_weight=remaining,
                        reason=tw.reason + " [budget下调部分保留]",
                        confidence=tw.confidence,
                    )
                    accumulated = new_budget
                # remaining <= 0.001：全砍，不加入 new_positions

        total_weight = sum(tw.target_weight for tw in new_positions.values())
        cash_ratio = new_budget - total_weight
        if cash_ratio < 0:
            cash_ratio = 0.0

        portfolio = TargetPortfolio(
            strategy_id=self.strategy_id,
            positions=new_positions,
            total_weight=total_weight,
            budget=new_budget,
            cash_ratio=cash_ratio,
            sizing_method=self.sizing_method,
            idempotency_key=f"{self.strategy_id}_rebalance_{int(datetime.now().timestamp())}",
        )
        self._last_target_portfolio = portfolio
        return portfolio

    def compute_performance_score(
        self, pnl_history: list[float], risk_free_rate: float = 0.0
    ) -> float:
        """计算 60 日滚动 Sortino → PerformanceScore [0.5, 1.5]。

        供 RegimeMetaAllocator 后验分配（Phase 2，34号 §3.1 口径对齐）。
        Sortino 只惩罚下行波动（符合"上行波动是好的"直觉）。

        映射：Sortino=0 → 0.5，Sortino≥2 → 1.5，线性插值。
        floor=0.5（防饿死），cap=1.5（防集中）。

        Args:
            pnl_history: 策略日度收益率历史（最新在前或后均可，取最后 60 日）
            risk_free_rate: 无风险利率（日度，默认 0）

        Returns:
            PerformanceScore ∈ [0.5, 1.5]
        """
        # 取最近 60 日
        recent = pnl_history[-PERF_SCORE_LOOKBACK:] if len(pnl_history) > PERF_SCORE_LOOKBACK else pnl_history
        if len(recent) < 2:
            return PERF_SCORE_FLOOR  # 样本不足返回 floor

        # 计算超额收益
        excess = [r - risk_free_rate for r in recent]
        mean_excess = sum(excess) / len(excess)

        # 下行偏差（Sortino 分母）：只惩罚负收益
        downside_returns = [min(0, e) for e in excess]
        downside_deviation = math.sqrt(
            sum(d ** 2 for d in downside_returns) / len(downside_returns)
        )

        if downside_deviation == 0:
            # 无下行波动：若均值正则给 cap，否则 floor
            sortino = float("inf") if mean_excess > 0 else 0.0
        else:
            # Sortino 年化：日度均值 × 252 / 日度下行偏差
            sortino = (mean_excess * 252) / (downside_deviation * math.sqrt(252))

        # 线性映射 Sortino → [0.5, 1.5]
        if sortino <= SORTINO_LOW:
            score = PERF_SCORE_FLOOR
        elif sortino >= SORTINO_HIGH:
            score = PERF_SCORE_CAP
        else:
            # 线性插值
            score = PERF_SCORE_FLOOR + (sortino - SORTINO_LOW) / (
                SORTINO_HIGH - SORTINO_LOW
            ) * (PERF_SCORE_CAP - PERF_SCORE_FLOOR)

        return max(PERF_SCORE_FLOOR, min(PERF_SCORE_CAP, score))

    def get_drawdown_level(self) -> DrawdownLevel:
        """获取当前回撤级别（§2.5.3 单策略层面）。"""
        level = self._drawdown_level
        actions = {
            0: "正常",
            1: "新仓风险敞口降至75%",
            2: "仓位缩减至75%+停开新仓",
            3: "停止所有新开仓",
            4: "关闭所有仓位+强制休息5天",
        }
        return DrawdownLevel(
            level=level,
            drawdown=self._current_drawdown,
            action=actions.get(level, "未知"),
        )

    def get_retreat_weight(self) -> float:
        """获取当前退潮加权系数（28号 §3.5 → 30号 链路2）。

        退潮阶段：按策略类型差异化（打板1.5/事件驱动1.3/多因子1.2）。
        非退潮阶段：1.0（无加权）。
        降级路径：confidence<0.6 → 回退 1.0（28号 §3.5）。
        """
        if self._sentiment_signal is None:
            return 1.0

        sig = self._sentiment_signal
        # 降级路径：confidence < 0.6 → 回退 1.0
        if sig.confidence < SENTIMENT_DEGRADE_THRESHOLD:
            return 1.0

        # 非退潮阶段：1.0
        if sig.stage != "退潮":
            return 1.0

        # 退潮阶段：按策略类型差异化
        return RETREAT_WEIGHT_BY_TYPE.get(self.strategy_type, RETREAT_WEIGHT_DEFAULT)

    def get_cold_start_state(
        self,
        today: date | None = None,
        perf_valid_observations: int = 0,
    ) -> ColdStartState:
        """冷启动状态机（30号 §6.7 MVP 基线 + §6.7 施工指导）。

        三段式渐进放大（与 53号 PARALLEL→SHADOW→GRAY_RAMP 同构）：
            上线 <30 天  → cold_start    ×0.30
            30~60 天     → half_position ×0.60
            ≥60 天       → full_position ×1.00（毕业）
        PerformanceScore 稳定（60 日窗口有效观测 ≥40）→ 锁定满仓 ×1.00（提前毕业）。

        晋升条件的质量门（无 firm 风险违例 / PnL 偏离回测 ≤30%）待 C1 实盘校准
        （§6.7 裁定要点 2），当前按上线天数自动晋升 + 观测数锁定。

        Args:
            today: 当前日期（None=date.today()，测试可注入）
            perf_valid_observations: PerformanceScore 60 日窗口有效观测数

        Returns:
            ColdStartState（stage/ratio/days_live/locked_full）
        """
        if today is None:
            today = date.today()

        # 非冷启动模式：未传 live_start_date → 既有策略恒满仓（零行为变化）
        if self._live_start_date is None:
            return ColdStartState(
                stage="full_position", ratio=1.0, days_live=None, locked_full=True
            )

        days_live = (today - self._live_start_date).days

        # PerformanceScore 稳定 → 锁定满仓（§6.7 裁定要点）
        if perf_valid_observations >= COLD_START_PERF_STABLE_OBS:
            return ColdStartState(
                stage="full_position", ratio=1.0, days_live=days_live, locked_full=True
            )

        if days_live < COLD_START_STAGE1_DAYS:
            return ColdStartState(
                stage="cold_start", ratio=COLD_START_RATIO_COLD,
                days_live=days_live, locked_full=False,
            )
        if days_live < COLD_START_STAGE2_DAYS:
            return ColdStartState(
                stage="half_position", ratio=COLD_START_RATIO_HALF,
                days_live=days_live, locked_full=False,
            )
        return ColdStartState(
            stage="full_position", ratio=1.0, days_live=days_live, locked_full=True
        )

    def get_cold_start_ratio(
        self,
        today: date | None = None,
        perf_valid_observations: int = 0,
    ) -> float:
        """当前冷启动执行比例（供 RegimeMetaAllocator.allocate() cold_start_ratios 消费）。"""
        return self.get_cold_start_state(today, perf_valid_observations).ratio

    # ── 子类实现接口 ──────────────────────────────────────────────────

    def select_stocks(self, alpha_signals: dict[str, Any]) -> list[str]:
        """策略 alpha 选股（子类实现）。

        Args:
            alpha_signals: 策略 alpha 信号（子类定义格式）

        Returns:
            选中的标的列表（symbol 列表）

        Raises:
            NotImplementedError: 子类必须实现
        """
        raise NotImplementedError("子类必须实现 alpha 选股逻辑")

    # ── 内部方法 ──────────────────────────────────────────────────────

    def size_positions(
        self,
        symbols: list[str],
        volatility_data: dict[str, float | VolatilityInfo] | None = None,
    ) -> dict[str, TargetWeight]:
        """粗仓位计算（equal_weight/risk_parity/custom，不用 Kelly）。

        权重口径：相对 strategy_budget 的占比（非绝对总资金权重）。

        Args:
            symbols: 选中的标的列表
            volatility_data: symbol → 年化波动率（risk_parity 用）。
                float 纯波动率或 VolatilityInfo（含样本量/上市天数元数据，
                触发 31号 §2.2.2 σ_i 异常判定 4 检查链部分降级）

        Returns:
            symbol → TargetWeight
        """
        if not symbols:
            return {}

        if self.sizing_method == "equal_weight":
            return self._size_equal_weight(symbols)
        elif self.sizing_method == "risk_parity":
            return self._size_risk_parity(symbols, volatility_data)
        elif self.sizing_method == "custom":
            # custom 由子类覆盖 size_positions 或 build_target_portfolio 实现
            # 默认降级为等权
            return self._size_equal_weight(symbols)
        else:
            raise ValueError(f"未知 sizing_method: {self.sizing_method}")

    def _size_equal_weight(self, symbols: list[str]) -> dict[str, TargetWeight]:
        """等权粗仓位：每个标的 budget/N。"""
        n = len(symbols)
        weight_per_symbol = self._current_budget / n
        return {
            sym: TargetWeight(
                target_weight=weight_per_symbol,
                reason="equal_weight",
                confidence=0.5,  # 等权默认中性自信度
            )
            for sym in symbols
        }

    def _size_risk_parity(
        self, symbols: list[str], volatility_data: dict[str, float | VolatilityInfo] | None
    ) -> dict[str, TargetWeight]:
        """Risk parity 粗仓位：inverse-volatility 加权（不用协方差，不用 MVO）。

        σ_i 异常判定 4 检查链（31号 §2.2.2，2026-08-10 施工流程补充）：
        任一触发 → 该标的**部分降级**为等权份额 budget/N（非阻断整个策略），
        其余标的仍按 inverse-vol 瓜分剩余 budget×N_ok/N：
            1. 缺失检查：σ_i = NaN/None/≤0（方差非正）→ 降级
            2. 样本量门控：60 日窗口内有效交易日 < 30 → 降级（元数据缺失时不判）
            3. 极端值检查：σ_i 年化 > 150%（新股/事件冲击期极端波动）→ 降级
            4. 新股冷启：上市 < 60 个交易日 → 降级（元数据缺失时不判）

        arXiv:2603.26893 Water-Filling 在 minimax 意义下更优，但 Phase 1 用
        inverse-vol（Morwane risk-parity 实证，与 A 模型"加法替代优化器"一致）。
        Phase 2 候选升级到 Clipped Water-Filling（若 inverse-vol 显示信号失真）。
        """
        if not volatility_data:
            # 无波动率数据：整体降级为等权
            return self._size_equal_weight(symbols)

        n = len(symbols)
        degraded_reasons: dict[str, str] = {}  # 异常标的 → 降级原因（审计归因）
        inv_vols: dict[str, float] = {}        # 正常标的 → 1/σ
        sigmas: dict[str, float] = {}          # 正常标的 → σ（reason 展示用）

        for sym in symbols:
            info = self._parse_vol_info(volatility_data.get(sym))
            reason = self._is_vol_anomaly(info)
            if reason is not None:
                degraded_reasons[sym] = reason
            else:
                inv_vols[sym] = 1.0 / info.sigma  # type: ignore[union-attr]
                sigmas[sym] = info.sigma          # type: ignore[union-attr]

        # 边界：全部异常 → 整体等权（与"无波动率数据"语义一致）
        if not inv_vols:
            return self._size_equal_weight(symbols)

        # 部分降级（31号 §2.2.2）：异常标的取等权份额 budget/N，
        # 正常标的按 inverse-vol 瓜分剩余 budget×N_ok/N，总和 = budget
        equal_share = self._current_budget / n
        ok_pool = self._current_budget * (n - len(degraded_reasons)) / n
        total_inv_vol = sum(inv_vols.values())

        result: dict[str, TargetWeight] = {}
        for sym in symbols:
            if sym in degraded_reasons:
                result[sym] = TargetWeight(
                    target_weight=equal_share,
                    reason=f"risk_parity降级等权({degraded_reasons[sym]})",
                    confidence=0.5,
                )
            else:
                result[sym] = TargetWeight(
                    target_weight=ok_pool * (inv_vols[sym] / total_inv_vol),
                    reason=f"risk_parity(inv_vol,σ={sigmas[sym]:.3f})",
                    confidence=0.5,
                )
        return result

    @staticmethod
    def _parse_vol_info(raw: float | VolatilityInfo | None) -> VolatilityInfo | None:
        """解析波动率输入：float → VolatilityInfo（无元数据），None → None。"""
        if raw is None:
            return None
        if isinstance(raw, VolatilityInfo):
            return raw
        return VolatilityInfo(sigma=float(raw))

    @staticmethod
    def _is_vol_anomaly(info: VolatilityInfo | None) -> str | None:
        """σ_i 异常判定 4 检查链（31号 §2.2.2）。返回降级原因，None=正常。

        规则2/4 在元数据缺失（None）时不判定——信息不足≠异常。
        """
        # 规则1 缺失检查：σ_i = NaN/None/≤0（方差非正）
        if info is None:
            return "σ缺失"
        if math.isnan(info.sigma) or info.sigma <= 0:
            return "σ非正/NaN"
        # 规则3 极端值检查：σ_i 年化 > 150%
        if info.sigma > SIGMA_EXTREME_CAP:
            return f"σ极端({info.sigma:.2f}>{SIGMA_EXTREME_CAP})"
        # 规则2 样本量门控：60 日窗口内有效交易日 < 30
        if info.valid_samples is not None and info.valid_samples < MIN_VALID_SAMPLES:
            return f"样本不足({info.valid_samples}<{MIN_VALID_SAMPLES})"
        # 规则4 新股冷启：上市 < 60 个交易日
        if info.listing_days is not None and info.listing_days < MIN_LISTING_DAYS:
            return f"新股冷启({info.listing_days}<{MIN_LISTING_DAYS}日)"
        return None

    def _apply_drawdown_protocol(
        self, positions: dict[str, TargetWeight]
    ) -> dict[str, TargetWeight]:
        """回撤 Protocol 仓位缩放（§2.5 单策略层面）。

        Level 1 (回撤>8%): 新仓风险敞口降至 75%——对新仓权重 ×0.75
        Level 2 (回撤>15%): 仓位缩减至 75%——所有仓位 ×0.75
        Level 3/4: 已在 build_target_portfolio 提前返回空仓
        """
        if self._drawdown_level <= 0:
            return positions

        scaled: dict[str, TargetWeight] = {}
        for sym, tw in positions.items():
            if self._drawdown_level >= 2:
                # Level 2+: 所有仓位 ×0.75
                scaled[sym] = TargetWeight(
                    target_weight=tw.target_weight * L2_POSITION_SCALAR,
                    reason=tw.reason + f" [L2缩放×{L2_POSITION_SCALAR}]",
                    confidence=tw.confidence,
                )
            elif self._drawdown_level == 1:
                # Level 1: 新仓风险敞口降至 75%
                # （简化处理：所有仓位 ×0.75，因为粗仓位阶段无法区分新旧仓）
                scaled[sym] = TargetWeight(
                    target_weight=tw.target_weight * L1_RISK_SCALAR,
                    reason=tw.reason + f" [L1缩放×{L1_RISK_SCALAR}]",
                    confidence=tw.confidence,
                )
            else:
                scaled[sym] = tw

        return scaled

    def _clip_to_budget(
        self, positions: dict[str, TargetWeight]
    ) -> dict[str, TargetWeight]:
        """budget 裁剪（total_weight ≤ budget）。

        若总权重超过 budget，按比例缩放（pro-rata，与 32号 §2.4 单票裁剪哲学一致）。
        """
        total = sum(tw.target_weight for tw in positions.values())
        if total <= self._current_budget:
            return positions

        # pro-rata 等比缩放
        scale = self._current_budget / total if total > 0 else 0.0
        return {
            sym: TargetWeight(
                target_weight=tw.target_weight * scale,
                reason=tw.reason + f" [budget裁剪×{scale:.3f}]",
                confidence=tw.confidence,
            )
            for sym, tw in positions.items()
        }

    def _update_drawdown_level(self, pnl_history: list[float]) -> None:
        """更新回撤级别（§2.5.1 四级阈值）。

        从 PnL 历史计算当前回撤，映射到四级阈值。
        """
        if not pnl_history:
            return

        # 计算累计净值
        cumulative = 1.0
        peak = 1.0
        for r in pnl_history:
            cumulative *= (1.0 + r)
            if cumulative > peak:
                peak = cumulative

        # 当前回撤 = (peak - current) / peak
        if peak > 0:
            self._current_drawdown = (peak - cumulative) / peak
        else:
            self._current_drawdown = 0.0

        # 映射到四级阈值（§2.5.1）
        if self._current_drawdown >= DRAWDOWN_L4_LIQUIDATE:
            self._drawdown_level = 4
        elif self._current_drawdown >= DRAWDOWN_L3_HALT:
            self._drawdown_level = 3
        elif self._current_drawdown >= DRAWDOWN_L2_REDUCE:
            self._drawdown_level = 2
        elif self._current_drawdown >= DRAWDOWN_L1_WARN:
            self._drawdown_level = 1
        else:
            self._drawdown_level = 0

    def _build_empty_portfolio(self, reason: str) -> TargetPortfolio:
        """构建空仓 portfolio（回撤 Protocol / 无选股信号时用）。"""
        return TargetPortfolio(
            strategy_id=self.strategy_id,
            positions={},
            total_weight=0.0,
            budget=self._current_budget,
            cash_ratio=self._current_budget,
            sizing_method=self.sizing_method,
            idempotency_key=f"{self.strategy_id}_empty_{int(datetime.now().timestamp())}",
        )
