# [BLUEPRINT] MOD-PA-007 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md
# [MODULE] zephyr.pf_alloc.core.regime_meta_allocator
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.shared.foundation.errors（regime 概率以纯数据入参消费，无代码级 import——依赖倒置）
# [CONSUMERS] MOD-POS-020(StrategyBook消费BudgetAllocation); MOD-POS-022(BudgetChangeHandler收BudgetChanged事件)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] allocation=normalize(Base×PerformanceScore)Σ=1.0; floor≥5%防饿死cap≤40%防集中; Shrinkage≤1.0只减不增; shrinkage_enabled开关(C1验证); regime只回答"多谨慎"不回答"偏向谁"(PerformanceScore后验捕获); 不做alpha择时(移除RegimeScore); global_shrinkage是全局的(归一化时约掉,只在effective_budget层缩放)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AllocationError(ZA-PA-0007); ShrinkageDisabled(ZA-PA-0008)
# [TESTS] tests/pf_alloc/test_regime_meta_allocator.py
# [A_module] module_id=MOD-PA-007 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


RegimeMetaAllocator — Regime元分配器 (MOD-PA-007)

A 模型（30_multi_strategy_concurrency §2.2）的 meta 层。消费 regime 检测器 (MOD-REGIME-001) 的
12 维灰度概率 + 各策略 PerformanceScore，通过 **Shrinkage 风险节流（只减不增）**
+ **PerformanceScore 后验分配**，产出各 StrategyBook 的资金预算占比。

核心裁定（30_multi_strategy_concurrency §2.2，2026-08-05）：移除 RegimeScore，regime 仅通过
Shrinkage 做风险节流。regime 只回答"现在该多谨慎"，不回答"现在该偏向哪个策略"——
后者由 PerformanceScore 后验 PnL 自然捕获。

分配公式：allocation_i = normalize(Base_i × PerformanceScore_i)
硬约束：floor ≥ 5%（防饿死），cap ≤ 40%（防集中）
总暴露：effective_budget_i = allocation_i × global_shrinkage

关键设计（§3.1 实现注记 + §3.4 施工要点 #4）：
    Shrinkage 是**全局**的（一个 regime 状态→一个 global_shrinkage，所有策略共用）。
    normalize(Base_i × PerformanceScore_i × global_shrinkage) = normalize(Base_i × PerformanceScore_i)
    ——全局 Shrinkage 在归一化时约掉，allocation_i 实际由 Base×PerformanceScore 决定，
    Shrinkage 只通过 effective_budget = allocation_i × global_shrinkage 缩放总暴露。

开源实证（Morwane/multi-strategy-alpha-book）：regime 做 risk-throttle Sharpe +1.43 /
MaxDD −10.3%；regime 做 alpha-timing Sharpe +0.87（降）。数据印证：同信号用于进攻
有害，用于防守有益。

依据: 30_multi_strategy_concurrency §2.2 + 10_regime_detector_spec §5（Shrinkage 二维公式）
      + 34_regime_meta_allocator §3.4（施工算法伪代码）+ blueprint §2.3
