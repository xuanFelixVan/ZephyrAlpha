---
module_id: DATA_SOURCE_HEALTH_MONITOR__001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: é¦å¸­æ¶æå¸?
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 1 æ°æ®é¢å¤çå±
compliance_level: ä¸ä¸æ å
priority: P1
layer: "Layer 1 (æ°æ®é¢å¤çå±)"
responsibility: æ°æ®æºå¥åº·çæ§ä¸æéåæ¢
---

# æ°æ®æºå¥åº·çæ§èå?

## 核心定位

负责数据源健康监控的设计与实现，基于健康检查技术，监控数据源状态，确保数据可用性。



> **æ ¸å¿èè´£**: æ°æ®æºå¯ç¨æ§çæ§ãååºæ¶é´çæ§ãéè¯¯ççæ§ãèªå¨æéåæ?
> **èè´£è¾¹ç**: 
> - â?æ¬ææ¡£è´è´£ï¼æ°æ®æºå¥åº·æ£æ¥ãæéæ£æµãåè­¦éç¥ãèªå¨åæ?
> - â?æ¬ææ¡£ä¸è´è´£ï¼æ°æ®ééé»è¾ãæ°æ®è´¨éæ£æ¥ãæ°æ®å­å?

**çæ¬**: v1.0.0 | **æ´æ°æ¥æ**: 2026-04-07 | **ç¶æ?*: Active

---

## æ ¸å¿å®ä½

è´è´£æ°æ®æºå¥åº·çæ§ï¼å®æ¶çæ§æ°æ®æºç¶æï¼æä¾å¥åº·æ£æ¥ãåè­¦åèªå¨æ¢å¤åè½ã?

## ð ä¸ãæ¨¡åæ¦è¿?

### 1.1 ä¸ä¸æºææ åè¦æ±

| æºæç±»å | çæ§è¦æ± | å¯ç¨æ§ç®æ ?|
|---------|---------|-----------|
| **æ¡¥æ°´åºé** | å®æ¶çæ§ãèªå¨åæ?| 99.99% |
| **æèºå¤å´ç§æ** | å¤ç»´åº¦å¥åº·æ£æ?| 99.95% |
| **Two Sigma** | é¢æµæ§ç»´æ?| 99.9% |
| **Citadel** | ç§çº§æéæ£æµ?| 99.99% |

### 1.2 æ ¸å¿åè½ç©éµ

| åè½æ¨¡å | å¼æºæ¹æ¡?| æçåº?| ä¸ªäººéç¨æ?| æ¨èææ° |
|---------|---------|--------|-----------|---------|
| **å¥åº·æ£æ?* | Prometheus + Blackbox Exporter | â­â­â­â­â­?| â­â­â­â­ | â­â­â­â­â­?|
| **ææ éé** | Prometheus | â­â­â­â­â­?| â­â­â­â­â­?| â­â­â­â­â­?|
| **å¯è§å?* | Grafana | â­â­â­â­â­?| â­â­â­â­â­?| â­â­â­â­â­?|
| **åè­¦** | Alertmanager | â­â­â­â­â­?| â­â­â­â­ | â­â­â­â­â­?|
| **æéåæ¢** | èªç  + HAProxy | â­â­â­â­ | â­â­â­â­ | â­â­â­â­ |

---

## ðï¸?äºãç³»ç»æ¶æè®¾è®?

### 2.1 æ´ä½æ¶æå?

```
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                   æ°æ®æºå¥åº·çæ§æ¶æ?                                     â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                                                                        â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â? â?                       æ°æ®æºå±                                    â? â?
â? â? â?iFind API  â?Tushare  â?AKShare  â?ä¸æ¹è´¢å¯  â?èªå®ä¹API       â? â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â?                             â?                                         â?
â?                             â?                                         â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â? â?                   å¥åº·æ£æ¥å±                                      â? â?
â? â? â?HTTPæ¢æµ  â?TCPæ¢æµ  â?APIååºæ£æ? â?æ°æ®å®æ´æ§æ£æ?           â? â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â?                             â?                                         â?
â?                             â?                                         â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â? â?                   ææ ééå±?(Prometheus)                         â? â?
â? â? â?ååºæ¶é´  â?éè¯¯ç? â?å¯ç¨æ? â?æ°æ®å»¶è¿                        â? â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â?                             â?                                         â?
â?                             â?                                         â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â? â?                   åè­¦ä¸æéåæ¢å±                                 â? â?
â? â? â?éå¼åè­? â?æºè½åè­¦  â?èªå¨åæ¢  â?éçº§ç­ç¥                    â? â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â?                             â?                                         â?
â?                             â?                                         â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â? â?                   å¯è§åå± (Grafana)                              â? â?
â? â? â?å®æ¶ä»ªè¡¨ç? â?åå²è¶å¿  â?åè­¦åå²  â?SLAæ¥è¡¨                   â? â?
â? ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ? â?
â?                                                                        â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
```

