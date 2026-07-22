# [A_test] module_id: MOD-GOV_l7_red_team | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] tests.llm_security.test_l7_red_team
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
import pytest

from zephyr.security.llm_defense.llm_security.self_protection.red_team_scanner import (
    PayloadResult,
    RedTeamScanner,
    ScanMode,
    ScanReport,
    ScanTarget,
)


class TestRedTeamScannerCreation:
    def test_default_mode_full_target_input(self):
        scanner = RedTeamScanner()
        assert scanner.mode == ScanMode.FULL
        assert scanner.target == ScanTarget.INPUT

    def test_quick_mode_input_only(self):
        scanner = RedTeamScanner(mode=ScanMode.QUICK, target=ScanTarget.INPUT)
        assert scanner.mode == ScanMode.QUICK
        assert scanner.target == ScanTarget.INPUT

    def test_results_empty_before_run(self):
        scanner = RedTeamScanner()
        assert len(scanner.results) == 0


class TestQuickScan:
    def test_quick_scan_returns_report(self):
        scanner = RedTeamScanner(mode=ScanMode.QUICK, target=ScanTarget.INPUT)
        report = scanner.run()
        assert isinstance(report, ScanReport)
        assert report.mode == "quick"
        assert report.total_payloads > 0
        assert report.total_variants > 0
        assert report.duration_seconds >= 0

    def test_quick_scan_block_rate_bounded(self):
        scanner = RedTeamScanner(mode=ScanMode.QUICK, target=ScanTarget.INPUT)
        report = scanner.run()
        assert 0.0 <= report.block_rate_pct <= 100.0

    def test_quick_scan_results_match_report_count(self):
        scanner = RedTeamScanner(mode=ScanMode.QUICK, target=ScanTarget.INPUT)
        report = scanner.run()
        assert len(scanner.results) == report.total_variants


class TestFullScan:
    @pytest.mark.slow
    def test_full_scan_returns_report(self):
        scanner = RedTeamScanner(mode=ScanMode.FULL, target=ScanTarget.INPUT)
        report = scanner.run()
        assert isinstance(report, ScanReport)
        assert report.mode == "full"
        assert report.total_payloads > 0
        assert report.total_variants > 0

    @pytest.mark.slow
    def test_full_scan_by_category_not_empty(self):
        scanner = RedTeamScanner(mode=ScanMode.FULL, target=ScanTarget.INPUT)
        report = scanner.run()
        assert len(report.by_category) > 0
        for cat, stats in report.by_category.items():
            assert "blocked" in stats
            assert "allowed" in stats
            assert "total" in stats
            assert stats["blocked"] + stats["allowed"] <= stats["total"]


class TestScanTargets:
    def test_input_only_target(self):
        scanner = RedTeamScanner(mode=ScanMode.QUICK, target=ScanTarget.INPUT)
        report = scanner.run()
        assert report.target == "input"
        assert report.total_variants > 0

    def test_output_only_target(self):
        scanner = RedTeamScanner(mode=ScanMode.QUICK, target=ScanTarget.OUTPUT)
        report = scanner.run()
        assert report.target == "output"
        assert report.total_variants > 0

    def test_both_target_has_more_variants(self):
        scanner_input = RedTeamScanner(mode=ScanMode.QUICK, target=ScanTarget.INPUT)
        report_input = scanner_input.run()

        scanner_both = RedTeamScanner(mode=ScanMode.QUICK, target=ScanTarget.BOTH)
        report_both = scanner_both.run()

        assert report_both.total_variants > report_input.total_variants


class TestReportStructure:
    def test_report_has_required_fields(self):
        scanner = RedTeamScanner(mode=ScanMode.QUICK, target=ScanTarget.INPUT)
        report = scanner.run()
        assert report.scan_id.startswith("rt_")
        assert report.mode in ("quick", "full", "adversarial")
        assert report.started_at != ""
        assert report.completed_at != ""
        assert report.duration_seconds >= 0
        assert report.avg_latency_ms >= 0

    def test_report_blocked_allowed_errors_sum(self):
        scanner = RedTeamScanner(mode=ScanMode.QUICK, target=ScanTarget.INPUT)
        report = scanner.run()
        assert report.blocked + report.allowed + report.errors == report.total_variants

    def test_report_failures_are_allowed_not_blocked(self):
        scanner = RedTeamScanner(mode=ScanMode.QUICK, target=ScanTarget.BOTH)
        report = scanner.run()
        for failure in report.failures:
            assert failure.blocked is False
            assert failure.decision != "error"


class TestPayloadResult:
    def test_payload_result_has_fields(self):
        pr = PayloadResult(
            payload_id="RT-TEST-001",
            name="Test Payload",
            category="LLM01",
            severity="critical",
            variant="test variant text",
            decision="deny",
            blocked=True,
            reason="blocked by layer",
            latency_ms=1.5,
        )
        assert pr.payload_id == "RT-TEST-001"
        assert pr.severity == "critical"
        assert pr.blocked is True
        assert pr.timestamp != ""

    def test_payload_result_default_reason_empty(self):
        pr = PayloadResult(
            payload_id="RT-TEST-002",
            name="Test 2",
            category="LLM02",
            severity="high",
            variant="text",
            decision="allow",
            blocked=False,
            latency_ms=0.5,
        )
        assert pr.reason == ""


class TestSeverityAndCategory:
    def test_by_severity_not_empty(self):
        scanner = RedTeamScanner(mode=ScanMode.QUICK, target=ScanTarget.INPUT)
        report = scanner.run()
        assert len(report.by_severity) > 0

    def test_high_severity_checked(self):
        scanner = RedTeamScanner(mode=ScanMode.QUICK, target=ScanTarget.INPUT)
        report = scanner.run()
        sev = report.by_severity
        high_keys = {"critical", "high"}
        found = any(k in sev for k in high_keys)
        assert found, f"Expected critical/high in by_severity keys: {list(sev.keys())}"
