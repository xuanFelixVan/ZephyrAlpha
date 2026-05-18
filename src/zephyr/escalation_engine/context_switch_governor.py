# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.context_switch_governor

# [INVARIANTS] 上下文切换预算不可超限;daily_capacity=16不可修改

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Context Switch Governor — v0.11.0 Owner上下文切换预算管理器。
"""
from __future__ import annotations

class ContextSwitchGovernor:
    def __init__(self):
        self._daily_switches:dict[str,int]={}
        self._max_switches_per_owner=12

    def can_switch(self, owner_id:str)->bool:
        current=self._daily_switches.get(owner_id,0)
        return current<self._max_switches_per_owner

    def record_switch(self, owner_id:str):
        self._daily_switches[owner_id]=self._daily_switches.get(owner_id,0)+1
