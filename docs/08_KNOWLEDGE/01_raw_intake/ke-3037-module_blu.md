---
module_id: KE-2937
status: active
title: ── Stage 3 ──
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# ── Stage 3 ──

── Stage 3 ──
class SafetyDecision(BaseModel):
    action: Literal["PROCEED", "HOLD", "FORBIDDEN"]
    reason: str = ""
