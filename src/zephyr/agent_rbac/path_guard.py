"""路径守卫——禁止读取/写入特定路径目录(黑名单+白名单)."""
from __future__ import annotations

from typing import Any


FORBIDDEN_PATHS = [
    "/etc/shadow", "/etc/passwd", "/root/", "C:\\Windows\\System32\\",
    ".env", ".secrets", "credentials.json", "id_rsa", "id_ed25519",
    ".git/config", ".git/HEAD",
]

ALLOWED_ROOTS = [
    "D:\\ZephyrAlpha\\", "tests/", "src/", "scripts/", "data/",
]


class PathGuard:
    def __init__(self) -> None:
        self._violations: list[dict[str, Any]] = []

    def check(self, path: str, operation: str = "read") -> dict[str, Any]:
        import os

        normalized = os.path.normpath(path).replace("\\", "/").lower()

        for fp in FORBIDDEN_PATHS:
            if fp.lower() in normalized:
                self._violations.append({"path": path, "operation": operation, "matched": fp})
                return {"allowed": False, "reason": f"forbidden_path_matched: {fp}", "path": path}

        return {"allowed": True, "path": path}

    def is_within_project(self, path: str) -> bool:
        import os
        normalized = os.path.normpath(path).replace("\\", "/").lower()
        return any(root.lower() in normalized for root in ALLOWED_ROOTS)
