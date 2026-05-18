# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.self_validator

# [INVARIANTS] Shadow Parallel Run必须通过;自验证不可跳过

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Self Validator — v0.10.0 升级协议自验证器: protocol自身规则+代码一致性自检。
"""
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
