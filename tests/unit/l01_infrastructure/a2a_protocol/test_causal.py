# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_causal
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: CausalTrace"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_causal_trace import (
    A2ACausalTrace,
    CausalGraph,
)


def test_trace_path_nonexistent():
    ct = A2ACausalTrace()
    assert ct.trace_path("nonexistent") == []


def test_open_trace_and_add_nodes():
    ct = A2ACausalTrace()
    ct.open_trace("trace-1")
    ct.add_node("trace-1", "n1", "agent-a", "write", "file.py", 1000.0)
    ct.add_node("trace-1", "n2", "agent-b", "read", "file.py", 1001.0)
    ct.add_dependency("trace-1", "n1", "n2", "read_after_write")
    path = ct.trace_path("trace-1")
    assert len(path) == 1
    assert "n1" in path[0] and "n2" in path[0]


def test_get_graph():
    ct = A2ACausalTrace()
    ct.open_trace("trace-2")
    graph = ct.get_graph("trace-2")
    assert isinstance(graph, CausalGraph)
    assert len(graph.nodes) == 0


def test_get_graph_nonexistent():
    ct = A2ACausalTrace()
    assert ct.get_graph("nonexistent") is None


def test_causal_graph_trace_path():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_causal_trace import CausalNode
    g = CausalGraph()
    g.add_node(CausalNode("n1", "a1", "write", "f.py", 0.0))
    g.add_node(CausalNode("n2", "a2", "read", "f.py", 1.0))
    g.add_edge("n1", "n2", "read_after_write")
    g.add_edge("n2", "n1", "feedback")
    assert len(g.trace_path) == 2
