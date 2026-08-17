# [A_test] module_id: MOD-GOV_results_writer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] tests.test_results_writer
# [INVARIANTS] write_benchmark_results;load_benchmark_history;detect_drift;DEFAULT_OUTPUT_DIR
# [MODIFY-GUARD] src/zephyr/pipeline/model-profiler/results_writer.py
# [CONSUMERS] MOD-INF-034
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.AssertionError
# [TESTS] tests/test_results_writer.py
# [TTL] task_bound

from __future__ import annotations

import json

from zephyr.intelligence.model_profiling.profiler import CaseResult, ModelProfile
from zephyr.intelligence.model_profiling.results_writer import (
    DEFAULT_OUTPUT_DIR,
    detect_drift,
    load_benchmark_history,
    to_model_benchmark_result,
    write_benchmark_results,
)


class TestDefaultOutputDir:
    def test_value(self):
        assert DEFAULT_OUTPUT_DIR == "data/model_profiles"

    def test_is_string(self):
        assert isinstance(DEFAULT_OUTPUT_DIR, str)


class TestWriteBenchmarkResults:
    def test_writes_jsonl_file(self, tmp_path):
        profiles = [
            ModelProfile(
                model_name="qwen3:8b",
                source="ollama",
                benchmark_date="2026-01-01T00:00:00",
                average_score=0.75,
            ),
        ]
        output_path = write_benchmark_results(profiles, output_dir=str(tmp_path))
        assert output_path.endswith(".jsonl")

    def test_file_contains_valid_jsonl(self, tmp_path):
        profiles = [
            ModelProfile(model_name="model-a", source="ollama", average_score=0.5),
            ModelProfile(model_name="model-b", source="ollama", average_score=0.6),
        ]
        output_path = write_benchmark_results(profiles, output_dir=str(tmp_path))
        with open(output_path, encoding="utf-8") as f:
            lines = [line for line in f.read().strip().split("\n") if line.strip()]
        assert len(lines) == 2
        for line in lines:
            record = json.loads(line)
            assert "model_name" in record

    def test_creates_output_directory(self, tmp_path):
        nested = tmp_path / "nested" / "dir"
        profiles = [ModelProfile(model_name="m", source="s")]
        output_path = write_benchmark_results(profiles, output_dir=str(nested))
        assert nested.exists()

    def test_empty_profiles(self, tmp_path):
        # ARCH-BENCH-LEAK-001：空 profiles 跳过写入（空文件无消费价值且遮蔽最新有效结果）
        output_path = write_benchmark_results([], output_dir=str(tmp_path))
        assert output_path == ""
        assert list(tmp_path.glob("benchmark_*.jsonl")) == []

    def test_profile_fields_in_output(self, tmp_path):
        profile = ModelProfile(
            model_name="test-model",
            source="ollama",
            benchmark_date="2026-05-22",
            average_score=0.88,
            latency_p50_ms=500.0,
            throughput_tokens_per_sec=80.0,
            hallucination_rate=0.03,
        )
        output_path = write_benchmark_results([profile], output_dir=str(tmp_path))
        with open(output_path, encoding="utf-8") as f:
            record = json.loads(f.readline())
        assert record["model_name"] == "test-model"
        assert record["average_score"] == 0.88
        assert record["latency_p50_ms"] == 500.0


