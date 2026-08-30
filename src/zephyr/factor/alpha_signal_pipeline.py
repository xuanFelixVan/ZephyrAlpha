# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.alpha_signal_pipeline
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.signal_fundamental.pipeline
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK-alpha_signal_pipeline | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# Re-export from signal domain SSoT — zephyr.signal_fundamental.pipeline
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: alpha_signal_pipeline.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 AlphaSignalPipeline, PipelineError, PipelineResult, PipelineStage（共 4 符号）
#   desc: __init__ import L0；__all__ 4 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（4 符号）
#   name_en: __all__
#   intro: AlphaSignalPipeline, PipelineError, PipelineResult, PipelineStage
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.signal_fundamental.pipeline import (
    AlphaSignalPipeline,
    PipelineError,
    PipelineResult,
    PipelineStage,
)

__all__ = [
    "AlphaSignalPipeline",
    "PipelineError",
    "PipelineResult",
    "PipelineStage",
]
