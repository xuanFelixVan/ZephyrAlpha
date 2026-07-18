# [A_test] module_id: SRC-TST-2040 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-657 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_kg_interface
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
import pytest

from zephyr.shared.knowledge.kg_interface import (
    InMemoryKnowledgeGraph,
    KGEntity,
    KGRelation,
    KnowledgeGraphInterface,
    create_knowledge_graph,
)


def _make_entity(eid: str, etype: str = "concept", name: str = "") -> KGEntity:
    return KGEntity(entity_id=eid, entity_type=etype, name=name or eid)


def _make_rel(rid: str, src: str, tgt: str, rtype: str = "related_to") -> KGRelation:
    return KGRelation(relation_id=rid, source_id=src, target_id=tgt, relation_type=rtype)


class TestKGEntity:
    def test_frozen(self):
        e = _make_entity("e1")
        with pytest.raises(AttributeError):
            e.entity_id = "e2"

    def test_default_timestamp(self):
        e = _make_entity("e1")
        assert e.created_at
        assert "T" in e.created_at


class TestKGRelation:
    def test_frozen(self):
        r = _make_rel("r1", "a", "b")
        with pytest.raises(AttributeError):
            r.relation_type = "x"

    def test_default_timestamp(self):
        r = _make_rel("r1", "a", "b")
        assert r.created_at


