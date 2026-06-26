---
module_id: KE-2935
status: active
title: ── Stage 1 ──
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# ── Stage 1 ──

── Stage 1 ──
class ExtractedReferences(BaseModel):
    file_paths: list[str]
    gate_ids: list[str]
    numeric_claims: list[NumericClaim]

class NumericClaim(BaseModel):
    field_name: str
    stated_value: int
    context: str
