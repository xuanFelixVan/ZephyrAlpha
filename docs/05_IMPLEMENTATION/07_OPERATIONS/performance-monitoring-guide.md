---

module_id: PERFORMANCE_MONITORING_GUIDE_001

version: 1.0.0

status: Active

created_date: 2026-04-07

last_updated: 2026-04-07

owner: 运维团队

standard_type: 专业量化机构指南

applicable_scope: ZephyrAlpha性能监控

responsibility:

  - PERFORMANCE_MONITORING操作指南

layer: layer_05
---




# ZephyrAlpha性能监控指南



## 📋 文档概要



**文档职责**: 提供ZephyrAlpha系统的性能监控指标和方法

**适用范围**: 应用监控、数据库监控、系统监控

**前置条件**: 已完成系统部署和监控配置



---



## 🎯 监控目标



### 监控原则



1. **全面覆盖**: 监控所有关键组件和指标

2. **实时告警**: 及时发现和通知问题

3. **可视化展示**: 直观展示监控数据

4. **历史分析**: 支持历史数据分析和趋势预测



---



### 监控维度



| 维度 | 监控内容 | 重要性 |

|------|---------|--------|

| **应用层** | API响应时间、错误率、吞吐量 | 高 |

| **数据库层** | 查询性能、连接数、锁等待 | 高 |

| **缓存层** | 缓存命中率、内存使用 | 中 |

| **系统层** | CPU、内存、磁盘、网络 | 高 |



---



## 📊 监控架构



### 1. 监控组件



```

┌─────────────────────────────────────────────────────────┐

│                    监控架构图                             │

├─────────────────────────────────────────────────────────┤

│                                                          │

│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │

│  │ 应用监控  │    │ 数据库监控 │    │ 系统监控  │          │

│  └─────┬────┘    └─────┬────┘    └─────┬────┘          │

│        │               │                │                │

│        └───────────────┴────────────────┘                │

│                        │                                  │

│                  ┌─────▼─────┐                           │

│                  │ Prometheus │  指标收集                 │

│                  └─────┬─────┘                           │

│                        │                                  │

│                  ┌─────▼─────┐                           │

│                  │  Grafana  │  可视化展示                │

│                  └─────┬─────┘                           │

│                        │                                  │

│                  ┌─────▼─────┐                           │

│                  │Alertmanager│  告警通知                 │

│                  └───────────┘                           │

│                                                          │

└─────────────────────────────────────────────────────────┘

```



---



### 2. 监控工具



| 工具 | 用途 | 端口 |

|------|------|------|

| **Prometheus** | 指标收集和存储 | 9090 |

| **Grafana** | 可视化展示 | 3000 |

| **Alertmanager** | 告警管理 | 9093 |

| **Node Exporter** | 系统指标采集 | 9100 |

| **Postgres Exporter** | 数据库指标采集 | 9187 |

| **Redis Exporter** | Redis指标采集 | 9121 |



---



## 🚀 应用监控



### 1. 应用指标



#### 1.1 请求指标



```python

# app/monitoring/metrics.py

from prometheus_client import Counter, Histogram, Gauge

import time



# 请求计数

REQUEST_COUNT = Counter(

    'http_requests_total',

    'Total HTTP requests',

    ['method', 'endpoint', 'status']

)



# 请求延迟

REQUEST_LATENCY = Histogram(

    'http_request_duration_seconds',

    'HTTP request latency',

    ['method', 'endpoint']

)



# 活跃请求

ACTIVE_REQUESTS = Gauge(

    'http_requests_active',

    'Active HTTP requests',

    ['method', 'endpoint']

)

```



---



#### 1.2 业务指标



```python

# 因子计算指标

FACTOR_CALCULATIONS = Counter(

    'factor_calculations_total',

    'Total factor calculations',

    ['factor_type', 'status']

)



FACTOR_CALCULATION_TIME = Histogram(

    'factor_calculation_duration_seconds',

    'Factor calculation duration',

    ['factor_type']

)



# 投资组合指标

PORTFOLIO_COUNT = Gauge(

    'portfolios_active_total',

    'Total active portfolios'

)



PORTFOLIO_VALUE = Gauge(

    'portfolio_value_total',

    'Total portfolio value',

    ['currency']

)

```



---



#### 1.3 中间件集成



