---
module_id: KE-module_blu-stage_4-000
title: ── Stage 4 ──
category: module_blueprint
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
