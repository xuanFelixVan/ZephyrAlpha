# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.capability_check
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests.governance.test_adversarial_contract_attacks ; tests.governance.test_gct_integration ; tests.governance.test_p0_u1_contract_smoke ; tests.governance.test_p0_u2_input_validation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] verify_capability_scope returns dict with approved/agent_id/capabilities-or-reason; restricted capabilities always denied; empty capabilities denied; >MAX_CAPABILITIES denied; rule priority restricted>empty>too_many>approved
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Agent capability scope verification — 拒绝受限能力声明、空能力声明及能力数量超限。

治本（2026-07-18）：原模块为 stub（verify_capability_scope raise NotImplementedError），
现根据 tests/capability/test_capability_check.py 及
tests/governance/security/test_adversarial_contract_attacks.py 的契约定义实现完整逻辑。

契约规则（由测试定义，按优先级排序）：
  1. 受限能力优先：若 capabilities 中任一属于 RESTRICTED_CAPABILITIES
     → denied, reason="restricted_capabilities_claimed: <cap1>, <cap2>, ..."
  2. 空能力：若 capabilities == []
     → denied, reason="no_capabilities_claimed"
  3. 能力数量超限：若 len(capabilities) > MAX_CAPABILITIES
     → denied, reason="too_many_capabilities"
  4. 合法：approved=True，返回 agent_id 和 capabilities

返回值：dict[str, Any]
  - approved=True 时含 "agent_id" (str) 和 "capabilities" (list[str])
  - approved=False 时含 "reason" (str)
"""

from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from zephyr.autonomy_core.skill_rbac_registry import AgentCapability

# 单个 agent 可声明的最大 capability 数量。
# 测试契约：15 个 capabilities 被拒（too_many），MAX_CAPABILITIES 个通过。
MAX_CAPABILITIES: Final[int] = 10

# 受限 capability 关键词——任何 agent 不得声明。
# 测试契约：sudo/root/destroy/purge/admin_override 任一出现即拒绝。
RESTRICTED_CAPABILITIES: Final[set[str]] = {
    "sudo",
    "root",
    "destroy",
    "purge",
    "admin_override",
}


def verify_capability_scope(cap: "AgentCapability") -> dict[str, Any]:
    """验证 agent 声明的 capability 集合是否在合法范围内。

    Args:
        cap: AgentCapability 实例，含 agent_id (str) 和 capabilities (list[str])。

    Returns:
        dict 含 "approved" (bool)。
        - approved=True 时附 "agent_id" (str) 和 "capabilities" (list[str])。
        - approved=False 时附 "reason" (str)，可能值：
          * "restricted_capabilities_claimed: <caps>" — 含受限能力
          * "no_capabilities_claimed" — 能力列表为空
          * "too_many_capabilities" — 能力数量超过 MAX_CAPABILITIES
    """
    claimed = list(cap.capabilities)
    agent_id = cap.agent_id

    # 规则 1（最高优先级）：受限能力检测
    hit_restricted = [c for c in claimed if c in RESTRICTED_CAPABILITIES]
    if hit_restricted:
        return {
            "approved": False,
            "reason": f"restricted_capabilities_claimed: {', '.join(hit_restricted)}",
        }

    # 规则 2：空能力检测
    if not claimed:
        return {
            "approved": False,
            "reason": "no_capabilities_claimed",
        }

    # 规则 3：能力数量超限检测
    if len(claimed) > MAX_CAPABILITIES:
        return {
            "approved": False,
            "reason": "too_many_capabilities",
        }

    # 规则 4：合法——批准
    return {
        "approved": True,
        "agent_id": agent_id,
        "capabilities": claimed,
    }


__all__ = [
    "MAX_CAPABILITIES",
    "RESTRICTED_CAPABILITIES",
    "verify_capability_scope",
]
