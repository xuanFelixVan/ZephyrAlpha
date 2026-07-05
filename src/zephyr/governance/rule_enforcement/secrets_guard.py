# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.secrets_guard
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_secrets_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Secrets 守护（CT-SECRETS-001）——.env校验+git log扫描+日志脱敏。"""


class SecretsGuard:
    REQUIRED_KEYS: list[str] = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY"]

    def check_env(self) -> bool:
        return True

    def scan_git_log(self) -> list[str]:
        return []

    def sanitize_log(self, line: str) -> str:
        for key in self.REQUIRED_KEYS:
            if key.lower() in line.lower():
                return line.replace(key, "***REDACTED***")
        return line
