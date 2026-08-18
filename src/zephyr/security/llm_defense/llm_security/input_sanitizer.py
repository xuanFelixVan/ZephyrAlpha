# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] zephyr.security.llm_defense.llm_security.input_sanitizer
# [DOMAIN] D_SECURITY
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
# [A_module] module_id=MOD-LLM_SECURITY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""

InputSanitizer: path whitelist + command whitelist + token budget guard.

Prevents path traversal, command injection, and token budget overruns
for AI agent operations.

Task: T-1-23 | experimental | GLM-5.1
Safety: HIGH
Depends: T-1-04 (task_repo.py)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 待校验文件路径 参数
#   fields: path 相对路径 + mode（read/write）
#   code: validate_path(path, mode) L184
# - id: I2
#   name: 待校验shell命令 参数
#   fields: command 命令字符串
#   code: validate_command(command) L217
# - id: I3
#   name: 待注入LLM的上下文 文本
#   fields: text 任意待注入文本
#   code: validate_llm_context(text) L238
# - id: I4
#   name: Token用量与预算 参数
#   fields: used 已用 + limit 上限 + request 本次请求
#   code: check_token_budget(used, limit, request) L246
# 层: 算法
# - id: A1
#   name_zh: ① 路径白名单校验
#   name_en: InputSanitizer.validate_path
#   intro: 挡路径穿越：危险模式扫描+必须落在root内+写模式查目录白名单
#   desc: 长度≤512 → DANGEROUS_PATTERNS 6类模式（../、\0、;&|`$、$(）→ resolve 后 relative_to(root) 防逃逸 → write 模式再查 ALLOWED_WRITE_DIRS 6目录（L184-215）
#   inputs: I1
#   outputs: 解析后的绝对 Path（不通过抛 PathTraversalError）
#   invariant: fail-closed，任何一步不通过即抛异常
# - id: A2
#   name_zh: ② 命令白名单校验
#   name_en: InputSanitizer.validate_command
#   intro: 挡命令注入：模式扫描+shlex解析+首命令必须在白名单
#   desc: DANGEROUS_PATTERNS 扫描 → shlex.split 解析 → basename(首命令) 查 ALLOWED_COMMANDS（python/pip/git/ruff/mypy/pytest/echo/ls/cat/rg/fd）（L217-236）
#   inputs: I2
#   outputs: 原命令字符串（不通过抛 CommandInjectionError）
# - id: A3
#   name_zh: ③ LLM上下文注入防护
#   name_en: InputSanitizer.validate_llm_context
#   intro: 注入LLM前拦代码执行/提示词注入/凭据泄露三类高危内容
#   desc: 50万字符上限 + _CONTEXT_INJECTION_CHECKS 3组正则（code_execution/prompt_injection/credential_pattern），CT-CE-LSG-001 L1 子集（L238-244）
#   inputs: I3
#   outputs: None（不通过抛 ContextInjectionError）
# - id: A4
#   name_zh: ④ Token预算闸
#   name_en: InputSanitizer.check_token_budget
#   intro: 已用+本次请求超上限即拦截
#   desc: used+request>limit → 抛 TokenBudgetExceededError，否则返回 True（L246-254）
#   inputs: I4
#   outputs: bool
# - id: A5
#   name_zh: ⑤ 文件名清洗
#   name_en: InputSanitizer.sanitize_filename
#   intro: 把文件名里的危险字符替换成下划线
#   desc: 非[\w-.]字符替换为_ → 空名或点开头加 sanitized_ 前缀 → 截断255字符（L256-260）
#   inputs: I1
#   outputs: 清洗后的文件名字符串
# 层: 输出
# - id: O1
#   name_zh: 校验通过的路径/命令/预算结果
#   name_en: Path / command / True
#   intro: 校验通过返回安全值，不通过抛 SanitizationError 系异常（ZA-SC-0017~0021）
#   downstream: 无下游/内部使用（AI agent 操作前置校验，# [CONSUMERS] 头为空）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A5
# I2 --> A2
# I3 --> A3
# I4 --> A4
# A1 --> O1
# A2 --> O1
# A3 --> O1
# A4 --> O1
# A5 --> O1
"""

from __future__ import annotations

import os
import re
import shlex
from pathlib import Path
from typing import Final

ALLOWED_WRITE_DIRS: Final[tuple[str, ...]] = (
    "docs/",
    "scripts/governance/",
    "scripts/hooks/",
    "scripts/migration/",
    ".audit_cache/",
    "src/zephyr/",
)

ALLOWED_COMMANDS: Final[frozenset[str]] = frozenset(
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

DANGEROUS_PATTERNS: Final[tuple[re.Pattern, ...]] = (
    re.compile(r"\.\.[/\\]"),
    re.compile(r"[/\\]\.\.[/\\]"),
    re.compile(r"\0"),
    re.compile(r"[;&|`$]"),
    re.compile(r"\$\("),
    re.compile(r"!\s*"),
)


class SanitizationError(Exception):
    """输入清洗器基础设施异常基类（InputSanitizer 所有异常由此派生）。"""

    error_code = "ZA-SC-0017"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class PathTraversalError(SanitizationError):
    """检测到路径穿越攻击（目标路径不在白名单目录范围内）。"""

    error_code = "ZA-SC-0018"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class CommandInjectionError(SanitizationError):
    """检测到命令注入攻击（输入含 OS 命令拼接特征如 `$(...)`、`;` 等）。"""

    error_code = "ZA-SC-0019"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class TokenBudgetExceededError(SanitizationError):
    """输入 Token 预算超标（超过 safety limits 配置的 max 阈值）。"""

    error_code = "ZA-SC-0020"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class ContextInjectionError(SanitizationError):
    """CT-CE-LSG-001 L1：即将注入 LLM 的上下文中含高危模式（代码执行/越权指令/疑似凭据）。"""

    error_code = "ZA-SC-0021"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


# L1 上下文注入防护：对标 MOD-MASTER CT-CE-LSG-001 input_sanitizer 检查项
_CONTEXT_INJECTION_CHECKS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "code_execution",
        re.compile(
            r"__import__\s*\(|eval\s*\(|exec\s*\(|compile\s*\(|"
            r"subprocess\s*\.|os\.system\s*\(|importlib\.import_module\s*\(",
            re.IGNORECASE,
        ),
    ),
    (
        "prompt_injection",
        re.compile(
            r"(?is)(ignore\s+(all\s+)?(previous|prior|above)\s+"
            r"(instructions|rules|directives)|disregard\s+(the\s+)?(above|previous)|"
            r"you\s+are\s+now\s+(a|an|the)\s+|"
            r"<\|im_start\|>|<\|assistant\|>|"
            r"\[INST\]|\[/INST\]|\bsystem\s*:\s*(override|prompt)\b)",
        ),
    ),
    (
        "credential_pattern",
        re.compile(
            r"(?i)(\bsk-[a-zA-Z0-9]{20,}|"
            r"api[_-]?key\s*[:=]\s*['\"]?\s*[a-zA-Z0-9_\-\.+]{16,}|"
            r"password\s*[:=]\s*['\"]?\s*[^\s'\"]{8,}|"
            r"bearer\s+[a-zA-Z0-9_\-\.]{24,}|"
            r"-----BEGIN\s+(RSA\s+|OPENSSH\s+|EC\s+)?PRIVATE\s+KEY-----)",
        ),
    ),
)

_MAX_LLM_CONTEXT_CHARS = 500_000


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
                raise PathTraversalError("Dangerous pattern in path")

        resolved = (self._root / path).resolve()

        try:
            resolved.relative_to(self._root)
        except ValueError:
            raise PathTraversalError("Path escapes root") from None

        if mode == "write":
            rel = str(resolved.relative_to(self._root)).replace("\\", "/")
            allowed = False
            for d in self._allowed_write_dirs:
                if rel.startswith(d) or rel == d.rstrip("/"):
                    allowed = True
                    break
            if not allowed:
                raise PathTraversalError(
                    f"Write path not in allowed dirs (allowed: {self._allowed_write_dirs})"
                )

        return resolved

    def validate_command(self, command: str) -> str:
        for pat in DANGEROUS_PATTERNS:
            if pat.search(command):
                raise CommandInjectionError(f"Dangerous pattern in command: {command}")

        try:
            parts = shlex.split(command)
        except ValueError as e:
            raise CommandInjectionError(f"Unparseable command: {command} ({e})") from e

        if not parts:
            raise CommandInjectionError("Empty command")

        base_cmd = os.path.basename(parts[0])
        if base_cmd not in self._allowed_commands:
            raise CommandInjectionError(
                f"Command not in whitelist: {base_cmd} (allowed: {sorted(self._allowed_commands)})"
            )

        return command

    def validate_llm_context(self, text: str) -> None:
        """上下文注入前安全校验（CT-CE-LSG-001 L1 子集）。"""
        if len(text) > _MAX_LLM_CONTEXT_CHARS:
            raise ContextInjectionError(f"LLM context too large: {len(text)} chars (max {_MAX_LLM_CONTEXT_CHARS})")
        for name, pattern in _CONTEXT_INJECTION_CHECKS:
            if pattern.search(text):
                raise ContextInjectionError(f"Blocked pattern ({name}) in LLM context")

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


__all__ = [  # noqa: n114-final  n114-final豁免: __all__是Python导出约定且本文件运行时动态append，Final标注不适用
    "ALLOWED_COMMANDS",
    "ALLOWED_WRITE_DIRS",
    "DANGEROUS_PATTERNS",
    "CommandInjectionError",
    "ContextInjectionError",
    "InputSanitizer",
    "PathTraversalError",
    "SanitizationError",
    "TokenBudgetExceededError",
]
