"""Strategy Scoper — v0.6.0 策略范围隔离器: SIG/Strat/Capital多层策略隔离。"""
from __future__ import annotations
from enum import Enum

class ScopeLevel(Enum):
    SIG="sig"
    STRATEGY="strategy"
    CAPITAL="capital"

class StrategyScoper:
    def __init__(self):
        self._scopes:dict[str,ScopeLevel]={}

    def assign_scope(self, agent_id:str, scope:ScopeLevel):
        self._scopes[agent_id]=scope

    def can_access(self, agent_id:str, target_scope:ScopeLevel)->bool:
        agent_scope=self._scopes.get(agent_id)
        if agent_scope is None:return False
        order=[ScopeLevel.SIG,ScopeLevel.STRATEGY,ScopeLevel.CAPITAL]
        return order.index(agent_scope)<=order.index(target_scope)
