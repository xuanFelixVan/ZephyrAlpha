---
module_id: AUDIT_LOGGING_001_8632
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
- 安全审计日志
standard_type: 专业量化机构蓝图
compliance_level: 专业标准
layer: layer_05
---



# 审计日志蓝图



> **核心职责**: 提供全面的审计日志记录和分析能力，支持安全审计、操作审计、合规审计

> **职责边界**: 

> - ✅ 本文档负责：审计日志记录、审计日志分析、合规检查

> - ❌ 本文档不负责：日志聚合（由日志聚合模块负责）、安全扫描（由安全扫描模块负责）



## 核心定位



负责审计日志模块的设计与构建，提供全面的审计日志记录和分析能力，支持安全审计、操作审计、合规审计，确保系统操作的可追溯性和合规性。



## 接口与契约（蓝图终稿）



- 全库 API 与事件约定真源：`API_Contract.md`。审计日志事件模型（主体、动作、资源、结果、追踪 id、时间戳）与查询/导出接口口径以该真源为准。



## 验收标准（可检查）



- 能记录至少 1 类关键事件（登录/权限变更/配置变更/交易操作中的任一），并可检索到完整字段（主体/时间/资源/结果）。

- 审计日志不可篡改口径明确（例如 WORM/签名/只追加存储之一），且有可检查的实现约束说明。

- 对外查询/导出接口能在 `API_Contract.md` 中定位到契约入口（或在“已知限制”列出未闭合项）。



## 已知限制



- 合规要求（留存周期、脱敏规则、访问审批）随地区/业务变化；落地阶段需固化策略并回填契约真源与运行手册。



## 设计目标



### 主要目标



1. **安全审计**: 记录安全相关操作（登录、权限变更、敏感数据访问）

2. **操作审计**: 记录关键业务操作（交易、配置变更、数据修改）

3. **合规审计**: 记录合规相关操作（数据访问、审批流程、审计报告）

4. **审计分析**: 提供审计日志查询、统计、告警功能



### 质量目标



- 审计日志完整性: 100%

- 审计日志准确性: 100%

- 审计日志查询性能: < 1秒

- 审计日志保留期: ≥ 90天



## 开源方案选型



### 推荐方案: Loki + Grafana



| 属性 | 详情 |

|------|------|

| **GitHub** | https://github.com/grafana/loki |

| **Stars** | 23,000+ |

| **License** | AGPL 3.0 |

| **语言** | Go |

| **特点** | 轻量级日志聚合系统，与Grafana完美集成 |



**选择理由**:

1. **轻量级**: 资源占用少，适合个人项目

2. **易于部署**: 单二进制文件，Docker支持

3. **Grafana集成**: 可视化查询和分析

4. **成本低**: 不需要全文索引，存储成本低

5. **查询灵活**: 支持LogQL查询语言

6. **个人友好**: 免费开源，适合个人使用



## 核心功能设计



### 1. 审计日志记录模块



```python

import json

from datetime import datetime

from typing import Dict, Any, Optional

from enum import Enum



class AuditEventType(Enum):

    """审计事件类型"""

    LOGIN = "login"

    LOGOUT = "logout"

    PERMISSION_CHANGE = "permission_change"

    DATA_ACCESS = "data_access"

    DATA_MODIFY = "data_modify"

    CONFIG_CHANGE = "config_change"

    TRANSACTION = "transaction"

    APPROVAL = "approval"



class AuditLogger:

    """审计日志记录器"""

    

    def __init__(self, loki_url: str = "http://localhost:3100"):

        self.loki_url = loki_url

        self.labels = {

            "job": "audit-logging",

            "environment": "production"

        }

    

    def log_event(

        self,

        event_type: AuditEventType,

        user_id: str,

        action: str,

        resource: str,

        details: Dict[str, Any] = None,

        ip_address: str = None,

        user_agent: str = None,

        status: str = "success"

    ):

        """记录审计事件"""

        audit_entry = {

            "timestamp": datetime.now().isoformat(),

            "event_type": event_type.value,

            "user_id": user_id,

            "action": action,

            "resource": resource,

            "details": details or {},

            "ip_address": ip_address,

            "user_agent": user_agent,

            "status": status

        }

        

        self._send_to_loki(audit_entry)

        

        return audit_entry

    

    def log_security_event(

        self,

        event_type: str,

        user_id: str,

        details: Dict[str, Any],

        severity: str = "medium"

    ):

        """记录安全审计事件"""

        return self.log_event(

            event_type=AuditEventType[event_type.upper()],

            user_id=user_id,

            action="security_event",

            resource="security",

            details={

                **details,

                "severity": severity

            }

        )

    

    def log_operation_event(

        self,

        operation: str,

        user_id: str,

        resource: str,

        before_value: Any = None,

        after_value: Any = None

    ):

        """记录操作审计事件"""

        return self.log_event(

            event_type=AuditEventType.DATA_MODIFY,

            user_id=user_id,

            action=operation,

            resource=resource,

            details={

                "before": before_value,

                "after": after_value

            }

        )

    

    def log_compliance_event(

        self,

        compliance_type: str,

        user_id: str,

        resource: str,

        details: Dict[str, Any]

    ):

        """记录合规审计事件"""

        return self.log_event(

            event_type=AuditEventType.APPROVAL,

            user_id=user_id,

            action="compliance_check",

            resource=resource,

            details={

                "compliance_type": compliance_type,

                **details

            }

        )

    

    def _send_to_loki(self, entry: Dict):

        """发送到Loki"""

        import requests

        

        headers = {"Content-Type": "application/json"}

        

        payload = {

            "streams": [

                {

                    "stream": self.labels,

                    "values": [

                        [str(int(datetime.now().timestamp() * 1e9)), json.dumps(entry)]

                    ]

                }

            ]

        }

        

        response = requests.post(

            f"{self.loki_url}/loki/api/v1/push",

            headers=headers,

            json=payload

        )

        

        if response.status_code != 204:

            raise Exception(f"Failed to send audit log: {response.text}")

```



