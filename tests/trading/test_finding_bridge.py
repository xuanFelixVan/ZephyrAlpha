# [A_test] module_id: SRC-TST-0916 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §test
# [MODULE] tests.test_finding_bridge
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_finding_bridge.py
# [TTL] task_bound

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from zephyr.orchestrator.contracts.finding_bridge import (
    _SEVERITY_MAP,
    finding_to_audit_finding,
    report_finding,
    report_findings,
)


class TestSeverityMap:
    def test_critical_mapping(self):
        assert _SEVERITY_MAP["CRITICAL"] == "critical"

    def test_high_mapping(self):
        assert _SEVERITY_MAP["HIGH"] == "high"

    def test_medium_mapping(self):
        assert _SEVERITY_MAP["MEDIUM"] == "medium"

    def test_low_mapping(self):
        assert _SEVERITY_MAP["LOW"] == "low"

    def test_info_mapping(self):
        assert _SEVERITY_MAP["INFO"] == "info"


class TestFindingToAuditFinding:
    def test_basic_finding_conversion(self):
        finding = SimpleNamespace(
            dimension=SimpleNamespace(value="completeness"),
            severity=SimpleNamespace(value="HIGH"),
            description="Test finding",
            target_file="test.py",
            evidence="evidence text",
            finding_id="F-001",
            category="test_cat",
        )
        result = finding_to_audit_finding(finding)
        assert result.dimension == "completeness"
        assert result.severity == "high"
        assert result.description == "Test finding"
        assert result.source_file == "test.py"
        assert result.finding_id == "F-001"

    def test_finding_without_enum_values(self):
        finding = SimpleNamespace(
            dimension="accuracy",
            severity="LOW",
            description="Simple finding",
            target_file="",
            evidence="",
            finding_id="",
            category="",
        )
        result = finding_to_audit_finding(finding)
        assert result.dimension == "accuracy"
        assert result.severity == "low"

    def test_finding_with_none_attributes(self):
        finding = SimpleNamespace(
            dimension=None,
            severity=None,
            description=None,
            target_file=None,
            evidence=None,
            finding_id=None,
            category=None,
        )
        result = finding_to_audit_finding(finding)
        assert result.dimension == "unknown"
        assert result.severity == "medium"

    def test_finding_with_remediation_action(self):
        finding = SimpleNamespace(
            dimension=SimpleNamespace(value="security"),
            severity=SimpleNamespace(value="CRITICAL"),
            description="Security issue",
            target_file="secret.py",
            evidence="leaked key",
            finding_id="F-002",
            category="secret_leak",
            remediation_action=SimpleNamespace(value="ROTATE_KEY"),
        )
        result = finding_to_audit_finding(finding)
        assert "[ROTATE_KEY]" in result.suggested_fix

    def test_finding_with_string_remediation_action(self):
        finding = SimpleNamespace(
            dimension="security",
            severity="MEDIUM",
            description="Issue",
            target_file="",
            evidence="ev",
            finding_id="",
            category="",
            remediation_action="fix it now",
        )
        result = finding_to_audit_finding(finding)
        assert result.suggested_fix == "fix it now"

    def test_finding_metadata_contains_source_file(self):
        finding = SimpleNamespace(
            dimension="test",
            severity="LOW",
            description="",
            target_file="path/to/file.py",
            evidence="",
            finding_id="F-003",
            category="cat",
        )
        result = finding_to_audit_finding(finding)
        assert result.metadata["source_file"] == "path/to/file.py"

    def test_finding_metadata_contains_finding_id(self):
        finding = SimpleNamespace(
            dimension="test",
            severity="LOW",
            description="",
            target_file="",
            evidence="",
            finding_id="F-004",
            category="",
        )
        result = finding_to_audit_finding(finding)
        assert result.metadata["finding_id"] == "F-004"

    def test_finding_without_finding_id_generates_one(self):
        finding = SimpleNamespace(
            dimension="completeness",
            severity="MEDIUM",
            description="",
            target_file="",
            evidence="",
            finding_id="",
            category="cat_a",
        )
        result = finding_to_audit_finding(finding)
        assert "completeness" in result.finding_id
        assert "cat_a" in result.finding_id

    def test_unknown_severity_defaults_to_medium(self):
        finding = SimpleNamespace(
            dimension="test",
            severity="UNKNOWN",
            description="",
            target_file="",
            evidence="",
            finding_id="",
            category="",
        )
        result = finding_to_audit_finding(finding)
        assert result.severity == "medium"


class TestReportFinding:
    def test_report_finding_calls_report_findings(self):
        mock_result = MagicMock()
        mock_result.findings_processed = 1
        mock_result.tasks_created = 0
        mock_result.tasks_failed = 0
        with patch("zephyr.trading.orchestrator.finding_bridge.report_findings", return_value=mock_result) as mock_rf:
            finding = SimpleNamespace(
                dimension="test",
                severity="LOW",
                description="test",
                target_file="",
                evidence="",
                finding_id="F-100",
                category="",
            )
            result = report_finding(finding, dry_run=True)
            mock_rf.assert_called_once()
            assert result.findings_processed == 1


class TestReportFindings:
    def test_report_findings_with_audit_finding_objects(self):
        mock_audit_finding = MagicMock()
        mock_audit_finding_instance = MagicMock()
        mock_bridge_result = MagicMock()
        mock_bridge_result.findings_processed = 1
        mock_bridge_result.tasks_created = 0
        mock_bridge_result.tasks_failed = 0

        with (
            patch("zephyr.trading.orchestrator.finding_bridge.FindingTaskBridge") as mock_bridge_cls,
            patch("zephyr.trading.orchestrator.finding_bridge.TaskRepository") as mock_repo_cls,
        ):
            mock_repo = MagicMock()
            mock_repo_cls.return_value = mock_repo
            mock_bridge = MagicMock()
            mock_bridge.bridge.return_value = mock_bridge_result
            mock_bridge_cls.return_value = mock_bridge

            result = report_findings([mock_audit_finding_instance], dry_run=True)
            assert result.findings_processed == 1
            mock_repo.close.assert_called_once()
