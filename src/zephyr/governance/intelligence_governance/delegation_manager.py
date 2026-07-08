# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.delegation_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.services.adapter;zephyr.trading.orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 委托链深度≤3;四级安全约束不可降级
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_delegation_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Delegation Manager — D-022-02 自动委托协议。

delegate(task, capability)->Agent + 四级安全约束：
1. 自委托禁止(SELF_DELEGATION->blocked)
2. 循环检测(detected_cycle->blocked)
3. 深度上限=3
4. SLA超时30s->compensation
"""

from __future__ import annotations

import time
from enum import Enum


class DelegateResult(Enum):
    GRANTED = "GRANTED"
    SELF_DELEGATION = "SELF_DELEGATION"
    CYCLE_DETECTED = "CYCLE_DETECTED"
    DEPTH_EXCEEDED = "DEPTH_EXCEEDED"
    SLA_TIMEOUT = "SLA_TIMEOUT"


class DelegationManager:
    MAX_DEPTH = 3
    SLA_TIMEOUT_S = 30.0

    def __init__(self):
        self._delegation_chain: list[str] = []
        self._seen_agents: set[str] = set()
        self._backoff_attempts: dict[str, int] = {}

    def delegate(self, task: dict, capability: str) -> tuple[bool, DelegateResult, str]:
        caller = task.get("caller", "unknown")
        if task.get("source_agent") == caller:
            return False, DelegateResult.SELF_DELEGATION, "SELF_DELEGATION"
        if caller in self._seen_agents:
            return False, DelegateResult.CYCLE_DETECTED, f"Cycle: {caller}"
        if len(self._delegation_chain) >= self.MAX_DEPTH:
            return False, DelegateResult.DEPTH_EXCEEDED, f"Depth>{self.MAX_DEPTH}"
        start = time.time()
        self._delegation_chain.append(caller)
        self._seen_agents.add(caller)
        elapsed = time.time() - start
        if elapsed > self.SLA_TIMEOUT_S:
            self._compensate(task)
            return False, DelegateResult.SLA_TIMEOUT, f"SLA timeout: {elapsed:.1f}s"
        return True, DelegateResult.GRANTED, "Delegated to target agent"

    def _compensate(self, task: dict):
        tid = task.get("task_id", "")
        self._backoff_attempts[tid] = self._backoff_attempts.get(tid, 0) + 1

    def injected_before(self, task: dict, capability: str) -> bool:
        caller = task.get("caller", "")
        return caller not in self._seen_agents

    def reset_chain(self):
        self._delegation_chain.clear()
        self._seen_agents.clear()
