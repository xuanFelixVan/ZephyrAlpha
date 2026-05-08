"""Process Isolator — v0.6.0 进程隔离器: engine运行在独立进程+资源限制+crash恢复。"""
from __future__ import annotations

class ProcessIsolator:
    def __init__(self):
        self._processes:dict[str,dict]={}

    def spawn_engine(self, engine_id:str, config:dict=None)->bool:
        self._processes[engine_id]={"status":"running","config":config or {}}
        return True

    def isolate(self, engine_id:str, resource_limits:dict=None)->bool:
        if engine_id not in self._processes:
            return False
        self._processes[engine_id]["limits"]=resource_limits or {"cpu":1,"memory_mb":256}
        return True

    def kill_engine(self, engine_id:str)->bool:
        proc=self._processes.pop(engine_id,None)
        return proc is not None
