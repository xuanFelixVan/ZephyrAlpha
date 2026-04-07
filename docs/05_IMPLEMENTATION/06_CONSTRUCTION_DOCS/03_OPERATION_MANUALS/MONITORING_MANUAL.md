---
standard_type: ﮔﻛﺛﮔﮒ
responsibility:
  - 实施指南、部署文档
applicable_scope: ﮒ۷ﻝﺏﭨﻝﭨ?compliance_level: ﮔ­۲ﮒﺙﮔ ﮒ
parent_document: ../README.md
implementation_status: ﮒﺓﺎﮒ؟ﮔ?owner: ﻟﺟﻝﭨﺑﮒ۱ﻠ
version: 1.0.0
module_id: MONITORING_MANUAL
created_date: 2026-04-02
last_updated: 2026-04-02
---
---

# ﻝﺏﭨﻝﭨﻝﮔ۶ﮔﮒ
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


**ﮔﮔ۰۲ﻝﮔ؛**: 1.0.0
**ﮔﮒﮔﺑﮔ?*: 2026-04-02
**ﮔﮔ۰۲ﮔﮔﻟ?*: ﻟﺟﻝﭨﺑﮒ۱ﻠ

---

## 1. ﻝﮔ۶ﮔ۵ﻟﺟﺍ

### 1.1 ﻝﮔ۶ﻝ؟ﮔ 

ﮒﭨﭦﻝ،ﮒ۷ﻠ۱ﻝﻝﺏﭨﻝﭨﻝﮔ۶ﻛﺛﻝﺏﭨﺅﺙﻝ۰؟ﻛﺟZephyrAlphaﻠﮒﻛﭦ۳ﮔﻝﺏﭨﻝﭨﻝ۷ﺏﮒ؟ﻟﺟﻟ۰ﺅﺙﮒﮔﭘﮒﻝﺍﮒﮒ۳ﻝﮒﺙﮒﺕﺕﮔﮒﭖﻙ?
### 1.2 ﻝﮔ۶ﻟﮒﺑ

- ﻝﺏﭨﻝﭨﮔ۶ﻟﺛﻝﮔ۶
- ﮒﭦﻝ۷ﮔ۶ﻟﺛﻝﮔ۶
- ﻛﺕﮒ۰ﮔﮔ ﻝﮔ۶
- ﮒ؟ﮒ۷ﻛﭦﻛﭨﭘﻝﮔ۶
- ﮔ۴ﮒﺟﻝﮔ۶

### 1.3 ﻝﮔ۶ﮒﺓ۴ﮒﺓ

- **Prometheus**: ﮔﮔ ﮔﭘﻠﮒﮒ­ﮒ?- **Grafana**: ﮒﺁﻟ۶ﮒﻝﮔ۶ﻠ۱ﮔ?- **AlertManager**: ﮒﻟ­۵ﻝ؟۰ﻝ
- **ELK Stack**: ﮔ۴ﮒﺟﮔﭘﻠﮒﮒﮔ?
---

## 2. ﻝﺏﭨﻝﭨﻝﮔ۶

### 2.1 CPUﻝﮔ۶

**ﻝﮔ۶ﮔﮔ **:
- CPUﻛﺛﺟﻝ۷ﻝ?- CPUﻟﺑﻟﺛﺛ
- CPUﮔ ﺕﮒﺟﻛﺛﺟﻝ۷ﻝ?
**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# CPUﻛﺛﺟﻝ۷ﻝ?100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# CPUﻟﺑﻟﺛﺛ
node_load1
node_load5
node_load15
```

**ﮒﻟ­۵ﻟ۶ﮒ**:
```yaml
- alert: HighCPUUsage
  expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "CPUﻛﺛﺟﻝ۷ﻝﻟﺟﻠ،?
    description: "CPUﻛﺛﺟﻝ۷ﻝﻟﭘﻟﺟ?0%ﺅﺙﮒﺛﮒﮒ? {{ $value }}%"
