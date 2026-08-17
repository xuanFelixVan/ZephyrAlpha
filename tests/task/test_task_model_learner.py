# [A_test] module_id: MOD-GOV_task_model_learner | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] tests.test_task_model_learner
# [INVARIANTS] ModelTaskEntry数据模型;ModelTaskMatrix推荐算法;THROUGHPUT_MAX;MIN_SAMPLES_FOR_LEARNED
# [MODIFY-GUARD] src/zephyr/pipeline/model-profiler/task_model_learner.py
# [CONSUMERS] MOD-INF-034
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.AssertionError
# [TESTS] tests/test_task_model_learner.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.intelligence.model_profiling.task_model_learner import (
    MIN_SAMPLES_FOR_LEARNED,
    THROUGHPUT_MAX,
    ModelTaskEntry,
    ModelTaskMatrix,
    TaskRecommendation,
)


class TestModelTaskEntryConstruction:
    def test_required_fields_only(self):
        entry = ModelTaskEntry(model_name="qwen3:8b")
        assert entry.model_name == "qwen3:8b"

    def test_all_defaults(self):
        entry = ModelTaskEntry(model_name="m")
        assert entry.sample_count == 0
        assert entry.total_duration_ms == 0.0
        assert entry.total_tokens == 0
        assert entry.total_confidence == 0.0
        assert entry.duration_samples == []
        assert entry.confidence_samples == []
        assert entry.last_updated == ""
        assert entry.avg_duration_ms == 0.0
        assert entry.avg_tokens_per_sec == 0.0
        assert entry.avg_confidence == 0.0
        assert entry.composite_score == 0.0

    def test_list_defaults_are_independent(self):
        a = ModelTaskEntry(model_name="a")
        b = ModelTaskEntry(model_name="b")
        a.duration_samples.append(1.0)
        assert b.duration_samples == []


class TestModelTaskEntryUpdate:
    def test_single_update(self):
        entry = ModelTaskEntry(model_name="m")
        entry.update(duration_ms=1000.0, tokens=100, confidence=0.8)
        assert entry.sample_count == 1
        assert entry.total_duration_ms == 1000.0
        assert entry.total_tokens == 100
        assert entry.total_confidence == 0.8
        assert entry.avg_duration_ms == 1000.0
        assert entry.avg_confidence == 0.8
        assert entry.last_updated != ""

    def test_multiple_updates(self):
        entry = ModelTaskEntry(model_name="m")
        entry.update(duration_ms=1000.0, tokens=100, confidence=0.8)
        entry.update(duration_ms=2000.0, tokens=200, confidence=0.9)
        assert entry.sample_count == 2
        assert entry.total_duration_ms == 3000.0
        assert entry.total_tokens == 300
        assert entry.avg_duration_ms == 1500.0
        assert entry.avg_confidence == pytest.approx(0.85, abs=0.001)

    def test_composite_score_after_update(self):
        entry = ModelTaskEntry(model_name="m")
        entry.update(duration_ms=1000.0, tokens=100, confidence=0.9)
        assert entry.composite_score > 0.0
        assert entry.composite_score <= 1.0

    def test_avg_tokens_per_sec(self):
        entry = ModelTaskEntry(model_name="m")
        entry.update(duration_ms=1000.0, tokens=100, confidence=0.5)
        assert entry.avg_tokens_per_sec == pytest.approx(100.0, abs=0.1)

    def test_duration_samples_capped_at_200(self):
        entry = ModelTaskEntry(model_name="m")
        for i in range(250):
            entry.update(duration_ms=float(i), tokens=1, confidence=0.5)
        assert len(entry.duration_samples) <= 200

    def test_confidence_samples_capped_at_200(self):
        entry = ModelTaskEntry(model_name="m")
        for i in range(250):
            entry.update(duration_ms=1.0, tokens=1, confidence=float(i) / 500.0)
        assert len(entry.confidence_samples) <= 200

    def test_update_with_zero_duration(self):
        entry = ModelTaskEntry(model_name="m")
        entry.update(duration_ms=0.0, tokens=100, confidence=0.5)
        assert entry.avg_tokens_per_sec == 0.0


class TestModelTaskMatrixConstruction:
    def test_default_storage_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        matrix = ModelTaskMatrix(storage_dir=str(tmp_path / "test_learning"))
        assert matrix.dir.exists()

    def test_custom_storage_dir(self, tmp_path):
        storage = tmp_path / "custom_matrix"
        matrix = ModelTaskMatrix(storage_dir=str(storage))
        assert storage.exists()


