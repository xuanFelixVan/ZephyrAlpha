---
standard_type: 操作指南
applicable_scope: 全系统
compliance_level: 正式标准
parent_document: ../README.md
implementation_status: 已完成
owner: 运维团队
version: 1.0.0
module_id: MONITORING_MANUAL
created_date: 2026-04-02
last_updated: 2026-04-02
---
# 系统监控手册

**文档版本**: 1.0.0
**最后更新**: 2026-04-02
**文档所有者**: 运维团队

---

## 1. 监控概述

### 1.1 监控目标

建立全面的系统监控体系，确保ZephyrAlpha量化交易系统稳定运行，及时发现和处理异常情况。

### 1.2 监控范围

- 系统性能监控
- 应用性能监控
- 业务指标监控
- 安全事件监控
- 日志监控

### 1.3 监控工具

- **Prometheus**: 指标收集和存储
- **Grafana**: 可视化监控面板
- **AlertManager**: 告警管理
- **ELK Stack**: 日志收集和分析

---

## 2. 系统监控

### 2.1 CPU监控

**监控指标**:
- CPU使用率
- CPU负载
- CPU核心使用率

**Prometheus查询**:
```promql
# CPU使用率
100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# CPU负载
node_load1
node_load5
node_load15
```

**告警规则**:
```yaml
- alert: HighCPUUsage
  expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "CPU使用率过高"
    description: "CPU使用率超过80%，当前值: {{ $value }}%"
```

### 2.2 内存监控

**监控指标**:
- 内存使用率
- 内存使用量
- Swap使用率

**Prometheus查询**:
```promql
# 内存使用率
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# 内存使用量
node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes
```

**告警规则**:
```yaml
- alert: HighMemoryUsage
  expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "内存使用率过高"
    description: "内存使用率超过85%，当前值: {{ $value }}%"
```

### 2.3 磁盘监控

**监控指标**:
- 磁盘使用率
- 磁盘IO
- 磁盘读写速度

**Prometheus查询**:
```promql
# 磁盘使用率
(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100

# 磁盘IO
irate(node_disk_read_bytes_total[5m])
irate(node_disk_written_bytes_total[5m])
```

**告警规则**:
```yaml
- alert: HighDiskUsage
  expr: (1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100 > 85
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "磁盘使用率过高"
    description: "磁盘使用率超过85%，当前值: {{ $value }}%"
```

### 2.4 网络监控

**监控指标**:
- 网络流量
- 网络连接数
- 网络错误率

**Prometheus查询**:
```promql
# 网络流量
irate(node_network_receive_bytes_total[5m])
irate(node_network_transmit_bytes_total[5m])

# 网络连接数
node_netstat_Tcp_CurrEstab
```

---

## 3. 应用监控

### 3.1 API监控

**监控指标**:
- 请求速率
- 响应时间
- 错误率
- 并发连接数

**Prometheus查询**:
```promql
# 请求速率
rate(http_requests_total[5m])

# 平均响应时间
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

# 错误率
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
```

**告警规则**:
```yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.1
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "API错误率过高"
    description: "API错误率超过10%，当前值: {{ $value | humanizePercentage }}"

- alert: SlowResponse
  expr: rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m]) > 1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "API响应时间过长"
    description: "API平均响应时间超过1秒，当前值: {{ $value }}秒"
```

### 3.2 数据库监控

**监控指标**:
- 连接数
- 查询性能
- 慢查询
- 死锁

**Prometheus查询**:
```promql
# 连接数
pg_stat_activity_count

# 慢查询
rate(pg_stat_statements_mean_exec_time_seconds[5m])
```

**告警规则**:
```yaml
- alert: TooManyDBConnections
  expr: pg_stat_activity_count > 100
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "数据库连接数过多"
    description: "数据库连接数超过100，当前值: {{ $value }}"

- alert: SlowDBQuery
  expr: rate(pg_stat_statements_mean_exec_time_seconds[5m]) > 1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "数据库查询过慢"
    description: "数据库平均查询时间超过1秒"
```

### 3.3 Redis监控

**监控指标**:
- 内存使用
- 连接数
- 命令执行速率
- 键空间命中率

**Prometheus查询**:
```promql
# 内存使用
redis_memory_used_bytes

# 连接数
redis_connected_clients

# 命令执行速率
rate(redis_commands_processed_total[5m])

# 键空间命中率
rate(redis_keyspace_hits_total[5m]) / (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m]))
```

---

## 4. 业务监控

### 4.1 交易监控

**监控指标**:
- 订单数量
- 成交数量
- 成交金额
- 拒单率

**Prometheus查询**:
```promql
# 订单数量
rate(orders_total[5m])

# 成交金额
rate(trade_value_total[5m])

# 拒单率
rate(orders_rejected_total[5m]) / rate(orders_total[5m])
```

**告警规则**:
```yaml
- alert: HighRejectionRate
  expr: rate(orders_rejected_total[5m]) / rate(orders_total[5m]) > 0.05
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "订单拒单率过高"
    description: "订单拒单率超过5%，当前值: {{ $value | humanizePercentage }}"
```

### 4.2 策略监控

**监控指标**:
- 策略运行状态
- 策略收益
- 策略回撤
- 策略夏普比率

