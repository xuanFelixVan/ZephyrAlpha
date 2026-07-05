# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.identity_verifier
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 身份验证不可绕过;克隆检测必须执行
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_identity_verifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Identity Verifier — D-022-12 Agent身份验证器: session_id+role+capability三元组验证。
"""

from __future__ import annotations


class IdentityVerifier:
    def verify(self, agent_id: str, session_id: str, claimed_role: str, required_capability: str) -> tuple[bool, str]:
        if not session_id or len(session_id) < 5:
            return False, "Invalid session_id"
        allowed_roles = {
            "orchestrator": ["dispatch_task", "invoke_gate"],
            "script_engine": ["report_finding", "scan_code"],
            "knowledge_agent": ["query_knowledge", "write_knowledge"],
            "human_owner": ["override", "emergency_stop", "approve"],
        }
        capabilities = allowed_roles.get(claimed_role, [])
        if required_capability not in capabilities:
            return False, f"Role {claimed_role} lacks capability {required_capability}"
        return True, "OK"

    def validate_session(self, session_id: str) -> bool:
        return bool(session_id and len(session_id) >= 5)
