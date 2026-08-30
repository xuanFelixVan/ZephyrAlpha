# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.contracts.finding_bridge
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.shared.contracts.task_repository_protocol; zephyr.shared.models
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
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CT-ORC-SCRIPT-001 运行时桥接
============================
Script System -> Orchestrator: Finding -> TaskCard 转换管道

数据流：
    script_system.Finding -> AuditFinding -> FindingTaskBridge -> TaskRepository -> TaskCard

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: finding 参数
#   fields: 参数 finding，类型注解 object
#   code: finding_bridge.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: db_path 参数
#   fields: 参数 db_path，类型注解 str | Path
#   code: finding_bridge.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: namespace 参数
#   fields: 参数 namespace，类型注解 TaskNamespace | None
#   code: finding_bridge.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: dry_run 参数
#   fields: 参数 dry_run，类型注解 bool
#   code: finding_bridge.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① finding_to_audit_finding
#   name_en: finding_to_audit_finding
#   intro: finding_to_audit_finding(finding) 源码 L145-L174
#   desc: 源码 L145-L174
#   inputs: finding
#   outputs: AuditFinding
# - id: A2
#   name_zh: ② report_finding
#   name_en: report_finding
#   intro: report_finding(finding, db_path, namespace, dry_run) 源码 L17…
#   desc: 源码 L177-L184
#   inputs: finding db_path namespace dry_run
#   outputs: BridgeResult
# - id: A3
#   name_zh: ③ report_findings
#   name_en: report_findings
#   intro: report_findings(findings, db_path, namespace, dry_run, min_…
#   desc: 源码 L187-L220
#   inputs: findings db_path namespace dry_run min_severity
#   outputs: BridgeResult
# 层: 输出
# - id: O1
#   name_zh: AuditFinding
#   name_en: AuditFinding
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: BridgeResult
#   name_en: BridgeResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import importlib as _importlib
import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Final

_bridge_mod = _importlib.import_module("zephyr.infrastructure.finding_task_bridge")
AuditFinding = _bridge_mod.AuditFinding
BridgeResult = _bridge_mod.BridgeResult
FindingTaskBridge = _bridge_mod.FindingTaskBridge
SEVERITY_TO_PRIORITY: Final[Any] = _bridge_mod.SEVERITY_TO_PRIORITY
from zephyr.shared.foundation.models import TaskNamespace
from zephyr.shared.io.paths import DB_PATH

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


def _normalize_dimension(finding: object) -> str:
    dim = getattr(finding, "dimension", None)
    return dim.value if dim is not None and hasattr(dim, "value") else str(dim or "unknown")


def _normalize_severity(finding: object) -> str:
    sev = getattr(finding, "severity", None)
    sev_str = sev.value if sev is not None and hasattr(sev, "value") else str(sev or "medium")
    return _SEVERITY_MAP.get(sev_str, "medium")


def _compute_suggested_fix(finding: object, evidence: str) -> str:
    suggested_fix = evidence
    if hasattr(finding, "remediation_action"):
        ra = getattr(finding, "remediation_action", None)
        if ra is not None:
            suggested_fix = f"[{ra.value}] {evidence}" if hasattr(ra, "value") else str(ra)
    return suggested_fix


def finding_to_audit_finding(finding: object) -> AuditFinding:
    dimension_str = _normalize_dimension(finding)
    sev_normalized = _normalize_severity(finding)

    desc = getattr(finding, "description", "") or str(finding)
    target = getattr(finding, "target_file", "") or ""
    evidence = getattr(finding, "evidence", "") or ""
    fid = getattr(finding, "finding_id", "") or ""
    category = getattr(finding, "category", "") or ""

    suggested_fix = _compute_suggested_fix(finding, evidence)

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

    from zephyr.governance.persistence.task_repo import TaskRepository  # deferred: break trading->governance cycle (#8)

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
