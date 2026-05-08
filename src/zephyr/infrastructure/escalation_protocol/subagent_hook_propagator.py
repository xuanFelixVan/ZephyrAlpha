"""Subagent Hook Propagator — v0.13.0 子Agent Hook旁路防护器。"""
from __future__ import annotations

class SubagentHookPropagator:
    def __init__(self):
        self._hooks:dict[str,dict]={}

    def register_hook(self, parent_agent:str, hook_name:str, propagate:bool=True):
        self._hooks[parent_agent]={"name":hook_name,"propagate_to_subagents":propagate}

    def must_propagate(self, parent_agent:str)->bool:
        hook=self._hooks.get(parent_agent,{})
        return hook.get("propagate_to_subagents",True)
