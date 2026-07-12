# [A_test] module_id: SRC-TST-1041 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §J

# [MODULE] tests.test_gate_health

# [INVARIANTS] no placeholder code; all assertions deterministic

# [MODIFY-GUARD] none

# [CONSUMERS] pytest

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] pytest exit 0 on pass; exit non-zero on fail

# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_health import GateHealth, GateSLI, _percentile


class TestPercentile:
    def test_empty_returns_zero(self):
        assert _percentile([], 50) == 0.0

    def test_single_element(self):
        assert _percentile([42.0], 50) == 42.0

    def test_p50_even_count(self):
        data = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
        result = _percentile(data, 50)
        assert 50.0 <= result <= 60.0

    def test_p99_clamps_to_last(self):
        data = [1.0, 2.0, 3.0]
        assert _percentile(data, 99) == 3.0

    def test_p0_returns_first(self):
        data = [5.0, 10.0, 15.0]
        assert _percentile(data, 0) == 5.0

    def test_p100_clamps_to_last(self):
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        assert _percentile(data, 100) == 5.0

    def test_unsorted_input(self):
        data = [30.0, 10.0, 20.0]
        assert _percentile(data, 50) == 20.0

    def test_negative_values(self):
        data = [-10.0, -5.0, 0.0, 5.0, 10.0]
        assert _percentile(data, 50) == 0.0


class TestGateSLI:
    def test_defaults(self):
        sli = GateSLI(gate_id="G1")
        assert sli.gate_id == "G1"
        assert sli.total_evaluations == 0
        assert sli.pass_count == 0
        assert sli.fail_count == 0
        assert sli.skip_count == 0
        assert sli.false_positive_count == 0
        assert sli.latencies_ms == []

    def test_pass_rate_no_evaluations(self):
        sli = GateSLI(gate_id="G1")
        assert sli.pass_rate == 1.0

    def test_pass_rate_all_pass(self):
        sli = GateSLI(gate_id="G1", total_evaluations=10, pass_count=10)
        assert sli.pass_rate == 1.0

    def test_pass_rate_mixed(self):
        sli = GateSLI(gate_id="G1", total_evaluations=10, pass_count=7, fail_count=3)
        assert sli.pass_rate == pytest.approx(0.7)

    def test_false_positive_rate_no_fails(self):
        sli = GateSLI(gate_id="G1")
        assert sli.false_positive_rate == 0.0

    def test_false_positive_rate_with_fails(self):
        sli = GateSLI(gate_id="G1", fail_count=10, false_positive_count=3)
        assert sli.false_positive_rate == pytest.approx(0.3)

    def test_p50_latency_empty(self):
        sli = GateSLI(gate_id="G1")
        assert sli.p50_latency_ms == 0.0

    def test_p99_latency_empty(self):
        sli = GateSLI(gate_id="G1")
        assert sli.p99_latency_ms == 0.0

    def test_p50_latency_with_data(self):
        sli = GateSLI(gate_id="G1", latencies_ms=[10.0, 20.0, 30.0, 40.0, 50.0])
        assert sli.p50_latency_ms == 30.0

    def test_p99_latency_with_data(self):
        sli = GateSLI(gate_id="G1", latencies_ms=[10.0, 20.0, 30.0, 40.0, 50.0])
        assert sli.p99_latency_ms == 50.0

    def test_pass_rate_zero_total(self):
        sli = GateSLI(gate_id="G1", total_evaluations=0, pass_count=0)
        assert sli.pass_rate == 1.0

    def test_false_positive_rate_zero_fails_nonzero_fp(self):
        sli = GateSLI(gate_id="G1", fail_count=0, false_positive_count=5)
        assert sli.false_positive_rate == 0.0


