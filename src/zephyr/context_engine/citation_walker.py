# [BLUEPRINT] MOD-INF-008 | 03_modules/_cross_layer/context-engine/blueprint.md | §

# [MODULE] zephyr.context_engine.citation_walker

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""citation_walker.py — 引用行走 (DD117, TASK-020)"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class CitationPath:
    ke_id: str
    cited_by: list[str]
    depth: int
    impact_score: float


class CitationWalker:
    """KE 引用链 BFS walker + per-KE impact score (DD117)."""
    def walk(self, start_ke: str, graph: dict[str, list[str]], max_depth: int = 3) -> list[CitationPath]:
        visited: set[str] = set()
        paths: list[CitationPath] = []
        queue: list[tuple[str, int]] = [(start_ke, 0)]
        while queue:
            ke_id, depth = queue.pop(0)
            if ke_id in visited or depth > max_depth:
                continue
            visited.add(ke_id)
            cited_by = graph.get(ke_id, [])
            paths.append(CitationPath(ke_id=ke_id, cited_by=cited_by, depth=depth, impact_score=len(cited_by) * (1.0 / (depth + 1))))
            for cited in cited_by:
                queue.append((cited, depth + 1))
        return paths