```python

# app/middleware/monitoring.py

from fastapi import Request, Response

from starlette.middleware.base import BaseHTTPMiddleware

import time



class MonitoringMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        start_time = time.time()

        

        # 记录活跃请求

        ACTIVE_REQUESTS.labels(

            method=request.method,

            endpoint=request.url.path

        ).inc()

        

        try:

            response: Response = await call_next(request)

            

            # 记录请求计数

            REQUEST_COUNT.labels(

                method=request.method,

                endpoint=request.url.path,

                status=response.status_code

            ).inc()

            

            # 记录请求延迟

            REQUEST_LATENCY.labels(

                method=request.method,

                endpoint=request.url.path

            ).observe(time.time() - start_time)

            

            return response

            

        finally:

            # 减少活跃请求计数

            ACTIVE_REQUESTS.labels(

                method=request.method,

                endpoint=request.url.path

            ).dec()

```



---



### 2. 应用健康检查



#### 2.1 健康检查端点



```python

# app/api/health.py

from fastapi import APIRouter, HTTPException

from datetime import datetime

import psutil

import redis

from sqlalchemy import text



router = APIRouter()



@router.get("/health")

async def health_check():

    checks = {

        "status": "healthy",

        "timestamp": datetime.utcnow().isoformat(),

        "checks": {}

    }

    

    # 检查数据库

    try:

        db.execute(text("SELECT 1"))

        checks["checks"]["database"] = "healthy"

    except Exception as e:

        checks["checks"]["database"] = f"unhealthy: {str(e)}"

        checks["status"] = "unhealthy"

    

    # 检查Redis

    try:

        redis_client = redis.Redis()

        redis_client.ping()

        checks["checks"]["redis"] = "healthy"

    except Exception as e:

        checks["checks"]["redis"] = f"unhealthy: {str(e)}"

        checks["status"] = "unhealthy"

    

    # 检查系统资源

    checks["checks"]["cpu"] = f"{psutil.cpu_percent()}%"

    checks["checks"]["memory"] = f"{psutil.virtual_memory().percent}%"

    checks["checks"]["disk"] = f"{psutil.disk_usage('/').percent}%"

    

    if checks["status"] == "unhealthy":

        raise HTTPException(status_code=503, detail=checks)

    

    return checks

```



---



#### 2.2 就绪检查端点



```python

@router.get("/ready")

async def readiness_check():

    checks = {

        "status": "ready",

        "timestamp": datetime.utcnow().isoformat(),

        "checks": {}

    }

    

    # 检查数据库连接池

    try:

        pool_status = db.get_pool_status()

        checks["checks"]["database_pool"] = {

            "size": pool_status.size,

            "checked_in": pool_status.checkedin,

            "overflow": pool_status.overflow

        }

    except Exception as e:

        checks["checks"]["database_pool"] = f"error: {str(e)}"

        checks["status"] = "not_ready"

    

    # 检查缓存连接

    try:

        redis_info = redis_client.info()

        checks["checks"]["redis"] = {

            "connected_clients": redis_info["connected_clients"],

            "used_memory": redis_info["used_memory_human"]

        }

    except Exception as e:

        checks["checks"]["redis"] = f"error: {str(e)}"

        checks["status"] = "not_ready"

    

    if checks["status"] == "not_ready":

        raise HTTPException(status_code=503, detail=checks)

    

    return checks

```



---



## 💾 数据库监控



### 1. 数据库指标



#### 1.1 连接指标



```sql

-- 活跃连接数

SELECT count(*) AS active_connections

FROM pg_stat_activity;



-- 连接状态分布

SELECT 

    state,

    count(*) AS count

FROM pg_stat_activity

GROUP BY state;



-- 连接来源分布

SELECT 

    client_addr,

    count(*) AS count

FROM pg_stat_activity

GROUP BY client_addr

ORDER BY count DESC;

```



---



#### 1.2 查询性能指标



```sql

-- 慢查询统计

SELECT 

    query,

    calls,

    total_time,

    mean_time,

    max_time

FROM pg_stat_statements

ORDER BY total_time DESC

LIMIT 10;



-- 查询缓存命中率

SELECT 

    sum(heap_blks_read) AS heap_read,

    sum(heap_blks_hit) AS heap_hit,

    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) AS ratio

FROM pg_statio_user_tables;



-- 索引使用率

SELECT 

    schemaname,

    tablename,

    indexname,

    idx_scan,

    idx_tup_read,

    idx_tup_fetch

FROM pg_stat_user_indexes

ORDER BY idx_scan ASC;

```



---



#### 1.3 锁等待指标



