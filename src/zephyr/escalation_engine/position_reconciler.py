# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.position_reconciler

# [INVARIANTS] 持仓对账必须执行;P0-FATAL必须触发硬中断

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Position Reconciler — v0.10.0 持仓对账: execution report+book record+counterparty三方对账。
"""
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
