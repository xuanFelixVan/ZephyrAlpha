# [A_test] module_id: SRC-TST-1763 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_trend_analyzer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_trend_analyzer.py -q
# [TTL] task_bound

from __future__ import annotations

import os
import sqlite3
from datetime import UTC, datetime, timedelta

from zephyr.gov_drift.trend_analyzer import (
    TrendAlert,
    TrendAnalyzer,
    TrendMetrics,
)


def _seed_db(db_path: str, rows: list[dict]) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS drift_events ("
        "event_id TEXT, module_id TEXT, detector_id TEXT, drift_dimension TEXT, "
        "baseline_version TEXT, state TEXT, created_at TEXT, updated_at TEXT, "
        "resolved_by TEXT, resolution_detail TEXT, auto_fixed INTEGER, rollback_verified INTEGER)"
    )
    for r in rows:
        conn.execute(
            "INSERT INTO drift_events (event_id, module_id, detector_id, drift_dimension, "
            "baseline_version, state, created_at, updated_at, resolved_by, resolution_detail, "
            "auto_fixed, rollback_verified) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                r.get("event_id", "e1"),
                r.get("module_id", "MOD-X"),
                r.get("detector_id", "det-1"),
                r.get("drift_dimension", "code"),
                r.get("baseline_version", "v1"),
                r.get("state", "OPEN"),
                r.get("created_at"),
                r.get("updated_at"),
                r.get("resolved_by", ""),
                r.get("resolution_detail", ""),
                r.get("auto_fixed", 0),
                r.get("rollback_verified", 0),
            ),
        )
    conn.commit()
    conn.close()


class TestTrendMetrics:
    def test_instantiation_with_defaults(self):
        m = TrendMetrics(module_id="MOD-001")
        assert m.module_id == "MOD-001"
        assert m.drift_velocity == 0.0
        assert m.resolution_rate == 0.0
        assert m.mean_time_to_resolve_hours == 0.0
        assert m.detector_fp_ratio == {}
        assert m.computed_at == ""

    def test_instantiation_with_all_fields(self):
        m = TrendMetrics(
            module_id="MOD-002",
            drift_velocity=3.5,
            resolution_rate=0.8,
            mean_time_to_resolve_hours=12.0,
            detector_fp_ratio={"det-a": 0.1},
            computed_at="2026-01-01T00:00:00+00:00",
        )
        assert m.drift_velocity == 3.5
        assert m.resolution_rate == 0.8
        assert m.mean_time_to_resolve_hours == 12.0
        assert m.detector_fp_ratio["det-a"] == 0.1


class TestTrendAlert:
    def test_instantiation(self):
        a = TrendAlert(module_id="MOD-003", alert_type="spike", severity="WARNING", detail="v=6")
        assert a.module_id == "MOD-003"
        assert a.alert_type == "spike"
        assert a.severity == "WARNING"
        assert a.detail == "v=6"


