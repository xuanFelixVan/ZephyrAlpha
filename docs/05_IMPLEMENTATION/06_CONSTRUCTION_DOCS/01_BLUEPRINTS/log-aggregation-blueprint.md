---

module_id: LOG_AGGREGATION_001

version: 1.0.0

status: Active

created_date: 2026-04-07

last_updated: 2026-04-07

owner: 首席文档架构师

responsibility:

  - 日志收集

  - 日志聚合

  - 日志搜索

  - 日志分析

standard_type: 专业量化机构蓝图

compliance_level: 专业标准

layer: layer_05

---



# 日志聚合蓝图



> **核心职责**: 提供统一的日志收集、聚合、搜索和分析能力，支持系统监控和问题排查

> **职责边界**: 

> - ✅ 本文档负责：日志收集、聚合、搜索、分析

> - ❌ 本文档不负责：指标监控（由Prometheus负责）、告警通知（由AlertManager负责）



## 核心定位



负责日志聚合模块的设计与构建，提供集中式日志管理，支持多源日志收集、实时搜索、可视化分析，帮助快速定位和解决问题。



## 接口与契约（蓝图终稿）



### API 契约索引



本模块遵循系统统一接口规范，详见 `API_Contract.md`。



### 核心接口定义



| 接口名称 | 索引 | 说明 |

|----------|------|------|

| 日志采集/推送 | API.LOG.001 | 推送结构化日志到聚合系统 |

| 日志检索查询 | API.LOG.002 | 按时间/字段过滤检索日志 |

| 告警联动事件 | API.LOG.003 | 告警触发与事件记录 |



### 数据格式规范



- 输入格式: `log_entry`（service/level/timestamp/message/fields）

- 输出格式: `search_results/alert_events`

- 时间戳格式: ISO 8601 UTC



## 验收标准（可检查）



- 能完成至少 1 条日志端到端：采集→存储→可检索查询，并支持按时间范围与关键字段过滤。

- 关键告警规则可触发并产生可追溯事件（包含原因/阈值/时间/来源）。

- 对外接口/事件能在 `API_Contract.md` 中定位到契约入口（或在“已知限制”列出未闭合项）。



## 已知限制



- 日志字段规范与留存策略需要随业务模块扩展统一；实施阶段需固化脱敏规则、留存周期与成本控制策略，并回填契约真源。



## 设计目标



### 主要目标



1. **日志收集**: 支持多种日志源的统一收集

2. **日志聚合**: 集中存储和管理所有日志

3. **日志搜索**: 提供快速、灵活的日志搜索能力

4. **日志分析**: 支持日志统计、趋势分析、异常检测



### 质量目标



- 日志收集延迟: <5s

- 日志搜索响应: <1s

- 日志存储可靠性: 99.99%

- 日志完整性: 100%



## 开源方案选型



### 推荐方案: Loki + Grafana



| 属性 | 详情 |

|------|------|

| **GitHub** | https://github.com/grafana/loki |

| **Stars** | 23,000+ |

| **License** | AGPL-3.0 |

| **语言** | Go |

| **特点** | 轻量级日志聚合，不建立索引 |



**选择理由**:

1. **轻量级**: 不建立全文索引，存储成本低

2. **与Grafana集成**: 已在监控系统中使用

3. **与Prometheus集成**: 统一可观测性平台

4. **配置简单**: Docker一键部署

5. **个人友好**: 适合个人开发者使用



### 备选方案



| 项目 | Stars | 特点 | 推荐度 |

|------|-------|------|--------|

| **ELK Stack** | - | 企业级日志方案 | ⭐⭐⭐⭐⭐ |

| **Fluentd** | 13k+ | 日志收集框架 | ⭐⭐⭐⭐ |



## 核心功能设计



### 1. 日志收集模块



