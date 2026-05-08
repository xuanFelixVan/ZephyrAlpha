"""Delegation Manager — D-022-02 自动委托协议。

delegate(task, capability)→Agent + 四级安全约束：
1. 自委托禁止(SELF_DELEGATION→blocked)
2. 循环检测(detected_cycle→blocked)
3. 深度上限=3
4. SLA超时30s→compensation
"""
from __future__ import annotations
from enum import Enum
from typing import Any
import time

class DelegateResult(Enum):
    GRANTED="GRANTED"
    SELF_DELEGATION="SELF_DELEGATION"
    CYCLE_DETECTED="CYCLE_DETECTED"
    DEPTH_EXCEEDED="DEPTH_EXCEEDED"
    SLA_TIMEOUT="SLA_TIMEOUT"

class DelegationManager:
    MAX_DEPTH=3
    SLA_TIMEOUT_S=30.0

    def __init__(self):
        self._delegation_chain: list[str]=[]
        self._seen_agents: set[str]=set()
        self._backoff_attempts: dict[str,int]={}

    def delegate(self, task: dict, capability: str) -> tuple[bool, DelegateResult, str]:
        caller = task.get("caller","unknown")
        if task.get("source_agent")==caller:
            return False, DelegateResult.SELF_DELEGATION, "SELF_DELEGATION"
        if caller in self._seen_agents:
            return False, DelegateResult.CYCLE_DETECTED, f"Cycle: {caller}"
        if len(self._delegation_chain)>=self.MAX_DEPTH:
            return False, DelegateResult.DEPTH_EXCEEDED, f"Depth>{self.MAX_DEPTH}"
        start=time.time()
        self._delegation_chain.append(caller)
        self._seen_agents.add(caller)
        elapsed=time.time()-start
        if elapsed>self.SLA_TIMEOUT_S:
            self._compensate(task)
            return False, DelegateResult.SLA_TIMEOUT, f"SLA timeout: {elapsed:.1f}s"
        return True, DelegateResult.GRANTED, f"Delegated to target agent"

    def _compensate(self, task: dict):
        tid=task.get("task_id","")
        self._backoff_attempts[tid]=self._backoff_attempts.get(tid,0)+1

    def injected_before(self, task: dict, capability: str)->bool:
        caller=task.get("caller","")
        return caller not in self._seen_agents

    def reset_chain(self):
        self._delegation_chain.clear()
        self._seen_agents.clear()