class TestTrendAnalyzer:
    def test_instantiation_with_project_root(self, tmp_path):
        analyzer = TrendAnalyzer(project_root=str(tmp_path))
        assert analyzer._project_root == str(tmp_path)
        assert os.path.isdir(analyzer._db_dir)

    def test_instantiation_default_root(self):
        analyzer = TrendAnalyzer()
        assert os.path.isdir(analyzer._db_dir)
        assert os.path.isdir(analyzer._archive_dir)

    def test_compute_metrics_empty_db(self, tmp_path):
        analyzer = TrendAnalyzer(project_root=str(tmp_path))
        conn = sqlite3.connect(analyzer._db_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS drift_events ("
            "event_id TEXT, module_id TEXT, detector_id TEXT, drift_dimension TEXT, "
            "baseline_version TEXT, state TEXT, created_at TEXT, updated_at TEXT, "
            "resolved_by TEXT, resolution_detail TEXT, auto_fixed INTEGER, rollback_verified INTEGER)"
        )
        conn.commit()
        conn.close()
        metrics = analyzer.compute_metrics("MOD-EMPTY")
        assert metrics.module_id == "MOD-EMPTY"
        assert metrics.drift_velocity == 0.0
        assert metrics.resolution_rate == 1.0
        assert metrics.mean_time_to_resolve_hours == 0.0

    def test_compute_metrics_with_data(self, tmp_path):
        analyzer = TrendAnalyzer(project_root=str(tmp_path))
        now = datetime.now(UTC)
        week_ago = (now - timedelta(days=3)).isoformat()
        month_ago = (now - timedelta(days=10)).isoformat()
        _seed_db(
            analyzer._db_path,
            [
                {
                    "event_id": "e1",
                    "module_id": "MOD-A",
                    "state": "OPEN",
                    "created_at": week_ago,
                    "updated_at": week_ago,
                    "detector_id": "det-1",
                },
                {
                    "event_id": "e2",
                    "module_id": "MOD-A",
                    "state": "VERIFIED",
                    "created_at": month_ago,
                    "updated_at": now.isoformat(),
                    "detector_id": "det-1",
                },
                {
                    "event_id": "e3",
                    "module_id": "MOD-A",
                    "state": "FALSE_POSITIVE",
                    "created_at": month_ago,
                    "updated_at": now.isoformat(),
                    "detector_id": "det-2",
                },
            ],
        )
        metrics = analyzer.compute_metrics("MOD-A")
        assert metrics.drift_velocity == 1.0
        assert 0.0 < metrics.resolution_rate <= 1.0
        assert metrics.mean_time_to_resolve_hours > 0.0
        assert "det-1" in metrics.detector_fp_ratio or "det-2" in metrics.detector_fp_ratio

    def test_check_trend_alerts_spike(self, tmp_path):
        analyzer = TrendAnalyzer(project_root=str(tmp_path))
        now = datetime.now(UTC)
        rows = []
        for i in range(7):
            ts = (now - timedelta(days=i)).isoformat()
            rows.append(
                {
                    "event_id": f"spike-{i}",
                    "module_id": "MOD-SPIKE",
                    "state": "OPEN",
                    "created_at": ts,
                    "updated_at": ts,
                    "detector_id": "det-1",
                }
            )
        _seed_db(analyzer._db_path, rows)
        alerts = analyzer.check_trend_alerts("MOD-SPIKE")
        spike_alerts = [a for a in alerts if a.alert_type == "spike"]
        assert len(spike_alerts) >= 1
        assert spike_alerts[0].severity == "WARNING"

    def test_check_trend_alerts_no_alerts_when_healthy(self, tmp_path):
        analyzer = TrendAnalyzer(project_root=str(tmp_path))
        now = datetime.now(UTC)
        _seed_db(
            analyzer._db_path,
            [
                {
                    "event_id": "h1",
                    "module_id": "MOD-HEALTHY",
                    "state": "VERIFIED",
                    "created_at": (now - timedelta(days=10)).isoformat(),
                    "updated_at": (now - timedelta(days=9)).isoformat(),
                    "detector_id": "det-1",
                },
            ],
        )
        alerts = analyzer.check_trend_alerts("MOD-HEALTHY")
        spike_alerts = [a for a in alerts if a.alert_type == "spike"]
        assert len(spike_alerts) == 0

    def test_archive_old_data_moves_records(self, tmp_path):
        analyzer = TrendAnalyzer(project_root=str(tmp_path))
        now = datetime.now(UTC)
        old_ts = (now - timedelta(days=120)).isoformat()
        recent_ts = (now - timedelta(days=10)).isoformat()
        _seed_db(
            analyzer._db_path,
            [
                {
                    "event_id": "old-1",
                    "module_id": "MOD-OLD",
                    "state": "OPEN",
                    "created_at": old_ts,
                    "updated_at": old_ts,
                    "detector_id": "det-1",
                },
                {
                    "event_id": "recent-1",
                    "module_id": "MOD-NEW",
                    "state": "OPEN",
                    "created_at": recent_ts,
                    "updated_at": recent_ts,
                    "detector_id": "det-1",
                },
            ],
        )
        analyzer.archive_old_data()
        conn = sqlite3.connect(analyzer._db_path)
        remaining = conn.execute("SELECT COUNT(*) FROM drift_events").fetchone()[0]
        conn.close()
        assert remaining == 1
        year = now.strftime("%Y")
        archive_path = os.path.join(analyzer._archive_dir, f"drift_{year}.jsonl")
        assert os.path.isfile(archive_path)

    def test_archive_old_data_no_old_records(self, tmp_path):
        analyzer = TrendAnalyzer(project_root=str(tmp_path))
        now = datetime.now(UTC)
        recent_ts = (now - timedelta(days=5)).isoformat()
        _seed_db(
            analyzer._db_path,
            [
                {
                    "event_id": "r1",
                    "module_id": "MOD-R",
                    "state": "OPEN",
                    "created_at": recent_ts,
                    "updated_at": recent_ts,
                    "detector_id": "det-1",
                },
            ],
        )
        analyzer.archive_old_data()
        conn = sqlite3.connect(analyzer._db_path)
        remaining = conn.execute("SELECT COUNT(*) FROM drift_events").fetchone()[0]
        conn.close()
        assert remaining == 1

    def test_fp_ratio_alert(self, tmp_path):
        analyzer = TrendAnalyzer(project_root=str(tmp_path))
        now = datetime.now(UTC)
        rows = []
        for i in range(5):
            ts = (now - timedelta(days=i)).isoformat()
            rows.append(
                {
                    "event_id": f"fp-{i}",
                    "module_id": "MOD-FP",
                    "state": "FALSE_POSITIVE",
                    "created_at": ts,
                    "updated_at": ts,
                    "detector_id": "det-bad",
                }
            )
        _seed_db(analyzer._db_path, rows)
        alerts = analyzer.check_trend_alerts("MOD-FP")
        fp_alerts = [a for a in alerts if a.alert_type == "fp_ratio"]
        assert len(fp_alerts) >= 1
        assert fp_alerts[0].severity == "MEDIUM"
