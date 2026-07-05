# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.guards.rule_injection_guard
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_forensic_b.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] injection patterns always detected; clean JSON never flagged
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check never raises; returns RuleInjectionCheck
# [TESTS] tests/agent_rbac/test_forensic_b.py
# [A_module] module_id=MOD-SEC_rule_injection_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""RuleInjectionGuard — 规则注入守卫.

依据蓝图 MOD-INF-018 §3:
- 检测规则内容中的代码注入模式
- 阻止 eval/exec/__import__/os.system 等危险调用
- 保护规则引擎免受注入攻击
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


INJECTION_PATTERNS = [
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"__import__\s*\(",
    r"\bos\.system\s*\(",
    r"\bsubprocess\.",
    r"\bcompile\s*\(",
    r"\bglobals\s*\(\s*\)",
    r"\blocals\s*\(\s*\)",
    r"\bgetattr\s*\(",
    r"\bsetattr\s*\(",
    r"\b__builtins__\b",
    r"\b__subclasses__\b",
    r"\b__class__\b",
    r"\b__bases__\b",
    r"\b__mro__\b",
    r"\b__globals__\b",
    r"\bopen\s*\(",
    r"\bfile\s*\(",
    r"<[^>]*script[^>]*>",
    r"javascript:",
    r"\bimport\s+os\b",
    r"\bimport\s+sys\b",
    r"\bfrom\s+os\s+import\b",
    r"\bfrom\s+subprocess\s+import\b",
    r"\bctypes\b",
    r"\bpickle\.loads?\s*\(",
    r"\bmarshal\.loads?\s*\(",
    r"\bbase64\.b64decode\s*\(",
    r"\\x[0-9a-f]{2}",  # hex escape sequences
]


@dataclass
class RuleInjectionCheck:
    """规则注入检查结果."""

    rule_id: str = ""
    injection_detected: bool = False
    matched_patterns: list[str] = field(default_factory=list)
    content_preview: str = ""


class RuleInjectionGuard:
    """规则注入守卫器."""

    def __init__(self) -> None:
        self._compiled = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

    def check(self, rule_id: str, content: str) -> RuleInjectionCheck:
        """检查规则内容是否包含注入模式.

        Args:
            rule_id: 规则ID
            content: 规则内容字符串

        Returns:
            RuleInjectionCheck 包含 injection_detected 和 matched_patterns
        """
        if not content or not isinstance(content, str):
            return RuleInjectionCheck(
                rule_id=rule_id,
                injection_detected=False,
                matched_patterns=[],
                content_preview="",
            )

        matched: list[str] = []
        for i, pat in enumerate(self._compiled):
            if pat.search(content):
                matched.append(INJECTION_PATTERNS[i])

        return RuleInjectionCheck(
            rule_id=rule_id,
            injection_detected=len(matched) > 0,
            matched_patterns=matched,
            content_preview=content[:100],
        )


__all__ = [
    "INJECTION_PATTERNS",
    "RuleInjectionCheck",
    "RuleInjectionGuard",
]
