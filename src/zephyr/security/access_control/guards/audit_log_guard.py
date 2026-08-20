# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.guards.audit_log_guard
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests.agent_rbac.test_forensic_c
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 审计日志注入防护; 控制字符与转义序列必须被净化
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/audit/test_audit_log_guard.py
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""audit_log_guard.py — 审计日志注入防护守卫

治本（裁定#18 G4）：本文件原为桩实现（AuditLogGuard: pass），缺 sanitize/
validate_entry/validate_dict 方法，导致 tests/audit/test_audit_log_guard.py 15 项
失败。现按测试契约实现日志注入防护：

- sanitize(value): 净化字符串中的控制字符（\\n/\\r/\\t/\\x00）与字面转义序列（\\n/\\r/\\t），
  替换为空格（\\x00 直接删除），防止日志注入攻击。
- validate_entry(key, value): 校验单个键值对，返回 {key, clean, original_len}。
- validate_dict(data): 批量校验字典，返回 {clean, issues}，非字符串值跳过。
"""

from typing import Any, Final

# 需净化的实际控制字符 → 替换目标
_CONTROL_CHAR_MAP: Final[dict[str, str]] = {
    "\n": " ",
    "\r": " ",
    "\t": " ",
    "\x00": "",
}

# 需净化的字面转义序列（反斜杠+字母）→ 替换为空格
_LITERAL_ESCAPE_SEQUENCES: Final[tuple[str, ...]] = ("\\n", "\\r", "\\t")


class AuditLogGuard:
    """审计日志注入防护守卫——治本（裁定#18 G4）。

    提供 sanitize/validate_entry/validate_dict 三个方法，确保写入审计日志的
    字符串不包含控制字符或转义序列，防止日志注入（log forging）攻击。
    """

    def sanitize(self, value: object) -> object:
        """净化字符串：替换控制字符与字面转义序列。

        - 实际控制字符 \\n/\\r/\\t → 空格，\\x00 → 删除
        - 字面转义序列 \\\\n/\\\\r/\\\\t（反斜杠+字母）→ 空格
        - 非字符串值原样返回
        - 空字符串返回空字符串
        """
        if not isinstance(value, str):
            return value
        result = value
        for char, replacement in _CONTROL_CHAR_MAP.items():
            result = result.replace(char, replacement)
        for seq in _LITERAL_ESCAPE_SEQUENCES:
            result = result.replace(seq, " ")
        return result

    def validate_entry(self, key: str, value: object) -> dict[str, Any]:
        """校验单个键值对是否包含注入字符。

        Returns:
            {"key": key, "clean": bool, "original_len": int}
            clean=True 表示净化后与原值一致（无注入字符）。
            非字符串值视为 clean（original_len=0）。
        """
        if not isinstance(value, str):
            return {"key": key, "clean": True, "original_len": 0}
        original_len = len(value)
        cleaned = self.sanitize(value)
        clean = cleaned == value
        return {"key": key, "clean": clean, "original_len": original_len}

    def validate_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """批量校验字典中的字符串值。

        非字符串值（int/bool 等）跳过，不影响 clean 判定。

        Returns:
            {"clean": bool, "issues": dict}
            issues 为 {key: True} 形式，记录含注入字符的键。
        """
        issues: dict[str, bool] = {}
        for key, value in data.items():
            if not isinstance(value, str):
                continue
            cleaned = self.sanitize(value)
            if cleaned != value:
                issues[key] = True
        return {"clean": len(issues) == 0, "issues": issues}


# 向后兼容：保留旧桩常量名（原为 None 桩）
LOG_INJECTION_PATTERNS: Final[list[str]] = list(_CONTROL_CHAR_MAP.keys()) + list(_LITERAL_ESCAPE_SEQUENCES)


__all__ = [
    "LOG_INJECTION_PATTERNS",
    "AuditLogGuard",
]
