"""Protocol State Store — v0.10.0 协议运行时状态持久化: JSON snapshot+recovery state+crash恢复。"""
from __future__ import annotations
import json,os
from datetime import datetime,timezone

class ProtocolStateStore:
    def __init__(self, state_dir:str=".audit_cache"):
        self._dir=state_dir
        self._state:dict={}
        os.makedirs(self._dir,exist_ok=True)

    def save(self)->str:
        snapshot={"state":self._state,"timestamp":datetime.now(timezone.utc).isoformat()}
        path=os.path.join(self._dir,"protocol_state.json")
        with open(path,"w",encoding="utf-8") as f:
            json.dump(snapshot,f,default=str)
        return path

    def update(self, key:str, value):
        self._state[key]=value
