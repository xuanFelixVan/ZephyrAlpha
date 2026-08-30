# [A_module] module_id=MOD-GOV-init | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
"""
Intelligence — Model Evaluation Concrete Implementations

Phase C 具体实现包。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations, BacktestConfig, DefaultBacktestEngine, DefaultInferenceE…
#   code: __init__.py import L45
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 BacktestConfig, DefaultBacktestEngine, DefaultInferenceEngine, default_infe…
#   desc: __init__ import L45；__all__ 4 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（4 符号）
#   name_en: __all__
#   intro: BacktestConfig, DefaultBacktestEngine, DefaultInferenceEngine, default_inferenc…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
    "default_inference_engine",
]
