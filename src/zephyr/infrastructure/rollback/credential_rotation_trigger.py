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
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CredentialRotationDetector — 回滚后凭据泄露检测（仅检测，不轮换）。

依据: 蓝图 MOD-INF-021 §7 Phase 10 + §6.17 B126 + exit code 43

回滚可能恢复含旧凭据的配置文件。
回滚后自动扫描敏感文件中的凭据模式——检测泄露并通知人工轮换。
若检测到凭据泄露 -> exit 43 (CREDENTIAL_LEAK_DETECTED)。

5.62.5 治本（名实分离）：本类从不执行任何轮换操作（credentials_rotated 恒为 0），
原类名 CredentialRotationTrigger 与 scan_and_rotate 名不副实。
判定依据：项目的 SecretRotation（feedback_loop/security/secret_rotation.py）仅管理
registry 跟踪的内存密钥生命周期，无法轮换第三方文件凭据（API key 轮换必须在
provider 侧执行，本地改写 .env 不等于服务端轮换，反而破坏可用性）——
故本类正名为 Detector 语义：仅检测 + 通知（notify_rotation_needed），轮换为人工动作。
原名 CredentialRotationTrigger / scan_and_rotate 保留为向后兼容别名（蓝图/YAML/测试引用）。
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
    credentials_rotated: int  # 恒为 0——本检测器仅检测不轮换（5.62.5 名实分离），字段保留供兼容
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


class CredentialRotationDetector:
    """凭据泄露检测器（仅检测，不轮换——5.62.5 治本名实分离）。

    扫描 SENSITIVE_FILES 中的凭据模式，检测泄露并以 exit 43 通知人工轮换。
    轮换本身 MUST 在 provider 侧人工执行（本地无法轮换第三方凭据）。
    """

    EXIT_CODE_CREDENTIAL_LEAK: int = 43
    SENSITIVE_FILES: list[str] = [".env", ".env.local", "config.yaml", "config.yml", "settings.py", "secrets.yaml"]

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def project_root(self):
        """只读：project_root（Stage 4 公共化）。"""
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        """写入：project_root（Stage 4 公共化）。"""
        self._project_root = value

    def scan(self) -> CredentialScanResult:
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
            credentials_rotated=0,  # 仅检测不轮换——轮换由 notify_rotation_needed 通知人工执行
            leaks_detected=leaks_detected,
            exit_code=exit_code,
            details=details,
        )

    def scan_and_rotate(self) -> CredentialScanResult:
        """向后兼容别名——真源为 scan()（5.62.5：仅检测不轮换）。"""
        return self.scan()

    @staticmethod
    def notify_rotation_needed(reason: str) -> dict[str, Any]:
        return {
            "action": "CREDENTIAL_ROTATION_REQUIRED",
            "reason": reason,
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "instructions": "Manually rotate all detected credentials. Do NOT commit old values.",
        }


# 5.62.5 治本：向后兼容别名（蓝图/YAML/测试仍引用旧名），真源为 CredentialRotationDetector
CredentialRotationTrigger = CredentialRotationDetector
