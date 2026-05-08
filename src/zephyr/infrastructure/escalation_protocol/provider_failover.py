"""Provider Failover — v0.7.0 多LLM Provider容灾: deepseek→claude→gpt fallback链。"""
from __future__ import annotations

FALLBACK_CHAIN=["deepseek","claude","gpt"]

class ProviderFailover:
    def __init__(self):
        self._healthy:dict[str,bool]={p:True for p in FALLBACK_CHAIN}

    def mark_unhealthy(self, provider:str):
        self._healthy[provider]=False

    def mark_healthy(self, provider:str):
        self._healthy[provider]=True

    def get_available(self)->str:
        for p in FALLBACK_CHAIN:
            if self._healthy.get(p,False):
                return p
        return "none"

    def is_degraded(self)->bool:
        return self.get_available()!=FALLBACK_CHAIN[0]
