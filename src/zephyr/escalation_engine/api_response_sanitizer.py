# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.api_response_sanitizer

# [INVARIANTS] API返回清洗不可跳过;injection marker必须移除

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

API Response Sanitizer — v0.9.0 API响应清洗器: 外部API返回内容清洗+injection检测。
"""
from __future__ import annotations

class APIResponseSanitizer:
    def sanitize(self,response_text:str)->str:
        dangerous=["<script","javascript:","onerror=","onclick="]
        result=response_text
        for d in dangerous:
            result=result.replace(d,"[SANITIZED]")
        return result

    def is_suspicious(self,response_text:str)->bool:
        return any(p in response_text.lower() for p in ["<script","eval(","__import__("])
