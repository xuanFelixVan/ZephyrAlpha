"""InputSanitizer: path whitelist + command whitelist + token budget guard.

Prevents path traversal, command injection, and token budget overruns
for AI agent operations.

Task: T-1-23 | Phase 1 | GLM-5.1
Safety: HIGH
Depends: T-1-04 (task_repo.py)
"""

from __future__ import annotations

import os
import re
import shlex
from pathlib import Path

ALLOWED_WRITE_DIRS: tuple[str, ...] = (
    "docs/",
    "scripts/governance/",
    "scripts/hooks/",
    "scripts/migration/",
    ".audit_cache/",
    "src/zephyr/",
)

ALLOWED_COMMANDS: frozenset[str] = frozenset(
    {
        "python",
        "pip",
        "git",
        "ruff",
        "mypy",
        "pytest",
        "echo",
        "ls",
        "cat",
        "rg",
        "fd",
    }
)

DANGEROUS_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"\.\.[/\\]"),
    re.compile(r"[/\\]\.\.[/\\]"),
    re.compile(r"\0"),
    re.compile(r"[;&|`$]"),
    re.compile(r"\$\("),
    re.compile(r"!\s*"),
)

class SanitizationError(Exception):
    """输入清洗器基础设施异常基类（InputSanitizer 所有异常由此派生）。"""

    pass

class PathTraversalError(SanitizationError):
    """检测到路径穿越攻击（目标路径不在白名单目录范围内）。"""

    pass

class CommandInjectionError(SanitizationError):
    """检测到命令注入攻击（输入含 OS 命令拼接特征如 `$(...)`、`;` 等）。"""

    pass

class TokenBudgetExceededError(SanitizationError):
    """输入 Token 预算超标（超过 safety limits 配置的 max 阈值）。"""

    pass

class InputSanitizer:
    """Validates file paths and shell commands against whitelists.

    Usage::

        sanitizer = InputSanitizer(root="/path/to/project")
        sanitizer.validate_path("docs/foo.md", mode="write")
        sanitizer.validate_command("python scripts/foo.py")
        sanitizer.check_token_budget(used=5000, limit=10000)
    """

    def __init__(
        self,
        root: str,
        allowed_write_dirs: tuple[str, ...] | None = None,
        allowed_commands: frozenset[str] | None = None,
        max_path_length: int = 512,
    ) -> None:
        self._root = Path(root).resolve()
        self._allowed_write_dirs = allowed_write_dirs or ALLOWED_WRITE_DIRS
        self._allowed_commands = allowed_commands or ALLOWED_COMMANDS
        self._max_path_length = max_path_length

    def validate_path(
        self,
        path: str,
        mode: str = "read",
    ) -> Path:
        if len(path) > self._max_path_length:
            raise PathTraversalError(f"Path too long: {len(path)} > {self._max_path_length}")

        for pat in DANGEROUS_PATTERNS:
            if pat.search(path):
                raise PathTraversalError(f"Dangerous pattern in path: {path}")

        resolved = (self._root / path).resolve()

        try:
            resolved.relative_to(self._root)
        except ValueError:
            raise PathTraversalError(f"Path escapes root: {path}")

        if mode == "write":
            rel = str(resolved.relative_to(self._root)).replace("\\", "/")
            allowed = False
            for d in self._allowed_write_dirs:
                if rel.startswith(d) or rel == d.rstrip("/"):
                    allowed = True
                    break
            if not allowed:
                raise PathTraversalError(
                    f"Write path not in allowed dirs: {path} (allowed: {self._allowed_write_dirs})"
                )

        return resolved

    def validate_command(self, command: str) -> str:
        for pat in DANGEROUS_PATTERNS:
            if pat.search(command):
                raise CommandInjectionError(f"Dangerous pattern in command: {command}")

        try:
            parts = shlex.split(command)
        except ValueError as e:
            raise CommandInjectionError(f"Unparseable command: {command} ({e})")

        if not parts:
            raise CommandInjectionError("Empty command")

        base_cmd = os.path.basename(parts[0])
        if base_cmd not in self._allowed_commands:
            raise CommandInjectionError(
                f"Command not in whitelist: {base_cmd} (allowed: {sorted(self._allowed_commands)})"
            )

        return command

    def check_token_budget(
        self,
        used: int,
        limit: int,
        request: int = 0,
    ) -> bool:
        if used + request > limit:
            raise TokenBudgetExceededError(f"Token budget exceeded: used={used} + request={request} > limit={limit}")
        return True

    def sanitize_filename(self, filename: str) -> str:
        filename = re.sub(r"[^\w\-.]", "_", filename)
        if not filename or filename.startswith("."):
            filename = f"sanitized_{filename}"
        return filename[:255]
