---
module_id: MONITORING_MANUAL
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
standard_type: ﮔﻛﺛﮔﮒ
responsibility:
  - 实施指南、部署文档
applicable_scope: ﮒ۷ﻝﺏﭨﻝﭨ?compliance_level: ﮔ۲ﮒﺙﮔﮒ
parent_document: ../README.md
implementation_status: ﮒﺓﺎﮒ؟ﮔ?owner: ﻟﺟﻝﭨﺑﮒ۱ﻠ
version: 1.0.0
module_id: MONITORING_MANUAL
created_date: 2026-04-02
last_updated: 2026-04-02
---
---

# ﻝﺏﭨﻝﭨﻝﮔ۶ﮔﮒ
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


**ﮔﮔ۰۲ﻝﮔ؛**: 1.0.0
**ﮔﮒﮔﺑﮔ?*: 2026-04-02
**ﮔﮔ۰۲ﮔﮔﻟ?*: ﻟﺟﻝﭨﺑﮒ۱ﻠ

---

## 1. ﻝﮔ۶ﮔ۵ﻟﺟﺍ

### 1.1 ﻝﮔ۶ﻝ؟ﮔ

ﮒﭨﭦﻝ،ﮒ۷ﻠ۱ﻝﻝﺏﭨﻝﭨﻝﮔ۶ﻛﺛﻝﺏﭨﺅﺙﻝ۰؟ﻛﺟZephyrAlphaﻠﮒﻛﭦ۳ﮔﻝﺏﭨﻝﭨﻝ۷ﺏﮒ؟ﻟﺟﻟ۰ﺅﺙﮒﮔﭘﮒﻝﺍﮒﮒ۳ﻝﮒﺙﮒﺕﺕﮔﮒﭖﻙ?
### 1.2 ﻝﮔ۶ﻟﮒﺑ

- ﻝﺏﭨﻝﭨﮔ۶ﻟﺛﻝﮔ۶
- ﮒﭦﻝ۷ﮔ۶ﻟﺛﻝﮔ۶
- ﻛﺕﮒ۰ﮔﮔﻝﮔ۶
- ﮒ؟ﮒ۷ﻛﭦﻛﭨﭘﻝﮔ۶
- ﮔ۴ﮒﺟﻝﮔ۶

### 1.3 ﻝﮔ۶ﮒﺓ۴ﮒﺓ

- **Prometheus**: ﮔﮔﮔﭘﻠﮒﮒﮒ?- **Grafana**: ﮒﺁﻟ۶ﮒﻝﮔ۶ﻠ۱ﮔ?- **AlertManager**: ﮒﻟ۵ﻝ؟۰ﻝ
- **ELK Stack**: ﮔ۴ﮒﺟﮔﭘﻠﮒﮒﮔ?
---

## 2. ﻝﺏﭨﻝﭨﻝﮔ۶

### 2.1 CPUﻝﮔ۶

**ﻝﮔ۶ﮔﮔ**:
- CPUﻛﺛﺟﻝ۷ﻝ?- CPUﻟﺑﻟﺛﺛ
- CPUﮔﺕﮒﺟﻛﺛﺟﻝ۷ﻝ?
**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# CPUﻛﺛﺟﻝ۷ﻝ?100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# CPUﻟﺑﻟﺛﺛ
node_load1
node_load5
node_load15
```

**ﮒﻟ۵ﻟ۶ﮒ**:
```yaml
- alert: HighCPUUsage
  expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "CPUﻛﺛﺟﻝ۷ﻝﻟﺟﻠ،?
    description: "CPUﻛﺛﺟﻝ۷ﻝﻟﭘﻟﺟ?0%ﺅﺙﮒﺛﮒﮒ? {{ $value }}%"
