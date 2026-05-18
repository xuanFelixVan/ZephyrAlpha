# [BLUEPRINT] MOD-INF-035 | 03_modules/_cross_layer/auto-runtime-core/blueprint.md | §

# [MODULE] zephyr.orchestrator.finding_bridge

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
CT-ORC-SCRIPT-001 运行时桥接
============================
Script System -> Orchestrator: Finding -> TaskCard 转换管道

数据流：
    script_system.Finding -> AuditFinding -> FindingTaskBridge -> TaskRepository -> TaskCard
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence

from zephyr.l01_infrastructure.finding_task_bridge import (
    AuditFinding,
    BridgeResult,
    FindingTaskBridge,
    SEVERITY_TO_PRIORITY,
)
from zephyr.db.task_repo import TaskRepository
from zephyr.core.models import TaskNamespace

_logger = logging.getLogger(__name__)

__all__ = [
    "report_finding",
    "report_findings",
    "finding_to_audit_finding",
]

_SEVERITY_MAP: dict[str, str] = {
    "CRITICAL": "critical",
    "HIGH": "high",
    "MEDIUM": "medium",
    "LOW": "low",
    "INFO": "info",
}


def finding_to_audit_finding(finding: object) -> AuditFinding:
    dim = getattr(finding, "dimension", None)
    dimension_str = dim.value if dim is not None and hasattr(dim, "value") else str(dim or "unknown")

    sev = getattr(finding, "severity", None)
    sev_str = sev.value if sev is not None and hasattr(sev, "value") else str(sev or "medium")
    sev_normalized = _SEVERITY_MAP.get(sev_str, "medium")

    desc = getattr(finding, "description", "") or str(finding)
    target = getattr(finding, "target_file", "") or ""
    evidence = getattr(finding, "evidence", "") or ""
    fid = getattr(finding, "finding_id", "") or ""
    category = getattr(finding, "category", "") or ""

    suggested_fix = evidence
    if hasattr(finding, "remediation_action"):
        ra = getattr(finding, "remediation_action", None)
        if ra is not None:
            suggested_fix = f"[{ra.value}] {evidence}" if hasattr(ra, "value") else str(ra)

    metadata = {
        "source_file": target,
        "category": category,
        "dimension_raw": dimension_str,
    }
    if fid:
        metadata["finding_id"] = fid

    return AuditFinding(
        finding_id=fid or f"FIND-{dimension_str}-{category}",
        dimension=dimension_str,
        severity=sev_normalized,
        description=desc,
        source_script="script_system",
        source_file=target,
        suggested_fix=suggested_fix,
        metadata=metadata,
    )


def report_finding(
    finding: object,
    db_path: str | Path = "data/zalpha_metadata.db",
    namespace: TaskNamespace | None = None,
    dry_run: bool = False,
) -> BridgeResult:
    audit = finding_to_audit_finding(finding)
    return report_findings([audit], db_path=db_path, namespace=namespace, dry_run=dry_run)


def report_findings(
    findings: Sequence[object | AuditFinding],
    db_path: str | Path = "data/zalpha_metadata.db",
    namespace: TaskNamespace | None = None,
    dry_run: bool = False,
    min_severity: str = "medium",
) -> BridgeResult:
    audit_findings: list[AuditFinding] = []
    for f in findings:
        if isinstance(f, AuditFinding):
            audit_findings.append(f)
        else:
            audit_findings.append(finding_to_audit_finding(f))

    repo = TaskRepository(db_path=Path(db_path), enable_gate=True)
    try:
        bridge = FindingTaskBridge(
            task_repo=repo,
            default_namespace=namespace or TaskNamespace.CP,
            min_severity_for_bridge=min_severity,
            dry_run=dry_run,
        )
        result = bridge.bridge(audit_findings)
        _logger.info(
            "report_findings: %d processed, %d tasks created, %d failed",
            result.findings_processed,
            result.tasks_created,
            result.tasks_failed,
        )
        return result
    finally:
        repo.close()
