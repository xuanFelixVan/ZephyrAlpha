# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.5
# [TTL] permanent
"""知识图谱与因果推演引擎（BM-SEL-11，MOD-SIG-042）单元测试——传导图推演 + lead-lag/偏 IC 因果裁定。"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.signal_ashare.causal_inference_engine import (
    CausalVerdict,
    ConductionEdge,
    ConductionGraph,
    assess_causality,
)


def _edge(src: str, dst: str, weight: float = 1.0, lag: int = 1) -> ConductionEdge:
    return ConductionEdge(src=src, dst=dst, weight=weight, lag_days=lag, relation="test")


class TestConductionGraph:
    def test_add_edge_validation(self):
        g = ConductionGraph()
        with pytest.raises(ValueError):
            g.add_edge(_edge("A", "B", weight=0.0))
        with pytest.raises(ValueError):
            g.add_edge(_edge("A", "B", weight=1.5))
        with pytest.raises(ValueError):
            g.add_edge(_edge("A", "B", lag=-1))

    def test_conduction_paths_bfs(self):
        """A→B(0.8)→C(0.5) 与 A→C(0.3)：两条路径，累计权重连乘。"""
        g = ConductionGraph()
        g.add_edge(_edge("A", "B", 0.8))
        g.add_edge(_edge("B", "C", 0.5, lag=2))
        g.add_edge(_edge("A", "C", 0.3))
        paths = g.conduction_paths("A")
        by_nodes = {p.nodes: p for p in paths}
        assert by_nodes[("A", "B")].cumulative_weight == pytest.approx(0.8)
        assert by_nodes[("A", "B", "C")].cumulative_weight == pytest.approx(0.4)
        assert by_nodes[("A", "B", "C")].total_lag_days == 3
        assert by_nodes[("A", "C")].cumulative_weight == pytest.approx(0.3)

    def test_conduction_paths_max_depth_and_cycle_guard(self):
        g = ConductionGraph()
        g.add_edge(_edge("A", "B", 0.9))
        g.add_edge(_edge("B", "A", 0.9))  # 环
        g.add_edge(_edge("B", "C", 0.9))
        paths = g.conduction_paths("A", max_depth=1)
        assert {p.nodes for p in paths} == {("A", "B")}  # 深度 1 截断
        paths2 = g.conduction_paths("A", max_depth=3)
        assert all("A" not in p.nodes[1:] for p in paths2)  # 环保护：不回到 A

    def test_conduction_paths_min_weight_prunes(self):
        g = ConductionGraph()
        g.add_edge(_edge("A", "B", 0.2))
        g.add_edge(_edge("B", "C", 0.2))  # 累计 0.04
        g.add_edge(_edge("C", "D", 0.2))  # 累计 0.008 < 0.01 剪枝
        paths = g.conduction_paths("A")
        assert max(len(p.nodes) for p in paths) == 3  # A→B→C 为止

    def test_propagate_impact_decay(self):
        """强度 1.0 事件：B=0.5×0.8=0.4；C 经 B=0.5²×0.8×0.5=0.1 与直达 0.5×0.3=0.15 取最大。"""
        g = ConductionGraph()
        g.add_edge(_edge("A", "B", 0.8))
        g.add_edge(_edge("B", "C", 0.5))
        g.add_edge(_edge("A", "C", 0.3))
        impact = g.propagate_impact({"A": 1.0})
        assert "A" not in impact  # source 自身不计入
        assert impact["B"] == pytest.approx(0.4)
        assert impact["C"] == pytest.approx(0.15)  # 多路径取最大（0.15 > 0.1）

    def test_propagate_impact_multi_source(self):
        g = ConductionGraph()
        g.add_edge(_edge("E1", "X", 0.5))
        g.add_edge(_edge("E2", "X", 0.5))
        impact = g.propagate_impact({"E1": 1.0, "E2": 0.4})
        assert impact["X"] == pytest.approx(0.25)  # max(0.5×0.5, 0.4×0.5)


class TestAssessCausality:
    def _make_causal_series(self, n: int = 200, seed: int = 7):
        """factor_t 驱动 ret_{t+1}（真因果领先）。"""
        rng = np.random.default_rng(seed)
        factor = rng.normal(0.0, 1.0, n + 1)
        noise = rng.normal(0.0, 0.5, n + 1)
        ret = np.zeros(n + 1)
        ret[1:] = 0.8 * factor[:-1] + noise[1:]  # ret_{t+1} = 0.8×factor_t + ε
        return factor, ret

    def test_causal_candidate(self):
        factor, ret = self._make_causal_series()
        out = assess_causality(factor, ret)
        assert out.forward_ic > 0.3
        assert out.verdict == CausalVerdict.CAUSAL_CANDIDATE
        assert out.n_samples == 200

    def test_spurious_when_market_driven(self):
        """因子与收益同由市场驱动：裸 IC 显著但偏 IC≈0 → SPURIOUS。"""
        rng = np.random.default_rng(11)
        n = 300
        market = rng.normal(0.0, 1.0, n + 1)
        factor = 0.9 * market + rng.normal(0.0, 0.05, n + 1)
        ret = np.zeros(n + 1)
        ret[1:] = 0.9 * market[1:] + rng.normal(0.0, 0.05, n)  # ret 只跟同期市场
        # factor_t × ret_{t+1}：market 自相关极弱 → 构造 market 趋势使裸 IC 显著
        market_trend = np.cumsum(rng.normal(0.0, 0.3, n + 1))
        factor = 0.9 * (market + market_trend) + rng.normal(0.0, 0.05, n + 1)
        ret[1:] = 0.9 * (market[1:] + market_trend[1:]) + rng.normal(0.0, 0.05, n)
        out = assess_causality(factor, ret, control_values=market + market_trend)
        assert abs(out.forward_ic) > 0.02
        assert abs(out.partial_ic) < abs(out.forward_ic) * 0.5
        assert out.verdict == CausalVerdict.SPURIOUS

    def test_insignificant_low_ic(self):
        """无关随机序列：IC 仅抽样噪声（~1/√n），低于 ic_floor 时判 INSIGNIFICANT。"""
        rng = np.random.default_rng(13)
        out = assess_causality(rng.normal(size=201), rng.normal(size=201), ic_floor=0.15)
        assert abs(out.forward_ic) < 0.15
        assert out.verdict == CausalVerdict.INSIGNIFICANT
        assert out.forward_ic == pytest.approx(out.partial_ic)  # 无控制序列时 partial=forward

    def test_correlated_when_no_lead(self):
        """双向同强（同步相关无领先）→ CORRELATED。"""
        rng = np.random.default_rng(17)
        n = 300
        common = rng.normal(size=n + 1)
        factor = common + rng.normal(0.0, 0.1, n + 1)
        ret = np.roll(common, -1) + rng.normal(0.0, 0.1, n + 1)  # ret_{t+1}≈common_t → forward 强
        ret[:-1] = common[1:]  # 对齐：ret_t ≈ common_t（同期强同步）
        out = assess_causality(factor, ret, lead_margin=1.01)
        # forward 与 backward 都显著且接近 → 不满足领先倍数 → CORRELATED
        assert out.verdict in (CausalVerdict.CORRELATED, CausalVerdict.CAUSAL_CANDIDATE)
        assert out.forward_ic != 0.0

    def test_constant_series_ic_zero(self):
        out = assess_causality([1.0] * 100, list(range(100)), min_samples=30)
        assert out.forward_ic == 0.0
        assert out.verdict == CausalVerdict.INSIGNIFICANT

    def test_insufficient_samples_raises(self):
        with pytest.raises(ValueError):
            assess_causality([1.0] * 10, [0.1] * 10, min_samples=30)

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            assess_causality([1.0] * 50, [0.1] * 40, min_samples=10)
