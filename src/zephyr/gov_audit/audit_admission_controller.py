# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4
# [MODULE] zephyr.gov_audit.audit_admission_controller
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.finding_model; zephyr.gov_audit.__init__
# [CONSUMERS] gates; orchestrator; pipeline
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 所有审计模块健康检查通过才允许操作; AdmissionResult为唯一准入判定结果
# [MODIFY-GUARD] audit-orchestrator/blueprint.md; audit_admission_controller.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AdmissionResult.allowed=False on any check failure; ImportError->module marked unavailable
# [TESTS] tests/audit-orchestrator/
# [A_module] module_id=MOD-GOV_audit_admission_controller | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from typing import Any

from pydantic import BaseModel, Field

try:
    from zephyr.gov_audit.finding_model import (
        AuditFinding,
        BlastRadius,
        FindingDimension,
        FindingImpact,
        FindingLifecycle,
        FindingRemediation,
        FindingSeverity,
        FindingStatus,
        FindingTarget,
        FindingTraceability,
        RecommendationBlock,
        RemediationAction,
        RemediationPriority,
        generate_finding_id,
    )

    _FINDING_MODEL_AVAILABLE = True
except ImportError:
    _FINDING_MODEL_AVAILABLE = False


class AdmissionResult(BaseModel):
    allowed: bool
    reason: str = ""
    checks_passed: list[str] = Field(default_factory=list)
    checks_failed: list[str] = Field(default_factory=list)
    blocked_by: list[str] = Field(default_factory=list)


class AuditAdmissionController:
    _MODULE_MAP: dict[str, str] = {
        "audit-trail": "zephyr.governance.audit_trail",
        "semantic-auditor": "zephyr.security.semantic_auditor",
        "orphan-judge": "zephyr.security.access_control.orphan_judge",
        "red-blue-validator": "zephyr.security.adversarial_validation",
        "behavioral-auditor": "zephyr.governance.drift_detection",
    }

    def __init__(self) -> None:
        self._modules: dict[str, Any] = {}
        for name, module_path in self._MODULE_MAP.items():
            try:
                import importlib

                self._modules[name] = importlib.import_module(module_path)
            except ImportError:
                self._modules[name] = None

    def check_admission(self, operation: str, target_path: str) -> AdmissionResult:
        health = self.full_health_check()
        passed = [k for k, v in health.items() if v]
        failed = [k for k, v in health.items() if not v]
        blocked = [k for k in failed if self._modules.get(k) is None]
        allowed = len(failed) == 0
        reason = "" if allowed else f"blocked by: {', '.join(failed)}"
        return AdmissionResult(
            allowed=allowed,
            reason=reason,
            checks_passed=passed,
            checks_failed=failed,
            blocked_by=blocked,
        )

    def check_audit_trail_health(self) -> bool:
        return self._modules.get("audit-trail") is not None

    def check_semantic_auditor_health(self) -> bool:
        return self._modules.get("semantic-auditor") is not None

    def check_orphan_judge_health(self) -> bool:
        return self._modules.get("orphan-judge") is not None

    def check_red_blue_health(self) -> bool:
        return self._modules.get("red-blue-validator") is not None

    def check_behavioral_health(self) -> bool:
        return self._modules.get("behavioral-auditor") is not None

    def full_health_check(self, jsonl_output: bool = False) -> dict[str, bool]:
        result = {
            "audit-trail": self.check_audit_trail_health(),
            "semantic-auditor": self.check_semantic_auditor_health(),
            "orphan-judge": self.check_orphan_judge_health(),
            "red-blue-validator": self.check_red_blue_health(),
            "behavioral-auditor": self.check_behavioral_health(),
        }
        if jsonl_output:
            self._output_health_as_jsonl(result)
        return result

    _MODULE_DIMENSION_MAP: dict[str, str] = {
        "semantic-auditor": "D12",
        "orphan-judge": "D1",
        "red-blue-validator": "D6",
        "behavioral-auditor": "D12",
        "audit-trail": "D1",
    }

    _HEALTH_SEVERITY_MAP: dict[str, str] = {
        "UNHEALTHY": "HIGH",
        "DEGRADED": "MEDIUM",
        "HEALTHY": "INFO",
    }

    def _output_health_as_jsonl(self, health: dict[str, bool]) -> list[str]:
        if not _FINDING_MODEL_AVAILABLE:
            return []
        findings: list[AuditFinding] = []
        for module_name, is_healthy in health.items():
            health_status = "HEALTHY" if is_healthy else "UNHEALTHY"
            sev_str = self._HEALTH_SEVERITY_MAP.get(health_status, "MEDIUM")
            dim_str = self._MODULE_DIMENSION_MAP.get(module_name, "D1")
            finding = AuditFinding(
                finding_id=generate_finding_id(dim_str, f"health:{module_name}"),
                dimension=FindingDimension(dim_str),
                severity=FindingSeverity(sev_str),
                category="审计模块健康检查",
                target=FindingTarget(file_path=f"zephyr.{module_name}"),
                description=f"Module {module_name} health check: {health_status}",
                evidence=f"healthy={is_healthy}",
                impact=FindingImpact(blast_radius=BlastRadius.module),
                remediation=FindingRemediation(
                    action=RemediationAction.INVESTIGATE,
                    priority=RemediationPriority.P1 if not is_healthy else RemediationPriority.P4,
                ),
                lifecycle=FindingLifecycle(status=FindingStatus.OPEN if not is_healthy else FindingStatus.CLOSED),
                traceability=FindingTraceability(),
                recommendation_block=RecommendationBlock(),
            )
            findings.append(finding)
        jsonl_lines: list[str] = []
        for f in findings:
            jsonl_lines.append(f.to_jsonl())
        if jsonl_lines:
            try:
                from zephyr.gov_audit.finding_ingest import FindingIngest

                ingest = FindingIngest()
                ingest.ingest_findings(findings)
            except Exception as e:
                logger.warning("suppressed error in audit_admission_controller", exc_info=True)
        return jsonl_lines
