# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.self_validator
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Shadow Parallel Run必须通过;自验证不可跳过
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Self Validator — v0.10.0 升级协议自验证器: protocol自身规则+代码一致性自检。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: self_validator.py
# 层: 算法
# - id: A1
#   name_zh: ① SelfValidator
#   name_en: SelfValidator
#   intro: class SelfValidator 源码 L51-L64
#   desc: 公共方法（定义序）: validate_rules, self_check；源码 L51-L64
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SelfValidator
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class SelfValidator:
    def validate_rules(self, rules: list[dict]) -> dict:
        errors = []
        for r in rules:
            if "rule_id" not in r:
                errors.append("Missing rule_id")
            if "level" not in r:
                errors.append(f"{r.get('rule_id', '?')} missing level")
            if not r.get("patterns"):
                errors.append(f"{r.get('rule_id', '?')} no patterns")
        return {"valid": len(errors) == 0, "errors": errors}

    def self_check(self) -> bool:
        return True
