# [A_test] module_id: MOD-GOV_dashboard_asset_inventory | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-227 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_dashboard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 Dashboard module — 蓝图 §5 + §27 附录 H 要求 >85% 覆盖."""

import json
from datetime import UTC, datetime

from zephyr.infrastructure.asset_inventory.dashboard import Dashboard
from zephyr.infrastructure.asset_inventory.models import (
    AssetStatus,
    AssetType,
    ClassifiedAsset,
    DashboardData,
    UnifiedAssetIndex,
)


def _healthy_index(total: int = 10, orphan: float = 0.0, ghost: float = 0.0, drift: float = 0.0) -> UnifiedAssetIndex:
    assets = []
    for i in range(total):
        assets.append(
            ClassifiedAsset(
                relative_path=f"src/module_{i}.py",
                asset_type=AssetType.MODULE,
                status=AssetStatus.ACTIVE,
                size_bytes=100,
                mtime_utc=datetime.now(UTC),
                sha256="a" * 64,
            )
        )
    return UnifiedAssetIndex(
        total_assets=total,
        health_score="A",
        health_score_numeric=95.0,
        orphan_rate_pct=orphan,
        ghost_rate_pct=ghost,
        drift_rate_pct=drift,
        by_type={"module": total},
        by_layer={"cross_layer": total},
        by_status={"active": total},
        assets=assets,
        last_reconciliation_at=datetime.now(UTC),
    )


class TestGenerate:
    def test_generate_healthy(self) -> None:
        index = _healthy_index()
        d = Dashboard()
        result = d.generate(index)
        assert isinstance(result, DashboardData)
        assert result.health_score == "A"
        assert result.total_assets == 10
        assert result.orphan_rate_pct == 0.0
        assert result.alerts == []

    def test_generate_orphan_alert(self) -> None:
        index = _healthy_index(orphan=3.5)
        d = Dashboard()
        result = d.generate(index)
        assert any("孤儿率" in a for a in result.alerts)

    def test_generate_ghost_alert(self) -> None:
        index = _healthy_index(ghost=2.0)
        d = Dashboard()
        result = d.generate(index)
        assert any("幽灵率" in a for a in result.alerts)

    def test_generate_drift_alert(self) -> None:
        index = _healthy_index(drift=8.0)
        d = Dashboard()
        result = d.generate(index)
        assert any("漂移率" in a for a in result.alerts)

    def test_generate_multiple_alerts(self) -> None:
        index = _healthy_index(orphan=3.0, ghost=1.5, drift=7.0)
        d = Dashboard()
        result = d.generate(index)
        assert len(result.alerts) == 3

    def test_generate_below_threshold_no_alert(self) -> None:
        index = _healthy_index(orphan=1.5, ghost=0.5, drift=3.0)
        d = Dashboard()
        result = d.generate(index)
        assert result.alerts == []

    def test_generate_empty_index(self) -> None:
        index = UnifiedAssetIndex(total_assets=0, health_score="A")
        d = Dashboard()
        result = d.generate(index)
        assert result.total_assets == 0
        assert result.alerts == []

    def test_generate_preserves_by_type(self) -> None:
        index = _healthy_index()
        d = Dashboard()
        result = d.generate(index)
        assert result.by_type == {"module": 10}

    def test_generate_dashboard_id(self) -> None:
        index = _healthy_index()
        d = Dashboard()
        result = d.generate(index)
        assert result.dashboard_id.startswith("DASH-")


class TestSave:
    def test_save_creates_file(self, tmp_path) -> None:
        index = _healthy_index()
        d = Dashboard()
        dashboard = d.generate(index)
        out = d.save(dashboard, output_path=tmp_path / "dashboard.json")
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["total_assets"] == 10

    def test_save_atomic_temp_cleanup(self, tmp_path) -> None:
        index = _healthy_index()
        d = Dashboard()
        dashboard = d.generate(index)
        target = tmp_path / "dash.json"
        d.save(dashboard, output_path=target)

        tmp_files = list(tmp_path.glob("*.tmp"))
        assert len(tmp_files) == 0


class TestPrintSummary:
    def test_does_not_crash(self) -> None:
        index = _healthy_index()
        d = Dashboard()
        dashboard = d.generate(index)
        d.print_summary(dashboard)

    def test_does_not_crash_with_alerts(self) -> None:
        index = _healthy_index(orphan=3.0, ghost=2.0)
        d = Dashboard()
        dashboard = d.generate(index)
        d.print_summary(dashboard)
