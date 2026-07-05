# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.guards.input_guard
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] dangerous cmd patterns always blocked; path traversal always blocked; safe params allowed
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check_params() never raises; returns InputCheckResult enum member
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_input_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""InputGuard — 输入参数守卫.

依据蓝图 MOD-INF-018 §3:
- 检测危险命令模式（rm -rf / 等）
- 检测路径穿越攻击（../../../etc/passwd）
- 安全参数放行
"""

from __future__ import annotations

import base64
import re
from enum import Enum
from typing import Any


class InputCheckResult(str, Enum):
    """输入检查结果枚举."""

    ALLOW = "ALLOW"
    BLOCKED = "BLOCKED"
    SANITIZED = "SANITIZED"


# 向后兼容别名（原 stub 导出名）
InputDecision = InputCheckResult


DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"rm\s+-rf\s+~",
    r"mkfs\.",
    r"dd\s+if=",
    r":\(\)\{.*\};",
    r"chmod\s+-R\s+777\s+/",
    r">\s*/dev/sda",
    r"shutdown",
    r"reboot",
    r"halt",
    r"curl\s+\S+\s*\|\s*(?:bash|sh)",
    r"wget\s+\S+\s*\|\s*(?:bash|sh)",
]

PROJECT_SAFE_DIRS = [
    "src/",
    "docs/",
    "scripts/",
    "tests/",
    "config/",
]

TRUSTED_PACKAGES = [
    "zephyr",
    "pytest",
    "numpy",
    "pandas",
]

_PATH_TRAVERSAL_PATTERN = re.compile(r"\.\./")
_BASE64_PATTERN = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")
_ABSOLUTE_PATH_PATTERN = re.compile(r"^/|^[A-Za-z]:[\\/]")


class InputGuard:
    """输入参数守卫.

    检测危险命令模式和路径穿越攻击。
    """

    def __init__(self) -> None:
        self._dangerous_patterns = [re.compile(p, re.IGNORECASE) for p in DANGEROUS_PATTERNS]

    def _try_base64_decode(self, value: str) -> str | None:
        """尝试 base64 解码，返回解码后的字符串或 None."""
        if not value or len(value) < 4:
            return None
        if not _BASE64_PATTERN.match(value):
            return None
        try:
            decoded = base64.b64decode(value, validate=True)
            return decoded.decode("utf-8", errors="ignore")
        except Exception:
            return None

    def _contains_dangerous(self, value: str) -> bool:
        """检查字符串是否包含危险模式（含 base64 解码检测）."""
        for pattern in self._dangerous_patterns:
            if pattern.search(value):
                return True
        decoded = self._try_base64_decode(value)
        if decoded is not None:
            for pattern in self._dangerous_patterns:
                if pattern.search(decoded):
                    return True
        return False

    def check_params(self, operation: str, params: dict[str, Any]) -> InputCheckResult:
        """检查操作参数是否包含危险模式.

        Args:
            operation: 操作名称
            params: 参数字典

        Returns:
            InputCheckResult: ALLOW / BLOCKED / SANITIZED
        """
        if not isinstance(params, dict):
            return InputCheckResult.ALLOW

        for key, value in params.items():
            str_value = str(value)

            # 检测危险命令模式（cmd/command/shell/exec/script 键）
            if key in ("cmd", "command", "shell", "exec", "script"):
                if self._contains_dangerous(str_value):
                    return InputCheckResult.BLOCKED

            # 检测路径穿越和绝对路径（path/file/filepath/target/dest 键）
            if key in ("path", "file", "filepath", "target", "dest", "destination"):
                if _PATH_TRAVERSAL_PATTERN.search(str_value):
                    return InputCheckResult.BLOCKED
                if _ABSOLUTE_PATH_PATTERN.match(str_value):
                    return InputCheckResult.BLOCKED

            # 对所有参数值检测危险命令和路径穿越
            if self._contains_dangerous(str_value):
                return InputCheckResult.BLOCKED
            if _PATH_TRAVERSAL_PATTERN.search(str_value):
                return InputCheckResult.BLOCKED

        # 包安装检查
        if operation == "package_install":
            package = str(params.get("package", ""))
            if package and package not in TRUSTED_PACKAGES:
                return InputCheckResult.BLOCKED

        return InputCheckResult.ALLOW


__all__ = [
    "DANGEROUS_PATTERNS",
    "PROJECT_SAFE_DIRS",
    "TRUSTED_PACKAGES",
    "InputCheckResult",
    "InputDecision",
    "InputGuard",
]
