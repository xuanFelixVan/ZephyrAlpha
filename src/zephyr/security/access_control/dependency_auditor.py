# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.dependency_auditor
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.rollback.phase_check_registry
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Stub module: zephyr.security.access_control.dependency_auditor — implementation pending.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: dependency_auditor.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 RESTRICTED_LICENSES, RESTRICTED_PACKAGES, DependencyAuditResult, Dependency…
#   desc: __init__ import L0；__all__ 4 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（2 类）
#   name_en: data classes
#   intro: DependencyAuditResult, DependencyAuditor
#   downstream: zephyr.infrastructure.rollback.phase_check_registry
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

RESTRICTED_LICENSES: Final[None] = None  # stub constant
RESTRICTED_PACKAGES: Final[None] = None  # stub constant


class DependencyAuditResult:
    """Stub class — implementation pending."""

    pass


class DependencyAuditor:
    """Stub class — implementation pending."""

    pass


__all__ = [
    "RESTRICTED_LICENSES",
    "RESTRICTED_PACKAGES",
    "DependencyAuditResult",
    "DependencyAuditor",
]
