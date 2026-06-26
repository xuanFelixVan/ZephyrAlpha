---
module_id: KE-2936
status: active
title: ── Stage 2 ──
category: module_blueprint
ttl: permanent
---

# ── Stage 2 ──

── Stage 2 ──
class TriggerResult(BaseModel):
    trigger_type: Literal["file_disconnection", "system_surpassed", "structural_gap"]
    certainty: float                    # 0.0 ~ 1.0
    severity: Severity
    target_location: str                # 规则文档中的具体位置
    evidence: str                       # 触发证据（机械可验证）

class DisconnectionIssue(TriggerResult):
    referenced_path: str
    alternative_paths: list[str]

class SurpassIssue(TriggerResult):
    field_name: str
    rule_stated: int
    actual: int

class GapIssue(TriggerResult):
    missing_id: str
    category: str
    near_matches: list[str]
