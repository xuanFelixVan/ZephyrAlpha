# [BLUEPRINT] MOD-SIG-126 | docs/03_modules/_domain_signal/stock_relation_gnn/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-126 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_stock_relation_gnn
# [TESTS] src/zephyr/signal_ashare/stock_relation_gnn.py
"""MOD-SIG-126 单元测试：stock_relation_gnn 股票关系 GNN 基类。

蓝图验收（B10-01830/CAND-TESTB-049，A1 §29.6，承接 TESTB-034/046 归并）：
3 种邻接图词表闭合（供应链/同行业/概念共现）+ GAT/GCN 两路聚合
（注意力 softmax / 度归一化加权均值，纯内存列表实现）+ 聚合特征接密度
预测注入回调（未注入 Fail-Closed）+ 图规模护栏 + 聚合确定性。
predictor 全注入内存替身，不触网。
"""

from __future__ import annotations

import math

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.stock_relation_gnn",
    reason="stock_relation_gnn not importable",
)

from zephyr.signal_ashare.stock_relation_gnn import (  # noqa: E402
    AggregateMode,
    RelationEdge,
    RelationKind,
    StockRelationGNN,
    StockRelationGnnError,
)


def _gnn(**kwargs) -> StockRelationGNN:
    kwargs.setdefault("predictor", lambda sid, feats: math.fsum(feats))
    return StockRelationGNN(**kwargs)


def _edge(
    src: str,
    dst: str,
    weight: float = 1.0,
    kind: RelationKind = RelationKind.SUPPLY_CHAIN,
) -> RelationEdge:
    return RelationEdge(kind=kind, src=src, dst=dst, weight=weight)


def _abc_graph(g: StockRelationGNN) -> None:
    """A-B(w=1.0)、B-C(w=0.5) 供应链图；特征 dim=2。"""
    g.add_node("A", [1.0, 0.0])
    g.add_node("B", [0.0, 1.0])
    g.add_node("C", [1.0, 1.0])
    g.add_edge(_edge("A", "B", 1.0))
    g.add_edge(_edge("B", "C", 0.5))


# ──────────────────────────────────────────────────────────────────────────────
# 构造与节点护栏
# ──────────────────────────────────────────────────────────────────────────────


def test_init_guards():
    with pytest.raises(StockRelationGnnError, match="max_nodes"):
        StockRelationGNN(max_nodes=0)
    with pytest.raises(StockRelationGnnError, match="max_nodes"):
        StockRelationGNN(max_nodes="10")  # type: ignore[arg-type]
    with pytest.raises(StockRelationGnnError, match="max_edges"):
        StockRelationGNN(max_edges=-1)


def test_add_node_ok():
    g = _gnn()
    g.add_node("A", [1.0, 2.0])
    assert g.node_count == 1
    assert g.feature_dim == 2
    assert g.node_features("A") == (1.0, 2.0)


def test_add_node_empty_id_or_features():
    g = _gnn()
    with pytest.raises(StockRelationGnnError, match="stock_id 为空"):
        g.add_node("", [1.0])
    with pytest.raises(StockRelationGnnError, match="特征为空"):
        g.add_node("A", [])


def test_add_node_non_finite():
    g = _gnn()
    with pytest.raises(StockRelationGnnError, match="非有限"):
        g.add_node("A", [float("nan")])
    with pytest.raises(StockRelationGnnError, match="非有限"):
        g.add_node("B", [float("inf")])


def test_add_node_duplicate_and_dim_mismatch():
    g = _gnn()
    g.add_node("A", [1.0, 2.0])
    with pytest.raises(StockRelationGnnError, match="节点重复"):
        g.add_node("A", [3.0, 4.0])
    with pytest.raises(StockRelationGnnError, match="维数不一致"):
        g.add_node("B", [1.0])


def test_max_nodes_guard():
    g = _gnn(max_nodes=2)
    g.add_node("A", [1.0])
    g.add_node("B", [2.0])
    with pytest.raises(StockRelationGnnError, match="护栏"):
        g.add_node("C", [3.0])


# ──────────────────────────────────────────────────────────────────────────────
# 关系边与邻接
# ──────────────────────────────────────────────────────────────────────────────


