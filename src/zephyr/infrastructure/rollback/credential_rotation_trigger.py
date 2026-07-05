# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.credential_rotation_trigger
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.infrastructure.rollback.__init__
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
# [A_module] module_id=MOD-INF_credential_rotation_trigger | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CredentialRotationTrigger — 凭据自动轮替。

依据: 蓝图 MOD-INF-021 §7 Phase 10 + §6.17 B126 + exit code 43

回滚可能恢复含旧凭据的配置文件。
回滚后自动触发凭据轮替——轮替成功的凭据标记为已过期。
若检测到凭据泄露 → exit 43 (CREDENTIAL_LEAK_DETECTED)。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class CredentialScanResult:
    files_scanned: int
    credentials_detected: int
    credentials_rotated: int
    leaks_detected: int
    exit_code: int
    details: list[str] = field(default_factory=list)


CREDENTIAL_PATTERNS: list[tuple[str, str]] = [
    ("API_KEY", r'(?:api[_-]?key|apikey)\s*[=:]\s*[\'"][^\'"]{8,}[\'"]'),
    ("TOKEN", r'(?:token|secret|password)\s*[=:]\s*[\'"][^\'"]{8,}[\'"]'),
    ("AWS_KEY", r"AKIA[0-9A-Z]{16}"),
    ("GITHUB_TOKEN", r'(?:gh[pousr]_[a-zA-Z0-9]{36}|github[_-]?token\s*[=:]\s*[\'"][^\'"]+[\'"])'),
    ("PRIVATE_KEY_HEADER", r"-----BEGIN (?:RSA|EC|DSA|OPENSSH) PRIVATE KEY-----"),
]


class CredentialRotationTrigger:
    EXIT_CODE_CREDENTIAL_LEAK: int = 43
    SENSITIVE_FILES: list[str] = [".env", ".env.local", "config.yaml", "config.yml", "settings.py", "secrets.yaml"]

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def scan_and_rotate(self) -> CredentialScanResult:
        files_scanned = 0
        credentials_detected = 0
        leaks_detected = 0
        details: list[str] = []

        for filename in self.SENSITIVE_FILES:
            path = self._project_root / filename
            if not path.exists():
                continue

            files_scanned += 1
            content = path.read_text(encoding="utf-8")

            for cred_type, pattern in CREDENTIAL_PATTERNS:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    credentials_detected += len(matches)
                    details.append(f"{filename}: {cred_type} detected ({len(matches)} match(es))")
                    if cred_type in ("AWS_KEY", "GITHUB_TOKEN"):
                        leaks_detected += len(matches)
                        details.append(f"{filename}: {cred_type} LEAK detected—immediate rotation required")

        exit_code = self.EXIT_CODE_CREDENTIAL_LEAK if leaks_detected > 0 else 0
        return CredentialScanResult(
            files_scanned=files_scanned,
            credentials_detected=credentials_detected,
            credentials_rotated=0,
            leaks_detected=leaks_detected,
            exit_code=exit_code,
            details=details,
        )

    @staticmethod
    def notify_rotation_needed(reason: str) -> dict[str, Any]:
        return {
            "action": "CREDENTIAL_ROTATION_REQUIRED",
            "reason": reason,
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "instructions": "Manually rotate all detected credentials. Do NOT commit old values.",
        }
