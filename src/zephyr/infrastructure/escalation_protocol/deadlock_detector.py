"""Deadlock Detector — D-022-04 多Agent死锁+循环依赖检测+超时破解。"""
from __future__ import annotations
from typing import Any

class DeadlockDetector:
    def __init__(self):
        self._wait_graph: dict[str,set[str]]={}

    def add_edge(self, waiter:str, holder:str):
        self._wait_graph.setdefault(waiter,set()).add(holder)

    def detect_cycle(self)->list[str]:
        visited=set()
        rec_stack=set()
        cycle=[]
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in self._wait_graph.get(node,set()):
                if neighbor not in visited:
                    result=dfs(neighbor)
                    if result:return result
                elif neighbor in rec_stack:
                    return [neighbor]
            rec_stack.discard(node)
            return None
        for node in self._wait_graph:
            if node not in visited:
                result=dfs(node)
                if result:
                    cycle=result
                    break
        return cycle

    def break_deadlock(self, node:str)->bool:
        self._wait_graph.pop(node,None)
        return True
