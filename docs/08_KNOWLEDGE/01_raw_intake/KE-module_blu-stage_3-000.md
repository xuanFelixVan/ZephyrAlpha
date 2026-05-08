---
module_id: KE-module_blu-stage_3-000
title: ── Stage 3 ──
category: module_blueprint
---

# ── Stage 3 ──

── Stage 3 ──
class SafetyDecision(BaseModel):
    action: Literal["PROCEED", "HOLD", "FORBIDDEN"]
    reason: str = ""
