"""
MOD-INF-016 B49: Knowledge Graph Interface Protocol

Unified abstraction for KG backends (Neo4j / Mem0 Graph Memory / in-memory).
Consumed by: drift_detector, auto-fix-engine, knowledge-specialist, a2a-protocol.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@dataclass(frozen=True)
class KGEntity:
    entity_id: str
    entity_type: str
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class KGRelation:
    relation_id: str
    source_id: str
    target_id: str
    relation_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class KGPath:
    nodes: List[KGEntity]
    edges: List[KGRelation]
    total_weight: float = 0.0


@dataclass
class KGSubgraph:
    entities: List[KGEntity]
    relations: List[KGRelation]
    depth: int = 0


@runtime_checkable
class KnowledgeGraphInterface(Protocol):
    def add_entity(self, entity: KGEntity) -> str: ...
    def add_relation(self, relation: KGRelation) -> str: ...
    def query_path(self, source_id: str, target_id: str, max_depth: int = 5) -> KGPath: ...
    def query_subgraph(self, center_id: str, depth: int = 2) -> KGSubgraph: ...
    def get_entity(self, entity_id: str) -> Optional[KGEntity]: ...
    def get_relations(self, entity_id: str, direction: str = "both") -> List[KGRelation]: ...
    def remove_entity(self, entity_id: str) -> bool: ...
    def remove_relation(self, relation_id: str) -> bool: ...


class InMemoryKnowledgeGraph:
    def __init__(self) -> None:
        self._entities: Dict[str, KGEntity] = {}
        self._relations: Dict[str, KGRelation] = {}
        self._outgoing: Dict[str, List[str]] = {}
        self._incoming: Dict[str, List[str]] = {}
        self._lock = threading.Lock()
        self._next_id = 0

    def _gen_id(self, prefix: str) -> str:
        self._next_id += 1
        return f"{prefix}-{self._next_id:06d}"

    def add_entity(self, entity: KGEntity) -> str:
        with self._lock:
            if entity.entity_id not in self._entities:
                self._entities[entity.entity_id] = entity
                self._outgoing.setdefault(entity.entity_id, [])
                self._incoming.setdefault(entity.entity_id, [])
            return entity.entity_id

    def add_relation(self, relation: KGRelation) -> str:
        with self._lock:
            if not relation.relation_id:
                relation = KGRelation(
                    relation_id=self._gen_id("rel"),
                    source_id=relation.source_id,
                    target_id=relation.target_id,
                    relation_type=relation.relation_type,
                    properties=relation.properties,
                    created_at=relation.created_at,
                )
            self._relations[relation.relation_id] = relation
            self._outgoing.setdefault(relation.source_id, []).append(relation.relation_id)
            self._incoming.setdefault(relation.target_id, []).append(relation.relation_id)
            return relation.relation_id

    def query_path(self, source_id: str, target_id: str, max_depth: int = 5) -> KGPath:
        with self._lock:
            if source_id not in self._entities or target_id not in self._entities:
                return KGPath(nodes=[], edges=[])

            visited: set[str] = set()
            queue: List[tuple[str, List[str], List[str]]] = [(source_id, [source_id], [])]

            while queue and len(visited) < 500:
                current, path_ids, rel_ids = queue.pop(0)
                if current == target_id:
                    nodes = [self._entities[eid] for eid in path_ids if eid in self._entities]
                    edges = [self._relations[rid] for rid in rel_ids if rid in self._relations]
                    return KGPath(nodes=nodes, edges=edges)

                if current in visited:
                    continue
                visited.add(current)

                if len(path_ids) > max_depth + 1:
                    continue

                for rid in self._outgoing.get(current, []):
                    rel = self._relations.get(rid)
                    if rel and rel.target_id not in visited:
                        queue.append((rel.target_id, path_ids + [rel.target_id], rel_ids + [rid]))

            return KGPath(nodes=[], edges=[])

    def query_subgraph(self, center_id: str, depth: int = 2) -> KGSubgraph:
        with self._lock:
            if center_id not in self._entities:
                return KGSubgraph(entities=[], relations=[], depth=0)

            entity_ids: set[str] = {center_id}
            relation_ids: set[str] = set()
            frontier = {center_id}

            for _ in range(depth):
                next_frontier: set[str] = set()
                for eid in frontier:
                    for rid in self._outgoing.get(eid, []):
                        rel = self._relations.get(rid)
                        if rel and rid not in relation_ids:
                            relation_ids.add(rid)
                            if rel.target_id not in entity_ids:
                                entity_ids.add(rel.target_id)
                                next_frontier.add(rel.target_id)
                    for rid in self._incoming.get(eid, []):
                        rel = self._relations.get(rid)
                        if rel and rid not in relation_ids:
                            relation_ids.add(rid)
                            if rel.source_id not in entity_ids:
                                entity_ids.add(rel.source_id)
                                next_frontier.add(rel.source_id)
                frontier = next_frontier
                if not frontier:
                    break

            entities = [self._entities[eid] for eid in entity_ids if eid in self._entities]
            relations = [self._relations[rid] for rid in relation_ids if rid in self._relations]
            return KGSubgraph(entities=entities, relations=relations, depth=depth)

    def get_entity(self, entity_id: str) -> Optional[KGEntity]:
        with self._lock:
            return self._entities.get(entity_id)

    def get_relations(self, entity_id: str, direction: str = "both") -> List[KGRelation]:
        with self._lock:
            rids: List[str] = []
            if direction in ("outgoing", "both"):
                rids.extend(self._outgoing.get(entity_id, []))
            if direction in ("incoming", "both"):
                rids.extend(self._incoming.get(entity_id, []))
            return [self._relations[rid] for rid in rids if rid in self._relations]

    def remove_entity(self, entity_id: str) -> bool:
        with self._lock:
            if entity_id not in self._entities:
                return False
            rels_to_remove = list(self._outgoing.get(entity_id, [])) + list(self._incoming.get(entity_id, []))
            for rid in set(rels_to_remove):
                self._relations.pop(rid, None)
            self._entities.pop(entity_id, None)
            self._outgoing.pop(entity_id, None)
            self._incoming.pop(entity_id, None)
            return True

    def remove_relation(self, relation_id: str) -> bool:
        with self._lock:
            rel = self._relations.pop(relation_id, None)
            if rel is None:
                return False
            if rel.source_id in self._outgoing:
                self._outgoing[rel.source_id] = [r for r in self._outgoing[rel.source_id] if r != relation_id]
            if rel.target_id in self._incoming:
                self._incoming[rel.target_id] = [r for r in self._incoming[rel.target_id] if r != relation_id]
            return True

    def stats(self) -> Dict[str, int]:
        with self._lock:
            return {"entities": len(self._entities), "relations": len(self._relations)}


def create_knowledge_graph(backend: str = "memory", **kwargs: Any) -> KnowledgeGraphInterface:
    if backend == "memory":
        return InMemoryKnowledgeGraph()
    raise ValueError(f"Unknown KG backend: {backend!r}. Supported: 'memory'")