### 2. 审计日志查询模块



```python

class AuditLogQuery:

    """审计日志查询器"""

    

    def __init__(self, loki_url: str = "http://localhost:3100"):

        self.loki_url = loki_url

    

    def query_by_user(

        self,

        user_id: str,

        start_time: datetime = None,

        end_time: datetime = None,

        limit: int = 100

    ) -> list:

        """按用户查询审计日志"""

        query = f'{{job="audit-logging"}} |= `{user_id}`'

        

        return self._execute_query(query, start_time, end_time, limit)

    

    def query_by_event_type(

        self,

        event_type: AuditEventType,

        start_time: datetime = None,

        end_time: datetime = None,

        limit: int = 100

    ) -> list:

        """按事件类型查询审计日志"""

        query = f'{{job="audit-logging"}} |= `{event_type.value}`'

        

        return self._execute_query(query, start_time, end_time, limit)

    

    def query_by_resource(

        self,

        resource: str,

        start_time: datetime = None,

        end_time: datetime = None,

        limit: int = 100

    ) -> list:

        """按资源查询审计日志"""

        query = f'{{job="audit-logging"}} |= `{resource}`'

        

        return self._execute_query(query, start_time, end_time, limit)

    

    def query_security_events(

        self,

        severity: str = None,

        start_time: datetime = None,

        end_time: datetime = None,

        limit: int = 100

    ) -> list:

        """查询安全事件"""

        query = f'{{job="audit-logging"}} |= `security_event`'

        

        if severity:

            query += f' |= `{severity}`'

        

        return self._execute_query(query, start_time, end_time, limit)

    

    def _execute_query(

        self,

        query: str,

        start_time: datetime = None,

        end_time: datetime = None,

        limit: int = 100

    ) -> list:

        """执行查询"""

        import requests

        

        params = {

            "query": query,

            "limit": limit

        }

        

        if start_time:

            params["start"] = int(start_time.timestamp() * 1e9)

        

        if end_time:

            params["end"] = int(end_time.timestamp() * 1e9)

        

        response = requests.get(

            f"{self.loki_url}/loki/api/v1/query_range",

            params=params

        )

        

        if response.status_code != 200:

            raise Exception(f"Query failed: {response.text}")

        

        result = response.json()

        

        logs = []

        for stream in result.get("data", {}).get("result", []):

            for value in stream.get("values", []):

                logs.append(json.loads(value[1]))

        

        return logs

```



### 3. 审计日志分析模块



