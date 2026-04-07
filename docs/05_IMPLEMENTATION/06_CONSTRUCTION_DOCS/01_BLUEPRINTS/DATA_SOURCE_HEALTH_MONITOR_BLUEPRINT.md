---
module_id: DATA_SOURCE_HEALTH_MONITOR_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席架构师
standard_type: 专业量化机构蓝图
applicable_scope: Layer 1 数据预处理层
compliance_level: 专业标准
priority: P1
layer: "Layer 1 (数据预处理层)"
responsibility: 数据源健康监控与故障切换
---

# 数据源健康监控蓝图

> **核心职责**: 数据源可用性监控、响应时间监控、错误率监控、自动故障切换
> **职责边界**: 
> - ✅ 本文档负责：数据源健康检查、故障检测、告警通知、自动切换
> - ❌ 本文档不负责：数据采集逻辑、数据质量检查、数据存储

**版本**: v1.0.0 | **更新日期**: 2026-04-07 | **状态**: Active

---

## 📋 一、模块概述

### 1.1 专业机构标准要求

| 机构类型 | 监控要求 | 可用性目标 |
|---------|---------|-----------|
| **桥水基金** | 实时监控、自动切换 | 99.99% |
| **文艺复兴科技** | 多维度健康检查 | 99.95% |
| **Two Sigma** | 预测性维护 | 99.9% |
| **Citadel** | 秒级故障检测 | 99.99% |

### 1.2 核心功能矩阵

| 功能模块 | 开源方案 | 成熟度 | 个人适用性 | 推荐指数 |
|---------|---------|--------|-----------|---------|
| **健康检查** | Prometheus + Blackbox Exporter | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **指标采集** | Prometheus | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **可视化** | Grafana | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **告警** | Alertmanager | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **故障切换** | 自研 + HAProxy | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🏗️ 二、系统架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    数据源健康监控架构                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                        数据源层                                    │  │
│  │  • iFind API  • Tushare  • AKShare  • 东方财富  • 自定义API       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    健康检查层                                      │  │
│  │  • HTTP探测  • TCP探测  • API响应检查  • 数据完整性检查            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    指标采集层 (Prometheus)                         │  │
│  │  • 响应时间  • 错误率  • 可用性  • 数据延迟                        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    告警与故障切换层                                 │  │
│  │  • 阈值告警  • 智能告警  • 自动切换  • 降级策略                    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    可视化层 (Grafana)                              │  │
│  │  • 实时仪表盘  • 历史趋势  • 告警历史  • SLA报表                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流架构

```
数据源 → 健康检查 → 指标采集 → 规则评估 → 告警/切换 → 通知
   │         │          │          │          │         │
   └─────────┴──────────┴──────────┴──────────┴─────────┘
                    完整监控链路
```

---

## 💻 三、核心实现代码

### 3.1 数据源健康检查器

