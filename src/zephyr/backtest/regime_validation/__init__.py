# [BLUEPRINT] MOD-BT-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=PKG-bt-regime-validation | layer=package | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #11_regime_backtest_validation_plan #C1-shrinkage-comparator
"""D_BACKTEST — Regime 回测验证包（11_regime_backtest_validation_plan 验证方案落地）。

对接现有 BM-BT 回测框架，为 regime 检测器 (MOD-REGIME-001) 提供验证工具：
  - ShrinkageProvider 系列 (B2): 对接 RegimeDetector / mock / 查表
  - C1ShrinkageComparator (C1): Shrinkage 开/关对比 + 一票否决（11_regime_backtest_validation_plan §4.3/§5）

依赖方向: backtest → regime（消费 regime 的 ShrinkageResult），符合
11_regime_backtest_validation_plan §2.1 "regime 验证复用现有 BM-BT 框架" 的对接约定。
"""
from zephyr.backtest.regime_validation.c1_comparator import (
    C1ComparisonResult,
    C1Config,
    C1MetricVerdict,
    C1ShrinkageComparator,
    C1ShrinkageComparatorError,
)
from zephyr.backtest.regime_validation.c2_extreme_event_protection import (
    C2EventResult,
    C2ProtectionError,
    C2ProtectionReport,
    evaluate_extreme_event_protection,
    max_drawdown_of,
)
from zephyr.backtest.regime_validation.c3_throttle_attribution import (
    C3AttributionError,
    C3AttributionReport,
    C3StateAttribution,
    attribute_throttle,
)
from zephyr.backtest.regime_validation.c4_deflated_sharpe_runner import (
    C4BatchReport,
    C4DeflatedSharpeError,
    C4VariantDSR,
    run_deflated_sharpe_batch,
)
from zephyr.backtest.regime_validation.e2_stationary_bootstrap import (
    E2BootstrapConfig,
    E2BootstrapError,
    E2BootstrapResult,
    annualized_sharpe,
    bootstrap_sharpe_difference,
    stationary_bootstrap_indices,
)
from zephyr.backtest.regime_validation.e3_param_sensitivity import (
    E3ParamVerdict,
    E3PerturbationPoint,
    E3SensitivityError,
    E3SensitivityReport,
    analyze_param_sensitivity,
    perturb_pm20,
)
from zephyr.backtest.regime_validation.e4_cost_sensitivity import (
    E4CostPoint,
    E4CostReport,
    E4CostSensitivityError,
    analyze_cost_sensitivity,
)
from zephyr.backtest.regime_validation.shrinkage_provider import (
    ConstShrinkageProvider,
    MockShrinkageProvider,
    RegimeDetectorShrinkageAdapter,
    ScheduleShrinkageProvider,
    ShrinkageProviderError,
    build_schedule_from_detector,
    build_schedule_from_results,
    clamp_shrinkage,
)

__all__ = [
    # B2: providers
    "ConstShrinkageProvider",
    "ScheduleShrinkageProvider",
    "MockShrinkageProvider",
    "RegimeDetectorShrinkageAdapter",
    "ShrinkageProviderError",
    "clamp_shrinkage",
    "build_schedule_from_results",
    "build_schedule_from_detector",
    # C1: comparator
    "C1Config",
    "C1MetricVerdict",
    "C1ComparisonResult",
    "C1ShrinkageComparator",
    "C1ShrinkageComparatorError",
    # C2: 极端事件回撤保护（分析型）
    "C2EventResult",
    "C2ProtectionError",
    "C2ProtectionReport",
    "evaluate_extreme_event_protection",
    "max_drawdown_of",
    # C3: 节流归因（分析型）
    "C3AttributionError",
    "C3AttributionReport",
    "C3StateAttribution",
    "attribute_throttle",
    # C4: Deflated Sharpe 跑批封装
    "C4BatchReport",
    "C4DeflatedSharpeError",
    "C4VariantDSR",
    "run_deflated_sharpe_batch",
    # E2: stationary bootstrap
    "E2BootstrapConfig",
    "E2BootstrapError",
    "E2BootstrapResult",
    "annualized_sharpe",
    "bootstrap_sharpe_difference",
    "stationary_bootstrap_indices",
    # E3: 参数敏感性 ±20%
    "E3ParamVerdict",
    "E3PerturbationPoint",
    "E3SensitivityError",
    "E3SensitivityReport",
    "analyze_param_sensitivity",
    "perturb_pm20",
    # E4: 交易成本敏感性 0-50bps
    "E4CostPoint",
    "E4CostReport",
    "E4CostSensitivityError",
    "analyze_cost_sensitivity",
]
