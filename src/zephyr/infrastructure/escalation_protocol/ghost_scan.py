"""Ghost Scan — v0.8.0 幽灵进程检测: lingering process扫描+资源泄漏检测。"""
from __future__ import annotations

class GhostScanner:
    def __init__(self):
        self._registered_pids:set[str]=set()

    def register(self, pid:str):
        self._registered_pids.add(pid)

    def detect_ghosts(self, active_pids:set[str])->list[str]:
        return list(self._registered_pids-active_pids)

    def cleanup(self, pid:str)->bool:
        self._registered_pids.discard(pid)
        return True
