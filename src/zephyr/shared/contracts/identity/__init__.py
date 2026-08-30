# [A_module] module_id=MOD-SHR-identity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.shared.contracts.identity
# [INVARIANTS] Agent身份模型不可被篡改;权限判定枚举不可扩展
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.security.access_control;zephyr.security.escalation;zephyr.governance;zephyr.integration.mcp
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT]
# [TESTS] tests/test_agent_rbac.py
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: importlib, MATURITY_AUTO_GUARD_TIMEOUT, MATURITY_TLB_LIMITS, ROLE_DEF…
#   code: __init__.py import L44
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 MATURITY_AUTO_GUARD_TIMEOUT, MATURITY_TLB_LIMITS, ROLE_DEFAULT_PERMISSIONS,…
#   desc: __init__ import L44；__all__ 14 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（14 符号）
#   name_en: __all__
#   intro: MATURITY_AUTO_GUARD_TIMEOUT, MATURITY_TLB_LIMITS, ROLE_DEFAULT_PERMISSIONS, Age…
#   downstream: zephyr.security.access_control;zephyr.security.escalation;zephyr.governance;zep…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import importlib

from zephyr.shared.contracts.identity.agent_identity import (
    MATURITY_AUTO_GUARD_TIMEOUT,
    MATURITY_TLB_LIMITS,
    ROLE_DEFAULT_PERMISSIONS,
    AgentIdentity,
    AgentMaturity,
    AgentRole,
    IDESource,
    MaturityLevel,
    RbacRole,
)
from zephyr.shared.contracts.identity.permission import GuardDecision, GuardResult


def __getattr__(name):
    if name == "AgentCapability":
        _mod = importlib.import_module("zephyr.governance.agent_spec.registry")
        _AC = _mod.AgentCapability
        globals()["AgentCapability"] = _AC
        return _AC
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "MATURITY_AUTO_GUARD_TIMEOUT",
    "MATURITY_TLB_LIMITS",
    "ROLE_DEFAULT_PERMISSIONS",
    "AgentCapability",
    "AgentIdentity",
    "AgentMaturity",
    "AgentRole",
    "GuardDecision",
    "GuardResult",
    "IDESource",
    "MaturityLevel",
    "RbacRole",
    "agent_identity",
    "permission",
]