SSoT: depgraph MOD-PA-007
Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: regime 概率向量 regime_probabilities
#   fields: MOD-REGIME-001 HMM 输出的状态概率向量（取 max(P)）
#   code: allocate L195 / _compute_confidence_signal L365
# - id: I2
#   name: 各策略 PerformanceScore
#   fields: {strategy_id: score∈[0.5,1.5]}（60日 Sortino 映射，冷启动传 1.0）
#   code: allocate L196 / compute_performance_score L493
# - id: I3
#   name: RiskSignal 13 参数输入
#   fields: risk_base + resonance_penalty + opportunity_recovery
#   code: _compute_risk_signal L384-386
# - id: I4
#   name: 先验权重 + 样本天数 + CRISIS 开关
#   fields: base_weights（缺省等权1/N）+ strategy_sample_days（<30天冷启动）+ is_crisis
#   code: allocate L194-199
# 层: 算法
# - id: A1
#   name_zh: ① ConfidenceSignal 四档映射
#   name_en: _compute_confidence_signal
#   intro: HMM 最大概率越大越敢投，分四档给出置信度系数
#   desc: max(P)<0.6→0.30；<0.8→0.60；<0.95→0.85；≥0.95→1.00（L88-93 阈值表，L365-371 映射）
#   inputs: I1
#   outputs: confidence_signal ∈{0.3,0.6,0.85,1.0}
# - id: A2
#   name_zh: ② RiskSignal 聚合裁剪
#   name_en: _compute_risk_signal
#   intro: 风险基底乘共振惩罚加机会恢复，钳在 0.30~1.00
#   desc: raw = risk_base×resonance_penalty + opportunity_recovery → clamp[0.30, 1.00]（L387-388）
#   inputs: I3
#   outputs: risk_signal ∈[0.30,1.00]
# - id: A3
#   name_zh: ③ global_shrinkage 风险节流
#   name_en: _compute_shrinkage
#   intro: 置信度×风险得到全局资金收缩比例，只减不增，危机态地板降到 5%
#   desc: raw=confidence×risk；final=max(floor, min(1.0, raw))，floor 常规 0.09 / is_crisis 0.05（L427-436；#208-① 当前参数域 raw≥0.09，0.05 floor 前瞻保留不生效）；shrinkage_enabled=False 时全 1.0（C1 验证开关，L319-327）
#   inputs: A1 A2 I4
#   outputs: global_shrinkage ∈[0.05,1.0]（ShrinkageDetail）
#   invariant: Shrinkage≤1.0 只减不增；全局共用一个值
# - id: A4
#   name_zh: ④ Base×Perf 后验乘法
#   name_en: _compute_raw_allocation
#   intro: 先验权重乘绩效得分决定各策略相对占比，Shrinkage 全局归一化时约掉不参与
#   desc: raw_i = base_i × perf_i（L403）；base 缺失按等权 1/N 补齐（L269-278）；<30 交易日冷启动 perf 强制 1.0 中性（L280-304）
#   inputs: I2 I4
#   outputs: raw_allocation
#   invariant: regime 只回答"多谨慎"不回答"偏向谁"
# - id: A5
#   name_zh: ⑤ 归一化 + floor/cap 迭代裁剪
#   name_en: _normalize_and_clip
#   intro: 归一化到 Σ=1 后按 5% 地板 40% 顶做 water-filling 投影，越界固定余量重分
#   desc: alloc=raw/Σ；N×cap<1 无解兜底放宽 cap=1-(N-1)×floor；≤floor 或 ≥cap 的固定，free 策略按比例 scale 重分，最多 5 轮迭代（L421-489）
#   inputs: A4
#   outputs: allocations（Σ=1.0，5%≤alloc≤40%）
#   invariant: floor≥5% 防饿死 cap≤40% 防集中；Σ=1.0
# - id: A6
#   name_zh: ⑥ effective_budget 缩放
#   name_en: allocate（Step 4）
#   intro: 相对占比乘全局收缩因子得到各策略实收预算
#   desc: effective_budget_i = allocation_i × global_shrinkage（L254-257），组装 BudgetAllocation 返回
#   inputs: A3 A5
#   outputs: effective_budgets
# 层: 输出
# - id: O1
#   name_zh: 资金预算分配 BudgetAllocation
#   name_en: BudgetAllocation
#   intro: 各策略相对占比+全局节流因子+实收预算，下发给 StrategyBook 并触发预算变更事件
#   invariant: allocation Σ=1.0；effective_budget = allocation × global_shrinkage
#   downstream: MOD-POS-020 StrategyBook（消费 BudgetAllocation）; MOD-POS-022 BudgetChangeHandler（收 BudgetChanged 事件）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I3 --> A2
# A1 --> A3
# A2 --> A3
# I4 --> A3
# I2 --> A4
# I4 --> A4
# A4 --> A5
# A5 --> A6
# A3 --> A6
# A6 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Sequence

import numpy as np

from zephyr.shared.foundation.errors import ZephyrBaseError

logger = logging.getLogger(__name__)


# ── 常量（参数来源：34_regime_meta_allocator §3.2.2 / §3.2.3 / §3.2.4）──────────

# floor/cap 硬约束（§3.2.4，行业经验值，BestFolio 2026-04 印证 cap=40%）
FLOOR: float = 0.05          # 单策略最低占比 5%（防饿死）
CAP: float = 0.40            # 单策略最高占比 40%（防集中）

# PerformanceScore 映射区间（§3.2.2）
PERF_SCORE_MIN: float = 0.5  # Sortino≤0 → 0.5（砍半但不饿死）
PERF_SCORE_MAX: float = 1.5  # Sortino≥2.0 → 1.5（×1.5但不集中）
SORTINO_FLOOR: float = 0.0   # Sortino 下限映射点
SORTINO_CEILING: float = 2.0 # Sortino 上限映射点
SORTINO_NEUTRAL: float = 1.0 # Sortino=1.0 → PerformanceScore=1.0（中性）