```

### 2.2 ﮒﮒ­ﻝﮔ۶

**ﻝﮔ۶ﮔﮔ **:
- ﮒﮒ­ﻛﺛﺟﻝ۷ﻝ?- ﮒﮒ­ﻛﺛﺟﻝ۷ﻠ?- Swapﻛﺛﺟﻝ۷ﻝ?
**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﮒﮒ­ﻛﺛﺟﻝ۷ﻝ?(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# ﮒﮒ­ﻛﺛﺟﻝ۷ﻠ?node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes
```

**ﮒﻟ­۵ﻟ۶ﮒ**:
```yaml
- alert: HighMemoryUsage
  expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "ﮒﮒ­ﻛﺛﺟﻝ۷ﻝﻟﺟﻠ،?
    description: "ﮒﮒ­ﻛﺛﺟﻝ۷ﻝﻟﭘﻟﺟ?5%ﺅﺙﮒﺛﮒﮒ? {{ $value }}%"
```

### 2.3 ﻝ۲ﻝﻝﮔ۶

**ﻝﮔ۶ﮔﮔ **:
- ﻝ۲ﻝﻛﺛﺟﻝ۷ﻝ?- ﻝ۲ﻝIO
- ﻝ۲ﻝﻟﺁﭨﮒﻠﮒﭦ۵

**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﻝ۲ﻝﻛﺛﺟﻝ۷ﻝ?(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100

# ﻝ۲ﻝIO
irate(node_disk_read_bytes_total[5m])
irate(node_disk_written_bytes_total[5m])
```

**ﮒﻟ­۵ﻟ۶ﮒ**:
```yaml
- alert: HighDiskUsage
  expr: (1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100 > 85
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "ﻝ۲ﻝﻛﺛﺟﻝ۷ﻝﻟﺟﻠ،?
    description: "ﻝ۲ﻝﻛﺛﺟﻝ۷ﻝﻟﭘﻟﺟ?5%ﺅﺙﮒﺛﮒﮒ? {{ $value }}%"
```

### 2.4 ﻝﺛﻝﭨﻝﮔ۶

**ﻝﮔ۶ﮔﮔ **:
- ﻝﺛﻝﭨﮔﭖﻠ
- ﻝﺛﻝﭨﻟﺟﮔ۴ﮔ?- ﻝﺛﻝﭨﻠﻟﺁﺁﻝ?
**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﻝﺛﻝﭨﮔﭖﻠ
irate(node_network_receive_bytes_total[5m])
irate(node_network_transmit_bytes_total[5m])

# ﻝﺛﻝﭨﻟﺟﮔ۴ﮔ?node_netstat_Tcp_CurrEstab
```

---

## 3. ﮒﭦﻝ۷ﻝﮔ۶

### 3.1 APIﻝﮔ۶

**ﻝﮔ۶ﮔﮔ **:
- ﻟﺁﺓﮔﺎﻠﻝ
- ﮒﮒﭦﮔﭘﻠﺑ
- ﻠﻟﺁﺁﻝ?- ﮒﺗﭘﮒﻟﺟﮔ۴ﮔ?
**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﻟﺁﺓﮔﺎﻠﻝ
rate(http_requests_total[5m])

# ﮒﺗﺏﮒﮒﮒﭦﮔﭘﻠﺑ
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

# ﻠﻟﺁﺁﻝ?rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
```

**ﮒﻟ­۵ﻟ۶ﮒ**:
```yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.1
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "APIﻠﻟﺁﺁﻝﻟﺟﻠ،?
    description: "APIﻠﻟﺁﺁﻝﻟﭘﻟﺟ?0%ﺅﺙﮒﺛﮒﮒ? {{ $value | humanizePercentage }}"

- alert: SlowResponse
  expr: rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m]) > 1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "APIﮒﮒﭦﮔﭘﻠﺑﻟﺟﻠﺟ"
    description: "APIﮒﺗﺏﮒﮒﮒﭦﮔﭘﻠﺑﻟﭘﻟﺟ1ﻝ۶ﺅﺙﮒﺛﮒﮒ? {{ $value }}ﻝ۶?
