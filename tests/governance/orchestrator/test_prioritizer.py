# [A_test] module_id: SRC-TST-1399 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_prioritizer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_prioritizer.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_code_quality.code_dedup.prioritizer import PrioritizedFix, Prioritizer


class TestPrioritizedFix:
    def test_default_values(self):
        pf = PrioritizedFix()
        assert pf.dup_group_id == ""
        assert pf.confidence == 0.0
        assert pf.impact_scope == 0
        assert pf.suitability == 0
        assert pf.priority_score == 0.0
        assert pf.rank == 0
        assert pf.action == ""


class TestPrioritizer:
    def test_instantiation(self):
        p = Prioritizer()
        assert p is not None

    def test_rank_empty(self):
        p = Prioritizer()
        result = p.rank([])
        assert result == []

    def test_rank_single_high_confidence(self):
        p = Prioritizer()
        result = p.rank([("DUP-001", 0.95, 80, 90)])
        assert len(result) == 1
        assert result[0].dup_group_id == "DUP-001"
        assert result[0].rank == 1
        assert result[0].action == "AUTO_FIX"

    def test_rank_single_medium_confidence(self):
        p = Prioritizer()
        result = p.rank([("DUP-002", 0.6, 50, 50)])
        assert result[0].action == "SUGGEST"

    def test_rank_single_low_confidence(self):
        p = Prioritizer()
        result = p.rank([("DUP-003", 0.1, 10, 10)])
        assert result[0].action == "INFORM"

    def test_rank_sorted_descending(self):
        p = Prioritizer()
        candidates = [
            ("DUP-LOW", 0.2, 20, 20),
            ("DUP-HIGH", 0.95, 90, 90),
            ("DUP-MED", 0.6, 50, 50),
        ]
        result = p.rank(candidates)
        assert result[0].dup_group_id == "DUP-HIGH"
        assert result[0].rank == 1
        assert result[1].dup_group_id == "DUP-MED"
        assert result[1].rank == 2
        assert result[2].dup_group_id == "DUP-LOW"
        assert result[2].rank == 3

    def test_rank_score_calculation(self):
        p = Prioritizer()
        result = p.rank([("DUP-001", 1.0, 100, 100)])
        expected = 1.0 * 0.4 + 1.0 * 0.3 + 1.0 * 0.3
        assert abs(result[0].priority_score - round(expected, 3)) < 0.001

    def test_rank_impact_capped_at_100(self):
        p = Prioritizer()
        result = p.rank([("DUP-001", 0.5, 200, 50)])
        assert result[0].impact_scope == 200

    def test_rank_zero_values(self):
        p = Prioritizer()
        result = p.rank([("DUP-000", 0.0, 0, 0)])
        assert result[0].priority_score == 0.0
        assert result[0].action == "INFORM"

    def test_rank_multiple_same_score(self):
        p = Prioritizer()
        result = p.rank([("DUP-A", 0.5, 50, 50), ("DUP-B", 0.5, 50, 50)])
        assert len(result) == 2
        assert result[0].rank == 1
        assert result[1].rank == 2
