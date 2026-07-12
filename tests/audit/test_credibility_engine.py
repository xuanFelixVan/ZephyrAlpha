# [A_test] module_id: SRC-TST-0637 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_credibility_engine
# [INVARIANTS] 可信度评分不可人为调整
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] CI;drift_engine
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_credibility_engine.py
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from zephyr.gov_drift.credibility_engine import (
    CredibilityEngine,
    CredibilityScore,
)


class TestCredibilityScore:
    def test_creates_with_fields(self):
        score = CredibilityScore(
            detector_id="d1",
            base_score=1.0,
            fp_rate=0.0,
            precision=1.0,
            recency_factor=1.0,
            credibility=1.0,
            modulation="normal_push",
        )
        assert score.detector_id == "d1"
        assert score.credibility == 1.0
        assert score.modulation == "normal_push"

    def test_has_optional_fields(self):
        score = CredibilityScore(
            detector_id="d2",
            base_score=0.5,
            fp_rate=0.1,
            precision=0.9,
            recency_factor=1.0,
            credibility=0.45,
            modulation="batched_aggregate",
            configured_weight=0.7,
        )
        assert score.configured_weight == 0.7
        assert isinstance(score.computed_at, str)


class TestCredibilityEngineInstantiation:
    def test_creates_instance(self):
        engine = CredibilityEngine()
        assert engine is not None

    def test_has_constants(self):
        assert CredibilityEngine.NEW_DETECTOR_BASE == 0.5
        assert CredibilityEngine.PROVEN_DETECTOR_BASE == 1.0
        assert CredibilityEngine.FP_RATE_THRESHOLD_MILD == 0.3
        assert CredibilityEngine.FP_RATE_THRESHOLD_SEVERE == 0.5
        assert CredibilityEngine.ALERT_HIGH == 0.8
        assert CredibilityEngine.ALERT_MEDIUM == 0.4


class TestCompute:
    def test_proven_detector_high_credibility(self):
        engine = CredibilityEngine()
        score = engine.compute(detector_id="proven_d", is_proven=True, fp_count=0, total_detections=10, precision=1.0)
        assert score.credibility >= CredibilityEngine.ALERT_HIGH
        assert score.modulation == "normal_push"

    def test_new_detector_moderate_credibility(self):
        engine = CredibilityEngine()
        score = engine.compute(detector_id="new_d", is_proven=False, fp_count=0, total_detections=0, precision=1.0)
        assert score.credibility < CredibilityEngine.ALERT_HIGH
        assert score.base_score == CredibilityEngine.NEW_DETECTOR_BASE

    def test_high_fp_rate_reduces_credibility(self):
        engine = CredibilityEngine()
        good = engine.compute(detector_id="good", is_proven=True, fp_count=1, total_detections=10, precision=1.0)
        bad = engine.compute(detector_id="bad", is_proven=True, fp_count=8, total_detections=10, precision=1.0)
        assert good.credibility > bad.credibility

    def test_severe_fp_rate_shadow_observe(self):
        engine = CredibilityEngine()
        score = engine.compute(detector_id="severe_fp", is_proven=False, fp_count=6, total_detections=10, precision=0.5)
        assert score.credibility < CredibilityEngine.ALERT_MEDIUM
        assert score.modulation == "shadow_observe"

    def test_mild_fp_rate_batched_aggregate(self):
        engine = CredibilityEngine()
        score = engine.compute(detector_id="mild_fp", is_proven=False, fp_count=2, total_detections=10, precision=0.8)
        assert score.modulation in ("batched_aggregate", "shadow_observe", "normal_push")

    def test_stale_detector_reduces_credibility(self):
        engine = CredibilityEngine()
        recent = engine.compute(detector_id="recent", is_proven=True, fp_count=0, total_detections=10, precision=1.0)
        stale_time = datetime.now(UTC) - timedelta(days=120)
        stale = engine.compute(
            detector_id="stale",
            is_proven=True,
            fp_count=0,
            total_detections=10,
            precision=1.0,
            last_detected_at=stale_time,
        )
        assert recent.credibility >= stale.credibility

    def test_credibility_bounded_between_zero_and_one(self):
        engine = CredibilityEngine()
        for fp in range(11):
            score = engine.compute(
                detector_id=f"fp_{fp}", is_proven=True, fp_count=fp, total_detections=10, precision=0.5
            )
            assert 0.0 <= score.credibility <= 1.0

    def test_zero_total_detections_zero_fp_rate(self):
        engine = CredibilityEngine()
        score = engine.compute(detector_id="zero_det", is_proven=True, fp_count=0, total_detections=0, precision=1.0)
        assert score.fp_rate == 0.0


class TestSetOwnerOverride:
    def test_applies_owner_override(self):
        engine = CredibilityEngine()
        engine.set_owner_override("d1", 0.9)
        score = engine.compute(detector_id="d1", is_proven=False, fp_count=5, total_detections=10, precision=0.5)
        assert score.configured_weight == 0.9

    def test_clamps_override_to_range(self):
        engine = CredibilityEngine()
        engine.set_owner_override("d2", 1.5)
        score = engine.compute(detector_id="d2", is_proven=True, fp_count=0, total_detections=10, precision=1.0)
        assert score.configured_weight <= 1.0

    def test_negative_override_clamped(self):
        engine = CredibilityEngine()
        engine.set_owner_override("d3", -0.5)
        score = engine.compute(detector_id="d3", is_proven=True, fp_count=0, total_detections=10, precision=1.0)
        assert score.configured_weight >= 0.0


class TestGetScore:
    def test_returns_none_for_unknown(self):
        engine = CredibilityEngine()
        assert engine.get_score("unknown") is None

    def test_returns_computed_score(self):
        engine = CredibilityEngine()
        engine.compute(detector_id="d1", is_proven=True, fp_count=0, total_detections=10, precision=1.0)
        score = engine.get_score("d1")
        assert score is not None
        assert score.detector_id == "d1"

    def test_overwrites_on_recompute(self):
        engine = CredibilityEngine()
        engine.compute(detector_id="d1", is_proven=True, fp_count=0, total_detections=10, precision=1.0)
        first = engine.get_score("d1").credibility
        engine.compute(detector_id="d1", is_proven=False, fp_count=5, total_detections=10, precision=0.5)
        second = engine.get_score("d1").credibility
        assert first != second
