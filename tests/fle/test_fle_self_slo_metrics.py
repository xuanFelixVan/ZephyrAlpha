# [A_test] module_id: SRC-TST-1022 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fle_self_slo_metrics
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.fle_self_slo_metrics
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fle_self_slo_metrics.py
# [TTL] task_bound

import time

from zephyr.feedback_loop.diagnosers.fle_self_slo_metrics import (
    FLESelfSLO,
    FLESLOMetric,
)


class TestFLESLOMetricDataclass:
    def test_creation_with_defaults(self):
        m = FLESLOMetric(dimension="MTTD", current=30.0, target=60.0)
        assert m.dimension == "MTTD"
        assert m.current == 30.0
        assert m.target == 60.0
        assert m.unit == ""

    def test_creation_with_unit(self):
        m = FLESLOMetric(dimension="MTTD", current=30.0, target=60.0, unit="s")
        assert m.unit == "s"

    def test_fields_are_set(self):
        m = FLESLOMetric(dimension="FP_RATE", current=0.05, target=0.1, unit="%")
        assert m.dimension == "FP_RATE"
        assert m.current == 0.05
        assert m.target == 0.1
        assert m.unit == "%"


class TestFLESelfSLOInstantiation:
    def test_default_values(self):
        slo = FLESelfSLO()
        assert slo.mttd_target == 60.0
        assert slo.mttr_target == 300.0
        assert slo.mtti_target == 300.0
        assert slo.fp_rate_target == 0.1
        assert slo.availability_target == 99.9
        assert slo.harmful_rate_target == 0.05
        assert slo.detection_events == []
        assert slo.repair_events == []
        assert slo.total_detections == 0
        assert slo.false_positives == 0
        assert slo.total_repairs == 0
        assert slo.harmful_repairs == 0

    def test_custom_targets(self):
        slo = FLESelfSLO(mttd_target=30.0, mttr_target=120.0, mtti_target=60.0)
        assert slo.mttd_target == 30.0
        assert slo.mttr_target == 120.0
        assert slo.mtti_target == 60.0


class TestCurrentMetrics:
    def test_returns_list_of_slo_metrics(self):
        slo = FLESelfSLO()
        metrics = slo.current_metrics()
        assert isinstance(metrics, list)
        assert all(isinstance(m, FLESLOMetric) for m in metrics)

    def test_seven_dimensions_returned(self):
        slo = FLESelfSLO()
        metrics = slo.current_metrics()
        assert len(metrics) == 7

    def test_dimension_names(self):
        slo = FLESelfSLO()
        metrics = slo.current_metrics()
        names = [m.dimension for m in metrics]
        assert "MTTD" in names
        assert "MTTR" in names
        assert "MTTI" in names
        assert "FP_RATE" in names
        assert "AVAILABILITY" in names
        assert "NET_VALUE" in names
        assert "HARMFUL_RATE" in names

    def test_empty_events_zero_mttd(self):
        slo = FLESelfSLO()
        metrics = slo.current_metrics()
        mttd = next(m for m in metrics if m.dimension == "MTTD")
        assert mttd.current == 0.0

    def test_with_detection_events(self):
        slo = FLESelfSLO()
        now = time.time()
        slo.detection_events = [(now - 100.0, now - 40.0)]
        metrics = slo.current_metrics()
        mttd = next(m for m in metrics if m.dimension == "MTTD")
        assert mttd.current == 60.0

    def test_with_repair_events(self):
        slo = FLESelfSLO()
        now = time.time()
        slo.repair_events = [(now - 200.0, now - 50.0)]
        metrics = slo.current_metrics()
        mttr = next(m for m in metrics if m.dimension == "MTTR")
        assert mttr.current == 150.0

    def test_fp_rate_calculation(self):
        slo = FLESelfSLO(total_detections=10, false_positives=2)
        metrics = slo.current_metrics()
        fp = next(m for m in metrics if m.dimension == "FP_RATE")
        assert abs(fp.current - 0.2) < 0.001

    def test_fp_rate_zero_detections(self):
        slo = FLESelfSLO(total_detections=0, false_positives=0)
        metrics = slo.current_metrics()
        fp = next(m for m in metrics if m.dimension == "FP_RATE")
        assert fp.current == 0.0

    def test_harmful_rate_calculation(self):
        slo = FLESelfSLO(total_repairs=20, harmful_repairs=1)
        metrics = slo.current_metrics()
        hr = next(m for m in metrics if m.dimension == "HARMFUL_RATE")
        assert abs(hr.current - 0.05) < 0.001

    def test_net_value_calculation(self):
        slo = FLESelfSLO(total_benefit=1000.0, total_cost=300.0)
        metrics = slo.current_metrics()
        nv = next(m for m in metrics if m.dimension == "NET_VALUE")
        assert nv.current == 700.0

    def test_net_value_negative(self):
        slo = FLESelfSLO(total_benefit=100.0, total_cost=500.0)
        metrics = slo.current_metrics()
        nv = next(m for m in metrics if m.dimension == "NET_VALUE")
        assert nv.current == -400.0

    def test_each_metric_has_unit(self):
        slo = FLESelfSLO()
        metrics = slo.current_metrics()
        for m in metrics:
            assert isinstance(m.unit, str)