```

### 3.2 ﮔﺍﮔ؟ﮒﭦﻝﮔ?
**ﻝﮔ۶ﮔﮔ **:
- ﻟﺟﮔ۴ﮔ?- ﮔ۴ﻟﺁ۱ﮔ۶ﻟﺛ
- ﮔ۱ﮔ۴ﻟﺁ?- ﮔ­ﭨﻠ

**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﻟﺟﮔ۴ﮔ?pg_stat_activity_count

# ﮔ۱ﮔ۴ﻟﺁ?rate(pg_stat_statements_mean_exec_time_seconds[5m])
```

**ﮒﻟ­۵ﻟ۶ﮒ**:
```yaml
- alert: TooManyDBConnections
  expr: pg_stat_activity_count > 100
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "ﮔﺍﮔ؟ﮒﭦﻟﺟﮔ۴ﮔﺍﻟﺟﮒ۳"
    description: "ﮔﺍﮔ؟ﮒﭦﻟﺟﮔ۴ﮔﺍﻟﭘﻟﺟ100ﺅﺙﮒﺛﮒﮒ? {{ $value }}"

- alert: SlowDBQuery
  expr: rate(pg_stat_statements_mean_exec_time_seconds[5m]) > 1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "ﮔﺍﮔ؟ﮒﭦﮔ۴ﻟﺁ۱ﻟﺟﮔ?
    description: "ﮔﺍﮔ؟ﮒﭦﮒﺗﺏﮒﮔ۴ﻟﺁ۱ﮔﭘﻠﺑﻟﭘﻟﺟ?ﻝ۶?
```

### 3.3 Redisﻝﮔ۶

**ﻝﮔ۶ﮔﮔ **:
- ﮒﮒ­ﻛﺛﺟﻝ۷
- ﻟﺟﮔ۴ﮔ?- ﮒﺛﻛﭨ۳ﮔ۶ﻟ۰ﻠﻝ
- ﻠ؟ﻝ۸ﭦﻠﺑﮒﺛﻛﺕ­ﻝ

**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﮒﮒ­ﻛﺛﺟﻝ۷
redis_memory_used_bytes

# ﻟﺟﮔ۴ﮔ?redis_connected_clients

# ﮒﺛﻛﭨ۳ﮔ۶ﻟ۰ﻠﻝ
rate(redis_commands_processed_total[5m])

# ﻠ؟ﻝ۸ﭦﻠﺑﮒﺛﻛﺕ­ﻝ
rate(redis_keyspace_hits_total[5m]) / (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m]))
```

---

## 4. ﻛﺕﮒ۰ﻝﮔ۶

### 4.1 ﻛﭦ۳ﮔﻝﮔ۶

**ﻝﮔ۶ﮔﮔ **:
- ﻟ؟۱ﮒﮔﺍﻠ
- ﮔﻛﭦ۳ﮔﺍﻠ
- ﮔﻛﭦ۳ﻠﻠ۱
- ﮔﮒﻝ?
**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﻟ؟۱ﮒﮔﺍﻠ
rate(orders_total[5m])

# ﮔﻛﭦ۳ﻠﻠ۱
rate(trade_value_total[5m])

# ﮔﮒﻝ?rate(orders_rejected_total[5m]) / rate(orders_total[5m])
```

**ﮒﻟ­۵ﻟ۶ﮒ**:
```yaml
- alert: HighRejectionRate
  expr: rate(orders_rejected_total[5m]) / rate(orders_total[5m]) > 0.05
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "ﻟ؟۱ﮒﮔﮒﻝﻟﺟﻠ،?
    description: "ﻟ؟۱ﮒﮔﮒﻝﻟﭘﻟﺟ?%ﺅﺙﮒﺛﮒﮒ? {{ $value | humanizePercentage }}"
```

### 4.2 ﻝ­ﻝ۴ﻝﮔ۶

