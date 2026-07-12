# [A_test] module_id: SRC-TST-0555 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_compliance_map
# [INVARIANTS] ComplianceMapper.map_event returns ComplianceMapping; framework filtering
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass; exit non-zero on fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_audit.compliance_map import (
    ComplianceFramework,
    ComplianceMapper,
    ComplianceMapping,
    ComplianceRequirement,
)
from zephyr.gov_audit.models import AuditEventType


class TestComplianceFramework:
    def test_enum_values(self):
        assert ComplianceFramework.GDPR == "gdpr"
        assert ComplianceFramework.HIPAA == "hipaa"
        assert ComplianceFramework.EU_AI_ACT == "eu_ai_act"
        assert ComplianceFramework.NIST == "nist"
        assert ComplianceFramework.SOC2 == "soc2"
        assert ComplianceFramework.ISO27001 == "iso27001"


class TestComplianceRequirement:
    def test_creation(self):
        req = ComplianceRequirement(
            framework=ComplianceFramework.GDPR,
            article="Art.25",
            title="Data Protection by Design",
            severity="high",
        )
        assert req.framework == ComplianceFramework.GDPR
        assert req.article == "Art.25"
        assert req.severity == "high"

    def test_default_severity(self):
        req = ComplianceRequirement(framework=ComplianceFramework.NIST)
        assert req.severity == "medium"


class TestComplianceMapping:
    def test_creation(self):
        mapping = ComplianceMapping(event_type="test_event")
        assert mapping.event_type == "test_event"
        assert mapping.requirements == []


class TestComplianceMapper:
    def test_map_known_event_type(self):
        mapper = ComplianceMapper()
        mapping = mapper.map_event(AuditEventType.PERMISSION_VIOLATION.value)
        assert mapping.event_type == "permission_violation"
        assert len(mapping.requirements) > 0

    def test_map_unknown_event_type(self):
        mapper = ComplianceMapper()
        mapping = mapper.map_event("unknown_event_type")
        assert mapping.event_type == "unknown_event_type"
        assert len(mapping.requirements) == 0

    def test_get_requirements_by_framework(self):
        mapper = ComplianceMapper()
        gdpr_reqs = mapper.get_requirements(framework=ComplianceFramework.GDPR)
        assert len(gdpr_reqs) > 0
        for req in gdpr_reqs:
            assert req.framework == ComplianceFramework.GDPR

    def test_get_requirements_by_event_type(self):
        mapper = ComplianceMapper()
        reqs = mapper.get_requirements(event_type=AuditEventType.FILE_DELETE.value)
        assert len(reqs) > 0

    def test_get_requirements_no_filter(self):
        mapper = ComplianceMapper()
        all_reqs = mapper.get_requirements()
        assert len(all_reqs) > 0

    def test_get_frameworks_for_event(self):
        mapper = ComplianceMapper()
        frameworks = mapper.get_frameworks_for_event(AuditEventType.PERMISSION_VIOLATION.value)
        assert ComplianceFramework.GDPR in frameworks
        assert ComplianceFramework.NIST in frameworks

    def test_custom_mappings_extend(self):
        custom = {
            "custom_event": [
                ComplianceRequirement(
                    framework=ComplianceFramework.GDPR,
                    article="Art.99",
                    title="Custom",
                    severity="low",
                ),
            ],
        }
        mapper = ComplianceMapper(custom_mappings=custom)
        mapping = mapper.map_event("custom_event")
        assert len(mapping.requirements) == 1
        assert mapping.requirements[0].article == "Art.99"

    def test_custom_mappings_extend_existing(self):
        existing_count = len(ComplianceMapper().map_event(AuditEventType.PERMISSION_VIOLATION.value).requirements)
        custom = {
            AuditEventType.PERMISSION_VIOLATION.value: [
                ComplianceRequirement(
                    framework=ComplianceFramework.ISO27001,
                    article="A.9",
                    title="Access Control",
                    severity="medium",
                ),
            ],
        }
        mapper = ComplianceMapper(custom_mappings=custom)
        mapping = mapper.map_event(AuditEventType.PERMISSION_VIOLATION.value)
        assert len(mapping.requirements) == existing_count + 1
