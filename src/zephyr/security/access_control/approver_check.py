# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.approver_check
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests.governance.test_adversarial_contract_attacks ; tests.governance.test_gct_004_escalation_to_rbac ; tests.governance.test_p0_u1_contract_smoke
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] verify_approver returns dict with approved/approver_id/action/reason; superadmin always approved; restricted action requires superadmin; others approved as valid_approver
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Approver authorization verifier — 校验审批人是否有权执行请求的动作。

治本（2026-07-18）：原模块为 stub（verify_approver raise NotImplementedError），
现根据 tests/governance/security/test_governance_approver_check.py 及
tests/governance/security/test_adversarial_contract_attacks.py 的契约定义实现完整逻辑。

契约规则（由测试定义，按优先级排序）：
  1. superadmin 通行：approver_id in SUPERADMIN_AGENTS
     → approved=True, reason="superadmin"
  2. 受限动作非 superadmin 拒绝：
     action in RESTRICTED_ACTIONS 且 approver_id not in SUPERADMIN_AGENTS
     → approved=False, reason="restricted_action_requires_superadmin"
  3. 普通审批：其余情况
     → approved=True, reason="valid_approver"

返回值：dict[str, Any]，含 "approved" (bool)、"approver_id" (str)、
       "action" (str)、"reason" (str)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: approver_id 参数
#   fields: 参数 approver_id，类型注解 str
#   code: approver_check.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: requested_action 参数
#   fields: 参数 requested_action，类型注解 str
#   code: approver_check.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① verify_approver
#   name_en: verify_approver
#   intro: 验证 approver 是否有权审批 requested_action。
#   desc: 验证 approver 是否有权审批 requested_action。 支持位置参数和关键字参数两种调用形式： verify_approver("admin", "deploy…；源码 L93-L138
#   inputs: approver_id requested_action
#   outputs: dict[str, Any]
# 层: 输出
# - id: O1
#   name_zh: dict[str, Any]
#   name_en: dict[str, Any]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests.governance.test_adversarial_contract_attacks ; tests.governance.test_gct_…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from typing import Any, Final

# 超级管理员 agent 集合——可执行任意动作（含受限动作）。
# 测试契约：bytebuddy 和 superadmin 必须在此集合中。
SUPERADMIN_AGENTS: Final[set[str]] = {
    "bytebuddy",
    "superadmin",
}

# 受限动作集合——仅 superadmin 可审批，普通 approver 一律拒绝。
# 测试契约：deploy/destroy/drop_table 必须在此集合中。
RESTRICTED_ACTIONS: Final[set[str]] = {
    "deploy",
    "destroy",
    "drop_table",
    "purge",
    "wipe",
    "format",
    "shutdown",
    "drop_database",
    "reset_production",
    "disable_safety",
}


def verify_approver(approver_id: str, requested_action: str) -> dict[str, Any]:
    """验证 approver 是否有权审批 requested_action。

    支持位置参数和关键字参数两种调用形式：
      verify_approver("admin", "deploy")
      verify_approver(approver_id="admin", requested_action="deploy")

    Args:
        approver_id: 审批人 agent ID。
        requested_action: 待审批动作名称。

    Returns:
        dict 含：
        - "approved" (bool): 是否批准
        - "approver_id" (str): 传入的 approver_id
        - "action" (str): 传入的 requested_action
        - "reason" (str): 批准/拒绝原因
          * "superadmin" — superadmin 通行
          * "restricted_action_requires_superadmin" — 受限动作需 superadmin
          * "valid_approver" — 普通审批通过
    """
    # 规则 1：superadmin 通行
    if approver_id in SUPERADMIN_AGENTS:
        return {
            "approved": True,
            "approver_id": approver_id,
            "action": requested_action,
            "reason": "superadmin",
        }

    # 规则 2：受限动作非 superadmin 拒绝
    if requested_action in RESTRICTED_ACTIONS:
        return {
            "approved": False,
            "approver_id": approver_id,
            "action": requested_action,
            "reason": "restricted_action_requires_superadmin",
        }

    # 规则 3：普通审批通过
    return {
        "approved": True,
        "approver_id": approver_id,
        "action": requested_action,
        "reason": "valid_approver",
    }


__all__ = [
    "RESTRICTED_ACTIONS",
    "SUPERADMIN_AGENTS",
    "verify_approver",
]
