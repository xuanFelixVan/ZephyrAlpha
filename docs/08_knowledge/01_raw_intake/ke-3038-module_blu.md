---
module_id: KE-2938
status: active
title: ── Stage 4 ──
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# ── Stage 4 ──

── Stage 4 ──
class AlignmentReport(BaseModel):
    aligned_count: int
    zombie_count: int
    orphan_count: int
    zombies: list[str]
    orphans: list[str]
    alignment_score: float
    drift_severity: Severity
