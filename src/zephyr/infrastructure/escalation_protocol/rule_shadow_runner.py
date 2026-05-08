"""Rule Shadow Runner — v0.10.0 规则影子模式: 新规则shadow运行3天→diff old vs new→promote。"""
from __future__ import annotations
import time

class RuleShadowRunner:
    def __init__(self):
        self._shadow_rules:dict[str,dict]={}

    def deploy_shadow(self, rule_id:str, rule_def:dict, shadow_days:int=3):
        self._shadow_rules[rule_id]={"rule":rule_def,"deployed_at":time.time(),"shadow_days":shadow_days,"decisions":[]}

    def record_shadow_decision(self, rule_id:str, operation:str, old_level:str, new_level:str):
        if rule_id in self._shadow_rules:
            self._shadow_rules[rule_id]["decisions"].append({"op":operation,"old":old_level,"new":new_level})

    def diff(self, rule_id:str)->dict:
        shadow=self._shadow_rules.get(rule_id)
        if not shadow:return {}
        changes=[d for d in shadow["decisions"] if d["old"]!=d["new"]]
        return {"rule_id":rule_id,"total":len(shadow["decisions"]),"changes":len(changes)}

    def promote(self, rule_id:str)->bool:
        return rule_id in self._shadow_rules
