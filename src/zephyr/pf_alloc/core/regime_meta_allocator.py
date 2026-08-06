# [BLUEPRINT] MOD-PA-007 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md
# [MODULE] zephyr.pf_alloc.core.regime_meta_allocator
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.regime.core.regime_detector
# [CONSUMERS] MOD-POS-020(StrategyBook消费BudgetAllocation); MOD-POS-022(BudgetChangeHandler收BudgetChanged事件)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] allocation=normalize(Base×PerformanceScore×Shrinkage)Σ=1.0; floor≥5%防饿死cap≤40%防集中; Shrinkage≤1.0只减不增; shrinkage_enabled开关(C1验证); regime只回答"多谨慎"不回答"偏向谁"(PerformanceScore后验捕获); 不做alpha择时(移除RegimeScore)
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

A 模型（design_memo_001 §2.2）的 meta 层。消费 regime 检测器 (MOD-REGIME-001) 的
12 维灰度概率 + 各策略 PerformanceScore，通过 **Shrinkage 风险节流（只减不增）**
+ **PerformanceScore 后验分配**，产出各 StrategyBook 的资金预算占比。

核心裁定（design_memo_001 §2.2，2026-08-05）：移除 RegimeScore，regime 仅通过
Shrinkage 做风险节流。regime 只回答"现在该多谨慎"，不回答"现在该偏向哪个策略"——
后者由 PerformanceScore 后验 PnL 自然捕获。

分配公式：allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)
硬约束：floor ≥ 5%（防饿死），cap ≤ 40%（防集中）

开源实证（Morwane/multi-strategy-alpha-book）：regime 做 risk-throttle Sharpe +1.43 /
MaxDD −10.3%；regime 做 alpha-timing Sharpe +0.87（降）。数据印证：同信号用于进攻
有害，用于防守有益。

阶段：骨架（接口完整，实现待填充）。第二阶段上（design_memo_001 §4.2）。
依据: design_memo_001 §2.2 + discussion_001 §5（Shrinkage 二维公式）+ blueprint §2.3
SSoT: depgraph MOD-PA-007
Version: 0.1.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ShrinkageDetail:
    """Shrinkage 计算明细（归因用）。"""

    confidence_signal: float      # max(P) → 4 档映射 + 稀有态折扣
    risk_signal: float            # 13 参数聚合
    raw_shrinkage: float          # confidence × risk
    final_shrinkage: float        # ≤1.0（裁剪后）
    shrinkage_enabled: bool       # 验证开关（C1 一票否决）


@dataclass(frozen=True)
class BudgetAllocation:
    """各策略 budget 占比（CTR-PA-007）。

    两个层次：allocation_i（相对占比 Σ=1.0）回答"偏向哪个策略"；
    global_shrinkage（总暴露因子）回答"现在该多谨慎"。
    StrategyBook 实收 effective_budget = allocation_i × global_shrinkage。
    """

    allocations: dict[str, float]            # {strategy_id: 相对占比}，Σ=1.0，floor 5%~cap 40%
    global_shrinkage: float                  # 全局风险节流因子（0.21~1.0）
    effective_budgets: dict[str, float]      # {strategy_id: allocation_i × global_shrinkage}
    shrinkage_detail: ShrinkageDetail
    rebalance_allowed: bool = True           # 当日是否允许再平衡（频率控制 ≤1次/日）
    created_at: datetime = field(default_factory=datetime.now)
    schema_version: str = "1.0"


class RegimeMetaAllocator:
    """Regime 元分配器（MOD-PA-007）。

    使用方式：
        allocator = RegimeMetaAllocator(base_weights={"s1": 0.34, ...}, shrinkage_enabled=True)
        budget = allocator.allocate(regime_probs, performance_scores, risk_inputs)

    骨架阶段：方法签名完整，实现待填充。
    """

    FLOOR: float = 0.05   # 防饿死
    CAP: float = 0.40     # 防集中

    def __init__(
        self,
        base_weights: dict[str, float] | None = None,
        shrinkage_enabled: bool = True,
    ) -> None:
        """初始化。

        Args:
            base_weights: 先验权重（等权 1/N 或人工先验），新策略冷启动只用这个。
            shrinkage_enabled: Shrinkage 开关（discussion_002 C1 验证，默认 True）。
                True → global_shrinkage = ConfidenceSignal × RiskSignal
                False → global_shrinkage = 1.0（C1 开/关对比基准，一票否决）
        """
        self.base_weights = base_weights or {}
        self.shrinkage_enabled = shrinkage_enabled

    # ── 公共接口 ──────────────────────────────────────────────────────

    def allocate(
        self,
        regime_probabilities: Any,         # RegimeProbabilities（避免循环导入用 Any）
        performance_scores: dict[str, float],
        risk_signal_inputs: dict[str, Any],
        strategy_sample_days: dict[str, int] | None = None,
    ) -> BudgetAllocation:
        """主入口：Shrinkage 节流 + PerformanceScore 后验分配 → BudgetAllocation。

        公式：allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)
        硬约束：floor ≥ 5%（防饿死），cap ≤ 40%（防集中）

        Args:
            regime_probabilities: regime 检测器 12 维灰度概率（MOD-REGIME-001）。
            performance_scores: {strategy_id: 60日滚动Sharpe→[0.5,1.5]}。
            risk_signal_inputs: RiskSignal 13 参数输入。
            strategy_sample_days: 各策略样本天数（<30 天额外收缩）。
        """
        shrinkage = self._compute_shrinkage(regime_probabilities, risk_signal_inputs)
        raw_alloc = self._compute_raw_allocation(performance_scores, shrinkage, strategy_sample_days)
        raise NotImplementedError("骨架：待实现 normalize + floor/cap 裁剪 + effective_budgets")

    # ── 子方法（待实现）──────────────────────────────────────────────

    def _compute_shrinkage(
        self, regime_probabilities: Any, risk_signal_inputs: dict[str, Any]
    ) -> ShrinkageDetail:
        """Shrinkage = ConfidenceSignal × RiskSignal（可开关）。

        - shrinkage_enabled=True  → ConfidenceSignal(max(P) 4档) × RiskSignal(13参数)
        - shrinkage_enabled=False → 1.0（C1 验证基准，一票否决）
        """
        if not self.shrinkage_enabled:
            return ShrinkageDetail(
                confidence_signal=1.0, risk_signal=1.0,
                raw_shrinkage=1.0, final_shrinkage=1.0, shrinkage_enabled=False,
            )
        raise NotImplementedError("骨架：待实现 ConfidenceSignal(max(P) 4档+稀有态折扣) × RiskSignal(13参数)")

    def _compute_raw_allocation(
        self,
        performance_scores: dict[str, float],
        shrinkage: ShrinkageDetail,
        strategy_sample_days: dict[str, int] | None,
    ) -> dict[str, float]:
        """Base × PerformanceScore × Shrinkage（归一化前）。

        样本 <30 天的策略额外收缩（SampleShrinkage）。
        """
        raise NotImplementedError("骨架：待实现 Base×Performance×Shrinkage + SampleShrinkage")

    def _normalize_and_clip(self, raw_alloc: dict[str, float]) -> dict[str, float]:
        """归一化 + floor 5% / cap 40% 硬约束。"""
        raise NotImplementedError("骨架：待实现归一化 + floor/cap 裁剪 + 再归一化")
