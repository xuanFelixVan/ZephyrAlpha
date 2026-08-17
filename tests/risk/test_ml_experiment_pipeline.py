# [A_test] module_id: MOD-GOV_ml_experiment_pipeline | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] tests.test_ml_experiment_pipeline
# [INVARIANTS] must test all public classes and methods of ml_experiment_pipeline
# [MODIFY-GUARD] ml_experiment_pipeline.py changes require sync
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/test_ml_experiment_pipeline.py
# [TTL] task_bound

from unittest.mock import MagicMock

from zephyr.risk.cross_asset.cross_market_data_adapter.ml_experiment_pipeline import (
    ExperimentResult,
    MLExperimentPipeline,
    PipelineError,
    PipelineStage,
)


class TestPipelineStage:
    def test_enum_values(self):
        assert PipelineStage.MODEL_DISCOVERY.value == "model_discovery"
        assert PipelineStage.INFERENCE_EXEC.value == "inference_exec"
        assert PipelineStage.METRIC_COLLECTION.value == "metric_collection"
        assert PipelineStage.STATISTICS_VALIDATE.value == "statistics_validate"
        assert PipelineStage.PRODUCTION_PROMOTE.value == "production_promote"

    def test_enum_count(self):
        assert len(PipelineStage) == 5


class TestPipelineError:
    # 治本（2026-07-17）：PipelineError 已 SSoT 化到 zephyr.shared.foundation.errors（5.76.1 修复）。
    # 旧签名 PipelineError(stage, message, detail=None) + .stage/.detail 属性已废弃。
    # 新签名 PipelineError(message, *, details=None, error_code=None) + .message/.details/.error_code 属性。
    # stage 信息现编码到 message 字符串中（本模块不再 raise PipelineError，仅 re-export）。
    def test_instantiation(self):
        err = PipelineError("[inference_exec] test")
        assert "[inference_exec]" in err.message
        assert "[inference_exec]" in str(err)
        assert err.error_code == "ZA-SH-0007"

    def test_with_detail(self):
        err = PipelineError("[model_discovery] fail", details={"x": 1})
        assert err.details == {"x": 1}


class TestExperimentResult:
    def test_default_values(self):
        r = ExperimentResult(
            pipeline_id="e1",
            status="running",
            stage=PipelineStage.MODEL_DISCOVERY,
        )
        assert r.models_discovered == 0
        assert r.inferences_run == 0
        assert r.inferences_failed == 0
        assert r.metrics_collected == 0
        assert r.significant_results == 0
        assert r.best_model is None
        assert r.best_effect_size == 0.0
        assert r.promoted is False
        assert r.errors == []

    def test_custom_values(self):
        r = ExperimentResult(
            pipeline_id="e2",
            status="completed",
            stage=PipelineStage.PRODUCTION_PROMOTE,
            models_discovered=3,
            inferences_run=2,
            significant_results=1,
            best_model="model_a",
            best_effect_size=0.5,
            promoted=True,
        )
        assert r.models_discovered == 3
        assert r.promoted is True


class TestMLExperimentPipeline:
    def setup_method(self):
        # 治本（2026-08-17 #108）：状态隔离走真源设计的公共 API reset_run_state()，
        # 不再直接写 global_run_count/seen_idempotency_keys 公共别名——
        # 两者是 R5 公共化批次机械生成的值拷贝别名（int 赋值即分叉、set 重绑定即分叉），
        # 对 _global_run_count/_seen_idempotency_keys 真源零效果（写死路）。
        MLExperimentPipeline.reset_run_state()

    def test_instantiation(self):
        pipe = MLExperimentPipeline()
        assert pipe.models == []
        assert pipe.engines == []

    def test_run_no_models(self):
        pipe = MLExperimentPipeline()
        result = pipe.run()
        assert result.status == "no_models"
        assert result.models_discovered == 0

    def test_run_with_custom_idempotency_key(self):
        pipe = MLExperimentPipeline()
        result = pipe.run(idempotency_key="key-abc")
        assert result.idempotency_key == "key-abc"

    def test_p_hacking_warning(self):
        # 治本（2026-08-17 #108）：p-hacking 检测真源=_global_run_count（run() 内自增，
        # 阈值 _MAX_RUNS_BEFORE_P_HACKING_WARNING=9）。原断言写公共别名 global_run_count=10
        # 系 R5 公共化机械改写引入的写死路（int 值拷贝别名），对真源零效果。
        # 对齐真源信号约定：经公开 run() 真实驱动 10 次（同 tests/ml_experiment/test_adversarial_ml.py
        # attack_03 的 20 次驱动模式），第 10 次越阈触发告警。
        pipe = MLExperimentPipeline()
        result = None
        for _ in range(10):
            result = pipe.run()
        assert result.status == "p_hacking_warning"
        assert any("p_hacking" in e.get("message", "") or "p-hacking" in e.get("message", "") for e in result.errors)

    def test_snapshot_builtins(self):
        snap = MLExperimentPipeline.snapshot_builtins()
        assert isinstance(snap, frozenset)
        assert "print" in snap

    def test_check_builtins_integrity_clean(self):
        snap = MLExperimentPipeline.snapshot_builtins()
        violations = MLExperimentPipeline.check_builtins_integrity(snap)
        assert violations == []

    def test_run_significance_test_empty(self):
        result = MLExperimentPipeline.run_significance_test([])
        assert result["significant_count"] == 0
        assert result["best_model"] is None

    def test_run_significance_test_with_data(self):
        preds = [
            {"model_id": "m1", "prediction": 0.5, "confidence": 0.96},
            {"model_id": "m2", "prediction": 0.3, "confidence": 0.8},
        ]
        result = MLExperimentPipeline.run_significance_test(preds)
        assert result["significant_count"] == 1
        assert result["best_model"] == "m1"

    def test_register_model(self):
        pipe = MLExperimentPipeline()
        meta = MagicMock()
        pipe.register_model(meta)
        assert len(pipe.models) == 1

    def test_register_engine(self):
        pipe = MLExperimentPipeline()
        engine = type("TestEngine", (), {})
        pipe.register_engine(engine)
        assert len(pipe.engines) == 1

    def test_run_with_mock_model_and_engine(self):
        pipe = MLExperimentPipeline()

        model_meta = MagicMock()
        model_meta.model_id = "test_model"
        model_meta.model_version = "1.0"
        model_meta.model_type = "classifier"
        model_meta.framework = "sklearn"
        model_meta.features = ["f1"]
        model_meta.target = "label"

        class MockEngine:
            __name__ = "test_model"

            def predict(self, features):
                pred = MagicMock()
                pred.prediction = 0.9
                pred.confidence = 0.97
                return pred

        pipe.register_model(model_meta)
        pipe.register_engine(MockEngine)
        result = pipe.run()
        assert result.models_discovered == 1
