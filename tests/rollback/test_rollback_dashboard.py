# [A_test] module_id: MOD-GOV_rollback_dashboard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_rollback_dashboard
# [INVARIANTS] generate() writes file and returns Path; generate_im_format() returns str
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DashboardMetrics defaults are all zero
# [TESTS] tests/test_rollback_dashboard.py
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.infrastructure.rollback.rollback_dashboard import (
    DashboardMetrics,
    RollbackDashboard,
)


class TestDashboardMetrics:
    def test_default_values(self):
        m = DashboardMetrics()
        assert m.total_rollbacks == 0
        assert m.mttr_seconds == 0.0
        assert m.success_rate == 0.0
        assert m.active_kill_switches == 0
        assert m.budget_remaining == 0
        assert m.drill_pass_rate == 0.0

    def test_custom_values(self):
        m = DashboardMetrics(
            total_rollbacks=42,
            mttr_seconds=12.5,
            success_rate=0.95,
            active_kill_switches=1,
            budget_remaining=80,
            drill_pass_rate=0.88,
        )
        assert m.total_rollbacks == 42
        assert m.mttr_seconds == 12.5
        assert m.success_rate == 0.95
        assert m.active_kill_switches == 1
        assert m.budget_remaining == 80
        assert m.drill_pass_rate == 0.88


class TestRollbackDashboardInstantiation:
    def test_default_project_root(self):
        d = RollbackDashboard()
        assert d.project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        assert d.project_root == tmp_path

    def test_none_project_root(self):
        d = RollbackDashboard(project_root=None)
        assert d.project_root == Path.cwd()

    def test_output_path_set(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        assert d.output_path == tmp_path / d.OUTPUT_PATH


class TestRollbackDashboardGenerate:
    def test_returns_path(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics()
        result = d.generate(m)
        assert isinstance(result, Path)

    def test_creates_output_file(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics(total_rollbacks=5)
        output = d.generate(m)
        assert output.exists()

    def test_contains_total_rollbacks(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics(total_rollbacks=42)
        output = d.generate(m)
        content = output.read_text(encoding="utf-8")
        assert "42" in content

    def test_contains_mttr(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics(mttr_seconds=12.5)
        output = d.generate(m)
        content = output.read_text(encoding="utf-8")
        assert "12.5" in content

    def test_contains_success_rate(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics(success_rate=0.95)
        output = d.generate(m)
        content = output.read_text(encoding="utf-8")
        assert "95.0%" in content

    def test_contains_kill_switches(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics(active_kill_switches=2)
        output = d.generate(m)
        content = output.read_text(encoding="utf-8")
        assert "2" in content

    def test_contains_budget_remaining(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics(budget_remaining=80)
        output = d.generate(m)
        content = output.read_text(encoding="utf-8")
        assert "80" in content

    def test_contains_drill_pass_rate(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics(drill_pass_rate=0.88)
        output = d.generate(m)
        content = output.read_text(encoding="utf-8")
        assert "88.0%" in content

    def test_zero_metrics(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics()
        output = d.generate(m)
        content = output.read_text(encoding="utf-8")
        assert "0" in content
        assert "0.0%" in content

    def test_creates_parent_directory(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics()
        output = d.generate(m)
        assert output.parent.exists()


class TestRollbackDashboardImFormat:
    def test_returns_string(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics()
        result = d.generate_im_format(m)
        assert isinstance(result, str)

    def test_contains_rollback_label(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics()
        result = d.generate_im_format(m)
        assert "Rollback Dashboard" in result

    def test_contains_total(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics(total_rollbacks=7)
        result = d.generate_im_format(m)
        assert "7" in result

    def test_green_emoji_above_90(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics(success_rate=0.95)
        result = d.generate_im_format(m)
        assert "🟢" in result

    def test_yellow_emoji_between_70_and_90(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics(success_rate=0.80)
        result = d.generate_im_format(m)
        assert "🟡" in result

    def test_red_emoji_below_70(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics(success_rate=0.50)
        result = d.generate_im_format(m)
        assert "🔴" in result

    def test_kill_switch_shown_when_active(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics(active_kill_switches=2)
        result = d.generate_im_format(m)
        assert "Kill Switches" in result
        assert "2" in result

    def test_kill_switch_hidden_when_zero(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics(active_kill_switches=0)
        result = d.generate_im_format(m)
        assert "Kill Switches" not in result

    def test_contains_mttr(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics(mttr_seconds=45.2)
        result = d.generate_im_format(m)
        assert "45.2s" in result

    def test_zero_success_rate_is_red(self, tmp_path: Path):
        d = RollbackDashboard(project_root=tmp_path)
        m = DashboardMetrics(success_rate=0.0)
        result = d.generate_im_format(m)
        assert "🔴" in result
