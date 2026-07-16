# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.shared.knowledge.kg_interface
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS] tests
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/kb/test_kg_interface.py
# [A_module] module_id=MOD-INT_kg_interface | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import threading
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class KGEntity:
    entity_id: str
    entity_type: str = "concept"
    name: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass(frozen=True)
class KGRelation:
    relation_id: str
    source_id: str
    target_id: str
    relation_type: str = "related_to"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class KGPath:
    nodes: list[KGEntity] = field(default_factory=list)
    edges: list[KGRelation] = field(default_factory=list)


@dataclass
class KGSubgraph:
    entities: list[KGEntity] = field(default_factory=list)
    relations: list[KGRelation] = field(default_factory=list)
    depth: int = 0


@runtime_checkable
class KnowledgeGraphInterface(Protocol):
    def add_entity(self, entity: KGEntity) -> str: ...
    def get_entity(self, entity_id: str) -> KGEntity | None: ...
    def add_relation(self, relation: KGRelation) -> str: ...
    def get_relations(self, entity_id: str, direction: str = "outgoing") -> list[KGRelation]: ...
    def remove_entity(self, entity_id: str) -> bool: ...
    def remove_relation(self, relation_id: str) -> bool: ...
    def query_path(self, from_id: str, to_id: str, max_depth: int = 5) -> KGPath: ...
    def query_subgraph(self, center_id: str, depth: int = 1) -> KGSubgraph: ...
    def stats(self) -> dict[str, int]: ...


def _expand_subgraph_frontier(
    frontier: set[str],
    entity_ids: set[str],
    relation_ids: set[str],
    outgoing: dict[str, list[str]],
    incoming: dict[str, list[str]],
    relations: dict[str, KGRelation],
) -> set[str]:
    next_frontier: set[str] = set()
    for eid in frontier:
        for rid in outgoing.get(eid, []):
            rel = relations.get(rid)
            if rel and rel.target_id not in entity_ids:
                next_frontier.add(rel.target_id)
                relation_ids.add(rid)
        for rid in incoming.get(eid, []):
            rel = relations.get(rid)
            if rel and rel.source_id not in entity_ids:
                next_frontier.add(rel.source_id)
                relation_ids.add(rid)
    return next_frontier


