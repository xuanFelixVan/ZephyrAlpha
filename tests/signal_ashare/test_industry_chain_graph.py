# [BLUEPRINT] MOD-SIG-125 | docs/03_modules/_domain_signal/industry_chain_graph/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-125 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_industry_chain_graph
# [TESTS] src/zephyr/signal_ashare/industry_chain_graph.py
"""MOD-SIG-125 单元测试：industry_chain_graph 产业链知识图谱。

蓝图验收（B10-02202/CAND-TESTB-053，A1 D-ALT-DATA-29）：
节点/边 SQLite 表（连接全注入）+ 增删查 + 上游/下游 N 跳 BFS 传导路径
（路径强度=decay^跳数×边权连乘）+ 词表闭合/边权/自环/悬空 Fail-Closed +
输出确定性排序。连接为 :memory: 内存库，不触网/不落盘。
"""

from __future__ import annotations

import sqlite3

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.industry_chain_graph",
    reason="industry_chain_graph not importable",
)

from zephyr.signal_ashare.industry_chain_graph import (  # noqa: E402
    ChainEdge,
    ChainNode,
    EdgeKind,
    IndustryChainError,
    IndustryChainGraph,
    NodeKind,
)


def _graph(decay: float = 1.0) -> IndustryChainGraph:
    return IndustryChainGraph(conn=sqlite3.connect(":memory:"), decay=decay)


def _node(node_id: str, kind: NodeKind = NodeKind.COMPANY) -> ChainNode:
    return ChainNode(node_id=node_id, name=f"名称-{node_id}", kind=kind, meta="")


def _edge(src: str, dst: str, weight: float = 0.5, kind: EdgeKind = EdgeKind.SUPPLY) -> ChainEdge:
    return ChainEdge(src=src, dst=dst, edge_kind=kind, weight=weight, source="测试源")


def _chain_ab_bc(g: IndustryChainGraph) -> None:
    """A -> B -> C 两跳链（A 为最上游）。"""
    for nid in ("A", "B", "C"):
        g.add_node(_node(nid))
    g.add_edge(_edge("A", "B", 0.8))
    g.add_edge(_edge("B", "C", 0.5))


# ──────────────────────────────────────────────────────────────────────────────
# 构造护栏
# ──────────────────────────────────────────────────────────────────────────────


def test_init_guards():
    with pytest.raises(IndustryChainError, match="sqlite3"):
        IndustryChainGraph(conn=None)  # type: ignore[arg-type]
    for bad_decay in (0.0, -0.5, 1.5):
        with pytest.raises(IndustryChainError, match="decay"):
            IndustryChainGraph(conn=sqlite3.connect(":memory:"), decay=bad_decay)


# ──────────────────────────────────────────────────────────────────────────────
# 节点增删查
# ──────────────────────────────────────────────────────────────────────────────


def test_add_and_get_node():
    g = _graph()
    g.add_node(_node("X", NodeKind.SEGMENT))
    node = g.get_node("X")
    assert node.node_id == "X" and node.kind is NodeKind.SEGMENT


def test_add_node_empty_id_or_name():
    g = _graph()
    with pytest.raises(IndustryChainError, match="node_id 为空"):
        g.add_node(ChainNode(node_id="", name="n", kind=NodeKind.COMPANY))
    with pytest.raises(IndustryChainError, match="name 为空"):
        g.add_node(ChainNode(node_id="X", name="", kind=NodeKind.COMPANY))


def test_add_node_bad_kind():
    g = _graph()
    with pytest.raises(IndustryChainError, match="非法节点类型"):
        g.add_node(ChainNode(node_id="X", name="n", kind="company"))  # type: ignore[arg-type]


def test_add_node_duplicate():
    g = _graph()
    g.add_node(_node("X"))
    with pytest.raises(IndustryChainError, match="节点重复"):
        g.add_node(_node("X"))


def test_list_nodes_sorted():
    g = _graph()
    for nid in ("C", "A", "B"):
        g.add_node(_node(nid))
    assert [n.node_id for n in g.list_nodes()] == ["A", "B", "C"]


def test_unknown_node_guards():
    g = _graph()
    with pytest.raises(IndustryChainError, match="未知节点"):
        g.get_node("ghost")
    with pytest.raises(IndustryChainError, match="未知节点"):
        g.remove_node("ghost")


def test_remove_node_cascades_edges():
    g = _graph()
    _chain_ab_bc(g)
    g.remove_node("B")
    assert g.list_edges() == ()
    with pytest.raises(IndustryChainError, match="未知节点"):
        g.get_node("B")


# ──────────────────────────────────────────────────────────────────────────────
# 边增删查
# ──────────────────────────────────────────────────────────────────────────────


def test_add_and_list_edges_sorted():
    g = _graph()
    for nid in ("A", "B", "C"):
        g.add_node(_node(nid))
    g.add_edge(_edge("B", "C", 0.5, EdgeKind.DEMAND))
    g.add_edge(_edge("A", "C", 0.4, EdgeKind.MATERIAL))
    g.add_edge(_edge("A", "B", 0.8))
    edges = g.list_edges()
    assert [(e.src, e.dst, e.edge_kind) for e in edges] == [
        ("A", "B", EdgeKind.SUPPLY),
        ("A", "C", EdgeKind.MATERIAL),
        ("B", "C", EdgeKind.DEMAND),
    ]
    assert edges[0].weight == 0.8 and edges[0].source == "测试源"


