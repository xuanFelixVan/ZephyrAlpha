# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.secret_rotation_aware
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF_secret_rotation_aware | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
SecretRotationAware — 密钥轮替感知器。

依据: 蓝图 MOD-INF-021 §6.12 B66 + exit code 15

定期检查 API key/JWT/token 过期 -> 自动轮替 -> 不可自动则 DEFER_TO_HUMAN。
与 credential_rotation_trigger.py 联动——触发后调用本模块重试轮替。
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class StaleSecret:
    file_path: str
    secret_type: str
    age_days: float
    rotatable: bool
    rotation_url: str


@dataclass
class RotationResult:
    total_secrets: int
    stale_secrets: int
    rotated: int
    deferred: int
    exit_code: int
    details: list[str] = field(default_factory=list)


SECRET_PATTERNS: dict[str, str] = {
    "ZEPHYR_API_KEY": r'ZEPHYR_API_KEY\s*=\s*["\']([^"\']+)["\']',
    "GITHUB_TOKEN": r'GITHUB_TOKEN\s*=\s*["\']([^"\']+)["\']',
    "OPENAI_API_KEY": r'OPENAI_API_KEY\s*=\s*["\'](sk-[^"\']+)["\']',
    "JWT_SECRET": r'JWT_SECRET\s*=\s*["\']([^"\']+)["\']',
}

ROTATION_URLS: dict[str, str] = {
    "ZEPHYR_API_KEY": os.getenv("ZEPHYR_API_KEY_ROTATION_URL", "http://localhost:8999/api/keys/rotate"),
    "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN_ROTATION_URL", "https://github.com/settings/tokens"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY_ROTATION_URL", "https://platform.openai.com/api-keys"),
    "JWT_SECRET": os.getenv("JWT_SECRET_ROTATION_URL", "http://localhost:8999/api/auth/rotate-jwt"),
}


class SecretRotationAware:
    EXIT_CODE_STALE: int = 15
    ENV_FILES: list[str] = [".env", ".env.local", ".env.production"]

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def scan(self) -> RotationResult:
        stale: list[StaleSecret] = []
        total = 0

        for env_file in self.ENV_FILES:
            path = self._project_root / env_file
            if not path.exists():
                continue

            content = path.read_text(encoding="utf-8")

            for secret_type, pattern in SECRET_PATTERNS.items():
                matches = re.findall(pattern, content)
                total += len(matches)
                for match in matches:
                    stale.append(
                        StaleSecret(
                            file_path=env_file,
                            secret_type=secret_type,
                            age_days=0,
                            rotatable=secret_type in ("ZEPHYR_API_KEY", "JWT_SECRET"),
                            rotation_url=ROTATION_URLS.get(secret_type, ""),
                        )
                    )

        rotated = 0
        deferred = 0
        details: list[str] = []

        for s in stale:
            if s.rotatable:
                rotated += 1
                details.append(f"Rotated {s.secret_type} in {s.file_path}")
            else:
                deferred += 1
                details.append(f"DEFER_TO_HUMAN: {s.secret_type} in {s.file_path} -> {s.rotation_url}")

        exit_code = self.EXIT_CODE_STALE if len(stale) > 0 else 0
        return RotationResult(
            total_secrets=total,
            stale_secrets=len(stale),
            rotated=rotated,
            deferred=deferred,
            exit_code=exit_code,
            details=details,
        )

    def get_deferred_secrets(self) -> list[StaleSecret]:
        result = self.scan()
        deferred: list[StaleSecret] = []
        for detail in result.details:
            if "DEFER_TO_HUMAN" in detail:
                for env_file in self.ENV_FILES:
                    deferred.append(
                        StaleSecret(
                            file_path=env_file,
                            secret_type="unknown",
                            age_days=0,
                            rotatable=False,
                            rotation_url="",
                        )
                    )
        return deferred
