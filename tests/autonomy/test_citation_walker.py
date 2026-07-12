# [A_test] module_id: SRC-TST-0523 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_citation_walker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_citation_walker.py
# [TTL] task_bound

import pytest

from zephyr.gov_kb.citation_walker import (
    CitationPath,
    CitationWalker,
)


class TestCitationPath:
    def test_instantiation(self):
        cp = CitationPath(ke_id="KE-001", cited_by=["KE-002"], depth=1, impact_score=0.5)
        assert cp.ke_id == "KE-001"
        assert cp.cited_by == ["KE-002"]
        assert cp.depth == 1
        assert cp.impact_score == 0.5

    def test_missing_field_raises(self):
        with pytest.raises(TypeError):
            CitationPath()


class TestCitationWalker:
    def test_instantiation(self):
        walker = CitationWalker()
        assert walker is not None

    def test_walk_simple_graph(self):
        walker = CitationWalker()
        graph = {"KE-001": ["KE-002", "KE-003"], "KE-002": [], "KE-003": []}
        paths = walker.walk("KE-001", graph)
        assert len(paths) == 3
        ke_ids = [p.ke_id for p in paths]
        assert "KE-001" in ke_ids
        assert "KE-002" in ke_ids
        assert "KE-003" in ke_ids

    def test_walk_empty_graph(self):
        walker = CitationWalker()
        paths = walker.walk("KE-001", {})
        assert len(paths) == 1
        assert paths[0].ke_id == "KE-001"
        assert paths[0].cited_by == []

    def test_walk_respects_max_depth(self):
        walker = CitationWalker()
        graph = {
            "KE-001": ["KE-002"],
            "KE-002": ["KE-003"],
            "KE-003": ["KE-004"],
            "KE-004": ["KE-005"],
        }
        paths = walker.walk("KE-001", graph, max_depth=1)
        ke_ids = [p.ke_id for p in paths]
        assert "KE-001" in ke_ids
        assert "KE-002" in ke_ids
        assert "KE-003" not in ke_ids

    def test_walk_no_cycles(self):
        walker = CitationWalker()
        graph = {
            "KE-001": ["KE-002"],
            "KE-002": ["KE-001"],
        }
        paths = walker.walk("KE-001", graph)
        ke_ids = [p.ke_id for p in paths]
        assert ke_ids.count("KE-001") == 1
        assert ke_ids.count("KE-002") == 1

    def test_walk_impact_score(self):
        walker = CitationWalker()
        graph = {"KE-001": ["KE-002", "KE-003"]}
        paths = walker.walk("KE-001", graph)
        root = next(p for p in paths if p.ke_id == "KE-001")
        assert root.impact_score == 2.0

    def test_walk_depth_zero_start(self):
        walker = CitationWalker()
        graph = {"KE-001": ["KE-002"]}
        paths = walker.walk("KE-001", graph)
        root = next(p for p in paths if p.ke_id == "KE-001")
        assert root.depth == 0

    def test_walk_child_depth_increments(self):
        walker = CitationWalker()
        graph = {"KE-001": ["KE-002"]}
        paths = walker.walk("KE-001", graph)
        child = next(p for p in paths if p.ke_id == "KE-002")
        assert child.depth == 1

    def test_walk_start_not_in_graph(self):
        walker = CitationWalker()
        paths = walker.walk("KE-999", {"KE-001": []})
        assert len(paths) == 1
        assert paths[0].ke_id == "KE-999"
        assert paths[0].cited_by == []
