---
module_id: KE-module_blu-2_252_fle_operational_ontology-000
title: 2.252 FLE Operational Ontology Model - fle_operational_ontology.py (🆕 v0.23.0 -
category: module_blueprint
---

# 2.252 FLE Operational Ontology Model - fle_operational_ontology.py (🆕 v0.23.0 -

2.252 FLE Operational Ontology Model - fle_operational_ontology.py (🆕 v0.23.0 - 盲点301 — 从离散KB到形式化的操作实体关系模型)

**致命问题**：FLE的KB是离散的JSON条目：{anomaly_pattern, diagnosis, repair_steps, success_rate}。但真实的系统是一个互联的实体网络：order_router DEPENDS_ON connection_pool, connection_pool HAS_METRIC connection_pool_usage, connection_pool_usage AFFECTS order_latency, order_latency IMPACTS trading_pnl。KB的离散条目无法表达这些实体关系→FLE的reasoning sees individual dots, not the connected graph。这就是Palantir Foundry的Ontology vs 传统数据库的区别：后者知道数据，前者知道实体间的关系。形式化的操作本体是FLE从"KB查询"到"推理实体关系图"的关键跃迁。
**对标**：Palantir Foundry Operational Ontology + Google Knowledge Graph + Wikidata Entity-Relationship Model + AWS CloudFormation Resource Dependency Graph + OWL (Web Ontology Language) + RDF Triples

```python
@dataclass
class OntologyEdge:
    source_entity: str        # "order_router"
    target_entity: str        # "connection_pool"
    relation_type: str        # "DEPENDS_ON"|"PRODUCES_METRIC"|"AFFECTS"|"CONTROLS"|"CONTAINS"|"TRIGGERS"
    confidence: float         # 关系的置信度 0-1
    evidence_sources: list[str]  # 此关系是从哪些证据中推断的
    is_transitive: bool       # 关系是否可传递 (如DEPENDS_ON是传递的)

class FLEOperationalOntologyModel:
    ONTOLOGY_REFRESH_INTERVAL_HOURS: int = 24

    async def build_and_refresh_ontology(self) -> OperationalOntology:
        graph = nx.DiGraph()
        # 1. 从IaC、配置、部署拓扑中提取静态关系
        static_edges = await self._extract_static_relationships()
        # 2. 从运行时的依赖追踪中提取动态关系
        dynamic_edges = await self._extract_dynamic_relationships()
        # 3. 从KB的故障链中学习因果关系
        causal_edges = await self._extract_causal_relationships_from_kb()
        
        for edge in static_edges + dynamic_edges + causal_edges:
            graph.add_edge(edge.source_entity, edge.target_entity,
                relation=edge)
        
        # 4. 运行传递闭包：发现间接依赖
        transitive_closure = nx.transitive_closure_dag(graph)
        # 5. 检测关键路径：如果root node故障，3跳后影响什么
        root_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]
        blast_paths = {}
        for root in root_nodes:
            paths = list(nx.all_simple_paths(transitive_closure, root, 
                [n for n in graph.nodes() if n.startswith("trading_pnl")], cutoff=5))
            blast_paths[root] = paths

        self.FLE.notify_owner("ONTOLOGY_REFRESHED",
            f"Operational ontology refreshed: {len(graph.nodes())} entities, "
            f"{len(graph.edges())} relationships, "
            f"{len(root_nodes)} root nodes, "
            f"{len(blast_paths)} blast-radius paths computed. "
            f"Top 3 most-connected entities: "
            f"{', '.join(node for node,_ in sorted(graph.in_degree(), key=lambda x:x[1], reverse=True)[:3])}.")

        return OperationalOntology(graph=graph, blast_paths=blast_paths,
            critical_entities=self._identify_critical_single_points_of_failure(graph))
```
