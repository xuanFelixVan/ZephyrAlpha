# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.knowledge.ke_linker
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.knowledge.ke_structurer
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_ke_linker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
KE Linker — 知识条目关联图。

依据：
    蓝图 MOD-TASK_SYSTEM §6.12.2 + v0.6.0
    任务卡 TASK-INF-0121
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class KELink:
    source_ke_id: str
    target_ke_id: str
    relation_type: str
    strength: float
    evidence: str = ""


@dataclass
class KEGraph:
    nodes: dict[str, dict[str, Any]]
    links: list[KELink]
    connected_components: int
    density: float


class KELinker:
    RELATION_TYPES: list[str] = [
        "depends_on",
        "derives_from",
        "contradicts",
        "extends",
        "generalizes",
        "implements",
    ]

    def __init__(self) -> None:
        self._links: list[KELink] = []

    def link(self, source_ke_id: str, target_ke_id: str, relation_type: str, evidence: str = "") -> KELink:
        if relation_type not in self.RELATION_TYPES:
            relation_type = "depends_on"

        link = KELink(
            source_ke_id=source_ke_id,
            target_ke_id=target_ke_id,
            relation_type=relation_type,
            strength=0.8,
            evidence=evidence,
        )

        self._links.append(link)
        return link

    def auto_link_task_knowledge(self, task_id: str, ke_ids: list[str]) -> list[KELink]:
        new_links: list[KELink] = []

        for i, src in enumerate(ke_ids):
            for j, tgt in enumerate(ke_ids):
                if i >= j:
                    continue

                new_links.append(
                    self.link(
                        source_ke_id=src,
                        target_ke_id=tgt,
                        relation_type="depends_on",
                        evidence=f"Same task: {task_id}",
                    )
                )

        return new_links

    def build_graph(self, nodes: dict[str, dict[str, Any]]) -> KEGraph:
        node_ids = set(nodes.keys())
        relevant_links = [l for l in self._links if l.source_ke_id in node_ids and l.target_ke_id in node_ids]

        components = self._count_connected_components(node_ids, relevant_links)

        n = len(node_ids)
        max_links = n * (n - 1)
        density = len(relevant_links) / max(max_links, 1)

        return KEGraph(
            nodes=nodes,
            links=relevant_links,
            connected_components=components,
            density=round(density, 4),
        )

    def find_related_kes(self, ke_id: str, max_distance: int = 2) -> list[KELink]:
        related: list[KELink] = []
        visited: set[str] = {ke_id}
        frontier: list[str] = [ke_id]

        for _ in range(max_distance):
            next_frontier: list[str] = []
            for fid in frontier:
                for link in self._links:
                    if link.source_ke_id == fid and link.target_ke_id not in visited:
                        related.append(link)
                        visited.add(link.target_ke_id)
                        next_frontier.append(link.target_ke_id)
                    elif link.target_ke_id == fid and link.source_ke_id not in visited:
                        related.append(link)
                        visited.add(link.source_ke_id)
                        next_frontier.append(link.source_ke_id)
            frontier = next_frontier

        return related

    @staticmethod
    def _count_connected_components(node_ids: set[str], links: list[KELink]) -> int:
        parent: dict[str, str] = {}

        def find(x: str) -> str:
            if x not in parent:
                parent[x] = x
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x: str, y: str) -> None:
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        for nid in node_ids:
            parent[nid] = nid

        for link in links:
            union(link.source_ke_id, link.target_ke_id)

        roots = {find(nid) for nid in node_ids}
        return len(roots)