### 2.2 æ°æ®æµæ¶æ?

```
æ°æ®æº?â?å¥åº·æ£æ?â?ææ éé â?è§åè¯ä¼° â?åè­¦/åæ¢ â?éç¥
   â?        â?         â?         â?         â?        â?
   âââââââââââ´âââââââââââ´âââââââââââ´âââââââââââ´ââââââââââ?
                    å®æ´çæ§é¾è·¯
```

---

## ð» ä¸ãæ ¸å¿å®ç°ä»£ç ?

### 3.1 æ°æ®æºå¥åº·æ£æ¥å¨

```python
"""
æ°æ®æºå¥åº·æ£æ¥å¨
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
    """å¥åº·ç¶ææä¸?""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """å¥åº·æ£æ¥ç»æ?""
    source_name: str
    status: HealthStatus
    response_time_ms: float
    error_message: Optional[str]
    timestamp: datetime
    details: Dict[str, Any]


class DataSourceHealthChecker:
    """æ°æ®æºå¥åº·æ£æ¥å¨"""
    
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
        """æ£æ¥HTTPç«¯ç¹å¥åº·ç¶æ?""
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
        """æ£æ¥APIååºå¥åº·ç¶æ?""
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
        """éªè¯APIååº"""
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
        """æ£æ¥æææ°æ®æº"""
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
        """è·åæ°æ®æºç¶æ?""
        if source_name in self.health_status:
            return self.health_status[source_name].status
        return HealthStatus.UNKNOWN
    
    def should_failover(self, source_name: str) -> bool:
        """å¤æ­æ¯å¦åºè¯¥æéåæ¢"""
        failures = self.consecutive_failures.get(source_name, 0)
        return failures >= self.failure_threshold
```

### 3.2 Prometheusææ å¯¼åºå?

```python
"""
Prometheusææ å¯¼åºå?
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_client.core import CollectorRegistry
from typing import Dict, Any
import time


class DataSourceMetrics:
    """æ°æ®æºçæ§ææ ?""
    
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
        """æ´æ°å¥åº·ç¶æææ ?""
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
        """è®°å½ååºæ¶é´"""
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
        """å¢å è¯·æ±è®¡æ°"""
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
        """å¢å éè¯¯è®¡æ°"""
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
        """æ´æ°å¯ç¨æ?""
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
        """æ´æ°æ°æ®å»¶è¿"""
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
        """æ´æ°æ´»è·è¿æ¥æ?""
        self.active_connections.labels(
            source_name=source_name,
            source_type=source_type
        ).set(count)
    
    def set_source_info(self, info: Dict[str, str]):
        """è®¾ç½®æ°æ®æºä¿¡æ?""
        self.source_info.info(info)
```

### 3.3 æéåæ¢ç®¡çå?

```python
"""
æéåæ¢ç®¡çå?
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import asyncio
import logging


class FailoverStrategy(Enum):
    """æéåæ¢ç­ç¥"""
    ACTIVE_PASSIVE = "active_passive"
    ACTIVE_ACTIVE = "active_active"
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"


@dataclass
class DataSourceEndpoint:
    """æ°æ®æºç«¯ç?""
    name: str
    endpoint: str
    priority: int
    weight: float
    is_active: bool
    last_check: datetime
    consecutive_failures: int


class FailoverManager:
    """æéåæ¢ç®¡çå?""
    
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
        """åå§åç«¯ç?""
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
        """è·åæ´»è·ç«¯ç¹"""
        if source_type in self.current_active:
            return self.current_active[source_type]
        
        if source_type in self.endpoints and self.endpoints[source_type]:
            return self.endpoints[source_type][0].name
        
        return None
    
    def get_all_endpoints(self, source_type: str) -> List[str]:
        """è·åææç«¯ç¹ï¼ç¨äºActive-Activeç­ç¥ï¼?""
        if source_type in self.endpoints:
            return [ep.name for ep in self.endpoints[source_type] if ep.is_active]
        return []
    
    def report_failure(self, source_type: str, endpoint_name: str):
        """æ¥åå¤±è´¥"""
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
        """æ¥åæå"""
        if source_type not in self.endpoints:
            return
        
        for endpoint in self.endpoints[source_type]:
            if endpoint.name == endpoint_name:
                endpoint.consecutive_failures = 0
                endpoint.is_active = True
                endpoint.last_check = datetime.now()
                break
    
    def _trigger_failover(self, source_type: str):
        """è§¦åæéåæ¢"""
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
        """å¥åº·æ£æ¥å¾ªç?""
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
        """è·åç¶æ?""
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

### 3.4 åè­¦ç®¡çå?

```python
"""
åè­¦ç®¡çå?
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
    """åè­¦ä¸¥éçº§å«"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class Alert:
    """åè­¦"""
    alert_id: str
    source_name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    details: Dict[str, Any]
    acknowledged: bool = False
    resolved: bool = False


