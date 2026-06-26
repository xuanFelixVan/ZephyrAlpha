---
module_id: KE-2939
status: active
title: ── Stage 6 ──
category: module_blueprint
ttl: permanent
---

# ── Stage 6 ──

── Stage 6 ──
class LLMFixResult(BaseModel):
    success: bool
    fix_text: str = ""
    token_used: int = 0
    error: str = ""
