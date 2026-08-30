# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.a2a_check
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] scripts.a2a_full_verification ; tests.governance.test_adversarial_contract_attacks ; tests.governance.test_gct_008_a2a_to_rbac_escalation ; tests.governance.test_gct_integration ; tests.governance.test_p0_u1_contract_smoke
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] verify_a2a_pair returns dict with approved/from/to keys; self_communication always approved; superadmin universal; ALLOWED_TALK_PAIRS bidirectional
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
A2A 通信对验证——校验两个 agent 之间是否允许通信。

治本（2026-07-18）：原模块为 stub（verify_a2a_pair raise NotImplementedError），
现根据 tests/a2a/test_a2a_check.py 及 tests/governance/security/test_governance_a2a_check.py
的契约定义实现完整逻辑。

契约规则（由测试定义）：
  1. from_agent == to_agent → approved, reason="self_communication"（含双方均为空串）
  2. from_agent == "superadmin" 或 to_agent == "superadmin" → approved（superadmin 通用通信）
  3. (from, to) 或 (to, from) 在 ALLOWED_TALK_PAIRS 中 → approved（双向匹配）
  4. (from, "*") 或 ("*", to) 在 ALLOWED_TALK_PAIRS 中 → approved（通配符匹配）
  5. 其余 → not approved, reason="pair_not_allowed"

返回值：dict[str, Any]，含 "approved" (bool)、"from" (str)、"to" (str)、可选 "reason" (str)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: from_agent 参数
#   fields: 参数 from_agent，类型注解 str
#   code: a2a_check.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: to_agent 参数
#   fields: 参数 to_agent，类型注解 str
#   code: a2a_check.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① verify_a2a_pair
#   name_en: verify_a2a_pair
#   intro: 验证两个 agent 之间是否允许 A2A 通信。
#   desc: 验证两个 agent 之间是否允许 A2A 通信。 Args: from_agent: 发起方 agent ID/角色。 to_agent: 接收方 agent ID/角色。 R…；源码 L79-L117
#   inputs: from_agent to_agent
#   outputs: dict[str, Any]
# 层: 输出
# - id: O1
#   name_zh: dict[str, Any]
#   name_en: dict[str, Any]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: scripts.a2a_full_verification ; tests.governance.test_adversarial_contract_atta…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from typing import Any, Final

# 允许通信对（双向匹配）。("*" 通配符表示"任意"）
# 测试校验：("orchestrator", "worker") 和 ("superadmin", "*") 必须在此集合中。
ALLOWED_TALK_PAIRS: Final[set[tuple[str, str]]] = {
    ("orchestrator", "worker"),
    ("orchestrator", "auditor"),
    ("superadmin", "*"),
}

_SUPERADMIN = "superadmin"
_WILDCARD = "*"


def verify_a2a_pair(from_agent: str, to_agent: str) -> dict[str, Any]:
    """验证两个 agent 之间是否允许 A2A 通信。

    Args:
        from_agent: 发起方 agent ID/角色。
        to_agent: 接收方 agent ID/角色。

    Returns:
        dict 含 "approved" (bool)、"from" (str)、"to" (str)，可选 "reason" (str)。
        - approved=True 时可能含 "reason"（如 "self_communication"）。
        - approved=False 时含 "reason"="pair_not_allowed"。
    """
    result: dict[str, Any] = {"from": from_agent, "to": to_agent}

    # 规则 1：自身通信（含双方均为空串）——始终允许
    if from_agent == to_agent:
        result["approved"] = True
        result["reason"] = "self_communication"
        return result

    # 规则 2：superadmin 通用通信——任意方向均允许
    if from_agent == _SUPERADMIN or to_agent == _SUPERADMIN:
        result["approved"] = True
        return result

    # 规则 3：ALLOWED_TALK_PAIRS 双向匹配
    if (from_agent, to_agent) in ALLOWED_TALK_PAIRS or (to_agent, from_agent) in ALLOWED_TALK_PAIRS:
        result["approved"] = True
        return result

    # 规则 4：通配符匹配——(from, "*") 或 ("*", to)
    if (from_agent, _WILDCARD) in ALLOWED_TALK_PAIRS or (_WILDCARD, to_agent) in ALLOWED_TALK_PAIRS:
        result["approved"] = True
        return result

    # 规则 5：未授权对——拒绝
    result["approved"] = False
    result["reason"] = "pair_not_allowed"
    return result


__all__ = [
    "ALLOWED_TALK_PAIRS",
    "verify_a2a_pair",
]
