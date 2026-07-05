# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain-governance/governance-automation/blueprint.md
# [MODULE] zephyr.infrastructure.script_system.finding
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_finding | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

# ---
# domain: infra_ops
# category: audit
# status: active
# created: "2026-05-04"
# ---
"""
Finding Schema — 审计发现标准化数据模型

对照 ISO 19011 审计原则 + NASA-STD-8739.8 严重度分级。
蓝图对齐：MOD-INF-005 §4.4 Plugin Contract（JSONL 输出 Finding Schema）；
          §6.5 recommendation 扩展字段；§4.3 为三件套入库流程（非本 Schema 字段表）。

所有审计脚本通过本 Schema 输出统一格式的 Finding，
写入 findings.jsonl（一行一个 JSON），并通过 SQLite 做竖切查询。

与 ``scripts/governance/meta/finding_state_machine.py`` 的关系：脚本侧持久化使用
独立 JSON（``finding-state-db.json``）及状态字符串；合法状态枚举 MUST 与
``LifecycleStatus`` / ``LIFECYCLE_STATUS_VALUES`` 对齐；``Finding.to_dict()`` 为
JSONL 行形状，与状态机 DB 行字段 **非逐键等价**（消费方各自解析）。

Usage:
    from zephyr.infrastructure.script_system.finding import Finding, Severity, Dimension, LifecycleStatus

    f = Finding(
        dimension=Dimension.D3,
        severity=Severity.HIGH,
        category="元数据合规",
        target_file="docs/01_policies_and_standards/rules/trae_043_meta_rule_metadata.yaml",
        description="缺少必填字段 'version'",
        evidence="frontmatter 中未找到 version 字段",
        remediation_action=RemediationAction.FIX,
        remediation_priority="P0",
    )
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from enum import Enum

from zephyr.integration.shared.schema.schemas import Priority


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
    # SLA 期限（fix_deadline_hours）由 finding_state_machine.py 的 SLA_DEADLINES
    # 从 thresholds.yaml 通过 _get_threshold() 读取，不在 Enum 中硬编码（ARCH-036 P3-A5）。
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


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
    """Finding 生命周期 — 与 ``scripts/governance/meta/finding_state_machine.py`` 共用（SSoT）。"""

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


#: 状态机构造/校验用 — meta 脚本 MUST 从本元组派生，禁止独立硬编码列表。
LIFECYCLE_STATUS_VALUES: tuple[str, ...] = tuple(m.value for m in LifecycleStatus)


class RecommendationType(str, Enum):
    """MOD-INF-005 §6.5 — recommendation_type"""

    AUTO_FIXABLE = "auto_fixable"
    MANUAL_ONLY = "manual_only"
    NEEDS_REVIEW = "needs_review"


class RecommendedAction(str, Enum):
    """MOD-INF-005 §6.5 — recommended_action"""

    MODIFY_FILE = "modify_file"
    CREATE_TASK = "create_task"
    CONSULT_OWNER = "consult_owner"
    IGNORE = "ignore"


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
        remediation_priority: Priority = Priority.P2,
        lifecycle_status: LifecycleStatus = LifecycleStatus.OPEN,
        related_kb: list[str] | None = None,
        related_ke: list[str] | None = None,
        related_finding: list[str] | None = None,
        recommendation: str = "",
        recommendation_type: RecommendationType | None = None,
        recommended_action: RecommendedAction | None = None,
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
        self.related_kb = related_kb or []
        self.related_ke = related_ke or []
        self.related_finding = related_finding or []
        self.recommendation = recommendation
        self.recommendation_type = recommendation_type
        self.recommended_action = recommended_action
        self.timestamp = timestamp or datetime.now(UTC).isoformat()

        if finding_id:
            self.finding_id = finding_id
        else:
            stable_content = f"{dimension.value}|{severity.value}|{target_file}|{description}"
            content_hash = hashlib.sha256(stable_content.encode()).hexdigest()[:12]
            date_str = datetime.now(UTC).strftime("%Y%m%d")
            self.finding_id = f"FIND-{dimension.value}-{date_str}-{content_hash}"

    def to_dict(self) -> dict:
        d: dict = {
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
                "related_kb": self.related_kb,
                "related_ke": self.related_ke,
                "related_finding": self.related_finding,
            },
            "timestamp": self.timestamp,
        }
        if self.recommendation or self.recommendation_type is not None or self.recommended_action is not None:
            d["recommendation_block"] = {
                "recommendation": self.recommendation,
                "recommendation_type": self.recommendation_type.value if self.recommendation_type else None,
                "recommended_action": self.recommended_action.value if self.recommended_action else None,
            }
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def to_jsonl_line(self) -> str:
        return self.to_json() + "\n"

    def __repr__(self) -> str:
        # 5.110.4 修复: 统一为 f"ClassName(field={self.field!r}, ...)" 格式, 使 __repr__ 可重建
        return (
            f"Finding(finding_id={self.finding_id!r}, "
            f"dimension={self.dimension.value!r}, severity={self.severity.value!r}, "
            f"target_file={self.target_file!r})"
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
        tmp_path = f"{path}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(self.to_jsonl())
            os.replace(tmp_path, path)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

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

    def __contains__(self, item: object) -> bool:
        """5.123.1 修复：显式 __contains__ 避免 `in` 回退到 O(n) 的 __iter__ 线性扫描。

        支持 Finding 实例或 finding_id 字符串查询。
        """
        if isinstance(item, Finding):
            target_id = item.finding_id
        elif isinstance(item, str):
            target_id = item
        else:
            return False
        return any(f.finding_id == target_id for f in self.findings)

    def __reversed__(self):
        """5.123.2 修复：显式 __reversed__ 避免 reversed() 抛 TypeError。"""
        return reversed(self.findings)
