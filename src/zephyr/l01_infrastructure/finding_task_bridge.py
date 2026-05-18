# [BLUEPRINT] MOD-INF-002 | 03_modules/l01_infrastructure/runtime-integration/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.finding_task_bridge

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
Finding→TaskCard 桥接器
======================
职责：将脚本系统的审计发现自动转换为任务卡，打通反馈回路（P0集成缺口修复）。
数据流：script-system Findings → FindingTaskBridge → TaskRepository → TaskCards
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.core.models import GateLevel, TaskCard, TaskNamespace, TaskStatus
from zephyr.db.task_repo import TaskRepository
from zephyr.shared.schema.schemas import Priority, SafetyLevel

logger = logging.getLogger(__name__)

__all__ = [
    "AuditFinding",
    "FindingTaskBridge",
    "FindingSeverity",
    "bridge_findings_to_tasks",
    "SEVERITY_TO_PRIORITY",
    "DIMENSION_TO_MODULE_INFO",
]

FindingSeverity = str


SEVERITY_TO_PRIORITY: dict[str, Priority] = {
    "critical": Priority.P0,
    "high": Priority.P1,
    "medium": Priority.P2,
    "low": Priority.P3,
    "info": Priority.P4,
}

DIMENSION_TO_MODULE_INFO: dict[str, dict[str, str]] = {
    "security": {
        "source_blueprint": "MOD-INF-001",
        "assigned_pipeline": "B",
        "pipeline_modules": "M6,M7,M8,M9",
    },
    "architecture": {
        "source_blueprint": "MOD-INF-002",
        "assigned_pipeline": "A",
        "pipeline_modules": "M1,M2,M3",
    },
    "data_quality": {
        "source_blueprint": "MOD-INF-001",
        "assigned_pipeline": "A",
        "pipeline_modules": "M1,M2",
    },
    "governance": {
        "source_blueprint": "MOD-INF-005",
        "assigned_pipeline": "B",
        "pipeline_modules": "M10,M11",
    },
    "performance": {
        "source_blueprint": "MOD-INF-001",
        "assigned_pipeline": "A",
        "pipeline_modules": "M4,M5",
    },
    "compliance": {
        "source_blueprint": "MOD-INF-006",
        "assigned_pipeline": "B",
        "pipeline_modules": "M6,M7",
    },
    "integration": {
        "source_blueprint": "MOD-INF-002",
        "assigned_pipeline": "A",
        "pipeline_modules": "M1,M2,M3,M4",
    },
    "documentation": {
        "source_blueprint": "MOD-INF-005",
        "assigned_pipeline": "A",
        "pipeline_modules": "M1",
    },
}

_DEFAULT_MODULE_INFO: dict[str, str] = {
    "source_blueprint": "MOD-INF-005",
    "assigned_pipeline": "A",
    "pipeline_modules": "M1",
}


@dataclass
class AuditFinding:
    """来自脚本审计系统的一条发现"""
    finding_id: str
    dimension: str
    severity: FindingSeverity
    description: str
    source_script: str = ""
    source_file: str = ""
    suggested_fix: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.severity not in SEVERITY_TO_PRIORITY:
            raise ValueError(f"Invalid severity: {self.severity}")


@dataclass
class BridgeResult:
    """桥接操作结果"""
    findings_processed: int = 0
    tasks_created: int = 0
    tasks_failed: int = 0
    task_ids: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    namespaces_used: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.findings_processed == 0:
            return 0.0
        return self.tasks_created / self.findings_processed


