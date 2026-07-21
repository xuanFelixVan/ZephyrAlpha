# [A_test] module_id: MOD-GOV_dependency_tracker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_dependency_tracker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_dependency_tracker.py -q
# [TTL] task_bound
from __future__ import annotations

from zephyr.shared.dependency.dependency_tracker import (
    DependencyGraph,
    DependencyTracker,
)


class TestDependencyGraph:
    def test_default_circular_deps(self):
        graph = DependencyGraph(nodes=["A", "B"], edges=[("A", "B")])
        assert graph.circular_deps == []

    def test_custom_circular_deps(self):
        graph = DependencyGraph(
            nodes=["A", "B"],
            edges=[("A", "B"), ("B", "A")],
            circular_deps=[("A", "B")],
        )
        assert graph.circular_deps == [("A", "B")]

    def test_empty_graph(self):
        graph = DependencyGraph(nodes=[], edges=[])
        assert graph.nodes == []
        assert graph.edges == []


class TestDependencyTrackerInit:
    def test_instantiation(self):
        tracker = DependencyTracker()
        assert hasattr(tracker, "build_graph")


class TestDependencyTrackerBuildGraph:
    def test_build_graph_basic(self):
        tracker = DependencyTracker()
        tasks = [
            {"id": "TASK-001", "depends_on": ["TASK-002"]},
            {"id": "TASK-002", "depends_on": []},
        ]
        graph = tracker.build_graph(tasks)
        assert isinstance(graph, DependencyGraph)
        assert "TASK-001" in graph.nodes
        assert "TASK-002" in graph.nodes

    def test_build_graph_edges(self):
        tracker = DependencyTracker()
        tasks = [
            {"id": "TASK-010", "depends_on": ["TASK-011"]},
            {"id": "TASK-011", "depends_on": []},
        ]
        graph = tracker.build_graph(tasks)
        assert ("TASK-010", "TASK-011") in graph.edges

    def test_build_graph_no_dependencies(self):
        tracker = DependencyTracker()
        tasks = [
            {"id": "TASK-020", "depends_on": []},
        ]
        graph = tracker.build_graph(tasks)
        assert graph.edges == []

    def test_build_graph_multiple_dependencies(self):
        tracker = DependencyTracker()
        tasks = [
            {"id": "TASK-030", "depends_on": ["TASK-031", "TASK-032"]},
            {"id": "TASK-031", "depends_on": []},
            {"id": "TASK-032", "depends_on": []},
        ]
        graph = tracker.build_graph(tasks)
        assert len(graph.edges) == 2
        assert ("TASK-030", "TASK-031") in graph.edges
        assert ("TASK-030", "TASK-032") in graph.edges

    def test_build_graph_empty_tasks(self):
        tracker = DependencyTracker()
        graph = tracker.build_graph([])
        assert graph.nodes == []
        assert graph.edges == []

    def test_build_graph_missing_id_uses_index(self):
        tracker = DependencyTracker()
        tasks = [
            {"depends_on": []},
        ]
        graph = tracker.build_graph(tasks)
        assert "TASK-0" in graph.nodes

    def test_build_graph_missing_depends_on(self):
        tracker = DependencyTracker()
        tasks = [
            {"id": "TASK-040"},
        ]
        graph = tracker.build_graph(tasks)
        assert "TASK-040" in graph.nodes
        assert graph.edges == []

    def test_build_graph_empty_dep_string_filtered(self):
        tracker = DependencyTracker()
        tasks = [
            {"id": "TASK-050", "depends_on": [""]},
        ]
        graph = tracker.build_graph(tasks)
        assert graph.edges == []

    def test_build_graph_circular_deps_default_empty(self):
        tracker = DependencyTracker()
        tasks = [
            {"id": "TASK-060", "depends_on": ["TASK-061"]},
            {"id": "TASK-061", "depends_on": ["TASK-060"]},
        ]
        graph = tracker.build_graph(tasks)
        assert graph.circular_deps == []
