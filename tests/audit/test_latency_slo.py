# [A_test] module_id: SRC-TST-1216 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_latency_slo
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.reliability.latency_slo
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_latency_slo.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.reliability.latency_slo import LatencySLO, LatencyWindow


class TestLatencyWindowInstantiation:
    def test_default_instantiation(self):
        w = LatencyWindow()
        assert w.p50_ms == 0.0
        assert w.p95_ms == 0.0
        assert w.p99_ms == 0.0
        assert w.sample_count == 0
        assert w.window_start > 0

    def test_custom_values(self):
        w = LatencyWindow(p50_ms=50.0, p95_ms=200.0, p99_ms=500.0, sample_count=1000)
        assert w.p50_ms == 50.0
        assert w.p95_ms == 200.0
        assert w.p99_ms == 500.0
        assert w.sample_count == 1000


class TestLatencySLOInstantiation:
    def test_default_instantiation(self):
        slo = LatencySLO()
        assert slo.p50_target_ms == 100.0
        assert slo.p95_target_ms == 500.0
        assert slo.p99_target_ms == 1000.0
        assert slo.windows == []

    def test_custom_targets(self):
        slo = LatencySLO(p50_target_ms=50.0, p95_target_ms=200.0, p99_target_ms=500.0)
        assert slo.p50_target_ms == 50.0
        assert slo.p95_target_ms == 200.0
        assert slo.p99_target_ms == 500.0


class TestRecord:
    def test_record_single_window(self):
        slo = LatencySLO()
        slo.record(p50=50.0, p95=200.0, p99=400.0, count=100)
        assert len(slo.windows) == 1
        assert slo.windows[0].p50_ms == 50.0
        assert slo.windows[0].p95_ms == 200.0
        assert slo.windows[0].p99_ms == 400.0
        assert slo.windows[0].sample_count == 100

    def test_record_multiple_windows(self):
        slo = LatencySLO()
        slo.record(p50=50.0, p95=200.0, p99=400.0, count=100)
        slo.record(p50=80.0, p95=450.0, p99=900.0, count=200)
        assert len(slo.windows) == 2

    def test_record_zero_values(self):
        slo = LatencySLO()
        slo.record(p50=0.0, p95=0.0, p99=0.0, count=0)
        assert len(slo.windows) == 1
        assert slo.windows[0].sample_count == 0

    def test_record_negative_latency(self):
        slo = LatencySLO()
        slo.record(p50=-1.0, p95=-1.0, p99=-1.0, count=10)
        assert slo.windows[0].p50_ms == -1.0


class TestCurrentStatus:
    def test_no_windows_returns_all_ok(self):
        slo = LatencySLO()
        status = slo.current_status()
        assert status["p50_ok"] is True
        assert status["p95_ok"] is True
        assert status["p99_ok"] is True

    def test_within_slo(self):
        slo = LatencySLO(p50_target_ms=100.0, p95_target_ms=500.0, p99_target_ms=1000.0)
        slo.record(p50=50.0, p95=200.0, p99=400.0, count=100)
        status = slo.current_status()
        assert status["p50_ok"] is True
        assert status["p95_ok"] is True
        assert status["p99_ok"] is True

    def test_p50_violation(self):
        slo = LatencySLO(p50_target_ms=100.0)
        slo.record(p50=150.0, p95=200.0, p99=400.0, count=100)
        status = slo.current_status()
        assert status["p50_ok"] is False
        assert status["p95_ok"] is True
        assert status["p99_ok"] is True

    def test_p95_violation(self):
        slo = LatencySLO(p95_target_ms=500.0)
        slo.record(p50=50.0, p95=600.0, p99=800.0, count=100)
        status = slo.current_status()
        assert status["p95_ok"] is False

    def test_p99_violation(self):
        slo = LatencySLO(p99_target_ms=1000.0)
        slo.record(p50=50.0, p95=200.0, p99=1200.0, count=100)
        status = slo.current_status()
        assert status["p99_ok"] is False

    def test_all_violated(self):
        slo = LatencySLO(p50_target_ms=50.0, p95_target_ms=100.0, p99_target_ms=200.0)
        slo.record(p50=100.0, p95=300.0, p99=500.0, count=100)
        status = slo.current_status()
        assert status["p50_ok"] is False
        assert status["p95_ok"] is False
        assert status["p99_ok"] is False

    def test_exact_target_is_ok(self):
        slo = LatencySLO(p50_target_ms=100.0, p95_target_ms=500.0, p99_target_ms=1000.0)
        slo.record(p50=100.0, p95=500.0, p99=1000.0, count=100)
        status = slo.current_status()
        assert status["p50_ok"] is True
        assert status["p95_ok"] is True
        assert status["p99_ok"] is True

    def test_uses_last_window(self):
        slo = LatencySLO(p50_target_ms=100.0)
        slo.record(p50=50.0, p95=200.0, p99=400.0, count=100)
        slo.record(p50=150.0, p95=200.0, p99=400.0, count=100)
        status = slo.current_status()
        assert status["p50_ok"] is False
