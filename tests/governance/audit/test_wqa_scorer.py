# [A_test] module_id: SRC-TST-1808 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_wqa_scorer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_audit.wqa_scorer import WQA_DIMENSIONS, WQAScore


class TestWQAScore:
    def test_default_values(self):
        score = WQAScore()
        assert score.w1_test_coverage == 0.0
        assert score.w2_blueprint_alignment == 0.0
        assert score.w3_ruff_zero_warn == 0.0
        assert score.w4_gate_no_new_fail == 0.0
        assert score.w5_owner_no_revert == 0.0
        assert score.w6_session_completion == 0.0
        assert score.w7_token_efficiency == 0.0

    def test_composite_all_zeros(self):
        score = WQAScore()
        assert score.composite == 0.0

    def test_composite_all_ones(self):
        score = WQAScore(
            w1_test_coverage=1.0,
            w2_blueprint_alignment=1.0,
            w3_ruff_zero_warn=1.0,
            w4_gate_no_new_fail=1.0,
            w5_owner_no_revert=1.0,
            w6_session_completion=1.0,
            w7_token_efficiency=1.0,
        )
        assert score.composite == 1.0

    def test_composite_partial(self):
        score = WQAScore(w1_test_coverage=0.5, w4_gate_no_new_fail=0.5)
        expected = 0.5 * 0.20 + 0.5 * 0.20
        assert abs(score.composite - expected) < 0.001

    def test_rating_a_plus(self):
        score = WQAScore(
            w1_test_coverage=0.95,
            w2_blueprint_alignment=0.95,
            w3_ruff_zero_warn=0.9,
            w4_gate_no_new_fail=0.95,
            w5_owner_no_revert=0.9,
            w6_session_completion=0.9,
            w7_token_efficiency=0.9,
        )
        assert score.rating == "A+"

    def test_rating_a(self):
        score = WQAScore(
            w1_test_coverage=0.85,
            w2_blueprint_alignment=0.85,
            w3_ruff_zero_warn=0.8,
            w4_gate_no_new_fail=0.85,
            w5_owner_no_revert=0.8,
            w6_session_completion=0.8,
            w7_token_efficiency=0.8,
        )
        assert score.rating == "A"

    def test_rating_b(self):
        score = WQAScore(
            w1_test_coverage=0.75,
            w2_blueprint_alignment=0.7,
            w3_ruff_zero_warn=0.7,
            w4_gate_no_new_fail=0.7,
            w5_owner_no_revert=0.7,
            w6_session_completion=0.7,
            w7_token_efficiency=0.7,
        )
        assert score.rating == "B"

    def test_rating_c(self):
        score = WQAScore(
            w1_test_coverage=0.65,
            w2_blueprint_alignment=0.6,
            w3_ruff_zero_warn=0.6,
            w4_gate_no_new_fail=0.6,
            w5_owner_no_revert=0.6,
            w6_session_completion=0.6,
            w7_token_efficiency=0.6,
        )
        assert score.rating == "C"

    def test_rating_d(self):
        score = WQAScore(
            w1_test_coverage=0.5,
            w2_blueprint_alignment=0.5,
            w3_ruff_zero_warn=0.5,
            w4_gate_no_new_fail=0.5,
            w5_owner_no_revert=0.5,
            w6_session_completion=0.5,
            w7_token_efficiency=0.5,
        )
        assert score.rating == "D"

    def test_rating_f(self):
        score = WQAScore()
        assert score.rating == "F"

    def test_composite_rounding(self):
        score = WQAScore(w1_test_coverage=0.333, w4_gate_no_new_fail=0.667)
        result = score.composite
        assert isinstance(result, float)
        assert len(str(result).split(".")[-1]) <= 3


class TestWQADimensions:
    def test_seven_dimensions(self):
        assert len(WQA_DIMENSIONS) == 7

    def test_dimension_structure(self):
        for key, value in WQA_DIMENSIONS.items():
            assert len(value) == 3
            idx, weight, desc = value
            assert isinstance(idx, int)
            assert isinstance(weight, float)
            assert isinstance(desc, str)

    def test_weights_sum_to_one(self):
        total = sum(v[1] for v in WQA_DIMENSIONS.values())
        assert abs(total - 1.0) < 0.001
