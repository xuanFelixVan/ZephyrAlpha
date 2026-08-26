# [BLUEPRINT] MOD-SIG-121 | docs/03_modules/_domain_signal/orderflow_network_panic/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-121 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_orderflow_network_panic
# [TESTS] src/zephyr/signal_ashare/orderflow_network_panic.py
"""MOD-SIG-121 单元测试：orderflow_network_panic 跨资产订单流网络与亏钱扩散。

蓝图验收（B10-01388/CAND-TESTB-041，A1 模块52）：
大幅回撤事件检测（窗口回撤 >30%）+ 板块内 Moran's I 空间聚集统计
（>0.3 聚集判定）+ 恐慌传导时滞（Granger 1-2 日注入检验器）+ 扩散路径
与强度输出。时钟/检验器全注入内存替身，纯内存不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.orderflow_network_panic",
    reason="orderflow_network_panic not importable",
)

from zephyr.signal_ashare.orderflow_network_panic import (  # noqa: E402
    DiffusionPath,
    OrderflowNetworkPanic,
    OrderflowPanicError,
)

_T0 = datetime.datetime(2026, 8, 26, 10, 0, 0)


def _model(
    granger=None,
) -> OrderflowNetworkPanic:
    return OrderflowNetworkPanic(
        granger_tester=granger,
        clock=lambda: _T0,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 回撤事件检测
# ──────────────────────────────────────────────────────────────────────────────


class TestDetectDrawdownEvents:
    def test_single_event(self) -> None:
        prices = [100.0] * 5 + [60.0] + [100.0] * 5
        evs = _model().detect_drawdown_events("A", prices, window=6)
        assert len(evs) == 1
        assert evs[0].node == "A"
        assert evs[0].depth == pytest.approx(0.4)

    def test_below_threshold_no_event(self) -> None:
        prices = [100.0] * 5 + [80.0] + [100.0] * 5
        evs = _model().detect_drawdown_events("A", prices, window=6)
        assert len(evs) == 0

    def test_no_overlap(self) -> None:
        """事件区间不重叠：第一次 trough 后跳至其后。"""
        prices = [100.0, 100.0, 100.0, 100.0, 100.0, 60.0,
                  90.0, 90.0, 90.0, 90.0, 90.0, 55.0]
        evs = _model().detect_drawdown_events("A", prices, window=6)
        assert len(evs) == 2

    def test_invalid_inputs_raises(self) -> None:
        with pytest.raises(OrderflowPanicError):
            _model().detect_drawdown_events("", [100.0, 90.0], window=2)
        with pytest.raises(OrderflowPanicError):
            _model().detect_drawdown_events("A", [100.0, 90.0], window=1)
        with pytest.raises(OrderflowPanicError):
            _model().detect_drawdown_events("A", [100.0, 90.0], window=2, threshold=1.2)
        with pytest.raises(OrderflowPanicError):
            _model().detect_drawdown_events("A", [100.0, -1.0], window=2)


# ──────────────────────────────────────────────────────────────────────────────
# Moran's I 空间聚集
# ──────────────────────────────────────────────────────────────────────────────


class TestMoransI:
    def test_positive_clustering(self) -> None:
        """高值相邻 → Moran's I > 0.3。"""
        values = [0.5, 0.55, 0.52, 0.1, 0.1]
        adj = [
            [0, 1, 1, 0, 0],
            [1, 0, 1, 0, 0],
            [1, 1, 0, 1, 0],
            [0, 0, 1, 0, 1],
            [0, 0, 0, 1, 0],
        ]
        m = _model().morans_i(values, adj)
        assert m > 0.3

    def test_no_variance_returns_zero(self) -> None:
        m = _model().morans_i([0.2, 0.2, 0.2], [[0, 1, 0], [1, 0, 1], [0, 1, 0]])
        assert m == 0.0

    def test_no_edges_raises(self) -> None:
        with pytest.raises(OrderflowPanicError):
            _model().morans_i([0.2, 0.3], [[0, 0], [0, 0]])

    def test_adjacency_validation(self) -> None:
        with pytest.raises(OrderflowPanicError):
            _model().morans_i([0.2], [[0]])  # 长度不足
        with pytest.raises(OrderflowPanicError):
            _model().morans_i([0.2, 0.3], [[0, 1], [1]])  # 非方阵
        with pytest.raises(OrderflowPanicError):
            _model().morans_i([0.2, 0.3], [[0, -1], [1, 0]])  # 负权重
        with pytest.raises(OrderflowPanicError):
            _model().morans_i([0.2, 0.3], [[0, 1], [1, 0], [0, 0]])  # 维度不齐


# ──────────────────────────────────────────────────────────────────────────────
# 恐慌传导时滞（Granger 注入）
# ──────────────────────────────────────────────────────────────────────────────


