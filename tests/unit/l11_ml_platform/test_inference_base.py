# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l11_ml_platform.test_inference_base
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""
单元测试：src/zephyr/l11_ml_platform/inference_base.py
=============================================================

覆盖矩阵：
  InferenceEngineBase (ABC):
    - 抽象类不可实例化 × 1
    - batch_predict 默认 NotImplementedError × 1
    - 注册表登记 × 1
  ModelTrainerBase (ABC):
    - 抽象类不可实例化 × 1
    - save_model 默认 NotImplementedError × 1
  ModelRegistry:
    - register / get / clear × 3
    - 重复注册 ValueError × 1
    - 缺少 __model_id__ AttributeError × 1
  ModelMetadata:
    - 默认 status × 1
"""

import pytest
from zephyr.l11_ml_platform.inference_base import (
    InferenceEngineBase,
    ModelMetadata,
    ModelRegistry,
    ModelTrainerBase,
)


class TestInferenceEngineBaseABC:
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            InferenceEngineBase()

    def test_batch_predict_default_raises(self):
        class MockInference(InferenceEngineBase):
            __inference_id__ = "mock_inf"

            def predict(self, request):
                return None

        engine = MockInference()
        with pytest.raises(NotImplementedError):
            engine.batch_predict([])

    def test_registry_exists(self):
        assert hasattr(InferenceEngineBase, "_registry")
        assert isinstance(InferenceEngineBase._registry, dict)


class TestModelTrainerBaseABC:
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            ModelTrainerBase()

    def test_save_model_default_raises(self):
        class MockTrainer(ModelTrainerBase):
            __model_id__ = "mock_trainer"

            def train(self, features, target, idempotency_key):
                return {}

            def validate(self, features, target):
                return {}

        t = MockTrainer()
        with pytest.raises(NotImplementedError):
            t.save_model("/tmp/model")


class TestModelRegistry:
    def setup_method(self):
        ModelRegistry.clear()

    def test_register_and_get(self):
        class RegTrainer(ModelTrainerBase):
            __model_id__ = "test_model_unit"

            def train(self, features, target, idempotency_key):
                return {}

            def validate(self, features, target):
                return {}

        ModelRegistry.register(RegTrainer)
        assert ModelRegistry.get("test_model_unit") is RegTrainer

    def test_duplicate_register_raises(self):
        class DupTrainer(ModelTrainerBase):
            __model_id__ = "dup_model"

            def train(self, features, target, idempotency_key):
                return {}

            def validate(self, features, target):
                return {}

        ModelRegistry.register(DupTrainer)
        with pytest.raises(ValueError, match="已注册"):
            ModelRegistry.register(DupTrainer)

    def test_missing_model_id_raises(self):
        class NoIdTrainer(ModelTrainerBase):
            def train(self, features, target, idempotency_key):
                return {}

            def validate(self, features, target):
                return {}

        with pytest.raises(AttributeError, match="__model_id__"):
            ModelRegistry.register(NoIdTrainer)


class TestModelMetadata:
    def test_default_status(self):
        m = ModelMetadata(
            model_id="m1",
            model_version="1.0",
            model_type="xgboost",
            framework="sklearn",
            features=["f1"],
            target="return",
        )
        assert m.status == "registered"
