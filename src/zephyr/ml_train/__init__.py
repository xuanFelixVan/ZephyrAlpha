# [A_module] module_id=MOD-L11-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L11-001 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train
# [DOMAIN] D_ML_TRAIN
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

D_ML_TRAIN — ML Training Domain

ML训练域统一包。包含模型训练、注册、推理的核心抽象和实现。

子模块:
  trainer_base.py   — 模型训练器/注册表/元数据 (ModelTrainerBase, ModelRegistry, ModelMetadata)
  inference_base.py — 推理引擎基类 (InferenceEngineBase)
  implementations/  — 具体实现 (DefaultInferenceEngine)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包属性访问 请求
#   fields: name 属性名（5个公开符号之一）
#   code: __getattr__(name) L36
# 层: 算法
# - id: A1
#   name_zh: ① ML训练域符号懒加载导出
#   name_en: __getattr__ + _lazy 映射
#   intro: 按需加载训练器/注册表/推理引擎基类，不进 __all__ 即抛 AttributeError
#   desc: _lazy 映射 5 符号到 trainer_base/inference_base/implementations.default_inference_engine，命中即 importlib.import_module 取符号（L36-49）
#   inputs: I1
#   outputs: ModelTrainerBase/ModelRegistry/ModelMetadata/InferenceEngineBase/DefaultInferenceEngine
# 层: 输出
# - id: O1
#   name_zh: ML训练域公共基类面
#   name_en: ml_train 公共符号集
#   intro: 对外暴露模型训练、注册、推理的核心抽象与默认实现
#   downstream: 无下游/内部使用（# [CONSUMERS] 头为空）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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


# ORPHAN-MODULE: 引用登记（让 depgraph 发现 import 边；纯 stdlib 模块，eager 安全）
from zephyr.ml_train.experiment_anomaly_detector import detect_experiment_anomalies  # noqa: F401