class InMemoryKnowledgeGraph:
    def __init__(self) -> None:
        self._entities: dict[str, KGEntity] = {}
        self._relations: dict[str, KGRelation] = {}
        self._outgoing: dict[str, list[str]] = {}
        self._incoming: dict[str, list[str]] = {}
        self._lock = threading.Lock()

    def add_entity(self, entity: KGEntity) -> str:
        with self._lock:
            self._entities[entity.entity_id] = entity
            if entity.entity_id not in self._outgoing:
                self._outgoing[entity.entity_id] = []
            if entity.entity_id not in self._incoming:
                self._incoming[entity.entity_id] = []
            return entity.entity_id

    def get_entity(self, entity_id: str) -> KGEntity | None:
        with self._lock:
            return self._entities.get(entity_id)

    def add_relation(self, relation: KGRelation) -> str:
        with self._lock:
            rid = relation.relation_id
            if not rid:
                rid = f"rel-{uuid.uuid4().hex[:8]}"
                relation = KGRelation(
                    relation_id=rid,
                    source_id=relation.source_id,
                    target_id=relation.target_id,
                    relation_type=relation.relation_type,
                    created_at=relation.created_at,
                )
            self._relations[rid] = relation
            self._outgoing.setdefault(relation.source_id, []).append(rid)
            self._incoming.setdefault(relation.target_id, []).append(rid)
            return rid

    def get_relations(self, entity_id: str, direction: str = "outgoing") -> list[KGRelation]:
        with self._lock:
            result: list[KGRelation] = []
            if direction in ("outgoing", "both"):
                for rid in self._outgoing.get(entity_id, []):
                    if rid in self._relations:
                        result.append(self._relations[rid])
            if direction in ("incoming", "both"):
                for rid in self._incoming.get(entity_id, []):
                    if rid in self._relations:
                        result.append(self._relations[rid])
            return result

    def remove_entity(self, entity_id: str) -> bool:
        with self._lock:
            if entity_id not in self._entities:
                return False
            del self._entities[entity_id]
            rels_to_remove: list[str] = []
            for rid in list(self._outgoing.get(entity_id, [])):
                rels_to_remove.append(rid)
            for rid in list(self._incoming.get(entity_id, [])):
                rels_to_remove.append(rid)
            for rid in set(rels_to_remove):
                self._remove_relation_internal(rid)
            self._outgoing.pop(entity_id, None)
            self._incoming.pop(entity_id, None)
            return True

    def remove_relation(self, relation_id: str) -> bool:
        with self._lock:
            return self._remove_relation_internal(relation_id)

    def _remove_relation_internal(self, relation_id: str) -> bool:
        rel = self._relations.pop(relation_id, None)
        if rel is None:
            return False
        if relation_id in self._outgoing.get(rel.source_id, []):
            self._outgoing[rel.source_id].remove(relation_id)
        if relation_id in self._incoming.get(rel.target_id, []):
            self._incoming[rel.target_id].remove(relation_id)
        return True

    def query_path(self, from_id: str, to_id: str, max_depth: int = 5) -> KGPath:
        with self._lock:
            if from_id not in self._entities or to_id not in self._entities:
                return KGPath()
            if from_id == to_id:
                return KGPath(nodes=[self._entities[from_id]])

            visited: set[str] = {from_id}
            queue: deque[tuple[str, list[str], list[str]]] = deque([(from_id, [from_id], [])])

            while queue:
                current, path_entities, path_rels = queue.popleft()
                if len(path_entities) - 1 >= max_depth:
                    continue
                for rid in self._outgoing.get(current, []):
                    rel = self._relations.get(rid)
                    if rel is None:
                        continue
                    next_id = rel.target_id
                    if next_id in visited:
                        continue
                    visited.add(next_id)
                    new_entities = path_entities + [next_id]
                    new_rels = path_rels + [rid]
                    if next_id == to_id:
                        nodes = [self._entities[eid] for eid in new_entities if eid in self._entities]
                        edges = [self._relations[rid] for rid in new_rels if rid in self._relations]
                        return KGPath(nodes=nodes, edges=edges)
                    queue.append((next_id, new_entities, new_rels))

            return KGPath()

    def query_subgraph(self, center_id: str, depth: int = 1) -> KGSubgraph:
        with self._lock:
            if center_id not in self._entities:
                return KGSubgraph()

            entity_ids: set[str] = {center_id}
            relation_ids: set[str] = set()
            frontier: set[str] = {center_id}

            for _ in range(depth):
                next_frontier = _expand_subgraph_frontier(
                    frontier, entity_ids, relation_ids, self._outgoing, self._incoming, self._relations
                )
                entity_ids.update(next_frontier)
                frontier = next_frontier

            for eid in entity_ids:
                for rid in self._outgoing.get(eid, []):
                    rel = self._relations.get(rid)
                    if rel and rel.target_id in entity_ids:
                        relation_ids.add(rid)

            entities = [self._entities[eid] for eid in entity_ids if eid in self._entities]
            relations = [self._relations[rid] for rid in relation_ids if rid in self._relations]
            return KGSubgraph(entities=entities, relations=relations, depth=depth)

    def stats(self) -> dict[str, int]:
        with self._lock:
            return {"entities": len(self._entities), "relations": len(self._relations)}


def create_knowledge_graph(backend: str = "memory") -> KnowledgeGraphInterface:
    if backend == "memory":
        return InMemoryKnowledgeGraph()
    raise ValueError(f"Unknown KG backend: {backend}")


__all__ = [
    "InMemoryKnowledgeGraph",
    "KGEntity",
    "KGPath",
    "KGRelation",
    "KGSubgraph",
    "KnowledgeGraphInterface",
    "create_knowledge_graph",
]
