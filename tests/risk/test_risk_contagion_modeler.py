# [BLUEPRINT] MOD-RK-046 | docs/03_modules/_domain_risk/risk_contagion_modeler/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-RK-046 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.risk.test_risk_contagion_modeler
# [TESTS] src/zephyr/risk/risk_contagion_modeler.py
"""MOD-RK-046 单元测试：risk_contagion_modeler 风险传播建模器。

蓝图验收（B14-04692/CAND-RSK-050，A9 M15-S01）：
相关性+产业链边建图（边权注入）+ 冲击传导路径模拟（沿边衰减传播）+ 传染评
分（节点暴露度归一）+ 评分入风控参考输出 + 盘后运行语义（非 post_close
Fail-Closed）。会话/评分回调/时钟全注入，不触网。
"""

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.risk.risk_contagion_modeler",
    reason="risk_contagion_modeler not importable",
)

from zephyr.risk.risk_contagion_modeler import (  # noqa: E402
    ContagionEdge,
    ContagionReport,
    EdgeKind,
    RiskContagionError,
    RiskContagionModeler,
    ShockEvent,
)

_T0 = datetime.datetime(2026, 8, 25, 17, 0, 0)

_NODES = ("bank_a", "bank_b", "broker_c")
_EDGES = (
    ContagionEdge("bank_a", "bank_b", Decimal("0.8"), EdgeKind.CORRELATION),
    ContagionEdge("bank_b", "broker_c", Decimal("0.5"), EdgeKind.INDUSTRY_CHAIN),
)


