---
standard_type: 蓝图标准
applicable_scope: 交易执行
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
owner: 执行层负责人
version: 1.0.0
module_id: EXE_BLUEPRINT
created_date: 2026-03-28
last_updated: 2026-04-02
---
module_id: MONITORING_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-02
owner: 首席文档架构师
standard_type: 专业量化机构蓝图
applicable_scope: 全系统架构设计
compliance_level: 初始标准
parent_document: ../README.md
implementation_status: 设计阶段
implementation_progress: 0%
---
---


# 监控告警系统蓝图（简化版）

> 清风量化系统 v5.0 的监控告警方案
> **索引**: `MON_001`
> **注意**: 本蓝图采用"购买而非自研"策略，使用成熟的Grafana+Prometheus方案


## 1. 设计原则

| 原则 | 说明 |
|------|------|
| 购买而非自研 | 使用成熟开源方案，不自研监控面板 |
| 监控即代码 | 监控配置纳入版本控制 |
| 告警即触发 | 告警规则明确，触发动作自动化 |


## 2. 监控方案选型

### 2.1 方案对比

| 方案 | 自研监控 | Grafana+Prometheus(推荐) |
|------|----------|-------------------------|
| 开发时间 | 2-3个月 | 1-2天 |
| 功能完整度 | 60% | 95% |
| 维护成本 | 高 | 极低 |
| 可扩展性 | 受限 | 强 |
| 社区支持 | 无 | 强大 |

### 2.2 最终选择

**采用 Grafana + Prometheus + AlertManager 方案**

```
┌─────────────────────────────────────────────────────────────┐
│                      Grafana 仪表板                         │
│   (策略绩效 / 风控指标 / 系统状态 / 告警历史)                │
└─────────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────────┐
│                    AlertManager 告警管理                      │
│   (告警路由 / 抑制 / 分组 / 升级)                           │
└─────────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────────┐
│                      Prometheus 监控                        │
│   (指标采集 / 存储 / 查询)                                  │
└─────────────────────────────────────────────────────────────┘
                            ↑
┌─────────────────────────────────────────────────────────────┐
│                   Exporters (被监控目标)                    │
│   - TradeExecutor / RiskMonitor / DataHub                  │
│   - Node Exporter (系统指标)                                │
│   - Custom Exporters (业务指标)                             │
└─────────────────────────────────────────────────────────────┘
```


## 3. 监控指标定义

### 3.1 业务指标

```yaml
# prometheus/metrics/business.yaml

metrics:
  # 策略指标
  - name: strategy_signal_count
    type: counter
    description: 策略信号数量
    labels: [strategy_id, signal_type]

  - name: strategy_signal_latency
    type: histogram
    description: 信号生成延迟
    labels: [strategy_id]
    buckets: [0.01, 0.05, 0.1, 0.5, 1.0]

  # 交易指标
  - name: order_submit_count
    type: counter
    description: 订单提交数量
    labels: [symbol, action, status]

  - name: order_execution_latency
    type: histogram
    description: 订单执行延迟
    labels: [order_type]
    buckets: [0.01, 0.05, 0.1, 0.5, 1.0]

  # 风控指标
  - name: risk_violation_count
    type: counter
    description: 风控违规次数
    labels: [rule_id, severity]

  - name: risk_position_value
    type: gauge
    description: 持仓风险值
    labels: [symbol]

  # 因子指标
  - name: factor_ic_value
    type: gauge
    description: 因子IC值
    labels: [factor_id]

  - name: factor_calculation_latency
    type: histogram
    description: 因子计算延迟
    labels: [factor_id]
```

### 3.2 系统指标

```yaml
# prometheus/metrics/system.yaml

metrics:
  - name: cpu_usage_percent
    type: gauge
    description: CPU使用率

  - name: memory_usage_bytes
    type: gauge
    description: 内存使用量

  - name: disk_usage_bytes
    type: gauge
    description: 磁盘使用量

  - name: network_io_bytes
    type: counter
    description: 网络IO

  - name: python_gc_count
    type: counter
    description: Python GC次数
    labels: [generation]
```


## 4. Grafana仪表板设计

### 4.1 仪表板列表

| 仪表板 | 用途 | 刷新频率 |
|--------|------|----------|
| 系统概览 | 全局状态一目了然 | 10s |
| 策略绩效 | 各策略表现 | 1min |
| 风控监控 | 风险指标实时 | 5s |
| 因子状态 | 因子IC监控 | 1min |
| 交易明细 | 订单执行情况 | 10s |
| 系统资源 | 服务器状态 | 30s |

### 4.2 系统概览仪表板

