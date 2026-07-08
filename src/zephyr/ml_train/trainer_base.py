# [BLUEPRINT] MOD-L11-001 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train.trainer_base
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-L11-001-trainer_base | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
D_ML_TRAIN — ML Training Base

模型训练核心抽象。包含模型元数据、训练器基类和模型注册表。
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar


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
    模型训练器抽象基类（OCP 扩展点 D_ML_TRAIN-TRN）

    实现者要求：
      - train(): 接收训练数据，产出训练指标
      - validate(): 验证模型性能，返回验证指标
      - 训练完成后将模型注册到 ModelRegistry
    """

    _registry: ClassVar[dict[str, type[ModelTrainerBase]]] = {}

    @abc.abstractmethod
    def train(self, features: dict[str, Any], target: Any, idempotency_key: str) -> dict[str, float]:
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
    模型注册表（OCP 扩展点 D_ML_TRAIN-REG）

    管理模型版本生命周期：
      - 注册（register）-> 激活（activate）-> 废弃（deprecate）
      - 每模型保留完整 lineage（训练数据 -> 特征 -> 参数 -> 指标）
    """

    _registry: ClassVar[dict[str, type[ModelTrainerBase]]] = {}

    @classmethod
    def register(cls, trainer_cls: type[ModelTrainerBase]) -> type[ModelTrainerBase]:
        """注册训练器类，关联模型 ID"""
        if not hasattr(trainer_cls, "__model_id__"):
            raise AttributeError(f"{trainer_cls.__name__} 缺少 __model_id__ 属性")
        mid = trainer_cls.__model_id__
        if mid in cls._registry:
            raise ValueError(f"模型 ID {mid!r} 已注册")
        cls._registry[mid] = trainer_cls
        return trainer_cls

    @classmethod
    def get(cls, model_id: str) -> type[ModelTrainerBase]:
        if model_id not in cls._registry:
            raise KeyError(f"Model trainer not registered: {model_id!r}. Available: {list(cls._registry.keys())}")  # 5.99.17 修复: 附加说明文字和可用列表
        return cls._registry[model_id]

    @classmethod
    def clear(cls) -> None:
        cls._registry.clear()


__all__ = [
    "ModelMetadata",
    "ModelRegistry",
    "ModelTrainerBase",
]
