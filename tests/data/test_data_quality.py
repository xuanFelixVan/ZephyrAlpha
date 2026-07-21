# [A_test] module_id: MOD-GOV_data_quality | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-374 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_data_quality
# [INVARIANTS] DQ_SPECS covers all DQDimension values; score_dq returns 0.0 for unknown dim
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_data_quality.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.data_governance.data_quality import (
    DQ_DIM_COUNT,
    DQ_SPECS,
    DQDimension,
    DQSpec,
    get_dq_spec,
    score_dq,
)


class TestDQDimension:
    def test_all_dimensions_exist(self):
        assert len(DQDimension) == DQ_DIM_COUNT

    def test_dimension_values(self):
        expected = {"Completeness", "Accuracy", "Consistency", "Timeliness", "Uniqueness", "Validity"}
        actual = {d.value for d in DQDimension}
        assert actual == expected


class TestDQSpec:
    def test_spec_creation_defaults(self):
        spec = DQSpec(dimension=DQDimension.ACCURACY, label="test", metric="m1")
        assert spec.threshold == 0.95
        assert spec.check_func == ""

    def test_spec_creation_custom(self):
        spec = DQSpec(dimension=DQDimension.COMPLETENESS, label="t", metric="m", threshold=0.80, check_func="cf")
        assert spec.threshold == 0.80
        assert spec.check_func == "cf"


class TestDQSpecs:
    def test_all_dimensions_have_specs(self):
        for dim in DQDimension:
            assert dim in DQ_SPECS

    def test_specs_have_check_funcs(self):
        for dim, spec in DQ_SPECS.items():
            assert spec.check_func != ""
            assert spec.dimension == dim


class TestGetDqSpec:
    def test_known_dimension(self):
        spec = get_dq_spec(DQDimension.ACCURACY)
        assert spec is not None
        assert spec.dimension == DQDimension.ACCURACY

    def test_returns_correct_spec(self):
        spec = get_dq_spec(DQDimension.COMPLETENESS)
        assert spec is not None
        assert spec.metric == "missing_pct"

    def test_all_dimensions_retrievable(self):
        for dim in DQDimension:
            assert get_dq_spec(dim) is not None


class TestScoreDq:
    def test_score_at_threshold(self):
        spec = get_dq_spec(DQDimension.COMPLETENESS)
        score = score_dq(DQDimension.COMPLETENESS, spec.threshold)
        assert score == 1.0

    def test_score_above_threshold_capped(self):
        score = score_dq(DQDimension.COMPLETENESS, 2.0)
        assert score == 1.0

    def test_score_below_threshold(self):
        score = score_dq(DQDimension.ACCURACY, 0.5)
        assert 0.0 < score < 1.0

    def test_score_zero_value(self):
        score = score_dq(DQDimension.ACCURACY, 0.0)
        assert score == 0.0


class TestBoundary:
    def test_dq_dim_count_matches_enum(self):
        assert len(DQDimension) == DQ_DIM_COUNT

    def test_score_dq_consistency(self):
        spec = get_dq_spec(DQDimension.CONSISTENCY)
        score = score_dq(DQDimension.CONSISTENCY, spec.threshold)
        assert score == 1.0
