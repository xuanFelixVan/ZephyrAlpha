# [A_module] module_id=MOD-RSC_experiment_tracker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model-capability-exam/blueprint.md
# [MODULE] zephyr.intelligence.model_evaluation.experiment_tracker
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""D_RESEARCH — Research & Innovation Concrete Implementations

Phase C 具体实现包。

实现清单：
  - DefaultBacktestEngine : BacktestEngineBase 的具体实现（向量化日频回测）
"""

from zephyr.backtest.implementations.vectorized_engine import (
    BacktestConfig,
    DefaultBacktestEngine,
)

__all__ = ["BacktestConfig", "DefaultBacktestEngine", "default_backtest_engine"]
