# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.risk.compliance_rule
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.trading_contracts.risk.__init__
# [CONSUMERS] l10-compliance
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODGEN:CTR-P1-012 ====

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: compliance_rule.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: ComplianceRule
#   desc: 数据契约/异常/枚举声明共 1 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（1 类）
#   name_en: data classes
#   intro: ComplianceRule
#   downstream: l10-compliance
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ComplianceRule:
    created_at: datetime
    description: str
    enforcement_action: str
    idempotency_key: str
    is_active: bool
    jurisdiction: str
    rule_id: str
    rule_logic: str
    rule_name: str
    rule_type: str
    severity: str
    updated_at: datetime
    version: str
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-P1-012 ====
