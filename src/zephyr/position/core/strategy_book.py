# [BLUEPRINT] MOD-POS-020 | docs/03_modules/_domain_position/strategy_book/blueprint.md
# [MODULE] zephyr.position.core.strategy_book
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.core.drawdown_controller; zephyr.position.core.capital_curve_manager
# [CONSUMERS] MOD-POS-021(FirmRiskAggregator消费TargetPortfolio); MOD-PA-007(RegimeMetaAllocator收PerformanceScore反馈)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] total_weight≤budget(粗仓位不经Kelly); sizing_method∈{equal_weight,risk_parity,custom}禁用Kelly/MVO; 策略不知道市场态只收budget数字; rebalance_to_budget必须返回适配portfolio(策略不能说"我不卖"); DrawdownProtocol四级回撤触发独立收缩; target_portfolio权重口径=相对strategy_budget占比(非绝对总资金权重)
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
Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 策略 alpha 信号 alpha_signals
#   fields: 策略specific信号dict，子类select_stocks消费定义格式
#   code: build_target_portfolio(alpha_signals) (strategy_book.py L214)
# - id: I2
#   name: 资金预算 budget
#   fields: RegimeMetaAllocator下发的预算占比，None=用_current_budget（默认1.0占位）
#   code: budget/_current_budget (strategy_book.py L216/L197)
# - id: I3
#   name: 策略 PnL 历史 strategy_pnl_history
#   fields: 日度收益率list（回撤四级判定与60日Sortino用）
#   code: strategy_pnl_history/pnl_history (strategy_book.py L218/L393)
# - id: I4
#   name: 标的年化波动率 volatility_data
#   fields: symbol→年化波动率（risk_parity用），None降级等权
#   code: volatility_data (strategy_book.py L219)
# - id: I5
#   name: 情绪周期信号 SentimentStageSignal
#   fields: 5阶段stage（冰点/反核/主升/疯狂/退潮）+ confidence + retreat_weight（28号链路2）
#   code: SentimentStageSignal (strategy_book.py L124)
# 层: 特征
# - id: F1
#   name_zh: 策略当前回撤
#   name_en: current_drawdown
#   intro: 从PnL累计净值算当前回撤比例，是四级回撤协议的触发输入
#   formula: cumulative=Π(1+r)逐日累乘 → peak=max(cumulative) → dd=(peak−cumulative)/peak
#   code: strategy_book.py L645-656
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2
#   name_zh: 60日滚动 Sortino 比率
#   name_en: sortino
#   intro: 只惩罚下行波动的风险调整收益，映射PerformanceScore供后验分配
#   formula: excess=r−rf → downside_dev=√(Σmin(0,e)²/N) → Sortino=mean(excess)×252/(downside_dev×√252)；无下行波动且均值正→inf
#   code: strategy_book.py L416-430
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F3
#   name_zh: 退潮加权系数
#   name_en: retreat_weight
#   intro: 退潮阶段按策略类型放大卖出权重，非退潮或低置信回退1.0不加权
#   formula: stage=退潮且confidence≥0.6 → 打板1.5/事件驱动1.3/多因子1.2（默认1.5）；否则1.0
#   code: strategy_book.py L461-481
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 目标组合构建主流程
#   name_en: build_target_portfolio
#   intro: 选股+粗仓位+回撤缩放+budget裁剪，产出策略想买什么的TargetPortfolio
#   desc: 更新budget/缓存情绪信号→回撤检查（L4清仓+休息5天/L3停仓返空仓）→select_stocks→size_positions→回撤协议缩放→budget裁剪→算cash_ratio（L212-302）
#   inputs: I1 I2 I3 I5 F1
#   outputs: TargetPortfolio
#   invariant: total_weight≤budget；策略不知道市场态只收budget数字
# - id: A2
#   name_zh: ② 粗仓位计算（禁用Kelly/MVO）
#   name_en: size_positions / _size_equal_weight / _size_risk_parity
#   intro: 等权budget/N或逆波动率加权，A模型只做粗仓位不碰优化器
#   desc: equal_weight: w=budget/N；risk_parity: w=budget×(1/vol)/Σ(1/vol)，vol缺失默认0.30，无波动率数据降级等权；custom默认降级等权（L501-578）
#   inputs: I2 I4
#   outputs: symbol→TargetWeight
#   invariant: sizing_method∈{equal_weight,risk_parity,custom}禁用Kelly/MVO
# - id: A3
#   name_zh: ③ 四级回撤协议
#   name_en: _update_drawdown_level / _apply_drawdown_protocol
#   intro: 回撤8/15/20/25%四级触发，独立收缩仓位与开仓权限
#   desc: dd≥8%→L1新仓×0.75；≥15%→L2全仓×0.75停新仓；≥20%→L3停所有新开仓；≥25%→L4清仓+强制休息5天（L580-612/L636-668）
#   inputs: F1
#   outputs: 缩放后仓位 + 回撤级别
#   invariant: DrawdownProtocol四级回撤触发独立收缩
# - id: A4
#   name_zh: ④ budget 等比裁剪
#   name_en: _clip_to_budget
#   intro: 总权重超budget时pro-rata等比缩回，保持各票相对比例
#   desc: total>budget → scale=budget/total，每票w×scale并记录理由（L614-634）
#   inputs: I2
#   outputs: 裁剪后仓位
#   invariant: Σtarget_weight≤budget（粗仓位不经Kelly）
# - id: A5
#   name_zh: ⑤ budget 适配再平衡
#   name_en: rebalance_to_budget
#   intro: 上调不强制买入（现金拖累可接受），下调按confidence从最不自信砍起，策略不能说不卖
#   desc: 新budget≥旧→仅更新budget仓位留待下次build；下调→按confidence降序保留，超限仓位部分保留remaining>0.001否则全砍（L304-390）
#   inputs: I2
#   outputs: 适配新budget的TargetPortfolio
#   invariant: rebalance_to_budget必须返回适配portfolio
# - id: A6
#   name_zh: ⑥ PerformanceScore 映射
#   name_en: compute_performance_score
#   intro: 60日Sortino线性映射到[0.5,1.5]，floor防饿死cap防集中
#   desc: Sortino≤0→0.5，≥2→1.5，中间线性插值，最后clamp到[0.5,1.5]；样本<2返回floor（L392-443）
#   inputs: F2 I3
#   outputs: PerformanceScore∈[0.5,1.5]
#   invariant: 0.5≤score≤1.5
# 层: 输出
# - id: O1
#   name_zh: 单策略目标组合 TargetPortfolio
#   name_en: TargetPortfolio
#   intro: 策略想买什么（标的+粗权重+cash_ratio），未经Kelly，交组合汇总层硬裁剪
#   invariant: total_weight≤budget；权重口径=相对strategy_budget占比（非绝对总资金权重）
#   downstream: MOD-POS-021 FirmRiskAggregator（消费TargetPortfolio）
# - id: O2
#   name_zh: 策略绩效分 PerformanceScore
#   name_en: PerformanceScore
#   intro: [0.5,1.5]反馈给RegimeMetaAllocator做后验budget分配
#   downstream: MOD-PA-007 RegimeMetaAllocator（收PerformanceScore反馈）
# - id: O3
#   name_zh: 状态查询接口 DrawdownLevel/retreat_weight
#   name_en: get_drawdown_level / get_retreat_weight
#   intro: 暴露当前回撤级别（0-4+动作描述）与退潮加权系数供外部查询
#   downstream: 无下游/内部使用（监控与28号情绪链路查询）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I5 --> A1
# I3 -.->|断点| F1
# I3 -.->|断点| F2
# I5 -.->|断点| F3
# F1 --> A1
# F1 --> A3
# A1 --> A2
# I2 --> A2
# I4 --> A2
# A2 --> A3
# A3 --> A4
# I2 --> A4
# A4 --> A1
# I2 --> A5
# F2 --> A6
# I3 --> A6
# A1 --> O1
# A5 --> O1
# A6 --> O2
# A3 --> O3
# F3 --> O3
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
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
    ) -> None:
        """初始化 StrategyBook。

        Args:
            strategy_id: 策略唯一标识（如 "daban_001" / "multifactor_002"）
            sizing_method: 粗仓位方法，equal_weight/risk_parity/custom
                （禁用 Kelly/MVO——A 模型不允许）
            strategy_type: 策略类型，用于退潮加权系数差异化
                （打板/事件驱动/多因子，28号 §3.5）
        """
        if sizing_method not in ("equal_weight", "risk_parity", "custom"):
            raise ValueError(
                f"sizing_method 禁用 {sizing_method}（A 模型不允许 Kelly/MVO）"
            )
        self.strategy_id = strategy_id
        self.sizing_method = sizing_method
        self.strategy_type = strategy_type
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
        volatility_data: dict[str, float] | None = None,
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
        volatility_data: dict[str, float] | None = None,
    ) -> dict[str, TargetWeight]:
        """粗仓位计算（equal_weight/risk_parity/custom，不用 Kelly）。

        权重口径：相对 strategy_budget 的占比（非绝对总资金权重）。

        Args:
            symbols: 选中的标的列表
            volatility_data: symbol → 年化波动率（risk_parity 用）

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
        self, symbols: list[str], volatility_data: dict[str, float] | None
    ) -> dict[str, TargetWeight]:
        """Risk parity 粗仓位：inverse-volatility 加权（不用协方差，不用 MVO）。

        arXiv:2603.26893 Water-Filling 在 minimax 意义下更优，但 Phase 1 用
        inverse-vol（Morwane risk-parity 实证，与 A 模型"加法替代优化器"一致）。
        Phase 2 候选升级到 Clipped Water-Filling（若 inverse-vol 显示信号失真）。
        """
        if not volatility_data:
            # 无波动率数据：降级为等权
            return self._size_equal_weight(symbols)

        # inverse-volatility 权重
        inv_vols: dict[str, float] = {}
        total_inv_vol = 0.0
        for sym in symbols:
            vol = volatility_data.get(sym, 0.0)
            if vol <= 0:
                vol = 0.30  # 缺失波动率默认 30%（A 股个股中位数）
            inv_vol = 1.0 / vol
            inv_vols[sym] = inv_vol
            total_inv_vol += inv_vol

        if total_inv_vol == 0:
            return self._size_equal_weight(symbols)

        return {
            sym: TargetWeight(
                target_weight=self._current_budget * (inv_vols[sym] / total_inv_vol),
                reason=f"risk_parity(inv_vol={volatility_data.get(sym, 0.30):.3f})",
                confidence=0.5,
            )
            for sym in symbols
        }

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
