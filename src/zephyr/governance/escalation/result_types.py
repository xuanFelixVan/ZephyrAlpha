# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md
# [MODULE] zephyr.governance.escalation.result_types
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.shared.contracts.rollback_types
# [CONSUMERS] tests/governance/escalation/test_result_types;tests/governance/governance_misc/test_governance_result_types;tests/governance/governance_e2e/test_gct_003_rollback_to_escalation;tests/governance/drift/test_gct_integration;tests/governance/shared/test_phase_gates;tests/governance/security/test_p0_u1_contract_smoke
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 结果类型定义;不可随意扩展
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RollbackError;TypeError
# [TESTS] tests/rollback/
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
[BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md

G-CT-003 — RollbackResult backward-compat re-export facade.
Canonical home is now: zephyr.shared.contracts.rollback_types

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: result_types.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 RollbackResult, RollbackStatus, ValidationResult（共 3 符号）
#   desc: __init__ import L0；__all__ 3 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（3 符号）
#   name_en: __all__
#   intro: RollbackResult, RollbackStatus, ValidationResult
#   downstream: tests/governance/escalation/test_result_types;tests/governance/governance_misc/…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.shared.contracts.rollback_types import (
    RollbackResult,
    RollbackStatus,
    ValidationResult,
)

__all__ = ["RollbackResult", "RollbackStatus", "ValidationResult"]