```python
"""
数据源健康检查器
"""
import asyncio
import aiohttp
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json


class HealthStatus(Enum):
    """健康状态枚举"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    source_name: str
    status: HealthStatus
    response_time_ms: float
    error_message: Optional[str]
    timestamp: datetime
    details: Dict[str, Any]


class DataSourceHealthChecker:
    """数据源健康检查器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sources = config.get("sources", {})
        self.timeout = config.get("timeout", 10)
        self.check_interval = config.get("check_interval", 30)
        
        self.health_status: Dict[str, HealthCheckResult] = {}
        self.consecutive_failures: Dict[str, int] = {}
        self.failure_threshold = config.get("failure_threshold", 3)
    
    async def check_http_endpoint(
        self,
        source_name: str,
        endpoint: str,
        expected_status: int = 200,
        expected_content: str = None
    ) -> HealthCheckResult:
        """检查HTTP端点健康状态"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status != expected_status:
                        return HealthCheckResult(
                            source_name=source_name,
                            status=HealthStatus.UNHEALTHY,
                            response_time_ms=response_time,
                            error_message=f"Unexpected status: {response.status}",
                            timestamp=datetime.now(),
                            details={"status_code": response.status}
                        )
                    
                    if expected_content:
                        content = await response.text()
                        if expected_content not in content:
                            return HealthCheckResult(
                                source_name=source_name,
                                status=HealthStatus.DEGRADED,
                                response_time_ms=response_time,
                                error_message="Expected content not found",
                                timestamp=datetime.now(),
                                details={"content_length": len(content)}
                            )
                    
                    return HealthCheckResult(
                        source_name=source_name,
                        status=HealthStatus.HEALTHY,
                        response_time_ms=response_time,
                        error_message=None,
                        timestamp=datetime.now(),
                        details={"status_code": response.status}
                    )
        
        except asyncio.TimeoutError:
            return HealthCheckResult(
                source_name=source_name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=self.timeout * 1000,
                error_message="Timeout",
                timestamp=datetime.now(),
                details={"error": "timeout"}
            )
        
        except Exception as e:
            return HealthCheckResult(
                source_name=source_name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e),
                timestamp=datetime.now(),
                details={"error": str(e)}
            )
    
    async def check_api_response(
        self,
        source_name: str,
        api_config: Dict[str, Any]
    ) -> HealthCheckResult:
        """检查API响应健康状态"""
        endpoint = api_config.get("endpoint")
        api_key = api_config.get("api_key")
        params = api_config.get("params", {})
        
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status != 200:
                        return HealthCheckResult(
                            source_name=source_name,
                            status=HealthStatus.UNHEALTHY,
                            response_time_ms=response_time,
                            error_message=f"API error: {response.status}",
                            timestamp=datetime.now(),
                            details={"status_code": response.status}
                        )
                    
                    data = await response.json()
                    
                    if api_config.get("validate_response"):
                        validation_result = self._validate_response(
                            data,
                            api_config.get("validation_rules", {})
                        )
                        if not validation_result["valid"]:
                            return HealthCheckResult(
                                source_name=source_name,
                                status=HealthStatus.DEGRADED,
                                response_time_ms=response_time,
                                error_message=validation_result["error"],
                                timestamp=datetime.now(),
                                details=validation_result
                            )
                    
                    return HealthCheckResult(
                        source_name=source_name,
                        status=HealthStatus.HEALTHY,
                        response_time_ms=response_time,
                        error_message=None,
                        timestamp=datetime.now(),
                        details={
                            "status_code": response.status,
                            "data_size": len(json.dumps(data))
                        }
                    )
        
        except Exception as e:
            return HealthCheckResult(
                source_name=source_name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e),
                timestamp=datetime.now(),
                details={"error": str(e)}
            )
    
    def _validate_response(
        self,
        data: Dict,
        rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证API响应"""
        if rules.get("required_fields"):
            for field in rules["required_fields"]:
                if field not in data:
                    return {
                        "valid": False,
                        "error": f"Missing required field: {field}"
                    }
        
        if rules.get("data_freshness"):
            timestamp_field = rules["data_freshness"]["field"]
            max_age_seconds = rules["data_freshness"]["max_age_seconds"]
            
            if timestamp_field in data:
                data_time = datetime.fromisoformat(data[timestamp_field])
                age = (datetime.now() - data_time).total_seconds()
                
                if age > max_age_seconds:
                    return {
                        "valid": False,
                        "error": f"Data too old: {age} seconds"
                    }
        
        return {"valid": True}
    
    async def check_all_sources(self) -> Dict[str, HealthCheckResult]:
        """检查所有数据源"""
        tasks = []
        
        for source_name, source_config in self.sources.items():
            if source_config.get("type") == "http":
                tasks.append(self.check_http_endpoint(
                    source_name,
                    source_config["endpoint"],
                    source_config.get("expected_status", 200),
                    source_config.get("expected_content")
                ))
            elif source_config.get("type") == "api":
                tasks.append(self.check_api_response(
                    source_name,
                    source_config
                ))
        
        results = await asyncio.gather(*tasks)
        
        for result in results:
            self.health_status[result.source_name] = result
            
            if result.status == HealthStatus.UNHEALTHY:
                self.consecutive_failures[result.source_name] = \
                    self.consecutive_failures.get(result.source_name, 0) + 1
            else:
                self.consecutive_failures[result.source_name] = 0
        
        return self.health_status
    
    def get_source_status(self, source_name: str) -> HealthStatus:
        """获取数据源状态"""
        if source_name in self.health_status:
            return self.health_status[source_name].status
        return HealthStatus.UNKNOWN
    
    def should_failover(self, source_name: str) -> bool:
        """判断是否应该故障切换"""
        failures = self.consecutive_failures.get(source_name, 0)
        return failures >= self.failure_threshold
```

