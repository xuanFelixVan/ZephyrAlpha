"""Memory Provenance — v0.9.0 记忆溯源追踪: 每条memory record的来源agent+timestamp+hash链。"""
from __future__ import annotations
import hashlib,json
from datetime import datetime,timezone

class MemoryProvenanceLog:
    def __init__(self):
        self._records:list[dict]=[]

    def record(self, agent_id:str, content:str, source_contract:str="")->str:
        h=hashlib.sha256(content.encode()).hexdigest()
        ts=datetime.now(timezone.utc).isoformat()
        self._records.append({"agent":agent_id,"hash":h,"timestamp":ts,"contract":source_contract})
        return h

    def trace(self, content_hash:str)->dict|None:
        for r in self._records:
            if r["hash"]==content_hash:
                return r
        return None
