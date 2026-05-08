"""Position Reconciler — v0.10.0 持仓对账: execution report+book record+counterparty三方对账。"""
from __future__ import annotations

class PositionReconciler:
    def __init__(self):
        self._positions:dict[str,dict]={}

    def reconcile(self, internal:dict, external:dict)->dict:
        diffs={}
        all_keys=set(internal.keys())|set(external.keys())
        for k in all_keys:
            i=internal.get(k,0)
            e=external.get(k,0)
            if i!=e:diffs[k]={"internal":i,"external":e,"diff":i-e}
        return {"match":len(diffs)==0,"diffs":diffs,"count":len(diffs)}

    def should_escalate(self, diff_count:int, threshold:int=3)->bool:
        return diff_count>=threshold