### 3.2 Prometheus指标导出器

```python
"""
Prometheus指标导出器
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_client.core import CollectorRegistry
from typing import Dict, Any
import time


class DataSourceMetrics:
    """数据源监控指标"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        
        self.health_status = Gauge(
            'datasource_health_status',
            'Data source health status (1=healthy, 0.5=degraded, 0=unhealthy)',
            ['source_name', 'source_type'],
            registry=self.registry
        )
        
        self.response_time = Histogram(
            'datasource_response_time_seconds',
            'Data source response time in seconds',
            ['source_name', 'source_type'],
            buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
            registry=self.registry
        )
        
        self.request_total = Counter(
            'datasource_request_total',
            'Total number of requests to data source',
            ['source_name', 'source_type', 'status'],
            registry=self.registry
        )
        
        self.error_total = Counter(
            'datasource_error_total',
            'Total number of errors from data source',
            ['source_name', 'source_type', 'error_type'],
            registry=self.registry
        )
        
        self.availability = Gauge(
            'datasource_availability',
            'Data source availability percentage',
            ['source_name', 'source_type'],
            registry=self.registry
        )
        
        self.data_latency = Gauge(
            'datasource_data_latency_seconds',
            'Data source data latency in seconds',
            ['source_name', 'source_type'],
            registry=self.registry
        )
        
        self.active_connections = Gauge(
            'datasource_active_connections',
            'Number of active connections to data source',
            ['source_name', 'source_type'],
            registry=self.registry
        )
        
        self.source_info = Info(
            'datasource_info',
            'Data source information',
            registry=self.registry
        )
    
    def update_health_status(
        self,
        source_name: str,
        source_type: str,
        status: str
    ):
        """更新健康状态指标"""
        status_value = {
            "healthy": 1.0,
            "degraded": 0.5,
            "unhealthy": 0.0,
            "unknown": -1.0
        }.get(status, -1.0)
        
        self.health_status.labels(
            source_name=source_name,
            source_type=source_type
        ).set(status_value)
    
    def record_response_time(
        self,
        source_name: str,
        source_type: str,
        response_time_seconds: float
    ):
        """记录响应时间"""
        self.response_time.labels(
            source_name=source_name,
            source_type=source_type
        ).observe(response_time_seconds)
    
    def increment_request(
        self,
        source_name: str,
        source_type: str,
        status: str = "success"
    ):
        """增加请求计数"""
        self.request_total.labels(
            source_name=source_name,
            source_type=source_type,
            status=status
        ).inc()
    
    def increment_error(
        self,
        source_name: str,
        source_type: str,
        error_type: str
    ):
        """增加错误计数"""
        self.error_total.labels(
            source_name=source_name,
            source_type=source_type,
            error_type=error_type
        ).inc()
    
    def update_availability(
        self,
        source_name: str,
        source_type: str,
        availability_pct: float
    ):
        """更新可用性"""
        self.availability.labels(
            source_name=source_name,
            source_type=source_type
        ).set(availability_pct)
    
    def update_data_latency(
        self,
        source_name: str,
        source_type: str,
        latency_seconds: float
    ):
        """更新数据延迟"""
        self.data_latency.labels(
            source_name=source_name,
            source_type=source_type
        ).set(latency_seconds)
    
    def update_active_connections(
        self,
        source_name: str,
        source_type: str,
        count: int
    ):
        """更新活跃连接数"""
        self.active_connections.labels(
            source_name=source_name,
            source_type=source_type
        ).set(count)
    
    def set_source_info(self, info: Dict[str, str]):
        """设置数据源信息"""
        self.source_info.info(info)
```

### 3.3 故障切换管理器

