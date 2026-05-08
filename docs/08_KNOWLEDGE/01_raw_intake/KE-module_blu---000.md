---
module_id: KE-module_blu---000
title: === 蓝图-代码一致性 ===
category: module_blueprint
---

# === 蓝图-代码一致性 ===

=== 蓝图-代码一致性 ===

class BlueprintCodeAlignment(BaseModel):
    """蓝图 ↔ 实现对齐检查结果"""
    model_config = ConfigDict(frozen=True)

    alignment_id: UUID = Field(default_factory=uuid4)
    blueprint_version: str
    code_commit_sha: str
    check_timestamp: datetime = Field(default_factory=datetime.utcnow)

    matches: int = 0
    mismatches: int = 0
    orphans_in_code: int = 0
    orphans_in_blueprint: int = 0

    status: Literal["aligned", "drift_detected", "critical_drift"] = "aligned"


class DriftReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    drift_id: UUID = Field(default_factory=uuid4)
    alignment: BlueprintCodeAlignment
    drift_category: Literal["missing_implementation", "extra_code", "semantic_gap"]
    blueprint_path: str
    code_path: str
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    suggested_fix: str = ""
