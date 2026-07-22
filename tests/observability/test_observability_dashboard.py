# [A_test] module_id: MOD-GOV_observability_dashboard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-411 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_observability_dashboard
# [INVARIANTS] DashboardPanel has 4 panels; SLI has 11 indicators; default config has all panels
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_observability_dashboard.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.observability_governance.observability_dashboard import (
    SLI,
    DashboardConfig,
    DashboardPanel,
)


class TestDashboardPanel:
    def test_all_panels(self):
        expected = {"system_health", "cost", "order_flow", "model_drift"}
        actual = {p.value for p in DashboardPanel}
        assert actual == expected

    def test_panel_count(self):
        assert len(DashboardPanel) == 4


class TestSLI:
    def test_sli_count(self):
        assert len(SLI) == 11

    def test_expected_slis(self):
        expected = {
            "cpu",
            "memory",
            "disk_io",
            "network_throughput",
            "context_length",
            "token_consumption",
            "decision_accuracy",
            "state_awareness",
            "knowledge_retrieval",
            "feedback_adoption",
            "data_freshness",
        }
        actual = {s.value for s in SLI}
        assert actual == expected


class TestDashboardConfig:
    def test_creation_defaults(self):
        cfg = DashboardConfig()
        assert cfg.panels == {}
        assert cfg.refresh_interval_seconds == 10

    def test_default_factory(self):
        cfg = DashboardConfig.default()
        assert len(cfg.panels) == 4
        assert cfg.refresh_interval_seconds == 10

    def test_default_has_system_health(self):
        cfg = DashboardConfig.default()
        assert "system_health" in cfg.panels

    def test_default_has_cost(self):
        cfg = DashboardConfig.default()
        assert "cost" in cfg.panels

    def test_default_has_order_flow(self):
        cfg = DashboardConfig.default()
        assert "order_flow" in cfg.panels

    def test_default_has_model_drift(self):
        cfg = DashboardConfig.default()
        assert "model_drift" in cfg.panels

    def test_default_system_health_sli_count(self):
        cfg = DashboardConfig.default()
        assert cfg.panels["system_health"]["sli_count"] == 11

    def test_custom_config(self):
        cfg = DashboardConfig(panels={"custom": {"title": "Custom"}}, refresh_interval_seconds=5)
        assert "custom" in cfg.panels
        assert cfg.refresh_interval_seconds == 5


class TestBoundary:
    def test_default_panels_all_have_titles(self):
        cfg = DashboardConfig.default()
        for key, panel in cfg.panels.items():
            assert "title" in panel

    def test_empty_panels(self):
        cfg = DashboardConfig(panels={})
        assert len(cfg.panels) == 0
