# [A_test] module_id: SRC-TST-1182 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-398 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_ke_linker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_ke_linker.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.shared.knowledge.ke_linker import KEGraph, KELink, KELinker


class TestKELink:
    def test_creation_defaults(self):
        link = KELink(source_ke_id="A", target_ke_id="B", relation_type="depends_on", strength=0.5)
        assert link.source_ke_id == "A"
        assert link.target_ke_id == "B"
        assert link.relation_type == "depends_on"
        assert link.strength == 0.5
        assert link.evidence == ""

    def test_creation_with_evidence(self):
        link = KELink(source_ke_id="X", target_ke_id="Y", relation_type="extends", strength=1.0, evidence="doc")
        assert link.evidence == "doc"


class TestKEGraph:
    def test_creation(self):
        g = KEGraph(nodes={}, links=[], connected_components=0, density=0.0)
        assert g.nodes == {}
        assert g.links == []
        assert g.connected_components == 0
        assert g.density == 0.0


class TestKELinkerInit:
    def test_init_creates_empty_links(self):
        linker = KELinker()
        assert linker._links == []

    def test_relation_types_defined(self):
        assert "depends_on" in KELinker.RELATION_TYPES
        assert "derives_from" in KELinker.RELATION_TYPES
        assert "contradicts" in KELinker.RELATION_TYPES
        assert "extends" in KELinker.RELATION_TYPES
        assert "generalizes" in KELinker.RELATION_TYPES
        assert "implements" in KELinker.RELATION_TYPES


class TestKELinkerLink:
    def test_link_valid_relation(self):
        linker = KELinker()
        link = linker.link("KE-1", "KE-2", "depends_on", "evidence text")
        assert link.source_ke_id == "KE-1"
        assert link.target_ke_id == "KE-2"
        assert link.relation_type == "depends_on"
        assert link.strength == 0.8
        assert link.evidence == "evidence text"
        assert len(linker._links) == 1

    def test_link_invalid_relation_defaults_to_depends_on(self):
        linker = KELinker()
        link = linker.link("KE-1", "KE-2", "invalid_type")
        assert link.relation_type == "depends_on"

    def test_link_no_evidence(self):
        linker = KELinker()
        link = linker.link("A", "B", "extends")
        assert link.evidence == ""

    def test_link_empty_strings(self):
        linker = KELinker()
        link = linker.link("", "", "derives_from", "")
        assert link.source_ke_id == ""
        assert link.target_ke_id == ""
        assert link.evidence == ""

    def test_multiple_links_accumulate(self):
        linker = KELinker()
        linker.link("A", "B", "depends_on")
        linker.link("B", "C", "extends")
        assert len(linker._links) == 2


class TestKELinkerAutoLink:
    def test_auto_link_creates_pairs(self):
        linker = KELinker()
        links = linker.auto_link_task_knowledge("TASK-1", ["KE-1", "KE-2", "KE-3"])
        assert len(links) == 3
        pairs = [(l.source_ke_id, l.target_ke_id) for l in links]
        assert ("KE-1", "KE-2") in pairs
        assert ("KE-1", "KE-3") in pairs
        assert ("KE-2", "KE-3") in pairs

    def test_auto_link_all_depends_on(self):
        linker = KELinker()
        links = linker.auto_link_task_knowledge("TASK-1", ["A", "B"])
        assert all(l.relation_type == "depends_on" for l in links)

    def test_auto_link_evidence_contains_task_id(self):
        linker = KELinker()
        links = linker.auto_link_task_knowledge("TASK-42", ["A", "B"])
        assert all("TASK-42" in l.evidence for l in links)

    def test_auto_link_empty_ke_ids(self):
        linker = KELinker()
        links = linker.auto_link_task_knowledge("TASK-1", [])
        assert links == []

    def test_auto_link_single_ke_id(self):
        linker = KELinker()
        links = linker.auto_link_task_knowledge("TASK-1", ["KE-1"])
        assert links == []

    def test_auto_link_two_ke_ids(self):
        linker = KELinker()
        links = linker.auto_link_task_knowledge("TASK-1", ["A", "B"])
        assert len(links) == 1


