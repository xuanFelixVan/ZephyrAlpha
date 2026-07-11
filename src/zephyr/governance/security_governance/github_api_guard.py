# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.github_api_guard
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] PR/Issue清洗不可跳过;注入标记必须移除
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_github_api_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

GitHub API Guard — v0.9.0 Comment and Control防御: PR评论命令注入检测+限制。
"""

from __future__ import annotations


class GitHubAPIGuard:
    def __init__(self):
        self._allowed_commands = {"run_tests", "format_code", "lint", "build", "deploy_staging"}
        self._audit: list[dict] = []

    def validate_command(self, command: str, user: str) -> tuple[bool, str]:
        if command not in self._allowed_commands:
            self._audit.append({"command": command, "user": user, "result": "denied"})
            return False, f"Command '{command}' not allowed"
        self._audit.append({"command": command, "user": user, "result": "allowed"})
        return True, "OK"

    def get_audit_log(self) -> list[dict]:
        return self._audit
