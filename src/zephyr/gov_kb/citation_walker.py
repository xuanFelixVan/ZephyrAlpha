# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md
# [MODULE] zephyr.gov_kb.citation_walker
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-ORC_citation_walker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""citation_walker.py — 引用行走 (DD117, TASK-020)"""

from dataclasses import dataclass


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
            paths.append(
                CitationPath(
                    ke_id=ke_id, cited_by=cited_by, depth=depth, impact_score=len(cited_by) * (1.0 / (depth + 1))
                )
            )
            for cited in cited_by:
                queue.append((cited, depth + 1))
        return paths
