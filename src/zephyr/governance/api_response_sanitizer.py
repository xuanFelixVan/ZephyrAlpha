# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [MODULE] zephyr.governance.api_response_sanitizer
# [DOMAIN] D-GOVERNANCE
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

"""

API Response Sanitizer — v0.9.0 API响应清洗器: 外部API返回内容清洗+injection检测。
"""

from __future__ import annotations


class APIResponseSanitizer:
    def sanitize(self, response_text: str) -> str:
        dangerous = ["<script", "javascript:", "onerror=", "onclick="]
        result = response_text
        for d in dangerous:
            result = result.replace(d, "[SANITIZED]")
        return result

    def is_suspicious(self, response_text: str) -> bool:
        return any(p in response_text.lower() for p in ["<script", "eval(", "__import__("])
