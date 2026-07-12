# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.gov_audit.compliance_map
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.models
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
# [A_module] module_id=MOD-GOV_compliance_map | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
audit-trail.compliance_map — MOD-INF-020 · 合规框架映射
========================================================
蓝图 D-020-25 · GDPR/HIPAA/EU AI Act/NIST 映射表

映射规则
--------
  将审计事件类型映射到合规框架的具体条款/要求
  支持多框架交叉映射
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from zephyr.gov_audit.models import AuditEventType

_logger = logging.getLogger(__name__)


class ComplianceFramework(str, Enum):
    GDPR = "gdpr"
    HIPAA = "hipaa"
    EU_AI_ACT = "eu_ai_act"
    NIST = "nist"
    SOC2 = "soc2"
    ISO27001 = "iso27001"


class ComplianceRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    framework: ComplianceFramework = ComplianceFramework.GDPR
    article: str = ""
    title: str = ""
    description: str = ""
    severity: str = "medium"


class ComplianceMapping(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_type: str = ""
    requirements: list[ComplianceRequirement] = Field(default_factory=list)
    mapped_at: str = ""


_COMPLIANCE_TABLE: dict[str, list[ComplianceRequirement]] = {
    AuditEventType.PERMISSION_VIOLATION.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.GDPR,
            article="Art.25",
            title="Data Protection by Design",
            description="Access control violations must be logged",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="AC-2",
            title="Account Management",
            description="Unauthorized access attempts must be audited",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.SOC2,
            article="CC6.1",
            title="Logical Access",
            description="Access violations tracked",
            severity="high",
        ),
    ],
    AuditEventType.FILE_DELETE.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.GDPR,
            article="Art.17",
            title="Right to Erasure",
            description="Data deletion must be recorded",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.HIPAA,
            article="164.312(b)",
            title="Audit Controls",
            description="Record information system activity",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="AU-2",
            title="Audit Events",
            description="Delete operations must be auditable",
            severity="medium",
        ),
    ],
    AuditEventType.FILE_WRITE.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.GDPR,
            article="Art.30",
            title="Records of Processing",
            description="Data modification must be logged",
            severity="medium",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.HIPAA,
            article="164.312(b)",
            title="Audit Controls",
            description="Record system activity including writes",
            severity="medium",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="AU-2",
            title="Audit Events",
            description="Write operations must be auditable",
            severity="medium",
        ),
    ],
    AuditEventType.ANOMALY_DETECTED.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.GDPR,
            article="Art.33",
            title="Breach Notification",
            description="Anomalies may indicate data breaches",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.HIPAA,
            article="164.312(b)",
            title="Audit Controls",
            description="Anomaly detection supports audit review",
            severity="medium",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.EU_AI_ACT,
            article="Art.14",
            title="Human Oversight",
            description="Anomalies require human review",
            severity="high",
        ),
    ],
    AuditEventType.TRUST_SCORE_CHANGE.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.EU_AI_ACT,
            article="Art.9",
            title="Risk Management",
            description="Trust score changes indicate risk level changes",
            severity="medium",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="RA-3",
            title="Risk Assessment",
            description="Trust changes must be tracked for risk management",
            severity="medium",
        ),
    ],
    AuditEventType.KB_POISONING_ATTEMPT.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.EU_AI_ACT,
            article="Art.15",
            title="Accuracy and Robustness",
            description="KB poisoning threatens AI system integrity",
            severity="critical",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="SI-3",
            title="Malicious Code Protection",
            description="Poisoning is a form of malicious content injection",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.GDPR,
            article="Art.25",
            title="Data Protection by Design",
            description="Input validation required",
            severity="high",
        ),
    ],
    AuditEventType.SUPPLY_CHAIN_INSTALL.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="SR-3",
            title="Supply Chain Protection",
            description="Package integrity must be verified",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.EU_AI_ACT,
            article="Art.15",
            title="Accuracy and Robustness",
            description="Supply chain integrity affects AI robustness",
            severity="medium",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.ISO27001,
            article="A.15",
            title="Supplier Relationships",
            description="Supply chain security controls",
            severity="medium",
        ),
    ],
    AuditEventType.DELEGATION_CHAIN_ISSUE.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.GDPR,
            article="Art.25",
            title="Data Protection by Design",
            description="Delegation must enforce least privilege",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="AC-4",
            title="Information Flow Enforcement",
            description="Delegation chains must be controlled",
            severity="high",
        ),
    ],
    AuditEventType.FEEDBACK_LOOP_SELF_REINFORCING.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.EU_AI_ACT,
            article="Art.9",
            title="Risk Management",
            description="Self-reinforcing loops create systemic risk",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="SI-4",
            title="System Monitoring",
            description="Feedback loops must be monitored",
            severity="medium",
        ),
    ],
    AuditEventType.DRIFT_DETECTED.value: [
        ComplianceRequirement(
            framework=ComplianceFramework.EU_AI_ACT,
            article="Art.15",
            title="Accuracy and Robustness",
            description="Drift affects AI accuracy",
            severity="high",
        ),
        ComplianceRequirement(
            framework=ComplianceFramework.NIST,
            article="SI-4",
            title="System Monitoring",
            description="Drift indicates system changes",
            severity="medium",
        ),
    ],
}


class ComplianceMapper:
    def __init__(self, custom_mappings: dict[str, list[ComplianceRequirement]] | None = None) -> None:
        self._mappings: dict[str, list[ComplianceRequirement]] = dict(_COMPLIANCE_TABLE)
        if custom_mappings:
            for event_type, requirements in custom_mappings.items():
                if event_type in self._mappings:
                    self._mappings[event_type].extend(requirements)
                else:
                    self._mappings[event_type] = requirements

    def map_event(self, event_type: str) -> ComplianceMapping:
        requirements = self._mappings.get(event_type, [])
        return ComplianceMapping(
            event_type=event_type,
            requirements=requirements,
            mapped_at=datetime.now(UTC).isoformat(),
        )

    def get_requirements(
        self,
        framework: ComplianceFramework | None = None,
        event_type: str | None = None,
    ) -> list[ComplianceRequirement]:
        requirements: list[ComplianceRequirement] = []
        source = (
            {event_type: self._mappings[event_type]} if event_type and event_type in self._mappings else self._mappings
        )
        for reqs in source.values():
            for req in reqs:
                if framework and req.framework != framework:
                    continue
                requirements.append(req)
        return requirements

    def get_frameworks_for_event(self, event_type: str) -> list[ComplianceFramework]:
        mapping = self.map_event(event_type)
        return list({r.framework for r in mapping.requirements})
