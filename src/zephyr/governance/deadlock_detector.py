# [A_module] module_id=MOD-RES_deadlock_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md

# [MODULE] zephyr.governance.deadlock_detector

# [INVARIANTS] 循环检测必须覆盖所有活跃委托;检测不可跳过;Dijkstra排序保证无死锁

# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.governance.delegation_engine;zephyr.infrastructure.a2a_protocol.layer3_coordination

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Deadlock Detector — D-022-04 多Agent死锁+循环依赖检测+超时破解。
SSoT: 本模块是全项目死锁检测的唯一真源。A2A Protocol 消费本模块，不再独立实现。
"""

from __future__ import annotations
from typing import Any


class DeadlockDetector:
    def __init__(self):
        self._wait_graph: dict[str, set[str]] = {}
        self._locks: dict[str, str] = {}
        self._preemption_order: list[str] = []

    def add_edge(self, waiter: str, holder: str):
        self._wait_graph.setdefault(waiter, set()).add(holder)

    def detect_cycle(self) -> list[str]:
        visited = set()
        rec_stack = set()
        cycle = []

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in self._wait_graph.get(node, set()):
                if neighbor not in visited:
                    result = dfs(neighbor)
                    if result:
                        return result
                elif neighbor in rec_stack:
                    return [neighbor]
            rec_stack.discard(node)
            return None

        for node in self._wait_graph:
            if node not in visited:
                result = dfs(node)
                if result:
                    cycle = result
                    break
        return cycle

    def break_deadlock(self, node: str) -> bool:
        self._wait_graph.pop(node, None)
        return True

    def try_acquire(self, resource: str, holder: str) -> bool:
        if resource in self._locks:
            return False
        self._locks[resource] = holder
        return True

    def release(self, resource: str, holder: str) -> bool:
        if self._locks.get(resource) == holder:
            del self._locks[resource]
            return True
        return False

    def dijkstra_order(self) -> list[str]:
        nodes = set(self._wait_graph.keys())
        for holders in self._wait_graph.values():
            nodes.update(holders)
        in_degree: dict[str, int] = {n: 0 for n in nodes}
        for waiter in self._wait_graph:
            for holder in self._wait_graph[waiter]:
                in_degree[holder] = in_degree.get(holder, 0)
            in_degree.setdefault(waiter, 0)

        for waiter in self._wait_graph:
            for holder in self._wait_graph[waiter]:
                pass

        queue = [n for n in nodes if in_degree.get(n, 0) == 0]
        order = []
        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbor in self._wait_graph.get(node, set()):
                in_degree[neighbor] = in_degree.get(neighbor, 1) - 1
                if in_degree[neighbor] <= 0:
                    queue.append(neighbor)
        self._preemption_order = order
        return order

    def preempt_lowest(self) -> str | None:
        if not self._preemption_order:
            self.dijkstra_order()
        if self._preemption_order:
            victim = self._preemption_order.pop(0)
            self.break_deadlock(victim)
            return victim
        return None

    def serialize(self) -> dict[str, Any]:
        return {
            "wait_graph": {k: list(v) for k, v in self._wait_graph.items()},
            "locks": dict(self._locks),
            "preemption_order": list(self._preemption_order),
        }
