# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.shell_dialect_detector

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Shell方言检测器——识别bash/powershell/cmd/python/perl方言防止shell注入."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ShellDialectResult(BaseModel):
    command: str
    detected_dialect: str = "unknown"
    dangerous_patterns: list[str] = []
    blocked: bool = False


DANGEROUS_SHELL_PATTERNS: dict[str, list[str]] = {
    "bash": ["$(...)", "`...`", ">/dev/null", "2>&1", "chmod +x", "rm -rf", "dd if=", "mkfifo"],
    "powershell": ["Invoke-Expression", "IEX(", "Start-Process", "iex(", "::", "System.Net.WebClient"],
    "cmd": ["%SYSTEMROOT%", "del /f", "reg add", "sc stop", "net user"],
    "python": ["__import__(", "eval(", "exec(", "compile(", "subprocess.Popen"],
    "perl": ["system(", "exec(", "qx/", "open(", "eval{"],
}


class ShellDialectDetector:
    def detect(self, command: str) -> ShellDialectResult:
        cmd_lower = command.lower()
        dialect = self._detect_dialect(cmd_lower)
        patterns = DANGEROUS_SHELL_PATTERNS.get(dialect, [])
        matched = [p for p in patterns if p.lower() in cmd_lower]

        return ShellDialectResult(
            command=command,
            detected_dialect=dialect,
            dangerous_patterns=matched,
            blocked=len(matched) > 0,
        )

    def _detect_dialect(self, cmd: str) -> str:
        if "iex(" in cmd or "invoke-expression" in cmd or "start-process" in cmd:
            return "powershell"
        if "%" in cmd and ("systemroot" in cmd or "systemdrive" in cmd):
            return "cmd"
        if "$(" in cmd or "`" in cmd or "2>&1" in cmd or "chmod" in cmd:
            return "bash"
        if "eval(" in cmd or "exec(" in cmd or "__import__(" in cmd:
            return "python"
        if "qx/" in cmd or "system(" in cmd or "exec{" in cmd:
            return "perl"
        return "unknown"
