# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4
# [MODULE] zephyr.governance.audit_trail.finding_model
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.integration.shared.schema.base_config
# [CONSUMERS] finding_ingest.py; pipeline_runner.py; audit-trail.writer; _finding_lifecycle.py; create_task_from_finding.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] AuditFinding is the single unified data contract between 144 governance scripts and 7 audit modules; all fields MUST be compatible with Finding Schema JSONL
# [MODIFY-GUARD] Field additions require blueprint update; field removals require migration plan
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] from_jsonl() raises ValueError on malformed input; to_jsonl() never raises
# [TESTS] tests/test_audit_finding_model.py
# [A_module] module_id=MOD-UNK_finding_model | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from zephyr.integration.shared.schema.base_config import BASE_CONFIG


class FindingSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class FindingDimension(str, Enum):
    D1 = "D1"
    D2 = "D2"
    D3 = "D3"
    D4 = "D4"
    D5 = "D5"
    D6 = "D6"
    D7 = "D7"
    D8 = "D8"
    D9 = "D9"
    D10 = "D10"
    D11 = "D11"
    D12 = "D12"

    @property
    def label(self) -> str:
        _labels: dict[str, str] = {
            "D1": "结构完整性",
            "D2": "链接完整性",
            "D3": "元数据合规",
            "D4": "路径有效性",
            "D5": "架构合规",
            "D6": "安全漏洞",
            "D7": "代码质量",
            "D8": "文档代码同步",
            "D9": "知识覆盖",
            "D10": "性能容量",
            "D11": "合规完整性",
            "D12": "AI幻觉检测",
        }
        return _labels[self.value]


class FindingStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    FIXED = "FIXED"
    VERIFIED = "VERIFIED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    WONTFIX = "WONTFIX"
    ACCEPTED_RISK = "ACCEPTED_RISK"
    CLOSED = "CLOSED"
    OVERDUE = "OVERDUE"
    DEFERRED = "DEFERRED"


class BlastRadius(str, Enum):
    file = "file"
    module = "module"
    layer = "layer"
    system = "system"


class RemediationAction(str, Enum):
    FIX = "FIX"
    DELETE = "DELETE"
    MOVE = "MOVE"
    UPDATE_REF = "UPDATE_REF"
    CREATE = "CREATE"
    INVESTIGATE = "INVESTIGATE"


class RemediationPriority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class FindingTarget(BaseModel):
    model_config = BASE_CONFIG

    file_path: str
    line_range: str = ""


class FindingImpact(BaseModel):
    model_config = BASE_CONFIG

    blast_radius: BlastRadius = BlastRadius.file


class FindingRemediation(BaseModel):
    model_config = BASE_CONFIG

    action: RemediationAction
    priority: RemediationPriority


class FindingLifecycle(BaseModel):
    model_config = BASE_CONFIG

    status: FindingStatus = FindingStatus.OPEN


class FindingTraceability(BaseModel):
    model_config = BASE_CONFIG

    related_kb: list[str] = Field(default_factory=list)
    related_ke: list[str] = Field(default_factory=list)
    related_finding: list[str] = Field(default_factory=list)


class RecommendationBlock(BaseModel):
    model_config = BASE_CONFIG

    recommendation: str = ""
    recommendation_type: str = ""
    recommended_action: str = ""


class AuditFinding(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        populate_by_name=True,
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "finding_id": "FIND-D3-20260526-a1b2c3d4e5f6",
                "dimension": "D3",
                "severity": "HIGH",
                "category": "元数据合规",
                "target": {
                    "file_path": "docs/01_policies_and_standards/rules/trae_043_meta_rule_metadata.yaml",
                    "line_range": "1-10",
                },
                "description": "缺少必填字段 'version'",
                "evidence": "frontmatter 中未找到 version 字段",
                "impact": {"blast_radius": "file"},
                "remediation": {"action": "FIX", "priority": "P1"},
                "lifecycle": {"status": "OPEN"},
                "traceability": {"related_kb": [], "related_ke": [], "related_finding": []},
                "timestamp": "2026-05-26T12:00:00+00:00",
                "recommendation_block": {"recommendation": "", "recommendation_type": "", "recommended_action": ""},
            }
        },
    )

    finding_id: str
    dimension: FindingDimension
    severity: FindingSeverity
    category: str
    target: FindingTarget
    description: str
    evidence: str = ""
    impact: FindingImpact = Field(default_factory=FindingImpact)
    remediation: FindingRemediation
    lifecycle: FindingLifecycle = Field(default_factory=FindingLifecycle)
    traceability: FindingTraceability = Field(default_factory=FindingTraceability)
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    recommendation_block: RecommendationBlock = Field(default_factory=RecommendationBlock)

    @classmethod
    def from_jsonl(cls, line: str) -> AuditFinding:
        stripped = line.strip()
        if not stripped:
            raise ValueError("Empty JSONL line")
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSONL: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError(f"JSONL line must be a JSON object, got {type(data).__name__}")
        required_keys = {"finding_id", "dimension", "severity", "category", "description"}
        missing = required_keys - data.keys()
        if missing:
            raise ValueError(f"Missing required keys: {sorted(missing)}")
        if "target" not in data or not isinstance(data["target"], dict):
            data["target"] = {"file_path": data.pop("target_file", ""), "line_range": data.pop("target_line_range", "")}
        if "impact" not in data:
            data["impact"] = {}
        if "remediation" not in data:
            data["remediation"] = {"action": "FIX", "priority": "P2"}
        if "lifecycle" not in data:
            data["lifecycle"] = {}
        if "traceability" not in data:
            data["traceability"] = {}
        if "recommendation_block" not in data:
            data["recommendation_block"] = {}
        return cls.model_validate(data)

    def to_jsonl(self) -> str:
        try:
            return self.model_dump_json() + "\n"
        except Exception:
            return json.dumps(self.to_finding_dict(), ensure_ascii=False) + "\n"

    def to_finding_dict(self) -> dict:
        return {
            "finding_id": self.finding_id,
            "dimension": self.dimension.value,
            "severity": self.severity.value,
            "category": self.category,
            "target": {
                "file_path": self.target.file_path,
                "line_range": self.target.line_range,
            },
            "description": self.description,
            "evidence": self.evidence,
            "impact": {
                "blast_radius": self.impact.blast_radius.value,
            },
            "remediation": {
                "action": self.remediation.action.value,
                "priority": self.remediation.priority.value,
            },
            "lifecycle": {
                "status": self.lifecycle.status.value,
            },
            "traceability": {
                "related_kb": self.traceability.related_kb,
                "related_ke": self.traceability.related_ke,
                "related_finding": self.traceability.related_finding,
            },
            "timestamp": self.timestamp,
            "recommendation_block": {
                "recommendation": self.recommendation_block.recommendation,
                "recommendation_type": self.recommendation_block.recommendation_type,
                "recommended_action": self.recommendation_block.recommended_action,
            },
        }


def generate_finding_id(dimension: str, description: str) -> str:
    date_str = datetime.now(UTC).strftime("%Y%m%d")
    content_hash = hashlib.sha256(f"{dimension}|{description}".encode()).hexdigest()[:12]
    return f"FIND-{dimension}-{date_str}-{content_hash}"