```python

from collections import defaultdict

from datetime import datetime, timedelta



class AuditLogAnalyzer:

    """审计日志分析器"""

    

    def __init__(self, audit_query: AuditLogQuery):

        self.query = audit_query

    

    def analyze_user_activity(

        self,

        user_id: str,

        days: int = 7

    ) -> Dict:

        """分析用户活动"""

        start_time = datetime.now() - timedelta(days=days)

        

        logs = self.query.query_by_user(user_id, start_time=start_time)

        

        activity = {

            "total_events": len(logs),

            "event_types": defaultdict(int),

            "resources_accessed": set(),

            "daily_activity": defaultdict(int),

            "failed_operations": 0

        }

        

        for log in logs:

            activity["event_types"][log.get("event_type")] += 1

            activity["resources_accessed"].add(log.get("resource"))

            

            log_date = datetime.fromisoformat(log.get("timestamp")).date()

            activity["daily_activity"][str(log_date)] += 1

            

            if log.get("status") == "failed":

                activity["failed_operations"] += 1

        

        activity["resources_accessed"] = list(activity["resources_accessed"])

        

        return activity

    

    def detect_anomalies(

        self,

        user_id: str = None,

        days: int = 7

    ) -> list:

        """检测异常行为"""

        start_time = datetime.now() - timedelta(days=days)

        

        anomalies = []

        

        if user_id:

            logs = self.query.query_by_user(user_id, start_time=start_time)

        else:

            logs = self.query.query_security_events(start_time=start_time)

        

        failed_count = sum(1 for log in logs if log.get("status") == "failed")

        

        if failed_count > 5:

            anomalies.append({

                "type": "high_failure_rate",

                "user_id": user_id,

                "count": failed_count,

                "severity": "high"

            })

        

        login_times = [

            datetime.fromisoformat(log.get("timestamp")).hour

            for log in logs

            if log.get("event_type") == "login"

        ]

        

        if login_times:

            off_hours_logins = sum(1 for hour in login_times if hour < 6 or hour > 22)

            

            if off_hours_logins > 3:

                anomalies.append({

                    "type": "off_hours_login",

                    "user_id": user_id,

                    "count": off_hours_logins,

                    "severity": "medium"

                })

        

        return anomalies

    

    def generate_audit_report(

        self,

        start_time: datetime,

        end_time: datetime,

        report_type: str = "summary"

    ) -> Dict:

        """生成审计报告"""

        report = {

            "report_time": datetime.now().isoformat(),

            "period": {

                "start": start_time.isoformat(),

                "end": end_time.isoformat()

            },

            "type": report_type,

            "summary": {

                "total_events": 0,

                "unique_users": set(),

                "event_types": defaultdict(int),

                "security_events": 0,

                "failed_operations": 0

            },

            "details": []

        }

        

        all_logs = self.query._execute_query(

            '{job="audit-logging"}',

            start_time=start_time,

            end_time=end_time,

            limit=10000

        )

        

        for log in all_logs:

            report["summary"]["total_events"] += 1

            report["summary"]["unique_users"].add(log.get("user_id"))

            report["summary"]["event_types"][log.get("event_type")] += 1

            

            if log.get("event_type") == "security_event":

                report["summary"]["security_events"] += 1

            

            if log.get("status") == "failed":

                report["summary"]["failed_operations"] += 1

            

            if report_type == "detailed":

                report["details"].append(log)

        

        report["summary"]["unique_users"] = list(report["summary"]["unique_users"])

        report["summary"]["event_types"] = dict(report["summary"]["event_types"])

        

        return report

```



## 技术实现



### 1. Loki部署配置



```yaml

version: '3.8'



services:

  loki:

    image: grafana/loki:2.9.0

    container_name: zephyr-loki

    ports:

      - "3100:3100"

    volumes:

      - ./loki-config.yml:/etc/loki/local-config.yaml

      - loki_data:/loki

    command: -config.file=/etc/loki/local-config.yaml

    networks:

      - zephyr-network

    healthcheck:

      test: ["CMD", "wget", "-q", "--spider", "http://localhost:3100/ready"]

      interval: 10s

      timeout: 5s

      retries: 3



  grafana:

    image: grafana/grafana:10.0.0

    container_name: zephyr-grafana

    ports:

      - "3000:3000"

    environment:

      - GF_SECURITY_ADMIN_PASSWORD=admin

    volumes:

      - grafana_data:/var/lib/grafana

    networks:

      - zephyr-network

    depends_on:

      - loki



volumes:

  loki_data:

  grafana_data:



networks:

  zephyr-network:

    external: true

```



### 2. Loki配置文件



```yaml

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



compactor:

  working_directory: /loki/compactor

  shared_store: filesystem

  retention_enabled: true

  retention_delete_delay: 2h

```



## 实施路径



### Phase 1: 核心功能（Week 1）



**目标**: 实现基础审计日志记录



**任务清单**:

- [ ] 部署Loki服务

- [ ] 实现审计日志记录

- [ ] 实现审计日志查询

- [ ] 集成到业务系统

- [ ] 编写单元测试



**交付物**:

- Loki部署配置

- AuditLogger类

- AuditLogQuery类

- 单元测试覆盖率≥80%



### Phase 2: 高级功能（Week 2）



**目标**: 实现审计日志分析和报告



**任务清单**:

- [ ] 实现审计日志分析

- [ ] 实现异常检测

- [ ] 实现审计报告

- [ ] 配置Grafana仪表板

- [ ] 编写集成测试



**交付物**:

- AuditLogAnalyzer类

- Grafana仪表板

- 集成测试覆盖率≥70%



```
```---
```



**文档版本**: v1.0.0

**创建日期**: 2026-04-07

**最后更新**: 2026-04-07

**状态**: Active

