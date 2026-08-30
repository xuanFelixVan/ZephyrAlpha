# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.architecture_governance.formal_verifier
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不变量验证必须通过;MCMAS验证不可跳过
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Formal Verifier — v0.6.0 形式验证器: 升级规则形式化验证->一致性+完备性检测。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: formal_verifier.py
# 层: 算法
# - id: A1
#   name_zh: ① FormalVerifier
#   name_en: FormalVerifier
#   intro: class FormalVerifier 源码 L51-L71
#   desc: 公共方法（定义序）: verify_rule_completeness, verify_rule_consistency；源码 L51-L71
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: FormalVerifier
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class FormalVerifier:
    def verify_rule_completeness(self, rules: list[dict], operation_space: list[str]) -> dict:
        covered = set()
        for rule in rules:
            for p in rule.get("patterns", []):
                covered.add(p)
        gaps = set(operation_space) - covered
        return {"complete": len(gaps) == 0, "gaps": list(gaps), "coverage": len(covered) / max(1, len(operation_space))}

    def verify_rule_consistency(self, rules: list[dict]) -> list[str]:
        conflicts = []
        for i, r1 in enumerate(rules):
            for j, r2 in enumerate(rules):
                if i >= j:
                    continue
                p1 = set(r1.get("patterns", []))
                p2 = set(r2.get("patterns", []))
                overlap = p1 & p2
                if overlap and r1.get("level") != r2.get("level"):
                    conflicts.append(f"Conflict: {r1.get('rule_id')} vs {r2.get('rule_id')} on {overlap}")
        return conflicts
