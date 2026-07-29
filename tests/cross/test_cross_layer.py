# [A_test] module_id: MOD-GOV_cross_layer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §test
# [MODULE] zephyr.cross_asset.cross_market_data_adapter
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_cross_layer.py
# [TTL] task_bound

from __future__ import annotations

import pytest

alpha_mod = pytest.importorskip("zephyr.cross_asset.cross_market_data_adapter.alpha_signal_pipeline")
ml_mod = pytest.importorskip("zephyr.cross_asset.cross_market_data_adapter.ml_experiment_pipeline")

AlphaSignalPipeline = alpha_mod.AlphaSignalPipeline
AlphaPipelineStage = alpha_mod.PipelineStage
AlphaPipelineResult = alpha_mod.PipelineResult
AlphaPipelineError = alpha_mod.PipelineError

MLExperimentPipeline = ml_mod.MLExperimentPipeline
MLPipelineStage = ml_mod.PipelineStage
ExperimentResult = ml_mod.ExperimentResult
MLPipelineError = ml_mod.PipelineError


class TestAlphaSignalPipeline:
    @pytest.fixture(autouse=True)
    def _clear_synth_registry(self):
        try:
            from zephyr.signal_fundamental.synth.signal_synthesizer import SignalSynthesizerBase

            SignalSynthesizerBase.registry.clear()
        except Exception:
            pass
        yield
        try:
            from zephyr.signal_fundamental.synth.signal_synthesizer import SignalSynthesizerBase

            SignalSynthesizerBase.registry.clear()
        except Exception:
            pass

    def test_instantiation(self):
        pipe = AlphaSignalPipeline()
        assert pipe is not None
        assert pipe.factors == []
        assert pipe.synthesizers == []

    def test_register_factor(self):
        pipe = AlphaSignalPipeline()

        class DummyFactor:
            def compute(self):
                return []

        pipe.register_factor(DummyFactor)
        assert len(pipe.factors) == 1

    def test_register_synthesizer(self):
        pipe = AlphaSignalPipeline()

        class DummySynth:
            def synthesize(self, signals):
                return []

        pipe.register_synthesizer(DummySynth)
        assert len(pipe.synthesizers) == 1

    def test_run_no_factors(self):
        pipe = AlphaSignalPipeline()
        result = pipe.run()
        assert isinstance(result, AlphaPipelineResult)
        assert result.status == "no_factors"

    def test_run_with_factor(self):
        pipe = AlphaSignalPipeline()

        class GoodFactor:
            def compute(self):
                return [{"confidence": 0.8, "signal_value": 1.5}]

        pipe.register_factor(GoodFactor)
        result = pipe.run()
        assert isinstance(result, AlphaPipelineResult)
        assert result.factors_computed >= 0

    def test_run_with_idempotency_key(self):
        pipe = AlphaSignalPipeline()
        result = pipe.run(idempotency_key="test-key-001")
        assert result.idempotency_key == "test-key-001"

    def test_pipeline_result_defaults(self):
        result = AlphaPipelineResult(
            pipeline_id="test",
            status="running",
            stage=AlphaPipelineStage.FACTOR_DISCOVERY,
        )
        assert result.factors_computed == 0
        assert result.signal_count == 0
        assert result.confidence == 0.0
        assert result.degraded is False
        assert result.errors == []

    def test_pipeline_error(self):
        err = AlphaPipelineError(
            AlphaPipelineStage.FACTOR_COMPUTE,
            "test error",
            {"detail": "value"},
        )
        assert err.stage == AlphaPipelineStage.FACTOR_COMPUTE
        assert "test error" in str(err)

    def test_pipeline_stages(self):
        assert AlphaPipelineStage.FACTOR_DISCOVERY.value == "factor_discovery"
        assert AlphaPipelineStage.FACTOR_COMPUTE.value == "factor_compute"
        assert AlphaPipelineStage.SIGNAL_SYNTHESIS.value == "signal_synthesis"
        assert AlphaPipelineStage.SIGNAL_VALIDATION.value == "signal_validation"
        assert AlphaPipelineStage.CAPITAL_ALLOCATION.value == "capital_allocation"

    def test_aggregate_confidence_empty(self):
        result = AlphaSignalPipeline._aggregate_confidence([])
        assert result == 0.0

    def test_aggregate_confidence_with_values(self):
        class FakeSignal:
            def __init__(self, c):
                self.confidence = c

        signals = [FakeSignal(0.6), FakeSignal(0.8)]
        result = AlphaSignalPipeline._aggregate_confidence(signals)
        assert abs(result - 0.7) < 1e-9

    def test_aggregate_confidence_dicts(self):
        signals = [{"confidence": 0.5}, {"confidence": 0.9}]
        result = AlphaSignalPipeline._aggregate_confidence(signals)
        assert abs(result - 0.7) < 1e-9


