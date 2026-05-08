"""Construction Verifier — 施工验证器: 任务卡完成度+蓝图一致性检查。"""
from __future__ import annotations

class ConstructionVerifier:
    def verify_card(self,task_id:str,produced_files:list[str],expected_files:list[str])->dict:
        missing=set(expected_files)-set(produced_files)
        extra=set(produced_files)-set(expected_files)
        return {"task_id":task_id,"match":len(missing)==0 and len(extra)==0,"missing":list(missing),"extra":list(extra)}

    def blueprint_consistency(self,blueprint_refs:list[str],actual_files:list[str])->float:
        bp_set=set(blueprint_refs)
        actual_set=set(actual_files)
        if not bp_set:return 0.0
        return len(bp_set & actual_set)/len(bp_set)
