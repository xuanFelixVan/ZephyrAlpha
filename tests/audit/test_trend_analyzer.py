# [A_test] module_id: MOD-GOV_trend_analyzer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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

import json
import os
import sqlite3
from datetime import UTC, datetime, timedelta

from zephyr.gov_drift.trend_analyzer import (
    TrendAlert,
    TrendAnalyzer,
    TrendMetrics,
)

# #62 子裁定（2026-08-21）：夹具复刻生产 governance.db drift_events 22 列 schema
# （与 drift_engine CREATE DDL 逐字一致；#62 §七.3——测试夹具复刻生产 schema 硬约束方向）
_PRODUCTION_DDL = (
    "CREATE TABLE IF NOT EXISTS drift_events ("
    "event_id INTEGER PRIMARY KEY AUTOINCREMENT, "
    "drift_type TEXT NOT NULL, "
    "target TEXT, "
    "expected_value TEXT, "
    "actual_value TEXT, "
    "severity TEXT, "
    "detected_at TEXT NOT NULL, "
    "resolved_at TEXT, "
    "resolution TEXT, "
    "detector_id TEXT DEFAULT '', "
    "module_id TEXT DEFAULT 'MOD-INF-023', "
    "state TEXT DEFAULT 'DETECTED', "
    "source_file TEXT, "
    "description TEXT, "
    "details TEXT, "
    "fix_description TEXT, "
    "scan_level TEXT DEFAULT 'STANDARD', "
    "auto_fixable INTEGER DEFAULT 0, "
    "resolution_detail TEXT, "
    "roi_score REAL DEFAULT 0.0, "
    "created_at TEXT, "
    "updated_at TEXT)"
)


def _make_analyzer(tmp_path) -> TrendAnalyzer:
    """测试隔离：db_path setter 显式注入临时库（生产默认=SSoT governance.db，#62 子裁定）。"""
    analyzer = TrendAnalyzer(project_root=str(tmp_path))
    analyzer.db_path = str(tmp_path / "test_drift.db")
    return analyzer


