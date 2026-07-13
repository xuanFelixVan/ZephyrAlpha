# [A_test] module_id: SRC-TST-1084 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_guard_interaction_topology_mapper
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.reliability.guard_interaction_topology_mapper
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_guard_interaction_topology_mapper.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.reliability.guard_interaction_topology_mapper import (
    GuardEdge,
    GuardInteractionTopologyMapper,
)


class TestGuardEdgeDataclass:
    def test_creation_with_defaults(self):
        e = GuardEdge(from_guard="A", to_guard="B")
        assert e.from_guard == "A"
        assert e.to_guard == "B"
        assert e.interaction_count == 0

    def test_creation_with_count(self):
        e = GuardEdge(from_guard="A", to_guard="B", interaction_count=5)
        assert e.interaction_count == 5


class TestGuardInteractionTopologyMapperInstantiation:
    def test_default_values(self):
        mapper = GuardInteractionTopologyMapper()
        assert mapper.edges == []
        assert mapper.adjacency == {}
        assert mapper.cycle_max_depth == 6

    def test_custom_values(self):
        mapper = GuardInteractionTopologyMapper(cycle_max_depth=10)
        assert mapper.cycle_max_depth == 10


class TestRecordInteraction:
    def test_first_interaction_creates_edge(self):
        mapper = GuardInteractionTopologyMapper()
        mapper.record_interaction("A", "B")
        assert len(mapper.edges) == 1
        assert mapper.edges[0].from_guard == "A"
        assert mapper.edges[0].to_guard == "B"
        assert mapper.edges[0].interaction_count == 1

    def test_repeated_interaction_increments_count(self):
        mapper = GuardInteractionTopologyMapper()
        mapper.record_interaction("A", "B")
        mapper.record_interaction("A", "B")
        assert len(mapper.edges) == 1
        assert mapper.edges[0].interaction_count == 2

    def test_builds_adjacency(self):
        mapper = GuardInteractionTopologyMapper()
        mapper.record_interaction("A", "B")
        assert "A" in mapper.adjacency
        assert "B" in mapper.adjacency["A"]

    def test_multiple_targets_from_same_source(self):
        mapper = GuardInteractionTopologyMapper()
        mapper.record_interaction("A", "B")
        mapper.record_interaction("A", "C")
        assert len(mapper.adjacency["A"]) == 2
        assert len(mapper.edges) == 2

    def test_no_duplicate_adjacency_entries(self):
        mapper = GuardInteractionTopologyMapper()
        mapper.record_interaction("A", "B")
        mapper.record_interaction("A", "B")
        assert len(mapper.adjacency["A"]) == 1


class TestDetectCycles:
    def test_no_cycles(self):
        mapper = GuardInteractionTopologyMapper()
        mapper.record_interaction("A", "B")
        mapper.record_interaction("B", "C")
        result = mapper.detect_cycles()
        assert result["cycles_detected"] is False
        assert result["cycles"] == []

    def test_simple_cycle(self):
        mapper = GuardInteractionTopologyMapper()
        mapper.record_interaction("A", "B")
        mapper.record_interaction("B", "C")
        mapper.record_interaction("C", "A")
        result = mapper.detect_cycles()
        assert result["cycles_detected"] is True
        assert len(result["cycles"]) >= 1

    def test_self_loop_not_counted(self):
        mapper = GuardInteractionTopologyMapper()
        mapper.record_interaction("A", "A")
        result = mapper.detect_cycles()
        assert result["cycles_detected"] is False

    def test_empty_graph(self):
        mapper = GuardInteractionTopologyMapper()
        result = mapper.detect_cycles()
        assert result["cycles_detected"] is False
        assert result["total_nodes"] == 0
        assert result["total_edges"] == 0

    def test_result_has_required_keys(self):
        mapper = GuardInteractionTopologyMapper()
        result = mapper.detect_cycles()
        assert "cycles_detected" in result
        assert "cycles" in result
        assert "total_nodes" in result
        assert "total_edges" in result

    def test_cycle_max_depth_respected(self):
        mapper = GuardInteractionTopologyMapper(cycle_max_depth=3)
        mapper.record_interaction("A", "B")
        mapper.record_interaction("B", "C")
        mapper.record_interaction("C", "D")
        mapper.record_interaction("D", "A")
        result = mapper.detect_cycles()
        assert result["cycles_detected"] is False


class TestGetMostInteractiveGuards:
    def test_empty_graph(self):
        mapper = GuardInteractionTopologyMapper()
        result = mapper.get_most_interactive_guards()
        assert result == []

    def test_single_interaction(self):
        mapper = GuardInteractionTopologyMapper()
        mapper.record_interaction("A", "B")
        result = mapper.get_most_interactive_guards()
        assert len(result) == 2
        guard_ids = [g["guard_id"] for g in result]
        assert "A" in guard_ids
        assert "B" in guard_ids

    def test_respects_n_parameter(self):
        mapper = GuardInteractionTopologyMapper()
        mapper.record_interaction("A", "B")
        mapper.record_interaction("B", "C")
        mapper.record_interaction("C", "D")
        result = mapper.get_most_interactive_guards(n=2)
        assert len(result) == 2

    def test_sorted_by_interaction_count(self):
        mapper = GuardInteractionTopologyMapper()
        for _ in range(5):
            mapper.record_interaction("A", "B")
        mapper.record_interaction("C", "D")
        result = mapper.get_most_interactive_guards()
        assert result[0]["guard_id"] == "A"
        assert result[0]["interactions"] == 5

    def test_result_structure(self):
        mapper = GuardInteractionTopologyMapper()
        mapper.record_interaction("A", "B")
        result = mapper.get_most_interactive_guards(n=1)
        assert "guard_id" in result[0]
        assert "interactions" in result[0]


class TestGetInteractionDensity:
    def test_empty_graph(self):
        mapper = GuardInteractionTopologyMapper()
        assert mapper.get_interaction_density() == 0.0

    def test_single_node(self):
        mapper = GuardInteractionTopologyMapper()
        mapper.adjacency["A"] = []
        assert mapper.get_interaction_density() == 0.0

    def test_two_nodes_one_edge(self):
        mapper = GuardInteractionTopologyMapper()
        mapper.record_interaction("A", "B")
        density = mapper.get_interaction_density()
        assert density == 0.5

    def test_full_graph(self):
        mapper = GuardInteractionTopologyMapper()
        mapper.record_interaction("A", "B")
        mapper.record_interaction("B", "A")
        density = mapper.get_interaction_density()
        assert density == 1.0

    def test_density_between_zero_and_one(self):
        mapper = GuardInteractionTopologyMapper()
        mapper.record_interaction("A", "B")
        mapper.record_interaction("B", "C")
        density = mapper.get_interaction_density()
        assert 0.0 <= density <= 1.0
