# [BLUEPRINT] MOD-INF-044 | docs/03_modules/_cross_layer/shared_core/dashboard_blueprint.md
# [A_module] module_id=MOD-INF-044 | layer=module | stability=evolving | safety=L
# [TTL] permanent
"""P2-10 Grafana 双数据源仪表盘模块测试。"""
import json

import pytest

from zephyr.shared.observability.dashboard import (
    ALERT_RULES,
    export_dashboard_json,
    generate_alert_rules_yaml,
    generate_ch_write_dashboard,
    generate_clickhouse_datasource_yaml,
    generate_data_collection_dashboard,
    generate_drain_health_dashboard,
    generate_prometheus_datasource_yaml,
)


class TestDatasourceConfig:
    """数据源配置生成器测试。"""

    def test_prometheus_yaml_contains_required_fields(self):
        yaml_text = generate_prometheus_datasource_yaml()
        assert "Prometheus" in yaml_text
        assert "type: prometheus" in yaml_text
        assert "uid: prometheus" in yaml_text

    def test_prometheus_yaml_custom_url(self):
        yaml_text = generate_prometheus_datasource_yaml(url="http://localhost:9090")
        assert "http://localhost:9090" in yaml_text

    def test_clickhouse_yaml_contains_required_fields(self):
        yaml_text = generate_clickhouse_datasource_yaml()
        assert "ClickHouse" in yaml_text
        assert "type: clickhouse" in yaml_text
        assert "uid: clickhouse" in yaml_text
        assert "c1_market" in yaml_text

    def test_clickhouse_yaml_custom_host_port(self):
        yaml_text = generate_clickhouse_datasource_yaml(host="10.0.0.1", port=8124)
        assert "10.0.0.1" in yaml_text
        assert "8124" in yaml_text


class TestDashboardTemplates:
    """Dashboard JSON 模板测试。"""

    def test_data_collection_dashboard_structure(self):
        dash = generate_data_collection_dashboard()
        assert dash["uid"] == "zephyr-data-collection"
        assert len(dash["panels"]) == 6
        assert dash["schemaVersion"] == 39

    def test_data_collection_dashboard_panel_exprs(self):
        dash = generate_data_collection_dashboard()
        exprs = [p["targets"][0]["expr"] for p in dash["panels"]]
        assert any("zephyr_tick_received_total" in e for e in exprs)
        assert any("zephyr_tick_written_total" in e for e in exprs)
        assert any("zephyr_tick_dropped_total" in e for e in exprs)
        assert any("zephyr_tick_queue_size" in e for e in exprs)
        assert any("zephyr_wal_segments_total" in e for e in exprs)
        assert any("zephyr_wal_dir_bytes" in e for e in exprs)

    def test_ch_write_dashboard_structure(self):
        dash = generate_ch_write_dashboard()
        assert dash["uid"] == "zephyr-ch-write"
        assert len(dash["panels"]) == 6

    def test_drain_health_dashboard_structure(self):
        dash = generate_drain_health_dashboard()
        assert dash["uid"] == "zephyr-drain-health"
        assert len(dash["panels"]) == 4

    def test_all_dashboards_use_prometheus_ds(self):
        for dash_fn in [
            generate_data_collection_dashboard,
            generate_ch_write_dashboard,
            generate_drain_health_dashboard,
        ]:
            dash = dash_fn()
            for panel in dash["panels"]:
                assert panel["datasource"]["uid"] == "prometheus"

    def test_export_dashboard_json_valid(self):
        dash = generate_data_collection_dashboard()
        json_str = export_dashboard_json(dash)
        parsed = json.loads(json_str)
        assert parsed["uid"] == dash["uid"]


class TestAlertRules:
    """告警规则测试。"""

    def test_alert_rules_count(self):
        assert len(ALERT_RULES) == 6

    def test_alert_rules_yaml_structure(self):
        yaml_text = generate_alert_rules_yaml()
        assert "groups:" in yaml_text
        assert "zephyr-data-layer" in yaml_text
        for rule in ALERT_RULES:
            assert rule["name"] in yaml_text

    def test_alert_rules_have_required_fields(self):
        for rule in ALERT_RULES:
            assert "name" in rule
            assert "expr" in rule
            assert "for" in rule
            assert "severity" in rule
            assert "summary" in rule

    def test_critical_alert_exists(self):
        critical = [r for r in ALERT_RULES if r["severity"] == "critical"]
        assert len(critical) >= 1
        assert any("WAL" in r["name"] for r in critical)