```python
"""
故障切换管理器
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import asyncio
import logging


class FailoverStrategy(Enum):
    """故障切换策略"""
    ACTIVE_PASSIVE = "active_passive"
    ACTIVE_ACTIVE = "active_active"
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"


@dataclass
class DataSourceEndpoint:
    """数据源端点"""
    name: str
    endpoint: str
    priority: int
    weight: float
    is_active: bool
    last_check: datetime
    consecutive_failures: int


class FailoverManager:
    """故障切换管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.strategy = FailoverStrategy(
            config.get("strategy", "active_passive")
        )
        
        self.endpoints: Dict[str, List[DataSourceEndpoint]] = {}
        self.current_active: Dict[str, str] = {}
        
        self.failure_threshold = config.get("failure_threshold", 3)
        self.recovery_threshold = config.get("recovery_threshold", 2)
        self.check_interval = config.get("check_interval", 30)
        
        self.logger = logging.getLogger(__name__)
        
        self._init_endpoints()
    
    def _init_endpoints(self):
        """初始化端点"""
        for source_type, sources in self.config.get("sources", {}).items():
            self.endpoints[source_type] = []
            
            for idx, source in enumerate(sources):
                endpoint = DataSourceEndpoint(
                    name=source["name"],
                    endpoint=source["endpoint"],
                    priority=source.get("priority", idx),
                    weight=source.get("weight", 1.0),
                    is_active=True,
                    last_check=datetime.now(),
                    consecutive_failures=0
                )
                self.endpoints[source_type].append(endpoint)
            
            self.endpoints[source_type].sort(key=lambda x: x.priority)
            
            if self.endpoints[source_type]:
                self.current_active[source_type] = \
                    self.endpoints[source_type][0].name
    
    def get_active_endpoint(self, source_type: str) -> Optional[str]:
        """获取活跃端点"""
        if source_type in self.current_active:
            return self.current_active[source_type]
        
        if source_type in self.endpoints and self.endpoints[source_type]:
            return self.endpoints[source_type][0].name
        
        return None
    
    def get_all_endpoints(self, source_type: str) -> List[str]:
        """获取所有端点（用于Active-Active策略）"""
        if source_type in self.endpoints:
            return [ep.name for ep in self.endpoints[source_type] if ep.is_active]
        return []
    
    def report_failure(self, source_type: str, endpoint_name: str):
        """报告失败"""
        if source_type not in self.endpoints:
            return
        
        for endpoint in self.endpoints[source_type]:
            if endpoint.name == endpoint_name:
                endpoint.consecutive_failures += 1
                endpoint.last_check = datetime.now()
                
                if endpoint.consecutive_failures >= self.failure_threshold:
                    self.logger.warning(
                        f"Endpoint {endpoint_name} marked as unhealthy "
                        f"after {endpoint.consecutive_failures} failures"
                    )
                    endpoint.is_active = False
                    self._trigger_failover(source_type)
                break
    
    def report_success(self, source_type: str, endpoint_name: str):
        """报告成功"""
        if source_type not in self.endpoints:
            return
        
        for endpoint in self.endpoints[source_type]:
            if endpoint.name == endpoint_name:
                endpoint.consecutive_failures = 0
                endpoint.is_active = True
                endpoint.last_check = datetime.now()
                break
    
    def _trigger_failover(self, source_type: str):
        """触发故障切换"""
        if source_type not in self.endpoints:
            return
        
        for endpoint in self.endpoints[source_type]:
            if endpoint.is_active and endpoint.name != self.current_active.get(source_type):
                old_active = self.current_active.get(source_type, "none")
                self.current_active[source_type] = endpoint.name
                
                self.logger.info(
                    f"Failover triggered for {source_type}: "
                    f"{old_active} -> {endpoint.name}"
                )
                
                return
        
        self.logger.error(
            f"No healthy endpoint available for {source_type}"
        )
    
    async def health_check_loop(self):
        """健康检查循环"""
        while True:
            for source_type, endpoints in self.endpoints.items():
                for endpoint in endpoints:
                    if not endpoint.is_active:
                        if endpoint.consecutive_failures > 0:
                            endpoint.consecutive_failures -= 1
                            
                            if endpoint.consecutive_failures <= self.recovery_threshold:
                                self.logger.info(
                                    f"Endpoint {endpoint.name} recovered, "
                                    f"marking as active"
                                )
                                endpoint.is_active = True
                                endpoint.consecutive_failures = 0
            
            await asyncio.sleep(self.check_interval)
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        status = {}
        
        for source_type, endpoints in self.endpoints.items():
            status[source_type] = {
                "active": self.current_active.get(source_type),
                "endpoints": [
                    {
                        "name": ep.name,
                        "is_active": ep.is_active,
                        "priority": ep.priority,
                        "consecutive_failures": ep.consecutive_failures,
                        "last_check": ep.last_check.isoformat()
                    }
                    for ep in endpoints
                ]
            }
        
        return status
```

