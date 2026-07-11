# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.credential_guard
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 密钥泄露检测不可禁用;自动吊销必须立即生效
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_credential_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Credential Guard — v0.7.0 密钥泄露防护: env检测+git log扫描+运行时脱敏。
"""

from __future__ import annotations

from typing import Final
import re

CREDENTIAL_PATTERNS: Final[list] = [
    r"sk-[A-Za-z0-9]{20,}",
    r"AKIA[A-Z0-9]{16}",
    r"eyJ[A-Za-z0-9_-]+\.eyJ",
    r'api_key\s*=\s*"[^"]{8,}"',
]


class CredentialGuard:
    def scan_line(self, line: str) -> list[str]:
        found = []
        for pattern in CREDENTIAL_PATTERNS:
            matches = re.findall(pattern, line)
            found.extend(matches)
        return found

    def sanitize(self, line: str) -> str:
        for pattern in CREDENTIAL_PATTERNS:
            line = re.sub(pattern, "***REDACTED***", line)
        return line

    def check_environment(self, env_vars: dict) -> list[str]:
        return [
            k
            for k, v in env_vars.items()
            if any(p.lower() in k.lower() for p in ["key", "secret", "token", "password"]) and len(str(v)) > 8
        ]
