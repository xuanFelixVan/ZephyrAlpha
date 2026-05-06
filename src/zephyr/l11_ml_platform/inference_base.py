"""
L11 — ML Platform Layer

机器学习平台层。负责模型训练、注册、推理和监控。

核心职责：
  - 模型注册（model_id / version / metadata / lineage）
  - 模型训练管线（特征工程 → 训练 → 验证 → 注册）
  - 模型推理服务（ModelServingRequest → ModelServingResponse）
  - 模型监控（漂移检测 / 性能退化告警）

扩展点：
  - ModelTrainerBase    : OCP L11-TRN — 模型训练
  - ModelRegistry       : OCP L11-REG — 模型注册与版本管理
  - InferenceEngineBase : OCP L11-INF — 模型推理服务

依赖方向：L02 → L11（特征输入）；L11 → L03/L05（推理输出给信号/决策层）
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar

from zephyr.shared.contracts.model_serving_request import ModelServingRequest
from zephyr.shared.contracts.model_serving_response import ModelServingResponse


@dataclass(frozen=True)
class ModelMetadata:
    """模型注册元数据"""
    model_id: str
    model_version: str
    model_type: str
    framework: str
    features: list[str]
    target: str
    metrics: dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "registered"


class ModelTrainerBase(abc.ABC):
    """
    模型训练器抽象基类（OCP 扩展点 L11-TRN）

    实现者要求：
      - train(): 接收训练数据，产出训练指标
      - validate(): 验证模型性能，返回验证指标
      - 训练完成后将模型注册到 ModelRegistry
    """
    _registry: ClassVar[dict[str, type["ModelTrainerBase"]]] = {}

    @abc.abstractmethod
    def train(self, features: dict[str, Any], target: Any,
              idempotency_key: str) -> dict[str, float]:
        """训练模型，返回训练指标"""
        ...

    @abc.abstractmethod
    def validate(self, features: dict[str, Any], target: Any) -> dict[str, float]:
        """验证模型，返回验证指标"""
        ...

    def save_model(self, path: str) -> None:
        """持久化模型（可选覆盖）"""
        raise NotImplementedError


class ModelRegistry:
    """
    模型注册表（OCP 扩展点 L11-REG）

    管理模型版本生命周期：
      - 注册（register）→ 激活（activate）→ 废弃（deprecate）
      - 每模型保留完整 lineage（训练数据 → 特征 → 参数 → 指标）
    """
    _registry: ClassVar[dict[str, type[ModelTrainerBase]]] = {}

    @classmethod
    def register(cls, trainer_cls: type[ModelTrainerBase]) -> type[ModelTrainerBase]:
        """注册训练器类，关联模型 ID"""
        if not hasattr(trainer_cls, "__model_id__"):
            raise AttributeError(
                f"{trainer_cls.__name__} 缺少 __model_id__ 属性"
            )
        mid = trainer_cls.__model_id__
        if mid in cls._registry:
            raise ValueError(f"模型 ID {mid!r} 已注册")
        cls._registry[mid] = trainer_cls
        return trainer_cls

    @classmethod
    def get(cls, model_id: str) -> type[ModelTrainerBase]:
        if model_id not in cls._registry:
            raise KeyError(model_id)
        return cls._registry[model_id]

    @classmethod
    def clear(cls) -> None:
        cls._registry.clear()


class InferenceEngineBase(abc.ABC):
    """
    推理引擎抽象基类（OCP 扩展点 L11-INF）

    契约对齐：CTR-P1-004（ModelServingRequest 入站）→ CTR-P1-005（ModelServingResponse 出站）

    实现者要求：
      - predict(): 接收推理请求，返回标准化推理响应
      - 必须包含 inference_ms 和 confidence
      - idempotency_key（INV-007）：每个推理请求必须关联幂等键
    """
    _registry: ClassVar[dict[str, type["InferenceEngineBase"]]] = {}

    @abc.abstractmethod
    def predict(self, request: ModelServingRequest) -> ModelServingResponse:
        """模型推理：请求 → 响应"""
        ...

    def batch_predict(self, requests: list[ModelServingRequest]) -> list[ModelServingResponse]:
        """批量推理（可选覆盖）"""
        raise NotImplementedError


__all__ = [
    "ModelMetadata",
    "ModelTrainerBase",
    "ModelRegistry",
    "InferenceEngineBase",
]