class TestLoadBenchmarkHistory:
    def test_empty_dir_returns_empty_list(self, tmp_path):
        result = load_benchmark_history("any-model", results_dir=str(tmp_path))
        assert result == []

    def test_nonexistent_dir_returns_empty_list(self, tmp_path):
        missing = tmp_path / "no_such_dir"
        result = load_benchmark_history("any-model", results_dir=str(missing))
        assert result == []

    def test_loads_matching_model(self, tmp_path):
        profile = ModelProfile(
            model_name="qwen3:8b",
            source="ollama",
            benchmark_date="2026-01-01",
            average_score=0.7,
        )
        write_benchmark_results([profile], output_dir=str(tmp_path))
        history = load_benchmark_history("qwen3:8b", results_dir=str(tmp_path))
        assert len(history) == 1
        assert history[0]["model_name"] == "qwen3:8b"

    def test_filters_non_matching_model(self, tmp_path):
        profiles = [
            ModelProfile(model_name="model-a", source="ollama", benchmark_date="2026-01-01"),
            ModelProfile(model_name="model-b", source="ollama", benchmark_date="2026-01-01"),
        ]
        write_benchmark_results(profiles, output_dir=str(tmp_path))
        history = load_benchmark_history("model-a", results_dir=str(tmp_path))
        assert len(history) == 1
        assert history[0]["model_name"] == "model-a"

    def test_history_sorted_by_date(self, tmp_path):
        import time

        p1 = ModelProfile(
            model_name="m",
            source="ollama",
            benchmark_date="2026-01-01",
            average_score=0.5,
        )
        p2 = ModelProfile(
            model_name="m",
            source="ollama",
            benchmark_date="2026-02-01",
            average_score=0.6,
        )
        write_benchmark_results([p1], output_dir=str(tmp_path))
        time.sleep(1.1)
        write_benchmark_results([p2], output_dir=str(tmp_path))
        history = load_benchmark_history("m", results_dir=str(tmp_path))
        assert len(history) == 2
        assert history[0]["benchmark_date"] <= history[1]["benchmark_date"]


class TestDetectDrift:
    def test_empty_list_no_drift(self):
        result = detect_drift([])
        assert result["drift_detected"] is False
        assert result["reason"] == "insufficient_history"

    def test_single_entry_no_drift(self):
        result = detect_drift([{"model_name": "m", "average_score": 0.8}])
        assert result["drift_detected"] is False
        assert result["reason"] == "insufficient_history"

    def test_no_drift_when_stable(self):
        history = [
            {
                "model_name": "m",
                "average_score": 0.8,
                "latency_p50_ms": 500.0,
                "category_scores": {},
                "hallucination_rate": 0.05,
                "throughput_tokens_per_sec": 80.0,
            },
            {
                "model_name": "m",
                "average_score": 0.79,
                "latency_p50_ms": 510.0,
                "category_scores": {},
                "hallucination_rate": 0.05,
                "throughput_tokens_per_sec": 79.0,
            },
        ]
        result = detect_drift(history)
        assert result["drift_detected"] is False

    def test_drift_detected_on_score_decline(self):
        history = [
            {
                "model_name": "m",
                "average_score": 0.8,
                "latency_p50_ms": 500.0,
                "category_scores": {},
                "hallucination_rate": 0.05,
                "throughput_tokens_per_sec": 80.0,
            },
            {
                "model_name": "m",
                "average_score": 0.5,
                "latency_p50_ms": 500.0,
                "category_scores": {},
                "hallucination_rate": 0.05,
                "throughput_tokens_per_sec": 80.0,
            },
        ]
        result = detect_drift(history)
        assert result["drift_detected"] is True
        assert result["details"]["score_delta"] < 0

    def test_drift_detected_on_latency_increase(self):
        history = [
            {
                "model_name": "m",
                "average_score": 0.8,
                "latency_p50_ms": 500.0,
                "category_scores": {},
                "hallucination_rate": 0.05,
                "throughput_tokens_per_sec": 80.0,
            },
            {
                "model_name": "m",
                "average_score": 0.8,
                "latency_p50_ms": 1000.0,
                "category_scores": {},
                "hallucination_rate": 0.05,
                "throughput_tokens_per_sec": 80.0,
            },
        ]
        result = detect_drift(history)
        assert result["drift_detected"] is True
        assert result["details"]["latency_increase_pct"] > 0

    def test_result_contains_model_name(self):
        history = [
            {
                "model_name": "test-model",
                "average_score": 0.8,
                "latency_p50_ms": 500.0,
                "category_scores": {},
                "hallucination_rate": 0.05,
                "throughput_tokens_per_sec": 80.0,
            },
            {
                "model_name": "test-model",
                "average_score": 0.5,
                "latency_p50_ms": 500.0,
                "category_scores": {},
                "hallucination_rate": 0.05,
                "throughput_tokens_per_sec": 80.0,
            },
        ]
        result = detect_drift(history)
        assert result["model_name"] == "test-model"

    def test_category_drift_computed(self):
        history = [
            {
                "model_name": "m",
                "average_score": 0.8,
                "latency_p50_ms": 500.0,
                "category_scores": {"code_generation": 0.9},
                "hallucination_rate": 0.05,
                "throughput_tokens_per_sec": 80.0,
            },
            {
                "model_name": "m",
                "average_score": 0.8,
                "latency_p50_ms": 500.0,
                "category_scores": {"code_generation": 0.7},
                "hallucination_rate": 0.05,
                "throughput_tokens_per_sec": 80.0,
            },
        ]
        result = detect_drift(history)
        assert "code_generation" in result["details"]["category_drift"]
        assert result["details"]["category_drift"]["code_generation"] < 0

    def test_custom_thresholds(self):
        history = [
            {
                "model_name": "m",
                "average_score": 0.8,
                "latency_p50_ms": 500.0,
                "category_scores": {},
                "hallucination_rate": 0.05,
                "throughput_tokens_per_sec": 80.0,
            },
            {
                "model_name": "m",
                "average_score": 0.76,
                "latency_p50_ms": 500.0,
                "category_scores": {},
                "hallucination_rate": 0.05,
                "throughput_tokens_per_sec": 80.0,
            },
        ]
        result_strict = detect_drift(history, threshold_score_decline=0.01)
        result_relaxed = detect_drift(history, threshold_score_decline=0.10)
        assert result_strict["drift_detected"] is True
        assert result_relaxed["drift_detected"] is False


