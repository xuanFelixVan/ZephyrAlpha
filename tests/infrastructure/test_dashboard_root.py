# [A_test] module_id: MOD-GOV_dashboard_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md | §
# [MODULE] tests.test_dashboard
# [INVARIANTS] Dashboard.generate must produce DashboardData from UnifiedAssetIndex; save must use atomic write
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError on invalid input; PermissionError on write failure
# [TESTS] tests/test_dashboard_root.py
# [TTL] task_bound

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from zephyr.infrastructure.asset_inventory.dashboard import (
    Dashboard,
    KnowledgeTransferGate,
    KnowledgeTransferRecord,
    _generate_dashboard_id,
)
from zephyr.infrastructure.asset_inventory.models import (
    DashboardData,
    UnifiedAssetIndex,
)


def _make_index(**overrides) -> UnifiedAssetIndex:
    defaults = dict(
        total_assets=10,
        health_score="A",
        health_score_numeric=95.0,
        orphan_rate_pct=0.5,
        ghost_rate_pct=0.2,
        drift_rate_pct=1.0,
        by_type={"module": 5, "script": 5},
        by_layer={"L01": 10},
        assets=[],
    )
    defaults.update(overrides)
    return UnifiedAssetIndex(**defaults)


class TestDashboardInstantiation:
    def test_default_root(self):
        d = Dashboard()
        assert d.root is not None
        assert isinstance(d.root, Path)

    def test_custom_root(self, tmp_path):
        d = Dashboard(root=tmp_path)
        assert d.root == tmp_path


class TestDashboardGenerate:
    def test_generate_healthy_index(self):
        d = Dashboard()
        index = _make_index()
        result = d.generate(index)
        assert isinstance(result, DashboardData)
        assert result.health_score == "A"
        assert result.total_assets == 10
        assert result.alerts == []

    def test_generate_with_orphan_alert(self):
        d = Dashboard()
        index = _make_index(orphan_rate_pct=5.0)
        result = d.generate(index)
        assert any("孤儿率" in a for a in result.alerts)

    def test_generate_with_ghost_alert(self):
        d = Dashboard()
        index = _make_index(ghost_rate_pct=3.0)
        result = d.generate(index)
        assert any("幽灵率" in a for a in result.alerts)

    def test_generate_with_drift_alert(self):
        d = Dashboard()
        index = _make_index(drift_rate_pct=8.0)
        result = d.generate(index)
        assert any("漂移率" in a for a in result.alerts)

    def test_generate_all_alerts(self):
        d = Dashboard()
        index = _make_index(orphan_rate_pct=5.0, ghost_rate_pct=3.0, drift_rate_pct=8.0)
        result = d.generate(index)
        assert len(result.alerts) == 3

    def test_generate_dashboard_id_format(self):
        dash_id = _generate_dashboard_id()
        assert dash_id.startswith("DASH-")
        assert len(dash_id) > 10

    def test_generate_preserves_by_type_and_by_layer(self):
        d = Dashboard()
        index = _make_index(by_type={"module": 3, "script": 7}, by_layer={"L01": 5, "L02": 5})
        result = d.generate(index)
        assert result.by_type == {"module": 3, "script": 7}
        assert result.by_layer == {"L01": 5, "L02": 5}

    def test_generate_with_last_reconciliation(self):
        d = Dashboard()
        now = datetime.now(UTC)
        index = _make_index(last_reconciliation_at=now)
        result = d.generate(index)
        assert result.last_reconciliation is not None

    def test_generate_without_last_reconciliation(self):
        d = Dashboard()
        index = _make_index(last_reconciliation_at=None)
        result = d.generate(index)
        assert result.last_reconciliation is None


class TestDashboardSave:
    def test_save_creates_file(self, tmp_path):
        d = Dashboard(root=tmp_path)
        index = _make_index()
        dashboard = d.generate(index)
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        out = d.save(dashboard, output_path=out_dir / "dash.json")
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["total_assets"] == 10

    def test_save_content_is_valid_json(self, tmp_path):
        d = Dashboard(root=tmp_path)
        index = _make_index()
        dashboard = d.generate(index)
        out = d.save(dashboard, output_path=tmp_path / "dash.json")
        content = out.read_text(encoding="utf-8")
        parsed = json.loads(content)
        assert "dashboard_id" in parsed
        assert "health_score" in parsed


class TestDashboardPrintSummary:
    def test_print_summary_runs(self, capsys):
        d = Dashboard()
        index = _make_index()
        dashboard = d.generate(index)
        d.print_summary(dashboard)
        captured = capsys.readouterr()
        assert "ZephyrAlpha" in captured.out
        assert "95" in captured.out or "A" in captured.out

    def test_print_summary_with_alerts(self, capsys):
        d = Dashboard()
        index = _make_index(orphan_rate_pct=5.0)
        dashboard = d.generate(index)
        d.print_summary(dashboard)
        captured = capsys.readouterr()
        assert "告警" in captured.out


class TestKnowledgeTransferGate:
    def test_instantiation(self, tmp_path):
        gate = KnowledgeTransferGate(project_root=tmp_path)
        assert gate._root == tmp_path

    def test_generate_summary_no_index(self, tmp_path):
        gate = KnowledgeTransferGate(project_root=tmp_path)
        summary = gate.generate_summary()
        assert "ZephyrAlpha" in summary
        assert "资产状态快照" in summary

    def test_write_handoff_creates_file(self, tmp_path):
        gate = KnowledgeTransferGate(project_root=tmp_path)
        out = gate.write_handoff(output_path=tmp_path / "handoff.txt")
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "ZephyrAlpha" in content


class TestKnowledgeTransferRecord:
    def test_defaults(self):
        rec = KnowledgeTransferRecord(transferred_at=datetime.now(UTC))
        assert rec.health_score == "A"
        assert rec.orphan_rate == 0.0
        assert rec.total_assets == 0
        assert rec.top_orphans == []
