# [BLUEPRINT] MOD-DATA_GOV-002 | (auto-injected by S4 reconciler) | §D-DATA-GOV
# [TTL] permanent
# [A_test] module_id: MOD-DATA_GOV-002 | layer=test | stability=volatile | safety=L
# [MODULE] tests.data_governance.test_lineage_tracker
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/data_governance/test_lineage_tracker.py
# [TTL] task_bound
"""D-DATA-GOV Lineage Tracker 测试。"""

from __future__ import annotations

import pytest

from zephyr.data_governance.core.lineage_tracker import (
    LineageEdge,
    LineageTracker,
)


class TestAddEdge:
    def test_add_simple_edge(self):
        tracker = LineageTracker()
        edge = tracker.add_edge("a", "b", "compute")
        assert isinstance(edge, LineageEdge)
        assert edge.source == "a"
        assert edge.target == "b"
        assert edge.transformation == "compute"

    def test_add_idempotent_updates(self):
        tracker = LineageTracker()
        tracker.add_edge("a", "b", "old")
        tracker.add_edge("a", "b", "new")
        edges = tracker.get_edges()
        assert len(edges) == 1
        assert edges[0].transformation == "new"

    def test_self_loop_rejected(self):
        tracker = LineageTracker()
        with pytest.raises(ValueError, match="自环"):
            tracker.add_edge("a", "a")

    def test_cycle_rejected(self):
        tracker = LineageTracker()
        tracker.add_edge("a", "b")
        tracker.add_edge("b", "c")
        with pytest.raises(ValueError, match="环"):
            tracker.add_edge("c", "a")


class TestUpstream:
    def test_direct_upstream(self):
        tracker = LineageTracker()
        tracker.add_edge("a", "c")
        tracker.add_edge("b", "c")
        upstream = tracker.get_direct_upstream("c")
        assert set(upstream) == {"a", "b"}

    def test_recursive_upstream(self):
        tracker = LineageTracker()
        tracker.add_edge("raw", "clean")
        tracker.add_edge("clean", "factor")
        tracker.add_edge("factor", "signal")
        upstream = tracker.get_upstream("signal")
        assert "factor" in upstream
        assert "clean" in upstream
        assert "raw" in upstream
        assert len(upstream) == 3

    def test_no_upstream(self):
        tracker = LineageTracker()
        tracker.add_edge("a", "b")
        assert tracker.get_upstream("a") == []
        assert tracker.get_upstream("unknown") == []


class TestDownstream:
    def test_direct_downstream(self):
        tracker = LineageTracker()
        tracker.add_edge("a", "b")
        tracker.add_edge("a", "c")
        downstream = tracker.get_direct_downstream("a")
        assert set(downstream) == {"b", "c"}

    def test_recursive_downstream(self):
        tracker = LineageTracker()
        tracker.add_edge("raw", "clean")
        tracker.add_edge("clean", "factor")
        tracker.add_edge("factor", "signal")
        downstream = tracker.get_downstream("raw")
        assert "clean" in downstream
        assert "factor" in downstream
        assert "signal" in downstream
        assert len(downstream) == 3

    def test_no_downstream(self):
        tracker = LineageTracker()
        tracker.add_edge("a", "b")
        assert tracker.get_downstream("b") == []
        assert tracker.get_downstream("unknown") == []


class TestNodesAndEdges:
    def test_get_nodes(self):
        tracker = LineageTracker()
        tracker.add_edge("a", "b")
        tracker.add_edge("b", "c")
        nodes = tracker.get_nodes()
        assert nodes == ["a", "b", "c"]

    def test_get_edges(self):
        tracker = LineageTracker()
        tracker.add_edge("a", "b", "compute")
        tracker.add_edge("b", "c", "aggregate")
        edges = tracker.get_edges()
        assert len(edges) == 2


class TestRealScenario:
    """模拟真实数据血缘：市场数据 → 因子 → 信号 → 策略 → 回测。"""

    def test_full_pipeline_lineage(self):
        tracker = LineageTracker()
        tracker.add_edge("market.kline_daily", "factor.momentum_20d", "compute")
        tracker.add_edge("market.kline_daily", "factor.value_factor", "compute")
        tracker.add_edge("factor.momentum_20d", "signal.alpha", "generate")
        tracker.add_edge("factor.value_factor", "signal.alpha", "generate")
        tracker.add_edge("signal.alpha", "strategy.default", "backtest")

        # signal.alpha 的上游应包含 2 个因子 + 1 个市场数据
        upstream = tracker.get_upstream("signal.alpha")
        assert "factor.momentum_20d" in upstream
        assert "factor.value_factor" in upstream
        assert "market.kline_daily" in upstream

        # market.kline_daily 的下游应包含因子+信号+策略
        downstream = tracker.get_downstream("market.kline_daily")
        assert "factor.momentum_20d" in downstream
        assert "signal.alpha" in downstream
        assert "strategy.default" in downstream
