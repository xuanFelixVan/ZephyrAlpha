# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.rule_engine.rule_debt_auditor
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 规则债务审计不可跳过;过时规则必须标记
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Rule Debt Auditor — v0.7.0 规则债务审计器: 分析escalation_rules.yaml维护债务指标。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: rule_debt_auditor.py
# 层: 算法
# - id: A1
#   name_zh: ① RuleDebtAuditor
#   name_en: RuleDebtAuditor
#   intro: class RuleDebtAuditor 源码 L51-L67
#   desc: 公共方法（定义序）: audit；源码 L51-L67
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: RuleDebtAuditor
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations


class RuleDebtAuditor:
    def audit(self, rules: list[dict]) -> dict:
        total = len(rules)
        levels = {r.get("level", "unknown") for r in rules}
        duplicate_patterns = set()
        all_patterns = []
        for r in rules:
            for p in r.get("patterns", []):
                if p in all_patterns:
                    duplicate_patterns.add(p)
                all_patterns.append(p)
        return {
            "total_rules": total,
            "unique_levels": len(levels),
            "duplicate_patterns": len(duplicate_patterns),
            "debt_score": len(duplicate_patterns) / max(1, total),
        }
