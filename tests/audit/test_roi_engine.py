# [A_test] module_id: SRC-TST-1471 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_roi_engine
# [INVARIANTS] ROI计算不可人为调整
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_roi_engine.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_drift.roi_engine import (
    ROIEngine,
    ROIScore,
)


class TestROIScore:
    def test_creation(self):
        score = ROIScore(
            detector_id="d1",
            impact_weight=10.0,
            frequency_score=1.0,
            effort_score=3.0,
            roi=3.3333,
            rank=0,
            effort_tier="suggestion_simple",
        )
        assert score.detector_id == "d1"
        assert score.impact_weight == 10.0
        assert score.roi == 3.3333
        assert score.rank == 0
        assert score.computed_at == ""

    def test_with_timestamp(self):
        score = ROIScore(
            detector_id="d2",
            impact_weight=5.0,
            frequency_score=2.0,
            effort_score=8.0,
            roi=1.25,
            rank=1,
            effort_tier="suggestion_complex",
            computed_at="2026-01-01T00:00:00Z",
        )
        assert score.computed_at != ""


class TestROIEngine:
    def test_instantiation(self):
        engine = ROIEngine()
        assert engine._effort_feedback == {}

    def test_compute_p0_high(self):
        engine = ROIEngine()
        score = engine.compute(
            detector_id="d1",
            module_tier="P0",
            severity="HIGH",
            detections_30d=10,
            effort_tier="auto_fixable",
        )
        assert score.detector_id == "d1"
        assert score.impact_weight == 30.0
        assert score.roi > 0
        assert score.effort_tier == "auto_fixable"

    def test_compute_p2_low(self):
        engine = ROIEngine()
        score = engine.compute(
            detector_id="d2",
            module_tier="P2",
            severity="LOW",
            detections_30d=0,
            effort_tier="needs_human",
        )
        assert score.impact_weight == 2.0
        assert score.effort_score == 20.0

    def test_compute_frequency_log(self):
        engine = ROIEngine()
        score_low = engine.compute(detector_id="d3", detections_30d=1)
        score_high = engine.compute(detector_id="d4", detections_30d=100)
        assert score_high.frequency_score > score_low.frequency_score

    def test_compute_zero_detections(self):
        engine = ROIEngine()
        score = engine.compute(detector_id="d5", detections_30d=0)
        assert score.frequency_score == 1.0

    def test_compute_with_feedback(self):
        engine = ROIEngine()
        engine.record_feedback("d6", actual_hours=2.0)
        score = engine.compute(detector_id="d6", effort_tier="needs_human")
        assert score.effort_score == 2.0

    def test_compute_feedback_overrides_effort(self):
        engine = ROIEngine()
        engine.record_feedback("d7", actual_hours=0.5)
        score = engine.compute(detector_id="d7", effort_tier="needs_human")
        assert score.effort_score == 1.0

    def test_compute_unknown_tier(self):
        engine = ROIEngine()
        score = engine.compute(detector_id="d8", module_tier="UNKNOWN", severity="UNKNOWN", effort_tier="unknown_tier")
        assert score.impact_weight == 4.0
        assert score.effort_score == 8.0

    def test_rank_sorts_by_roi(self):
        engine = ROIEngine()
        s1 = ROIScore(
            detector_id="a",
            impact_weight=10.0,
            frequency_score=1.0,
            effort_score=1.0,
            roi=10.0,
            rank=0,
            effort_tier="auto_fixable",
        )
        s2 = ROIScore(
            detector_id="b",
            impact_weight=5.0,
            frequency_score=1.0,
            effort_score=1.0,
            roi=5.0,
            rank=0,
            effort_tier="auto_fixable",
        )
        s3 = ROIScore(
            detector_id="c",
            impact_weight=2.0,
            frequency_score=1.0,
            effort_score=1.0,
            roi=2.0,
            rank=0,
            effort_tier="auto_fixable",
        )
        ranked = engine.rank([s3, s1, s2])
        assert ranked[0].detector_id == "a"
        assert ranked[0].rank == 1
        assert ranked[1].detector_id == "b"
        assert ranked[1].rank == 2
        assert ranked[2].detector_id == "c"
        assert ranked[2].rank == 3

    def test_rank_empty_list(self):
        engine = ROIEngine()
        result = engine.rank([])
        assert result == []

    def test_rank_single_element(self):
        engine = ROIEngine()
        s = ROIScore(
            detector_id="x",
            impact_weight=1.0,
            frequency_score=1.0,
            effort_score=1.0,
            roi=1.0,
            rank=0,
            effort_tier="auto_fixable",
        )
        ranked = engine.rank([s])
        assert len(ranked) == 1
        assert ranked[0].rank == 1

    def test_weight_map(self):
        assert ROIEngine.WEIGHT_MAP["P0"] == 10
        assert ROIEngine.WEIGHT_MAP["P1"] == 5
        assert ROIEngine.WEIGHT_MAP["P2"] == 2

    def test_severity_mult(self):
        assert ROIEngine.SEVERITY_MULT["HIGH"] == 3
        assert ROIEngine.SEVERITY_MULT["MEDIUM"] == 2
        assert ROIEngine.SEVERITY_MULT["LOW"] == 1

    def test_effort_map(self):
        assert ROIEngine.EFFORT_MAP["auto_fixable"] == 1
        assert ROIEngine.EFFORT_MAP["suggestion_simple"] == 3
        assert ROIEngine.EFFORT_MAP["suggestion_complex"] == 8
        assert ROIEngine.EFFORT_MAP["needs_human"] == 20