class TestPanicConductionLag:
    def test_significant_lag(self) -> None:
        def tester(src, tgt, lag):
            # lag=1 显著，lag=2 不显著
            return 0.01 if lag == 1 else 0.99

        m = _model(granger=tester)
        lag = m.panic_conduction_lag([0.01] * 8, [0.01] * 8, max_lag=2, alpha=0.05)
        assert lag == 1
        # lag=1 不显著时取 lag=2
        m2 = _model(granger=lambda s, t, l: 0.99 if l == 1 else 0.01)
        assert m2.panic_conduction_lag([0.01] * 8, [0.01] * 8, max_lag=2) == 2

    def test_no_significant_lag(self) -> None:
        def tester(src, tgt, lag):
            return 0.99

        m = _model(granger=tester)
        lag = m.panic_conduction_lag([0.01] * 8, [0.01] * 8, max_lag=2, alpha=0.05)
        assert lag is None

    def test_not_injected_raises(self) -> None:
        with pytest.raises(OrderflowPanicError):
            _model().panic_conduction_lag([0.01] * 8, [0.01] * 8, max_lag=2)

    def test_invalid_params_raises(self) -> None:
        def tester(src, tgt, lag):
            return 0.01

        with pytest.raises(OrderflowPanicError):
            _model(granger=tester).panic_conduction_lag(
                [0.01] * 8, [0.01] * 8, max_lag=3,
            )
        with pytest.raises(OrderflowPanicError):
            _model(granger=tester).panic_conduction_lag(
                [0.01] * 8, [0.01] * 8, max_lag=2, alpha=1.0,
            )
        with pytest.raises(OrderflowPanicError):
            _model(granger=tester).panic_conduction_lag(
                [0.01] * 4, [0.01] * 4, max_lag=2,
            )
        with pytest.raises(OrderflowPanicError):
            _model(granger=tester).panic_conduction_lag(
                [0.01] * 8, [0.01] * 4, max_lag=2,
            )

    def test_tester_failure_raises(self) -> None:
        def bad_tester(src, tgt, lag):
            raise RuntimeError("模拟检验器故障")

        with pytest.raises(OrderflowPanicError):
            _model(granger=bad_tester).panic_conduction_lag(
                [0.01] * 8, [0.01] * 8, max_lag=1,
            )
        with pytest.raises(OrderflowPanicError):
            _model(granger=lambda s, t, l: float("nan")).panic_conduction_lag(
                [0.01] * 8, [0.01] * 8, max_lag=1,
            )


# ──────────────────────────────────────────────────────────────────────────────
# 扩散路径（BFS + 强度衰减）
# ──────────────────────────────────────────────────────────────────────────────


class TestDiffusionPaths:
    def test_basic_star(self) -> None:
        """星型中心 A 传播至其余节点（1 跳）。"""
        adj = [
            [0, 1, 1, 1],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
            [1, 0, 0, 0],
        ]
        paths = _model().diffusion_paths(
            ["A", "B", "C", "D"], {"A": 0.4}, adj, decay=0.5,
        )
        assert len(paths) == 3
        for p in paths:
            assert p.source == "A"
            assert p.hops == 1
            assert p.strength == pytest.approx(0.4 * 0.5)

    def test_chain(self) -> None:
        """链式 A-B-C：A 到 C 2 跳。"""
        adj = [
            [0, 1, 0],
            [1, 0, 1],
            [0, 1, 0],
        ]
        paths = _model().diffusion_paths(
            ["A", "B", "C"], {"A": 0.4}, adj, decay=0.5,
        )
        p_map = {(p.source, p.target): p for p in paths}
        assert p_map[("A", "B")].hops == 1
        assert p_map[("A", "C")].hops == 2
        assert p_map[("A", "C")].strength == pytest.approx(0.4 * 0.5 * 0.5)

    def test_multi_sources(self) -> None:
        """多源：A 可达 B(1)/C(2)；B 可达 A(1)/C(1)，共 4 条。"""
        adj = [
            [0, 1, 0],
            [1, 0, 1],
            [0, 1, 0],
        ]
        paths = _model().diffusion_paths(
            ["A", "B", "C"], {"A": 0.4, "B": 0.3}, adj, decay=0.5,
        )
        assert len(paths) == 4
        hops = sorted(p.hops for p in paths)
        assert hops == [1, 1, 1, 2]
        # 同跳按 source/target 确定性排序
        assert [(p.hops, p.source, p.target) for p in paths] == sorted(
            (p.hops, p.source, p.target) for p in paths
        )

    def test_diffusion_invalid_inputs_raises(self) -> None:
        with pytest.raises(OrderflowPanicError):
            _model().diffusion_paths(["A"], {}, [[0]], decay=0.5)  # 空源
        with pytest.raises(OrderflowPanicError):
            _model().diffusion_paths([], {"A": 0.4}, [[0]], decay=0.5)  # 空节点
        with pytest.raises(OrderflowPanicError):
            _model().diffusion_paths(
                ["A", "B"], {"C": 0.4}, [[0, 1], [1, 0]], decay=0.5,
            )  # 源不在节点全集
        with pytest.raises(OrderflowPanicError):
            _model().diffusion_paths(["A", "B"], {"A": 0.4}, [[0, 1], [1, 0]], decay=1.2)
        with pytest.raises(OrderflowPanicError):
            _model().diffusion_paths(["A", "B"], {"A": -0.4}, [[0, 1], [1, 0]], decay=0.5)
        with pytest.raises(OrderflowPanicError):
            _model().diffusion_paths(
                ["A", "B"], {"A": float("nan")}, [[0, 1], [1, 0]], decay=0.5,
            )


