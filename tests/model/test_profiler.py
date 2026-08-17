# [A_test] module_id: MOD-GOV_profiler | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] tests.test_profiler
# [INVARIANTS] CaseResult数据模型;ModelProfile数据模型;MAX_OLLAMA_MODELS;SKIP_MODEL_PATTERNS
# [MODIFY-GUARD] src/zephyr/pipeline/model-profiler/profiler.py
# [CONSUMERS] MOD-INF-034
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.AssertionError
# [TESTS] tests/test_profiler.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.intelligence.model_profiling.benchmark_suite import BenchmarkCase
from zephyr.intelligence.model_profiling.profiler import (
    MAX_OLLAMA_MODELS,
    SKIP_MODEL_PATTERNS,
    CaseResult,
    ModelProfile,
    ModelProfiler,
)


class TestCaseResultConstruction:
    def test_all_fields_populated(self):
        cr = CaseResult(
            case_id="CG-001",
            category="code_generation",
            subcategory="function_impl",
            passed=True,
            score=0.85,
            latency_ms=1200.0,
            tokens_generated=150,
            tokens_per_second=125.0,
            output_text="def is_prime(n):",
            expected_matches=3,
            total_expected=4,
            forbidden_hits=0,
            error="",
        )
        assert cr.case_id == "CG-001"
        assert cr.category == "code_generation"
        assert cr.subcategory == "function_impl"
        assert cr.passed is True
        assert cr.score == 0.85
        assert cr.latency_ms == 1200.0
        assert cr.tokens_generated == 150
        assert cr.tokens_per_second == 125.0
        assert cr.output_text == "def is_prime(n):"
        assert cr.expected_matches == 3
        assert cr.total_expected == 4
        assert cr.forbidden_hits == 0
        assert cr.error == ""

    def test_required_fields_only(self):
        cr = CaseResult(
            case_id="T-001",
            category="test",
            subcategory="sub",
            passed=False,
            score=0.0,
            latency_ms=0.0,
            tokens_generated=0,
            tokens_per_second=0.0,
            output_text="",
            expected_matches=0,
            total_expected=0,
            forbidden_hits=0,
        )
        assert cr.case_id == "T-001"
        assert cr.passed is False

    def test_error_default(self):
        cr = CaseResult(
            case_id="T",
            category="c",
            subcategory="s",
            passed=False,
            score=0.0,
            latency_ms=0.0,
            tokens_generated=0,
            tokens_per_second=0.0,
            output_text="",
            expected_matches=0,
            total_expected=0,
            forbidden_hits=0,
        )
        assert cr.error == ""

    def test_with_error(self):
        cr = CaseResult(
            case_id="T",
            category="c",
            subcategory="s",
            passed=False,
            score=0.0,
            latency_ms=0.0,
            tokens_generated=0,
            tokens_per_second=0.0,
            output_text="",
            expected_matches=0,
            total_expected=0,
            forbidden_hits=0,
            error="timeout",
        )
        assert cr.error == "timeout"


class TestModelProfileConstruction:
    def test_required_fields_only(self):
        mp = ModelProfile(model_name="qwen3:8b", source="ollama")
        assert mp.model_name == "qwen3:8b"
        assert mp.source == "ollama"

    def test_all_defaults(self):
        mp = ModelProfile(model_name="m", source="s")
        assert mp.benchmark_date == ""
        assert mp.total_tests == 0
        assert mp.passed_tests == 0
        assert mp.average_score == 0.0
        assert mp.latency_p50_ms == 0.0
        assert mp.latency_p95_ms == 0.0
        assert mp.latency_p99_ms == 0.0
        assert mp.throughput_tokens_per_sec == 0.0
        assert mp.total_tokens == 0
        assert mp.total_time_ms == 0.0
        assert mp.category_scores == {}
        assert mp.hallucination_rate == 0.0
        assert mp.refusal_rate == 0.0
        assert mp.json_validity_rate == 0.0
        assert mp.code_validity_rate == 0.0
        assert mp.case_results == []
        assert mp.recommendation == ""
        assert mp.rank == 0
        assert mp.available is True
        assert mp.error == ""

    def test_full_construction(self):
        mp = ModelProfile(
            model_name="test-model",
            source="ollama",
            benchmark_date="2026-01-01",
            total_tests=26,
            passed_tests=20,
            average_score=0.78,
            latency_p50_ms=500.0,
            latency_p95_ms=1500.0,
            latency_p99_ms=3000.0,
            throughput_tokens_per_sec=85.0,
            total_tokens=5000,
            total_time_ms=60000.0,
            category_scores={"code_generation": 0.8},
            hallucination_rate=0.05,
            rank=1,
            available=True,
        )
        assert mp.model_name == "test-model"
        assert mp.average_score == 0.78
        assert mp.rank == 1
        assert mp.category_scores["code_generation"] == 0.8

    def test_list_defaults_are_independent(self):
        a = ModelProfile(model_name="a", source="s")
        b = ModelProfile(model_name="b", source="s")
        a.category_scores["x"] = 1.0
        assert "x" not in b.category_scores


