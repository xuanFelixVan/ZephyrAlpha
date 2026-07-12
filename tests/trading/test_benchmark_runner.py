# [A_test] module_id: SRC-TST-0425 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_benchmark_runner
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_benchmark_runner.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.orchestrator.quality.benchmark_runner import BASELINES, BenchmarkRunner


class TestBenchmarkRunnerInstantiation:
    def test_default_construction(self):
        runner = BenchmarkRunner()
        assert runner is not None


class TestBenchmarkRunnerGetBaseline:
    def test_known_contract(self):
        runner = BenchmarkRunner()
        baseline = runner.get_baseline("CT-ORC-SCRIPT-001")
        assert baseline["p50_ms"] == 500
        assert baseline["p95_ms"] == 3000
        assert baseline["p99_ms"] == 5000

    def test_another_known_contract(self):
        runner = BenchmarkRunner()
        baseline = runner.get_baseline("CT-ORC-CE-001")
        assert baseline["p50_ms"] == 100
        assert baseline["p95_ms"] == 500

    def test_pipe_orc_contract(self):
        runner = BenchmarkRunner()
        baseline = runner.get_baseline("CT-PIPE-ORC-001")
        assert baseline["p50_ms"] == 10
        assert baseline["p95_ms"] == 50

    def test_unknown_contract_returns_default(self):
        runner = BenchmarkRunner()
        baseline = runner.get_baseline("UNKNOWN-001")
        assert baseline["p50_ms"] == 100
        assert baseline["p95_ms"] == 500
        assert baseline["p99_ms"] == 1000

    def test_empty_contract_id_returns_default(self):
        runner = BenchmarkRunner()
        baseline = runner.get_baseline("")
        assert baseline["p50_ms"] == 100


class TestBenchmarkRunnerDetectRegression:
    def test_no_regression_within_threshold(self):
        runner = BenchmarkRunner()
        assert runner.detect_regression("CT-ORC-SCRIPT-001", 3000.0) is False

    def test_regression_above_threshold(self):
        runner = BenchmarkRunner()
        assert runner.detect_regression("CT-ORC-SCRIPT-001", 5000.0) is True

    def test_regression_at_exact_1_5x(self):
        runner = BenchmarkRunner()
        baseline = runner.get_baseline("CT-ORC-SCRIPT-001")
        threshold = baseline["p95_ms"] * 1.5
        assert runner.detect_regression("CT-ORC-SCRIPT-001", threshold + 1) is True

    def test_no_regression_just_below_1_5x(self):
        runner = BenchmarkRunner()
        baseline = runner.get_baseline("CT-ORC-SCRIPT-001")
        threshold = baseline["p95_ms"] * 1.5
        assert runner.detect_regression("CT-ORC-SCRIPT-001", threshold - 1) is False

    def test_regression_with_unknown_contract(self):
        runner = BenchmarkRunner()
        assert runner.detect_regression("UNKNOWN", 1000.0) is True

    def test_no_regression_with_unknown_contract_low_p95(self):
        runner = BenchmarkRunner()
        assert runner.detect_regression("UNKNOWN", 100.0) is False

    def test_zero_p95_no_regression(self):
        runner = BenchmarkRunner()
        assert runner.detect_regression("CT-ORC-SCRIPT-001", 0.0) is False


class TestBaselinesConstant:
    def test_baselines_has_three_entries(self):
        assert len(BASELINES) == 3

    def test_baselines_keys(self):
        assert "CT-ORC-SCRIPT-001" in BASELINES
        assert "CT-ORC-CE-001" in BASELINES
        assert "CT-PIPE-ORC-001" in BASELINES

    def test_baselines_have_required_keys(self):
        for key, baseline in BASELINES.items():
            assert "p50_ms" in baseline
            assert "p95_ms" in baseline
            assert "p99_ms" in baseline