**ﻝﮔ۶ﮔﮔ **:
- ﻝ­ﻝ۴ﻟﺟﻟ۰ﻝﭘﮔ?- ﻝ­ﻝ۴ﮔﭘﻝ
- ﻝ­ﻝ۴ﮒﮔ۳
- ﻝ­ﻝ۴ﮒ۳ﮔ؟ﮔﺁﻝ

**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﻝ­ﻝ۴ﮔﭘﻝ
strategy_returns_total

# ﻝ­ﻝ۴ﮒﮔ۳
strategy_drawdown

# ﻝ­ﻝ۴ﮒ۳ﮔ؟ﮔﺁﻝ
strategy_sharpe_ratio
```

**ﮒﻟ­۵ﻟ۶ﮒ**:
```yaml
- alert: StrategyDrawdown
  expr: strategy_drawdown > 0.1
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "ﻝ­ﻝ۴ﮒﮔ۳ﻟﺟﮒ۳۶"
    description: "ﻝ­ﻝ۴ﮒﮔ۳ﻟﭘﻟﺟ10%ﺅﺙﮒﺛﮒﮒ? {{ $value | humanizePercentage }}"
```

### 4.3 ﻠ۲ﮔ۶ﻝﮔ۶

**ﻝﮔ۶ﮔﮔ **:
- ﻠ۲ﮔ۶ﻟ۶۵ﮒﮔ؛۰ﮔﺍ
- ﻠ۲ﮔ۶ﮔ۵ﮔ۹ﮔ؛۰ﮔﺍ
- ﻠ۲ﮔ۶ﻟ۶ﮒﮒﺛﻛﺕ­ﻝ?
**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﻠ۲ﮔ۶ﻟ۶۵ﮒﮔ؛۰ﮔﺍ
rate(risk_control_triggered_total[5m])

# ﻠ۲ﮔ۶ﮔ۵ﮔ۹ﮔ؛۰ﮔﺍ
rate(risk_control_blocked_total[5m])
```

---

## 5. ﮔ۴ﮒﺟﻝﮔ۶

### 5.1 ﮔ۴ﮒﺟﮔﭘﻠ

**ﻠﻝﺛ؟Filebeat**:
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

### 5.2 ﮔ۴ﮒﺟﮒﮔ

**Kibanaﮔ۴ﻟﺁ۱ﻝ۳ﭦﻛﺝ**:
```
# ﮔ۴ﮔﺝﻠﻟﺁﺁﮔ۴ﮒﺟ
level: ERROR

# ﮔ۴ﮔﺝﻝﺗﮒ؟APIﻝﮔ۴ﮒﺟ?api: /api/orders AND level: ERROR

# ﮔ۴ﮔﺝﮔ۱ﻟﺁﺓﮔﺎ?duration: >1000
```

### 5.3 ﮔ۴ﮒﺟﮒﻟ­۵

**ﻠﻝﺛ؟ﮒﻟ­۵ﻟ۶ﮒ**:
```yaml
- alert: HighErrorLogRate
  expr: rate(log_entries_total{level="ERROR"}[5m]) > 10
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "ﻠﻟﺁﺁﮔ۴ﮒﺟﻟﺟﮒ۳"
    description: "ﻠﻟﺁﺁﮔ۴ﮒﺟﻠﻝﻟﭘﻟﺟ10ﮔ?ﮒﻠ"
```

---

## 6. Grafanaﻠ۱ﮔﺟ

### 6.1 ﻝﺏﭨﻝﭨﻝﮔ۶ﻠ۱ﮔﺟ

