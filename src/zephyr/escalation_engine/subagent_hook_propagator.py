# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.subagent_hook_propagator

# [INVARIANTS] 子Agent Hook传播必须继承;sha256校验不可跳过

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Subagent Hook Propagator — v0.13.0 子Agent Hook旁路防护器。
"""
from __future__ import annotations

class SubagentHookPropagator:
    def __init__(self):
        self._hooks:dict[str,dict]={}

    def register_hook(self, parent_agent:str, hook_name:str, propagate:bool=True):
        self._hooks[parent_agent]={"name":hook_name,"propagate_to_subagents":propagate}

    def must_propagate(self, parent_agent:str)->bool:
        hook=self._hooks.get(parent_agent,{})
        return hook.get("propagate_to_subagents",True)