def _seed_db(db_path: str, rows: list[dict]) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(_PRODUCTION_DDL)
    for r in rows:
        created = r.get("created_at") or datetime.now(UTC).isoformat()
        detector = r.get("detector_id", "det-1")
        conn.execute(
            "INSERT INTO drift_events (drift_type, detector_id, module_id, severity, state, "
            "description, detected_at, auto_fixable, resolution_detail, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                detector,  # drift_type/detector_id 同填（#62 legacy 双列同值口径）
                detector,
                r.get("module_id", "MOD-X"),
                "MEDIUM",
                r.get("state", "DETECTED"),
                r.get("drift_dimension", "code"),  # description 列承载 drift_dimension
                created,  # detected_at=created_at（#62 writer 口径）
                r.get("auto_fixed", 0),  # auto_fixed→auto_fixable
                r.get("resolution_detail", ""),
                created,
                r.get("updated_at"),
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
        assert analyzer.project_root == str(tmp_path)
        assert os.path.isdir(analyzer.db_dir)

    def test_instantiation_default_root(self):
        analyzer = TrendAnalyzer()
        assert os.path.isdir(analyzer.db_dir)
        assert os.path.isdir(analyzer.archive_dir)

    def test_db_path_default_is_ssot(self):
        # #62 子裁定：生产默认指向 DB_PATH SSoT（governance.db），第四物理位置消除
        from zephyr.shared.io.paths import DB_PATH

        analyzer = TrendAnalyzer()
        assert analyzer.db_path == str(DB_PATH)

    def test_compute_metrics_empty_db(self, tmp_path):
        analyzer = _make_analyzer(tmp_path)
        conn = sqlite3.connect(analyzer.db_path)
        conn.execute(_PRODUCTION_DDL)
        conn.commit()
        conn.close()
        metrics = analyzer.compute_metrics("MOD-EMPTY")
        assert metrics.module_id == "MOD-EMPTY"
        assert metrics.drift_velocity == 0.0
        assert metrics.resolution_rate == 1.0
        assert metrics.mean_time_to_resolve_hours == 0.0

    def test_compute_metrics_with_data(self, tmp_path):
        analyzer = _make_analyzer(tmp_path)
        now = datetime.now(UTC)
        week_ago = (now - timedelta(days=3)).isoformat()
        month_ago = (now - timedelta(days=10)).isoformat()
        _seed_db(
            analyzer.db_path,
            [
                {
                    "module_id": "MOD-A",
                    "state": "DETECTED",
                    "created_at": week_ago,
                    "updated_at": week_ago,
                    "detector_id": "det-1",
                },
                {
                    "module_id": "MOD-A",
                    "state": "VERIFIED",
                    "created_at": month_ago,
                    "updated_at": now.isoformat(),
                    "detector_id": "det-1",
                },
                {
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
        analyzer = _make_analyzer(tmp_path)
        now = datetime.now(UTC)
        rows = []
        for i in range(7):
            ts = (now - timedelta(days=i)).isoformat()
            rows.append(
                {
                    "module_id": "MOD-SPIKE",
                    "state": "DETECTED",
                    "created_at": ts,
                    "updated_at": ts,
                    "detector_id": "det-1",
                }
            )
        _seed_db(analyzer.db_path, rows)
        alerts = analyzer.check_trend_alerts("MOD-SPIKE")
        spike_alerts = [a for a in alerts if a.alert_type == "spike"]
        assert len(spike_alerts) >= 1
        assert spike_alerts[0].severity == "WARNING"

    def test_check_trend_alerts_no_alerts_when_healthy(self, tmp_path):
        analyzer = _make_analyzer(tmp_path)
        now = datetime.now(UTC)
        _seed_db(
            analyzer.db_path,
            [
                {
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

    def test_archive_old_data_exports_records_keeps_ssot_rows(self, tmp_path):
        # #62 子裁定：export-only——导出 jsonl 但 SSoT 行保留（读方不得 DELETE）
        analyzer = _make_analyzer(tmp_path)
        now = datetime.now(UTC)
        old_ts = (now - timedelta(days=120)).isoformat()
        recent_ts = (now - timedelta(days=10)).isoformat()
        _seed_db(
            analyzer.db_path,
            [
                {
                    "module_id": "MOD-OLD",
                    "state": "DETECTED",
                    "created_at": old_ts,
                    "updated_at": old_ts,
                    "detector_id": "det-1",
                    "drift_dimension": "code",
                    "auto_fixed": 1,
                },
                {
                    "module_id": "MOD-NEW",
                    "state": "DETECTED",
                    "created_at": recent_ts,
                    "updated_at": recent_ts,
                    "detector_id": "det-1",
                },
            ],
        )
        analyzer.archive_old_data()
        conn = sqlite3.connect(analyzer.db_path)
        remaining = conn.execute("SELECT COUNT(*) FROM drift_events").fetchone()[0]
        conn.close()
        assert remaining == 2  # SSoT 行保留（export-only）
        year = now.strftime("%Y")
        archive_path = os.path.join(analyzer.archive_dir, f"drift_{year}.jsonl")
        assert os.path.isfile(archive_path)
        with open(archive_path, encoding="utf-8") as fh:
            records = [json.loads(line) for line in fh if line.strip()]
        assert len(records) == 1  # 仅 90 天前的 1 行被导出
        assert records[0]["module_id"] == "MOD-OLD"
        # 列重映射实证：drift_dimension←description、auto_fixed←auto_fixable
        assert records[0]["drift_dimension"] == "code"
        assert records[0]["auto_fixed"] == 1

    def test_archive_old_data_no_old_records(self, tmp_path):
        analyzer = _make_analyzer(tmp_path)
        now = datetime.now(UTC)
        recent_ts = (now - timedelta(days=5)).isoformat()
        _seed_db(
            analyzer.db_path,
            [
                {
                    "module_id": "MOD-R",
                    "state": "DETECTED",
                    "created_at": recent_ts,
                    "updated_at": recent_ts,
                    "detector_id": "det-1",
                },
            ],
        )
        analyzer.archive_old_data()
        conn = sqlite3.connect(analyzer.db_path)
        remaining = conn.execute("SELECT COUNT(*) FROM drift_events").fetchone()[0]
        conn.close()
        assert remaining == 1

    def test_fp_ratio_alert(self, tmp_path):
        analyzer = _make_analyzer(tmp_path)
        now = datetime.now(UTC)
        rows = []
        for i in range(5):
            ts = (now - timedelta(days=i)).isoformat()
            rows.append(
                {
                    "module_id": "MOD-FP",
                    "state": "FALSE_POSITIVE",
                    "created_at": ts,
                    "updated_at": ts,
                    "detector_id": "det-bad",
                }
            )
        _seed_db(analyzer.db_path, rows)
        alerts = analyzer.check_trend_alerts("MOD-FP")
        fp_alerts = [a for a in alerts if a.alert_type == "fp_ratio"]
        assert len(fp_alerts) >= 1
        assert fp_alerts[0].severity == "MEDIUM"
