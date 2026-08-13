# [BLUEPRINT] MOD-GOV_AGENT_RBAC | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.governance.agent_rbac.contracts
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.contracts (RBACAuditBridge)
# [CONSUMERS] tests.governance.test_p0_i2_construction_order
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] G-CT-001 RBAC 契约
# [MODIFY-GUARD] blueprint.md §4
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回None
# [TESTS] tests/governance/audit/test_p0_i2_construction_order.py
# [A_module] module_id=MOD-GOV_AGENT_RBAC | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

agent-rbac/contracts.py — G-CT-001 RBAC 契约（re-export）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: RBAC审计桥接类
#   fields: RBACAuditBridge（G-CT-001 RBAC 契约的唯一实现）
#   code: zephyr.security.access_control.contracts L（import 自 L21）
# 层: 算法
# - id: A1
#   name_zh: ① 契约再导出 re-export
#   name_en: contracts.__all__
#   intro: 把 security 域的 RBACAuditBridge 在 agent-rbac 包下再导出，统一契约入口
#   desc: from zephyr.security.access_control.contracts import RBACAuditBridge（noqa F401）→ __all__=["RBACAuditBridge"]（L21-23），无新逻辑
#   inputs: I1
#   outputs: agent-rbac 包的契约命名空间
#   invariant: G-CT-001 RBAC 契约；桥接失败返回 None
# 层: 输出
# - id: O1
#   name_zh: G-CT-001 RBAC 契约入口
#   name_en: RBACAuditBridge re-export
#   intro: agent-rbac 模块对外暴露的 RBAC 审计桥接契约，蓝图 MOD-GOV_AGENT_RBAC 的 SSoT 入口
#   downstream: tests.governance.test_p0_i2_construction_order（构造顺序测试）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.security.access_control.contracts import RBACAuditBridge  # noqa: F401

__all__ = ["RBACAuditBridge"]
