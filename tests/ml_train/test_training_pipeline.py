# [BLUEPRINT] MOD-ML-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-ML_test_training_pipeline | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ml_train.test_training_pipeline
# [TESTS] src/zephyr/ml_train/training_pipeline/pipeline_orchestrator.py
# [TTL] task_bound
"""MOD-ML-001 训练管线编排 toy 断言（数据→训练→评估→登记四段全链）。

登记段只产 model_registry 晋升片段草稿（恒 candidate），禁直改注册表。
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pytest

from zephyr.ml_train.implementations.density_quantile_trainer import DensityQuantileTrainer
from zephyr.ml_train.training_pipeline import (
    PipelineStageError,
    TrainingPipelineOrchestrator,
    TrainingPipelineRequest,
)


def _toy_xy(n: int = 200, seed: int = 3):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(n, 2))
    y = x[:, 0] - 0.5 * x[:, 1] + rng.normal(scale=0.2, size=n)
    return x, y


def _request() -> TrainingPipelineRequest:
    x, y = _toy_xy()
    return TrainingPipelineRequest(
        pipeline_id="pipe-toy-1",
        trainer=DensityQuantileTrainer(),
        train_features={"X": x[:150]},
        train_target=y[:150],
        eval_features={"X": x[150:]},
        eval_target=y[150:],
        idempotency_key="pipe-toy-1",
    )


class TestPipelineHappyPath:
    def test_full_run_four_stages(self):
        result = TrainingPipelineOrchestrator().run(_request())
        assert result.status == "completed"
        assert result.stages == ("load", "train", "evaluate", "register")
        assert result.train_metrics["n_train"] == 150.0
        assert result.eval_metrics["n"] == 50.0

    def test_register_stage_emits_candidate_draft_only(self):
        result = TrainingPipelineOrchestrator().run(_request())
        draft = result.registry_draft
        assert draft["model_id"] == "ML-DENSITY-001"
        assert draft["promotion_stage"] == "candidate"  # 晋升桩：永不直改注册表

    def test_run_is_deterministic_on_same_key(self):
        r1 = TrainingPipelineOrchestrator().run(_request())
        r2 = TrainingPipelineOrchestrator().run(_request())
        assert r1.train_metrics == r2.train_metrics


class TestPipelineFailures:
    def test_train_failure_marks_failed_and_stops(self):
        # features 非空但缺 "X" → 过 load 段、炸 train 段（DensityTrainError 被吸收）
        req = dataclasses.replace(_request(), train_features={"wrong_key": np.zeros((40, 2))})
        result = TrainingPipelineOrchestrator().run(req)
        assert result.status == "failed"
        assert result.failed_stage == "train"
        assert "register" not in result.stages

    def test_load_failure_on_empty_features(self):
        req = dataclasses.replace(_request(), train_features={})
        result = TrainingPipelineOrchestrator().run(req)
        assert result.status == "failed"
        assert result.failed_stage == "load"

    def test_empty_eval_falls_back_to_train_metrics(self):
        req = dataclasses.replace(_request(), eval_features=None, eval_target=None)
        result = TrainingPipelineOrchestrator().run(req)
        assert result.status == "completed"
        assert result.eval_metrics == result.train_metrics

    def test_bad_request_raises(self):
        with pytest.raises(PipelineStageError, match="trainer"):
            TrainingPipelineOrchestrator().run(
                TrainingPipelineRequest(
                    pipeline_id="bad",
                    trainer=None,  # type: ignore[arg-type]
                    train_features={"X": np.zeros((40, 2))},
                    train_target=np.zeros(40),
                    eval_features=None,
                    eval_target=None,
                    idempotency_key="bad",
                )
            )