**Prometheus查询**:
```promql
# 策略收益
strategy_returns_total

# 策略回撤
strategy_drawdown

# 策略夏普比率
strategy_sharpe_ratio
```

**告警规则**:
```yaml
- alert: StrategyDrawdown
  expr: strategy_drawdown > 0.1
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "策略回撤过大"
    description: "策略回撤超过10%，当前值: {{ $value | humanizePercentage }}"
```

### 4.3 风控监控

**监控指标**:
- 风控触发次数
- 风控拦截次数
- 风控规则命中率

**Prometheus查询**:
```promql
# 风控触发次数
rate(risk_control_triggered_total[5m])

# 风控拦截次数
rate(risk_control_blocked_total[5m])
```

---

## 5. 日志监控

### 5.1 日志收集

**配置Filebeat**:
```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/zephyr/*.log
  fields:
    app: zephyr
  fields_under_root: true

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "zephyr-%{+yyyy.MM.dd}"
```

### 5.2 日志分析

**Kibana查询示例**:
```
# 查找错误日志
level: ERROR

# 查找特定API的日志
api: /api/orders AND level: ERROR

# 查找慢请求
duration: >1000
```

### 5.3 日志告警

**配置告警规则**:
```yaml
- alert: HighErrorLogRate
  expr: rate(log_entries_total{level="ERROR"}[5m]) > 10
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "错误日志过多"
    description: "错误日志速率超过10条/分钟"
```

---

## 6. Grafana面板

### 6.1 系统监控面板

**面板配置**:
```json
{
  "title": "系统监控",
  "panels": [
    {
      "title": "CPU使用率",
      "type": "graph",
      "targets": [
        {
          "expr": "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
        }
      ]
    },
    {
      "title": "内存使用率",
      "type": "graph",
      "targets": [
        {
          "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100"
        }
      ]
    }
  ]
}
```

### 6.2 应用监控面板

**面板配置**:
```json
{
  "title": "应用监控",
  "panels": [
    {
      "title": "请求速率",
      "type": "graph",
      "targets": [
        {
          "expr": "rate(http_requests_total[5m])"
        }
      ]
    },
    {
      "title": "响应时间",
      "type": "graph",
      "targets": [
        {
          "expr": "rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])"
        }
      ]
    }
  ]
}
```

---

## 7. 告警管理

### 7.1 告警渠道

**配置通知渠道**:
```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'team-email'

receivers:
- name: 'team-email'
  email_configs:
  - to: 'team@example.com'
    from: 'alert@example.com'
    smarthost: 'smtp.example.com:587'
    auth_username: 'alert@example.com'
    auth_password: 'password'

- name: 'team-slack'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/xxx'
    channel: '#alerts'
```

### 7.2 告警分级

**告警级别**:
- **Critical**: 需要立即处理
- **Warning**: 需要关注
- **Info**: 信息通知

**告警处理流程**:
1. 接收告警通知
2. 确认告警级别
3. 查看监控面板
4. 分析根本原因
5. 执行修复措施
6. 验证修复效果
7. 记录处理过程

---

## 8. 监控维护

### 8.1 日常检查

**每日检查项**:
- [ ] 检查系统资源使用情况
- [ ] 检查应用错误日志
- [ ] 检查告警历史
- [ ] 检查备份状态

### 8.2 定期维护

**每周维护**:
- 清理过期监控数据
- 优化告警规则
- 更新监控面板

**每月维护**:
- 评估监控覆盖率
- 调整告警阈值
- 优化监控性能

---

## 9. 故障排查

### 9.1 常见问题

**问题1: 监控数据缺失**
```bash
# 检查Prometheus状态
systemctl status prometheus

# 检查数据采集
curl http://localhost:9090/api/v1/targets

# 检查存储空间
df -h /var/lib/prometheus
```

**问题2: 告警未发送**
```bash
# 检查AlertManager状态
systemctl status alertmanager

# 检查告警规则
curl http://localhost:9090/api/v1/rules

# 检查通知渠道
curl http://localhost:9093/api/v1/receivers
```

**问题3: Grafana面板无法访问**
```bash
# 检查Grafana状态
systemctl status grafana-server

# 检查日志
tail -f /var/log/grafana/grafana.log

# 重启服务
systemctl restart grafana-server
```

---

## 10. 最佳实践

### 10.1 监控设计原则

1. **全面性**: 覆盖所有关键指标
2. **及时性**: 快速发现和响应问题
3. **准确性**: 避免误报和漏报
4. **可操作性**: 提供可操作的告警信息

### 10.2 告警设计原则

1. **分级管理**: 根据严重程度分级
2. **避免噪音**: 减少无效告警
3. **提供上下文**: 包含足够的诊断信息
4. **快速响应**: 建立快速响应机制

---

## 11. 参考文档

- [部署手册](./DEPLOYMENT_MANUAL.md)
- [风险监控手册](./RISK_MONITORING_MANUAL.md)
- [维护手册](./MAINTENANCE_MANUAL.md)
- [监控配置模板](../04_CONFIG_TEMPLATES/monitoring_config_template.yaml)

---

**文档状态**: 正式标准
**下次审查**: 2026-07-02