class AlertManager:
    """åè­¦ç®¡çå?""
    
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
        """åå»ºåè­¦"""
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
        """å¤æ­æ¯å¦åºè¯¥åéåè­?""
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
        """åééç¥"""
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
        """åéé®ä»¶éç¥"""
        msg = MIMEMultipart()
        msg['From'] = config['sender']
        msg['To'] = ', '.join(config['recipients'])
        msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.source_name} - {alert.message}"
        
        body = f"""
æ°æ®æºåè­¦éç¥

åè­¦ID: {alert.alert_id}
æ°æ®æº? {alert.source_name}
ä¸¥éçº§å«: {alert.severity.value}
æ¶æ¯: {alert.message}
æ¶é´: {alert.timestamp.isoformat()}

è¯¦ç»ä¿¡æ¯:
{json.dumps(alert.details, indent=2, ensure_ascii=False)}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
    
    def _send_webhook(self, alert: Alert, config: Dict[str, Any]):
        """åéWebhookéç¥"""
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
        """åéå¾®ä¿¡éç¥"""
        webhook_url = config['webhook_url']
        
        content = f"""
**æ°æ®æºåè­?*
> æ¥æº: {alert.source_name}
> çº§å«: {alert.severity.value}
> æ¶æ¯: {alert.message}
> æ¶é´: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        
        requests.post(webhook_url, json=payload, timeout=10)
    
    def _send_dingtalk(self, alert: Alert, config: Dict[str, Any]):
        """åééééç¥"""
        webhook_url = config['webhook_url']
        
        content = f"""
æ°æ®æºåè­?
- æ¥æº: {alert.source_name}
- çº§å«: {alert.severity.value}
- æ¶æ¯: {alert.message}
- æ¶é´: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
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
        """ç¡®è®¤åè­¦"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """è§£å³åè­¦"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                self.alerts.remove(alert)
                return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """è·åæ´»è·åè­¦"""
        return [a for a in self.alerts if not a.resolved]
    
    def get_alert_history(
        self,
        source_name: str = None,
        severity: AlertSeverity = None,
        hours: int = 24
    ) -> List[Alert]:
        """è·ååè­¦åå²"""
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

## ð åãé¨ç½²éç½?

### 4.1 Prometheuséç½®

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

### 4.2 åè­¦è§å

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
          summary: "æ°æ®æº?{{ $labels.source_name }} ä¸å¯ç?
          description: "æ°æ®æº?{{ $labels.source_name }} å·²ç»ä¸å¯ç¨è¶è¿?åé"
      
      - alert: DataSourceDegraded
        expr: datasource_health_status == 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "æ°æ®æº?{{ $labels.source_name }} æ§è½éçº§"
          description: "æ°æ®æº?{{ $labels.source_name }} æ§è½éçº§è¶è¿5åé"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, datasource_response_time_seconds) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "æ°æ®æº?{{ $labels.source_name }} ååºæ¶é´è¿é¿"
          description: "æ°æ®æº?{{ $labels.source_name }} P95ååºæ¶é´è¶è¿5ç§?
      
      - alert: HighErrorRate
        expr: rate(datasource_error_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "æ°æ®æº?{{ $labels.source_name }} éè¯¯çè¿é«?
          description: "æ°æ®æº?{{ $labels.source_name }} éè¯¯çè¶è¿?0%"
      
      - alert: LowAvailability
        expr: datasource_availability < 99
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "æ°æ®æº?{{ $labels.source_name }} å¯ç¨æ§è¿ä½?
          description: "æ°æ®æº?{{ $labels.source_name }} å¯ç¨æ§ä½äº?9%"
```

### 4.3 Docker Composeéç½®

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

## ð äºãä½¿ç¨ç¤ºä¾?

### 5.1 å¥åº·æ£æ?

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

### 5.2 æéåæ¢

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
print(f"å½åæ´»è·ç«¯ç¹: {active}")

failover.report_failure("market_data", "ifind")
failover.report_failure("market_data", "ifind")
failover.report_failure("market_data", "ifind")

active = failover.get_active_endpoint("market_data")
print(f"æéåæ¢åæ´»è·ç«¯ç? {active}")
```

### 5.3 åè­¦éç¥

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
    message="æ°æ®æºä¸å¯ç¨",
    details={"error": "Connection timeout"}
)

