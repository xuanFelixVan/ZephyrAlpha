---
module_id: DATA_SOURCE_FAILOVER_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席架构师
layer: Layer 0 (数据源层)
standard_type: 专业量化机构级蓝图
applicable_scope: 数据源故障转移模块
compliance_level: 顶级专业标准
reference_models: ["Bloomberg", "Reuters", "Wind"]
---

# 数据源故障转移蓝图

> **版本**: v1.0  
> **创建日期**: 2026-04-07  
> **优先级**: P1级专业模块  
> **实施周期**: 2周

---

## 一、模块概述

### 1.1 核心定位

数据源故障转移模块负责在主数据源故障时自动切换到备用数据源，保障数据服务的连续性和可用性。

### 1.2 业务价值

| 价值维度 | 说明 |
|---------|------|
| **高可用性** | 确保数据服务持续可用 |
| **故障恢复** | 快速自动故障转移 |
| **数据一致性** | 保证故障转移后数据一致性 |
| **监控告警** | 实时监控数据源健康状态 |

### 1.3 技术选型

| 组件 | 方案 | 开源项目 | Stars | 替代率 |
|------|------|---------|-------|--------|
| 健康检查 | 自研 | - | - | 20% |
| 故障检测 | Circuit Breaker | pybreaker | 700+ | 80% |
| 消息队列 | RabbitMQ | rabbitmq | 12k+ | 90% |
| 监控 | Prometheus | prometheus | 55k+ | 95% |

---

## 二、架构设计

### 2.1 系统架构

```
┌─────────────────────────────────────────────────────────┐
│            数据源故障转移架构                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  主数据源     │  │  备用数据源1 │  │  备用数据源2 │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                  │                  │         │
│         └──────────────────┼──────────────────┘         │
│                            │                            │
│                    ┌───────▼───────┐                    │
│                    │  故障转移管理器 │                    │
│                    └───────┬───────┘                    │
│                            │                            │
│         ┌──────────────────┼──────────────────┐         │
│         │                  │                  │         │
│  ┌──────▼──────┐  ┌───────▼───────┐  ┌──────▼──────┐ │
│  │ 健康检查     │  │ 故障检测      │  │ 自动切换    │ │
│  └─────────────┘  └───────────────┘  └─────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 核心组件

#### 2.2.1 故障转移管理器

```python
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import time
import logging
import threading
from queue import Queue
import pybreaker
import requests

logger = logging.getLogger(__name__)

class DataSourceStatus(Enum):
    """数据源状态"""
    HEALTHY = 'healthy'
    DEGRADED = 'degraded'
    UNHEALTHY = 'unhealthy'
    OFFLINE = 'offline'

class FailoverStrategy(Enum):
    """故障转移策略"""
    PRIORITY = 'priority'
    ROUND_ROBIN = 'round_robin'
    WEIGHTED = 'weighted'

@dataclass
class DataSource:
    """数据源"""
    source_id: str
    name: str
    endpoint: str
    priority: int
    weight: float = 1.0
    status: DataSourceStatus = DataSourceStatus.HEALTHY
    last_check_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    failure_count: int = 0
    success_count: int = 0
    avg_response_time: float = 0.0
    metadata: Dict = field(default_factory=dict)

@dataclass
class FailoverEvent:
    """故障转移事件"""
    event_id: str
    source_id: str
    event_type: str
    old_status: DataSourceStatus
    new_status: DataSourceStatus
    timestamp: datetime
    reason: str
    metadata: Dict = field(default_factory=dict)

