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
"""Intelligence — Model Evaluation Domain

模型评估、推理、知识库统一域。
包含原 research/ 和 ml_train/ 的核心模块。
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