def test_add_edge_undirected_closure():
    g = _gnn()
    _abc_graph(g)
    adj = g.adjacency(RelationKind.SUPPLY_CHAIN)
    assert adj["A"] == (("B", 1.0),)
    assert adj["B"] == (("A", 1.0), ("C", 0.5))  # 无向闭合 + 按id排序
    assert adj["C"] == (("B", 0.5),)
    assert g.edge_count == 2


def test_add_edge_guards():
    g = _gnn()
    g.add_node("A", [1.0])
    g.add_node("B", [2.0])
    with pytest.raises(StockRelationGnnError, match="非法关系类型"):
        g.add_edge(RelationEdge(kind="supply", src="A", dst="B"))  # type: ignore[arg-type]
    with pytest.raises(StockRelationGnnError, match="未知节点"):
        g.add_edge(_edge("A", "ghost"))
    with pytest.raises(StockRelationGnnError, match="自环"):
        g.add_edge(_edge("A", "A"))
    for bad_weight in (0.0, -0.3, 1.2):
        with pytest.raises(StockRelationGnnError, match="边权"):
            g.add_edge(_edge("A", "B", bad_weight))


def test_add_edge_duplicate_and_reversed():
    g = _gnn()
    g.add_node("A", [1.0])
    g.add_node("B", [2.0])
    g.add_edge(_edge("A", "B", 0.5, RelationKind.SAME_INDUSTRY))
    with pytest.raises(StockRelationGnnError, match="边重复"):
        g.add_edge(_edge("A", "B", 0.8, RelationKind.SAME_INDUSTRY))
    with pytest.raises(StockRelationGnnError, match="边重复"):
        g.add_edge(_edge("B", "A", 0.8, RelationKind.SAME_INDUSTRY))  # 无向：反向亦重复
    # 同端点不同关系图合法
    g.add_edge(_edge("A", "B", 0.8, RelationKind.CONCEPT_COOCCUR))
    assert g.edge_count == 2


def test_max_edges_guard():
    g = _gnn(max_edges=1)
    for nid in ("A", "B", "C"):
        g.add_node(nid, [1.0])
    g.add_edge(_edge("A", "B"))
    with pytest.raises(StockRelationGnnError, match="护栏"):
        g.add_edge(_edge("B", "C"))