```sql

-- 锁等待统计

SELECT 

    locktype,

    mode,

    count(*) AS count

FROM pg_locks

WHERE granted = false

GROUP BY locktype, mode;



-- 锁等待详情

SELECT 

    pid,

    now() - pg_stat_activity.query_start AS duration,

    query,

    state

FROM pg_stat_activity

WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';

```



---



### 2. 数据库监控配置



#### 2.1 Postgres Exporter配置



```yaml

# prometheus/postgres_exporter.yml

datasource:

  host: localhost

  port: 5432

  user: postgres

  password: ${DB_PASSWORD}

  database: zephyr_alpha



queries:

  - name: pg_stat_activity

    query: "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"

    metrics:

      - active_queries:

          usage: "GAUGE"

          description: "Number of active queries"

```



---



#### 2.2 Prometheus配置



```yaml

# prometheus/prometheus.yml

scrape_configs:

  - job_name: 'postgres'

    static_configs:

      - targets: ['localhost:9187']

    relabel_configs:

      - source_labels: [__address__]

        target_label: instance

```



---



## 🖥️ 系统监控



### 1. 系统指标



#### 1.1 CPU指标



```bash

# CPU使用率

top -b -n 1 | grep "Cpu(s)"



# CPU负载

cat /proc/loadavg



# CPU核心数

nproc



# CPU详细信息

lscpu

```



---



#### 1.2 内存指标



```bash

# 内存使用

free -h



# 内存详细信息

cat /proc/meminfo



# 内存使用趋势

vmstat 1 10



# 内存映射

pmap -x $(pgrep -f zephyr)

```



---



#### 1.3 磁盘指标



```bash

# 磁盘使用

df -h



# 磁盘IO

iostat -x 1



# 磁盘性能

hdparm -t /dev/sda



# 文件系统信息

tune2fs -l /dev/sda1

```



---



#### 1.4 网络指标



```bash

# 网络连接

netstat -an | grep ESTABLISHED



# 网络流量

ifconfig eth0



# 网络延迟

ping -c 10 target_host



# 网络带宽

iperf3 -c target_host

```



---



### 2. 系统监控配置



#### 2.1 Node Exporter配置



```bash

# 安装Node Exporter

wget https://github.com/prometheus/node_exporter/releases/download/v1.3.1/node_exporter-1.3.1.linux-amd64.tar.gz

tar xzf node_exporter-1.3.1.linux-amd64.tar.gz

cd node_exporter-1.3.1.linux-amd64



# 启动Node Exporter

./node_exporter --web.listen-address=:9100



# 配置systemd服务

cat > /etc/systemd/system/node_exporter.service <<EOF

[Unit]

Description=Node Exporter

After=network.target



[Service]

Type=simple

User=prometheus

ExecStart=/usr/local/bin/node_exporter

Restart=on-failure



[Install]

WantedBy=multi-user.target

EOF



systemctl daemon-reload

systemctl start node_exporter

systemctl enable node_exporter

```



---



#### 2.2 Prometheus配置



```yaml

# prometheus/prometheus.yml

scrape_configs:

  - job_name: 'node'

    static_configs:

      - targets: ['localhost:9100']

    relabel_configs:

      - source_labels: [__address__]

        target_label: instance

```



---



## 📈 Grafana可视化



### 1. Grafana配置



#### 1.1 数据源配置



```yaml

# grafana/provisioning/datasources/prometheus.yml

apiVersion: 1

datasources:

  - name: Prometheus

    type: prometheus

    access: proxy

    url: http://localhost:9090

    isDefault: true

    editable: false

```



---



#### 1.2 Dashboard配置



```json

{

  "dashboard": {

    "title": "ZephyrAlpha监控面板",

    "panels": [

      {

        "title": "API响应时间",

        "type": "graph",

        "targets": [

          {

            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",

            "legendFormat": "P95"

          },

          {

            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",

            "legendFormat": "P99"

          }

        ]

      },

      {

        "title": "请求速率",

        "type": "graph",

        "targets": [

          {

            "expr": "rate(http_requests_total[5m])",

            "legendFormat": "{{method}} {{endpoint}}"

          }

        ]

      },

      {

        "title": "错误率",

        "type": "graph",

        "targets": [

          {

            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m])",

            "legendFormat": "Error Rate"

          }

        ]

      }

    ]

  }

}

```



---



### 2. 常用Dashboard



#### 2.1 应用监控Dashboard