```python

import logging

import json

from datetime import datetime

from typing import Dict, Any

import requests



class LokiLogHandler(logging.Handler):

    """Loki日志处理器"""

    

    def __init__(

        self,

        loki_url: str = "http://loki:3100",

        labels: Dict[str, str] = None

    ):

        super().__init__()

        self.loki_url = loki_url

        self.labels = labels or {"service": "unknown"}

    

    def emit(self, record: logging.LogRecord):

        """发送日志到Loki"""

        try:

            log_entry = {

                "streams": [

                    {

                        "stream": {

                            **self.labels,

                            "level": record.levelname,

                            "logger": record.name

                        },

                        "values": [

                            [

                                str(int(datetime.now().timestamp() * 1e9)),

                                json.dumps({

                                    "message": record.getMessage(),

                                    "timestamp": datetime.now().isoformat(),

                                    "level": record.levelname,

                                    "logger": record.name,

                                    "module": record.module,

                                    "function": record.funcName,

                                    "line": record.lineno

                                })

                            ]

                        ]

                    }

                ]

            }

            

            requests.post(

                f"{self.loki_url}/loki/api/v1/push",

                json=log_entry,

                headers={"Content-Type": "application/json"}

            )

        except Exception as e:

            print(f"Failed to send log to Loki: {e}")





class StructuredLogger:

    """结构化日志记录器"""

    

    def __init__(self, service_name: str, loki_url: str = "http://loki:3100"):

        self.logger = logging.getLogger(service_name)

        self.logger.setLevel(logging.DEBUG)

        

        handler = LokiLogHandler(

            loki_url=loki_url,

            labels={"service": service_name}

        )

        self.logger.addHandler(handler)

    

    def info(self, message: str, **kwargs):

        """记录INFO日志"""

        self.logger.info(message, extra=kwargs)

    

    def error(self, message: str, **kwargs):

        """记录ERROR日志"""

        self.logger.error(message, extra=kwargs)

    

    def warning(self, message: str, **kwargs):

        """记录WARNING日志"""

        self.logger.warning(message, extra=kwargs)

    

    def debug(self, message: str, **kwargs):

        """记录DEBUG日志"""

        self.logger.debug(message, extra=kwargs)

    

    def log_trade(self, trade_data: Dict[str, Any]):

        """记录交易日志"""

        self.info(

            "Trade executed",

            trade_type=trade_data.get("type"),

            symbol=trade_data.get("symbol"),

            quantity=trade_data.get("quantity"),

            price=trade_data.get("price"),

            **trade_data

        )

    

    def log_signal(self, signal_data: Dict[str, Any]):

        """记录信号日志"""

        self.info(

            "Signal generated",

            signal_type=signal_data.get("type"),

            symbol=signal_data.get("symbol"),

            strength=signal_data.get("strength"),

            **signal_data

        )

```



### 2. 日志搜索模块



```python

from typing import List, Dict, Any, Optional

from datetime import datetime, timedelta

import requests



class LogSearcher:

    """日志搜索器"""

    

    def __init__(self, loki_url: str = "http://loki:3100"):

        self.loki_url = loki_url

    

    def search(

        self,

        query: str,

        start_time: datetime = None,

        end_time: datetime = None,

        limit: int = 100

    ) -> List[Dict[str, Any]]:

        """搜索日志"""

        if not start_time:

            start_time = datetime.now() - timedelta(hours=1)

        if not end_time:

            end_time = datetime.now()

        

        params = {

            "query": query,

            "start": int(start_time.timestamp() * 1e9),

            "end": int(end_time.timestamp() * 1e9),

            "limit": limit

        }

        

        response = requests.get(

            f"{self.loki_url}/loki/api/v1/query_range",

            params=params

        )

        

        return self._parse_response(response.json())

    

    def search_by_service(

        self,

        service_name: str,

        start_time: datetime = None,

        end_time: datetime = None

    ) -> List[Dict[str, Any]]:

        """按服务搜索日志"""

        query = f'{{service="{service_name}"}}'

        return self.search(query, start_time, end_time)

    

    def search_by_level(

        self,

        level: str,

        start_time: datetime = None,

        end_time: datetime = None

    ) -> List[Dict[str, Any]]:

        """按级别搜索日志"""

        query = f'{{level="{level}"}}'

        return self.search(query, start_time, end_time)

    

    def search_errors(

        self,

        start_time: datetime = None,

        end_time: datetime = None

    ) -> List[Dict[str, Any]]:

        """搜索错误日志"""

        return self.search_by_level("ERROR", start_time, end_time)

    

    def _parse_response(self, response: Dict) -> List[Dict[str, Any]]:

        """解析响应"""

        results = []

        

        for stream in response.get("data", {}).get("result", []):

            labels = stream.get("stream", {})

            

            for value in stream.get("values", []):

                timestamp, log = value

                

                try:

                    log_data = json.loads(log)

                except json.JSONDecodeError:

                    log_data = {"message": log}

                

                results.append({

                    "timestamp": datetime.fromtimestamp(int(timestamp) / 1e9),

                    "labels": labels,

                    **log_data

                })

        

        return results

```



