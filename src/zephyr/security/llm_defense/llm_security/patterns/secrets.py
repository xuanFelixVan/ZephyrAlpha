# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] zephyr.security.llm_defense.llm_security.patterns.secrets
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.shared.security.secrets
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SEC_secrets | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from typing import Final

import re
from re import Pattern
from typing import Any

_SECRET_PATTERNS: list[dict[str, Any]] = [
    {
        "name": "openai_api_key",
        "pattern": r"sk-(proj-)?[a-zA-Z0-9]{20,}",
        "category": "api_key",
        "severity": "critical",
        "action": "block",
    },
    {
        "name": "aws_access_key",
        "pattern": r"AKIA[0-9A-Z]{16}",
        "category": "api_key",
        "severity": "critical",
        "action": "block",
    },
    {
        "name": "aws_secret_key",
        "pattern": r"(?:aws_secret_access_key|secret_key|SecretAccessKey)\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{40}['\"]?",
        "category": "api_key",
        "severity": "critical",
        "action": "block",
    },
    {
        "name": "github_token",
        "pattern": r"gh[pousr]_[A-Za-z0-9_]{36,}",
        "category": "api_key",
        "severity": "critical",
        "action": "block",
    },
    {
        "name": "slack_token",
        "pattern": r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}(-[a-zA-Z0-9]{24})?",
        "category": "api_key",
        "severity": "critical",
        "action": "block",
    },
    {
        "name": "stripe_key",
        "pattern": r"sk_(live|test)_[0-9a-zA-Z]{24,}",
        "category": "api_key",
        "severity": "critical",
        "action": "block",
    },
    {
        "name": "google_api_key",
        "pattern": r"AIza[0-9A-Za-z_-]{35}",
        "category": "api_key",
        "severity": "critical",
        "action": "block",
    },
    {
        "name": "private_key_pem",
        "pattern": r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
        "category": "cryptographic",
        "severity": "critical",
        "action": "block",
    },
    {
        "name": "password_inline",
        "pattern": r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"]?[^\s'\"]{8,}['\"]?",
        "category": "credential",
        "severity": "high",
        "action": "block",
    },
    {
        "name": "secret_inline",
        "pattern": r"(?i)(secret)\s*[=:]\s*['\"]?[^\s'\"]{4,}['\"]?",
        "category": "credential",
        "severity": "high",
        "action": "block",
    },
    {
        "name": "bearer_token",
        "pattern": r"Bearer\s+[a-zA-Z0-9_\-\.]+",
        "category": "token",
        "severity": "high",
        "action": "mask",
    },
    {
        "name": "jwt_token",
        "pattern": r"eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*",
        "category": "token",
        "severity": "high",
        "action": "mask",
    },
    {
        "name": "email_address",
        "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "category": "pii",
        "severity": "medium",
        "action": "mask",
    },
    {
        "name": "phone_number",
        "pattern": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "category": "pii",
        "severity": "medium",
        "action": "mask",
    },
    {
        "name": "ssn",
        "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
        "category": "pii",
        "severity": "high",
        "action": "mask",
    },
    {
        "name": "credit_card",
        "pattern": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b",
        "category": "pii",
        "severity": "critical",
        "action": "block",
    },
    {
        "name": "ip_address",
        "pattern": r"\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
        "category": "network",
        "severity": "low",
        "action": "flag",
    },
    {
        "name": "database_url",
        "pattern": r"(?i)(postgres|mysql|mongodb|redis)://[^:]+:[^@]+@[^/]+/[^\s\"']+",
        "category": "credential",
        "severity": "critical",
        "action": "block",
    },
    {
        "name": "internal_hostname",
        "pattern": r"(?i)\b(?:internal|prod|staging|dev|admin|api)\.(?:zephyr|internal|corp)\.[a-z]{2,}\b",
        "category": "internal",
        "severity": "low",
        "action": "flag",
    },
    {
        "name": "internal_path",
        "pattern": r"(?i)(/etc/shadow|/etc/passwd|/var/log/|/proc/|C:\\\\Windows\\\\System32)",
        "category": "internal",
        "severity": "medium",
        "action": "flag",
    },
    {
        "name": "env_var_secret",
        "pattern": r"(?i)(SECRET_KEY|API_KEY|AUTH_TOKEN|PRIVATE_KEY)\s*=\s*['\"]?[^\s'\"]+['\"]?",
        "category": "credential",
        "severity": "critical",
        "action": "block",
    },
    {
        "name": "telegram_bot_token",
        "pattern": r"\d{9,10}:[A-Za-z0-9_-]{35}",
        "category": "api_key",
        "severity": "critical",
        "action": "block",
    },
    {
        "name": "discord_webhook",
        "pattern": r"https://discord\.com/api/webhooks/\d{18,19}/[A-Za-z0-9_-]{68}",
        "category": "api_key",
        "severity": "high",
        "action": "mask",
    },
    {
        "name": "azure_storage_key",
        "pattern": r"DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[^;]+;",
        "category": "api_key",
        "severity": "critical",
        "action": "block",
    },
    {
        "name": "npm_token",
        "pattern": r"npm_[A-Za-z0-9]{36}",
        "category": "api_key",
        "severity": "high",
        "action": "mask",
    },
    {
        "name": "docker_config_auth",
        "pattern": r"\"auth\"\s*:\s*\"[A-Za-z0-9+/=]+\"",
        "category": "credential",
        "severity": "high",
        "action": "mask",
    },
    {
        "name": "s3_bucket_url",
        "pattern": r"s3://[a-z0-9-]+(/[^\s\"']*)",
        "category": "internal",
        "severity": "low",
        "action": "flag",
    },
    {
        "name": "ssh_private_key",
        "pattern": r"-----BEGIN OPENSSH PRIVATE KEY-----",
        "category": "cryptographic",
        "severity": "critical",
        "action": "block",
    },
]

PRECOMPILED_SECRET_PATTERNS: Final[list[tuple[str, Pattern, str, str]]] = []
for entry in _SECRET_PATTERNS:
    try:
        PRECOMPILED_SECRET_PATTERNS.append(
            (
                entry["name"],
                re.compile(entry["pattern"]),
                entry.get("action", "flag"),
                entry.get("severity", "low"),
            )
        )
    except re.error:
        continue


def scan_secrets(content: str) -> list[dict[str, Any]]:
    hits = []
    for name, pattern, action, severity in PRECOMPILED_SECRET_PATTERNS:
        for match in pattern.finditer(content):
            hits.append(
                {
                    "name": name,
                    "match": match.group()[:120],
                    "action": action,
                    "severity": severity,
                    "start": match.start(),
                    "end": match.end(),
                }
            )
    return hits


# Re-export from canonical location (zephyr.shared.security.secrets)
from zephyr.shared.security.secrets import (  # noqa: F401
    SECRET_INDICATOR_PATTERNS,
    DotEnvSecretProvider,
    EnvSecretProvider,
    SecretProvider,
    SecretsError,
    sanitize_secret,
)
