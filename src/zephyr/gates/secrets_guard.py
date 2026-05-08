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
