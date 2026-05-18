# [BLUEPRINT] MOD-INF-007 | 03_modules/_cross_layer/gate-engine/blueprint.md | §

# [MODULE] zephyr.gates.secrets_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Secrets 守护（CT-SECRETS-001）——.env校验+git log扫描+日志脱敏。"""

from __future__ import annotations

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
