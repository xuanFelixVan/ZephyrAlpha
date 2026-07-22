# [A_test] module_id: MOD-GOV_finding_task_bridge | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §finding_task_bridge
# [MODULE] tests.test_finding_task_bridge
# [INVARIANTS] AuditFinding.severity必须在SEVERITY_TO_PRIORITY中; BridgeResult.success_rate计算正确
# [MODIFY-GUARD] 仅当finding_task_bridge公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_finding_task_bridge.py -q
# [TTL] task_bound

from unittest.mock import MagicMock

import pytest

from zephyr.infrastructure.finding_task_bridge import (
    DIMENSION_TO_MODULE_INFO,
    SEVERITY_TO_PRIORITY,
    AuditFinding,
    BridgeResult,
    FindingTaskBridge,
)


class TestSEVERITY_TO_PRIORITY:
    def test_all_severity_levels_mapped(self):
        assert "critical" in SEVERITY_TO_PRIORITY
        assert "high" in SEVERITY_TO_PRIORITY
        assert "medium" in SEVERITY_TO_PRIORITY
        assert "low" in SEVERITY_TO_PRIORITY
        assert "info" in SEVERITY_TO_PRIORITY


class TestDIMENSION_TO_MODULE_INFO:
    def test_known_dimensions(self):
        assert "security" in DIMENSION_TO_MODULE_INFO
        assert "architecture" in DIMENSION_TO_MODULE_INFO
        assert "governance" in DIMENSION_TO_MODULE_INFO

    def test_each_has_required_keys(self):
        for dim, info in DIMENSION_TO_MODULE_INFO.items():
            assert "source_blueprint" in info
            assert "assigned_pipeline" in info
            assert "pipeline_modules" in info


class TestAuditFinding:
    def test_valid_severity(self):
        finding = AuditFinding(
            finding_id="F-001",
            dimension="security",
            severity="critical",
            description="SQL injection detected",
        )
        assert finding.finding_id == "F-001"
        assert finding.severity == "critical"

    def test_invalid_severity_raises(self):
        with pytest.raises(ValueError, match="Invalid severity"):
            AuditFinding(
                finding_id="F-002",
                dimension="security",
                severity="unknown",
                description="test",
            )

    def test_default_fields(self):
        finding = AuditFinding(
            finding_id="F-003",
            dimension="architecture",
            severity="low",
            description="test finding",
        )
        assert finding.source_script == ""
        assert finding.source_file == ""
        assert finding.suggested_fix == ""
        assert finding.metadata == {}


class TestBridgeResult:
    def test_default_construction(self):
        result = BridgeResult()
        assert result.findings_processed == 0
        assert result.tasks_created == 0
        assert result.tasks_failed == 0
        assert result.success_rate == 0.0

    def test_success_rate_calculation(self):
        result = BridgeResult(findings_processed=10, tasks_created=8)
        assert result.success_rate == 0.8

    def test_success_rate_zero_processed(self):
        result = BridgeResult(findings_processed=0, tasks_created=0)
        assert result.success_rate == 0.0


class TestFindingTaskBridge:
    def test_instantiation(self):
        mock_repo = MagicMock()
        bridge = FindingTaskBridge(task_repo=mock_repo)
        assert bridge is not None

    def test_bridge_dry_run(self):
        mock_repo = MagicMock()
        mock_repo.next_seq.return_value = 1
        bridge = FindingTaskBridge(task_repo=mock_repo, dry_run=True)
        findings = [
            AuditFinding(
                finding_id="F-100",
                dimension="security",
                severity="high",
                description="vulnerability found",
            ),
        ]
        result = bridge.bridge(findings)
        assert result.findings_processed == 1
        assert result.tasks_created == 1
        mock_repo.create.assert_not_called()

    def test_bridge_filters_low_severity(self):
        mock_repo = MagicMock()
        bridge = FindingTaskBridge(
            task_repo=mock_repo,
            min_severity_for_bridge="high",
            dry_run=True,
        )
        findings = [
            AuditFinding(
                finding_id="F-200",
                dimension="security",
                severity="low",
                description="minor issue",
            ),
        ]
        result = bridge.bridge(findings)
        assert result.tasks_created == 0

    def test_bridge_filters_script_error_keywords(self):
        mock_repo = MagicMock()
        bridge = FindingTaskBridge(task_repo=mock_repo, dry_run=True)
        findings = [
            AuditFinding(
                finding_id="F-300",
                dimension="governance",
                severity="high",
                description="脚本执行异常 occurred",
            ),
        ]
        result = bridge.bridge(findings)
        assert result.tasks_created == 0

    def test_bridge_creates_task_for_valid_finding(self):
        mock_repo = MagicMock()
        mock_repo.next_seq.return_value = 1
        bridge = FindingTaskBridge(task_repo=mock_repo, dry_run=False)
        findings = [
            AuditFinding(
                finding_id="F-400",
                dimension="architecture",
                severity="medium",
                description="circular dependency",
                suggested_fix="refactor module",
            ),
        ]
        result = bridge.bridge(findings)
        assert result.tasks_created == 1
        mock_repo.create.assert_called_once()

    def test_bridge_handles_repo_error(self):
        mock_repo = MagicMock()
        mock_repo.next_seq.return_value = 1
        mock_repo.create.side_effect = RuntimeError("DB error")
        bridge = FindingTaskBridge(task_repo=mock_repo, dry_run=False)
        findings = [
            AuditFinding(
                finding_id="F-500",
                dimension="security",
                severity="critical",
                description="breach detected",
            ),
        ]
        result = bridge.bridge(findings)
        assert result.tasks_failed == 1
        assert len(result.errors) == 1

    def test_bridge_empty_findings(self):
        mock_repo = MagicMock()
        bridge = FindingTaskBridge(task_repo=mock_repo)
        result = bridge.bridge([])
        assert result.findings_processed == 0
        assert result.tasks_created == 0
