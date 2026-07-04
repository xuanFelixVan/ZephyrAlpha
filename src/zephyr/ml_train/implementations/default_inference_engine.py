# [BLUEPRINT] MOD-L11-001 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train.implementations.default_inference_engine
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] zephyr.ml_train.inference_base; zephyr.ml_train.trainer_base; zephyr.trading.trading_contracts.execution.model_serving_request; zephyr.shared.contracts.experiment.model_serving_response
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_default_inference_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""D_ML_TRAIN — Default Inference Engine

ML 推理引擎具体实现。实现 InferenceEngineBase。

CTR 契约：
  消费者 — CTR-006 (PositionSnapshot) ← D_EXECUTION_CORE
  生产者 — CTR-P1-004 (ModelServingRequest) → D_SIGNAL/D_PORTFOLIO_CORE
  生产者 — CTR-P1-005 (ModelServingResponse) → D_SIGNAL/D_PORTFOLIO_CORE

SSoT: cross_layer_contracts.yaml → CTR-P1-004 + CTR-P1-005
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

from zephyr.ml_train.inference_base import InferenceEngineBase
from zephyr.ml_train.trainer_base import ModelMetadata
from zephyr.shared.contracts.experiment.model_serving_response import ModelServingResponse
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.trading.trading_contracts.execution.model_serving_request import ModelServingRequest

_logger = logging.getLogger(__name__)

# 5.117.1 修复：joblib.load 底层使用 pickle，是已知 RCE sink。
# 限定模型路径必须在项目 data 目录下，防止路径穿越和恶意文件加载。
_ALLOWED_MODEL_ROOT = (REPO_ROOT / "data").resolve()

__inference_id__ = "default-inference-engine"


class DefaultInferenceEngine(InferenceEngineBase):
    """默认推理引擎——模型加载 + 预测"""

    __inference_id__ = __inference_id__

    def __init__(self, model_registry: dict[str, Any] | None = None):
        self._models: dict[str, Any] = {}
        self._metadatas: dict[str, ModelMetadata] = {}
        self._model_registry = model_registry or {}

    def load_model(self, model_id: str, model_path: str) -> bool:
        metadata = ModelMetadata(
            model_id=model_id,
            model_type="unknown",
            model_version="1.0.0",
            features=[],
            target="regression",
            framework="auto",
        )

        try:
            import joblib

            # 5.117.1 修复：路径白名单校验，防止路径穿越和恶意模型文件加载
            resolved = Path(model_path).resolve()
            if not str(resolved).startswith(str(_ALLOWED_MODEL_ROOT)):
                raise ValueError(
                    f"model_path must be under {_ALLOWED_MODEL_ROOT}, got {resolved}"
                )
            self._models[model_id] = joblib.load(resolved)
            self._metadatas[model_id] = metadata
            _logger.info("Model loaded: model_id=%s path=%s", model_id, model_path)
            return True
        except Exception as e:
            _logger.error("Failed to load model: model_id=%s error=%s", model_id, e)

            if model_id in self._model_registry:
                self._models[model_id] = self._model_registry[model_id]
                self._metadatas[model_id] = metadata
                _logger.info("Model loaded from registry: model_id=%s", model_id)
                return True

            return False

    def predict(self, request: ModelServingRequest) -> ModelServingResponse:
        model_id = request.model_id
        model = self._models.get(model_id)

        start = time.perf_counter()

        if model is None:
            inference_ms = int((time.perf_counter() - start) * 1000)
            return ModelServingResponse(
                request_id=request.request_id,
                model_id=model_id,
                prediction=0.0,
                prediction_type="regression",
                confidence=0.0,
                inference_ms=inference_ms,
                idempotency_key=request.idempotency_key,
            )

        try:
            if hasattr(model, "predict"):
                import numpy as np

                feature_values = list(request.input_features.values())
                feature_array = np.array([feature_values])
                raw_pred = model.predict(feature_array)
                prediction = float(raw_pred[0]) if hasattr(raw_pred, "__getitem__") else float(raw_pred)
            else:
                prediction = 0.0

            inference_ms = int((time.perf_counter() - start) * 1000)

            return ModelServingResponse(
                request_id=request.request_id,
                model_id=model_id,
                prediction=prediction,
                prediction_type="regression",
                confidence=0.85,
                inference_ms=inference_ms,
                idempotency_key=request.idempotency_key,
            )
        except Exception as e:
            _logger.error("Prediction failed: model_id=%s error=%s", model_id, e)
            inference_ms = int((time.perf_counter() - start) * 1000)
            return ModelServingResponse(
                request_id=request.request_id,
                model_id=model_id,
                prediction=0.0,
                prediction_type="regression",
                confidence=0.0,
                inference_ms=inference_ms,
                idempotency_key=request.idempotency_key,
            )

    def get_model_metadata(self, model_id: str) -> ModelMetadata | None:
        return self._metadatas.get(model_id)

    def list_models(self) -> list[str]:
        return list(self._models.keys())


__all__ = ["DefaultInferenceEngine"]
