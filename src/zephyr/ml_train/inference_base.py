# [BLUEPRINT] MOD-L11-001 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train.inference_base
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] zephyr.trading.trading_contracts.execution.model_serving_request; zephyr.shared.contracts.experiment.model_serving_response; zephyr.ml_train.trainer_base
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L11-001-inference_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
D_ML_TRAIN — ML Inference Base

模型推理引擎抽象基类。
"""

from __future__ import annotations

import abc
from typing import ClassVar

from zephyr.shared.contracts.experiment.model_serving_response import ModelServingResponse
from zephyr.trading.trading_contracts.execution.model_serving_request import ModelServingRequest


class InferenceEngineBase(abc.ABC):
    """
    推理引擎抽象基类（OCP 扩展点 D_ML_TRAIN-INF）

    契约对齐：CTR-P1-004（ModelServingRequest 入站）→ CTR-P1-005（ModelServingResponse 出站）

    实现者要求：
      - predict(): 接收推理请求，返回标准化推理响应
      - 必须包含 inference_ms 和 confidence
      - idempotency_key（INV-007）：每个推理请求必须关联幂等键
    """

    _registry: ClassVar[dict[str, type[InferenceEngineBase]]] = {}

    @abc.abstractmethod
    def predict(self, request: ModelServingRequest) -> ModelServingResponse:
        """模型推理：请求 → 响应"""
        ...

    def batch_predict(self, requests: list[ModelServingRequest]) -> list[ModelServingResponse]:
        """批量推理（可选覆盖）"""
        raise NotImplementedError


__all__ = [
    "InferenceEngineBase",
]

# Re-export from trainer_base for backward compatibility
from zephyr.ml_train.trainer_base import ModelMetadata, ModelRegistry, ModelTrainerBase  # noqa: F401
