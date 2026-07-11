# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.security_governance.api_response_sanitizer
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] API返回清洗不可跳过;injection marker必须移除
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_api_response_sanitizer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

API Response Sanitizer — v0.9.0 API响应清洗器: 外部API返回内容清洗+injection检测。
"""

from __future__ import annotations

import re


class APIResponseSanitizer:
    # 5.45.5 修复：扩展 XSS 模式列表 + 大小写不敏感匹配。
    # 原仅 4 个模式且 replace 大小写敏感，<SCRIPT>/<Img onerror 等变体可绕过。
    _DANGEROUS_PATTERNS: list[str] = [
        r"<script[^>]*>",
        r"</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onclick\s*=",
        r"onload\s*=",
        r"onmouseover\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"data:text/html",
        r"vbscript:",
    ]

    def sanitize(self, response_text: str) -> str:
        result = response_text
        for pattern in self._DANGEROUS_PATTERNS:
            result = re.sub(pattern, "[SANITIZED]", result, flags=re.IGNORECASE)
        return result

    def is_suspicious(self, response_text: str) -> bool:
        return any(p in response_text.lower() for p in ["<script", "eval(", "__import__("])