print(f"åè­¦ID: {alert.alert_id}")
```

---

## ð å­ãæ§è½ææ 

### 6.1 çæ§ææ 

| ææ  | ç®æ å?| åè­¦éå?|
|------|--------|---------|
| **å¯ç¨æ?* | â?9.9% | <99% |
| **ååºæ¶é´(P95)** | <1s | >5s |
| **éè¯¯ç?* | <1% | >10% |
| **æ°æ®å»¶è¿** | <10s | >60s |
| **æéæ£æµæ¶é?* | <30s | >60s |
| **æéåæ¢æ¶é´** | <10s | >30s |

### 6.2 èµæºå ç¨

| èµæº | Prometheus | Grafana | Alertmanager | æ»è®¡ |
|------|-----------|---------|-------------|------|
| CPU | 0.5æ ?| 0.2æ ?| 0.1æ ?| 0.8æ ?|
| åå­ | 512MB | 256MB | 128MB | 896MB |
| å­å¨ | 10GB | 1GB | 1GB | 12GB |

---

## ð ä¸ãæä½³å®è·?

### 7.1 å¥åº·æ£æ?

1. **å¤ç»´åº¦æ£æ?*: HTTPæ¢æµ + APIååº + æ°æ®å®æ´æ?
2. **åçé´é**: 30ç§æ£æ¥ä¸æ¬¡ï¼é¿åè¿åº¦è¯·æ±
3. **è¶æ¶è®¾ç½®**: æ ¹æ®æ°æ®æºç¹æ§è®¾ç½®åçè¶æ?
4. **å¤±è´¥éå?*: è¿ç»­3æ¬¡å¤±è´¥æå¤å®ä¸ºä¸å¥åº·

### 7.2 æéåæ¢

1. **ä¼åçº§ç­ç?*: ä¸»æ°æ®æºä¼åï¼å¤ç¨æ°æ®æºæä¼åçº§æåº
2. **èªå¨æ¢å¤**: å¤ç¨æ°æ®æºæ¢å¤åèªå¨ååä¸»æ°æ®æº
3. **ç¶ææä¹å**: è®°å½åæ¢åå²ï¼ä¾¿äºå®¡è®?
4. **éç¥æºå¶**: åæ¢æ¶åééç¥

### 7.3 åè­¦ç®¡ç

1. **åçº§åè­¦**: INFO/WARNING/CRITICAL/EMERGENCY
2. **å·å´æºå¶**: é¿ååè­¦é£æ´
3. **å¤æ¸ ééç¥**: é®ä»¶ + Webhook + å³æ¶éè®¯
4. **åè­¦èå**: ç¸ååè­¦èåæ¾ç¤º

---

## ð å«ãå®æ½è·¯å¾?

### Phase 1: åºç¡çæ§ï¼?å¨ï¼

- [x] Prometheusé¨ç½²
- [x] åºç¡å¥åº·æ£æ?
- [x] ææ éé

### Phase 2: å®ååè½ï¼?å¨ï¼

- [x] Grafanaä»ªè¡¨ç?
- [x] åè­¦è§åéç½®
- [x] æéåæ¢åè½

### Phase 3: ä¼åå¢å¼ºï¼?å¨ï¼

- [x] å¤æ¸ ééç¥
- [x] èªå¨åæ¢å¤?
- [x] SLAæ¥è¡¨

---

## ð ä¹ãåèèµæº?

### 9.1 å¼æºé¡¹ç?

| é¡¹ç® | å°å | ç¨é?|
|------|------|------|
| Prometheus | https://prometheus.io/ | çæ§ç³»ç» |
| Grafana | https://grafana.com/ | å¯è§å?|
| Alertmanager | https://prometheus.io/docs/alerting/ | åè­¦ç®¡ç |
| Blackbox Exporter | https://github.com/prometheus/blackbox_exporter | é»çæ¢æµ |

### 9.2 ç¸å³ææ¡£

- [Prometheusæä½³å®è·µ](https://prometheus.io/docs/practices/)
- [SREè¿ç»´æå](https://sre.google/sre-book/)
- [çæ§åè­¦è®¾è®¡æ¨¡å¼](https://www.oreilly.com/library/view/monitoring-distributed-systems/9781491913580/)

---

## ð åãåæ´åå?

| çæ¬ | æ¥æ | åæ´åå®¹ | ä½è?|
|------|------|---------|------|
| v1.0.0 | 2026-04-07 | åå§çæ¬åå»º | é¦å¸­æ¶æå¸?|

---

**ææ¡£ç»æ**
