# [A_test] module_id: SRC-TST-1550 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_self_benchmark
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.health.self_benchmark
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_self_benchmark.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.diagnosers.health.self_benchmark import SelfBenchmark


class TestSelfBenchmarkInstantiation:
    def test_default_instantiation(self):
        sb = SelfBenchmark()
        assert sb.baselines == {}

    def test_instantiation_with_baselines(self):
        sb = SelfBenchmark(baselines={"latency_ms": 100.0})
        assert sb.baselines["latency_ms"] == 100.0


class TestCompare:
    def test_compare_with_existing_baseline(self):
        sb = SelfBenchmark(baselines={"latency_ms": 100.0})
        delta = sb.compare("latency_ms", 150.0)
        assert delta == pytest.approx(50.0)

    def test_compare_below_baseline(self):
        sb = SelfBenchmark(baselines={"latency_ms": 100.0})
        delta = sb.compare("latency_ms", 80.0)
        assert delta == pytest.approx(-20.0)

    def test_compare_equal_to_baseline(self):
        sb = SelfBenchmark(baselines={"latency_ms": 100.0})
        delta = sb.compare("latency_ms", 100.0)
        assert delta == pytest.approx(0.0)

    def test_compare_unknown_metric_uses_current_as_baseline(self):
        sb = SelfBenchmark()
        delta = sb.compare("new_metric", 42.0)
        assert delta == pytest.approx(0.0)

    def test_compare_zero_baseline(self):
        sb = SelfBenchmark(baselines={"zero_metric": 0.0})
        delta = sb.compare("zero_metric", 10.0)
        assert delta == pytest.approx(10.0)


class TestSelfBenchmarkBoundaries:
    def test_compare_none_metric_uses_current_as_baseline(self):
        sb = SelfBenchmark()
        delta = sb.compare(None, 42.0)
        assert delta == pytest.approx(0.0)

    def test_compare_none_value_raises(self):
        sb = SelfBenchmark(baselines={"x": 1.0})
        with pytest.raises(TypeError):
            sb.compare("x", None)

    def test_compare_negative_values(self):
        sb = SelfBenchmark(baselines={"x": -10.0})
        delta = sb.compare("x", -5.0)
        assert delta == pytest.approx(5.0)

    def test_compare_very_large_values(self):
        sb = SelfBenchmark(baselines={"x": 1e15})
        delta = sb.compare("x", 1e15 + 1.0)
        assert delta == pytest.approx(1.0)