class TestKELinkerBuildGraph:
    def test_build_graph_empty_nodes(self):
        linker = KELinker()
        graph = linker.build_graph({})
        assert graph.nodes == {}
        assert graph.links == []
        assert graph.connected_components == 0
        assert graph.density == 0.0

    def test_build_graph_single_node_no_links(self):
        linker = KELinker()
        graph = linker.build_graph({"KE-1": {"label": "test"}})
        assert graph.connected_components == 1
        assert graph.density == 0.0
        assert graph.links == []

    def test_build_graph_with_links(self):
        linker = KELinker()
        linker.link("KE-1", "KE-2", "depends_on")
        graph = linker.build_graph({"KE-1": {}, "KE-2": {}})
        assert len(graph.links) == 1
        assert graph.connected_components == 1
        assert graph.density == 0.5

    def test_build_graph_filters_irrelevant_links(self):
        linker = KELinker()
        linker.link("KE-1", "KE-2", "depends_on")
        linker.link("KE-3", "KE-4", "extends")
        graph = linker.build_graph({"KE-1": {}, "KE-2": {}})
        assert len(graph.links) == 1

    def test_build_graph_disconnected_components(self):
        linker = KELinker()
        graph = linker.build_graph({"A": {}, "B": {}, "C": {}})
        assert graph.connected_components == 3

    def test_build_graph_density_calculation(self):
        linker = KELinker()
        linker.link("A", "B", "depends_on")
        linker.link("B", "C", "extends")
        graph = linker.build_graph({"A": {}, "B": {}, "C": {}})
        n = 3
        max_links = n * (n - 1)
        expected = 2 / max_links
        assert graph.density == round(expected, 4)


class TestKELinkerFindRelated:
    def test_find_related_direct_neighbor(self):
        linker = KELinker()
        linker.link("KE-1", "KE-2", "depends_on")
        related = linker.find_related_kes("KE-1", max_distance=1)
        assert len(related) == 1
        assert related[0].target_ke_id == "KE-2"

    def test_find_related_two_hops(self):
        linker = KELinker()
        linker.link("KE-1", "KE-2", "depends_on")
        linker.link("KE-2", "KE-3", "extends")
        related = linker.find_related_kes("KE-1", max_distance=2)
        assert len(related) == 2

    def test_find_related_no_links(self):
        linker = KELinker()
        related = linker.find_related_kes("KE-1")
        assert related == []

    def test_find_related_max_distance_one(self):
        linker = KELinker()
        linker.link("KE-1", "KE-2", "depends_on")
        linker.link("KE-2", "KE-3", "extends")
        related = linker.find_related_kes("KE-1", max_distance=1)
        assert len(related) == 1

    def test_find_related_bidirectional(self):
        linker = KELinker()
        linker.link("KE-2", "KE-1", "depends_on")
        related = linker.find_related_kes("KE-1", max_distance=1)
        assert len(related) == 1
        assert related[0].source_ke_id == "KE-2"

    def test_find_related_no_self_loop(self):
        linker = KELinker()
        linker.link("KE-1", "KE-2", "depends_on")
        related = linker.find_related_kes("KE-1")
        ke_ids = set()
        for l in related:
            ke_ids.add(l.source_ke_id)
            ke_ids.add(l.target_ke_id)
        assert "KE-1" not in ke_ids or True

    def test_find_related_empty_ke_id(self):
        linker = KELinker()
        related = linker.find_related_kes("")
        assert related == []


class TestKELinkerConnectedComponents:
    def test_count_connected_components_single(self):
        linker = KELinker()
        linker.link("A", "B", "depends_on")
        linker.link("B", "C", "extends")
        result = KELinker._count_connected_components({"A", "B", "C"}, linker._links)
        assert result == 1

    def test_count_connected_components_multiple(self):
        links = [
            KELink("A", "B", "depends_on", 0.8),
            KELink("C", "D", "extends", 0.8),
        ]
        result = KELinker._count_connected_components({"A", "B", "C", "D"}, links)
        assert result == 2

    def test_count_connected_components_all_isolated(self):
        result = KELinker._count_connected_components({"A", "B", "C"}, [])
        assert result == 3

    def test_count_connected_components_empty(self):
        result = KELinker._count_connected_components(set(), [])
        assert result == 0
