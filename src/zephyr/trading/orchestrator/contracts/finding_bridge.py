# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.contracts.finding_bridge
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.contracts.task_repository_protocol; zephyr.shared.models
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_finding_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CT-ORC-SCRIPT-001 运行时桥接
============================
Script System -> Orchestrator: Finding -> TaskCard 转换管道

数据流：
    script_system.Finding -> AuditFinding -> FindingTaskBridge -> TaskRepository -> TaskCard
"""

from __future__ import annotations

from typing import Final
import importlib as _importlib
import logging
from collections.abc import Sequence
from pathlib import Path

_bridge_mod = _importlib.import_module("zephyr.infrastructure.finding_task_bridge")
AuditFinding = _bridge_mod.AuditFinding
BridgeResult = _bridge_mod.BridgeResult
FindingTaskBridge = _bridge_mod.FindingTaskBridge
SEVERITY_TO_PRIORITY: Final[Any] = _bridge_mod.SEVERITY_TO_PRIORITY
from zephyr.shared.io.paths import DB_PATH
from zephyr.shared.foundation.models import TaskNamespace

_logger = logging.getLogger(__name__)

# 治本(2026-06-30): 消除默认参数硬编码 "data/databases/governance.db", 改用 SSoT 源
_DEFAULT_DB_PATH = str(DB_PATH)

__all__ = [
    "finding_to_audit_finding",
    "report_finding",
    "report_findings",
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
    db_path: str | Path = _DEFAULT_DB_PATH,
    namespace: TaskNamespace | None = None,
    dry_run: bool = False,
) -> BridgeResult:
    audit = finding_to_audit_finding(finding)
    return report_findings([audit], db_path=db_path, namespace=namespace, dry_run=dry_run)


def report_findings(
    findings: Sequence[object | AuditFinding],
    db_path: str | Path = _DEFAULT_DB_PATH,
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

    from zephyr.governance.persistence.task_repo import TaskRepository  # deferred: break trading→governance cycle (#8)

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