class TestModelTaskMatrixRecord:
    def test_record_creates_entry(self, tmp_path):
        matrix = ModelTaskMatrix(storage_dir=str(tmp_path / "learn"))
        matrix.record("M3", "qwen3:8b", duration_ms=1000.0, tokens=100, confidence=0.8)
        snapshot = matrix.snapshot()
        assert "M3" in snapshot
        assert "qwen3:8b" in snapshot["M3"]
        assert snapshot["M3"]["qwen3:8b"]["sample_count"] == 1

    def test_record_accumulates(self, tmp_path):
        matrix = ModelTaskMatrix(storage_dir=str(tmp_path / "learn"))
        matrix.record("M3", "qwen3:8b", duration_ms=1000.0, tokens=100, confidence=0.8)
        matrix.record("M3", "qwen3:8b", duration_ms=2000.0, tokens=200, confidence=0.9)
        snapshot = matrix.snapshot()
        assert snapshot["M3"]["qwen3:8b"]["sample_count"] == 2

    def test_record_multiple_models(self, tmp_path):
        matrix = ModelTaskMatrix(storage_dir=str(tmp_path / "learn"))
        matrix.record("M3", "model-a", duration_ms=1000.0, tokens=100, confidence=0.8)
        matrix.record("M3", "model-b", duration_ms=500.0, tokens=200, confidence=0.9)
        snapshot = matrix.snapshot()
        assert "model-a" in snapshot["M3"]
        assert "model-b" in snapshot["M3"]


class TestModelTaskMatrixRecommend:
    def test_recommend_with_no_data_returns_static(self, tmp_path):
        matrix = ModelTaskMatrix(storage_dir=str(tmp_path / "learn"))
        rec = matrix.recommend("M3")
        assert isinstance(rec, TaskRecommendation)
        assert rec.task_type == "M3"
        assert rec.source in ("static_spec", "benchmark_baseline")

    def test_recommend_with_learned_data(self, tmp_path):
        matrix = ModelTaskMatrix(storage_dir=str(tmp_path / "learn"))
        for _ in range(MIN_SAMPLES_FOR_LEARNED):
            matrix.record("M3", "best-model", duration_ms=500.0, tokens=200, confidence=0.95)
        rec = matrix.recommend("M3")
        assert rec.source == "learned"
        assert rec.best_model == "best-model"
        assert rec.sample_count >= MIN_SAMPLES_FOR_LEARNED

    def test_recommend_with_insufficient_samples(self, tmp_path):
        matrix = ModelTaskMatrix(storage_dir=str(tmp_path / "learn"))
        matrix.record("M3", "weak-model", duration_ms=500.0, tokens=100, confidence=0.5)
        rec = matrix.recommend("M3")
        assert rec.source != "learned"

    def test_recommend_picks_best_model(self, tmp_path):
        matrix = ModelTaskMatrix(storage_dir=str(tmp_path / "learn"))
        for _ in range(MIN_SAMPLES_FOR_LEARNED):
            matrix.record("M3", "slow-model", duration_ms=5000.0, tokens=50, confidence=0.3)
        for _ in range(MIN_SAMPLES_FOR_LEARNED):
            matrix.record("M3", "fast-model", duration_ms=500.0, tokens=200, confidence=0.95)
        rec = matrix.recommend("M3")
        assert rec.best_model == "fast-model"

    def test_recommend_includes_alternatives(self, tmp_path):
        matrix = ModelTaskMatrix(storage_dir=str(tmp_path / "learn"))
        for model in ["model-a", "model-b", "model-c"]:
            for _ in range(MIN_SAMPLES_FOR_LEARNED):
                matrix.record("M3", model, duration_ms=1000.0, tokens=100, confidence=0.7)
        rec = matrix.recommend("M3")
        assert len(rec.alternatives) >= 1


class TestModelTaskMatrixSnapshot:
    def test_snapshot_empty(self, tmp_path):
        matrix = ModelTaskMatrix(storage_dir=str(tmp_path / "learn"))
        assert matrix.snapshot() == {}

    def test_snapshot_with_data(self, tmp_path):
        matrix = ModelTaskMatrix(storage_dir=str(tmp_path / "learn"))
        matrix.record("M3", "model-x", duration_ms=1000.0, tokens=100, confidence=0.8)
        snap = matrix.snapshot()
        assert "M3" in snap
        assert "model-x" in snap["M3"]
        assert snap["M3"]["model-x"]["sample_count"] == 1


class TestConstants:
    def test_throughput_max(self):
        assert THROUGHPUT_MAX == 200.0

    def test_min_samples_for_learned(self):
        assert MIN_SAMPLES_FOR_LEARNED == 3

    def test_throughput_max_is_positive(self):
        assert THROUGHPUT_MAX > 0

    def test_min_samples_is_positive(self):
        assert MIN_SAMPLES_FOR_LEARNED > 0


class TestModelTaskMatrixPersistence:
    def test_save_and_reload(self, tmp_path):
        storage = tmp_path / "persist_learn"
        matrix = ModelTaskMatrix(storage_dir=str(storage))
        matrix.record("M3", "qwen3:8b", duration_ms=1000.0, tokens=100, confidence=0.8)
        matrix.save()

        matrix2 = ModelTaskMatrix(storage_dir=str(storage))
        snap = matrix2.snapshot()
        assert "M3" in snap
        assert "qwen3:8b" in snap["M3"]
        assert snap["M3"]["qwen3:8b"]["sample_count"] == 1

    def test_persistence_path(self, tmp_path):
        storage = tmp_path / "path_test"
        matrix = ModelTaskMatrix(storage_dir=str(storage))
        assert matrix.persistence_path().endswith("task-model-matrix.json")