class TestInMemoryKnowledgeGraph:
    def test_protocol_conformance(self):
        kg = InMemoryKnowledgeGraph()
        assert isinstance(kg, KnowledgeGraphInterface)

    def test_add_and_get_entity(self):
        kg = InMemoryKnowledgeGraph()
        e = _make_entity("e1", "rule", "Rule A")
        eid = kg.add_entity(e)
        assert eid == "e1"
        got = kg.get_entity("e1")
        assert got is not None
        assert got.name == "Rule A"

    def test_get_entity_not_found(self):
        kg = InMemoryKnowledgeGraph()
        assert kg.get_entity("missing") is None

    def test_add_entity_idempotent(self):
        kg = InMemoryKnowledgeGraph()
        kg.add_entity(_make_entity("e1"))
        kg.add_entity(_make_entity("e1"))
        assert kg.stats()["entities"] == 1

    def test_add_and_get_relation(self):
        kg = InMemoryKnowledgeGraph()
        kg.add_entity(_make_entity("a"))
        kg.add_entity(_make_entity("b"))
        rid = kg.add_relation(_make_rel("r1", "a", "b", "depends_on"))
        assert rid == "r1"
        rels = kg.get_relations("a", "outgoing")
        assert len(rels) == 1
        assert rels[0].relation_type == "depends_on"

    def test_add_relation_auto_id(self):
        kg = InMemoryKnowledgeGraph()
        kg.add_entity(_make_entity("a"))
        kg.add_entity(_make_entity("b"))
        rid = kg.add_relation(KGRelation(relation_id="", source_id="a", target_id="b", relation_type="links"))
        assert rid.startswith("rel-")

    def test_get_relations_incoming(self):
        kg = InMemoryKnowledgeGraph()
        kg.add_entity(_make_entity("a"))
        kg.add_entity(_make_entity("b"))
        kg.add_relation(_make_rel("r1", "a", "b"))
        rels = kg.get_relations("b", "incoming")
        assert len(rels) == 1
        rels = kg.get_relations("b", "outgoing")
        assert len(rels) == 0

    def test_get_relations_both(self):
        kg = InMemoryKnowledgeGraph()
        kg.add_entity(_make_entity("a"))
        kg.add_entity(_make_entity("b"))
        kg.add_entity(_make_entity("c"))
        kg.add_relation(_make_rel("r1", "a", "b"))
        kg.add_relation(_make_rel("r2", "c", "a"))
        rels = kg.get_relations("a", "both")
        assert len(rels) == 2

    def test_query_path_simple(self):
        kg = InMemoryKnowledgeGraph()
        kg.add_entity(_make_entity("a"))
        kg.add_entity(_make_entity("b"))
        kg.add_entity(_make_entity("c"))
        kg.add_relation(_make_rel("r1", "a", "b"))
        kg.add_relation(_make_rel("r2", "b", "c"))
        path = kg.query_path("a", "c")
        assert len(path.nodes) == 3
        assert path.nodes[0].entity_id == "a"
        assert path.nodes[-1].entity_id == "c"
        assert len(path.edges) == 2

    def test_query_path_no_path(self):
        kg = InMemoryKnowledgeGraph()
        kg.add_entity(_make_entity("a"))
        kg.add_entity(_make_entity("b"))
        path = kg.query_path("a", "b")
        assert len(path.nodes) == 0

    def test_query_path_missing_entity(self):
        kg = InMemoryKnowledgeGraph()
        path = kg.query_path("x", "y")
        assert len(path.nodes) == 0

    def test_query_path_max_depth(self):
        kg = InMemoryKnowledgeGraph()
        for i in range(10):
            kg.add_entity(_make_entity(f"e{i}"))
            if i > 0:
                kg.add_relation(_make_rel(f"r{i}", f"e{i - 1}", f"e{i}"))
        path = kg.query_path("e0", "e9", max_depth=3)
        assert len(path.nodes) == 0

    def test_query_subgraph(self):
        kg = InMemoryKnowledgeGraph()
        kg.add_entity(_make_entity("center"))
        kg.add_entity(_make_entity("n1"))
        kg.add_entity(_make_entity("n2"))
        kg.add_relation(_make_rel("r1", "center", "n1"))
        kg.add_relation(_make_rel("r2", "center", "n2"))
        sg = kg.query_subgraph("center", depth=1)
        assert len(sg.entities) == 3
        assert len(sg.relations) == 2
        assert sg.depth == 1

    def test_query_subgraph_depth_2(self):
        kg = InMemoryKnowledgeGraph()
        kg.add_entity(_make_entity("c"))
        kg.add_entity(_make_entity("l1"))
        kg.add_entity(_make_entity("l2"))
        kg.add_relation(_make_rel("r1", "c", "l1"))
        kg.add_relation(_make_rel("r2", "l1", "l2"))
        sg = kg.query_subgraph("c", depth=2)
        assert len(sg.entities) == 3
        assert len(sg.relations) == 2

    def test_query_subgraph_missing(self):
        kg = InMemoryKnowledgeGraph()
        sg = kg.query_subgraph("missing")
        assert len(sg.entities) == 0

    def test_remove_entity(self):
        kg = InMemoryKnowledgeGraph()
        kg.add_entity(_make_entity("e1"))
        kg.add_entity(_make_entity("e2"))
        kg.add_relation(_make_rel("r1", "e1", "e2"))
        assert kg.remove_entity("e1")
        assert kg.get_entity("e1") is None
        assert len(kg.get_relations("e2", "incoming")) == 0

    def test_remove_entity_not_found(self):
        kg = InMemoryKnowledgeGraph()
        assert kg.remove_entity("missing") is False

    def test_remove_relation(self):
        kg = InMemoryKnowledgeGraph()
        kg.add_entity(_make_entity("a"))
        kg.add_entity(_make_entity("b"))
        kg.add_relation(_make_rel("r1", "a", "b"))
        assert kg.remove_relation("r1")
        assert len(kg.get_relations("a", "outgoing")) == 0

    def test_remove_relation_not_found(self):
        kg = InMemoryKnowledgeGraph()
        assert kg.remove_relation("missing") is False

    def test_stats(self):
        kg = InMemoryKnowledgeGraph()
        kg.add_entity(_make_entity("e1"))
        kg.add_entity(_make_entity("e2"))
        kg.add_relation(_make_rel("r1", "e1", "e2"))
        s = kg.stats()
        assert s["entities"] == 2
        assert s["relations"] == 1

    def test_thread_safety(self):
        import threading

        kg = InMemoryKnowledgeGraph()
        errors: list[str] = []

        def writer(start: int) -> None:
            try:
                for i in range(50):
                    kg.add_entity(_make_entity(f"e{start + i}"))
            except Exception as exc:
                errors.append(str(exc))

        threads = [threading.Thread(target=writer, args=(t * 50,)) for t in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        assert kg.stats()["entities"] == 200


class TestCreateKnowledgeGraph:
    def test_memory_backend(self):
        kg = create_knowledge_graph("memory")
        assert isinstance(kg, InMemoryKnowledgeGraph)

    def test_unknown_backend(self):
        with pytest.raises(ValueError, match="Unknown KG backend"):
            create_knowledge_graph("neo4j")
