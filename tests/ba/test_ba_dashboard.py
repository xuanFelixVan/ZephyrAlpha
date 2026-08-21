# [A_test] module_id: MOD-GOV_ba_dashboard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_ba_dashboard
# [INVARIANTS] 仪表板数据只读
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_ba_dashboard.py
# [TTL] task_bound

from __future__ import annotations

import json
import os
import sqlite3

from zephyr.gov_drift.dashboard import Dashboard, DashboardData


def _seed_gov_db(tmp_path, rows: list[tuple]) -> None:
    """tmp governance.db 布局造数（#62 裁定口径：DB_PATH 相对 MAIN_REPO_ROOT 重定位）。"""
    from zephyr.shared.io.paths import DB_PATH, MAIN_REPO_ROOT

    db_path = os.path.join(str(tmp_path), *DB_PATH.relative_to(MAIN_REPO_ROOT).parts)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE drift_events (module_id TEXT, state TEXT, created_at TEXT)")
    for row in rows:
        conn.execute("INSERT INTO drift_events VALUES (?, ?, ?)", row)
    conn.commit()
    conn.close()


class TestDashboardData:
    def test_default_fields(self):
        dd = DashboardData()
        assert dd.coverage_matrix == {}
        assert dd.module_health_index == {}
        assert dd.drift_heatmap == []
        assert dd.generated_at == ""
        # #62 裁定（2026-08-21）：data_as_of 字段默认 None（表空/库不存在）
        assert dd.data_as_of is None

    def test_custom_fields(self):
        dd = DashboardData(
            coverage_matrix={"det1": {"a": 1}},
            module_health_index={"MOD-A": 0.85},
            drift_heatmap=[{"date": "2025-01-01", "module_id": "M1", "count": 3}],
            generated_at="2025-01-01T00:00:00Z",
        )
        assert "det1" in dd.coverage_matrix
        assert dd.module_health_index["MOD-A"] == 0.85
        assert len(dd.drift_heatmap) == 1


