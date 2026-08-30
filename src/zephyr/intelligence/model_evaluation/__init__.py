# [A_module] module_id=MOD-INF-036 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model-capability-exam/blueprint.md
# [MODULE] zephyr.intelligence.model_evaluation
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
Intelligence — Model Evaluation Domain

模型评估、推理、知识库统一域。
包含原 research/ 和 ml_train/ 的核心模块。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations
#   code: __init__.py import L46
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 ActivateGate, InferenceEngineBase, ModelMetadata, ModelRegistry, ModelTrain…
#   desc: __init__ import L46；__all__ 11 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（11 符号）
#   name_en: __all__
#   intro: ActivateGate, InferenceEngineBase, ModelMetadata, ModelRegistry, ModelTrainerBa…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


def __getattr__(name):
    """Lazy imports to avoid triggering circular import chains at package load time."""
    _lazy = {
        "UnifiedMemoryAPI": ".unified_memory_api",
        "Reranker": ".reranker",
        "ActivateGate": ".activate",
        "InferenceEngineBase": ".inference_base",
        "ModelMetadata": ".inference_base",
        "ModelRegistry": ".inference_base",
        "ModelTrainerBase": ".inference_base",
    }
    if name in _lazy:
        import importlib

        mod = importlib.import_module(_lazy[name], __name__)
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ActivateGate",
    "InferenceEngineBase",
    "ModelMetadata",
    "ModelRegistry",
    "ModelTrainerBase",
    "Reranker",
    "UnifiedMemoryAPI",
    "activate",
    "inference_base",
    "reranker",
    "unified_memory_api",
]
