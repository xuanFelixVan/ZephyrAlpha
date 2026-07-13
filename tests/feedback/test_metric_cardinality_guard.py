# [A_test] module_id: SRC-TST-1268 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_metric_cardinality_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_metric_cardinality_guard.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.reliability.metric_cardinality_guard import (
    CardinalityStatus,
    MetricCardinalityGuard,
)


class TestCardinalityStatus:
    def test_enum_values(self):
        assert CardinalityStatus.SAFE.value == "SAFE"
        assert CardinalityStatus.ELEVATED.value == "ELEVATED"
        assert CardinalityStatus.DANGEROUS.value == "DANGEROUS"
        assert CardinalityStatus.CRITICAL.value == "CRITICAL"


class TestMetricCardinalityGuard:
    def test_default_construction(self):
        guard = MetricCardinalityGuard()
        assert guard.max_cardinality == 10000
        assert guard.warning_cardinality == 5000
        assert guard.max_growth_rate_per_hour == 100.0
        assert guard.window_size == 100
        assert guard.metrics == {}
        assert guard.cardinality_alerts == []

    def test_custom_construction(self):
        guard = MetricCardinalityGuard(max_cardinality=5000, warning_cardinality=2000)
        assert guard.max_cardinality == 5000
        assert guard.warning_cardinality == 2000

    def test_record_labels_new_metric(self):
        guard = MetricCardinalityGuard()
        result = guard.record_labels("http_requests", (("method", "GET"), ("path", "/api")))
        assert result["metric"] == "http_requests"
        assert result["cardinality"] == 1
        assert result["status"] == CardinalityStatus.SAFE.value

    def test_record_labels_increments_cardinality(self):
        guard = MetricCardinalityGuard()
        guard.record_labels("http_requests", (("method", "GET"),))
        result = guard.record_labels("http_requests", (("method", "POST"),))
        assert result["cardinality"] == 2

    def test_record_labels_same_set_no_increment(self):
        guard = MetricCardinalityGuard()
        guard.record_labels("http_requests", (("method", "GET"),))
        result = guard.record_labels("http_requests", (("method", "GET"),))
        assert result["cardinality"] == 1

    def test_record_labels_elevated_status(self):
        guard = MetricCardinalityGuard(warning_cardinality=3, max_cardinality=100)
        for i in range(4):
            guard.record_labels("m", (("k", str(i)),))
        result = guard.record_labels("m", (("k", "extra"),))
        assert result["status"] == CardinalityStatus.ELEVATED.value

    def test_record_labels_dangerous_status(self):
        guard = MetricCardinalityGuard(warning_cardinality=2, max_cardinality=100)
        for i in range(5):
            guard.record_labels("m", (("k", str(i)),))
        result = guard.record_labels("m", (("k", "extra"),))
        assert result["status"] == CardinalityStatus.DANGEROUS.value

    def test_record_labels_critical_status(self):
        guard = MetricCardinalityGuard(max_cardinality=5, warning_cardinality=2)
        for i in range(6):
            guard.record_labels("m", (("k", str(i)),))
        assert guard._classify_cardinality(5) == CardinalityStatus.CRITICAL

    def test_record_labels_generates_alert_for_dangerous(self):
        guard = MetricCardinalityGuard(warning_cardinality=2, max_cardinality=100)
        for i in range(5):
            guard.record_labels("m", (("k", str(i)),))
        guard.record_labels("m", (("k", "extra"),))
        assert len(guard.cardinality_alerts) > 0

    def test_record_labels_generates_alert_for_critical(self):
        guard = MetricCardinalityGuard(max_cardinality=5, warning_cardinality=2)
        for i in range(6):
            guard.record_labels("m", (("k", str(i)),))
        assert len(guard.cardinality_alerts) > 0

    def test_classify_cardinality_safe(self):
        guard = MetricCardinalityGuard(warning_cardinality=5, max_cardinality=100)
        assert guard._classify_cardinality(3) == CardinalityStatus.SAFE

    def test_classify_cardinality_elevated(self):
        guard = MetricCardinalityGuard(warning_cardinality=5, max_cardinality=100)
        assert guard._classify_cardinality(5) == CardinalityStatus.ELEVATED

    def test_classify_cardinality_dangerous(self):
        guard = MetricCardinalityGuard(warning_cardinality=5, max_cardinality=100)
        assert guard._classify_cardinality(10) == CardinalityStatus.DANGEROUS

    def test_classify_cardinality_critical(self):
        guard = MetricCardinalityGuard(warning_cardinality=5, max_cardinality=100)
        assert guard._classify_cardinality(100) == CardinalityStatus.CRITICAL

    def test_compute_growth_rate_insufficient_data(self):
        guard = MetricCardinalityGuard()
        guard.record_labels("m", (("k", "v"),))
        assert guard._compute_growth_rate("m") == 0.0

    def test_compute_growth_rate_unknown_metric(self):
        guard = MetricCardinalityGuard()
        assert guard._compute_growth_rate("nonexistent") == 0.0

    def test_get_top_cardinality_metrics_empty(self):
        guard = MetricCardinalityGuard()
        assert guard.get_top_cardinality_metrics() == []

    def test_get_top_cardinality_metrics_ranked(self):
        guard = MetricCardinalityGuard()
        for i in range(10):
            guard.record_labels("m1", (("k", str(i)),))
        for i in range(3):
            guard.record_labels("m2", (("k", str(i)),))
        top = guard.get_top_cardinality_metrics(top_n=2)
        assert len(top) == 2
        assert top[0]["metric"] == "m1"
        assert top[0]["cardinality"] >= top[1]["cardinality"]

    def test_suggest_label_pruning_unknown_metric(self):
        guard = MetricCardinalityGuard()
        assert guard.suggest_label_pruning("nonexistent") == []

    def test_suggest_label_pruning_below_threshold(self):
        guard = MetricCardinalityGuard(warning_cardinality=100)
        for i in range(5):
            guard.record_labels("m", (("k", str(i)),))
        assert guard.suggest_label_pruning("m") == []

    def test_suggest_label_pruning_above_threshold(self):
        guard = MetricCardinalityGuard(warning_cardinality=3, max_cardinality=1000)
        for i in range(5):
            guard.record_labels("m", (("k", str(i)),))
        suggestions = guard.suggest_label_pruning("m")
        assert len(suggestions) >= 1

    def test_overall_cardinality_health_empty(self):
        guard = MetricCardinalityGuard()
        assert guard.overall_cardinality_health() == 1.0

    def test_overall_cardinality_health_all_safe(self):
        guard = MetricCardinalityGuard(warning_cardinality=100, max_cardinality=1000)
        for i in range(5):
            guard.record_labels("m", (("k", str(i)),))
        assert guard.overall_cardinality_health() == 1.0

    def test_overall_cardinality_health_with_critical(self):
        guard = MetricCardinalityGuard(max_cardinality=3, warning_cardinality=1)
        guard.metrics["m"] = {
            "unique_label_sets": {("k", "v1"), ("k", "v2"), ("k", "v3")},
            "history": [],
            "peak_cardinality": 3,
        }
        health = guard.overall_cardinality_health()
        assert health < 1.0

    def test_peak_cardinality_tracked(self):
        guard = MetricCardinalityGuard()
        for i in range(5):
            guard.record_labels("m", (("k", str(i)),))
        result = guard.record_labels("m", (("k", "extra"),))
        assert result["peak_cardinality"] >= 5