def test_query_guards():
    g = _gnn()
    g.add_node("A", [1.0])
    with pytest.raises(StockRelationGnnError, match="非法关系类型"):
        g.adjacency("supply_chain")  # type: ignore[arg-type]
    with pytest.raises(StockRelationGnnError, match="未知节点"):
        g.node_features("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# GCN / GAT 聚合（确定性数值）
# ──────────────────────────────────────────────────────────────────────────────


def test_aggregate_gcn_values_and_layout():
    g = _gnn()
    _abc_graph(g)
    out = g.aggregate_features(AggregateMode.GCN)
    # 布局：x_i ⊕ supply ⊕ industry ⊕ concept（dim=2 → 总长 8；空关系图=零向量）
    assert len(out["A"]) == 8
    # 供应链 GCN：A 仅邻居 B（权1）→ agg=x_B；B 邻居 A(1)/C(0.5) → 2/3·x_A+1/3·x_C
    assert out["A"][2:4] == pytest.approx((0.0, 1.0))
    assert out["B"][2:4] == pytest.approx((2 / 3 * 1 + 1 / 3 * 1, 2 / 3 * 0 + 1 / 3 * 1))
    assert out["C"][2:4] == pytest.approx((0.0, 1.0))
    assert out["A"][4:] == (0.0, 0.0, 0.0, 0.0)  # 同行业/概念共现空图零向量
    assert out["A"][:2] == (1.0, 0.0)  # 首段为自身特征


def test_aggregate_gat_uniform_when_identical_features():
    g = _gnn()
    for nid in ("A", "B", "C"):
        g.add_node(nid, [1.0, 2.0])
    g.add_edge(_edge("A", "B"))
    g.add_edge(_edge("B", "C"))
    out = g.aggregate_features(AggregateMode.GAT)
    # 特征全同 → 打分全同 → 注意力均匀 → 聚合=邻居均值=同特征
    assert out["B"][2:4] == pytest.approx((1.0, 2.0))


def test_aggregate_gat_two_node_softmax():
    g = _gnn()
    g.add_node("A", [1.0, 0.0])
    g.add_node("B", [0.0, 1.0])
    g.add_edge(_edge("A", "B", 0.7))  # GAT 不用边权，仅作连接
    out = g.aggregate_features(AggregateMode.GAT)
    # 单邻居 → softmax 必为 1 → agg=邻居特征
    assert out["A"][2:4] == pytest.approx((0.0, 1.0))
    assert out["B"][2:4] == pytest.approx((1.0, 0.0))


def test_aggregate_isolated_node_zero():
    g = _gnn()
    g.add_node("LONE", [3.0, 4.0])
    g.add_node("X", [1.0, 1.0])
    g.add_node("Y", [2.0, 2.0])
    g.add_edge(_edge("X", "Y"))
    out = g.aggregate_features(AggregateMode.GCN)
    assert out["LONE"][2:] == (0.0,) * 6  # 孤立节点三路聚合全零
    assert out["LONE"][:2] == (3.0, 4.0)


def test_aggregate_three_relation_kinds_independent():
    g = _gnn()
    for nid in ("A", "B"):
        g.add_node(nid, [1.0])
    g.add_edge(_edge("A", "B", 1.0, RelationKind.CONCEPT_COOCCUR))
    out = g.aggregate_features(AggregateMode.GCN)
    # 仅概念共现图有边 → 第4段（concept）非零，2/3段（supply/industry）为零
    assert out["A"][1] == 0.0 and out["A"][2] == 0.0
    assert out["A"][3] == pytest.approx(1.0)


def test_aggregate_guards():
    g = _gnn()
    with pytest.raises(StockRelationGnnError, match="非法聚合模式"):
        g.aggregate_features("gcn")  # type: ignore[arg-type]
    with pytest.raises(StockRelationGnnError, match="图为空"):
        g.aggregate_features(AggregateMode.GCN)


# ──────────────────────────────────────────────────────────────────────────────
# 密度预测（注入 predictor 回调）
# ──────────────────────────────────────────────────────────────────────────────


def test_predict_density_ok():
    seen: list[tuple[str, tuple[float, ...]]] = []
    g = StockRelationGNN(predictor=lambda sid, feats: seen.append((sid, feats)) or 0.5)
    _abc_graph(g)
    fc = g.predict_density("A", AggregateMode.GCN)
    assert fc.stock_id == "A" and fc.mode is AggregateMode.GCN
    assert fc.score == pytest.approx(0.5)
    assert seen == [("A", fc.features)]  # predictor 收到聚合特征
    assert fc.features == g.aggregate_features(AggregateMode.GCN)["A"]


def test_predict_density_no_predictor_fail_closed():
    g = StockRelationGNN(predictor=None)
    g.add_node("A", [1.0])
    with pytest.raises(StockRelationGnnError, match="predictor 未注入"):
        g.predict_density("A", AggregateMode.GCN)


def test_predict_density_guards():
    g = _gnn()
    g.add_node("A", [1.0])
    with pytest.raises(StockRelationGnnError, match="未知节点"):
        g.predict_density("ghost", AggregateMode.GCN)
    with pytest.raises(StockRelationGnnError, match="非法聚合模式"):
        g.predict_density("A", "gat")  # type: ignore[arg-type]


def test_predict_density_predictor_failure():
    def _boom(_sid, _feats):
        raise RuntimeError("外部预测器故障")

    g = StockRelationGNN(predictor=_boom)
    g.add_node("A", [1.0])
    with pytest.raises(StockRelationGnnError, match="预测异常"):
        g.predict_density("A", AggregateMode.GCN)
    g_nan = StockRelationGNN(predictor=lambda _s, _f: float("nan"))
    g_nan.add_node("A", [1.0])
    with pytest.raises(StockRelationGnnError, match="非有限"):
        g_nan.predict_density("A", AggregateMode.GAT)


def test_determinism_same_input_same_output():
    def _build() -> dict:
        g = _gnn()
        for nid, feat in (("C", [0.3, 0.7]), ("A", [1.0, 0.0]), ("B", [0.5, 0.5])):
            g.add_node(nid, feat)
        g.add_edge(_edge("A", "B", 0.9, RelationKind.SUPPLY_CHAIN))
        g.add_edge(_edge("B", "C", 0.4, RelationKind.SUPPLY_CHAIN))
        g.add_edge(_edge("A", "C", 0.6, RelationKind.SAME_INDUSTRY))
        return g.aggregate_features(AggregateMode.GAT)

    assert _build() == _build()