```

### 2.2 ﮒﮒﻝﮔ۶

**ﻝﮔ۶ﮔﮔ**:
- ﮒﮒﻛﺛﺟﻝ۷ﻝ?- ﮒﮒﻛﺛﺟﻝ۷ﻠ?- Swapﻛﺛﺟﻝ۷ﻝ?
**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﮒﮒﻛﺛﺟﻝ۷ﻝ?(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# ﮒﮒﻛﺛﺟﻝ۷ﻠ?node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes
```

**ﮒﻟ۵ﻟ۶ﮒ**:
```yaml
- alert: HighMemoryUsage
  expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
  for: 5m
  labels:
    severity: warning
  annotations:
summary: "ﮒﮒﻛﺛﺟﻝ۷ﻝﻟﺟﻠ،?
description: "ﮒﮒﻛﺛﺟﻝ۷ﻝﻟﭘﻟﺟ?5%ﺅﺙﮒﺛﮒﮒ? {{ $value }}%"
```

### 2.3 ﻝ۲ﻝﻝﮔ۶

**ﻝﮔ۶ﮔﮔ**:
- ﻝ۲ﻝﻛﺛﺟﻝ۷ﻝ?- ﻝ۲ﻝIO
- ﻝ۲ﻝﻟﺁﭨﮒﻠﮒﭦ۵

**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﻝ۲ﻝﻛﺛﺟﻝ۷ﻝ?(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100

# ﻝ۲ﻝIO
irate(node_disk_read_bytes_total[5m])
irate(node_disk_written_bytes_total[5m])
```

**ﮒﻟ۵ﻟ۶ﮒ**:
```yaml
- alert: HighDiskUsage
  expr: (1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100 > 85
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "ﻝ۲ﻝﻛﺛﺟﻝ۷ﻝﻟﺟﻠ،?
    description: "ﻝ۲ﻝﻛﺛﺟﻝ۷ﻝﻟﭘﻟﺟ?5%ﺅﺙﮒﺛﮒﮒ? {{ $value }}%"
```

### 2.4 ﻝﺛﻝﭨﻝﮔ۶

**ﻝﮔ۶ﮔﮔ**:
- ﻝﺛﻝﭨﮔﭖﻠ
- ﻝﺛﻝﭨﻟﺟﮔ۴ﮔ?- ﻝﺛﻝﭨﻠﻟﺁﺁﻝ?
**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﻝﺛﻝﭨﮔﭖﻠ
irate(node_network_receive_bytes_total[5m])
irate(node_network_transmit_bytes_total[5m])

# ﻝﺛﻝﭨﻟﺟﮔ۴ﮔ?node_netstat_Tcp_CurrEstab
```

---

## 3. ﮒﭦﻝ۷ﻝﮔ۶

### 3.1 APIﻝﮔ۶

**ﻝﮔ۶ﮔﮔ**:
- ﻟﺁﺓﮔﺎﻠﻝ
- ﮒﮒﭦﮔﭘﻠﺑ
- ﻠﻟﺁﺁﻝ?- ﮒﺗﭘﮒﻟﺟﮔ۴ﮔ?
**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﻟﺁﺓﮔﺎﻠﻝ
rate(http_requests_total[5m])

# ﮒﺗﺏﮒﮒﮒﭦﮔﭘﻠﺑ
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

# ﻠﻟﺁﺁﻝ?rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
```

**ﮒﻟ۵ﻟ۶ﮒ**:
```yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.1
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "APIﻠﻟﺁﺁﻝﻟﺟﻠ،?
    description: "APIﻠﻟﺁﺁﻝﻟﭘﻟﺟ?0%ﺅﺙﮒﺛﮒﮒ? {{ $value | humanizePercentage }}"

- alert: SlowResponse
  expr: rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m]) > 1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "APIﮒﮒﭦﮔﭘﻠﺑﻟﺟﻠﺟ"
    description: "APIﮒﺗﺏﮒﮒﮒﭦﮔﭘﻠﺑﻟﭘﻟﺟ1ﻝ۶ﺅﺙﮒﺛﮒﮒ? {{ $value }}ﻝ۶?
