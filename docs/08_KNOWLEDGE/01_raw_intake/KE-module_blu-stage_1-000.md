---
module_id: KE-module_blu-stage_1-000
title: ── Stage 1 ──
category: module_blueprint
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