# ──────────────────────────────────────────────────────────────────────────────
# 综合评估（端到端 + 确定性）
# ──────────────────────────────────────────────────────────────────────────────


def _default_granger(src, tgt, lag):
    return 0.01


def _make_returns(n: int, start: float = 1.0) -> list[float]:
    return [0.01] * n


class TestAssess:
    def test_no_events_not_panic(self) -> None:
        returns = {chr(65 + i): _make_returns(10) for i in range(3)}
        adj = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
        out = _model(granger=_default_granger).assess(
            node_returns=returns, adjacency=adj, window=4,
        )
        assert len(out.events) == 0
        assert out.is_panic is False
        assert out.assessed_at == _T0

    def test_events_no_clustering_not_panic(self) -> None:
        # 给一个节点深回撤，但 Moran's I 低（其他节点 0 回撤），不聚集
        returns = {
            "A": [0.5, 0.5, 0.5, -0.3, 0.5, 0.5],
            "B": [0.01] * 6,
            "C": [0.01] * 6,
        }
        adj = [[0, 1, 0], [1, 0, 0], [0, 0, 0]]
        out = _model(granger=_default_granger).assess(
            node_returns=returns, adjacency=adj, window=3,
        )
        assert len(out.events) > 0
        assert out.is_clustered is False
        assert out.is_panic is False

    def test_events_and_clustering_is_panic(self) -> None:
        returns = {
            "A": [0.5, 0.5, 0.5, -0.4, 0.5, 0.5],
            "B": [0.5, 0.5, 0.5, -0.4, 0.5, 0.5],
            "C": [0.01] * 6,
        }
        adj = [[0, 1, 0], [1, 0, 0], [0, 0, 0]]
        out = _model(granger=_default_granger).assess(
            node_returns=returns, adjacency=adj, window=3,
        )
        assert len(out.events) > 0
        assert out.is_clustered is True
        assert out.is_panic is True

    def test_conduction_links_present(self) -> None:
        returns = {
            "A": [0.5, 0.5, 0.5, -0.4, 0.5, 0.5],
            "B": [0.5, 0.5, 0.5, -0.4, 0.5, 0.5],
        }
        adj = [[0, 1], [1, 0]]
        out = _model(granger=_default_granger).assess(
            node_returns=returns, adjacency=adj, window=3,
        )
        assert len(out.conduction_links) > 0

    def test_empty_node_returns_raises(self) -> None:
        with pytest.raises(OrderflowPanicError):
            _model(granger=_default_granger).assess(
                node_returns={}, adjacency=[[0]], window=3,
            )

    def test_mismatched_series_lengths_raises(self) -> None:
        with pytest.raises(OrderflowPanicError):
            _model(granger=_default_granger).assess(
                node_returns={"A": [0.01] * 5, "B": [0.01] * 4},
                adjacency=[[0, 1], [1, 0]],
                window=3,
            )

    def test_diffusion_paths_present(self) -> None:
        returns = {
            "A": [0.5, 0.5, 0.5, -0.4, 0.5, 0.5],
            "B": [0.5, 0.5, 0.5, -0.4, 0.5, 0.5],
            "C": [0.01] * 6,
        }
        adj = [
            [0, 1, 0],
            [1, 0, 1],
            [0, 1, 0],
        ]
        out = _model(granger=_default_granger).assess(
            node_returns=returns, adjacency=adj, window=3,
        )
        assert len(out.diffusion_paths) > 0
        assert isinstance(out.diffusion_paths[0], DiffusionPath)

    def test_determinism(self) -> None:
        returns = {
            "A": [0.5, 0.5, 0.5, -0.4, 0.5, 0.5],
            "B": [0.5, 0.5, 0.5, -0.4, 0.5, 0.5],
        }
        adj = [[0, 1], [1, 0]]
        kwargs = dict(node_returns=returns, adjacency=adj, window=3)
        a = _model(granger=_default_granger).assess(**kwargs)
        b = _model(granger=_default_granger).assess(**kwargs)
        assert a == b