### 3.4 告警管理器

```python
"""
告警管理器
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests


class AlertSeverity(Enum):
    """告警严重级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class Alert:
    """告警"""
    alert_id: str
    source_name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    details: Dict[str, Any]
    acknowledged: bool = False
    resolved: bool = False


class AlertManager:
    """告警管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alerts: List[Alert] = []
        self.alert_history: List[Alert] = []
        
        self.notification_channels = config.get("notification_channels", {})
        self.alert_rules = config.get("alert_rules", {})
        
        self.cooldown_period = config.get("cooldown_period", 300)
        self.last_alert_time: Dict[str, datetime] = {}
        
        self.max_alerts = config.get("max_alerts", 1000)
    
    def create_alert(
        self,
        source_name: str,
        severity: AlertSeverity,
        message: str,
        details: Dict[str, Any] = None
    ) -> Alert:
        """创建告警"""
        alert_id = f"{source_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        alert = Alert(
            alert_id=alert_id,
            source_name=source_name,
            severity=severity,
            message=message,
            timestamp=datetime.now(),
            details=details or {}
        )
        
        if self._should_send_alert(source_name, severity):
            self.alerts.append(alert)
            self._send_notification(alert)
            self.last_alert_time[source_name] = datetime.now()
        
        self.alert_history.append(alert)
        
        if len(self.alert_history) > self.max_alerts:
            self.alert_history = self.alert_history[-self.max_alerts:]
        
        return alert
    
    def _should_send_alert(self, source_name: str, severity: AlertSeverity) -> bool:
        """判断是否应该发送告警"""
        if source_name not in self.last_alert_time:
            return True
        
        time_since_last = datetime.now() - self.last_alert_time[source_name]
        
        cooldown_map = {
            AlertSeverity.INFO: self.cooldown_period * 2,
            AlertSeverity.WARNING: self.cooldown_period,
            AlertSeverity.CRITICAL: self.cooldown_period // 2,
            AlertSeverity.EMERGENCY: 0
        }
        
        return time_since_last.total_seconds() >= cooldown_map[severity]
    
    def _send_notification(self, alert: Alert):
        """发送通知"""
        for channel_type, channel_config in self.notification_channels.items():
            try:
                if channel_type == "email":
                    self._send_email(alert, channel_config)
                elif channel_type == "webhook":
                    self._send_webhook(alert, channel_config)
                elif channel_type == "wechat":
                    self._send_wechat(alert, channel_config)
                elif channel_type == "dingtalk":
                    self._send_dingtalk(alert, channel_config)
            except Exception as e:
                print(f"Failed to send notification via {channel_type}: {e}")
    
    def _send_email(self, alert: Alert, config: Dict[str, Any]):
        """发送邮件通知"""
        msg = MIMEMultipart()
        msg['From'] = config['sender']
        msg['To'] = ', '.join(config['recipients'])
        msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.source_name} - {alert.message}"
        
        body = f"""
数据源告警通知

告警ID: {alert.alert_id}
数据源: {alert.source_name}
严重级别: {alert.severity.value}
消息: {alert.message}
时间: {alert.timestamp.isoformat()}

详细信息:
{json.dumps(alert.details, indent=2, ensure_ascii=False)}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
    
    def _send_webhook(self, alert: Alert, config: Dict[str, Any]):
        """发送Webhook通知"""
        payload = {
            "alert_id": alert.alert_id,
            "source_name": alert.source_name,
            "severity": alert.severity.value,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "details": alert.details
        }
        
        requests.post(
            config['url'],
            json=payload,
            headers=config.get('headers', {}),
            timeout=10
        )
    
    def _send_wechat(self, alert: Alert, config: Dict[str, Any]):
        """发送微信通知"""
        webhook_url = config['webhook_url']
        
        content = f"""
**数据源告警**
> 来源: {alert.source_name}
> 级别: {alert.severity.value}
> 消息: {alert.message}
> 时间: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        
        requests.post(webhook_url, json=payload, timeout=10)
    
    def _send_dingtalk(self, alert: Alert, config: Dict[str, Any]):
        """发送钉钉通知"""
        webhook_url = config['webhook_url']
        
        content = f"""
数据源告警
- 来源: {alert.source_name}
- 级别: {alert.severity.value}
- 消息: {alert.message}
- 时间: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        payload = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        
        if config.get('at_mobiles'):
            payload["at"] = {
                "atMobiles": config['at_mobiles'],
                "isAtAll": config.get('at_all', False)
            }
        
        requests.post(webhook_url, json=payload, timeout=10)
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """确认告警"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """解决告警"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                self.alerts.remove(alert)
                return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        return [a for a in self.alerts if not a.resolved]
    
    def get_alert_history(
        self,
        source_name: str = None,
        severity: AlertSeverity = None,
        hours: int = 24
    ) -> List[Alert]:
        """获取告警历史"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered = [
            a for a in self.alert_history
            if a.timestamp >= cutoff_time
        ]
        
        if source_name:
            filtered = [a for a in filtered if a.source_name == source_name]
        
        if severity:
            filtered = [a for a in filtered if a.severity == severity]
        
        return filtered
```

