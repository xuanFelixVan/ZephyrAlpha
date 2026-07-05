# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.resilience_governance.deadlock_detector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.intelligence_governance.delegation_engine;zephyr.infrastructure.a2a_protocol.layer3_coordination
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 循环检测必须覆盖所有活跃委托;检测不可跳过;Dijkstra排序保证无死锁
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_deadlock_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Deadlock Detector — D-022-04 多Agent死锁+循环依赖检测+超时破解。
SSoT: 本模块是全项目死锁检测的唯一真源。A2A Protocol 消费本模块，不再独立实现。
"""

from __future__ import annotations

import time
from typing import Any


class DeadlockDetector:
    def __init__(self):
        self._wait_graph: dict[str, set[str]] = {}
        self._locks: dict[str, str] = {}
        self._lock_timestamps: dict[str, float] = {}
        self._preemption_order: list[str] = []

    def add_edge(self, waiter: str, holder: str):
        self._wait_graph.setdefault(waiter, set()).add(holder)

    def detect_cycle(self, waiter: str | None = None, holder: str | None = None) -> list[str]:
        if waiter is not None and holder is not None:
            self.add_edge(waiter, holder)
        visited: set[str] = set()
        rec_stack: set[str] = set()
        path: list[str] = []

        def dfs(node: str) -> list[str] | None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            for neighbor in self._wait_graph.get(node, set()):
                if neighbor not in visited:
                    result = dfs(neighbor)
                    if result:
                        return result
                elif neighbor in rec_stack:
                    idx = path.index(neighbor)
                    return path[idx:]
            path.pop()
            rec_stack.discard(node)
            return None

        for node in self._wait_graph:
            if node not in visited:
                path = []
                result = dfs(node)
                if result:
                    return result
        return []

    def break_deadlock(self, node: str) -> bool:
        self._wait_graph.pop(node, None)
        res_to_remove = [r for r, h in self._locks.items() if h == node]
        for r in res_to_remove:
            self._locks.pop(r, None)
            self._lock_timestamps.pop(r, None)
        return True

    def try_acquire(self, resource: str, holder: str) -> bool:
        if resource in self._locks:
            return False
        self._locks[resource] = holder
        self._lock_timestamps[resource] = time.monotonic()
        return True

    def release(self, resource: str, holder: str) -> bool:
        if self._locks.get(resource) == holder:
            del self._locks[resource]
            self._lock_timestamps.pop(resource, None)
            return True
        return False

    def break_timeout(self, timeout_seconds: float) -> list[str]:
        now = time.monotonic()
        expired = [
            r for r, ts in self._lock_timestamps.items()
            if now - ts >= timeout_seconds
        ]
        for r in expired:
            holder = self._locks.pop(r, None)
            self._lock_timestamps.pop(r, None)
            if holder:
                self._wait_graph.pop(holder, None)
        return expired

    def dijkstra_order(self) -> list[str]:
        nodes = set(self._wait_graph.keys())
        for holders in self._wait_graph.values():
            nodes.update(holders)
        in_degree: dict[str, int] = {n: 0 for n in nodes}
        for waiter in self._wait_graph:
            for holder in self._wait_graph[waiter]:
                in_degree[holder] = in_degree.get(holder, 0) + 1

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