### 3. 日志分析模块



```python

from collections import Counter

from typing import Dict, List

import pandas as pd



class LogAnalyzer:

    """日志分析器"""

    

    def __init__(self, searcher: LogSearcher):

        self.searcher = searcher

    

    def analyze_error_patterns(

        self,

        start_time: datetime = None,

        end_time: datetime = None

    ) -> Dict[str, Any]:

        """分析错误模式"""

        errors = self.searcher.search_errors(start_time, end_time)

        

        error_messages = [e.get("message", "") for e in errors]

        error_counts = Counter(error_messages)

        

        return {

            "total_errors": len(errors),

            "unique_errors": len(error_counts),

            "top_errors": error_counts.most_common(10),

            "errors_by_service": self._group_by(errors, "service"),

            "errors_by_hour": self._group_by_hour(errors)

        }

    

    def analyze_service_health(

        self,

        service_name: str,

        start_time: datetime = None,

        end_time: datetime = None

    ) -> Dict[str, Any]:

        """分析服务健康度"""

        logs = self.searcher.search_by_service(

            service_name, start_time, end_time

        )

        

        levels = [l.get("level", "INFO") for l in logs]

        level_counts = Counter(levels)

        

        return {

            "service": service_name,

            "total_logs": len(logs),

            "level_distribution": dict(level_counts),

            "error_rate": level_counts.get("ERROR", 0) / max(len(logs), 1),

            "warning_rate": level_counts.get("WARNING", 0) / max(len(logs), 1)

        }

    

    def analyze_trade_activity(

        self,

        start_time: datetime = None,

        end_time: datetime = None

    ) -> Dict[str, Any]:

        """分析交易活动"""

        trade_logs = self.searcher.search(

            'trade_type=~".*"',

            start_time, end_time

        )

        

        return {

            "total_trades": len(trade_logs),

            "trades_by_symbol": self._group_by(trade_logs, "symbol"),

            "trades_by_type": self._group_by(trade_logs, "trade_type"),

            "trades_by_hour": self._group_by_hour(trade_logs)

        }

    

    def detect_anomalies(

        self,

        service_name: str,

        window_hours: int = 1

    ) -> List[Dict[str, Any]]:

        """检测异常"""

        end_time = datetime.now()

        start_time = end_time - timedelta(hours=window_hours)

        

        current_errors = len(self.searcher.search_by_service(

            service_name, start_time, end_time

        ))

        

        baseline_start = start_time - timedelta(hours=window_hours)

        baseline_errors = len(self.searcher.search_by_service(

            service_name, baseline_start, start_time

        ))

        

        anomalies = []

        

        if baseline_errors > 0:

            error_increase = (current_errors - baseline_errors) / baseline_errors

            

            if error_increase > 0.5:

                anomalies.append({

                    "type": "error_spike",

                    "service": service_name,

                    "current_errors": current_errors,

                    "baseline_errors": baseline_errors,

                    "increase_rate": error_increase,

                    "detected_at": datetime.now().isoformat()

                })

        

        return anomalies

    

    def _group_by(self, items: List[Dict], key: str) -> Dict[str, int]:

        """按字段分组"""

        return dict(Counter(item.get(key, "unknown") for item in items))

    

    def _group_by_hour(self, items: List[Dict]) -> Dict[str, int]:

        """按小时分组"""

        hours = []

        for item in items:

            ts = item.get("timestamp", datetime.now())

            if isinstance(ts, datetime):

                hours.append(ts.strftime("%Y-%m-%d %H:00"))

        

        return dict(Counter(hours))

```



