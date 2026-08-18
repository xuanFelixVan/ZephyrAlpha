# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.detectors.shell_dialect_detector
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests.agent_rbac.test_forensic_b
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] detect() returns ShellDialectResult with detected_dialect/dangerous_patterns/blocked; never raises
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] detect() never raises; returns result with blocked=False on error
# [TESTS] tests/agent_rbac/test_forensic_b.py
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ShellDialectDetector — Shell 方言检测器.

依据蓝图 MOD-INF-018 §:
- 检测命令字符串的 shell 方言（bash/powershell/sh）
- 识别危险模式（rm -rf, IEX, 下载执行等）
- 返回检测结果（方言/危险模式/是否阻断）

治本(2026-07-18): 实现 stub 以匹配 tests/agent_rbac/test_forensic_b.py 契约.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# bash 危险模式（正则，忽略大小写）
_BASH_DANGEROUS_PATTERNS: list[str] = [
    r"rm\s+-rf?\s",
    r"2>&1",
    r"\$\(",                                   # 命令替换
    r"\beval\b",
    r"\bchmod\s+[0-7]{3,4}",
    r"\bchown\b",
    r"\bmkfs\b",
    r"\bdd\b\s+if=",
    r">\s*/dev/sd",
    r"\|\s*sh\b",
    r"\bcurl\b.*\|\s*sh",
    r"\bwget\b.*\|\s*sh",
]

# powershell 危险模式
_POWERSHELL_DANGEROUS_PATTERNS: list[str] = [
    r"IEX\b",
    r"Invoke-Expression",
    r"New-Object\s+Net\.WebClient",
    r"DownloadString",
    r"DownloadFile",
    r"Start-Process",
    r"Set-ExecutionPolicy",
    r"Remove-Item\s+-Recurse",
    r"\bSystem\.Reflection\b",
    r"FromBase64String",
]


@dataclass
class ShellDialectResult:
    """Shell 方言检测结果."""

    detected_dialect: str = "unknown"  # bash / powershell / sh / unknown
    dangerous_patterns: list[str] = field(default_factory=list)
    blocked: bool = False


class ShellDialectDetector:
    """Shell 方言检测器 — 识别命令方言与危险模式."""

    def detect(self, command: str) -> ShellDialectResult:
        """检测命令字符串的方言与危险模式.

        Args:
            command: 待检测的命令字符串

        Returns:
            ShellDialectResult 包含 detected_dialect/dangerous_patterns/blocked
        """
        if not command:
            return ShellDialectResult(detected_dialect="unknown", blocked=False)

        dialect = self._detect_dialect(command)
        patterns = self._find_dangerous_patterns(command, dialect)
        blocked = len(patterns) > 0
        return ShellDialectResult(
            detected_dialect=dialect,
            dangerous_patterns=patterns,
            blocked=blocked,
        )

    def _detect_dialect(self, command: str) -> str:
        """识别命令方言."""
        # powershell 特征
        ps_markers = [
            "IEX", "Invoke-", "New-Object", "-Command", "Set-",
            "Get-", "Remove-Item", "Write-", "$env:", "$PS",
            "DownloadString", "FromBase64String",
        ]
        for marker in ps_markers:
            if marker in command:
                return "powershell"

        # bash/sh 特征
        bash_markers = [
            "rm ", "2>&1", "$(", "`", "chmod", "chown", "mkfs",
            "curl ", "wget ", "dd if=", "| sh", "/bin/",
        ]
        for marker in bash_markers:
            if marker in command:
                return "bash"

        # 通用 shell 特征（管道/重定向）
        if any(c in command for c in ["|", ">", "<"]) or " " in command:
            return "bash"

        return "unknown"

    def _find_dangerous_patterns(self, command: str, dialect: str) -> list[str]:
        """查找危险模式，返回匹配的模式描述列表."""
        found: list[str] = []
        patterns: list[tuple[str, str]] = []

        if dialect == "powershell":
            patterns = [
                (r"IEX\b", "IEX (Invoke-Expression)"),
                (r"Invoke-Expression", "Invoke-Expression"),
                (r"New-Object\s+Net\.WebClient", "New-Object Net.WebClient"),
                (r"DownloadString", "DownloadString"),
                (r"DownloadFile", "DownloadFile"),
                (r"FromBase64String", "FromBase64String"),
                (r"Start-Process", "Start-Process"),
                (r"Set-ExecutionPolicy", "Set-ExecutionPolicy"),
                (r"Remove-Item\s+-Recurse", "Remove-Item -Recurse"),
            ]
        else:
            # bash/sh + 通用危险模式
            patterns = [
                (r"rm\s+-rf?\s", "rm -rf"),
                (r"\beval\b", "eval"),
                (r"\bchmod\s+[0-7]{3,4}", "chmod"),
                (r"\bchown\b", "chown"),
                (r"\bmkfs\b", "mkfs"),
                (r"\bdd\b\s+if=", "dd"),
                (r">\s*/dev/sd", "write to block device"),
                (r"\|\s*sh\b", "pipe to shell"),
                (r"\bcurl\b.*\|\s*sh", "curl | sh"),
                (r"\bwget\b.*\|\s*sh", "wget | sh"),
                (r"\$\(", "command substitution"),
            ]

        for regex, desc in patterns:
            if re.search(regex, command, re.IGNORECASE):
                found.append(desc)
        return found


__all__ = [
    "ShellDialectDetector",
    "ShellDialectResult",
]