```json
{
  "title": "清风量化 - 系统概览",
  "panels": [
    {
      "title": "策略信号",
      "type": "stat",
      "targets": [
        {
          "expr": "sum(rate(strategy_signal_count[5m]))",
          "legendFormat": "信号/秒"
        }
      ]
    },
    {
      "title": "订单执行",
      "type": "stat",
      "targets": [
        {
          "expr": "sum(rate(order_submit_count[5m]))",
          "legendFormat": "订单/秒"
        }
      ]
    },
    {
      "title": "风控事件",
      "type": "stat",
      "targets": [
        {
          "expr": "sum(rate(risk_violation_count[5m]))",
          "legendFormat": "违规/秒"
        }
      ]
    },
    {
      "title": "策略绩效热力图",
      "type": "heatmap",
      "targets": [
        {
          "expr": "strategy_return_rate",
          "legendFormat": "{{strategy_id}}"
        }
      ]
    }
  ]
}
```


## 5. 告警规则

### 5.1 告警规则定义

```yaml
# alertmanager/rules/quant_system.yaml

groups:
  - name: strategy_alerts
    rules:
      - alert: StrategyHighLatency
        expr: strategy_signal_latency > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "策略信号延迟过高"
          description: "{{ $labels.strategy_id }} 延迟 {{ $value }}s"

      - alert: StrategyNoSignal
        expr: rate(strategy_signal_count[10m]) == 0
        for: 30m
        labels:
          severity: critical
        annotations:
          summary: "策略无信号"
          description: "{{ $labels.strategy_id }} 已30分钟无信号"

  - name: risk_alerts
    rules:
      - alert: RiskViolation
        expr: rate(risk_violation_count[5m]) > 10
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "风控违规频繁"
          description: "5分钟内发生 {{ $value }} 次违规"

      - alert: RiskExposureHigh
        expr: risk_position_value > 0.8
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "风险敞口过高"
          description: "当前敞口 {{ $value }}"

  - name: system_alerts
    rules:
      - alert: HighCPU
        expr: cpu_usage_percent > 80
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "CPU使用率高"
          description: "CPU使用率 {{ $value }}%"

      - alert: HighMemory
        expr: memory_usage_bytes > 8e9
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "内存使用率高"
          description: "内存使用 {{ $value | humanize1024 }}"
```

### 5.2 告警通知配置

```yaml
# alertmanager/config.yaml

route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'critical-pager'
      continue: true
    - match:
        severity: warning
      receiver: 'warning-email'

receivers:
  - name: 'default'
    webhook_configs:
      - url: 'http://localhost:5001/webhook/grafana'

  - name: 'critical-pager'
    webhook_configs:
      - url: 'http://localhost:5001/webhook/grafana'
    pagerduty_configs:
      - service_key: '${PAGERDUTY_KEY}'

  - name: 'warning-email'
    email_configs:
      - to: 'alert@quant.local'
        send_resolved: true
```


## 6. 快速部署

### 6.1 Docker Compose配置

```yaml
# docker-compose.monitoring.yml

version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./rules:/etc/prometheus/rules
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - ./dashboards:/etc/grafana/provisioning/dashboards
      - ./datasources:/etc/grafana/provisioning/datasources
    ports:
      - "3000:3000"
    depends_on:
      - prometheus

  alertmanager:
    image: prom/alertmanager:latest
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    ports:
      - "9093:9093"

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
```

### 6.2 启动命令

```bash
# 启动监控服务
docker-compose -f docker-compose.monitoring.yml up -d

# 访问
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
# AlertManager: http://localhost:9093
```


## 7. 指标导出代码示例

### 7.1 自定义指标导出

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# 定义指标
signal_count = Counter('strategy_signal_count', '策略信号数量',
                       ['strategy_id', 'signal_type'])
signal_latency = Histogram('strategy_signal_latency', '信号生成延迟',
                          ['strategy_id'])
risk_violation = Counter('risk_violation_count', '风控违规次数',
                       ['rule_id', 'severity'])
factor_ic = Gauge('factor_ic_value', '因子IC值', ['factor_id'])

# 在代码中使用
class StrategyMonitor:
    def on_signal(self, strategy_id: str, signal_type: str):
        signal_count.labels(strategy_id=strategy_id, signal_type=signal_type).inc()

    def on_risk_violation(self, rule_id: str, severity: str):
        risk_violation.labels(rule_id=rule_id, severity=severity).inc()

# 启动指标服务器
start_http_server(8000)
```


## 8. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本 - 简化版设计 |


**维护者**: 清风量化系统
**索引**: `MON_001`
