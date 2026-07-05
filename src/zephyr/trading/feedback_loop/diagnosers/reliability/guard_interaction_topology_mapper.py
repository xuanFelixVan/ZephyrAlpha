# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.reliability.guard_interaction_topology_mapper
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_guard_interaction_topology_mapper | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R518: GuardInteractionTopologyMapper
Guard交互有向图+环路检测 — A→B→C→A 循环
"""

from collections import deque
from dataclasses import dataclass, field


@dataclass
class GuardEdge:
    from_guard: str
    to_guard: str
    interaction_count: int = 0


@dataclass
class GuardInteractionTopologyMapper:
    edges: list[GuardEdge] = field(default_factory=list)
    adjacency: dict[str, list[str]] = field(default_factory=dict)
    cycle_max_depth: int = 6

    def record_interaction(self, from_guard: str, to_guard: str) -> None:
        if from_guard not in self.adjacency:
            self.adjacency[from_guard] = []
        if to_guard not in self.adjacency[from_guard]:
            self.adjacency[from_guard].append(to_guard)

        for edge in self.edges:
            if edge.from_guard == from_guard and edge.to_guard == to_guard:
                edge.interaction_count += 1
                return
        self.edges.append(GuardEdge(from_guard=from_guard, to_guard=to_guard, interaction_count=1))

    def detect_cycles(self) -> dict:
        cycles = []
        all_nodes = set(self.adjacency.keys())
        for dest in self.adjacency.values():
            all_nodes.update(dest)

        for start_node in all_nodes:
            found = self._bfs_cycle_search(start_node)
            cycles.extend(found)

        unique_cycles = []
        seen = set()
        for cycle in cycles:
            key = tuple(sorted(cycle))
            if key not in seen:
                seen.add(key)
                unique_cycles.append(cycle)

        return {
            "cycles_detected": len(unique_cycles) > 0,
            "cycles": [list(c) for c in unique_cycles],
            "total_nodes": len(all_nodes),
            "total_edges": len(self.edges),
        }

    def get_interaction_density(self) -> float:
        nodes = set(self.adjacency.keys())
        for dest in self.adjacency.values():
            nodes.update(dest)
        n = len(nodes)
        if n < 2:
            return 0.0
        return len(self.edges) / (n * (n - 1))

    def get_most_interactive_guards(self, n: int = 5) -> list[dict]:
        degrees = {}
        for edge in self.edges:
            degrees[edge.from_guard] = degrees.get(edge.from_guard, 0) + edge.interaction_count
            degrees[edge.to_guard] = degrees.get(edge.to_guard, 0) + edge.interaction_count
        sorted_guards = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
        return [{"guard_id": g, "interactions": c} for g, c in sorted_guards[:n]]

    def _bfs_cycle_search(self, start: str) -> list[tuple[str, ...]]:
        cycles = []
        queue = deque([(start, [start])])
        while queue:
            node, path = queue.popleft()
            if len(path) > self.cycle_max_depth:
                continue
            for neighbor in self.adjacency.get(node, []):
                if neighbor == start and len(path) >= 2:
                    cycles.append(tuple(path + [neighbor]))
                elif neighbor not in path:
                    queue.append((neighbor, path + [neighbor]))
        return cycles
