"""Formal Verifier — v0.6.0 形式验证器: 升级规则形式化验证→一致性+完备性检测。"""
from __future__ import annotations

class FormalVerifier:
    def verify_rule_completeness(self,rules:list[dict],operation_space:list[str])->dict:
        covered=set()
        for rule in rules:
            for p in rule.get("patterns",[]):
                covered.add(p)
        gaps=set(operation_space)-covered
        return {"complete":len(gaps)==0,"gaps":list(gaps),"coverage":len(covered)/max(1,len(operation_space))}

    def verify_rule_consistency(self,rules:list[dict])->list[str]:
        conflicts=[]
        for i,r1 in enumerate(rules):
            for j,r2 in enumerate(rules):
                if i>=j:continue
                p1=set(r1.get("patterns",[]))
                p2=set(r2.get("patterns",[]))
                overlap=p1&p2
                if overlap and r1.get("level")!=r2.get("level"):
                    conflicts.append(f"Conflict: {r1.get('rule_id')} vs {r2.get('rule_id')} on {overlap}")
        return conflicts
