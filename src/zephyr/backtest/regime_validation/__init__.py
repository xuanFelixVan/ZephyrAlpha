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
]
