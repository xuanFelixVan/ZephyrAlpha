# [BLUEPRINT] MOD-INF-044 | docs/03_modules/_cross_layer/shared_core/dashboard_blueprint.md
# [MODULE] zephyr.shared.observability.dashboard
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.observability.metrics; zephyr.data.ch_writer(可选运行时查询)
# [CONSUMERS] grafana(provisioning); zephyr.shared.observability.dashboard.dashboard_templates
# [STARTUP] imported
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
"""

Grafana 双数据源仪表盘模块（MOD-INF-044）。

提供：
- datasource_config: 生成 Grafana datasource provisioning YAML（Prometheus + ClickHouse）
- dashboard_templates: 生成 Dashboard JSON 模板（数据采集/CH写入/Drain健康）
- alert_rules: Prometheus 告警规则定义

设计要点：
- 配置文件由代码生成，确保 SSoT（代码=真源，YAML/JSON=产物）
- Dashboard JSON 符合 Grafana 11 provisioning 格式
- 告警规则使用 Prometheus 表达式，与 P1-5 metrics 指标名对齐

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 三个仪表盘子模块生成函数
#   fields: datasource_config(Prometheus/ClickHouse数据源YAML生成) + dashboard_templates(3类Dashboard JSON+导出) + alert_rules(告警规则YAML+ALERT_RULES常量)
#   code: zephyr.shared.observability.dashboard.{datasource_config,dashboard_templates,alert_rules}
# 层: 算法
# - id: A1
#   name_zh: ① 门面包聚合并再导出
#   name_en: dashboard package __init__
#   intro: Grafana双数据源仪表盘的统一门面，把三个子模块的生成函数收拢到一个包入口对外
#   desc: 从datasource_config导入2个数据源YAML生成函数 + dashboard_templates导入3类Dashboard生成与export_dashboard_json + alert_rules导入generate_alert_rules_yaml与ALERT_RULES → __all__共8个符号统一导出; 代码=真源,YAML/JSON=产物
#   inputs: I1
#   outputs: 统一包级API(8个导出符号)
#   invariant: datasource配置生成可幂等输出YAML; Dashboard JSON符合Grafana 11 provisioning格式; 告警规则使用Prometheus表达式
# 层: 输出
# - id: O1
#   name_zh: 仪表盘配置生成API门面
#   name_en: zephyr.shared.observability.dashboard
#   intro: 对外提供数据源YAML/Dashboard JSON/告警规则生成能力，产物供Grafana provisioning消费
#   downstream: grafana(provisioning) ; zephyr.shared.observability.dashboard.dashboard_templates
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.shared.observability.dashboard.alert_rules import (
    ALERT_RULES,
    generate_alert_rules_yaml,
)
from zephyr.shared.observability.dashboard.dashboard_templates import (
    export_dashboard_json,
    generate_ch_write_dashboard,
    generate_data_collection_dashboard,
    generate_drain_health_dashboard,
)
from zephyr.shared.observability.dashboard.datasource_config import (
    generate_clickhouse_datasource_yaml,
    generate_prometheus_datasource_yaml,
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
