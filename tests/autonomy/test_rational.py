# [A_test] module_id: SRC-TST-1426 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_rational
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_rational.py -q
# [TTL] task_bound
from __future__ import annotations

from zephyr.gov_kb.ke_justification import KEJustificationGenerator, SelectedKE


class TestSelectedKE:
    def test_fields_assigned(self):
        ske = SelectedKE(ke_id="KE-1", reason="keyword_match", score=0.9)
        assert ske.ke_id == "KE-1"
        assert ske.reason == "keyword_match"
        assert ske.score == 0.9

    def test_score_can_be_zero(self):
        ske = SelectedKE(ke_id="KE-X", reason="none", score=0.0)
        assert ske.score == 0.0

    def test_score_can_be_one(self):
        ske = SelectedKE(ke_id="KE-Y", reason="full", score=1.0)
        assert ske.score == 1.0


class TestKEJustificationGeneratorInstantiation:
    def test_can_instantiate(self):
        gen = KEJustificationGenerator()
        assert gen is not None


class TestJustify:
    def test_returns_selected_ke_list(self):
        gen = KEJustificationGenerator()
        result = gen.justify(["KE-1"], [0.8])
        assert len(result) == 1
        assert isinstance(result[0], SelectedKE)

    def test_ke_ids_preserved(self):
        gen = KEJustificationGenerator()
        result = gen.justify(["KE-A", "KE-B"], [0.5, 0.7])
        assert result[0].ke_id == "KE-A"
        assert result[1].ke_id == "KE-B"

    def test_scores_preserved(self):
        gen = KEJustificationGenerator()
        result = gen.justify(["KE-1", "KE-2"], [0.3, 0.9])
        assert result[0].score == 0.3
        assert result[1].score == 0.9

    def test_reason_cycles_through_four_types(self):
        gen = KEJustificationGenerator()
        result = gen.justify(
            ["KE-1", "KE-2", "KE-3", "KE-4"],
            [0.1, 0.2, 0.3, 0.4],
        )
        reasons = [r.reason for r in result]
        assert reasons == [
            "keyword_match",
            "similarity_top_k",
            "authority_boosted",
            "freshness_promoted",
        ]

    def test_reason_wraps_around_after_four(self):
        gen = KEJustificationGenerator()
        result = gen.justify(
            ["KE-1", "KE-2", "KE-3", "KE-4", "KE-5"],
            [0.1, 0.2, 0.3, 0.4, 0.5],
        )
        assert result[4].reason == "keyword_match"

    def test_empty_inputs(self):
        gen = KEJustificationGenerator()
        result = gen.justify([], [])
        assert result == []

    def test_single_entry(self):
        gen = KEJustificationGenerator()
        result = gen.justify(["KE-S"], [1.0])
        assert len(result) == 1
        assert result[0].ke_id == "KE-S"
        assert result[0].score == 1.0
        assert result[0].reason == "keyword_match"

    def test_mismatched_lengths_zip_stops_at_shorter(self):
        gen = KEJustificationGenerator()
        result = gen.justify(["KE-1", "KE-2"], [0.5])
        assert len(result) == 1