class TestDashboard:
    def test_instantiation_with_project_root(self, tmp_path):
        db = Dashboard(project_root=str(tmp_path))
        assert db.project_root == str(tmp_path)

    def test_instantiation_default_root(self):
        db = Dashboard()
        assert db.project_root != ""

    def test_compute_module_health_no_db(self, tmp_path):
        db = Dashboard(project_root=str(tmp_path))
        health = db.compute_module_health()
        assert health == {}

    def test_compute_module_health_with_data(self, tmp_path):
        # #62 裁定（2026-08-20）：tmp governance.db 布局（治自出生即红——原建
        # data/drift_audit/drift_events.db 与 Dashboard 真读 governance.db 不符）。
        # 路径推导与 dashboard.py:96-98 同口径（DB_PATH 相对 MAIN_REPO_ROOT 重定位）。
        from zephyr.shared.io.paths import DB_PATH, MAIN_REPO_ROOT

        db_path = os.path.join(str(tmp_path), *DB_PATH.relative_to(MAIN_REPO_ROOT).parts)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE drift_events (module_id TEXT, state TEXT, created_at TEXT)")
        conn.execute("INSERT INTO drift_events VALUES ('MOD-A', 'VERIFIED', '2025-01-01')")
        conn.execute("INSERT INTO drift_events VALUES ('MOD-A', 'OPEN', '2025-01-02')")
        conn.execute("INSERT INTO drift_events VALUES ('MOD-B', 'VERIFIED', '2025-01-01')")
        conn.commit()
        conn.close()
        db = Dashboard(project_root=str(tmp_path))
        health = db.compute_module_health()
        assert "MOD-A" in health
        assert "MOD-B" in health
        assert 0.0 <= health["MOD-A"] <= 1.0
        assert 0.0 <= health["MOD-B"] <= 1.0

    def test_compute_drift_heatmap_no_db(self, tmp_path):
        db = Dashboard(project_root=str(tmp_path))
        heatmap = db.compute_drift_heatmap()
        assert heatmap == []

    def test_compute_drift_heatmap_with_data(self, tmp_path):
        # #62 裁定（2026-08-20）：同上——tmp governance.db 布局。
        from zephyr.shared.io.paths import DB_PATH, MAIN_REPO_ROOT

        db_path = os.path.join(str(tmp_path), *DB_PATH.relative_to(MAIN_REPO_ROOT).parts)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE drift_events (module_id TEXT, state TEXT, created_at TEXT)")
        conn.execute("INSERT INTO drift_events VALUES ('MOD-A', 'OPEN', '2025-01-01')")
        conn.execute("INSERT INTO drift_events VALUES ('MOD-A', 'OPEN', '2025-01-01')")
        conn.execute("INSERT INTO drift_events VALUES ('MOD-B', 'OPEN', '2025-01-02')")
        conn.commit()
        conn.close()
        db = Dashboard(project_root=str(tmp_path))
        heatmap = db.compute_drift_heatmap()
        assert len(heatmap) >= 1
        assert "date" in heatmap[0]
        assert "module_id" in heatmap[0]
        assert "count" in heatmap[0]

    def test_generate_returns_dashboard_data(self, tmp_path):
        db = Dashboard(project_root=str(tmp_path))
        data = db.generate()
        assert isinstance(data, DashboardData)
        assert data.generated_at != ""

    def test_to_json_summary(self, tmp_path):
        db = Dashboard(project_root=str(tmp_path))
        result = db.to_json_summary()
        parsed = json.loads(result)
        assert "coverage_dimensions" in parsed
        assert "modules" in parsed
        assert "generated_at" in parsed

    def test_to_cli_table(self, tmp_path):
        db = Dashboard(project_root=str(tmp_path))
        table = db.to_cli_table()
        assert "Module Health Index" in table

    def test_load_coverage_matrix_no_registry(self, tmp_path):
        db = Dashboard(project_root=str(tmp_path))
        matrix = db.load_coverage_matrix()
        assert isinstance(matrix, dict)


class TestDataAsOfIntegration:
    """#62 裁定（2026-08-21）：data_as_of 展示层接入——死数据警示防过期"健康度良好"假象。"""

    def test_generate_includes_data_as_of(self, tmp_path):
        _seed_gov_db(tmp_path, [("MOD-A", "VERIFIED", "2025-01-01"), ("MOD-A", "OPEN", "2025-01-02")])
        db = Dashboard(project_root=str(tmp_path))
        data = db.generate()
        assert data.data_as_of == "2025-01-02"  # MAX(created_at)

    def test_to_json_summary_includes_data_as_of(self, tmp_path):
        _seed_gov_db(tmp_path, [("MOD-A", "OPEN", "2025-01-01")])
        db = Dashboard(project_root=str(tmp_path))
        parsed = json.loads(db.to_json_summary())
        assert parsed["data_as_of"] == "2025-01-01"

    def test_cli_table_stale_banner_for_old_data(self, tmp_path):
        # 2025-01-01 距今远超 STALE_DAYS=7 → 过期警示
        _seed_gov_db(tmp_path, [("MOD-A", "OPEN", "2025-01-01")])
        db = Dashboard(project_root=str(tmp_path))
        table = db.to_cli_table()
        assert "STALE" in table
        assert "2025-01-01" in table
        assert "Module Health Index" in table

    def test_cli_table_no_data_banner_when_no_db(self, tmp_path):
        db = Dashboard(project_root=str(tmp_path))
        table = db.to_cli_table()
        assert "NO DATA" in table

    def test_cli_table_fresh_data_no_stale(self, tmp_path):
        from datetime import UTC, datetime

        today = datetime.now(UTC).isoformat()
        _seed_gov_db(tmp_path, [("MOD-A", "OPEN", today)])
        db = Dashboard(project_root=str(tmp_path))
        table = db.to_cli_table()
        assert "Data as of" in table
        assert "STALE" not in table
