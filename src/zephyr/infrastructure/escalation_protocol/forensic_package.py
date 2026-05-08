"""Forensic Package — v0.8.0 取证就绪: escalation event bundle+hash chain+timestamp。"""
from __future__ import annotations
import hashlib,json
from datetime import datetime,timezone

class ForensicPackage:
    def __init__(self):
        self._events:list[dict]=[]
        self._chain:list[str]=[]

    def bundle(self, event:dict)->str:
        serialized=json.dumps(event,sort_keys=True,default=str)
        h=hashlib.sha256(serialized.encode()).hexdigest()
        self._events.append({"hash":h,"timestamp":datetime.now(timezone.utc).isoformat(),"event":event})
        if self._chain:
            prev=self._chain[-1]
            h=hashlib.sha256((prev+serialized).encode()).hexdigest()
        self._chain.append(h)
        return h

    def verify_chain(self)->bool:
        for i in range(1,len(self._chain)):
            prev=self._chain[i-1]
            curr_event=json.dumps(self._events[i]["event"],sort_keys=True,default=str)
            expected=hashlib.sha256((prev+curr_event).encode()).hexdigest()
            if expected!=self._chain[i]:
                return False
        return True
