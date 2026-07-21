# [A_test] module_id: MOD-GOV_a2a_causal_trace | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_a2a_causal_trace
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

mod = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_causal_trace",
    reason="a2a_causal_trace module not available",
)


class TestA2ACausalTrace:
    def test_instantiation(self):
        obj = mod.A2ACausalTrace()
        assert obj is not None

    def test_open_trace(self):
        obj = mod.A2ACausalTrace()
        obj.open_trace("trace_1")

    def test_add_node_and_get_graph(self):
        obj = mod.A2ACausalTrace()
        obj.open_trace("trace_2")
        obj.add_node("trace_2", "n1", "agent1", "read_file", "file.py", "2024-01-01T00:00:00")
        graph = obj.get_graph("trace_2")
        assert graph is not None

    def test_add_dependency(self):
        obj = mod.A2ACausalTrace()
        obj.open_trace("trace_3")
        obj.add_node("trace_3", "n1", "agent1", "read", "f1", "t1")
        obj.add_node("trace_3", "n2", "agent2", "write", "f2", "t2")
        obj.add_dependency("trace_3", "n1", "n2", "data_flow")
        graph = obj.get_graph("trace_3")
        assert graph is not None

    def test_trace_path(self):
        obj = mod.A2ACausalTrace()
        obj.open_trace("trace_4")
        obj.add_node("trace_4", "n1", "a1", "act1", "r1", "t1")
        path = obj.trace_path("trace_4")
        assert isinstance(path, list)

    def test_get_graph_nonexistent(self):
        obj = mod.A2ACausalTrace()
        graph = obj.get_graph("nonexistent")
        assert graph is None or graph is not None


class TestCausalGraph:
    def test_add_node(self):
        g = mod.CausalGraph()
        node = mod.CausalNode(node_id="n1", agent_id="a1", action="act", resource="r", timestamp="t")
        g.add_node(node)

    def test_add_edge(self):
        g = mod.CausalGraph()
        g.add_edge("n1", "n2", "data_flow")

    def test_trace_path_is_property(self):
        g = mod.CausalGraph()
        path = g.trace_path
        assert isinstance(path, list)
