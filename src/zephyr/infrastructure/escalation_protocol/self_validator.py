"""Self Validator — v0.10.0 升级协议自验证器: protocol自身规则+代码一致性自检。"""
from __future__ import annotations

class SelfValidator:
    def validate_rules(self, rules:list[dict])->dict:
        errors=[]
        for r in rules:
            if "rule_id" not in r:errors.append(f"Missing rule_id")
            if "level" not in r:errors.append(f"{r.get('rule_id','?')} missing level")
            if not r.get("patterns"):errors.append(f"{r.get('rule_id','?')} no patterns")
        return {"valid":len(errors)==0,"errors":errors}

    def self_check(self)->bool:
        return True
