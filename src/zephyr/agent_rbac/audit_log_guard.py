"""审计日志守卫——防止攻击者通过日志注入伪造审计记录."""
from __future__ import annotations

from typing import Any


LOG_INJECTION_PATTERNS = ["\n", "\r", "\t", "\x00", "\x1b", "\\n", "\\r"]


class AuditLogGuard:
    def sanitize(self, value: str) -> str:
        result = value
        for pattern in LOG_INJECTION_PATTERNS:
            result = result.replace(pattern, f"[{repr(pattern)[1:-1]}]")
        return result

    def validate_entry(self, key: str, value: str) -> dict[str, Any]:
        sanitized = self.sanitize(value)
        clean = sanitized == value
        return {"key": key, "clean": clean, "original_len": len(value), "sanitized_len": len(sanitized)}

    def validate_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        issues = {}
        for k, v in data.items():
            if isinstance(v, str):
                sv = self.sanitize(v)
                if sv != v:
                    issues[k] = {"original": v, "sanitized": sv}
        return {"clean": len(issues) == 0, "issues": issues}