### 4. 日志告警模块



```python

from typing import Callable, List

import time

import threading



class LogAlerter:

    """日志告警器"""

    

    def __init__(self, searcher: LogSearcher):

        self.searcher = searcher

        self.alert_rules: List[Dict] = []

        self.running = False

    

    def add_alert_rule(

        self,

        name: str,

        query: str,

        threshold: int,

        window_minutes: int,

        callback: Callable

    ):

        """添加告警规则"""

        self.alert_rules.append({

            "name": name,

            "query": query,

            "threshold": threshold,

            "window_minutes": window_minutes,

            "callback": callback,

            "last_triggered": None

        })

    

    def start_monitoring(self, interval_seconds: int = 60):

        """开始监控"""

        self.running = True

        

        def monitor():

            while self.running:

                self._check_rules()

                time.sleep(interval_seconds)

        

        thread = threading.Thread(target=monitor, daemon=True)

        thread.start()

    

    def stop_monitoring(self):

        """停止监控"""

        self.running = False

    

    def _check_rules(self):

        """检查告警规则"""

        for rule in self.alert_rules:

            end_time = datetime.now()

            start_time = end_time - timedelta(minutes=rule["window_minutes"])

            

            results = self.searcher.search(

                rule["query"],

                start_time, end_time

            )

            

            if len(results) >= rule["threshold"]:

                if rule["last_triggered"] is None or \

                   (datetime.now() - rule["last_triggered"]).total_seconds() > 300:

                    

                    alert = {

                        "rule_name": rule["name"],

                        "count": len(results),

                        "threshold": rule["threshold"],

                        "triggered_at": datetime.now().isoformat(),

                        "sample_logs": results[:5]

                    }

                    

                    rule`"callback"`

                    rule["last_triggered"] = datetime.now()

```



## 部署架构



### Docker Compose部署



```yaml

version: '3.8'



services:

  loki:

    image: grafana/loki:latest

    ports:

      - "3100:3100"

    volumes:

      - ./loki-config.yml:/etc/loki/local-config.yaml

      - loki_data:/loki

    command: -config.file=/etc/loki/local-config.yaml

    restart: unless-stopped

  

  promtail:

    image: grafana/promtail:latest

    volumes:

      - /var/log:/var/log

      - ./promtail-config.yml:/etc/promtail/config.yml

    command: -config.file=/etc/promtail/config.yml

    restart: unless-stopped

  

  grafana:

    image: grafana/grafana:latest

    ports:

      - "3000:3000"

    environment:

      - GF_AUTH_ANONYMOUS_ENABLED=true

      - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin

    volumes:

      - grafana_data:/var/lib/grafana

      - ./grafana-dashboards:/etc/grafana/provisioning/dashboards

    restart: unless-stopped



volumes:

  loki_data:

  grafana_data:

```



### Loki配置



```yaml

# loki-config.yml

auth_enabled: false



server:

  http_listen_port: 3100



ingester:

  lifecycler:

    address: 127.0.0.1

    ring:

      kvstore:

        store: inmemory

      replication_factor: 1

    final_sleep: 0s

  chunk_idle_period: 5m

  chunk_retain_period: 30s



schema_config:

  configs:

    - from: 2020-10-24

      store: boltdb-shipper

      object_store: filesystem

      schema: v11

      index:

        prefix: index_

        period: 24h



storage_config:

  boltdb_shipper:

    active_index_directory: /loki/boltdb-shipper-active

    cache_location: /loki/boltdb-shipper-cache

    cache_ttl: 24h

  filesystem:

    directory: /loki/chunks



limits_config:

  enforce_metric_name: false

  reject_old_samples: true

  reject_old_samples_max_age: 168h



chunk_store_config:

  max_look_back_period: 0s



table_manager:

  retention_deletes_enabled: true

  retention_period: 168h

```



### Promtail配置



