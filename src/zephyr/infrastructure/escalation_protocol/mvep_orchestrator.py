"""MVEP Orchestrator — v0.11.0 Minimum Viable Escalation Protocol调度器。"""
from __future__ import annotations

MVE_SEQUENCE=["D-022-01 engine","D-022-02 delegation","D-022-03 economic","D-022-04 deadlock","D-022-05 confidence"]

class MVEPOrchestrator:
    def __init__(self):
        self._implemented:set[str]=set()

    def mark_implemented(self, decision_id:str):
        self._implemented.add(decision_id)

    def missing_mvps(self)->list[str]:
        base={d.split()[0] for d in MVE_SEQUENCE}
        return list(base-self._implemented)

    def all_implemented(self)->bool:
        return len(self.missing_mvps())==0
