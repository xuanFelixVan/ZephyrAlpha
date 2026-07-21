# [A_test] module_id: MOD-GOV_data_source_reliability | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-infra_ops/drift-detector/blueprint.md
# [MODULE] tests.test_data_source_reliability
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] src/zephyr/behavioral-auditor/data_source_reliability.py
# [CONSUMERS] CI pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip
# [TESTS] python -m pytest tests/test_data_source_reliability.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.data_governance.data_source_reliability import (
    DIMENSION_WEIGHTS,
    ReliabilityDimension,
    ReliabilityScore,
    compare_sources,
    score_source,
)


class TestReliabilityDimension:
    def test_enum_values(self):
        assert ReliabilityDimension.UPTIME.value == "Uptime"
        assert ReliabilityDimension.ACCURACY.value == "Accuracy"
        assert ReliabilityDimension.TIMELINESS.value == "Timeliness"
        assert ReliabilityDimension.COMPLETENESS.value == "Completeness"
        assert ReliabilityDimension.CONSISTENCY.value == "Consistency"

    def test_enum_members_count(self):
        assert len(ReliabilityDimension) == 5

    def test_enum_is_str(self):
        for dim in ReliabilityDimension:
            assert isinstance(dim.value, str)


class TestDimensionWeights:
    def test_all_dimensions_have_weights(self):
        for dim in ReliabilityDimension:
            assert dim in DIMENSION_WEIGHTS

    def test_weights_sum_to_one(self):
        total = sum(DIMENSION_WEIGHTS.values())
        assert abs(total - 1.0) < 1e-9

    def test_weights_are_positive(self):
        for dim, weight in DIMENSION_WEIGHTS.items():
            assert weight > 0


class TestReliabilityScore:
    def test_default_values(self):
        rs = ReliabilityScore(source="test")
        assert rs.source == "test"
        assert rs.scores == {}
        assert rs.composite == 0.0

    def test_compute_composite_with_scores(self):
        rs = ReliabilityScore(
            source="test",
            scores={dim: 1.0 for dim in ReliabilityDimension},
        )
        result = rs.compute_composite()
        assert result == 1.0
        assert rs.composite == 1.0

    def test_compute_composite_partial_scores(self):
        rs = ReliabilityScore(
            source="test",
            scores={ReliabilityDimension.UPTIME: 0.8, ReliabilityDimension.ACCURACY: 0.9},
        )
        result = rs.compute_composite()
        assert result > 0.0
        assert result < 1.0

    def test_compute_composite_empty_scores(self):
        rs = ReliabilityScore(source="test")
        result = rs.compute_composite()
        assert result == 0.0

    def test_rating_excellent(self):
        rs = ReliabilityScore(source="test", composite=0.95)
        assert rs.rating == "A — Excellent"

    def test_rating_good(self):
        rs = ReliabilityScore(source="test", composite=0.80)
        assert rs.rating == "B — Good"

    def test_rating_acceptable(self):
        rs = ReliabilityScore(source="test", composite=0.65)
        assert rs.rating == "C — Acceptable"

    def test_rating_degraded(self):
        rs = ReliabilityScore(source="test", composite=0.45)
        assert rs.rating == "D — Degraded"

    def test_rating_unreliable(self):
        rs = ReliabilityScore(source="test", composite=0.2)
        assert rs.rating == "F — Unreliable"

    def test_rating_boundary_90(self):
        rs = ReliabilityScore(source="test", composite=0.90)
        assert rs.rating == "A — Excellent"

    def test_rating_boundary_75(self):
        rs = ReliabilityScore(source="test", composite=0.75)
        assert rs.rating == "B — Good"

    def test_rating_boundary_60(self):
        rs = ReliabilityScore(source="test", composite=0.60)
        assert rs.rating == "C — Acceptable"

    def test_rating_boundary_40(self):
        rs = ReliabilityScore(source="test", composite=0.40)
        assert rs.rating == "D — Degraded"


class TestScoreSource:
    def test_returns_reliability_score(self):
        scores = {dim: 0.9 for dim in ReliabilityDimension}
        result = score_source("api_v2", scores)
        assert isinstance(result, ReliabilityScore)
        assert result.source == "api_v2"

    def test_composite_computed(self):
        scores = {dim: 0.8 for dim in ReliabilityDimension}
        result = score_source("api_v2", scores)
        assert result.composite > 0.0

    def test_empty_scores(self):
        result = score_source("empty", {})
        assert result.composite == 0.0


class TestCompareSources:
    def test_sorted_descending(self):
        s1 = ReliabilityScore(source="low", composite=0.3)
        s2 = ReliabilityScore(source="high", composite=0.9)
        s3 = ReliabilityScore(source="mid", composite=0.6)
        result = compare_sources(s1, s2, s3)
        assert result[0][0] == "high"
        assert result[1][0] == "mid"
        assert result[2][0] == "low"

    def test_single_source(self):
        s1 = ReliabilityScore(source="only", composite=0.5)
        result = compare_sources(s1)
        assert len(result) == 1
        assert result[0] == ("only", 0.5)

    def test_empty_input(self):
        result = compare_sources()
        assert result == []