def _modeler(**overrides) -> RiskContagionModeler:
    kwargs = {
        "nodes": _NODES,
        "edges": _EDGES,
        "decay": Decimal("0.5"),
        "session_provider": lambda: "post_close",
        "clock": lambda: _T0,
    }
    kwargs.update(overrides)
    return RiskContagionModeler(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 构造 + 建图 Fail-Closed
# ──────────────────────────────────────────────────────────────────────────────


class TestBuildGraph:
    def test_empty_nodes_raises(self) -> None:
        with pytest.raises(RiskContagionError):
            RiskContagionModeler(nodes=[], session_provider=lambda: "post_close")

    def test_decay_out_of_range_raises(self) -> None:
        with pytest.raises(RiskContagionError):
            _modeler(decay=Decimal("0"))
        with pytest.raises(RiskContagionError):
            _modeler(decay=Decimal("1"))

    def test_edge_unknown_endpoint_raises(self) -> None:
        bad = ContagionEdge("bank_a", "ghost", Decimal("0.5"), EdgeKind.CORRELATION)
        with pytest.raises(RiskContagionError):
            _modeler(edges=[bad])

    def test_edge_weight_out_of_range_raises(self) -> None:
        bad = ContagionEdge("bank_a", "bank_b", Decimal("1.5"), EdgeKind.CORRELATION)
        with pytest.raises(RiskContagionError):
            _modeler(edges=[bad])
        with pytest.raises(RiskContagionError):
            _modeler().add_edge(
                ContagionEdge("bank_a", "bank_b", Decimal("0"), EdgeKind.CORRELATION)
            )

    def test_self_loop_rejected(self) -> None:
        with pytest.raises(RiskContagionError):
            _modeler().add_edge(
                ContagionEdge("bank_a", "bank_a", Decimal("0.5"), EdgeKind.CORRELATION)
            )

    def test_neighbors_sorted_deterministic(self) -> None:
        m = RiskContagionModeler(
            nodes=_NODES,
            edges=[
                ContagionEdge("bank_a", "broker_c", Decimal("0.3"), EdgeKind.INDUSTRY_CHAIN),
                ContagionEdge("bank_a", "bank_b", Decimal("0.8"), EdgeKind.CORRELATION),
            ],
            session_provider=lambda: "post_close",
            clock=lambda: _T0,
        )
        assert [e.target for e in m.neighbors_of("bank_a")] == ["bank_b", "broker_c"]
        assert m.graph_nodes() == ("bank_a", "bank_b", "broker_c")
        with pytest.raises(RiskContagionError):
            m.neighbors_of("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# 盘后运行语义
# ──────────────────────────────────────────────────────────────────────────────


class TestPostCloseSemantics:
    def test_session_not_injected_raises(self) -> None:
        m = _modeler(session_provider=None)
        with pytest.raises(RiskContagionError):
            m.simulate([ShockEvent("bank_a", Decimal("-0.1"))])

    def test_intraday_session_rejected(self) -> None:
        m = _modeler(session_provider=lambda: "intraday")
        with pytest.raises(RiskContagionError, match="盘后"):
            m.simulate([ShockEvent("bank_a", Decimal("-0.1"))])

    def test_post_close_accepted(self) -> None:
        report = _modeler().simulate([ShockEvent("bank_a", Decimal("-0.1"))])
        assert isinstance(report, ContagionReport)
        assert report.evaluated_at == _T0


# ──────────────────────────────────────────────────────────────────────────────
# 冲击传导模拟（沿边衰减传播）
# ──────────────────────────────────────────────────────────────────────────────


class TestPropagation:
    def test_shock_validations(self) -> None:
        m = _modeler()
        with pytest.raises(RiskContagionError):
            m.simulate([])
        with pytest.raises(RiskContagionError):
            m.simulate([ShockEvent("ghost", Decimal("-0.1"))])
        with pytest.raises(RiskContagionError):
            m.simulate([ShockEvent("bank_a", Decimal("0"))])

    def test_decay_along_edges(self) -> None:
        # bank_a 冲击 -1 → bank_b: -1×0.8×0.5=-0.4 → broker_c: -0.4×0.5×0.5=-0.1
        report = _modeler().simulate([ShockEvent("bank_a", Decimal("-1"))])
        assert report.impact_of("bank_a") == Decimal("-1")
        assert report.impact_of("bank_b") == Decimal("-0.4")
        assert report.impact_of("broker_c") == Decimal("-0.10")
        assert report.rounds_used == 2

    def test_unconnected_node_untouched(self) -> None:
        report = _modeler().simulate([ShockEvent("broker_c", Decimal("-0.5"))])
        assert report.impact_of("bank_a") == Decimal("0")
        assert report.impact_of("bank_b") == Decimal("0")
        assert report.impact_of("broker_c") == Decimal("-0.5")

    def test_multi_shock_accumulates(self) -> None:
        report = _modeler().simulate([
            ShockEvent("bank_a", Decimal("-1")),
            ShockEvent("bank_a", Decimal("-0.5")),
        ])
        assert report.impact_of("bank_a") == Decimal("-1.5")

    def test_scores_normalized_exposure(self) -> None:
        report = _modeler().simulate([ShockEvent("bank_a", Decimal("-1"))])
        assert report.score_of("bank_a") == Decimal("1")
        assert report.score_of("bank_b") == Decimal("0.4")
        assert report.score_of("broker_c") == Decimal("0.1")
        assert all(Decimal("0") <= s <= Decimal("1") for _, s in report.scores)

    def test_impacts_sorted_by_node(self) -> None:
        report = _modeler().simulate([ShockEvent("broker_c", Decimal("-1"))])
        assert [n for n, _ in report.impacts] == ["bank_a", "bank_b", "broker_c"]

    def test_score_sink_receives_report(self) -> None:
        seen: list[ContagionReport] = []
        report = _modeler(score_sink=seen.append).simulate(
            [ShockEvent("bank_a", Decimal("-1"))]
        )
        assert seen == [report]  # 评分入风控参考输出

    def test_score_sink_failure_not_blocking(self) -> None:
        def boom(report: ContagionReport) -> None:
            raise RuntimeError("sink 宕机")

        report = _modeler(score_sink=boom).simulate([ShockEvent("bank_a", Decimal("-1"))])
        assert report.impact_of("bank_a") == Decimal("-1")

    def test_determinism_same_input_same_output(self) -> None:
        m1, m2 = _modeler(), _modeler()
        r1 = m1.simulate([ShockEvent("bank_a", Decimal("-1"))])
        r2 = m2.simulate([ShockEvent("bank_a", Decimal("-1"))])
        assert r1 == r2
