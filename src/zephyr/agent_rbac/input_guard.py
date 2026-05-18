# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.input_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
L3 Input Guard — 参数级护栏 (schema白名单+危险模式+路径白名单+包安装+网络边界+编码绕过)

MOD-INF-018 §2.6  D-018-08

权限颗粒度从Tool级细化到参数级——L3是参数级防御线。
"""

import base64
import re
from enum import Enum
from pathlib import Path
from typing import Optional

from zephyr.agent_rbac.immutable_core import ImmutableCore


class InputDecision(str, Enum):
    ALLOW = "ALLOW"
    BLOCKED = "BLOCKED"
    SANITIZED = "SANITIZED"


DANGEROUS_PATTERNS: list[tuple[str, str]] = [
    (r"rm\s+-rf", "Recursive force deletion"),
    (r"curl\s+.*\|.*bash", "curl-to-bash pipe"),
    (r"wget\s+.*\|.*sh", "wget-to-sh pipe"),
    (r">\s*/dev/null", "Redirect to /dev/null"),
    (r">\s*/etc/passwd", "Write to /etc/passwd"),
    (r">\s*/etc/shadow", "Write to /etc/shadow"),
    (r"chmod\s+777", "World-writable permissions"),
    (r"chown\s+root", "Change ownership to root"),
    (r"eval\s+", "Shell eval injection"),
    (r"`.*`", "Backtick command substitution"),
    (r"\$\(.*\)", "Dollar-parenthesis substitution"),
    (r"__import__\s*\(.*os", "Dynamic os import"),
    (r"exec\s*\(|eval\s*\(", "Code execution builtins"),
    (r"subprocess\.(call|Popen|run)\s*\(", "Subprocess execution"),
    (r"os\.system\s*\(", "OS system call"),
    (r";\s*rm\s+-", "Chained rm command"),
    (r"\|\s*sh\b", "Pipe to shell"),
]

TRUSTED_PACKAGES: list[str] = [
    "pytest", "pytest-asyncio", "pytest-cov", "pytest-timeout",
    "pydantic", "pyyaml", "cryptography", "opentelemetry-api",
    "black", "isort", "mypy", "ruff", "pre-commit",
    "httpx", "ed25519",
]

PROJECT_SAFE_DIRS: list[str] = [
    "src/", "tests/", "docs/", "data/", "scripts/",
    "config/", "_journals/", "session-logs/",
]


class InputGuard:
    def __init__(self, immutable_core: Optional[ImmutableCore] = None, project_root: Optional[Path] = None) -> None:
        self._immutable_core = immutable_core or ImmutableCore()
        self._project_root = project_root or Path(__file__).resolve().parents[3]

    def check_params(self, operation: str, params: dict) -> InputDecision:
        result, _ = self._check_dangerous_patterns(str(params))
        if result != InputDecision.ALLOW:
            return result

        decoded = self._try_decode(params)
        if decoded != params:
            result, _ = self._check_dangerous_patterns(str(decoded))
            if result != InputDecision.ALLOW:
                return result

        path = params.get("path", params.get("file_path", ""))
        if path:
            path_decision, _ = self.check_path(str(path))
            if path_decision != InputDecision.ALLOW:
                return path_decision

        pkg = params.get("package", params.get("pkg", ""))
        if pkg:
            pkg_decision, _ = self.check_package_install(str(pkg))
            if pkg_decision != InputDecision.ALLOW:
                return pkg_decision

        url = params.get("url", params.get("network_target", ""))
        if url:
            url_decision, _ = self.check_network_target(str(url))
            if url_decision != InputDecision.ALLOW:
                return url_decision

        return InputDecision.ALLOW

    def _check_dangerous_patterns(self, content: str) -> tuple[InputDecision, str]:
        for pattern, description in DANGEROUS_PATTERNS:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return InputDecision.BLOCKED, f"Dangerous pattern '{match.group(0)[:50]}' detected ({description})"
        return InputDecision.ALLOW, ""

    def _try_decode(self, params: dict) -> dict:
        decoded = dict(params)
        for key in ("command", "script", "content", "code"):
            val = str(params.get(key, ""))
            if val:
                for decoder in (self._try_decode_base64, self._try_decode_hex):
                    d = decoder(val)
                    if d and d != val:
                        decoded[key] = d
        return decoded

    def _try_decode_base64(self, s: str) -> Optional[str]:
        try:
            decoded = base64.b64decode(s, validate=True)
            text = decoded.decode("utf-8", errors="replace")
            if text.isprintable() or "rm" in text.lower():
                return text
        except Exception:
            pass
        return None

    def _try_decode_hex(self, s: str) -> Optional[str]:
        try:
            if re.match(r"^[0-9a-fA-F]+$", s) and len(s) % 2 == 0:
                decoded = bytes.fromhex(s).decode("utf-8", errors="replace")
                return decoded
        except Exception:
            pass
        return None

    def check_path(self, path: str) -> tuple[InputDecision, str]:
        normalized = path.replace("\\", "/")

        if normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
            return InputDecision.BLOCKED, f"Absolute path '{path}' not allowed"

        if ".." in normalized:
            return InputDecision.BLOCKED, f"Path traversal detected in '{path}'"

        if self._immutable_core.is_protected_path(path):
            return InputDecision.BLOCKED, f"Path '{path}' is protected (L0 Immutable Core)"

        for safe_dir in PROJECT_SAFE_DIRS:
            if normalized.startswith(safe_dir.rstrip("/")):
                return InputDecision.ALLOW, ""

        if normalized.startswith("_temp") or normalized.startswith("."):
            return InputDecision.ALLOW, ""

        return InputDecision.BLOCKED, f"Path '{path}' not in project safe directories"

    def check_package_install(self, package_name: str) -> tuple[InputDecision, str]:
        pkg = package_name.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip()
        for trusted in TRUSTED_PACKAGES:
            if pkg.lower() == trusted.lower():
                return InputDecision.ALLOW, ""
        return InputDecision.BLOCKED, f"Package '{pkg}' not in trusted packages whitelist"

    def check_network_target(self, url: str) -> tuple[InputDecision, str]:
        local_patterns = [
            r"^https?://localhost",
            r"^https?://127\.0\.0\.1",
            r"^https?://0\.0\.0\.0",
        ]
        for pat in local_patterns:
            if re.match(pat, url, re.IGNORECASE):
                return InputDecision.ALLOW, ""

        if "google.com" in url or "github.com" in url or "pypi.org" in url:
            return InputDecision.ALLOW, ""

        return InputDecision.BLOCKED, f"Network target '{url[:80]}' not in trusted destinations"
