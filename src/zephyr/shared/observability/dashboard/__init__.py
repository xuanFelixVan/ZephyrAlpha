# [BLUEPRINT] MOD-INF-044 | docs/03_modules/_cross_layer/shared_core/dashboard_blueprint.md
# [MODULE] zephyr.shared.observability.dashboard
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.observability.metrics; zephyr.data.ch_writer(可选运行时查询)
# [CONSUMERS] grafana(provisioning); zephyr.shared.observability.dashboard.dashboard_templates
# [STARTUP] lazy
# [MATURITY] production
# [INVARIANTS] datasource配置生成可幂等输出YAML; Dashboard JSON符合Grafana 11 provisioning格式; 告警规则使用Prometheus表达式
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 配置生成失败->返回空字符串+log; Dashboard导出失败->返回空dict
# [TESTS] tests/zephyr/shared/observability/test_dashboard.py
# [A_module] module_id=MOD-INF-044 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Grafana 双数据源仪表盘模块（MOD-INF-044）。

提供：
- datasource_config: 生成 Grafana datasource provisioning YAML（Prometheus + ClickHouse）
- dashboard_templates: 生成 Dashboard JSON 模板（数据采集/CH写入/Drain健康）
- alert_rules: Prometheus 告警规则定义

设计要点：
- 配置文件由代码生成，确保 SSoT（代码=真源，YAML/JSON=产物）
- Dashboard JSON 符合 Grafana 11 provisioning 格式
- 告警规则使用 Prometheus 表达式，与 P1-5 metrics 指标名对齐
"""
from zephyr.shared.observability.dashboard.datasource_config import (
    generate_clickhouse_datasource_yaml,
    generate_prometheus_datasource_yaml,
)
from zephyr.shared.observability.dashboard.dashboard_templates import (
    generate_data_collection_dashboard,
    generate_ch_write_dashboard,
    generate_drain_health_dashboard,
    export_dashboard_json,
)
from zephyr.shared.observability.dashboard.alert_rules import (
    generate_alert_rules_yaml,
    ALERT_RULES,
)

__all__ = [
    "generate_clickhouse_datasource_yaml",
    "generate_prometheus_datasource_yaml",
    "generate_data_collection_dashboard",
    "generate_ch_write_dashboard",
    "generate_drain_health_dashboard",
    "generate_alert_rules_yaml",
    "export_dashboard_json",
    "ALERT_RULES",
]
