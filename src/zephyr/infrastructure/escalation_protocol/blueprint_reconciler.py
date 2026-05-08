"""Blueprint Reconciler — v0.10.0 蓝图实现一致性校验器。"""
from __future__ import annotations

class BlueprintReconciler:
    def verify_module(self, blueprint_specs:dict, implementation_files:list[str])->dict:
        expected=set(blueprint_specs.get("files",[]))
        actual=set(implementation_files)
        missing=list(expected-actual)
        extra=list(actual-expected)
        return {"consistent":len(missing)==0,"missing":missing,"extra":extra}