# Sortino 统计防护（§3.2.2 四件套）
DOWNSIDE_MIN_OBSERVATIONS: int = 15   # downside 样本量门槛（<15 强制中性）
COLD_START_MIN_DAYS: int = 30         # 冷启动过渡门槛（交易日）
GAP_NORMAL_CEILING: float = 1.5       # Sortino/Sharpe gap 正常上限（quantt.co.uk 2026-04 实证 1.3-1.5）
GAP_WARNING_MULTIPLIER: float = 1.2   # gap > 1.5×1.2=1.8 → 疑似 inflated 警告
GAP_SEVERE_MULTIPLIER: float = 1.5    # gap > 1.5×1.5=2.25 → 严重 inflated 强制复核

# MAR / Rf（§3.2.2 MAR 选型决策：MAR=Rf=货币基金~2%年化）
MAR_ANNUAL: float = 0.02
TRADING_DAYS: int = 252

# ConfidenceSignal 四档阈值（§3.2.3，[10号] §5.1）
# (max(P) 上界, ConfidenceSignal 值)
CONFIDENCE_THRESHOLDS: list[tuple[float, float]] = [
    (0.60, 0.30),   # max(P) < 60% → 0.3（强收缩，不确定时别赌方向）
    (0.80, 0.60),   # 60% ≤ max(P) < 80% → 0.6（中度收缩）
    (0.95, 0.85),   # 80% ≤ max(P) < 95% → 0.85（轻度收缩）
    (1.01, 1.00),   # max(P) ≥ 95% → 1.0（满部署，高确信度）
]

# Shrinkage floor（§3.2.2 熊市最低总暴露 + §3.2.2 危机态覆盖说明）
SHRINKAGE_FLOOR: float = 0.09          # = 0.3 × 0.30 = 9%（r4 熊市常规态最低暴露）
# AI-NIGHT-001 #208-①：CRISIS floor 0.05 在当前参数域数学不可达——clamp 链下界
# conf≥0.30（四档最小档）× risk≥0.30（RISK_SIGNAL_MIN clamp）→ raw≥0.09>0.05，
# max(0.05, raw) 永不选中 0.05。本常量为对齐 31号 §2.4.3 ⑩CRISIS cap 的前瞻口径
# 保留（参数域放宽使 raw<0.09 可能时生效），非误删死代码——可达性由测试
# test_crisis_floor_lowers_to_005（monkeypatch 参数域）与
# test_crisis_floor_005_unreachable_in_current_param_domain（当前域不可达断言）双锚定。
CRISIS_SHRINKAGE_FLOOR: float = 0.05   # CRISIS 态 floor 降至 5%（对齐 31号 §2.4.3 ⑩CRISIS cap）

# RiskSignal clamp 范围（§3.2.3，[10号] §5.3.3）
RISK_SIGNAL_MIN: float = 0.30
RISK_SIGNAL_MAX: float = 1.00

# 归一化裁剪最大迭代次数（§3.2.4，有界投影有限步收敛）
MAX_CLIP_ITERATIONS: int = 5


class AllocationError(ZephyrBaseError):
    """ZA-PA-0007: 分配计算异常（如策略列表为空、base_weights 缺失等）。"""

    # 2026-08-17 对齐全域错误基类（原裸继承 Exception 且无 error_code 类属性）
    error_code = "ZA-PA-0007"


@dataclass(frozen=True)
class ShrinkageDetail:
    """Shrinkage 计算明细（归因用）。

    Shrinkage 是**全局**的——一个 regime 状态对应一个 global_shrinkage，
    所有策略共用。归一化时约掉，只在 effective_budget 层缩放总暴露。
    """

    confidence_signal: float      # max(P) → 4 档映射（+ 稀有态折扣，当前 4 态不触发）
    risk_signal: float            # 13 参数聚合（[10号] §5.3.3 输出）
    raw_shrinkage: float          # confidence × risk（裁剪前）
    final_shrinkage: float        # ≥ floor（裁剪后，即 global_shrinkage）
    shrinkage_enabled: bool       # 验证开关（C1 一票否决）
    is_crisis: bool = False       # D-SIGNAL-68 overlay 是否触发 CRISIS 态（§3.2.2 危机态覆盖）


@dataclass(frozen=True)
class BudgetAllocation:
    """各策略 budget 占比（CTR-PA-007）。

    两个层次（§3.1）：
      - allocation_i（相对占比 Σ=1.0）回答"偏向哪个策略"——由 Base×PerformanceScore 决定
      - global_shrinkage（总暴露因子）回答"现在该多谨慎"——由 regime ConfidenceSignal×RiskSignal 决定
      - effective_budgets = allocation_i × global_shrinkage 是策略实收预算
    """

    allocations: dict[str, float]            # {strategy_id: 相对占比}，Σ=1.0，floor 5%~cap 40%
    global_shrinkage: float                  # 全局风险节流因子（0.05~1.0）
    effective_budgets: dict[str, float]      # {strategy_id: allocation_i × global_shrinkage}
    shrinkage_detail: ShrinkageDetail
    perf_scores: dict[str, float] = field(default_factory=dict)  # 各策略 PerformanceScore（审计用）
    sortino_sharpe_gaps: dict[str, float] = field(default_factory=dict)  # gap 监控（§3.2.2 四件套 #3）
    rebalance_allowed: bool = True           # 当日是否允许再平衡（频率控制 ≤1次/日）
    created_at: datetime = field(default_factory=datetime.now)
    schema_version: str = "1.0"