class TestMLExperimentPipeline:
    def test_instantiation(self):
        pipe = MLExperimentPipeline()
        assert pipe is not None
        assert pipe.models == []
        assert pipe.engines == []

    def test_register_model(self):
        pipe = MLExperimentPipeline()
        from zephyr.intelligence.model_evaluation.inference_base import ModelMetadata

        meta = ModelMetadata(
            model_id="test-m",
            model_version="1.0",
            model_type="clf",
            framework="sklearn",
            features=["f1"],
            target="y",
        )
        pipe.register_model(meta)
        assert len(pipe.models) == 1

    def test_register_engine(self):
        pipe = MLExperimentPipeline()

        class DummyEngine:
            __name__ = "DummyEngine"

        pipe.register_engine(DummyEngine)
        assert len(pipe.engines) == 1

    def test_set_experiment_config(self):
        pipe = MLExperimentPipeline()
        from zephyr.simulation.pipeline_base import ExperimentConfig

        cfg = ExperimentConfig(
            experiment_id="exp-1",
            hypothesis="test",
            control_params={},
            treatment_params={},
            metrics=[],
            start_date="2026-01-01",
            end_date="2026-02-01",
        )
        pipe.set_experiment_config(cfg)
        assert pipe.experiment_config is not None
        assert pipe.experiment_config.experiment_id == "exp-1"

    def test_run_no_models(self):
        pipe = MLExperimentPipeline()
        result = pipe.run()
        assert isinstance(result, ExperimentResult)
        assert result.status == "no_models"

    def test_run_with_idempotency_key(self):
        pipe = MLExperimentPipeline()
        result = pipe.run(idempotency_key="ml-key-001")
        assert result.idempotency_key == "ml-key-001"

    def test_experiment_result_defaults(self):
        result = ExperimentResult(
            pipeline_id="test",
            status="running",
            stage=MLPipelineStage.MODEL_DISCOVERY,
        )
        assert result.models_discovered == 0
        assert result.inferences_run == 0
        assert result.significant_results == 0
        assert result.promoted is False

    def test_pipeline_error(self):
        err = MLPipelineError(
            MLPipelineStage.INFERENCE_EXEC,
            "inference failed",
        )
        assert err.stage == MLPipelineStage.INFERENCE_EXEC
        assert "inference failed" in str(err)

    def test_pipeline_stages(self):
        assert MLPipelineStage.MODEL_DISCOVERY.value == "model_discovery"
        assert MLPipelineStage.INFERENCE_EXEC.value == "inference_exec"
        assert MLPipelineStage.METRIC_COLLECTION.value == "metric_collection"
        assert MLPipelineStage.STATISTICS_VALIDATE.value == "statistics_validate"
        assert MLPipelineStage.PRODUCTION_PROMOTE.value == "production_promote"

    def test_snapshot_builtins(self):
        snapshot = MLExperimentPipeline._snapshot_builtins()
        assert isinstance(snapshot, frozenset)
        assert "print" in snapshot

    def test_check_builtins_integrity_clean(self):
        snapshot = MLExperimentPipeline._snapshot_builtins()
        violations = MLExperimentPipeline._check_builtins_integrity(snapshot)
        assert isinstance(violations, list)
        assert len(violations) == 0
