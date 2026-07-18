# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md
# [MODULE] zephyr.security.access_control.detectors.shell_dialect_detector
# [DOMAIN] D_SECURITY
# [MATURITY] production
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""ShellDialectDetector - shell dialect & dangerous pattern detection."""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ShellDialectResult:
    detected_dialect: str = "unknown"
    dangerous_patterns: list[str] = field(default_factory=list)
    blocked: bool = False


class ShellDialectDetector:
    def detect(self, command: str) -> ShellDialectResult:
        if not command:
            return ShellDialectResult(detected_dialect="unknown", blocked=False)
        dialect = self._detect_dialect(command)
        patterns = self._find_dangerous_patterns(command, dialect)
        blocked = len(patterns) > 0
        return ShellDialectResult(detected_dialect=dialect, dangerous_patterns=patterns, blocked=blocked)

    def _detect_dialect(self, command: str) -> str:
        ps_markers = ["IEX", "Invoke-", "New-Object", "-Command", "Set-", "Get-", "Remove-Item", "Write-", "DownloadString", "FromBase64String"]
        for marker in ps_markers:
            if marker in command:
                return "powershell"
        bash_markers = ["rm ", "2>&1", "chmod", "chown", "mkfs", "curl ", "wget ", "dd if=", "| sh", "/bin/"]
        for marker in bash_markers:
            if marker in command:
                return "bash"
        if any(c in command for c in ["|", ">", "<"]) or " " in command:
            return "bash"
        return "unknown"

    def _find_dangerous_patterns(self, command: str, dialect: str) -> list[str]:
        found: list[str] = []
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


__all__ = ["ShellDialectDetector", "ShellDialectResult"]