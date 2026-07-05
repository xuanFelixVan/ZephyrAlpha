# [A_module] module_id=MOD-RSC_implementations | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model-capability-exam/blueprint.md
# [MODULE] zephyr.intelligence.model_evaluation.implementations
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""Intelligence — Model Evaluation Concrete Implementations

Phase C 具体实现包。
"""

from __future__ import annotations

from zephyr.backtest.implementations.vectorized_engine import (
    BacktestConfig,
    DefaultBacktestEngine,
)
from zephyr.intelligence.model_evaluation.implementations.default_inference_engine import (
    DefaultInferenceEngine,
)

__all__ = [
    "BacktestConfig",
    "DefaultBacktestEngine",
    "DefaultInferenceEngine",
    "default_backtest_engine",
    "default_inference_engine",
    "implementations",
]