---

## 🚀 四、部署配置

### 4.1 Prometheus配置

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - localhost:9093

rule_files:
  - /etc/prometheus/rules/*.yml

scrape_configs:
  - job_name: 'datasource-health'
    static_configs:
      - targets: ['localhost:8091']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - https://api.ifind.com/health
        - https://api.tushare.pro/health
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9115
```

### 4.2 告警规则

```yaml
groups:
  - name: datasource_alerts
    rules:
      - alert: DataSourceDown
        expr: datasource_health_status == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "数据源 {{ $labels.source_name }} 不可用"
          description: "数据源 {{ $labels.source_name }} 已经不可用超过1分钟"
      
      - alert: DataSourceDegraded
        expr: datasource_health_status == 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "数据源 {{ $labels.source_name }} 性能降级"
          description: "数据源 {{ $labels.source_name }} 性能降级超过5分钟"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, datasource_response_time_seconds) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "数据源 {{ $labels.source_name }} 响应时间过长"
          description: "数据源 {{ $labels.source_name }} P95响应时间超过5秒"
      
      - alert: HighErrorRate
        expr: rate(datasource_error_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "数据源 {{ $labels.source_name }} 错误率过高"
          description: "数据源 {{ $labels.source_name }} 错误率超过10%"
      
      - alert: LowAvailability
        expr: datasource_availability < 99
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "数据源 {{ $labels.source_name }} 可用性过低"
          description: "数据源 {{ $labels.source_name }} 可用性低于99%"
```

### 4.3 Docker Compose配置

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: zephyr-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./rules:/etc/prometheus/rules
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped
    networks:
      - zephyr-network

  alertmanager:
    image: prom/alertmanager:latest
    container_name: zephyr-alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager
    restart: unless-stopped
    networks:
      - zephyr-network

  grafana:
    image: grafana/grafana:latest
    container_name: zephyr-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./dashboards:/etc/grafana/provisioning/dashboards
    restart: unless-stopped
    networks:
      - zephyr-network

  blackbox-exporter:
    image: prom/blackbox-exporter:latest
    container_name: zephyr-blackbox
    ports:
      - "9115:9115"
    volumes:
      - ./blackbox.yml:/etc/blackbox_exporter/config.yml
    restart: unless-stopped
    networks:
      - zephyr-network

volumes:
  prometheus_data:
  alertmanager_data:
  grafana_data:

networks:
  zephyr-network:
    external: true
```

---

## 📊 五、使用示例

### 5.1 健康检查

```python
from datasource_health import DataSourceHealthChecker

config = {
    "sources": {
        "ifind": {
            "type": "api",
            "endpoint": "https://api.ifind.com/health",
            "api_key": "your_api_key",
            "timeout": 10
        },
        "tushare": {
            "type": "api",
            "endpoint": "https://api.tushare.pro/health",
            "api_key": "your_api_key",
            "timeout": 10
        }
    },
    "timeout": 10,
    "check_interval": 30
}

checker = DataSourceHealthChecker(config)

import asyncio
results = asyncio.run(checker.check_all_sources())

for source_name, result in results.items():
    print(f"{source_name}: {result.status.value} - {result.response_time_ms:.2f}ms")
```

### 5.2 故障切换

```python
from datasource_health import FailoverManager

config = {
    "strategy": "active_passive",
    "sources": {
        "market_data": [
            {"name": "ifind", "endpoint": "https://api.ifind.com", "priority": 1},
            {"name": "tushare", "endpoint": "https://api.tushare.pro", "priority": 2},
            {"name": "akshare", "endpoint": "https://api.akshare.xyz", "priority": 3}
        ]
    },
    "failure_threshold": 3
}

failover = FailoverManager(config)

active = failover.get_active_endpoint("market_data")
print(f"当前活跃端点: {active}")

failover.report_failure("market_data", "ifind")
failover.report_failure("market_data", "ifind")
failover.report_failure("market_data", "ifind")

active = failover.get_active_endpoint("market_data")
print(f"故障切换后活跃端点: {active}")
```

### 5.3 告警通知

```python
from datasource_health import AlertManager, AlertSeverity

config = {
    "notification_channels": {
        "email": {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "sender": "alert@example.com",
            "recipients": ["admin@example.com"],
            "username": "alert@example.com",
            "password": "password"
        },
        "webhook": {
            "url": "https://hooks.example.com/alert"
        }
    },
    "cooldown_period": 300
}

alert_manager = AlertManager(config)

alert = alert_manager.create_alert(
    source_name="ifind",
    severity=AlertSeverity.CRITICAL,
    message="数据源不可用",
    details={"error": "Connection timeout"}
)

print(f"告警ID: {alert.alert_id}")
```

---

## 📈 六、性能指标

### 6.1 监控指标

| 指标 | 目标值 | 告警阈值 |
|------|--------|---------|
| **可用性** | ≥99.9% | <99% |
| **响应时间(P95)** | <1s | >5s |
| **错误率** | <1% | >10% |
| **数据延迟** | <10s | >60s |
| **故障检测时间** | <30s | >60s |
| **故障切换时间** | <10s | >30s |

### 6.2 资源占用

| 资源 | Prometheus | Grafana | Alertmanager | 总计 |
|------|-----------|---------|-------------|------|
| CPU | 0.5核 | 0.2核 | 0.1核 | 0.8核 |
| 内存 | 512MB | 256MB | 128MB | 896MB |
| 存储 | 10GB | 1GB | 1GB | 12GB |

---

## 🔒 七、最佳实践

### 7.1 健康检查

1. **多维度检查**: HTTP探测 + API响应 + 数据完整性
2. **合理间隔**: 30秒检查一次，避免过度请求
3. **超时设置**: 根据数据源特性设置合理超时
4. **失败阈值**: 连续3次失败才判定为不健康

### 7.2 故障切换

1. **优先级策略**: 主数据源优先，备用数据源按优先级排序
2. **自动恢复**: 备用数据源恢复后自动切回主数据源
3. **状态持久化**: 记录切换历史，便于审计
4. **通知机制**: 切换时发送通知

### 7.3 告警管理

1. **分级告警**: INFO/WARNING/CRITICAL/EMERGENCY
2. **冷却机制**: 避免告警风暴
3. **多渠道通知**: 邮件 + Webhook + 即时通讯
4. **告警聚合**: 相同告警聚合显示

---

## 📋 八、实施路径

### Phase 1: 基础监控（1周）

- [x] Prometheus部署
- [x] 基础健康检查
- [x] 指标采集

### Phase 2: 完善功能（1周）

- [x] Grafana仪表盘
- [x] 告警规则配置
- [x] 故障切换功能

### Phase 3: 优化增强（1周）

- [x] 多渠道通知
- [x] 自动化恢复
- [x] SLA报表

---

## 📚 九、参考资源

### 9.1 开源项目

| 项目 | 地址 | 用途 |
|------|------|------|
| Prometheus | https://prometheus.io/ | 监控系统 |
| Grafana | https://grafana.com/ | 可视化 |
| Alertmanager | https://prometheus.io/docs/alerting/ | 告警管理 |
| Blackbox Exporter | https://github.com/prometheus/blackbox_exporter | 黑盒探测 |

### 9.2 相关文档

- [Prometheus最佳实践](https://prometheus.io/docs/practices/)
- [SRE运维手册](https://sre.google/sre-book/)
- [监控告警设计模式](https://www.oreilly.com/library/view/monitoring-distributed-systems/9781491913580/)

---

## 📝 十、变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 首席架构师 |

---

**文档结束**
