# [A_test] module_id: MOD-GOV_dependency_graph | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-377 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_dependency_graph
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_dependency_graph.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.shared.dependency.dependency_graph import (
    CycleDetection,
    DependencyGraph,
    DependencyNode,
    KillChain,
)


class TestDependencyNode:
    def test_default_values(self):
        node = DependencyNode(task_id="T-001")
        assert node.task_id == "T-001"
        assert node.depends_on == []
        assert node.blocked_by == []
        assert node.all_dependencies == []

    def test_with_dependencies(self):
        node = DependencyNode(task_id="T-001", depends_on=["T-002"], blocked_by=["T-003"])
        assert node.depends_on == ["T-002"]
        assert node.blocked_by == ["T-003"]


class TestCycleDetection:
    def test_no_cycle(self):
        cd = CycleDetection(has_cycle=False, cycle_path=[], message="no cycle")
        assert cd.has_cycle is False
        assert cd.cycle_path == []

    def test_with_cycle(self):
        cd = CycleDetection(has_cycle=True, cycle_path=["A", "B", "A"], message="cycle found")
        assert cd.has_cycle is True
        assert len(cd.cycle_path) == 3


class TestKillChain:
    def test_creation(self):
        kc = KillChain(
            task_id="T-001", chain_depth=2, chain_path=["T-001", "T-002", "T-003"], direct_deps=1, transitive_deps=2
        )
        assert kc.task_id == "T-001"
        assert kc.chain_depth == 2
        assert kc.direct_deps == 1
        assert kc.transitive_deps == 2


class TestDependencyGraph:
    def test_instantiation(self):
        graph = DependencyGraph()
        assert graph.nodes == {}

    def test_add_node(self):
        graph = DependencyGraph()
        node = graph.add_node("T-001")
        assert node.task_id == "T-001"
        assert node.depends_on == []
        assert node.blocked_by == []

    def test_add_node_with_dependencies(self):
        graph = DependencyGraph()
        graph.add_node("T-002")
        graph.add_node("T-003")
        node = graph.add_node("T-001", depends_on=["T-002"], blocked_by=["T-003"])
        assert node.depends_on == ["T-002"]
        assert node.blocked_by == ["T-003"]

    def test_add_node_idempotent(self):
        graph = DependencyGraph()
        graph.add_node("T-001")
        node = graph.add_node("T-001", depends_on=["T-002"])
        assert node.task_id == "T-001"
        assert node.depends_on == ["T-002"]

    def test_add_node_resolves_transitive_deps(self):
        graph = DependencyGraph()
        graph.add_node("T-003")
        graph.add_node("T-002", depends_on=["T-003"])
        node = graph.add_node("T-001", depends_on=["T-002"])
        assert "T-002" in node.all_dependencies
        assert "T-003" in node.all_dependencies

    def test_detect_cycles_no_cycle(self):
        graph = DependencyGraph()
        graph.add_node("T-002")
        graph.add_node("T-001", depends_on=["T-002"])
        cycles = graph.detect_cycles()
        assert len(cycles) == 0

    def test_detect_cycles_with_cycle(self):
        graph = DependencyGraph()
        graph.add_node("T-001", depends_on=["T-002"])
        graph.add_node("T-002", depends_on=["T-001"])
        cycles = graph.detect_cycles()
        assert len(cycles) > 0
        assert cycles[0].has_cycle is True
        assert len(cycles[0].cycle_path) > 0

    def test_detect_cycles_self_dependency(self):
        graph = DependencyGraph()
        graph.add_node("T-001", depends_on=["T-001"])
        cycles = graph.detect_cycles()
        assert len(cycles) > 0
        assert cycles[0].has_cycle is True

    def test_detect_cycles_empty_graph(self):
        graph = DependencyGraph()
        cycles = graph.detect_cycles()
        assert cycles == []

    def test_build_kill_chain(self):
        graph = DependencyGraph()
        graph.add_node("T-003")
        graph.add_node("T-002", depends_on=["T-003"])
        graph.add_node("T-001", depends_on=["T-002"])
        kc = graph.build_kill_chain("T-001")
        assert kc is not None
        assert kc.task_id == "T-001"
        assert kc.chain_depth == 2
        assert kc.direct_deps == 1
        assert kc.transitive_deps == 2

    def test_build_kill_chain_nonexistent(self):
        graph = DependencyGraph()
        result = graph.build_kill_chain("nonexistent")
        assert result is None

    def test_build_kill_chain_no_deps(self):
        graph = DependencyGraph()
        graph.add_node("T-001")
        kc = graph.build_kill_chain("T-001")
        assert kc is not None
        assert kc.chain_depth == 0
        assert kc.direct_deps == 0
        assert kc.transitive_deps == 0

    def test_validate_task_deps_valid(self):
        graph = DependencyGraph()
        task = {"task_id": "T-001", "depends_on": ["T-002"], "blocked_by": ["T-003"]}
        valid, msg = graph.validate_task_deps(task)
        assert valid is True
        assert "valid" in msg.lower()

    def test_validate_task_deps_self_dependency(self):
        graph = DependencyGraph()
        task = {"task_id": "T-001", "depends_on": ["T-001"], "blocked_by": []}
        valid, msg = graph.validate_task_deps(task)
        assert valid is False
        assert "Self-dependency" in msg

    def test_validate_task_deps_conflicting_dependency(self):
        graph = DependencyGraph()
        task = {"task_id": "T-001", "depends_on": ["T-002"], "blocked_by": ["T-002"]}
        valid, msg = graph.validate_task_deps(task)
        assert valid is False
        assert "Conflicting" in msg

    def test_validate_task_deps_invalid_type(self):
        graph = DependencyGraph()
        task = {"task_id": "T-001", "depends_on": "not-a-list", "blocked_by": []}
        valid, msg = graph.validate_task_deps(task)
        assert valid is False
        assert "must be lists" in msg

    def test_validate_task_deps_empty(self):
        graph = DependencyGraph()
        task = {"task_id": "T-001"}
        valid, msg = graph.validate_task_deps(task)
        assert valid is True

    def test_validate_task_deps_none_values(self):
        graph = DependencyGraph()
        task = {"task_id": "T-001", "depends_on": None, "blocked_by": None}
        valid, msg = graph.validate_task_deps(task)
        assert valid is False