class TestMaxOllamaModels:
    def test_value(self):
        assert MAX_OLLAMA_MODELS == 10

    def test_is_positive(self):
        assert MAX_OLLAMA_MODELS > 0


class TestSkipModelPatterns:
    def test_is_list(self):
        assert isinstance(SKIP_MODEL_PATTERNS, list)

    def test_non_empty(self):
        assert len(SKIP_MODEL_PATTERNS) > 0

    def test_contains_embedding_patterns(self):
        assert "embed" in SKIP_MODEL_PATTERNS

    def test_contains_bge_pattern(self):
        assert "bge" in SKIP_MODEL_PATTERNS

    def test_all_strings(self):
        for p in SKIP_MODEL_PATTERNS:
            assert isinstance(p, str)


class TestModelProfilerConstruction:
    def test_default_construction(self):
        profiler = ModelProfiler()
        assert profiler.url == "http://localhost:11434"
        assert profiler.timeout == 60.0
        assert profiler.max_models == MAX_OLLAMA_MODELS

    def test_custom_url(self):
        profiler = ModelProfiler(ollama_url="http://custom:9999")
        assert profiler.url == "http://custom:9999"

    def test_url_trailing_slash_stripped(self):
        profiler = ModelProfiler(ollama_url="http://localhost:11434/")
        assert profiler.url == "http://localhost:11434"

    def test_custom_timeout(self):
        profiler = ModelProfiler(timeout_per_case_s=30.0)
        assert profiler.timeout == 30.0

    def test_custom_max_models(self):
        profiler = ModelProfiler(max_ollama_models=5)
        assert profiler.max_models == 5


class TestModelProfilerShouldSkipModel:
    def test_skip_embedding_model(self):
        profiler = ModelProfiler()
        assert profiler.should_skip_model("bge-large-en") is True

    def test_skip_nomic_model(self):
        profiler = ModelProfiler()
        assert profiler.should_skip_model("nomic-embed-text") is True

    def test_do_not_skip_chat_model(self):
        profiler = ModelProfiler()
        assert profiler.should_skip_model("qwen3:8b") is False

    def test_do_not_skip_code_model(self):
        profiler = ModelProfiler()
        assert profiler.should_skip_model("deepseek-coder:6b") is False

    def test_case_insensitive_skip(self):
        profiler = ModelProfiler()
        assert profiler.should_skip_model("BGE-LARGE") is True


class TestModelProfilerScoreOutput:
    def test_empty_output(self):
        case = BenchmarkCase(
            case_id="T",
            category="c",
            subcategory="s",
            prompt="p",
            expected_patterns=["def"],
        )
        assert ModelProfiler.score_output(case, "") == 0.0

    def test_matching_expected_patterns(self):
        case = BenchmarkCase(
            case_id="T",
            category="c",
            subcategory="s",
            prompt="p",
            expected_patterns=["def", "return"],
        )
        score = ModelProfiler.score_output(case, "def foo():\n    return 42")
        assert score > 0.0

    def test_forbidden_patterns_penalty(self):
        case = BenchmarkCase(
            case_id="T",
            category="c",
            subcategory="s",
            prompt="p",
            expected_patterns=["def"],
            forbidden_patterns=["try:"],
        )
        score_clean = ModelProfiler.score_output(case, "def foo(): return 1")
        score_dirty = ModelProfiler.score_output(case, "def foo(): try: return 1")
        assert score_clean >= score_dirty

    def test_score_bounded(self):
        case = BenchmarkCase(
            case_id="T",
            category="c",
            subcategory="s",
            prompt="p",
            expected_patterns=["def", "return", "class", "if"],
        )
        score = ModelProfiler.score_output(case, "def foo(): return 1")
        assert 0.0 <= score <= 1.0


class TestModelProfilerPercentile:
    def test_empty_data(self):
        assert ModelProfiler.percentile([], 0.5) == 0.0

    def test_single_value(self):
        assert ModelProfiler.percentile([100.0], 0.5) == 100.0

    def test_two_values_p50(self):
        result = ModelProfiler.percentile([10.0, 20.0], 0.5)
        assert 10.0 <= result <= 20.0

    def test_multiple_values(self):
        data = [10.0, 20.0, 30.0, 40.0, 50.0]
        p50 = ModelProfiler.percentile(data, 0.5)
        assert 20.0 <= p50 <= 40.0