```yaml

# promtail-config.yml

server:

  http_listen_port: 9080

  grpc_listen_port: 0



positions:

  filename: /tmp/positions.yaml



clients:

  - url: http://loki:3100/loki/api/v1/push



scrape_configs:

  - job_name: system

    static_configs:

      - targets:

          - localhost

        labels:

          job: varlogs

          __path__: /var/log/*log

  

  - job_name: docker

    docker_sd_configs:

      - host: unix:///var/run/docker.sock

        refresh_interval: 5s

    relabel_configs:

      - source_labels: ['__meta_docker_container_name']

        target_label: 'container'

```



## 与现有系统集成



### 1. 与Python应用集成



```python

import logging

from log_aggregation import StructuredLogger



logger = StructuredLogger(

    service_name="data-service",

    loki_url="http://loki:3100"

)



logger.info("Service started", version="1.0.0")



logger.log_trade({

    "type": "BUY",

    "symbol": "AAPL",

    "quantity": 100,

    "price": 150.25

})



try:

    result = risky_operation()

except Exception as e:

    logger.error(

        "Operation failed",

        error=str(e),

        operation="risky_operation"

    )

```



### 2. 与Grafana可视化集成



```json

{

  "dashboard": {

    "title": "Log Analysis Dashboard",

    "panels": [

      {

        "title": "Error Rate",

        "type": "graph",

        "targets": [

          {

            "expr": "sum(rate({level=\"ERROR\"}[5m]))",

            "refId": "A"

          }

        ]

      },

      {

        "title": "Logs by Service",

        "type": "piechart",

        "targets": [

          {

            "expr": "sum by (service) (count_over_time({service=~\".*\"}[1h]))",

            "refId": "A"

          }

        ]

      }

    ]

  }

}

```



### 3. 与告警系统集成



```python

from log_aggregation import LogAlerter, LogSearcher



def send_alert(alert):

    print(f"ALERT: {alert['rule_name']} - {alert['count']} occurrences")



searcher = LogSearcher("http://loki:3100")

alerter = LogAlerter(searcher)



alerter.add_alert_rule(

    name="High Error Rate",

    query='{level="ERROR"}',

    threshold=10,

    window_minutes=5,

    callback=send_alert

)



alerter.start_monitoring()

```



## 实施计划



### 阶段1: 基础部署 (Week 1)



| 任务 | 工时 | 负责人 | 交付物 |

|------|------|--------|--------|

| Docker环境搭建 | 2h | 开发者 | Docker Compose配置 |

| Loki部署 | 4h | 开发者 | 运行中的日志系统 |

| Promtail配置 | 4h | 开发者 | 日志收集配置 |

| 测试验证 | 2h | 开发者 | 测试报告 |



### 阶段2: 应用集成 (Week 2)



| 任务 | 工时 | 负责人 | 交付物 |

|------|------|--------|--------|

| Python日志集成 | 8h | 开发者 | 日志处理器 |

| Grafana仪表盘 | 4h | 开发者 | 可视化仪表盘 |

| 日志搜索功能 | 4h | 开发者 | 搜索API |



### 阶段3: 高级功能 (Week 3)



| 任务 | 工时 | 负责人 | 交付物 |

|------|------|--------|--------|

| 日志分析功能 | 8h | 开发者 | 分析模块 |

| 异常检测 | 4h | 开发者 | 检测规则 |

| 告警集成 | 4h | 开发者 | 告警配置 |



## 性能指标



| 指标 | 目标值 | 测量方法 |

|------|--------|---------|

| **日志收集延迟** | <5s | 日志产生到存储时间 |

| **搜索响应时间** | <1s | 查询延迟 |

| **存储效率** | 10:1 | 压缩比 |

| **系统可用性** | 99.9% | 月度可用性统计 |



## 成本估算



| 项目 | 开源方案成本 | 商业方案成本 |

|------|-------------|-------------|

| **软件许可** | $0 | $30k+/年 |

| **部署运维** | 自行维护 | 供应商支持 |

| **硬件资源** | 2核4G | 云服务费用 |

| **存储成本** | 本地存储 | 云存储费用 |

| **总成本** | $0 + 运维时间 | $30k+/年 |



---



**文档版本**: v1.0.0

**创建日期**: 2026-04-07

**最后更新**: 2026-04-07

**状态**: Active

