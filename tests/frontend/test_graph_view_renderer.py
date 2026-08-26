# [BLUEPRINT] MOD-FE-005 | docs/03_modules/_domain_frontend/graph_view_renderer/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FE-005 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.frontend.test_graph_view_renderer
# [TESTS] src/zephyr/frontend/graph_view_renderer.py
"""MOD-FE-005 单元测试：graph_view_renderer 依赖图DAG渲染数据器。

蓝图验收（B10-02408/CAND-FE-006，A1 M5-S07）：
分层布局坐标（最长路径层分配 + barycenter 层内降交叉）+ 状态着色映射 +
钻取 N 跳邻居诱导子图 payload。节点/边快照全内存构造（DI 注入），不触库。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.frontend.graph_view_renderer",
    reason="graph_view_renderer not importable",
)

from zephyr.frontend.graph_view_renderer import (  # noqa: E402
    DepEdge,
    DepNode,
    GraphViewError,
    GraphViewRenderer,
    NodeStatus,
)


def _node(node_id: str, status: NodeStatus = NodeStatus.HEALTHY) -> DepNode:
    return DepNode(node_id=node_id, label=f"节点{node_id}", status=status)


def _renderer(
    nodes: list[DepNode] | None = None,
    edges: list[DepEdge] | None = None,
    **kwargs,
) -> GraphViewRenderer:
    if nodes is None:
        nodes = [_node("a"), _node("b"), _node("c")]
    if edges is None:
        edges = [DepEdge("a", "b"), DepEdge("b", "c")]
    return GraphViewRenderer(nodes=nodes, edges=edges, **kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 构造校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_ok(self) -> None:
        renderer = _renderer()
        assert renderer.color_map() == {"a": "green", "b": "green", "c": "green"}

    def test_empty_nodes_raises(self) -> None:
        with pytest.raises(GraphViewError):
            GraphViewRenderer(nodes=[], edges=[])

    def test_blank_node_id_raises(self) -> None:
        with pytest.raises(GraphViewError):
            GraphViewRenderer(nodes=[_node("")], edges=[])

    def test_duplicate_node_id_raises(self) -> None:
        with pytest.raises(GraphViewError):
            GraphViewRenderer(nodes=[_node("a"), _node("a")], edges=[])

    def test_invalid_status_raises(self) -> None:
        bad = DepNode(node_id="a", label="x", status="healthy")  # type: ignore[arg-type]
        with pytest.raises(GraphViewError):
            GraphViewRenderer(nodes=[bad], edges=[])

    def test_edge_unknown_endpoint_raises(self) -> None:
        with pytest.raises(GraphViewError):
            GraphViewRenderer(nodes=[_node("a")], edges=[DepEdge("a", "ghost")])
        with pytest.raises(GraphViewError):
            GraphViewRenderer(nodes=[_node("a")], edges=[DepEdge("ghost", "a")])

    def test_self_loop_raises(self) -> None:
        with pytest.raises(GraphViewError):
            GraphViewRenderer(nodes=[_node("a")], edges=[DepEdge("a", "a")])

    def test_cycle_raises(self) -> None:
        nodes = [_node("a"), _node("b"), _node("c")]
        edges = [DepEdge("a", "b"), DepEdge("b", "c"), DepEdge("c", "a")]
        with pytest.raises(GraphViewError):
            GraphViewRenderer(nodes=nodes, edges=edges)

    def test_duplicate_edge_idempotent(self) -> None:
        renderer = _renderer(edges=[DepEdge("a", "b"), DepEdge("a", "b"), DepEdge("b", "c")])
        assert len(renderer.layout().edges) == 2

    def test_non_positive_spacing_raises(self) -> None:
        with pytest.raises(GraphViewError):
            _renderer(x_spacing=0)
        with pytest.raises(GraphViewError):
            _renderer(y_spacing=-1.0)


# ──────────────────────────────────────────────────────────────────────────────
# 分层布局
# ──────────────────────────────────────────────────────────────────────────────


class TestLayout:
    def test_chain_layers(self) -> None:
        layout = _renderer().layout()
        layers = {n.node_id: n.layer for n in layout.nodes}
        assert layers == {"a": 0, "b": 1, "c": 2}
        assert layout.layer_count == 3

    def test_diamond_longest_path(self) -> None:
        edges = [DepEdge("a", "b"), DepEdge("a", "c"), DepEdge("b", "d"), DepEdge("c", "d")]
        layout = _renderer(nodes=[_node(n) for n in "abcd"], edges=edges).layout()
        layers = {n.node_id: n.layer for n in layout.nodes}
        assert layers["a"] == 0
        assert layers["d"] == 2
        assert layers["b"] == 1 and layers["c"] == 1

    def test_skip_edge_longest_path(self) -> None:
        # a→c 直达 + a→b→c：c 层=最长路径 2 而非 1
        edges = [DepEdge("a", "b"), DepEdge("b", "c"), DepEdge("a", "c")]
        layout = _renderer(edges=edges).layout()
        layers = {n.node_id: n.layer for n in layout.nodes}
        assert layers["c"] == 2

    def test_coordinates_from_spacing(self) -> None:
        layout = _renderer(x_spacing=100.0, y_spacing=50.0).layout()
        by_id = {n.node_id: n for n in layout.nodes}
        assert (by_id["a"].x, by_id["a"].y) == (0.0, 0.0)
        assert (by_id["b"].x, by_id["b"].y) == (0.0, 50.0)
        assert (by_id["c"].x, by_id["c"].y) == (0.0, 100.0)

    def test_nodes_sorted_by_layer_order(self) -> None:
        edges = [DepEdge("a", "c"), DepEdge("b", "c")]
        layout = _renderer(nodes=[_node(n) for n in "abc"], edges=edges).layout()
        keys = [(n.layer, n.order) for n in layout.nodes]
        assert keys == sorted(keys)

    def test_barycenter_reduces_crossing(self) -> None:
        # 层0: a(0),b(1)；边 a→y, b→x。字典序层1=[x,y] 必交叉，
        # barycenter(x)=1, barycenter(y)=0 → 重排为 [y,x] 无交叉
        nodes = [_node(n) for n in ("a", "b", "x", "y")]
        edges = [DepEdge("a", "y"), DepEdge("b", "x")]
        layout = GraphViewRenderer(nodes=nodes, edges=edges).layout()
        layer1 = [n.node_id for n in layout.nodes if n.layer == 1]
        assert layer1 == ["y", "x"]

    def test_deterministic(self) -> None:
        edges = [DepEdge("a", "b"), DepEdge("a", "c"), DepEdge("b", "d"), DepEdge("c", "d")]
        nodes = [_node(n) for n in "abcd"]
        r1 = GraphViewRenderer(nodes=nodes, edges=edges)
        r2 = GraphViewRenderer(nodes=list(reversed(nodes)), edges=edges)
        assert r1.layout() == r2.layout() == r1.layout()


# ──────────────────────────────────────────────────────────────────────────────
# 状态着色
# ──────────────────────────────────────────────────────────────────────────────


class TestColorMap:
    def test_status_color_mapping(self) -> None:
        nodes = [
            _node("h", NodeStatus.HEALTHY),
            _node("d", NodeStatus.DEGRADED),
            _node("f", NodeStatus.FAILED),
            _node("u", NodeStatus.UNKNOWN),
        ]
        renderer = GraphViewRenderer(nodes=nodes, edges=[])
        assert renderer.color_map() == {"h": "green", "d": "amber", "f": "red", "u": "gray"}

    def test_layout_node_carries_color(self) -> None:
        nodes = [_node("a", NodeStatus.FAILED), _node("b")]
        layout = GraphViewRenderer(nodes=nodes, edges=[DepEdge("a", "b")]).layout()
        by_id = {n.node_id: n for n in layout.nodes}
        assert by_id["a"].color == "red"
        assert by_id["b"].color == "green"


# ──────────────────────────────────────────────────────────────────────────────
# 钻取邻居子图
# ──────────────────────────────────────────────────────────────────────────────


class TestDrilldown:
    def _diamond(self) -> GraphViewRenderer:
        nodes = [_node(n) for n in "abcde"]
        edges = [DepEdge("a", "b"), DepEdge("b", "c"), DepEdge("c", "d"), DepEdge("b", "e")]
        return GraphViewRenderer(nodes=nodes, edges=edges)

    def test_hops1_both_directions(self) -> None:
        payload = self._diamond().drilldown("b", hops=1)
        assert payload.center == "b"
        assert tuple(n.node_id for n in payload.nodes) == ("a", "b", "c", "e")

    def test_hops2_reaches_grand_neighbors(self) -> None:
        payload = self._diamond().drilldown("b", hops=2)
        assert tuple(n.node_id for n in payload.nodes) == ("a", "b", "c", "d", "e")

    def test_induced_edges_only(self) -> None:
        payload = self._diamond().drilldown("b", hops=1)
        pairs = [(e.source, e.target) for e in payload.edges]
        assert pairs == [("a", "b"), ("b", "c"), ("b", "e")]  # c→d 不在诱导子图

    def test_unknown_node_raises(self) -> None:
        with pytest.raises(GraphViewError):
            self._diamond().drilldown("ghost")

    def test_invalid_hops_raises(self) -> None:
        renderer = self._diamond()
        with pytest.raises(GraphViewError):
            renderer.drilldown("b", hops=0)
        with pytest.raises(GraphViewError):
            renderer.drilldown("b", hops=-1)