class DataSourceFailoverManager:
    """数据源故障转移管理器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.data_sources: Dict[str, DataSource] = {}
        self.active_source_id: Optional[str] = None
        self.failover_strategy = FailoverStrategy(
            config.get('failover_strategy', 'priority')
        )
        self.health_check_interval = config.get('health_check_interval', 30)
        self.failure_threshold = config.get('failure_threshold', 3)
        self.recovery_threshold = config.get('recovery_threshold', 2)
        
        self.circuit_breakers: Dict[str, pybreaker.CircuitBreaker] = {}
        self.event_queue: Queue = Queue()
        self.health_check_thread: Optional[threading.Thread] = None
        self.running = False
        
        self._initialize_data_sources()
        self._initialize_circuit_breakers()
    
    def _initialize_data_sources(self):
        """初始化数据源"""
        
        sources_config = self.config.get('data_sources', [])
        
        for source_config in sources_config:
            source = DataSource(
                source_id=source_config['id'],
                name=source_config['name'],
                endpoint=source_config['endpoint'],
                priority=source_config.get('priority', 1),
                weight=source_config.get('weight', 1.0),
                metadata=source_config.get('metadata', {})
            )
            
            self.data_sources[source.source_id] = source
        
        if self.data_sources:
            self.active_source_id = self._select_active_source()
    
    def _initialize_circuit_breakers(self):
        """初始化熔断器"""
        
        for source_id in self.data_sources:
            self.circuit_breakers[source_id] = pybreaker.CircuitBreaker(
                fail_max=self.failure_threshold,
                reset_timeout=60
            )
    
    def start_health_check(self):
        """启动健康检查"""
        
        if self.running:
            return
        
        self.running = True
        self.health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self.health_check_thread.start()
        
        logger.info("Health check thread started")
    
    def stop_health_check(self):
        """停止健康检查"""
        
        self.running = False
        
        if self.health_check_thread:
            self.health_check_thread.join(timeout=5)
        
        logger.info("Health check thread stopped")
    
    def _health_check_loop(self):
        """健康检查循环"""
        
        while self.running:
            try:
                self._check_all_sources()
                time.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health check error: {e}")
                time.sleep(5)
    
    def _check_all_sources(self):
        """检查所有数据源"""
        
        for source_id, source in self.data_sources.items():
            try:
                is_healthy = self._check_source_health(source)
                
                old_status = source.status
                
                if is_healthy:
                    source.status = DataSourceStatus.HEALTHY
                    source.last_success_time = datetime.now()
                    source.success_count += 1
                    source.failure_count = 0
                else:
                    source.failure_count += 1
                    
                    if source.failure_count >= self.failure_threshold:
                        source.status = DataSourceStatus.UNHEALTHY
                
                source.last_check_time = datetime.now()
                
                if old_status != source.status:
                    self._record_failover_event(
                        source_id,
                        'status_change',
                        old_status,
                        source.status,
                        f"Health check: {'healthy' if is_healthy else 'unhealthy'}"
                    )
                    
                    if source_id == self.active_source_id and source.status == DataSourceStatus.UNHEALTHY:
                        self._perform_failover()
            
            except Exception as e:
                logger.error(f"Error checking source {source_id}: {e}")
    
    def _check_source_health(self, source: DataSource) -> bool:
        """检查数据源健康状态"""
        
        try:
            start_time = time.time()
            
            response = requests.get(
                f"{source.endpoint}/health",
                timeout=5
            )
            
            response_time = time.time() - start_time
            
            source.avg_response_time = (
                source.avg_response_time * 0.9 + response_time * 0.1
            )
            
            if response.status_code == 200:
                return True
            else:
                return False
        
        except Exception as e:
            logger.warning(f"Health check failed for {source.source_id}: {e}")
            return False
    
    def _select_active_source(self) -> Optional[str]:
        """选择活跃数据源"""
        
        healthy_sources = [
            s for s in self.data_sources.values()
            if s.status == DataSourceStatus.HEALTHY
        ]
        
        if not healthy_sources:
            logger.error("No healthy data sources available")
            return None
        
        if self.failover_strategy == FailoverStrategy.PRIORITY:
            healthy_sources.sort(key=lambda s: s.priority)
            return healthy_sources[0].source_id
        
        elif self.failover_strategy == FailoverStrategy.ROUND_ROBIN:
            return healthy_sources[0].source_id
        
        elif self.failover_strategy == FailoverStrategy.WEIGHTED:
            import random
            total_weight = sum(s.weight for s in healthy_sources)
            r = random.uniform(0, total_weight)
            
            cumulative = 0
            for source in healthy_sources:
                cumulative += source.weight
                if r <= cumulative:
                    return source.source_id
            
            return healthy_sources[0].source_id
        
        return healthy_sources[0].source_id
    
    def _perform_failover(self):
        """执行故障转移"""
        
        old_active = self.active_source_id
        
        new_active = self._select_active_source()
        
        if new_active and new_active != old_active:
            self.active_source_id = new_active
            
            self._record_failover_event(
                new_active,
                'failover',
                DataSourceStatus.UNHEALTHY,
                DataSourceStatus.HEALTHY,
                f"Failover from {old_active} to {new_active}"
            )
            
            logger.warning(f"Failover: {old_active} -> {new_active}")
        else:
            logger.error("Failover failed: no healthy source available")
    
    def _record_failover_event(self,
                               source_id: str,
                               event_type: str,
                               old_status: DataSourceStatus,
                               new_status: DataSourceStatus,
                               reason: str):
        """记录故障转移事件"""
        
        event = FailoverEvent(
            event_id=f"EVT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_id=source_id,
            event_type=event_type,
            old_status=old_status,
            new_status=new_status,
            timestamp=datetime.now(),
            reason=reason
        )
        
        self.event_queue.put(event)
    
    def get_data(self, request: Dict) -> Optional[Dict]:
        """获取数据"""
        
        if not self.active_source_id:
            logger.error("No active data source")
            return None
        
        source = self.data_sources[self.active_source_id]
        
        try:
            with self.circuit_breakers[self.active_source_id]:
                response = requests.post(
                    f"{source.endpoint}/data",
                    json=request,
                    timeout=10
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Data request failed: {response.status_code}")
                    return None
        
        except pybreaker.CircuitBreakerError:
            logger.error(f"Circuit breaker open for {self.active_source_id}")
            self._perform_failover()
            return None
        
        except Exception as e:
            logger.error(f"Data request error: {e}")
            return None
    
    def get_failover_status(self) -> Dict:
        """获取故障转移状态"""
        
        return {
            'active_source': self.active_source_id,
            'data_sources': {
                source_id: {
                    'name': source.name,
                    'status': source.status.value,
                    'priority': source.priority,
                    'failure_count': source.failure_count,
                    'avg_response_time': source.avg_response_time
                }
                for source_id, source in self.data_sources.items()
            },
            'recent_events': self._get_recent_events(10)
        }
    
    def _get_recent_events(self, limit: int = 10) -> List[Dict]:
        """获取最近事件"""
        
        events = []
        temp_queue = Queue()
        
        while not self.event_queue.empty() and len(events) < limit:
            event = self.event_queue.get()
            events.append({
                'event_id': event.event_id,
                'source_id': event.source_id,
                'event_type': event.event_type,
                'old_status': event.old_status.value,
                'new_status': event.new_status.value,
                'timestamp': event.timestamp.isoformat(),
                'reason': event.reason
            })
            temp_queue.put(event)
        
        while not temp_queue.empty():
            self.event_queue.put(temp_queue.get())
        
        return events
```

---

## 三、接口设计

### 3.1 核心接口

```python
class DataSourceFailoverInterface:
    """数据源故障转移接口"""
    
    def get_data(self, request: Dict) -> Optional[Dict]:
        """获取数据"""
        pass
    
    def get_active_source(self) -> Optional[str]:
        """获取活跃数据源"""
        pass
    
    def get_failover_status(self) -> Dict:
        """获取故障转移状态"""
        pass
```

### 3.2 数据接口

```python
@dataclass
class FailoverConfig:
    """故障转移配置"""
    failover_strategy: str
    health_check_interval: int
    failure_threshold: int
    recovery_threshold: int
    data_sources: List[Dict]
```

---

## 四、实施路径

### 4.1 实施步骤

| 阶段 | 任务 | 时间 | 交付物 |
|------|------|------|--------|
| Phase 1 | 健康检查开发 | 3天 | 健康检查模块 |
| Phase 2 | 故障检测开发 | 2天 | 故障检测模块 |
| Phase 3 | 自动切换开发 | 2天 | 自动切换模块 |
| Phase 4 | 测试验证 | 2天 | 测试报告 |

### 4.2 依赖安装

```bash
pip install pybreaker
pip install requests
pip install prometheus-client
```

### 4.3 配置示例

```yaml
failover:
  strategy: 'priority'
  health_check_interval: 30
  failure_threshold: 3
  recovery_threshold: 2
  
data_sources:
  - id: 'primary'
    name: 'Primary Data Source'
    endpoint: 'http://primary.example.com'
    priority: 1
    weight: 1.0
    
  - id: 'backup1'
    name: 'Backup Data Source 1'
    endpoint: 'http://backup1.example.com'
    priority: 2
    weight: 0.8
    
  - id: 'backup2'
    name: 'Backup Data Source 2'
    endpoint: 'http://backup2.example.com'
    priority: 3
    weight: 0.6
```

---

## 五、质量保证

### 5.1 测试标准

- 单元测试覆盖率 ≥ 80%
- 集成测试通过率 = 100%
- 故障转移时间 < 5秒

### 5.2 可用性标准

- 系统可用性 ≥ 99.9%
- 故障检测时间 < 30秒
- 数据一致性保证 = 100%

---

## 六、成本评估

| 成本项 | 数量 | 单价 | 总价 |
|--------|------|------|------|
| 开发时间 | 2周 | - | ¥0 |
| 云服务器 | 1个月 | ¥500 | ¥500 |
| 备用数据源 | 1个月 | ¥300 | ¥300 |
| **总计** | - | - | **¥800** |

---

**版本**: v1.0 | **更新**: 2026-04-07 | **状态**: ✅ 活跃