```

### 3.2 ﮔﺍﮔ؟ﮒﭦﻝﮔ?
**ﻝﮔ۶ﮔﮔ**:
- ﻟﺟﮔ۴ﮔ?- ﮔ۴ﻟﺁ۱ﮔ۶ﻟﺛ
- ﮔ۱ﮔ۴ﻟﺁ?- ﮔﭨﻠ

**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﻟﺟﮔ۴ﮔ?pg_stat_activity_count

# ﮔ۱ﮔ۴ﻟﺁ?rate(pg_stat_statements_mean_exec_time_seconds[5m])
```

**ﮒﻟ۵ﻟ۶ﮒ**:
```yaml
- alert: TooManyDBConnections
  expr: pg_stat_activity_count > 100
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "ﮔﺍﮔ؟ﮒﭦﻟﺟﮔ۴ﮔﺍﻟﺟﮒ۳"
    description: "ﮔﺍﮔ؟ﮒﭦﻟﺟﮔ۴ﮔﺍﻟﭘﻟﺟ100ﺅﺙﮒﺛﮒﮒ? {{ $value }}"

- alert: SlowDBQuery
  expr: rate(pg_stat_statements_mean_exec_time_seconds[5m]) > 1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "ﮔﺍﮔ؟ﮒﭦﮔ۴ﻟﺁ۱ﻟﺟﮔ?
    description: "ﮔﺍﮔ؟ﮒﭦﮒﺗﺏﮒﮔ۴ﻟﺁ۱ﮔﭘﻠﺑﻟﭘﻟﺟ?ﻝ۶?
```

### 3.3 Redisﻝﮔ۶

**ﻝﮔ۶ﮔﮔ**:
- ﮒﮒﻛﺛﺟﻝ۷
- ﻟﺟﮔ۴ﮔ?- ﮒﺛﻛﭨ۳ﮔ۶ﻟ۰ﻠﻝ
- ﻠ؟ﻝ۸ﭦﻠﺑﮒﺛﻛﺕﻝ

**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﮒﮒﻛﺛﺟﻝ۷
redis_memory_used_bytes

# ﻟﺟﮔ۴ﮔ?redis_connected_clients

# ﮒﺛﻛﭨ۳ﮔ۶ﻟ۰ﻠﻝ
rate(redis_commands_processed_total[5m])

# ﻠ؟ﻝ۸ﭦﻠﺑﮒﺛﻛﺕﻝ
rate(redis_keyspace_hits_total[5m]) / (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m]))
```

---

## 4. ﻛﺕﮒ۰ﻝﮔ۶

### 4.1 ﻛﭦ۳ﮔﻝﮔ۶

**ﻝﮔ۶ﮔﮔ**:
- ﻟ؟۱ﮒﮔﺍﻠ
- ﮔﻛﭦ۳ﮔﺍﻠ
- ﮔﻛﭦ۳ﻠﻠ۱
- ﮔﮒﻝ?
**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﻟ؟۱ﮒﮔﺍﻠ
rate(orders_total[5m])

# ﮔﻛﭦ۳ﻠﻠ۱
rate(trade_value_total[5m])

# ﮔﮒﻝ?rate(orders_rejected_total[5m]) / rate(orders_total[5m])
```

**ﮒﻟ۵ﻟ۶ﮒ**:
```yaml
- alert: HighRejectionRate
  expr: rate(orders_rejected_total[5m]) / rate(orders_total[5m]) > 0.05
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "ﻟ؟۱ﮒﮔﮒﻝﻟﺟﻠ،?
    description: "ﻟ؟۱ﮒﮔﮒﻝﻟﭘﻟﺟ?%ﺅﺙﮒﺛﮒﮒ? {{ $value | humanizePercentage }}"
```

### 4.2 ﻝﻝ۴ﻝﮔ۶

**ﻝﮔ۶ﮔﮔ**:
- ﻝﻝ۴ﻟﺟﻟ۰ﻝﭘﮔ?- ﻝﻝ۴ﮔﭘﻝ
- ﻝﻝ۴ﮒﮔ۳
- ﻝﻝ۴ﮒ۳ﮔ؟ﮔﺁﻝ