**ﻠ۱ﮔﺟﻠﻝﺛ؟**:
```json
{
  "title": "ﻝﺏﭨﻝﭨﻝﮔ۶",
  "panels": [
    {
      "title": "CPUﻛﺛﺟﻝ۷ﻝ?,
      "type": "graph",
      "targets": [
        {
          "expr": "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
        }
      ]
    },
    {
      "title": "ﮒﮒ­ﻛﺛﺟﻝ۷ﻝ?,
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

### 6.2 ﮒﭦﻝ۷ﻝﮔ۶ﻠ۱ﮔﺟ

**ﻠ۱ﮔﺟﻠﻝﺛ؟**:
```json
{
  "title": "ﮒﭦﻝ۷ﻝﮔ۶",
  "panels": [
    {
      "title": "ﻟﺁﺓﮔﺎﻠﻝ",
      "type": "graph",
      "targets": [
        {
          "expr": "rate(http_requests_total[5m])"
        }
      ]
    },
    {
      "title": "ﮒﮒﭦﮔﭘﻠﺑ",
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

## 7. ﮒﻟ­۵ﻝ؟۰ﻝ

### 7.1 ﮒﻟ­۵ﮔﺕ ﻠ

**ﻠﻝﺛ؟ﻠﻝ۴ﮔﺕ ﻠ**:
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

### 7.2 ﮒﻟ­۵ﮒﻝﭦ۶

**ﮒﻟ­۵ﻝﭦ۶ﮒ،**:
- **Critical**: ﻠﻟ۵ﻝ،ﮒﺏﮒ۳ﻝ?- **Warning**: ﻠﻟ۵ﮒﺏﮔﺏ?- **Info**: ﻛﺟ۰ﮔﺁﻠﻝ۴

**ﮒﻟ­۵ﮒ۳ﻝﮔﭖﻝ۷**:
1. ﮔ۴ﮔﭘﮒﻟ­۵ﻠﻝ۴
2. ﻝ۰؟ﻟ؟۳ﮒﻟ­۵ﻝﭦ۶ﮒ،
3. ﮔ۴ﻝﻝﮔ۶ﻠ۱ﮔﺟ
4. ﮒﮔﮔ ﺗﮔ؛ﮒﮒ 
5. ﮔ۶ﻟ۰ﻛﺟ؟ﮒ۳ﮔ۹ﮔﺛ
6. ﻠ۹ﻟﺁﻛﺟ؟ﮒ۳ﮔﮔ
7. ﻟ؟ﺍﮒﺛﮒ۳ﻝﻟﺟﻝ۷

---

## 8. ﻝﮔ۶ﻝﭨﺑﮔ۳

### 8.1 ﮔ۴ﮒﺕﺕﮔ۲ﮔ?
**ﮔﺁﮔ۴ﮔ۲ﮔ۴ﻠ۰ﺗ**:
- [ ] ﮔ۲ﮔ۴ﻝﺏﭨﻝﭨﻟﭖﮔﭦﻛﺛﺟﻝ۷ﮔﮒ?- [ ] ﮔ۲ﮔ۴ﮒﭦﻝ۷ﻠﻟﺁﺁﮔ۴ﮒﺟ?- [ ] ﮔ۲ﮔ۴ﮒﻟ­۵ﮒﮒ?- [ ] ﮔ۲ﮔ۴ﮒ۳ﻛﭨﺛﻝﭘﮔ?
### 8.2 ﮒ؟ﮔﻝﭨﺑﮔ۳

**ﮔﺁﮒ۷ﻝﭨﺑﮔ۳**:
- ﮔﺕﻝﻟﺟﮔﻝﮔ۶ﮔﺍﮔ؟
- ﻛﺙﮒﮒﻟ­۵ﻟ۶ﮒ
- ﮔﺑﮔﺍﻝﮔ۶ﻠ۱ﮔﺟ

**ﮔﺁﮔﻝﭨﺑﮔ۳**:
- ﻟﺁﻛﺙﺍﻝﮔ۶ﻟ۵ﻝﻝ?- ﻟﺍﮔﺑﮒﻟ­۵ﻠﮒ?- ﻛﺙﮒﻝﮔ۶ﮔ۶ﻟﺛ

---

## 9. ﮔﻠﮔﮔ۴

### 9.1 ﮒﺕﺕﻟ۶ﻠ؟ﻠ۱

**ﻠ؟ﻠ۱1: ﻝﮔ۶ﮔﺍﮔ؟ﻝﺙﭦﮒ۳ﺎ**
```bash
# ﮔ۲ﮔ۴Prometheusﻝﭘﮔ?systemctl status prometheus

# ﮔ۲ﮔ۴ﮔﺍﮔ؟ﻠﻠ?curl http://localhost:9090/api/v1/targets

# ﮔ۲ﮔ۴ﮒ­ﮒ۷ﻝ۸ﭦﻠ?df -h /var/lib/prometheus
```

**ﻠ؟ﻠ۱2: ﮒﻟ­۵ﮔ۹ﮒﻠ?*
```bash
# ﮔ۲ﮔ۴AlertManagerﻝﭘﮔ?systemctl status alertmanager

# ﮔ۲ﮔ۴ﮒﻟ­۵ﻟ۶ﮒ?curl http://localhost:9090/api/v1/rules

# ﮔ۲ﮔ۴ﻠﻝ۴ﮔﺕ ﻠ
curl http://localhost:9093/api/v1/receivers
```

**ﻠ؟ﻠ۱3: Grafanaﻠ۱ﮔﺟﮔ ﮔﺏﻟ؟ﺟﻠ؟**
```bash
# ﮔ۲ﮔ۴Grafanaﻝﭘﮔ?systemctl status grafana-server

# ﮔ۲ﮔ۴ﮔ۴ﮒﺟ?tail -f /var/log/grafana/grafana.log

# ﻠﮒﺁﮔﮒ۰
systemctl restart grafana-server
```

---

## 10. ﮔﻛﺛﺏﮒ؟ﻟﺓ?
### 10.1 ﻝﮔ۶ﻟ؟ﺝﻟ؟۰ﮒﮒ

1. **ﮒ۷ﻠ۱ﮔ?*: ﻟ۵ﻝﮔﮔﮒﺏﻠ؟ﮔﮔ ?2. **ﮒﮔﭘﮔ?*: ﮒﺟ،ﻠﮒﻝﺍﮒﮒﮒﭦﻠ؟ﻠ۱
3. **ﮒﻝ۰؟ﮔ?*: ﻠﺟﮒﻟﺁﺁﮔ۴ﮒﮔﺙﮔ?4. **ﮒﺁﮔﻛﺛﮔ?*: ﮔﻛﺝﮒﺁﮔﻛﺛﻝﮒﻟ­۵ﻛﺟ۰ﮔﺁ

### 10.2 ﮒﻟ­۵ﻟ؟ﺝﻟ؟۰ﮒﮒ

1. **ﮒﻝﭦ۶ﻝ؟۰ﻝ**: ﮔ ﺗﮔ؟ﻛﺕ۴ﻠﻝ۷ﮒﭦ۵ﮒﻝﭦ۶
2. **ﻠﺟﮒﮒ۹ﻠﺏ**: ﮒﮒﺍﮔ ﮔﮒﻟ­۵
3. **ﮔﻛﺝﻛﺕﻛﺕﮔ?*: ﮒﮒ،ﻟﭘﺏﮒ۳ﻝﻟﺁﮔ­ﻛﺟ۰ﮔ?4. **ﮒﺟ،ﻠﮒﮒﭦ?*: ﮒﭨﭦﻝ،ﮒﺟ،ﻠﮒﮒﭦﮔﭦﮒ?
---

## 11. ﮒﻟﮔﮔ۰?
- [ﻠ۷ﻝﺛﺎﮔﮒ](./DEPLOYMENT_MANUAL.md)
- [ﻠ۲ﻠ۸ﻝﮔ۶ﮔﮒ](./RISK_MONITORING_MANUAL.md)
- [ﻝﭨﺑﮔ۳ﮔﮒ](./MAINTENANCE_MANUAL.md)
- [ﻝﮔ۶ﻠﻝﺛ؟ﮔ۷۰ﮔﺟ](../04_CONFIG_TEMPLATES/monitoring_config_template.yaml)

---

**ﮔﮔ۰۲ﻝﭘﮔ?*: ﮔ­۲ﮒﺙﮔ ﮒ
**ﻛﺕﮔ؛۰ﮒ؟۰ﮔ۴**: 2026-07-02
