# [BLUEPRINT] MOD-EX_SOR | (pending)
# [MODULE] zephyr.ex_sor.services
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_sor/test_slippage_analyzer.py; tests/ex_sor/test_transaction_cost_optimizer.py; tests/ex_sor/test_execution_quality_scorer.py
# [A_module] module_id=MOD-EX_SOR | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ex_sor/services — 滑点分析 / 成本优化 / 质量评分

from typing import Final

from zephyr.ex_sor.services.execution_quality_scorer import (
    DefaultBenchmarkProvider,
    ExecutionDimensionScore,
    ExecutionQualityResult,
    ExecutionQualityScorer,
    InsufficientMetricsError,
    InvalidWeightsError,
    QualityBenchmarkProvider,
    QualityDimension,
    QualityScorerError,
    QualityWeights,
)
from zephyr.ex_sor.services.slippage_analyzer import (
    InsufficientFillsError,
    InvalidBenchmarkError,
    SlippageAnalyzer,
    SlippageAnalyzerError,
    SlippageAttribution,
    SlippageBenchmark,
    SlippageFillRecord,
    SlippageMetric,
    SlippagePredictor,
    SlippageResult,
    SquareRootImpactPredictor,
)
from zephyr.ex_sor.services.transaction_cost_optimizer import (
    CostComponent,
    FeeSchedule,
    ImpactCostEstimator,
    InvalidCostInputError,
    InvalidFeeScheduleError,
    LinearImpactEstimator,
    OptimizationAdvice,
    TransactionCostBreakdown,
    TransactionCostError,
    TransactionCostOptimizer,
    TransactionCostResult,
)

__all__: Final = [
    # XS-EXT-001 Slippage Analyzer
    "SlippageAnalyzer",
    "SlippageFillRecord",
    "SlippageBenchmark",
    "SlippageMetric",
    "SlippageAttribution",
    "SlippageResult",
    "SlippagePredictor",
    "SquareRootImpactPredictor",
    "SlippageAnalyzerError",
    "InsufficientFillsError",
    "InvalidBenchmarkError",
    # XS-EXT-003 Transaction Cost Optimizer
    "TransactionCostOptimizer",
    "FeeSchedule",
    "CostComponent",
    "TransactionCostBreakdown",
    "TransactionCostResult",
    "OptimizationAdvice",
    "ImpactCostEstimator",
    "LinearImpactEstimator",
    "TransactionCostError",
    "InvalidFeeScheduleError",
    "InvalidCostInputError",
    # XS-EXT-002 Execution Quality Scorer
    "ExecutionQualityScorer",
    "QualityDimension",
    "QualityWeights",
    "ExecutionDimensionScore",
    "ExecutionQualityResult",
    "QualityBenchmarkProvider",
    "DefaultBenchmarkProvider",
    "QualityScorerError",
    "InvalidWeightsError",
    "InsufficientMetricsError",
]