**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﻝﻝ۴ﮔﭘﻝ
strategy_returns_total

# ﻝﻝ۴ﮒﮔ۳
strategy_drawdown

# ﻝﻝ۴ﮒ۳ﮔ؟ﮔﺁﻝ
strategy_sharpe_ratio
```

**ﮒﻟ۵ﻟ۶ﮒ**:
```yaml
- alert: StrategyDrawdown
  expr: strategy_drawdown > 0.1
  for: 5m
  labels:
    severity: critical
  annotations:
summary: "ﻝﻝ۴ﮒﮔ۳ﻟﺟﮒ۳۶"
description: "ﻝﻝ۴ﮒﮔ۳ﻟﭘﻟﺟ10%ﺅﺙﮒﺛﮒﮒ? {{ $value | humanizePercentage }}"
```

### 4.3 ﻠ۲ﮔ۶ﻝﮔ۶

**ﻝﮔ۶ﮔﮔ**:
- ﻠ۲ﮔ۶ﻟ۶۵ﮒﮔ؛۰ﮔﺍ
- ﻠ۲ﮔ۶ﮔ۵ﮔ۹ﮔ؛۰ﮔﺍ
- ﻠ۲ﮔ۶ﻟ۶ﮒﮒﺛﻛﺕﻝ?
**Prometheusﮔ۴ﻟﺁ۱**:
```promql
# ﻠ۲ﮔ۶ﻟ۶۵ﮒﮔ؛۰ﮔﺍ
rate(risk_control_triggered_total[5m])

# ﻠ۲ﮔ۶ﮔ۵ﮔ۹ﮔ؛۰ﮔﺍ
rate(risk_control_blocked_total[5m])
```

---

## 5. ﮔ۴ﮒﺟﻝﮔ۶

### 5.1 ﮔ۴ﮒﺟﮔﭘﻠ

**ﻠﻝﺛ؟Filebeat**:
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

### 5.2 ﮔ۴ﮒﺟﮒﮔ

**Kibanaﮔ۴ﻟﺁ۱ﻝ۳ﭦﻛﺝ**:
```
# ﮔ۴ﮔﺝﻠﻟﺁﺁﮔ۴ﮒﺟ
level: ERROR

# ﮔ۴ﮔﺝﻝﺗﮒ؟APIﻝﮔ۴ﮒﺟ?api: /api/orders AND level: ERROR

# ﮔ۴ﮔﺝﮔ۱ﻟﺁﺓﮔﺎ?duration: >1000
```

### 5.3 ﮔ۴ﮒﺟﮒﻟ۵

**ﻠﻝﺛ؟ﮒﻟ۵ﻟ۶ﮒ**:
```yaml
- alert: HighErrorLogRate
  expr: rate(log_entries_total{level="ERROR"}[5m]) > 10
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "ﻠﻟﺁﺁﮔ۴ﮒﺟﻟﺟﮒ۳"
    description: "ﻠﻟﺁﺁﮔ۴ﮒﺟﻠﻝﻟﭘﻟﺟ10ﮔ?ﮒﻠ"
