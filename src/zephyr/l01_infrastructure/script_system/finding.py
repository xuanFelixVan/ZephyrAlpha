# ---
# layer: l01_infrastructure
# category: audit
# status: active
# created: "2026-05-04"
# ---
"""
Finding Schema — 审计发现标准化数据模型

对照 ISO 19011 审计原则 + NASA-STD-8739.8 严重度分级。
蓝图定义：MOD-INF-005 §4.3

所有审计脚本通过本 Schema 输出统一格式的 Finding，
写入 findings.jsonl（一行一个 JSON），并通过 SQLite 做竖切查询。

Usage:
    from zephyr.l01_infrastructure.script_system.finding import Finding, Severity, Dimension, LifecycleStatus

    f = Finding(
        dimension=Dimension.D3,
        severity=Severity.HIGH,
        category="元数据合规",
        target_file="docs/01_policies_and_standards/meta/index.md",
        description="缺少必填字段 'version'",
        evidence="frontmatter 中未找到 version 字段",
        remediation_action=RemediationAction.FIX,
        remediation_priority="P0",
    )
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from enum import Enum
from typing import Literal

class Dimension(str, Enum):
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
        _labels = {
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

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

    @property
    def fix_deadline_hours(self) -> int | None:
        _deadlines = {
            "CRITICAL": 24,
            "HIGH": 168,
            "MEDIUM": 720,
            "LOW": None,
            "INFO": None,
        }
        return _deadlines[self.value]

class BlastRadius(str, Enum):
    FILE = "file"
    MODULE = "module"
    LAYER = "layer"
    SYSTEM = "system"

class RemediationAction(str, Enum):
    FIX = "FIX"
    DELETE = "DELETE"
    MOVE = "MOVE"
    UPDATE_REF = "UPDATE_REF"
    CREATE = "CREATE"
    INVESTIGATE = "INVESTIGATE"

class LifecycleStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    FIXED = "FIXED"
    WONTFIX = "WONTFIX"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    DEFERRED = "DEFERRED"

class Finding:
    def __init__(
        self,
        dimension: Dimension,
        severity: Severity,
        category: str,
        target_file: str,
        description: str,
        evidence: str = "",
        target_line_range: str = "",
        blast_radius: BlastRadius = BlastRadius.FILE,
        remediation_action: RemediationAction = RemediationAction.FIX,
        remediation_priority: Literal["P0", "P1", "P2", "P3"] = "P2",
        lifecycle_status: LifecycleStatus = LifecycleStatus.OPEN,
        related_adr: list[str] | None = None,
        related_ke: list[str] | None = None,
        related_finding: list[str] | None = None,
        finding_id: str | None = None,
        timestamp: str | None = None,
    ):
        self.dimension = dimension
        self.severity = severity
        self.category = category
        self.target_file = target_file
        self.target_line_range = target_line_range
        self.description = description
        self.evidence = evidence
        self.blast_radius = blast_radius
        self.remediation_action = remediation_action
        self.remediation_priority = remediation_priority
        self.lifecycle_status = lifecycle_status
        self.related_adr = related_adr or []
        self.related_ke = related_ke or []
        self.related_finding = related_finding or []
        self.timestamp = timestamp or datetime.now(UTC).isoformat()

        if finding_id:
            self.finding_id = finding_id
        else:
            stable_content = f"{dimension.value}|{severity.value}|{target_file}|{description}"
            content_hash = hashlib.sha256(stable_content.encode()).hexdigest()[:12]
            date_str = datetime.now(UTC).strftime("%Y%m%d")
            self.finding_id = f"FIND-{dimension.value}-{date_str}-{content_hash}"

    def to_dict(self) -> dict:
        return {
            "finding_id": self.finding_id,
            "dimension": self.dimension.value,
            "severity": self.severity.value,
            "category": self.category,
            "target": {
                "file_path": self.target_file,
                "line_range": self.target_line_range,
            },
            "description": self.description,
            "evidence": self.evidence,
            "impact": {
                "blast_radius": self.blast_radius.value,
            },
            "remediation": {
                "action": self.remediation_action.value,
                "priority": self.remediation_priority,
            },
            "lifecycle": {
                "status": self.lifecycle_status.value,
            },
            "traceability": {
                "related_adr": self.related_adr,
                "related_ke": self.related_ke,
                "related_finding": self.related_finding,
            },
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def to_jsonl_line(self) -> str:
        return self.to_json() + "\n"

    def __repr__(self) -> str:
        return (
            f"Finding({self.finding_id}, D={self.dimension.value}, " f"SEV={self.severity.value}, {self.target_file})"
        )

    @classmethod
    def from_result_dict(
        cls,
        rule_id: str,
        file_path: str,
        message: str,
        dimension: Dimension,
        severity: Severity = Severity.MEDIUM,
    ) -> Finding:
        return cls(
            dimension=dimension,
            severity=severity,
            category=f"{dimension.label} — {rule_id}",
            target_file=file_path,
            description=message,
            remediation_action=RemediationAction.FIX,
        )

class FindingCollection:
    def __init__(self, findings: list[Finding] | None = None):
        self.findings: list[Finding] = findings or []

    def add(self, finding: Finding):
        self.findings.append(finding)

    def extend(self, findings: list[Finding]):
        self.findings.extend(findings)

    def to_jsonl(self) -> str:
        return "".join(f.to_jsonl_line() for f in self.findings)

    def write_jsonl(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_jsonl())

    def append_jsonl(self, path: str):
        with open(path, "a", encoding="utf-8") as f:
            f.write(self.to_jsonl())

    def by_dimension(self, dimension: Dimension) -> FindingCollection:
        return FindingCollection([f for f in self.findings if f.dimension == dimension])

    def by_severity(self, severity: Severity) -> FindingCollection:
        return FindingCollection([f for f in self.findings if f.severity == severity])

    def critical_only(self) -> FindingCollection:
        """返回仅含 CRITICAL 严重度的 FindingCollection 子集。"""
        return self.by_severity(Severity.CRITICAL)

    @property
    def total(self) -> int:
        return len(self.findings)

    def summary(self) -> dict:
        counts = {s.value: 0 for s in Severity}
        dim_counts = {d.value: 0 for d in Dimension}
        for f in self.findings:
            counts[f.severity.value] += 1
            dim_counts[f.dimension.value] += 1
        return {
            "total": self.total,
            "by_severity": counts,
            "by_dimension": dim_counts,
        }

    def __len__(self) -> int:
        return self.total

    def __iter__(self):
        return iter(self.findings)
