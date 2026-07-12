# [A_test] module_id: SRC-TST-1291 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_model_version_semantic_drift
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.model_version_semantic_drift
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_model_version_semantic_drift.py
# [TTL] task_bound

import time

from zephyr.feedback_loop.diagnosers.model_version_semantic_drift import (
    DriftSeverity,
    ModelVersionSemanticDrift,
)


class TestDriftSeverity:
    def test_none_value(self):
        assert DriftSeverity.NONE.value == "NONE"

    def test_minor_value(self):
        assert DriftSeverity.MINOR.value == "MINOR"

    def test_significant_value(self):
        assert DriftSeverity.SIGNIFICANT.value == "SIGNIFICANT"

    def test_breaking_value(self):
        assert DriftSeverity.BREAKING.value == "BREAKING"

    def test_all_severities_count(self):
        assert len(DriftSeverity) == 4


class TestModelVersionSemanticDriftInstantiation:
    def test_default_instantiation(self):
        mvsd = ModelVersionSemanticDrift()
        assert mvsd.drift_threshold_mean_shift == 0.15
        assert mvsd.drift_threshold_variance_shift == 0.30
        assert mvsd.max_minor_drift == 3
        assert mvsd.model_fingerprints == {}
        assert mvsd.benchmark_baselines == {}
        assert mvsd.drift_events == []

    def test_custom_thresholds(self):
        mvsd = ModelVersionSemanticDrift(
            drift_threshold_mean_shift=0.2,
            drift_threshold_variance_shift=0.4,
            max_minor_drift=5,
        )
        assert mvsd.drift_threshold_mean_shift == 0.2
        assert mvsd.max_minor_drift == 5


class TestRegisterModel:
    def test_register_model(self):
        mvsd = ModelVersionSemanticDrift()
        mvsd.register_model("gpt-4", "2024-01", "openai")
        assert "gpt-4" in mvsd.model_fingerprints
        assert mvsd.model_fingerprints["gpt-4"]["version"] == "2024-01"
        assert mvsd.model_fingerprints["gpt-4"]["provider"] == "openai"

    def test_register_model_with_deprecation(self):
        mvsd = ModelVersionSemanticDrift()
        dep_date = time.time() + 86400 * 5
        mvsd.register_model("gpt-3.5", "v1", "openai", deprecation_date=dep_date)
        assert mvsd.model_fingerprints["gpt-3.5"]["deprecation_date"] == dep_date

    def test_register_model_creates_fingerprint(self):
        mvsd = ModelVersionSemanticDrift()
        mvsd.register_model("m1", "v1", "p1")
        assert "fingerprint" in mvsd.model_fingerprints["m1"]
        assert len(mvsd.model_fingerprints["m1"]["fingerprint"]) == 16

    def test_register_model_overwrite(self):
        mvsd = ModelVersionSemanticDrift()
        mvsd.register_model("m1", "v1", "p1")
        mvsd.register_model("m1", "v2", "p1")
        assert mvsd.model_fingerprints["m1"]["version"] == "v2"


class TestRecordBenchmark:
    def test_record_benchmark(self):
        mvsd = ModelVersionSemanticDrift()
        mvsd.register_model("m1", "v1", "p1")
        result = mvsd.record_benchmark("m1", "accuracy", [0.9, 0.92, 0.88])
        assert result["model_id"] == "m1"
        assert result["benchmark"] == "accuracy"
        assert result["sample_count"] == 3

    def test_record_benchmark_unknown_model(self):
        mvsd = ModelVersionSemanticDrift()
        result = mvsd.record_benchmark("unknown", "acc", [0.5])
        assert result["error"] == "unknown_model"

    def test_record_benchmark_empty_scores(self):
        mvsd = ModelVersionSemanticDrift()
        mvsd.register_model("m1", "v1", "p1")
        result = mvsd.record_benchmark("m1", "acc", [])
        assert result["mean_score"] == 0.0
        assert result["sample_count"] == 0