class TestGateHealth:
    def test_init_empty(self):
        gh = GateHealth()
        assert gh.summary() == []

    def test_get_or_create_new(self):
        gh = GateHealth()
        sli = gh.get_or_create("G1")
        assert isinstance(sli, GateSLI)
        assert sli.gate_id == "G1"
        assert sli.total_evaluations == 0

    def test_get_or_create_returns_same(self):
        gh = GateHealth()
        sli1 = gh.get_or_create("G1")
        sli1.total_evaluations = 5
        sli2 = gh.get_or_create("G1")
        assert sli2.total_evaluations == 5
        assert sli1 is sli2

    def test_record_pass(self):
        gh = GateHealth()
        gh.record("G1", passed=True, latency_ms=50.0)
        sli = gh.get_or_create("G1")
        assert sli.total_evaluations == 1
        assert sli.pass_count == 1
        assert sli.fail_count == 0
        assert sli.false_positive_count == 0
        assert sli.latencies_ms == [50.0]

    def test_record_fail(self):
        gh = GateHealth()
        gh.record("G1", passed=False, latency_ms=200.0)
        sli = gh.get_or_create("G1")
        assert sli.total_evaluations == 1
        assert sli.pass_count == 0
        assert sli.fail_count == 1
        assert sli.false_positive_count == 0
        assert sli.latencies_ms == [200.0]

    def test_record_false_positive(self):
        gh = GateHealth()
        gh.record("G1", passed=False, latency_ms=100.0, is_false_positive=True)
        sli = gh.get_or_create("G1")
        assert sli.fail_count == 1
        assert sli.false_positive_count == 1

    def test_record_false_positive_on_pass_ignored(self):
        gh = GateHealth()
        gh.record("G1", passed=True, latency_ms=10.0, is_false_positive=True)
        sli = gh.get_or_create("G1")
        assert sli.pass_count == 1
        assert sli.false_positive_count == 0

    def test_record_multiple_gates(self):
        gh = GateHealth()
        gh.record("G1", passed=True, latency_ms=10.0)
        gh.record("G2", passed=False, latency_ms=500.0)
        summary = gh.summary()
        assert len(summary) == 2
        ids = {s.gate_id for s in summary}
        assert ids == {"G1", "G2"}

    def test_record_accumulates(self):
        gh = GateHealth()
        gh.record("G1", passed=True, latency_ms=10.0)
        gh.record("G1", passed=True, latency_ms=20.0)
        gh.record("G1", passed=False, latency_ms=300.0, is_false_positive=True)
        sli = gh.get_or_create("G1")
        assert sli.total_evaluations == 3
        assert sli.pass_count == 2
        assert sli.fail_count == 1
        assert sli.false_positive_count == 1
        assert sli.latencies_ms == [10.0, 20.0, 300.0]

    def test_summary_returns_copy(self):
        gh = GateHealth()
        gh.record("G1", passed=True, latency_ms=10.0)
        s1 = gh.summary()
        gh.record("G2", passed=True, latency_ms=20.0)
        s2 = gh.summary()
        assert len(s1) == 1
        assert len(s2) == 2

    def test_health_score_no_evaluations(self):
        gh = GateHealth()
        score = gh.health_score("G1")
        assert score == 1.0

    def test_health_score_all_pass(self):
        gh = GateHealth()
        gh.record("G1", passed=True, latency_ms=50.0)
        gh.record("G1", passed=True, latency_ms=60.0)
        score = gh.health_score("G1")
        assert score == pytest.approx(1.0)

    def test_health_score_with_false_positives(self):
        gh = GateHealth()
        for _ in range(8):
            gh.record("G1", passed=True, latency_ms=10.0)
        gh.record("G1", passed=False, latency_ms=20.0, is_false_positive=True)
        score = gh.health_score("G1")
        assert 0.0 < score < 1.0

    def test_health_score_with_high_latency(self):
        gh = GateHealth()
        gh.record("G1", passed=True, latency_ms=6000.0)
        score = gh.health_score("G1")
        assert score < 1.0

    def test_health_score_clamped_to_zero(self):
        gh = GateHealth()
        for _ in range(10):
            gh.record("G1", passed=False, latency_ms=6000.0, is_false_positive=True)
        score = gh.health_score("G1")
        assert score == 0.0

    def test_health_score_clamped_to_one(self):
        gh = GateHealth()
        gh.record("G1", passed=True, latency_ms=1.0)
        score = gh.health_score("G1")
        assert score <= 1.0

    def test_health_score_unknown_gate(self):
        gh = GateHealth()
        score = gh.health_score("NONEXISTENT")
        assert score == 1.0

    def test_record_zero_latency(self):
        gh = GateHealth()
        gh.record("G1", passed=True, latency_ms=0.0)
        sli = gh.get_or_create("G1")
        assert sli.latencies_ms == [0.0]
        assert sli.p50_latency_ms == 0.0

    def test_record_negative_latency(self):
        gh = GateHealth()
        gh.record("G1", passed=True, latency_ms=-5.0)
        sli = gh.get_or_create("G1")
        assert sli.latencies_ms == [-5.0]

    def test_multiple_records_same_gate_sli_consistency(self):
        gh = GateHealth()
        gh.record("G1", passed=True, latency_ms=10.0)
        gh.record("G1", passed=False, latency_ms=200.0)
        gh.record("G1", passed=True, latency_ms=30.0)
        sli = gh.get_or_create("G1")
        assert sli.pass_rate == pytest.approx(2.0 / 3.0)
        assert sli.false_positive_rate == 0.0
        assert sli.total_evaluations == 3
