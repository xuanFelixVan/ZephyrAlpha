# [A_test] module_id: SRC-TST-0359 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_audit_observability_dashboard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_audit.observability_dashboard import (
    SLI,
    DashboardConfig,
    DashboardPanel,
)


class TestDashboardPanel:
    def test_all_panels_exist(self):
        assert DashboardPanel.SYSTEM_HEALTH.value == "system_health"
        assert DashboardPanel.COST.value == "cost"
        assert DashboardPanel.ORDER_FLOW.value == "order_flow"
        assert DashboardPanel.MODEL_DRIFT.value == "model_drift"

    def test_panel_count(self):
        assert len(DashboardPanel) == 4


class TestSLI:
    def test_all_slis_exist(self):
        expected = [
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
        ]
        for name in expected:
            assert hasattr(SLI, name.upper())

    def test_sli_count(self):
        assert len(SLI) == 11


class TestDashboardConfig:
    def test_default_config(self):
        config = DashboardConfig.default()
        assert isinstance(config, DashboardConfig)
        assert config.refresh_interval_seconds == 10
        assert len(config.panels) == 4

    def test_default_panels_have_titles(self):
        config = DashboardConfig.default()
        for panel_name, panel_data in config.panels.items():
            assert "title" in panel_data

    def test_custom_config(self):
        config = DashboardConfig(
            panels={"custom": {"title": "Custom Panel"}},
            refresh_interval_seconds=30,
        )
        assert "custom" in config.panels
        assert config.refresh_interval_seconds == 30

    def test_empty_config(self):
        config = DashboardConfig()
        assert config.panels == {}
        assert config.refresh_interval_seconds == 10

    def test_default_system_health_sli_count(self):
        config = DashboardConfig.default()
        health = config.panels.get("system_health", {})
        assert health.get("sli_count") == 11