def test_add_edge_dangling_endpoint():
    g = _graph()
    g.add_node(_node("A"))
    with pytest.raises(IndustryChainError, match="未知节点"):
        g.add_edge(_edge("A", "ghost"))


def test_add_edge_self_loop():
    g = _graph()
    g.add_node(_node("A"))
    with pytest.raises(IndustryChainError, match="自环"):
        g.add_edge(_edge("A", "A"))


def test_add_edge_weight_out_of_range():
    g = _graph()
    g.add_node(_node("A"))
    g.add_node(_node("B"))
    for bad_weight in (0.0, -0.1, 1.01):
        with pytest.raises(IndustryChainError, match="边权"):
            g.add_edge(_edge("A", "B", bad_weight))


def test_add_edge_bad_kind():
    g = _graph()
    g.add_node(_node("A"))
    g.add_node(_node("B"))
    with pytest.raises(IndustryChainError, match="非法边类型"):
        g.add_edge(ChainEdge(src="A", dst="B", edge_kind="supply", weight=0.5))  # type: ignore[arg-type]


def test_add_edge_duplicate():
    g = _graph()
    g.add_node(_node("A"))
    g.add_node(_node("B"))
    g.add_edge(_edge("A", "B"))
    with pytest.raises(IndustryChainError, match="边重复"):
        g.add_edge(_edge("A", "B", 0.3))


def test_remove_edge_and_unknown():
    g = _graph()
    _chain_ab_bc(g)
    g.remove_edge("A", "B", EdgeKind.SUPPLY)
    assert [(e.src, e.dst) for e in g.list_edges()] == [("B", "C")]
    with pytest.raises(IndustryChainError, match="未知边"):
        g.remove_edge("A", "B", EdgeKind.SUPPLY)


def test_list_edges_filtered_by_node():
    g = _graph()
    _chain_ab_bc(g)
    edges = g.list_edges("B")
    assert {(e.src, e.dst) for e in edges} == {("A", "B"), ("B", "C")}


# ──────────────────────────────────────────────────────────────────────────────
# 传导路径查询（上/下游 BFS + 乘积衰减）
# ──────────────────────────────────────────────────────────────────────────────


def test_upstream_paths_single_hop():
    g = _graph()
    _chain_ab_bc(g)
    paths = g.upstream_paths("B", 1)
    assert len(paths) == 1
    assert paths[0].steps == ("B", "A")
    assert paths[0].hops == 1
    assert paths[0].strength == pytest.approx(0.8)


def test_upstream_paths_multi_hop_product_decay_and_max_hops():
    g = _graph(decay=0.5)
    _chain_ab_bc(g)
    by_steps = {p.steps: p for p in g.upstream_paths("C", 2)}
    # 1跳：0.5×decay；2跳：0.5×0.8×decay²
    assert by_steps[("C", "B")].strength == pytest.approx(0.5 * 0.5)
    assert by_steps[("C", "B", "A")].strength == pytest.approx(0.5 * 0.8 * 0.25)
    assert by_steps[("C", "B", "A")].hops == 2
    assert all(p.hops <= 1 for p in g.upstream_paths("C", 1))


def test_downstream_paths():
    g = _graph()
    _chain_ab_bc(g)
    by_steps = {p.steps: p for p in g.downstream_paths("A", 2)}
    assert by_steps[("A", "B")].strength == pytest.approx(0.8)
    assert by_steps[("A", "B", "C")].strength == pytest.approx(0.8 * 0.5)


def test_paths_sorted_by_strength_desc():
    g = _graph()
    for nid in ("S", "A", "B", "C"):
        g.add_node(_node(nid))
    g.add_edge(_edge("A", "S", 0.9))
    g.add_edge(_edge("B", "S", 0.7))
    g.add_edge(_edge("C", "S", 0.8))
    paths = g.upstream_paths("S", 1)
    assert [p.steps[1] for p in paths] == ["A", "C", "B"]  # 强度降序


def test_paths_no_cycle_infinite():
    g = _graph()
    for nid in ("A", "B"):
        g.add_node(_node(nid))
    g.add_edge(_edge("A", "B", 0.9))
    g.add_edge(_edge("B", "A", 0.9))
    paths = g.downstream_paths("A", 5)
    assert [p.steps for p in paths] == [("A", "B")]  # 简单路径防环


def test_paths_guards():
    g = _graph()
    g.add_node(_node("A"))
    with pytest.raises(IndustryChainError, match="未知节点"):
        g.upstream_paths("ghost", 2)
    for bad_hops in (0, -1, 1.5, "2"):
        with pytest.raises(IndustryChainError, match="max_hops"):
            g.downstream_paths("A", bad_hops)  # type: ignore[arg-type]


def test_determinism_same_input_same_output():
    def _build() -> tuple:
        g = _graph(decay=0.7)
        for nid in ("S", "A", "B", "C", "D"):
            g.add_node(_node(nid))
        g.add_edge(_edge("A", "S", 0.9))
        g.add_edge(_edge("B", "S", 0.6))
        g.add_edge(_edge("C", "A", 0.8))
        g.add_edge(_edge("D", "B", 0.5))
        return g.upstream_paths("S", 2)

    assert _build() == _build()
