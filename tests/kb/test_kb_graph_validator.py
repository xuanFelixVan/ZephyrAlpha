# [A_test] module_id: SRC-TST-1167 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_graph_validator
# [INVARIANTS] GraphValidator.validate returns ValidationReport; check_near_duplicate is standalone
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_kb.graph_validator import (
    ValidationIssue,
    ValidationReport,
    ValidationSeverity,
    _normalize,
)


class TestValidationSeverity:
    def test_enum_values(self):
        assert ValidationSeverity.ERROR.value == "ERROR"
        assert ValidationSeverity.WARNING.value == "WARNING"
        assert ValidationSeverity.INFO.value == "INFO"


class TestValidationIssue:
    def test_creation(self):
        issue = ValidationIssue(
            check_id="GV-001",
            severity=ValidationSeverity.WARNING,
            description="Test issue",
            ke_id="KE-001",
        )
        assert issue.check_id == "GV-001"
        assert issue.severity == ValidationSeverity.WARNING
        assert issue.description == "Test issue"
        assert issue.details == {}


class TestValidationReport:
    def test_default_values(self):
        r = ValidationReport()
        assert r.total_checked == 0
        assert r.error_count == 0
        assert r.warning_count == 0
        assert r.info_count == 0
        assert r.issues == []
        assert r.passed is True

    def test_with_errors(self):
        r = ValidationReport(
            error_count=1,
            issues=[ValidationIssue(check_id="GV-001", severity=ValidationSeverity.ERROR, description="err")],
            passed=False,
        )
        assert r.passed is False


class TestNormalize:
    def test_basic(self):
        assert _normalize("Hello World") == "hello world"

    def test_punctuation_removed(self):
        result = _normalize("Hello, World! Test.")
        assert "," not in result
        assert "!" not in result

    def test_whitespace_normalized(self):
        result = _normalize("Hello   World")
        assert "  " not in result