```

---

## 6. Grafanaﻠ۱ﮔﺟ

### 6.1 ﻝﺏﭨﻝﭨﻝﮔ۶ﻠ۱ﮔﺟ

**ﻠ۱ﮔﺟﻠﻝﺛ؟**:
```json
{
  "title": "ﻝﺏﭨﻝﭨﻝﮔ۶",
  "panels": [
    {
      "title": "CPUﻛﺛﺟﻝ۷ﻝ?,
      "type": "graph",
      "targets": [
        {
          "expr": "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
        }
      ]
    },
    {
"title": "ﮒﮒﻛﺛﺟﻝ۷ﻝ?,
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

### 6.2 ﮒﭦﻝ۷ﻝﮔ۶ﻠ۱ﮔﺟ

**ﻠ۱ﮔﺟﻠﻝﺛ؟**:
```json
{
  "title": "ﮒﭦﻝ۷ﻝﮔ۶",
  "panels": [
    {
      "title": "ﻟﺁﺓﮔﺎﻠﻝ",
      "type": "graph",
      "targets": [
        {
          "expr": "rate(http_requests_total[5m])"
        }
      ]
    },
    {
      "title": "ﮒﮒﭦﮔﭘﻠﺑ",
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

## 7. ﮒﻟ۵ﻝ؟۰ﻝ

### 7.1 ﮒﻟ۵ﮔﺕﻠ

**ﻠﻝﺛ؟ﻠﻝ۴ﮔﺕﻠ**:
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

### 7.2 ﮒﻟ۵ﮒﻝﭦ۶

**ﮒﻟ۵ﻝﭦ۶ﮒ،**:
- **Critical**: ﻠﻟ۵ﻝ،ﮒﺏﮒ۳ﻝ?- **Warning**: ﻠﻟ۵ﮒﺏﮔﺏ?- **Info**: ﻛﺟ۰ﮔﺁﻠﻝ۴

**ﮒﻟ۵ﮒ۳ﻝﮔﭖﻝ۷**:
1. ﮔ۴ﮔﭘﮒﻟ۵ﻠﻝ۴
2. ﻝ۰؟ﻟ؟۳ﮒﻟ۵ﻝﭦ۶ﮒ،
3. ﮔ۴ﻝﻝﮔ۶ﻠ۱ﮔﺟ
4. ﮒﮔﮔﺗﮔ؛ﮒﮒ
5. ﮔ۶ﻟ۰ﻛﺟ؟ﮒ۳ﮔ۹ﮔﺛ
6. ﻠ۹ﻟﺁﻛﺟ؟ﮒ۳ﮔﮔ
7. ﻟ؟ﺍﮒﺛﮒ۳ﻝﻟﺟﻝ۷

---

## 8. ﻝﮔ۶ﻝﭨﺑﮔ۳

### 8.1 ﮔ۴ﮒﺕﺕﮔ۲ﮔ?
**ﮔﺁﮔ۴ﮔ۲ﮔ۴ﻠ۰ﺗ**:
- [ ] ﮔ۲ﮔ۴ﻝﺏﭨﻝﭨﻟﭖﮔﭦﻛﺛﺟﻝ۷ﮔﮒ?- [ ] ﮔ۲ﮔ۴ﮒﭦﻝ۷ﻠﻟﺁﺁﮔ۴ﮒﺟ?- [ ] ﮔ۲ﮔ۴ﮒﻟ۵ﮒﮒ?- [ ] ﮔ۲ﮔ۴ﮒ۳ﻛﭨﺛﻝﭘﮔ?
### 8.2 ﮒ؟ﮔﻝﭨﺑﮔ۳

**ﮔﺁﮒ۷ﻝﭨﺑﮔ۳**:
- ﮔﺕﻝﻟﺟﮔﻝﮔ۶ﮔﺍﮔ؟
- ﻛﺙﮒﮒﻟ۵ﻟ۶ﮒ
- ﮔﺑﮔﺍﻝﮔ۶ﻠ۱ﮔﺟ

**ﮔﺁﮔﻝﭨﺑﮔ۳**:
- ﻟﺁﻛﺙﺍﻝﮔ۶ﻟ۵ﻝﻝ?- ﻟﺍﮔﺑﮒﻟ۵ﻠﮒ?- ﻛﺙﮒﻝﮔ۶ﮔ۶ﻟﺛ

---

## 9. ﮔﻠﮔﮔ۴

### 9.1 ﮒﺕﺕﻟ۶ﻠ؟ﻠ۱

**ﻠ؟ﻠ۱1: ﻝﮔ۶ﮔﺍﮔ؟ﻝﺙﭦﮒ۳ﺎ**
```bash
# ﮔ۲ﮔ۴Prometheusﻝﭘﮔ?systemctl status prometheus

# ﮔ۲ﮔ۴ﮔﺍﮔ؟ﻠﻠ?curl http://localhost:9090/api/v1/targets

# ﮔ۲ﮔ۴ﮒﮒ۷ﻝ۸ﭦﻠ?df -h /var/lib/prometheus
```

**ﻠ؟ﻠ۱2: ﮒﻟ۵ﮔ۹ﮒﻠ?*
```bash
# ﮔ۲ﮔ۴AlertManagerﻝﭘﮔ?systemctl status alertmanager

# ﮔ۲ﮔ۴ﮒﻟ۵ﻟ۶ﮒ?curl http://localhost:9090/api/v1/rules

# ﮔ۲ﮔ۴ﻠﻝ۴ﮔﺕﻠ
curl http://localhost:9093/api/v1/receivers
```

**ﻠ؟ﻠ۱3: Grafanaﻠ۱ﮔﺟﮔﮔﺏﻟ؟ﺟﻠ؟**
```bash
# ﮔ۲ﮔ۴Grafanaﻝﭘﮔ?systemctl status grafana-server

# ﮔ۲ﮔ۴ﮔ۴ﮒﺟ?tail -f /var/log/grafana/grafana.log

# ﻠﮒﺁﮔﮒ۰
systemctl restart grafana-server
```

---

## 10. ﮔﻛﺛﺏﮒ؟ﻟﺓ?
### 10.1 ﻝﮔ۶ﻟ؟ﺝﻟ؟۰ﮒﮒ

1. **ﮒ۷ﻠ۱ﮔ?*: ﻟ۵ﻝﮔﮔﮒﺏﻠ؟ﮔﮔ?2. **ﮒﮔﭘﮔ?*: ﮒﺟ،ﻠﮒﻝﺍﮒﮒﮒﭦﻠ؟ﻠ۱
3. **ﮒﻝ۰؟ﮔ?*: ﻠﺟﮒﻟﺁﺁﮔ۴ﮒﮔﺙﮔ?4. **ﮒﺁﮔﻛﺛﮔ?*: ﮔﻛﺝﮒﺁﮔﻛﺛﻝﮒﻟ۵ﻛﺟ۰ﮔﺁ

### 10.2 ﮒﻟ۵ﻟ؟ﺝﻟ؟۰ﮒﮒ

1. **ﮒﻝﭦ۶ﻝ؟۰ﻝ**: ﮔﺗﮔ؟ﻛﺕ۴ﻠﻝ۷ﮒﭦ۵ﮒﻝﭦ۶
2. **ﻠﺟﮒﮒ۹ﻠﺏ**: ﮒﮒﺍﮔﮔﮒﻟ۵
3. **ﮔﻛﺝﻛﺕﻛﺕﮔ?*: ﮒﮒ،ﻟﭘﺏﮒ۳ﻝﻟﺁﮔﻛﺟ۰ﮔ?4. **ﮒﺟ،ﻠﮒﮒﭦ?*: ﮒﭨﭦﻝ،ﮒﺟ،ﻠﮒﮒﭦﮔﭦﮒ?
---

## 11. ﮒﻟﮔﮔ۰?
- [ﻠ۷ﻝﺛﺎﮔﮒ](./DEPLOYMENT_MANUAL.md)
- [ﻠ۲ﻠ۸ﻝﮔ۶ﮔﮒ](./RISK_MONITORING_MANUAL.md)
- [ﻝﭨﺑﮔ۳ﮔﮒ](./MAINTENANCE_MANUAL.md)
- [ﻝﮔ۶ﻠﻝﺛ؟ﮔ۷۰ﮔﺟ](../04_CONFIG_TEMPLATES/monitoring_config_template.yaml)

---

**ﮔﮔ۰۲ﻝﭘﮔ?*: ﮔ۲ﮒﺙﮔﮒ
**ﻛﺕﮔ؛۰ﮒ؟۰ﮔ۴**: 2026-07-02
