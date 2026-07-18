# [A_test] module_id: SRC-TST-1063 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-388 | docs/03_modules/_domain_governance/blueprint.md | §test
# [MODULE] tests.test_gov_data_source_reliability
# [INVARIANTS] DIMENSION_WEIGHTS总和=1.0;ReliabilityScore.rating边界正确
# [MODIFY-GUARD] src/zephyr/integration/governance/data_source_reliability.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/test_gov_data_source_reliability.py
# [TTL] task_bound

from __future__ import annotations

import pytest

dsr_mod = pytest.importorskip("zephyr.governance.data_source_reliability")
ReliabilityDimension = dsr_mod.ReliabilityDimension
DIMENSION_WEIGHTS = dsr_mod.DIMENSION_WEIGHTS
ReliabilityScore = dsr_mod.ReliabilityScore
score_source = dsr_mod.score_source
compare_sources = dsr_mod.compare_sources


class TestReliabilityDimension:
    def test_all_values(self):
        assert ReliabilityDimension.UPTIME.value == "Uptime"
        assert ReliabilityDimension.ACCURACY.value == "Accuracy"
        assert ReliabilityDimension.TIMELINESS.value == "Timeliness"
        assert ReliabilityDimension.COMPLETENESS.value == "Completeness"
        assert ReliabilityDimension.CONSISTENCY.value == "Consistency"

    def test_member_count(self):
        assert len(ReliabilityDimension) == 5

    def test_is_str_enum(self):
        assert isinstance(ReliabilityDimension.UPTIME, str)


class TestDimensionWeights:
    def test_all_dimensions_have_weights(self):
        for dim in ReliabilityDimension:
            assert dim in DIMENSION_WEIGHTS, f"Missing weight for {dim}"

    def test_weights_sum_to_one(self):
        total = sum(DIMENSION_WEIGHTS.values())
        assert abs(total - 1.0) < 1e-9

    def test_weights_are_positive(self):
        for dim, weight in DIMENSION_WEIGHTS.items():
            assert weight > 0, f"Non-positive weight for {dim}"


class TestReliabilityScore:
    def test_create_with_defaults(self):
        rs = ReliabilityScore(source="test")
        assert rs.source == "test"
        assert rs.composite == 0.0
        assert rs.scores == {}

    def test_compute_composite_all_perfect(self):
        rs = ReliabilityScore(
            source="perfect",
            scores={dim: 1.0 for dim in ReliabilityDimension},
        )
        result = rs.compute_composite()
        assert result == 1.0
        assert rs.composite == 1.0

    def test_compute_composite_all_zero(self):
        rs = ReliabilityScore(
            source="zero",
            scores={dim: 0.0 for dim in ReliabilityDimension},
        )
        result = rs.compute_composite()
        assert result == 0.0

    def test_compute_composite_partial_scores(self):
        rs = ReliabilityScore(
            source="partial",
            scores={
                ReliabilityDimension.UPTIME: 0.9,
                ReliabilityDimension.ACCURACY: 0.8,
            },
        )
        result = rs.compute_composite()
        expected = 0.9 * 0.25 + 0.8 * 0.30
        assert abs(result - expected) < 1e-4

    def test_compute_composite_empty_scores(self):
        rs = ReliabilityScore(source="empty", scores={})
        result = rs.compute_composite()
        assert result == 0.0

    def test_rating_a_excellent(self):
        rs = ReliabilityScore(source="a", composite=0.95)
        assert rs.rating == "A — Excellent"

    def test_rating_b_good(self):
        rs = ReliabilityScore(source="b", composite=0.80)
        assert rs.rating == "B — Good"

    def test_rating_c_acceptable(self):
        rs = ReliabilityScore(source="c", composite=0.65)
        assert rs.rating == "C — Acceptable"

    def test_rating_d_degraded(self):
        rs = ReliabilityScore(source="d", composite=0.45)
        assert rs.rating == "D — Degraded"

    def test_rating_f_unreliable(self):
        rs = ReliabilityScore(source="f", composite=0.20)
        assert rs.rating == "F — Unreliable"

    def test_rating_boundary_90(self):
        rs = ReliabilityScore(source="boundary", composite=0.90)
        assert rs.rating == "A — Excellent"

    def test_rating_boundary_75(self):
        rs = ReliabilityScore(source="boundary", composite=0.75)
        assert rs.rating == "B — Good"

    def test_rating_boundary_60(self):
        rs = ReliabilityScore(source="boundary", composite=0.60)
        assert rs.rating == "C — Acceptable"

    def test_rating_boundary_40(self):
        rs = ReliabilityScore(source="boundary", composite=0.40)
        assert rs.rating == "D — Degraded"

    def test_rating_just_below_40(self):
        rs = ReliabilityScore(source="low", composite=0.39)
        assert rs.rating == "F — Unreliable"


class TestScoreSource:
    def test_returns_reliability_score(self):
        rs = score_source("test_src", {ReliabilityDimension.UPTIME: 1.0})
        assert isinstance(rs, ReliabilityScore)
        assert rs.source == "test_src"

    def test_computes_composite(self):
        rs = score_source("test_src", {dim: 1.0 for dim in ReliabilityDimension})
        assert rs.composite == 1.0

    def test_empty_scores(self):
        rs = score_source("empty", {})
        assert rs.composite == 0.0


class TestCompareSources:
    def test_sorts_by_composite_descending(self):
        s1 = ReliabilityScore(source="low", composite=0.3)
        s2 = ReliabilityScore(source="high", composite=0.9)
        s3 = ReliabilityScore(source="mid", composite=0.6)
        result = compare_sources(s1, s2, s3)
        assert result[0][0] == "high"
        assert result[1][0] == "mid"
        assert result[2][0] == "low"

    def test_single_source(self):
        s = ReliabilityScore(source="only", composite=0.5)
        result = compare_sources(s)
        assert len(result) == 1
        assert result[0][0] == "only"

    def test_equal_composites(self):
        s1 = ReliabilityScore(source="a", composite=0.5)
        s2 = ReliabilityScore(source="b", composite=0.5)
        result = compare_sources(s1, s2)
        assert len(result) == 2