- API响应时间（P50, P95, P99）

- 请求速率（QPS）

- 错误率

- 活跃请求数

- 业务指标（因子计算、投资组合等）



#### 2.2 数据库监控Dashboard



- 数据库连接数

- 查询性能

- 慢查询统计

- 锁等待

- 缓存命中率



#### 2.3 系统监控Dashboard



- CPU使用率

- 内存使用率

- 磁盘使用率

- 网络流量

- 系统负载



---



## 🚨 告警配置



### 1. 告警规则



#### 1.1 应用告警规则



```yaml

# prometheus/alert_rules.yml

groups:

  - name: application_alerts

    rules:

      - alert: HighErrorRate

        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05

        for: 5m

        labels:

          severity: warning

        annotations:

          summary: "高错误率告警"

          description: "错误率超过5%，当前值: {{ $value }}"

      

      - alert: HighLatency

        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1

        for: 5m

        labels:

          severity: warning

        annotations:

          summary: "高延迟告警"

          description: "P95延迟超过1秒，当前值: {{ $value }}秒"

      

      - alert: ServiceDown

        expr: up{job="zephyr"} == 0

        for: 1m

        labels:

          severity: critical

        annotations:

          summary: "服务不可用"

          description: "ZephyrAlpha服务已停止"

```



---



#### 1.2 数据库告警规则



```yaml

  - name: database_alerts

    rules:

      - alert: HighConnectionCount

        expr: pg_stat_activity_count > 100

        for: 5m

        labels:

          severity: warning

        annotations:

          summary: "数据库连接数过高"

          description: "当前连接数: {{ $value }}"

      

      - alert: SlowQuery

        expr: pg_stat_statements_mean_time_seconds > 1

        for: 5m

        labels:

          severity: warning

        annotations:

          summary: "慢查询告警"

          description: "平均查询时间: {{ $value }}秒"

```



---



#### 1.3 系统告警规则



```yaml

  - name: system_alerts

    rules:

      - alert: HighCPUUsage

        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80

        for: 5m

        labels:

          severity: warning

        annotations:

          summary: "CPU使用率过高"

          description: "CPU使用率: {{ $value }}%"

      

      - alert: HighMemoryUsage

        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 80

        for: 5m

        labels:

          severity: warning

        annotations:

          summary: "内存使用率过高"

          description: "内存使用率: {{ $value }}%"

      

      - alert: DiskSpaceLow

        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 20

        for: 5m

        labels:

          severity: critical

        annotations:

          summary: "磁盘空间不足"

          description: "剩余磁盘空间: {{ $value }}%"

```



---



### 2. 告警通知



#### 2.1 Alertmanager配置



```yaml

# alertmanager/alertmanager.yml

global:

  resolve_timeout: 5m

  smtp_smarthost: 'smtp.gmail.com:587'

  smtp_from: 'alert@zephyr-alpha.com'

  smtp_auth_username: 'alert@zephyr-alpha.com'

  smtp_auth_password: 'app_password'



route:

  group_by: ['alertname', 'severity']

  group_wait: 10s

  group_interval: 10s

  repeat_interval: 12h

  receiver: 'team-email'

  

  routes:

    - match:

        severity: critical

      receiver: 'team-email-critical'

    

    - match:

        severity: warning

      receiver: 'team-email'



receivers:

  - name: 'team-email'

    email_configs:

      - to: 'team@zephyr-alpha.com'

        send_resolved: true

  

  - name: 'team-email-critical'

    email_configs:

      - to: 'team@zephyr-alpha.com'

        send_resolved: true

    webhook_configs:

      - url: 'https://hooks.slack.com/services/xxx'

        send_resolved: true

```



---



## 📊 监控最佳实践



### 1. 监控指标选择



**RED方法**（适用于请求驱动服务）:

- **Rate**: 请求速率

- **Errors**: 错误率

- **Duration**: 请求持续时间



**USE方法**（适用于资源）:

- **Utilization**: 资源使用率

- **Saturation**: 资源饱和度

- **Errors**: 错误数



---



### 2. 告警最佳实践



- 设置合理的告警阈值

- 避免告警疲劳

- 提供可操作的告警信息

- 建立告警分级机制

- 定期审查告警规则



---



## 🔗 相关文档



- 性能调优指南

- 故障诊断指南

- 系统部署指南

- 环境配置指南



---



**文档版本**: v1.0.0 | **创建日期**: 2026-04-07 | **状态**: Active

