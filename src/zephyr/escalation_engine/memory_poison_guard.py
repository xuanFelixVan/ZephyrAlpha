# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.memory_poison_guard

# [INVARIANTS] 记忆投毒检测不可禁用;存储前检测必须执行

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Memory Poison Guard — v0.9.0 记忆投毒防护: Memory写入内容审计+恶意注入检测。
"""
from __future__ import annotations

class MemoryPoisonGuard:
    def __init__(self):
        self._trusted_agents:set[str]=set()

    def register_trusted(self, agent_id:str):
        self._trusted_agents.add(agent_id)

    def validate_write(self, agent_id:str, memory_content:str)->tuple[bool,str]:
        if agent_id not in self._trusted_agents:
            return False,f"Agent {agent_id} not trusted for memory write"
        suspicious=["ignore_previous","forget_rules","new_identity","system_prompt:"]
        for s in suspicious:
            if s in memory_content.lower():
                return False,f"Suspicious content: {s}"
        return True,"OK"