class RegimeMetaAllocator:
    """Regime 元分配器（MOD-PA-007）。

    A 模型 meta 层：消费 regime 检测器概率 + 各策略 PerformanceScore，
    通过 Shrinkage 风险节流 + PerformanceScore 后验分配，产出 BudgetAllocation。

    使用方式：
        allocator = RegimeMetaAllocator(
            base_weights={"daban": 0.3, "multi_factor": 0.4, "event_driven": 0.3},
            shrinkage_enabled=True,
        )
        budget = allocator.allocate(
            regime_probabilities=regime_probs,      # HMM 输出的概率向量
            performance_scores={"daban": 1.2, ...},  # 60日 Sortino→[0.5,1.5] 映射
            risk_signal_inputs={"risk_base": 0.8, ...},  # 13 参数
            is_crisis=False,
        )
        # budget.effective_budgets["daban"] = allocation × global_shrinkage

    依据: 34_regime_meta_allocator §3.4 施工算法伪代码
    """

    FLOOR: float = FLOOR   # 防饿死（5%）
    CAP: float = CAP       # 防集中（40%）

    def __init__(
        self,
        base_weights: dict[str, float] | None = None,
        shrinkage_enabled: bool = True,
    ) -> None:
        """初始化。

        Args:
            base_weights: 先验权重（等权 1/N 或人工先验），新策略冷启动只用这个。
                如 {"daban": 0.3, "multi_factor": 0.4, "event_driven": 0.3}。
                若为 None，allocate() 时按等权 1/N 自动填充。
            shrinkage_enabled: Shrinkage 开关（11_regime_backtest_validation_plan C1 验证，默认 True）。
                True → global_shrinkage = ConfidenceSignal × RiskSignal
                False → global_shrinkage = 1.0（C1 开/关对比基准，一票否决）
        """
        self.base_weights: dict[str, float] = dict(base_weights) if base_weights else {}
        self.shrinkage_enabled: bool = shrinkage_enabled

    # ── 公共接口 ──────────────────────────────────────────────────────

    def allocate(
        self,
        regime_probabilities: Any,
        performance_scores: dict[str, float],
        risk_signal_inputs: dict[str, Any],
        strategy_sample_days: dict[str, int] | None = None,
        is_crisis: bool = False,
    ) -> BudgetAllocation:
        """主入口：Shrinkage 节流 + PerformanceScore 后验分配 → BudgetAllocation。

        流程（§3.4 施工算法）：
          1. 计算 global_shrinkage（ConfidenceSignal 四档 × RiskSignal 13 参数，含 CRISIS floor）
          2. 三因子乘法 raw_allocation_i = Base_i × PerformanceScore_i
             （Shrinkage 是全局的，归一化时约掉，只在 effective_budget 层缩放，§3.1 实现注记）
          3. 归一化 + floor/cap 迭代裁剪（含 N=2 无解兜底，§3.2.4）
          4. effective_budget_i = allocation_i × global_shrinkage

        Args:
            regime_probabilities: regime 检测器输出的概率向量（np.ndarray 或 list）。
                取 max(P) 映射 ConfidenceSignal 四档。
            performance_scores: {strategy_id: PerformanceScore}，已由上游按 60 日 Sortino
                映射到 [0.5, 1.5]（可用 compute_performance_score() 静态方法计算）。
                冷启动策略应传 1.0 中性。
            risk_signal_inputs: RiskSignal 13 参数输入（[10号] §5.3.3 输出）。
                关键字段：risk_base, resonance_penalty, opportunity_recovery。
            strategy_sample_days: 各策略样本天数（<30 天冷启动，PerformanceScore 应已为 1.0）。
                若提供，额外做冷启动校验（防上游误传非中性值）。
            is_crisis: D-SIGNAL-68 overlay 是否触发 CRISIS 态（§3.2.2 危机态覆盖）。
                True → SHRINKAGE_FLOOR 从 0.09 降至 0.05（对齐 31号 crisis cap）。

        Returns:
            BudgetAllocation（allocations + global_shrinkage + effective_budgets）

        Raises:
            AllocationError: 策略列表为空或 base_weights 无法确定。
        """
        strategies = list(performance_scores.keys())
        if not strategies:
            raise AllocationError("performance_scores 为空，无策略可分配")

        N = len(strategies)

        # 确定 base_weights：若未提供或缺失策略，按等权 1/N 补齐
        base = self._resolve_base_weights(strategies)

        # 冷启动校验（§3.2.2）：<30 交易日策略 PerformanceScore 应为 1.0 中性
        perf_scores = self._apply_cold_start_neutral(
            performance_scores, strategy_sample_days, strategies
        )

        # ── Step 1: 计算 global_shrinkage（§3.2.3）──
        shrinkage = self._compute_shrinkage(regime_probabilities, risk_signal_inputs, is_crisis)

        # ── Step 2: 三因子乘法 raw_allocation（§3.1 实现注记 + §3.4 施工要点 #4）──
        #    Shrinkage 是全局的，归一化时约掉，raw_allocation 不含 Shrinkage
        raw_allocation = self._compute_raw_allocation(perf_scores, base, strategies)

        # ── Step 3: 归一化 + floor/cap 迭代裁剪（§3.2.4）──
        allocations = self._normalize_and_clip(raw_allocation, strategies)

        # ── Step 4: effective_budget = allocation × global_shrinkage（§3.1 两层）──
        global_shrinkage = shrinkage.final_shrinkage
        effective_budgets = {
            sid: allocations[sid] * global_shrinkage for sid in strategies
        }

        return BudgetAllocation(
            allocations=allocations,
            global_shrinkage=global_shrinkage,
            effective_budgets=effective_budgets,
            shrinkage_detail=shrinkage,
            perf_scores=dict(perf_scores),
        )

    # ── 子方法 ────────────────────────────────────────────────────────

    def _resolve_base_weights(self, strategies: list[str]) -> dict[str, float]:
        """解析 base_weights：若未提供或缺失策略，按等权 1/N 补齐。

        §3.2.1：冷启动（无 PnL）用等权 1/N；人工有先验信念用人工设定。
        """
        base = {}
        equal_weight = 1.0 / len(strategies)
        for sid in strategies:
            base[sid] = self.base_weights.get(sid, equal_weight)
        return base

    def _apply_cold_start_neutral(
        self,
        performance_scores: dict[str, float],
        strategy_sample_days: dict[str, int] | None,
        strategies: list[str],
    ) -> dict[str, float]:
        """冷启动校验：<30 交易日策略 PerformanceScore 强制 1.0 中性。

        §3.2.2 冷启动过渡：上线 <30 交易日 → PerformanceScore=1.0 中性。
        防上游误传非中性值（如刚上线 10 天的策略传了 1.5）。
        """
        if strategy_sample_days is None:
            return dict(performance_scores)

        scores = dict(performance_scores)
        for sid in strategies:
            days = strategy_sample_days.get(sid, COLD_START_MIN_DAYS)
            if days < COLD_START_MIN_DAYS:
                if scores[sid] != 1.0:
                    logger.warning(
                        "策略 %s 样本天数 %d < %d（冷启动），PerformanceScore %.3f → 1.0 中性",
                        sid, days, COLD_START_MIN_DAYS, scores[sid],
                    )
                    scores[sid] = 1.0
        return scores

    def _compute_shrinkage(
        self,
        regime_probabilities: Any,
        risk_signal_inputs: dict[str, Any],
        is_crisis: bool = False,
    ) -> ShrinkageDetail:
        """Shrinkage = ConfidenceSignal × RiskSignal（可开关，含 CRISIS floor）。

        - shrinkage_enabled=True  → ConfidenceSignal(max(P) 4档) × RiskSignal(13参数)
        - shrinkage_enabled=False → 1.0（C1 验证基准，一票否决）

        §3.2.2 危机态覆盖：is_crisis=True 时 floor 从 0.09 降至 0.05（对齐 31号 crisis cap）。
        #208-① 口径：当前参数域 conf≥0.30×risk≥0.30→raw≥0.09>0.05，0.05 floor
        数学不可达（前瞻保留，参数域放宽时生效），见 CRISIS_SHRINKAGE_FLOOR 注释。
        """
        if not self.shrinkage_enabled:
            return ShrinkageDetail(
                confidence_signal=1.0,
                risk_signal=1.0,
                raw_shrinkage=1.0,
                final_shrinkage=1.0,
                shrinkage_enabled=False,
                is_crisis=is_crisis,
            )

        confidence_signal = self._compute_confidence_signal(regime_probabilities)
        risk_signal = self._compute_risk_signal(risk_signal_inputs)
        raw_shrinkage = confidence_signal * risk_signal

        # CRISIS 态 floor 降级（§3.2.2 危机态覆盖说明 + §3.4 施工要点 #12）
        # #208-①：当前参数域 raw_shrinkage≥0.09>0.05，crisis floor 不约束结果
        # （前瞻口径保留），日志如实说明不夸大生效范围。
        effective_floor = CRISIS_SHRINKAGE_FLOOR if is_crisis else SHRINKAGE_FLOOR
        final_shrinkage = max(effective_floor, min(1.0, raw_shrinkage))

        if is_crisis:
            logger.info(
                "CRISIS 态激活：effective_floor %.2f → %.2f（对齐 31号 crisis cap；"
                "#208-① 当前参数域数学下界 conf≥0.30×risk≥0.30→raw≥0.09，0.05 floor "
                "前瞻保留不约束），ConfidenceSignal=%.2f RiskSignal=%.2f → global_shrinkage=%.4f",
                SHRINKAGE_FLOOR, CRISIS_SHRINKAGE_FLOOR,
                confidence_signal, risk_signal, final_shrinkage,
            )

        return ShrinkageDetail(
            confidence_signal=confidence_signal,
            risk_signal=risk_signal,
            raw_shrinkage=raw_shrinkage,
            final_shrinkage=final_shrinkage,
            shrinkage_enabled=True,
            is_crisis=is_crisis,
        )

    def _compute_confidence_signal(self, regime_probabilities: Any) -> float:
        """ConfidenceSignal 四档映射（§3.2.3，[10号] §5.1）。

        regime_probs 是 HMM 输出的状态概率向量，取 max(P) 映射四档：
          max(P) < 60%  → 0.30（强收缩，不确定时别赌方向）
          60% ≤ max(P) < 80% → 0.60（中度收缩）
          80% ≤ max(P) < 95% → 0.85（轻度收缩）
          max(P) ≥ 95% → 1.00（满部署，高确信度）

        60% 阈值的外部印证：1uptick 2026-06 机构方案"max(P)<60% 减仓 30-50%"完全一致。
        """
        probs = np.asarray(regime_probabilities, dtype=float)
        max_p = float(np.max(probs))

        for threshold, signal in CONFIDENCE_THRESHOLDS:
            if max_p < threshold:
                return signal
        return CONFIDENCE_THRESHOLDS[-1][1]  # 默认 1.0

    def _compute_risk_signal(self, params: dict[str, Any]) -> float:
        """RiskSignal 13 参数连续值（§3.2.3，[10号] §5.3.3）。

        RiskSignal = clamp[0.30, RiskBase × 共振惩罚 + 机会恢复, 1.00]
        13 参数：realized_vol 分位 / 量价时空 / 跨市场相关性 / 虹吸态 /
                 技术背离 / 新闻情绪 / 筹码结构等。
        #1 门控：危机期 #1<1.0 才激活附加参数。

        本函数是占位接口——实际 13 参数聚合逻辑归 [10号] §5.3.3 regime 检测器实现，
        本模块只管"如何消费 RiskSignal 值"（clamp[0.30, ..., 1.00]）。
        """
        risk_base = float(params.get("risk_base", 1.0))
        resonance_penalty = float(params.get("resonance_penalty", 1.0))
        opportunity_recovery = float(params.get("opportunity_recovery", 0.0))
        raw = risk_base * resonance_penalty + opportunity_recovery
        return max(RISK_SIGNAL_MIN, min(RISK_SIGNAL_MAX, raw))

    def _compute_raw_allocation(
        self,
        performance_scores: dict[str, float],
        base: dict[str, float],
        strategies: list[str],
    ) -> dict[str, float]:
        """Base × PerformanceScore（归一化前）。

        §3.1 实现注记 + §3.4 施工要点 #4：
            Shrinkage 是全局的（所有策略共用 global_shrinkage），归一化时约掉：
            normalize(Base_i × PerfScore_i × global_shrinkage) = normalize(Base_i × PerfScore_i)
            所以 raw_allocation 不含 Shrinkage，Shrinkage 只在 effective_budget 层缩放。
        """
        return {sid: base[sid] * performance_scores[sid] for sid in strategies}

    def _normalize_and_clip(
        self,
        raw: dict[str, float],
        strategies: list[str],
    ) -> dict[str, float]:
        """归一化 + floor/cap 迭代裁剪（§3.2.4，含 N=2 无解兜底）。

        算法（water-filling 投影）：
          1. 归一化 raw 使 Σ=1.0
          2. 可行性检查：若 N × cap < 1.0（cap 太紧），放宽 cap 到 1-(N-1)×floor
          3. 迭代裁剪：越界策略固定到 floor/cap，剩余 budget 按比例分配给未越界策略
          4. 重复直到收敛（无策略越界）或达到最大迭代次数

        water-filling 比"裁剪+全局再归一化"更稳定——固定越界值后只重分配未越界部分，
        避免被裁剪的值在再归一化时被拉回越界区间（原算法的收敛失败根因）。
        """
        N = len(strategies)

        # Step 1: 归一化
        total = sum(raw[sid] for sid in strategies)
        if total <= 0:
            logger.warning("raw_allocation 全零，回退等权 1/%d", N)
            return {sid: 1.0 / N for sid in strategies}
        alloc = {sid: raw[sid] / total for sid in strategies}

        # Step 2: 可行性检查（§3.2.4 无解兜底）
        # N × cap < 1.0 → 所有策略都到 cap 也不够 Σ=1.0 → cap 不可行
        effective_cap = CAP
        if N * CAP < 1.0 - 1e-9:
            relaxed_cap = 1.0 - (N - 1) * FLOOR
            logger.warning(
                "floor/cap 无解兜底触发：N=%d, floor=%.2f, cap=%.2f → "
                "放宽 cap 到 %.2f（优先保 floor 防饿死，§3.2.4）",
                N, FLOOR, CAP, relaxed_cap,
            )
            effective_cap = relaxed_cap

        # Step 3: 迭代 water-filling 裁剪
        for _ in range(MAX_CLIP_ITERATIONS):
            fixed_sum = 0.0
            free_sids: list[str] = []
            free_sum = 0.0

            for sid in strategies:
                if alloc[sid] <= FLOOR:
                    fixed_sum += FLOOR
                elif alloc[sid] >= effective_cap:
                    fixed_sum += effective_cap
                else:
                    free_sids.append(sid)
                    free_sum += alloc[sid]

            if not free_sids:
                break  # 全部固定

            target_free = 1.0 - fixed_sum
            # 除零安全性（2026-08-16 F5 裁定删除兜底分支的依据，AI-R5 勘正论证）：
            # free sid 判定条件 = FLOOR < alloc < cap（严格区间），故 free_sids 非空
            # ⇒ free_sum > |free|×FLOOR > 0，scale 分母恒正。target_free 与 free_sum
            # 一般并不相等——其差 = 固定侧被抬到 FLOOR/压到 cap 的调整量，正是 free 侧
            # 缩放（scale = target_free/free_sum）需要吸收的部分，即 water-filling 的
            # 收敛机制本身；多轮迭代 + 最终安全裁剪保证 Σalloc→1 与边界钳制。
            scale = target_free / free_sum
            changed = False
            for sid in free_sids:
                new_val = alloc[sid] * scale
                if abs(new_val - alloc[sid]) > 1e-9:
                    changed = True
                alloc[sid] = new_val

            # 固定越界策略
            for sid in strategies:
                if sid not in free_sids:
                    alloc[sid] = FLOOR if alloc[sid] <= FLOOR else effective_cap

            if not changed:
                break

        # 最终安全裁剪（防浮点漂移）
        for sid in strategies:
            alloc[sid] = max(FLOOR, min(effective_cap, alloc[sid]))

        # Σ=1.0 硬不变量兜底（2026-08-19 AI-NIGHT-001 #206）：全部策略同轮越界时
        # Step 3 循环 break（free_sids 空），裁剪后 Σ≠1——实证 base={0.98,0.01,0.01}
        # → Σ=0.5（50% 资金静默闲置）、N=25 全贴 floor → Σ=1.25。按比例归一化，
        # floor/cap 边界让位 Σ=1 硬不变量（头注 INVARIANTS）。
        total_final = sum(alloc[sid] for sid in strategies)
        if abs(total_final - 1.0) > 1e-9 and total_final > 0:
            logger.warning(
                "water-filling 全越界破产兜底：Σ=%.6f≠1.0，按比例归一化"
                "（floor/cap 边界让位 Σ=1.0 硬不变量）",
                total_final,
            )
            alloc = {sid: alloc[sid] / total_final for sid in strategies}

        return alloc

    # ── 静态工具方法（供上游计算 PerformanceScore）────────────────────

    @staticmethod
    def compute_performance_score(
        daily_returns: Sequence[float],
        trading_days_live: int | None = None,
    ) -> tuple[float, float, float]:
        """从日频收益率计算 PerformanceScore（60 日 Sortino → [0.5, 1.5] 线性映射）。

        §3.2.2 + §3.4 施工算法 _compute_sortino_and_sharpe：
          - MAR = Rf = 2% 年化（货币基金，§3.2.2 MAR 选型）
          - Sortino 下行偏差分母用 n-1（总样本量，ddof=1 与 Sharpe 一致，§3.4 施工要点 #10/#13）
          - downside 样本 <15 → 强制 1.0 中性（§3.2.2 四件套 #1）
          - 冷启动 <30 交易日 → 1.0 中性
          - Sortino/Sharpe gap 监控（§3.2.2 四件套 #3）

        Args:
            daily_returns: 日频收益率序列（如 60 日滚动窗口）。
            trading_days_live: 策略上线交易日数。若 None，用 len(daily_returns)。

        Returns:
            (performance_score, sortino, sharpe) 三元组。
            sortino/sharpe 为年化值，performance_score ∈ [0.5, 1.5]。
        """
        returns_arr = np.array(daily_returns, dtype=float)
        n = len(returns_arr)
        days_live = trading_days_live if trading_days_live is not None else n

        # 冷启动过渡（§3.2.2）：<30 交易日 → 1.0 中性
        if days_live < COLD_START_MIN_DAYS:
            return (1.0, SORTINO_NEUTRAL, SORTINO_NEUTRAL)

        if n == 0:
            return (1.0, SORTINO_NEUTRAL, SORTINO_NEUTRAL)

        # 年化收益（日均 × 252）
        r_p_annual = float(np.mean(returns_arr)) * TRADING_DAYS
        mar_daily = MAR_ANNUAL / TRADING_DAYS

        # ── Sortino：下行偏差只统计 R_daily < MAR 的日子（§3.2.2）──
        # §3.4 施工要点 #13：分母用 n-1（总样本量，ddof=1），非 n_downside-1
        downside_mask = returns_arr < mar_daily
        downside_returns = returns_arr[downside_mask]
        n_downside = len(downside_returns)

        # downside 样本量门槛（§3.2.2 四件套 #1）——n_downside==0 被本门槛拦截，
        # 原"无下行日"分支不可达（2026-08-16 双轮审查 F5 裁定清理）
        if n_downside < DOWNSIDE_MIN_OBSERVATIONS:
            logger.warning(
                "downside 样本 %d < %d，Sortino 统计不可靠，PerformanceScore 强制中性 1.0",
                n_downside, DOWNSIDE_MIN_OBSERVATIONS,
            )
            return (1.0, SORTINO_NEUTRAL, SORTINO_NEUTRAL)

        # 标准 Sortino 下行偏差（§3.4 施工要点 #10/#13）：
        # 分母用总样本量 n-1（ddof=1，与 Sharpe np.std(ddof=1) 一致）
        sum_sq_downside = float(np.sum((downside_returns - mar_daily) ** 2))
        downside_deviation = math.sqrt(sum_sq_downside / max(n - 1, 1))
        annual_downside_dev = downside_deviation * math.sqrt(TRADING_DAYS)
        if annual_downside_dev > 0:
            sortino = (r_p_annual - MAR_ANNUAL) / annual_downside_dev
        else:
            sortino = SORTINO_CEILING

        # ── Sharpe：总标准差（对照指标，§3.2.2 gap 监控用）──
        if n > 1:
            total_deviation = float(np.std(returns_arr, ddof=1))
        else:
            total_deviation = 0.0
        annual_total_dev = total_deviation * math.sqrt(TRADING_DAYS)
        if annual_total_dev > 0:
            sharpe = (r_p_annual - MAR_ANNUAL) / annual_total_dev
        else:
            sharpe = 0.0

        # PerformanceScore 线性映射 [0,2] → [0.5,1.5]（§3.2.2）
        if sortino <= SORTINO_FLOOR:
            perf_score = PERF_SCORE_MIN
        elif sortino >= SORTINO_CEILING:
            perf_score = PERF_SCORE_MAX
        else:
            perf_score = PERF_SCORE_MIN + (sortino - SORTINO_FLOOR) / (
                SORTINO_CEILING - SORTINO_FLOOR
            ) * (PERF_SCORE_MAX - PERF_SCORE_MIN)

        # gap 监控（§3.2.2 四件套 #3）
        if sharpe > 0:
            gap = sortino / sharpe
            if gap > GAP_NORMAL_CEILING * GAP_SEVERE_MULTIPLIER:
                logger.warning(
                    "Sortino/Sharpe gap=%.2f 严重 inflated（>%.2f），疑似 downside 样本太少"
                    "或连胜期未遇回撤，建议复核 PerformanceScore",
                    gap, GAP_NORMAL_CEILING * GAP_SEVERE_MULTIPLIER,
                )
            elif gap > GAP_NORMAL_CEILING * GAP_WARNING_MULTIPLIER:
                logger.warning(
                    "Sortino/Sharpe gap=%.2f 疑似 inflated（>%.2f），标记复核",
                    gap, GAP_NORMAL_CEILING * GAP_WARNING_MULTIPLIER,
                )

        return (perf_score, sortino, sharpe)
