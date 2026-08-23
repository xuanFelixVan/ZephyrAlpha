# [BLUEPRINT] MOD-SIG-055 | docs/03_modules/MOD-SIG-055/
# [MODULE] tests.signal_ashare.test_supply_chain_gnn
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] pytest tests/signal_ashare/test_supply_chain_gnn.py -q
# [TTL] permanent

"""供应链 GNN 骨架（MOD-SIG-055）单元测试——图校验/未训练 fail-closed/风险传播占位。"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.signal_ashare.supply_chain_gnn import SupplyChainGnn


def _graph():
    nodes = ["A", "B", "C"]
    edges = [("A", "B", 0.8), ("B", "C", 0.5)]
    return nodes, edges


class TestFailClosed:
    def test_propagate_before_fit_raises(self):
        g = SupplyChainGnn()
        with pytest.raises(ValueError, match="未训练"):
            g.propagate_risk({"A": 1.0})


class TestGraphValidation:
    def test_edge_to_unknown_node_rejected(self):
        g = SupplyChainGnn()
        with pytest.raises(ValueError):
            g.fit_baseline(["A"], [("A", "B", 0.5)])

    def test_edge_weight_bounds(self):
        g = SupplyChainGnn()
        with pytest.raises(ValueError):
            g.fit_baseline(["A", "B"], [("A", "B", 0.0)])
        with pytest.raises(ValueError):
            g.fit_baseline(["A", "B"], [("A", "B", 1.5)])

    def test_duplicate_node_rejected(self):
        g = SupplyChainGnn()
        with pytest.raises(ValueError):
            g.fit_baseline(["A", "A"], [])

    def test_empty_nodes_rejected(self):
        g = SupplyChainGnn()
        with pytest.raises(ValueError):
            g.fit_baseline([], [])


class TestPropagation:
    def test_seed_scores_passthrough_without_edges(self):
        g = SupplyChainGnn()
        g.fit_baseline(["A", "B"], [])
        scores = g.propagate_risk({"A": 0.9})
        assert scores["A"] == pytest.approx(0.9)
        assert scores["B"] == 0.0

    def test_risk_propagates_along_edges_with_decay(self):
        g = SupplyChainGnn(decay=1.0)
        nodes, edges = _graph()
        g.fit_baseline(nodes, edges)
        scores = g.propagate_risk({"A": 1.0})
        assert scores["B"] == pytest.approx(0.8)
        assert scores["C"] == pytest.approx(0.8 * 0.5)

    def test_unknown_seed_node_rejected(self):
        g = SupplyChainGnn()
        nodes, edges = _graph()
        g.fit_baseline(nodes, edges)
        with pytest.raises(ValueError):
            g.propagate_risk({"ZZ": 1.0})

    def test_scores_clipped_to_unit(self):
        g = SupplyChainGnn()
        g.fit_baseline(["A", "B"], [("A", "B", 1.0)])
        scores = g.propagate_risk({"A": 5.0})
        assert scores["B"] <= 1.0

    def test_decay_bounds_validated(self):
        with pytest.raises(ValueError):
            SupplyChainGnn(decay=0.0)
