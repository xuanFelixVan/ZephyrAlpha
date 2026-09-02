# [BLUEPRINT] MOD-KNW-003 | docs/03_modules/_domain_knowledge/financial_knowledge_graph/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-KNW-003 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.knowledge.test_financial_knowledge_graph
# [TESTS] src/zephyr/knowledge/financial_knowledge_graph.py
"""MOD-KNW-003 单元测试：financial_knowledge_graph 金融知识图谱。

蓝图验收（B1-00126/CAND-KNW-001，C2 D-KNOW-01）：
六类实体词表闭合 + 关系表（类型/权重/属性JSON）+ 增删查 + N跳子图抽取 +
BFS最短路径 + LLM抽取pending_review状态机 + 百万边护栏。真:memory: sqlite，不触网。
"""

from __future__ import annotations

import datetime
import sqlite3

import pytest

pytest.importorskip(
    "zephyr.knowledge.financial_knowledge_graph",
    reason="financial_knowledge_graph not importable",
)

from zephyr.knowledge.financial_knowledge_graph import (  # noqa: E402
    EntityType,
    FinancialGraphError,
    FinancialKnowledgeGraph,
    ReviewStatus,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _graph(**kwargs) -> FinancialKnowledgeGraph:
    return FinancialKnowledgeGraph(conn=sqlite3.connect(":memory:"), clock=lambda: _T0, **kwargs)


def _seed_chain(graph: FinancialKnowledgeGraph) -> None:
    """A -> B -> C 链 + A -> D，用于遍历/路径测试。"""
    graph.add_entity("A", EntityType.COMPANY, "甲公司")
    graph.add_entity("B", EntityType.COMPANY, "乙公司")
    graph.add_entity("C", EntityType.INDUSTRY, "半导体")
    graph.add_entity("D", EntityType.CONCEPT, "国产替代")
    graph.add_edge("A", "B", "supplies_to", 0.9, attrs={"since": 2024})
    graph.add_edge("B", "C", "belongs_to", 1.0)
    graph.add_edge("A", "D", "tagged_with", 0.5)


# ──────────────────────────────────────────────────────────────────────────────
# 构造 / 词表（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_ok(self) -> None:
        graph = _graph()
        assert graph.entity_count() == 0
        assert graph.edge_count() == 0

    def test_conn_missing_raises(self) -> None:
        with pytest.raises(FinancialGraphError):
            FinancialKnowledgeGraph(conn=None)  # type: ignore[arg-type]

    def test_empty_relation_vocab_raises(self) -> None:
        with pytest.raises(FinancialGraphError):
            FinancialKnowledgeGraph(conn=sqlite3.connect(":memory:"), relation_types=())

    def test_duplicate_relation_vocab_raises(self) -> None:
        with pytest.raises(FinancialGraphError):
            FinancialKnowledgeGraph(conn=sqlite3.connect(":memory:"), relation_types=("x", "x"))

    def test_bad_max_edges_raises(self) -> None:
        with pytest.raises(FinancialGraphError):
            _graph(max_edges=0)


# ──────────────────────────────────────────────────────────────────────────────
# 实体 / 关系增删查
# ──────────────────────────────────────────────────────────────────────────────


class TestCrud:
    def test_add_six_entity_types(self) -> None:
        graph = _graph()
        for i, etype in enumerate(EntityType):
            graph.add_entity(f"e{i}", etype, f"名称{i}")
        assert graph.entity_count() == 6
        assert graph.get_entity("e2").entity_type is EntityType.SUPPLY_CHAIN

    def test_add_entity_bad_type_raises(self) -> None:
        graph = _graph()
        with pytest.raises(FinancialGraphError):
            graph.add_entity("e1", "ghost_type", "x")  # type: ignore[arg-type]

    def test_add_entity_duplicate_raises(self) -> None:
        graph = _graph()
        graph.add_entity("e1", EntityType.COMPANY, "x")
        with pytest.raises(FinancialGraphError):
            graph.add_entity("e1", EntityType.COMPANY, "y")

    def test_add_entity_blank_fields_raise(self) -> None:
        graph = _graph()
        with pytest.raises(FinancialGraphError):
            graph.add_entity("", EntityType.COMPANY, "x")
        with pytest.raises(FinancialGraphError):
            graph.add_entity("e1", EntityType.COMPANY, "")

    def test_add_edge_ok_with_attrs_json(self) -> None:
        graph = _graph()
        _seed_chain(graph)
        edge = graph.neighbors("A")[0]
        assert edge.attrs == {"since": 2024}  # 属性 JSON 往返
        assert graph.edge_count() == 3

    def test_add_edge_unknown_rel_type_raises(self) -> None:
        graph = _graph()
        _seed_chain(graph)
        with pytest.raises(FinancialGraphError):
            graph.add_edge("A", "B", "ghost_rel", 0.5)

    def test_add_edge_weight_out_of_range_raises(self) -> None:
        graph = _graph()
        _seed_chain(graph)
        with pytest.raises(FinancialGraphError):
            graph.add_edge("A", "B", "holds", 0.0)
        with pytest.raises(FinancialGraphError):
            graph.add_edge("A", "B", "holds", 1.1)

    def test_add_edge_unknown_entity_raises(self) -> None:
        graph = _graph()
        graph.add_entity("A", EntityType.COMPANY, "x")
        with pytest.raises(FinancialGraphError):
            graph.add_edge("A", "ghost", "holds", 0.5)

    def test_add_edge_duplicate_raises(self) -> None:
        graph = _graph()
        _seed_chain(graph)
        with pytest.raises(FinancialGraphError):
            graph.add_edge("A", "B", "supplies_to", 0.8)

    def test_remove_edge_ok_and_unknown_raises(self) -> None:
        graph = _graph()
        _seed_chain(graph)
        graph.remove_edge("A", "D", "tagged_with")
        assert graph.edge_count() == 2
        with pytest.raises(FinancialGraphError):
            graph.remove_edge("A", "D", "tagged_with")

    def test_remove_entity_cascades_edges(self) -> None:
        graph = _graph()
        _seed_chain(graph)
        graph.remove_entity("A")
        assert graph.entity_count() == 3
        assert graph.edge_count() == 1  # 仅剩 B->C

    def test_neighbors_sorted(self) -> None:
        graph = _graph()
        _seed_chain(graph)
        assert [(e.dst, e.rel_type) for e in graph.neighbors("A")] == [
            ("B", "supplies_to"),
            ("D", "tagged_with"),
        ]


# ──────────────────────────────────────────────────────────────────────────────
# 子图 / 最短路径
# ──────────────────────────────────────────────────────────────────────────────


class TestTraversal:
    def test_subgraph_one_hop(self) -> None:
        graph = _graph()
        _seed_chain(graph)
        sub = graph.subgraph("A", 1)
        assert [e.entity_id for e in sub.entities] == ["A", "B", "D"]

    def test_subgraph_two_hops(self) -> None:
        graph = _graph()
        _seed_chain(graph)
        sub = graph.subgraph("A", 2)
        assert [e.entity_id for e in sub.entities] == ["A", "B", "C", "D"]
        assert [(e.src, e.dst) for e in sub.edges] == [("A", "B"), ("A", "D"), ("B", "C")]

    def test_subgraph_bad_hops_raises(self) -> None:
        graph = _graph()
        _seed_chain(graph)
        with pytest.raises(FinancialGraphError):
            graph.subgraph("A", 0)

    def test_subgraph_unknown_entity_raises(self) -> None:
        graph = _graph()
        with pytest.raises(FinancialGraphError):
            graph.subgraph("ghost", 1)

    def test_shortest_path_direct(self) -> None:
        graph = _graph()
        _seed_chain(graph)
        assert graph.shortest_path("A", "C") == ("A", "B", "C")

    def test_shortest_path_unreachable_returns_none(self) -> None:
        graph = _graph()
        _seed_chain(graph)
        assert graph.shortest_path("C", "A") is None  # 出向不可达

    def test_shortest_path_self(self) -> None:
        graph = _graph()
        _seed_chain(graph)
        assert graph.shortest_path("A", "A") == ("A",)

    def test_shortest_path_unknown_raises(self) -> None:
        graph = _graph()
        with pytest.raises(FinancialGraphError):
            graph.shortest_path("A", "ghost")


# ──────────────────────────────────────────────────────────────────────────────
# LLM 抽取审核状态机
# ──────────────────────────────────────────────────────────────────────────────


class TestExtractionReview:
    def _submit(self, graph: FinancialKnowledgeGraph) -> str:
        graph.add_entity("A", EntityType.COMPANY, "甲公司")
        return graph.submit_extraction(
            entities=[{"entity_id": "E1", "entity_type": "event", "name": "扩产公告"}],
            edges=[{"src": "A", "dst": "E1", "rel_type": "triggers", "weight": 0.7}],
        )

    def test_pending_invisible_until_approved(self) -> None:
        graph = _graph()
        sub_id = self._submit(graph)
        assert sub_id == "sub-000001"
        assert graph.entity_count() == 1  # pending 不入图
        assert graph.edge_count() == 0
        with pytest.raises(FinancialGraphError):
            graph.get_entity("E1")
        pending = graph.pending_submissions()
        assert len(pending) == 1
        assert pending[0].status is ReviewStatus.PENDING
        assert pending[0].submitted_at == _T0

    def test_approve_makes_visible(self) -> None:
        graph = _graph()
        sub_id = self._submit(graph)
        graph.approve_extraction(sub_id)
        assert graph.entity_count() == 2
        assert graph.edge_count() == 1
        assert graph.get_entity("E1").entity_type is EntityType.EVENT
        assert graph.pending_submissions() == ()

    def test_reject_keeps_invisible(self) -> None:
        graph = _graph()
        sub_id = self._submit(graph)
        graph.reject_extraction(sub_id)
        assert graph.entity_count() == 1
        assert graph.edge_count() == 0

    def test_double_transition_raises(self) -> None:
        graph = _graph()
        sub_id = self._submit(graph)
        graph.approve_extraction(sub_id)
        with pytest.raises(FinancialGraphError):
            graph.approve_extraction(sub_id)
        with pytest.raises(FinancialGraphError):
            graph.reject_extraction(sub_id)

    def test_unknown_submission_raises(self) -> None:
        graph = _graph()
        with pytest.raises(FinancialGraphError):
            graph.approve_extraction("sub-999999")

    def test_empty_batch_raises(self) -> None:
        graph = _graph()
        with pytest.raises(FinancialGraphError):
            graph.submit_extraction()

    def test_batch_with_bad_edge_raises(self) -> None:
        graph = _graph()
        graph.add_entity("A", EntityType.COMPANY, "x")
        with pytest.raises(FinancialGraphError):
            graph.submit_extraction(edges=[{"src": "A", "dst": "ghost", "rel_type": "holds", "weight": 0.5}])

    def test_fifo_order(self) -> None:
        graph = _graph()
        graph.add_entity("A", EntityType.COMPANY, "x")
        s1 = graph.submit_extraction(entities=[{"entity_id": "E1", "entity_type": "event", "name": "事件一"}])
        s2 = graph.submit_extraction(entities=[{"entity_id": "E2", "entity_type": "event", "name": "事件二"}])
        assert [s.submission_id for s in graph.pending_submissions()] == [s1, s2]


# ──────────────────────────────────────────────────────────────────────────────
# 护栏 + 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestGuardAndDeterminism:
    def test_edge_capacity_guard(self) -> None:
        graph = _graph(max_edges=1)
        _seed_chain_entities_only(graph)
        graph.add_edge("A", "B", "holds", 0.5)
        with pytest.raises(FinancialGraphError):
            graph.add_edge("B", "C", "holds", 0.5)

    def test_determinism_same_input_same_output(self) -> None:
        def _run() -> list:
            graph = _graph()
            _seed_chain(graph)
            sub = graph.subgraph("A", 2)
            return [
                [e.entity_id for e in sub.entities],
                [(e.src, e.dst, e.rel_type, e.weight) for e in sub.edges],
                graph.shortest_path("A", "C"),
                [(e.dst, e.rel_type) for e in graph.neighbors("A")],
            ]

        assert _run() == _run()


def _seed_chain_entities_only(graph: FinancialKnowledgeGraph) -> None:
    graph.add_entity("A", EntityType.COMPANY, "甲")
    graph.add_entity("B", EntityType.COMPANY, "乙")
    graph.add_entity("C", EntityType.INDUSTRY, "丙")
