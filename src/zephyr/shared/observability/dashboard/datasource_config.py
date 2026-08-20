# [BLUEPRINT] MOD-INF-044 | docs/03_modules/_cross_layer/shared_core/dashboard_blueprint.md
# [A_module] module_id=MOD-INF-044 | layer=module | stability=evolving | safety=L
# [TTL] permanent
"""Grafana 数据源配置生成器。

生成 Grafana provisioning 兼容的 datasource YAML，支持：
- Prometheus（实时 metrics，P1-5 /metrics 端点）
- ClickHouse（历史行情 / 回测结果）

Usage::

    from zephyr.shared.observability.dashboard import generate_clickhouse_datasource_yaml
    yaml_text = generate_clickhouse_datasource_yaml(host="172.24.30.100", port=8123)
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