class TestToModelBenchmarkResult:
    def test_converts_profile(self):
        profile = ModelProfile(
            model_name="qwen3:8b",
            source="ollama",
            benchmark_date="2026-05-22",
            average_score=0.75,
            latency_p50_ms=500.0,
            throughput_tokens_per_sec=80.0,
            hallucination_rate=0.05,
            code_validity_rate=0.8,
            json_validity_rate=0.9,
            category_scores={"code_generation": 0.8},
            case_results=[
                CaseResult(
                    case_id="CG-001",
                    category="code_generation",
                    subcategory="function_impl",
                    passed=False,
                    score=0.3,
                    latency_ms=1000.0,
                    tokens_generated=50,
                    tokens_per_second=50.0,
                    output_text="bad",
                    expected_matches=1,
                    total_expected=4,
                    forbidden_hits=0,
                    error="",
                ),
            ],
        )
        result = to_model_benchmark_result(profile)
        assert result["model_name"] == "qwen3:8b"
        assert result["task_scores"]["composite_score"] == 0.75
        assert result["task_scores"]["latency_p50_ms"] == 500.0
        assert "code_generation" in result["task_scores"]
        assert result["regression_detected"] is False
        assert "CG-001" in result["regression_tasks"]

    def test_model_version_extracted(self):
        profile = ModelProfile(model_name="qwen3:8b", source="ollama")
        result = to_model_benchmark_result(profile)
        assert result["model_version"] == "8b"

    def test_model_version_empty_for_no_colon(self):
        profile = ModelProfile(model_name="local-model", source="ollama")
        result = to_model_benchmark_result(profile)
        assert result["model_version"] == ""

    def test_regression_detected_for_low_score(self):
        profile = ModelProfile(
            model_name="m",
            source="s",
            average_score=0.2,
        )
        result = to_model_benchmark_result(profile)
        assert result["regression_detected"] is True
