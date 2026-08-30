# [BLUEPRINT] MOD-INF-044 | docs/03_modules/_cross_layer/shared_core/dashboard_blueprint.md
# [A_module] module_id=MOD-INF-044 | layer=module | stability=evolving | safety=L
# [TTL] permanent
"""
Grafana 数据源配置生成器。

生成 Grafana provisioning 兼容的 datasource YAML，支持：
- Prometheus（实时 metrics，P1-5 /metrics 端点）
- ClickHouse（历史行情 / 回测结果）

Usage::

    from zephyr.shared.observability.dashboard import generate_clickhouse_datasource_yaml
    yaml_text = generate_clickhouse_datasource_yaml(host="172.24.30.100", port=8123)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: url 参数
#   fields: 参数 url，类型注解 str
#   code: datasource_config.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: is_default 参数
#   fields: 参数 is_default，类型注解 bool
#   code: datasource_config.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: host 参数
#   fields: 参数 host，类型注解 str
#   code: datasource_config.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: port 参数
#   fields: 参数 port，类型注解 int
#   code: datasource_config.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① generate_prometheus_datasource_yaml
#   name_en: generate_prometheus_datasource_yaml
#   intro: 生成 Prometheus datasource YAML。
#   desc: 生成 Prometheus datasource YAML。 Args: url: Prometheus URL（docker-compose 内部网络用 http://prom…；源码 L73-L106
#   inputs: url is_default
#   outputs: str
# - id: A2
#   name_zh: ② generate_clickhouse_datasource_yaml
#   name_en: generate_clickhouse_datasource_yaml
#   intro: 生成 ClickHouse datasource YAML。
#   desc: 生成 ClickHouse datasource YAML。 需要安装 grafana-clickhouse-datasource 插件： docker-compose.yml…；源码 L109-L155
#   inputs: host port database username is_default
#   outputs: str
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def generate_prometheus_datasource_yaml(
    url: str = "http://prometheus:9090",
    is_default: bool = True,
) -> str:
    """生成 Prometheus datasource YAML。

    Args:
        url: Prometheus URL（docker-compose 内部网络用 http://prometheus:9090）
        is_default: 是否设为默认数据源

    Returns:
        Grafana provisioning 兼容的 YAML 文本
    """
    return f"""# Grafana Prometheus Datasource — 由 datasource_config.py 生成（MOD-INF-044）
# P2-10 双数据源仪表盘

apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    uid: prometheus
    url: {url}
    isDefault: {str(is_default).lower()}
    editable: true
    jsonData:
      timeInterval: "15s"
      queryTimeout: "30s"
      httpMethod: "POST"
      exemplarTraceIdDestinations:
        - name: traceID
          datasourceUid: prometheus
"""


def generate_clickhouse_datasource_yaml(
    host: str = "172.24.30.100",
    port: int = 8123,
    database: str = "c1_market",
    username: str = "default",
    is_default: bool = False,
) -> str:
    """生成 ClickHouse datasource YAML。

    需要安装 grafana-clickhouse-datasource 插件：
    docker-compose.yml GF_INSTALL_PLUGINS 追加 grafana-clickhouse-datasource

    Args:
        host: ClickHouse 主机
        port: ClickHouse HTTP 端口
        database: 默认数据库
        username: 用户名
        is_default: 是否设为默认数据源

    Returns:
        Grafana provisioning 兼容的 YAML 文本
    """
    return f"""# Grafana ClickHouse Datasource — 由 datasource_config.py 生成（MOD-INF-044）
# P2-10 双数据源仪表盘
# 注意：需安装 grafana-clickhouse-datasource 插件

apiVersion: 1

datasources:
  - name: ClickHouse
    type: clickhouse
    access: proxy
    uid: clickhouse
    url: http://{host}:{port}
    isDefault: {str(is_default).lower()}
    editable: true
    jsonData:
      defaultDatabase: {database}
      port: {port}
      protocol: http
      timeout: 30
      usePOST: true
      queryTimeout: 60
    secureJsonData:
      username: {username}
      password: ""
"""
