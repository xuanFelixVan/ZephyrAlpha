# [A_test] module_id: MOD-GOV_sla_monitor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-433 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_sla_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] pytest tests/test_sla_monitor.py
# [TTL] task_bound

from __future__ import annotations

import json
import time
from pathlib import Path

from zephyr.infrastructure.sla.sla_monitor import (
    RPO_TARGET_TASKS,
    RTO_TARGET_S,
    SLABreach,
    SLAMonitor,
    SLAReport,
)
from zephyr.shared.io.paths import REPO_ROOT


class TestSLABreachDataclass:
    def test_default_details(self):
        b = SLABreach(
            metric="RTO",
            target=300,
            actual=500,
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        assert b.details == ""

    def test_custom_details(self):
        b = SLABreach(
            metric="RPO",
            target=1,
            actual=5,
            timestamp_utc="2026-01-01T00:00:00+00:00",
            details="Lost 5 tasks",
        )
        assert b.details == "Lost 5 tasks"


class TestSLAReportDataclass:
    def test_fields(self):
        report = SLAReport(
            report_id="SLA-20260522",
            rto_ms=1500.0,
            rto_ok=True,
            rpo_tasks=0,
            rpo_ok=True,
            breaches=[],
            overall_ok=True,
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        assert report.overall_ok is True
        assert report.rto_ok is True
        assert report.rpo_ok is True


class TestSLAMonitor:
    def test_instantiation_with_tmp_path(self, tmp_path):
        mon = SLAMonitor(data_dir=tmp_path / "sla")
        assert mon.data_dir == tmp_path / "sla"

    def test_instantiation_default(self):
        mon = SLAMonitor()
        assert mon.data_dir == REPO_ROOT / "data" / "sla"

    def test_record_rto_within_target(self, tmp_path):
        mon = SLAMonitor(data_dir=tmp_path)
        breach = mon.record_rto(100.0)
        assert breach is None
        assert 100.0 in mon.rto_samples

    def test_record_rto_exceeds_target(self, tmp_path):
        mon = SLAMonitor(data_dir=tmp_path)
        breach = mon.record_rto(500.0)
        assert breach is not None
        assert breach.metric == "RTO"
        assert breach.actual == 500.0
        assert breach.target == RTO_TARGET_S
        assert tmp_path.joinpath("sla_breaches.jsonl").exists()

    def test_record_rto_zero(self, tmp_path):
        mon = SLAMonitor(data_dir=tmp_path)
        breach = mon.record_rto(0.0)
        assert breach is None

    def test_record_rto_negative(self, tmp_path):
        mon = SLAMonitor(data_dir=tmp_path)
        breach = mon.record_rto(-10.0)
        assert breach is None

    def test_record_rpo_within_target(self, tmp_path):
        mon = SLAMonitor(data_dir=tmp_path)
        breach = mon.record_rpo(0)
        assert breach is None
        assert 0 in mon.rpo_counts

    def test_record_rpo_exceeds_target(self, tmp_path):
        mon = SLAMonitor(data_dir=tmp_path)
        breach = mon.record_rpo(5)
        assert breach is not None
        assert breach.metric == "RPO"
        assert breach.actual == 5
        assert breach.target == RPO_TARGET_TASKS

    def test_record_rpo_at_target_boundary(self, tmp_path):
        mon = SLAMonitor(data_dir=tmp_path)
        breach = mon.record_rpo(1)
        assert breach is None

    def test_record_recovery_success(self, tmp_path):
        mon = SLAMonitor(data_dir=tmp_path)
        start = time.time() - 0.1
        report = mon.record_recovery(start, lost_tasks=0)
        assert report.rto_ok is True
        assert report.rpo_ok is True
        assert report.overall_ok is True
        assert len(report.breaches) == 0

    def test_record_recovery_with_breaches(self, tmp_path):
        mon = SLAMonitor(data_dir=tmp_path)
        start = time.time() - 400
        report = mon.record_recovery(start, lost_tasks=5)
        assert report.rto_ok is False
        assert report.rpo_ok is False
        assert report.overall_ok is False
        assert len(report.breaches) == 2

    def test_record_recovery_saves_report(self, tmp_path):
        mon = SLAMonitor(data_dir=tmp_path)
        start = time.time() - 0.05
        report = mon.record_recovery(start, lost_tasks=0)
        report_file = tmp_path / f"{report.report_id}.json"
        assert report_file.exists()
        data = json.loads(report_file.read_text(encoding="utf-8"))
        assert data["report_id"] == report.report_id
        assert data["overall_ok"] is True

    def test_get_statistics_empty(self, tmp_path):
        mon = SLAMonitor(data_dir=tmp_path)
        stats = mon.get_statistics()
        assert stats["avg_rto_s"] == 0.0
        assert stats["avg_rpo_tasks"] == 0.0
        assert stats["rto_compliance"] == 0.0
        assert stats["rpo_compliance"] == 0.0
        assert stats["total_samples"] == 0

    def test_get_statistics_with_data(self, tmp_path):
        mon = SLAMonitor(data_dir=tmp_path)
        mon.record_rto(100.0)
        mon.record_rto(200.0)
        mon.record_rpo(0)
        mon.record_rpo(1)
        stats = mon.get_statistics()
        assert stats["avg_rto_s"] == 150.0
        assert stats["avg_rpo_tasks"] == 0.5
        assert stats["rto_compliance"] == 1.0
        assert stats["rpo_compliance"] == 1.0
        assert stats["total_samples"] == 2

    def test_breach_log_written(self, tmp_path):
        mon = SLAMonitor(data_dir=tmp_path)
        mon.record_rto(500.0)
        log_path = tmp_path / "sla_breaches.jsonl"
        assert log_path.exists()
        lines = log_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["metric"] == "RTO"
        assert data["actual"] == 500.0
