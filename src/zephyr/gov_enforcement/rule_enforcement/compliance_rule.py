# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.compliance_rule
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.shared.contracts.compliance_rule
# [CONSUMERS] l10-compliance
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] re-export shim only; truth source is zephyr.shared.contracts.compliance_rule
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.shared.contracts.compliance_rule
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Re-export shim — ComplianceRule 真源已合并至 zephyr.shared.contracts.compliance_rule。

SSoT: cross_layer_contracts.yaml -> CTR-P1-012
canonical: src/zephyr/shared/contracts/compliance_rule.py

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: compliance_rule.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 ComplianceRule（共 1 符号）
#   desc: __init__ import L0；__all__ 1 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（1 符号）
#   name_en: __all__
#   intro: ComplianceRule
#   downstream: l10-compliance
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.shared.contracts.compliance_rule import ComplianceRule  # noqa: F401

__all__ = ["ComplianceRule"]
