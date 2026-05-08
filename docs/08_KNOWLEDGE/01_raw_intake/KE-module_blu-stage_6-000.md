---
module_id: KE-module_blu-stage_6-000
title: ── Stage 6 ──
category: module_blueprint
---

# ── Stage 6 ──

── Stage 6 ──
class LLMFixResult(BaseModel):
    success: bool
    fix_text: str = ""
    token_used: int = 0
    error: str = ""
