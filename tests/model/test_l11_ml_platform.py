# [A_test] module_id: MOD-GOV_l11_ml_platform | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L11-001 | docs/03_modules/_domain_machine_learning_train/blueprint.md | §test
# [MODULE] zephyr.ml_serve.serving_orchestrator
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_l11_ml_platform.py
# [TTL] task_bound

from __future__ import annotations

from datetime import datetime

import pytest

mod = pytest.importorskip("zephyr.ml_train.inference_base")

ModelMetadata = mod.ModelMetadata
ModelTrainerBase = mod.ModelTrainerBase
ModelRegistry = mod.ModelRegistry
InferenceEngineBase = mod.InferenceEngineBase


class TestModelMetadata:
    def test_creation(self):
        meta = ModelMetadata(
            model_id="test-model",
            model_version="1.0",
            model_type="classifier",
            framework="sklearn",
            features=["f1", "f2"],
            target="label",
        )
        assert meta.model_id == "test-model"
        assert meta.model_version == "1.0"
        assert meta.model_type == "classifier"
        assert meta.framework == "sklearn"
        assert meta.features == ["f1", "f2"]
        assert meta.target == "label"
        assert meta.status == "registered"

    def test_frozen(self):
        meta = ModelMetadata(
            model_id="m1",
            model_version="1.0",
            model_type="regressor",
            framework="pytorch",
            features=["x"],
            target="y",
        )
        with pytest.raises(Exception):
            meta.model_id = "changed"

    def test_default_metrics(self):
        meta = ModelMetadata(
            model_id="m2",
            model_version="2.0",
            model_type="clf",
            framework="xgb",
            features=[],
            target="z",
        )
        assert meta.metrics == {}
        assert isinstance(meta.created_at, datetime)

    def test_custom_metrics(self):
        meta = ModelMetadata(
            model_id="m3",
            model_version="1.0",
            model_type="clf",
            framework="lr",
            features=[],
            target="y",
            metrics={"accuracy": 0.95, "f1": 0.90},
        )
        assert meta.metrics["accuracy"] == 0.95


class TestModelTrainerBase:
    def test_is_abstract(self):
        with pytest.raises(TypeError):
            ModelTrainerBase()

    def test_subclass_must_implement_train(self):
        class IncompleteTrainer(ModelTrainerBase):
            def validate(self, features, target):
                return {}

        with pytest.raises(TypeError):
            IncompleteTrainer()

    def test_concrete_subclass(self):
        class DummyTrainer(ModelTrainerBase):
            __model_id__ = "dummy-v1"

            def train(self, features, target, idempotency_key):
                return {"loss": 0.1}

            def validate(self, features, target):
                return {"accuracy": 0.9}

        trainer = DummyTrainer()
        result = trainer.train({}, None, "key-001")
        assert result == {"loss": 0.1}
        val = trainer.validate({}, None)
        assert val == {"accuracy": 0.9}

    def test_save_model_raises(self):
        class DummyTrainer(ModelTrainerBase):
            __model_id__ = "dummy-v2"

            def train(self, features, target, idempotency_key):
                return {}

            def validate(self, features, target):
                return {}

        trainer = DummyTrainer()
        with pytest.raises(NotImplementedError):
            trainer.save_model("/tmp/model")


class TestModelRegistry:
    def setup_method(self):
        ModelRegistry.clear()

    def test_register_and_get(self):
        class MyTrainer(ModelTrainerBase):
            __model_id__ = "reg-test-001"

            def train(self, features, target, idempotency_key):
                return {}

            def validate(self, features, target):
                return {}

        ModelRegistry.register(MyTrainer)
        result = ModelRegistry.get("reg-test-001")
        assert result is MyTrainer

    def test_register_duplicate_raises(self):
        class MyTrainer(ModelTrainerBase):
            __model_id__ = "reg-dup-001"

            def train(self, features, target, idempotency_key):
                return {}

            def validate(self, features, target):
                return {}

        ModelRegistry.register(MyTrainer)
        with pytest.raises(ValueError, match="已注册"):
            ModelRegistry.register(MyTrainer)

    def test_register_missing_model_id_raises(self):
        class NoIdTrainer(ModelTrainerBase):
            def train(self, features, target, idempotency_key):
                return {}

            def validate(self, features, target):
                return {}

        with pytest.raises(AttributeError, match="__model_id__"):
            ModelRegistry.register(NoIdTrainer)

    def test_get_nonexistent_raises(self):
        with pytest.raises(KeyError):
            ModelRegistry.get("nonexistent-model")

    def test_clear(self):
        class MyTrainer(ModelTrainerBase):
            __model_id__ = "reg-clear-001"

            def train(self, features, target, idempotency_key):
                return {}

            def validate(self, features, target):
                return {}

        ModelRegistry.register(MyTrainer)
        ModelRegistry.clear()
        with pytest.raises(KeyError):
            ModelRegistry.get("reg-clear-001")


class TestInferenceEngineBase:
    def test_is_abstract(self):
        with pytest.raises(TypeError):
            InferenceEngineBase()

    def test_subclass_must_implement_predict(self):
        class IncompleteEngine(InferenceEngineBase):
            def batch_predict(self, requests):
                return []

        with pytest.raises(TypeError):
            IncompleteEngine()

    def test_batch_predict_raises(self):
        class DummyEngine(InferenceEngineBase):
            def predict(self, request):
                return None

        engine = DummyEngine()
        with pytest.raises(NotImplementedError):
            engine.batch_predict([])
