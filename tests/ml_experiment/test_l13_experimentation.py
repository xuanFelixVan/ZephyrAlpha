# [A_test] module_id: MOD-GOV_l13_experimentation | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L13-001 | docs/03_modules/_domain_simulation/blueprint.md | §test
# [MODULE] zephyr.ex_core.src.zephyr
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_l13_experimentation.py
# [TTL] task_bound

from __future__ import annotations

from datetime import datetime

import pytest

mod = pytest.importorskip("zephyr.simulation.pipeline_base")

ExperimentConfig = mod.ExperimentConfig
ExperimentMetric = mod.ExperimentMetric
ExperimentPipelineBase = mod.ExperimentPipelineBase
ScoutAgentBase = mod.ScoutAgentBase


class TestExperimentConfig:
    def test_creation(self):
        cfg = ExperimentConfig(
            experiment_id="exp-001",
            hypothesis="Treatment improves accuracy",
            control_params={"lr": 0.01},
            treatment_params={"lr": 0.1},
            metrics=["accuracy"],
            start_date="2026-01-01",
            end_date="2026-02-01",
        )
        assert cfg.experiment_id == "exp-001"
        assert cfg.hypothesis == "Treatment improves accuracy"
        assert cfg.control_params == {"lr": 0.01}
        assert cfg.treatment_params == {"lr": 0.1}
        assert cfg.metrics == ["accuracy"]
        assert cfg.status == "registered"

    def test_frozen(self):
        cfg = ExperimentConfig(
            experiment_id="exp-002",
            hypothesis="test",
            control_params={},
            treatment_params={},
            metrics=[],
            start_date="2026-01-01",
            end_date="2026-02-01",
        )
        with pytest.raises(Exception):
            cfg.experiment_id = "changed"

    def test_default_status(self):
        cfg = ExperimentConfig(
            experiment_id="exp-003",
            hypothesis="h",
            control_params={},
            treatment_params={},
            metrics=[],
            start_date="2026-01-01",
            end_date="2026-02-01",
        )
        assert cfg.status == "registered"


class TestExperimentMetric:
    def test_creation(self):
        metric = ExperimentMetric(
            experiment_id="exp-001",
            metric_name="accuracy",
            control_value=0.80,
            treatment_value=0.90,
            effect_size=0.5,
            p_value=0.03,
            is_significant=True,
        )
        assert metric.experiment_id == "exp-001"
        assert metric.metric_name == "accuracy"
        assert metric.effect_size == 0.5
        assert metric.is_significant is True

    def test_frozen(self):
        metric = ExperimentMetric(
            experiment_id="exp-002",
            metric_name="f1",
            control_value=0.5,
            treatment_value=0.6,
            effect_size=0.3,
            p_value=0.1,
            is_significant=False,
        )
        with pytest.raises(Exception):
            metric.experiment_id = "changed"

    def test_default_timestamp(self):
        metric = ExperimentMetric(
            experiment_id="exp-003",
            metric_name="loss",
            control_value=1.0,
            treatment_value=0.5,
            effect_size=0.8,
            p_value=0.01,
            is_significant=True,
        )
        assert isinstance(metric.timestamp, datetime)


class TestExperimentPipelineBase:
    def test_is_abstract(self):
        with pytest.raises(TypeError):
            ExperimentPipelineBase()

    def test_subclass_must_implement_run(self):
        class IncompletePipeline(ExperimentPipelineBase):
            def compute_effect_size_only(self):
                return 0.0

        with pytest.raises(TypeError):
            IncompletePipeline()

    def test_concrete_subclass(self):
        class DummyPipeline(ExperimentPipelineBase):
            def run(self, config, idempotency_key):
                return []

        pipe = DummyPipeline()
        cfg = ExperimentConfig(
            experiment_id="exp-004",
            hypothesis="h",
            control_params={},
            treatment_params={},
            metrics=[],
            start_date="2026-01-01",
            end_date="2026-02-01",
        )
        result = pipe.run(cfg, "key-001")
        assert result == []

    def test_compute_effect_size(self):
        result = ExperimentPipelineBase.compute_effect_size(0.5, 0.8, 0.3)
        assert abs(result - 1.0) < 1e-9

    def test_compute_effect_size_zero_std(self):
        result = ExperimentPipelineBase.compute_effect_size(0.5, 0.8, 0.0)
        assert result == 0.0

    def test_compute_effect_size_negative(self):
        result = ExperimentPipelineBase.compute_effect_size(0.8, 0.5, 0.3)
        assert result < 0


class TestScoutAgentBase:
    def test_is_abstract(self):
        with pytest.raises(TypeError):
            ScoutAgentBase()

    def test_subclass_must_implement_scout_and_archive(self):
        class IncompleteScout(ScoutAgentBase):
            def scout(self, context, idempotency_key):
                return None

        with pytest.raises(TypeError):
            IncompleteScout()

    def test_concrete_subclass(self):
        class DummyScout(ScoutAgentBase):
            def scout(self, context, idempotency_key):
                return None

            def archive_to_kms(self, result):
                return True

        scout = DummyScout()
        assert scout.archive_to_kms(None) is True
