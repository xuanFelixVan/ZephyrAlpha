# [BLUEPRINT] MOD-GOV-053 | docs/03_modules/_domain_gov_audit/audit_trace_graph_builder/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-GOV-053 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.gov_audit.test_audit_trace_graph_builder
# [TESTS] src/zephyr/gov_audit/audit_trace_graph_builder.py
"""MOD-GOV-053 单元测试：audit_trace_graph_builder 审计追踪依赖构建器。

蓝图验收（B14-04667/CAND-GOVAUDIT-004，A9 M48-S01）：
决策→代码→测试→部署四段全链边登记（段词表闭合）+ 全链反查 +
缺口自动检测（缺段/断链清单）+ 补齐建议输出。
纯内存图，不触库不触网。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.gov_audit.audit_trace_graph_builder",
    reason="audit_trace_graph_builder not importable",
)

from zephyr.gov_audit.audit_trace_graph_builder import (  # noqa: E402
    AuditTraceError,
    AuditTraceGraphBuilder,
    GapKind,
    TraceSegment,
)


def _full_chain(builder: AuditTraceGraphBuilder, prefix: str = "") -> None:
    """登记一条 decision→code→test→deploy 完整链。"""
    builder.register_node(f"{prefix}d1", TraceSegment.DECISION, "决策")
    builder.register_node(f"{prefix}c1", TraceSegment.CODE, "代码")
    builder.register_node(f"{prefix}t1", TraceSegment.TEST, "测试")
    builder.register_node(f"{prefix}p1", TraceSegment.DEPLOY, "部署")
    builder.register_edge(f"{prefix}d1", f"{prefix}c1")
    builder.register_edge(f"{prefix}c1", f"{prefix}t1")
    builder.register_edge(f"{prefix}t1", f"{prefix}p1")


# ──────────────────────────────────────────────────────────────────────────────
# 节点登记（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterNode:
    def test_register_ok(self) -> None:
        builder = AuditTraceGraphBuilder()
        builder.register_node("d1", TraceSegment.DECISION, "风控决策")
        nodes = builder.nodes()
        assert len(nodes) == 1
        assert nodes[0].node_id == "d1"
        assert nodes[0].segment is TraceSegment.DECISION
        assert nodes[0].label == "风控决策"

    def test_empty_node_id_raises(self) -> None:
        with pytest.raises(AuditTraceError):
            AuditTraceGraphBuilder().register_node("", TraceSegment.DECISION)

    def test_invalid_segment_raises(self) -> None:
        with pytest.raises(AuditTraceError):
            AuditTraceGraphBuilder().register_node("d1", "decision")

    def test_duplicate_node_raises(self) -> None:
        builder = AuditTraceGraphBuilder()
        builder.register_node("d1", TraceSegment.DECISION)
        with pytest.raises(AuditTraceError):
            builder.register_node("d1", TraceSegment.CODE)

    def test_nodes_sorted_by_segment_then_id(self) -> None:
        builder = AuditTraceGraphBuilder()
        builder.register_node("p1", TraceSegment.DEPLOY)
        builder.register_node("d2", TraceSegment.DECISION)
        builder.register_node("d1", TraceSegment.DECISION)
        builder.register_node("c1", TraceSegment.CODE)
        assert [n.node_id for n in builder.nodes()] == ["d1", "d2", "c1", "p1"]


# ──────────────────────────────────────────────────────────────────────────────
# 边登记（相邻段向下）
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterEdge:
    def test_adjacent_edges_ok(self) -> None:
        builder = AuditTraceGraphBuilder()
        _full_chain(builder)
        assert [(e.src_id, e.dst_id) for e in builder.edges()] == [
            ("c1", "t1"), ("d1", "c1"), ("t1", "p1"),
        ]

    def test_skip_segment_rejected(self) -> None:
        builder = AuditTraceGraphBuilder()
        builder.register_node("d1", TraceSegment.DECISION)
        builder.register_node("t1", TraceSegment.TEST)
        with pytest.raises(AuditTraceError):
            builder.register_edge("d1", "t1")  # 越段 decision→test

    def test_reverse_edge_rejected(self) -> None:
        builder = AuditTraceGraphBuilder()
        builder.register_node("d1", TraceSegment.DECISION)
        builder.register_node("c1", TraceSegment.CODE)
        with pytest.raises(AuditTraceError):
            builder.register_edge("c1", "d1")  # 逆向 code→decision

    def test_same_segment_rejected(self) -> None:
        builder = AuditTraceGraphBuilder()
        builder.register_node("c1", TraceSegment.CODE)
        builder.register_node("c2", TraceSegment.CODE)
        with pytest.raises(AuditTraceError):
            builder.register_edge("c1", "c2")

    def test_self_loop_rejected(self) -> None:
        builder = AuditTraceGraphBuilder()
        builder.register_node("d1", TraceSegment.DECISION)
        with pytest.raises(AuditTraceError):
            builder.register_edge("d1", "d1")

    def test_unknown_endpoint_raises(self) -> None:
        builder = AuditTraceGraphBuilder()
        builder.register_node("d1", TraceSegment.DECISION)
        with pytest.raises(AuditTraceError):
            builder.register_edge("d1", "ghost")
        with pytest.raises(AuditTraceError):
            builder.register_edge("ghost", "d1")

    def test_duplicate_edge_idempotent(self) -> None:
        builder = AuditTraceGraphBuilder()
        builder.register_node("d1", TraceSegment.DECISION)
        builder.register_node("c1", TraceSegment.CODE)
        builder.register_edge("d1", "c1")
        builder.register_edge("d1", "c1")  # 幂等不抛
        assert len(builder.edges()) == 1


# ──────────────────────────────────────────────────────────────────────────────
# 全链反查
# ──────────────────────────────────────────────────────────────────────────────


class TestChainQuery:
    def test_chain_of_full_from_any_node(self) -> None:
        builder = AuditTraceGraphBuilder()
        _full_chain(builder)
        for node_id in ("d1", "c1", "t1", "p1"):
            assert [n.node_id for n in builder.chain_of(node_id)] == [
                "d1", "c1", "t1", "p1",
            ]

    def test_chain_of_unknown_raises(self) -> None:
        with pytest.raises(AuditTraceError):
            AuditTraceGraphBuilder().chain_of("ghost")

    def test_chain_of_partial(self) -> None:
        builder = AuditTraceGraphBuilder()
        builder.register_node("d1", TraceSegment.DECISION)
        builder.register_node("c1", TraceSegment.CODE)
        builder.register_edge("d1", "c1")
        assert [n.node_id for n in builder.chain_of("c1")] == ["d1", "c1"]

    def test_reachable_segments(self) -> None:
        builder = AuditTraceGraphBuilder()
        _full_chain(builder)
        assert builder.reachable_segments("d1") == (
            TraceSegment.CODE, TraceSegment.TEST, TraceSegment.DEPLOY,
        )
        assert builder.reachable_segments("t1") == (TraceSegment.DEPLOY,)
        assert builder.reachable_segments("p1") == ()

    def test_fan_out_chain_branch_isolated(self) -> None:
        builder = AuditTraceGraphBuilder()
        _full_chain(builder)
        builder.register_node("c2", TraceSegment.CODE)
        builder.register_edge("d1", "c2")  # 一决策对两代码
        # c2 分支：祖先 ∪ 后代，不含兄弟 c1 的下游子树
        assert [n.node_id for n in builder.chain_of("c2")] == ["d1", "c2"]
        # c1 分支仍完整到 deploy
        assert [n.node_id for n in builder.chain_of("c1")] == [
            "d1", "c1", "t1", "p1",
        ]


# ──────────────────────────────────────────────────────────────────────────────
# 缺口检测 / 补齐建议
# ──────────────────────────────────────────────────────────────────────────────


class TestGapReport:
    def test_full_chain_no_gap(self) -> None:
        builder = AuditTraceGraphBuilder()
        _full_chain(builder)
        report = builder.gap_report()
        assert report.gaps == ()
        assert report.suggestions == ()

    def test_empty_graph_no_gap(self) -> None:
        report = AuditTraceGraphBuilder().gap_report()
        assert report.gaps == ()

    def test_lonely_decision_missing_all_segments(self) -> None:
        builder = AuditTraceGraphBuilder()
        builder.register_node("d1", TraceSegment.DECISION)
        report = builder.gap_report()
        missing = [g for g in report.gaps if g.kind is GapKind.MISSING_SEGMENT]
        assert [g.segment for g in missing] == [
            TraceSegment.CODE, TraceSegment.TEST, TraceSegment.DEPLOY,
        ]
        broken = [g for g in report.gaps if g.kind is GapKind.BROKEN_LINK]
        assert len(broken) == 1  # d1 无 code 出边
        assert len(report.gaps) == len(report.suggestions)

    def test_broken_link_no_incoming(self) -> None:
        builder = AuditTraceGraphBuilder()
        _full_chain(builder)
        builder.register_node("t9", TraceSegment.TEST)  # 孤儿 test 节点
        report = builder.gap_report()
        broken = [g for g in report.gaps if g.kind is GapKind.BROKEN_LINK]
        assert any(g.node_id == "t9" and "入边" in g.detail for g in broken)
        assert any(g.node_id == "t9" and "出边" in g.detail for g in broken)

    def test_missing_segment_partial_chain(self) -> None:
        builder = AuditTraceGraphBuilder()
        builder.register_node("d1", TraceSegment.DECISION)
        builder.register_node("c1", TraceSegment.CODE)
        builder.register_edge("d1", "c1")
        report = builder.gap_report()
        missing = {g.segment for g in report.gaps if g.kind is GapKind.MISSING_SEGMENT}
        assert missing == {TraceSegment.TEST, TraceSegment.DEPLOY}

    def test_suggestions_actionable(self) -> None:
        builder = AuditTraceGraphBuilder()
        builder.register_node("d1", TraceSegment.DECISION)
        report = builder.gap_report()
        assert any("补齐" in s and "code" in s for s in report.suggestions)
        assert any("下游边" in s for s in report.suggestions)

    def test_determinism_same_input_same_output(self) -> None:
        def _run() -> tuple:
            builder = AuditTraceGraphBuilder()
            _full_chain(builder, "a_")
            _full_chain(builder, "b_")
            builder.register_node("x1", TraceSegment.CODE)
            report = builder.gap_report()
            return (
                tuple((g.kind, g.node_id, g.segment, g.detail) for g in report.gaps),
                report.suggestions,
            )

        assert _run() == _run()