class TestCheckSemanticDrift:
    def test_no_baseline(self):
        mvsd = ModelVersionSemanticDrift()
        result = mvsd.check_semantic_drift("m1", "acc", [0.9])
        assert result["severity"] == DriftSeverity.NONE.value
        assert result["reason"] == "no_baseline"

    def test_no_baseline_for_benchmark(self):
        mvsd = ModelVersionSemanticDrift()
        mvsd.register_model("m1", "v1", "p1")
        mvsd.record_benchmark("m1", "acc", [0.9, 0.91])
        result = mvsd.check_semantic_drift("m1", "other_bench", [0.9])
        assert result["reason"] == "no_baseline_for_other_bench"

    def test_no_drift(self):
        mvsd = ModelVersionSemanticDrift()
        mvsd.register_model("m1", "v1", "p1")
        mvsd.record_benchmark("m1", "acc", [0.9, 0.91, 0.89])
        result = mvsd.check_semantic_drift("m1", "acc", [0.9, 0.905, 0.895])
        assert result["severity"] == DriftSeverity.NONE.value

    def test_breaking_drift(self):
        mvsd = ModelVersionSemanticDrift(drift_threshold_mean_shift=0.15)
        mvsd.register_model("m1", "v1", "p1")
        mvsd.record_benchmark("m1", "acc", [0.9, 0.91, 0.89])
        result = mvsd.check_semantic_drift("m1", "acc", [0.3, 0.35, 0.32])
        assert result["severity"] == DriftSeverity.BREAKING.value

    def test_drift_event_recorded(self):
        mvsd = ModelVersionSemanticDrift()
        mvsd.register_model("m1", "v1", "p1")
        mvsd.record_benchmark("m1", "acc", [0.9, 0.91, 0.89])
        mvsd.check_semantic_drift("m1", "acc", [0.3, 0.35])
        assert len(mvsd.drift_events) == 1

    def test_recommendation_rollback_on_breaking(self):
        mvsd = ModelVersionSemanticDrift()
        mvsd.register_model("m1", "v1", "p1")
        mvsd.record_benchmark("m1", "acc", [0.9, 0.91])
        result = mvsd.check_semantic_drift("m1", "acc", [0.3, 0.35])
        if result["severity"] == DriftSeverity.BREAKING.value:
            assert result["recommendation"] == "rollback_model_version"


class TestGetDriftSummary:
    def test_empty_summary(self):
        mvsd = ModelVersionSemanticDrift()
        summary = mvsd.get_drift_summary()
        assert summary["models_tracked"] == 0
        assert summary["breaking_drifts"] == 0
        assert summary["healthy"] is True

    def test_summary_with_drift_events(self):
        mvsd = ModelVersionSemanticDrift()
        mvsd.drift_events = [
            {"severity": "BREAKING", "model_id": "m1"},
            {"severity": "SIGNIFICANT", "model_id": "m2"},
            {"severity": "MINOR", "model_id": "m3"},
        ]
        summary = mvsd.get_drift_summary()
        assert summary["breaking_drifts"] == 1
        assert summary["significant_drifts"] == 1
        assert summary["minor_drifts"] == 1
        assert summary["healthy"] is False

    def test_summary_recommendation_freeze_on_breaking(self):
        mvsd = ModelVersionSemanticDrift()
        mvsd.drift_events = [{"severity": "BREAKING"}]
        summary = mvsd.get_drift_summary()
        assert summary["recommendation"] == "freeze_all_model_upgrades"


class TestOverallModelHealth:
    def test_no_models_perfect_health(self):
        mvsd = ModelVersionSemanticDrift()
        assert mvsd.overall_model_health() == 1.0

    def test_health_with_breaking_drift(self):
        mvsd = ModelVersionSemanticDrift()
        mvsd.model_fingerprints = {"m1": {}}
        mvsd.drift_events = [{"severity": "BREAKING"}]
        health = mvsd.overall_model_health()
        assert health == 0.8

    def test_health_caps_at_zero(self):
        mvsd = ModelVersionSemanticDrift()
        mvsd.model_fingerprints = {"m1": {}}
        mvsd.drift_events = [{"severity": "BREAKING"}] * 10
        health = mvsd.overall_model_health()
        assert health == 0.0


class TestCheckDeprecationProximity:
    def test_no_deprecation_dates(self):
        mvsd = ModelVersionSemanticDrift()
        mvsd.register_model("m1", "v1", "p1")
        alerts = mvsd.check_deprecation_proximity()
        assert alerts == []

    def test_deprecation_soon(self):
        mvsd = ModelVersionSemanticDrift()
        dep_date = time.time() + 86400 * 3
        mvsd.register_model("m1", "v1", "p1", deprecation_date=dep_date)
        alerts = mvsd.check_deprecation_proximity()
        assert len(alerts) >= 1
        assert alerts[0]["model_id"] == "m1"

    def test_deprecation_far_future(self):
        mvsd = ModelVersionSemanticDrift()
        dep_date = time.time() + 86400 * 365
        mvsd.register_model("m1", "v1", "p1", deprecation_date=dep_date)
        alerts = mvsd.check_deprecation_proximity()
        assert len(alerts) == 0

    def test_deprecation_critical(self):
        mvsd = ModelVersionSemanticDrift()
        dep_date = time.time() + 86400 * 0.5
        mvsd.register_model("m1", "v1", "p1", deprecation_date=dep_date)
        alerts = mvsd.check_deprecation_proximity()
        assert any(a["severity"] == "CRITICAL" for a in alerts)
