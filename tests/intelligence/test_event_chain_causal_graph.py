# [BLUEPRINT] MOD-INT-EVENT-CHAIN | docs/03_modules/_domain_intelligence/event_chain_causal_graph/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INT-EVENT-CHAIN | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.intelligence.test_event_chain_causal_graph
# [TESTS] src/zephyr/intelligence/event_chain_causal_graph.py
"""MOD-INT-EVENT-CHAIN 单元测试：event_chain_causal_graph 事件链推理因果图。

蓝图验收（B10-01448/CAND-AISA-011，A1 模块41）：
事件节点四类词表闭合 + Granger 因果边（滞后+p 值阈值，检验器注入）+
贝叶斯条件概率表（频次+拉普拉斯平滑）+ P(B|A) 查询。
granger 检验器全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.intelligence.event_chain_causal_graph",
    reason="event_chain_causal_graph not importable",
)

from zephyr.intelligence.event_chain_causal_graph import (  # noqa: E402
    EventChainCausalGraph,
    EventChainError,
    EventNode,
    EventType,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)
_SERIES = [0.1, 0.4, 0.2, 0.5, 0.3, 0.6, 0.2, 0.7]


def _graph(p_value: float = 0.01, **kw) -> EventChainCausalGraph:
    return EventChainCausalGraph(granger_tester=lambda a, b, lag: p_value, **kw)


def _node(event_id: str, etype: EventType = EventType.POLICY) -> EventNode:
    return EventNode(event_id=event_id, event_type=etype, name=f"事件{event_id}", occurred_at=_T0)


def _two_node_graph(p_value: float = 0.01) -> EventChainCausalGraph:
    g = _graph(p_value)
    g.register_event(_node("policy-a"))
    g.register_event(_node("industry-b", EventType.INDUSTRY_DATA))
    return g


# ──────────────────────────────────────────────────────────────────────────────
# 事件节点表
# ──────────────────────────────────────────────────────────────────────────────


class TestNodes:
    def test_register_four_types(self) -> None:
        g = _graph()
        for i, et in enumerate(EventType):
            g.register_event(_node(f"e{i}", et))
        assert g.node_count() == 4

    def test_duplicate_id_raises(self) -> None:
        g = _graph()
        g.register_event(_node("e1"))
        with pytest.raises(EventChainError):
            g.register_event(_node("e1", EventType.OVERSEAS))

    def test_invalid_type_raises(self) -> None:
        g = _graph()
        bad = EventNode(event_id="e1", event_type=" rumor", name="x", occurred_at=_T0)
        with pytest.raises(EventChainError):
            g.register_event(bad)  # type: ignore[arg-type]

    def test_empty_fields_raise(self) -> None:
        g = _graph()
        with pytest.raises(EventChainError):
            g.register_event(_node(""))
        with pytest.raises(EventChainError):
            g.register_event(EventNode(event_id="e1", event_type=EventType.POLICY, name="", occurred_at=_T0))

    def test_unknown_event_query_raises(self) -> None:
        with pytest.raises(EventChainError):
            _graph().event("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# Granger 因果边
# ──────────────────────────────────────────────────────────────────────────────


class TestGrangerEdge:
    def test_add_edge_ok(self) -> None:
        g = _two_node_graph(p_value=0.01)
        edge = g.add_granger_edge("policy-a", "industry-b", lag=2, cause_series=_SERIES, effect_series=_SERIES)
        assert edge.lag == 2
        assert edge.p_value == 0.01

    def test_insignificant_p_rejected(self) -> None:
        g = _two_node_graph(p_value=0.2)  # >= 默认阈值 0.05
        with pytest.raises(EventChainError):
            g.add_granger_edge("policy-a", "industry-b", lag=1, cause_series=_SERIES, effect_series=_SERIES)
        assert g.edges_of("policy-a") == ()  # 未注册

    def test_p_boundary_accepted(self) -> None:
        g = _two_node_graph(p_value=0.049)
        g.add_granger_edge("policy-a", "industry-b", lag=1, cause_series=_SERIES, effect_series=_SERIES)

    def test_tester_invoked_with_lag(self) -> None:
        seen: list[int] = []
        g = EventChainCausalGraph(granger_tester=lambda a, b, lag: seen.append(lag) or 0.01)
        g.register_event(_node("a"))
        g.register_event(_node("b", EventType.ANNOUNCEMENT))
        g.add_granger_edge("a", "b", lag=3, cause_series=_SERIES, effect_series=_SERIES)
        assert seen == [3]

    def test_lag_out_of_range_raises(self) -> None:
        g = _two_node_graph()
        with pytest.raises(EventChainError):
            g.add_granger_edge("policy-a", "industry-b", lag=0, cause_series=_SERIES, effect_series=_SERIES)
        with pytest.raises(EventChainError):
            g.add_granger_edge("policy-a", "industry-b", lag=99, cause_series=_SERIES, effect_series=_SERIES)

    def test_self_loop_raises(self) -> None:
        g = _two_node_graph()
        with pytest.raises(EventChainError):
            g.add_granger_edge("policy-a", "policy-a", lag=1, cause_series=_SERIES, effect_series=_SERIES)

    def test_unknown_node_raises(self) -> None:
        g = _two_node_graph()
        with pytest.raises(EventChainError):
            g.add_granger_edge("ghost", "industry-b", lag=1, cause_series=_SERIES, effect_series=_SERIES)

    def test_duplicate_edge_raises(self) -> None:
        g = _two_node_graph()
        g.add_granger_edge("policy-a", "industry-b", lag=1, cause_series=_SERIES, effect_series=_SERIES)
        with pytest.raises(EventChainError):
            g.add_granger_edge("policy-a", "industry-b", lag=2, cause_series=_SERIES, effect_series=_SERIES)

    def test_bad_series_raises(self) -> None:
        g = _two_node_graph()
        with pytest.raises(EventChainError):
            g.add_granger_edge("policy-a", "industry-b", lag=1, cause_series=[], effect_series=[])
        with pytest.raises(EventChainError):
            g.add_granger_edge("policy-a", "industry-b", lag=1, cause_series=[1.0], effect_series=_SERIES)

    def test_p_value_out_of_range_raises(self) -> None:
        g = _two_node_graph(p_value=1.5)
        with pytest.raises(EventChainError):
            g.add_granger_edge("policy-a", "industry-b", lag=1, cause_series=_SERIES, effect_series=_SERIES)

    def test_constructor_validation(self) -> None:
        with pytest.raises(EventChainError):
            EventChainCausalGraph(granger_tester=None)  # type: ignore[arg-type]
        with pytest.raises(EventChainError):
            EventChainCausalGraph(granger_tester=lambda a, b, l: 0.01, p_threshold=0.0)
        with pytest.raises(EventChainError):
            EventChainCausalGraph(granger_tester=lambda a, b, l: 0.01, max_lag=0)


# ──────────────────────────────────────────────────────────────────────────────
# 贝叶斯条件概率表
# ──────────────────────────────────────────────────────────────────────────────


class TestBayesianCpt:
    def _graph_with_edge(self) -> EventChainCausalGraph:
        g = _two_node_graph()
        g.add_granger_edge("policy-a", "industry-b", lag=1, cause_series=_SERIES, effect_series=_SERIES)
        return g

    def test_laplace_prior_half(self) -> None:
        g = self._graph_with_edge()
        assert g.probability("industry-b", given_cause_id="policy-a") == pytest.approx(0.5)

    def test_frequency_estimate(self) -> None:
        g = self._graph_with_edge()
        for hit in (True, True, True, False):
            g.record_outcome("policy-a", "industry-b", effect_occurred=hit)
        # (3+1)/(4+2) = 4/6
        assert g.probability("industry-b", given_cause_id="policy-a") == pytest.approx(4.0 / 6.0)

    def test_all_misses(self) -> None:
        g = self._graph_with_edge()
        for _ in range(3):
            g.record_outcome("policy-a", "industry-b", effect_occurred=False)
        assert g.probability("industry-b", given_cause_id="policy-a") == pytest.approx(1.0 / 5.0)

    def test_probability_bounded(self) -> None:
        g = self._graph_with_edge()
        for _ in range(50):
            g.record_outcome("policy-a", "industry-b", effect_occurred=True)
        p = g.probability("industry-b", given_cause_id="policy-a")
        assert 0.0 <= p <= 1.0

    def test_custom_alpha(self) -> None:
        g = _two_node_graph()
        g2 = EventChainCausalGraph(granger_tester=lambda a, b, l: 0.01, laplace_alpha=2.0)
        g2.register_event(_node("policy-a"))
        g2.register_event(_node("industry-b", EventType.INDUSTRY_DATA))
        g2.add_granger_edge("policy-a", "industry-b", lag=1, cause_series=_SERIES, effect_series=_SERIES)
        g2.record_outcome("policy-a", "industry-b", effect_occurred=True)
        # (1+2)/(1+4) = 3/5
        assert g2.probability("industry-b", given_cause_id="policy-a") == pytest.approx(0.6)
        assert g.node_count() == 2

    def test_unknown_edge_query_raises(self) -> None:
        g = self._graph_with_edge()
        with pytest.raises(EventChainError):
            g.probability("policy-a", given_cause_id="industry-b")  # 反向边不存在
        with pytest.raises(EventChainError):
            g.record_outcome("industry-b", "policy-a", effect_occurred=True)

    def test_cpt_view_sorted(self) -> None:
        g = _two_node_graph()
        g.register_event(_node("overseas-c", EventType.OVERSEAS))
        g.add_granger_edge("policy-a", "overseas-c", lag=1, cause_series=_SERIES, effect_series=_SERIES)
        g.add_granger_edge("policy-a", "industry-b", lag=1, cause_series=_SERIES, effect_series=_SERIES)
        table = g.cpt("policy-a")
        assert [e for e, _ in table] == ["industry-b", "overseas-c"]  # 确定性排序
        assert all(0.0 <= p <= 1.0 for _, p in table)
