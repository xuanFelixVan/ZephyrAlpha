"""Rule Debt Auditor — v0.7.0 规则债务审计器: 分析escalation_rules.yaml维护债务指标。"""
from __future__ import annotations

class RuleDebtAuditor:
    def audit(self, rules:list[dict])->dict:
        total=len(rules)
        levels={r.get("level","unknown") for r in rules}
        duplicate_patterns=set()
        all_patterns=[]
        for r in rules:
            for p in r.get("patterns",[]):
                if p in all_patterns:
                    duplicate_patterns.add(p)
                all_patterns.append(p)
        return {"total_rules":total,"unique_levels":len(levels),
                "duplicate_patterns":len(duplicate_patterns),
                "debt_score":len(duplicate_patterns)/max(1,total)}
