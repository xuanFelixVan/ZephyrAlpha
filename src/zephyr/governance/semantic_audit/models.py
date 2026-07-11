# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §4.2
# [MODULE] zephyr.governance.semantic_audit.models
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] trigger_engine;fix_prioritizer;llm_bridge;reference_extractor;safety_boundary;alignment_engine;issue_aggregator;self_health
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] severity必须为RED/YELLOW/INFO; SafetyDecision必须为PROCEED/HOLD/FORBIDDEN; TriggerResult.severity与Severity枚举一致
# [MODIFY-GUARD] blueprint.md §4.2; semantic_audit/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValidationError on invalid severity/SafetyDecision
# [TESTS] tests/semantic-auditor/test_models.py
# [A_module] module_id=MOD-GOV_models | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""语义审计管线数据模型 — MOD-INF-028 §4.2

所有 Stage 共享的类型定义：Severity / SafetyDecision / TriggerResult /
TriggerDecision / ExtractedReferences / LLMFixResult / AlignmentReport /
HealResult / SemanticAuditReport
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

__all__ = [
    "AlignmentReport",
    "ExtractedReferences",
    "HealResult",
    "LLMFixResult",
    "SafetyDecision",
    "SemanticAuditFinding",
    "SemanticAuditReport",
    "Severity",
    "TriggerDecision",
    "TriggerResult",
]


class Severity(str, Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    INFO = "INFO"


class SafetyDecision(str, Enum):
    PROCEED = "PROCEED"
    HOLD = "HOLD"
    FORBIDDEN = "FORBIDDEN"


class TriggerResult(BaseModel):
    trigger_type: str = ""
    certainty: float = 0.0
    severity: Severity = Severity.INFO
    target_location: str = ""
    evidence: str = ""


class TriggerDecision(BaseModel):
    should_trigger: bool = False
    reason: str = ""
    results: list[TriggerResult] = Field(default_factory=list)
    trigger_count: int = 0
    trigger_type: str = ""


class ExtractedReferences(BaseModel):
    file_paths: list[str] = Field(default_factory=list)
    depends_on_targets: list[dict] = Field(default_factory=list)
    blueprint_links: list[str] = Field(default_factory=list)
    internal_rule_ids: list[str] = Field(default_factory=list)
    module_id_refs: list[str] = Field(default_factory=list)
    section_refs: list[str] = Field(default_factory=list)
    script_refs: list[str] = Field(default_factory=list)
    numeric_claims: list[dict] = Field(default_factory=list)
    frontmatter_metadata: dict = Field(default_factory=dict)


class LLMFixResult(BaseModel):
    success: bool = False
    fix_text: str = ""
    token_used: int = 0
    error: str = ""


# 向后兼容别名：FixResult 已重命名为 LLMFixResult
FixResult = LLMFixResult


class AlignmentReport(BaseModel):
    aligned_count: int = 0
    zombie_count: int = 0
    orphan_count: int = 0
    alignment_score: float = 0.0
    staleness_severity: Severity = Severity.INFO
    missing_files: list[str] = Field(default_factory=list)
    extra_files: list[str] = Field(default_factory=list)
    misregistered: list[str] = Field(default_factory=list)


class HealResult(BaseModel):
    success: bool
    reason: str = ""
    rollback_applied: bool = False


class SemanticAuditReport(BaseModel):
    audit_id: str = ""
    rule_document: str = ""
    total_triggers: int = 0
    safety_filtered_out: int = 0
    red_issues: list[dict] = Field(default_factory=list)
    yellow_issues: list[dict] = Field(default_factory=list)
    alignment_reports: list[AlignmentReport] = Field(default_factory=list)
    llm_fixes: list[LLMFixResult] = Field(default_factory=list)
    heal_results: list[HealResult] = Field(default_factory=list)
    duration_ms: int = 0
    token_used: int = 0
    fresh_until: datetime | None = None


class SemanticAuditFinding(BaseModel):
    """语义审计发现 - 单个审计问题的结构化描述.

    字段:
    - finding_id: 发现唯一 ID
    - module: 被审计的模块名
    - severity: 严重等级 (RED/YELLOW/INFO)
    - dimension: 审计维度 (如 dependson_chain_broken)
    - description: 问题描述
    - source_location: 源文件位置
    """

    finding_id: str = ""
    module: str = ""
    severity: Severity = Severity.INFO
    dimension: str = ""
    description: str = ""
    source_location: str = ""