class FindingTaskBridge:
    """将脚本审计发现桥接到任务系统，自动创建 TaskCard。

    使用方式：
        bridge = FindingTaskBridge(repo)
        result = bridge.bridge(findings)
    """

    def __init__(
        self,
        task_repo: TaskRepository,
        default_namespace: TaskNamespace = TaskNamespace.CP,
        min_severity_for_bridge: FindingSeverity = "medium",
        dry_run: bool = False,
    ):
        self._repo = task_repo
        self._default_namespace = default_namespace
        self._min_severity = min_severity_for_bridge
        self._dry_run = dry_run

        _severity_order = ["critical", "high", "medium", "low", "info"]
        self._min_severity_idx = _severity_order.index(min_severity_for_bridge)
        self._severity_order = _severity_order

    def bridge(
        self,
        findings: list[AuditFinding],
        namespace: TaskNamespace | None = None,
        phase: int = 2,
    ) -> BridgeResult:
        """将一批 Finding 转换为 TaskCard 并持久化。

        Args:
            findings: 审计发现列表
            namespace: 任务命名空间，默认使用构造参数
            phase: 施工阶段

        Returns:
            BridgeResult 包含统计信息
        """
        ns = namespace or self._default_namespace
        result = BridgeResult(findings_processed=len(findings))

        for finding in findings:
            if not self._should_bridge(finding):
                continue

            try:
                task = self._finding_to_taskcard(finding, ns, phase)
                if not self._dry_run:
                    self._repo.create(task)
                    result.tasks_created += 1
                    result.task_ids.append(task.task_id)
                    if ns.value not in result.namespaces_used:
                        result.namespaces_used.append(ns.value)
                else:
                    result.tasks_created += 1
            except Exception as e:
                result.tasks_failed += 1
                err_msg = f"[{finding.finding_id}] {type(e).__name__}: {e}"
                result.errors.append(err_msg)
                logger.warning(err_msg)

        return result

    def _should_bridge(self, finding: AuditFinding) -> bool:
        sev_idx = self._severity_order.index(finding.severity)
        return sev_idx <= self._min_severity_idx

    def _finding_to_taskcard(
        self,
        finding: AuditFinding,
        namespace: TaskNamespace,
        phase: int,
    ) -> TaskCard:
        seq = self._repo.next_seq(namespace)
        module_info = DIMENSION_TO_MODULE_INFO.get(
            finding.dimension, _DEFAULT_MODULE_INFO
        )
        priority = SEVERITY_TO_PRIORITY.get(finding.severity, Priority.P3)

        safety = SafetyLevel.M
        if finding.severity in ("critical", "high"):
            safety = SafetyLevel.H

        task_id = f"{namespace.value}-{seq}"

        description = (
            f"[自动桥接] {finding.severity.upper()} Finding: {finding.description}"
        )
        if finding.suggested_fix:
            description += f" — 建议修复: {finding.suggested_fix}"

        upstream: list[str] = []
        if finding.source_file:
            upstream.append(finding.source_file)

        tags = [
            "auto-bridged",
            "from-finding",
            finding.dimension,
        ]

        now = datetime.now(UTC)

        return TaskCard(
            task_id=task_id,
            namespace=namespace,
            seq=seq,
            title=f"[{finding.severity.upper()}] {finding.description[:80]}",
            description=description,
            status=TaskStatus.PENDING,
            priority=priority,
            phase=phase,
            execution_model="deepseek",
            safety_level=safety,
            source_blueprint=module_info["source_blueprint"],
            source_section="§auto(finding_task_bridge)",
            assigned_pipeline=module_info["assigned_pipeline"],
            pipeline_modules=module_info["pipeline_modules"].split(","),
            upstream_files=upstream,
            estimated_tokens=8000,
            timeout_minutes=60,
            completed_gates=[GateLevel.G0],
            construction_status="pending",
            verification_status="unverified",
            tags=tags,
            created_at=now,
            updated_at=now,
        )


def bridge_findings_to_tasks(
    findings: list[AuditFinding],
    db_path: str | Path = "data/zalpha_metadata.db",
    namespace: TaskNamespace | None = None,
    dry_run: bool = False,
) -> BridgeResult:
    """便捷函数：从 Finding 列表到数据库持久化的全链路桥接。

    Args:
        findings: 审计发现列表
        db_path: SQLite 数据库路径
        namespace: 命名空间
        dry_run: 仅模拟不写入

    Returns:
        BridgeResult
    """
    repo = TaskRepository(db_path=Path(db_path), enable_gate=False)
    try:
        bridge = FindingTaskBridge(
            task_repo=repo,
            default_namespace=namespace or TaskNamespace.CP,
            dry_run=dry_run,
        )
        return bridge.bridge(findings)
    finally:
        repo.close()
