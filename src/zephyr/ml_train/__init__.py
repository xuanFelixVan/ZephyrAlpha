# [A_module] module_id=MOD-L11-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L11-001 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""D_ML_TRAIN — ML Training Domain

ML训练域统一包。包含模型训练、注册、推理的核心抽象和实现。

子模块:
  trainer_base.py   — 模型训练器/注册表/元数据 (ModelTrainerBase, ModelRegistry, ModelMetadata)
  inference_base.py — 推理引擎基类 (InferenceEngineBase)
  implementations/  — 具体实现 (DefaultInferenceEngine)
"""

from __future__ import annotations

__all__ = [
    "DefaultInferenceEngine",
    "InferenceEngineBase",
    "ModelMetadata",
    "ModelRegistry",
    "ModelTrainerBase",
    "inference_base",
    "trainer_base",
]


def __getattr__(name):
    _lazy = {
        "ModelTrainerBase": ".trainer_base",
        "ModelRegistry": ".trainer_base",
        "ModelMetadata": ".trainer_base",
        "InferenceEngineBase": ".inference_base",
        "DefaultInferenceEngine": ".implementations.default_inference_engine",
    }
    if name in _lazy:
        import importlib

        mod = importlib.import_module(_lazy[name], __name__)
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
