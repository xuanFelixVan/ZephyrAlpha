# [A_test] module_id: SRC-TST-0973 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_meta_performance_gate
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.meta_performance_gate
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_meta_performance_gate.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.meta_performance_gate import MetaPerformanceGate


class TestMetaPerformanceGateInstantiation:
    def test_default_construction(self):
        mpg = MetaPerformanceGate()
        assert mpg.mttd_seconds == 300.0
        assert mpg.mttr_seconds == 600.0

    def test_custom_construction(self):
        mpg = MetaPerformanceGate(mttd_seconds=120.0, mttr_seconds=300.0)
        assert mpg.mttd_seconds == 120.0
        assert mpg.mttr_seconds == 300.0


class TestMetricsAccess:
    def test_mttd_readable(self):
        mpg = MetaPerformanceGate()
        assert mpg.mttd_seconds > 0

    def test_mttr_readable(self):
        mpg = MetaPerformanceGate()
        assert mpg.mttr_seconds > 0

    def test_metrics_modifiable(self):
        mpg = MetaPerformanceGate()
        mpg.mttd_seconds = 60.0
        assert mpg.mttd_seconds == 60.0


class TestBoundaries:
    def test_zero_mttd(self):
        mpg = MetaPerformanceGate(mttd_seconds=0.0)
        assert mpg.mttd_seconds == 0.0

    def test_negative_mttr(self):
        mpg = MetaPerformanceGate(mttr_seconds=-1.0)
        assert mpg.mttr_seconds == -1.0
