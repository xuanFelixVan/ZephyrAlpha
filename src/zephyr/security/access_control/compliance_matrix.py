# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.compliance_matrix
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] design
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
Stub module: zephyr.security.access_control.compliance_matrix — implementation pending.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: compliance_matrix.py
# 层: 算法
# - id: A1
#   name_zh: ① compliant_items
#   name_en: compliant_items
#   intro: Stub function — implementation pending.
#   desc: Stub function — implementation pending.；源码 L81-L83
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② get_by_reg_id
#   name_en: get_by_reg_id
#   intro: Stub function — implementation pending.
#   desc: Stub function — implementation pending.；源码 L86-L88
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ non_compliant_items
#   name_en: non_compliant_items
#   intro: Stub function — implementation pending.
#   desc: Stub function — implementation pending.；源码 L91-L93
#   inputs: 无参数
#   outputs: 返回值
#   （注：A3 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: compliant_items, get_by_reg_id, non_compliant_items
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from typing import Final

COMPLIANCE_MATRIX: Final[None] = None  # stub constant


class ComplianceItem:
    """Stub class — implementation pending."""

    pass


class ComplianceStatus:
    """Stub class — implementation pending."""

    pass


def compliant_items(*args, **kwargs):
    """Stub function — implementation pending."""
    raise NotImplementedError("compliant_items not implemented")


def get_by_reg_id(*args, **kwargs):
    """Stub function — implementation pending."""
    raise NotImplementedError("get_by_reg_id not implemented")


def non_compliant_items(*args, **kwargs):
    """Stub function — implementation pending."""
    raise NotImplementedError("non_compliant_items not implemented")


__all__ = [
    "COMPLIANCE_MATRIX",
    "ComplianceItem",
    "ComplianceStatus",
    "compliant_items",
    "get_by_reg_id",
    "non_compliant_items",
]
