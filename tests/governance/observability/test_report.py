# [A_test] module_id: SRC-TST-1447 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_report
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_report.py
# [TTL] task_bound

from __future__ import annotations

import json

from zephyr.gov_code_quality.code_dedup.report import (
    DebtProjection,
    DuplicationIntakeRate,
    EngineSelfMetrics,
    HealthComponents,
    HotspotCategory,
    ReportGenerator,
    ScanMetadata,
)
from zephyr.gov_code_quality.code_dedup.report import (
    ExitCode as ReportExitCode,
)


class TestReportExitCode:
    def test_values(self):
        assert ReportExitCode.CLEAN == 0
        assert ReportExitCode.WARN == 1
        assert ReportExitCode.ERROR == 2
        assert ReportExitCode.FAULT == 3
        assert ReportExitCode.DEGRADED == 4


class TestEngineSelfMetrics:
    def test_default_values(self):
        esm = EngineSelfMetrics()
        assert esm.fpr_7d == 0.0
        assert esm.fix_success_rate == 100.0


class TestDuplicationIntakeRate:
    def test_default_values(self):
        dir_ = DuplicationIntakeRate()
        assert dir_.new_duplicates_this_week == 0
        assert dir_.trend == "flat"


class TestDebtProjection:
    def test_default_values(self):
        dp = DebtProjection()
        assert dp.weeks_to_payoff == 0.0
        assert dp.current_debt_groups == 0


class TestScanMetadata:
    def test_default_values(self):
        sm = ScanMetadata()
        assert sm.scan_mode == "incremental"
        assert sm.trigger == "manual"


class TestHealthComponents:
    def test_default_values(self):
        hc = HealthComponents()
        assert hc.overall == 0
        assert hc.auto_fix_success_rate == 100.0


class TestHotspotCategory:
    def test_default_values(self):
        hc = HotspotCategory()
        assert hc.category == ""
        assert hc.duplicate_count == 0


class TestReportGenerator:
    def test_instantiation(self):
        rg = ReportGenerator()
        assert rg._exit_code == ReportExitCode.CLEAN
        assert rg._degradation_level == "none"

    def test_generate_minimal(self):
        rg = ReportGenerator()
        report = rg.generate()
        assert "scan_metadata" in report
        assert "engine_self_metrics" in report
        assert "duplication_intake_rate" in report
        assert "debt_projection" in report
        assert "health_summary" in report
        assert "hotspot_categories" in report
        assert "summary" in report
        assert "duplicate_groups" in report

    def test_generate_with_duplicate_groups(self):
        rg = ReportGenerator()
        groups = [
            {"confidence": 95, "members": [("a.py", ""), ("b.py", "")]},
            {"confidence": 80, "members": [("c.py", ""), ("d.py", "")]},
            {"confidence": 50, "members": [("e.py", "")]},
        ]
        report = rg.generate(duplicate_groups=groups)
        assert report["summary"]["duplicate_groups_total"] == 3
        assert report["summary"]["high_confidence"] == 1
        assert report["summary"]["medium_confidence"] == 1
        assert report["summary"]["low_confidence"] == 1

    def test_generate_with_engine_metrics(self):
        rg = ReportGenerator()
        metrics = EngineSelfMetrics(fpr_7d=0.05, fix_success_rate=90.0)
        report = rg.generate(engine_metrics=metrics)
        assert report["engine_self_metrics"]["false_positive_rate_7d"] == 0.05
        assert report["engine_self_metrics"]["fix_success_rate"] == 90.0

    def test_generate_with_health(self):
        rg = ReportGenerator()
        health = HealthComponents(overall=85, trend="up", duplication_rate=0.1)
        report = rg.generate(health=health)
        assert report["health_summary"]["overall"] == 85
        assert report["health_summary"]["trend"] == "up"

    def test_generate_with_hotspots(self):
        rg = ReportGenerator()
        hotspots = [
            HotspotCategory(category="shared", duplicate_count=5, trend="up"),
            HotspotCategory(category="core", duplicate_count=3, trend="flat"),
        ]
        report = rg.generate(hotspots=hotspots)
        assert len(report["hotspot_categories"]) == 2

    def test_generate_hotspots_capped_at_5(self):
        rg = ReportGenerator()
        hotspots = [HotspotCategory(category=f"cat_{i}", duplicate_count=i) for i in range(10)]
        report = rg.generate(hotspots=hotspots)
        assert len(report["hotspot_categories"]) <= 5

    def test_to_json(self):
        rg = ReportGenerator()
        report = rg.generate()
        json_str = rg.to_json(report)
        parsed = json.loads(json_str)
        assert "scan_metadata" in parsed

    def test_to_yaml_dict(self):
        rg = ReportGenerator()
        report = rg.generate()
        result = rg.to_yaml_dict(report)
        assert result is report

    def test_set_degradation(self):
        rg = ReportGenerator()
        rg.set_degradation("stage2_failed")
        assert rg._degradation_level == "stage2_failed"
        assert rg._exit_code == ReportExitCode.DEGRADED

    def test_set_exit_code(self):
        rg = ReportGenerator()
        rg.set_exit_code(2)
        assert rg._exit_code == 2

    def test_generate_scan_metadata_fields(self):
        rg = ReportGenerator()
        report = rg.generate(total_functions=100, scanned=80, cached=20, duration_ms=500)
        meta = report["scan_metadata"]
        assert meta["total_functions"] == 100
        assert meta["scanned_functions"] == 80
        assert meta["cached_functions"] == 20
        assert meta["scan_duration_ms"] == 500

    def test_generate_empty_duplicate_groups(self):
        rg = ReportGenerator()
        report = rg.generate(duplicate_groups=[])
        assert report["summary"]["duplicate_groups_total"] == 0
        assert report["summary"]["high_confidence"] == 0

    def test_generate_affected_files_count(self):
        rg = ReportGenerator()
        groups = [
            {"confidence": 95, "members": [("a.py", ""), ("b.py", ""), ("a.py", "")]},
        ]
        report = rg.generate(duplicate_groups=groups)
        assert report["summary"]["affected_files"] == 2
