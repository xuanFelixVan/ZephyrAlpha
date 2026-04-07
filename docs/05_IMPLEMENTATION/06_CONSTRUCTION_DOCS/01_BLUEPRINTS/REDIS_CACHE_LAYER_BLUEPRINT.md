---
module_id: REDIS_CACHE_LAYER_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
  - 实施指南、部署文档
  - 会话管理
  - 分布式锁
layer: "Layer 1 (数据预处理层)"
---

# Redis缓存层集成蓝图

> **核心职责**: 数据缓存、会话管理、分布式锁、消息队列
> **职责边界**: 
> - ✅ 本模块负责：热点数据缓存、会话管理、分布式锁、轻量消息队列
> - ❌ 本模块不负责：持久化存储（TimescaleDB/ClickHouse）、大数据处理

## 核心定位

**单一职责**: 数据缓存、会话管理、分布式锁

### 职责边界

| 负责 | 不负责 |
|------|--------|
| ✅ 实时行情缓存 | ❌ 持久化数据存储 |
| ✅ 因子值缓存 | ❌ 大规模数据分析 |
| ✅ 会话管理 | ❌ 数据清洗处理 |
| ✅ 分布式锁 | ❌ 数据血缘追踪 |
| ✅ 消息队列（轻量） | ❌ 重型消息系统 |

---

## 1. 技术选型

### 1.1 为什么选择Redis

| 特性 | Redis | KeyDB | Dragonfly |
|------|-------|-------|-----------|
| 性能 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 生态 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 学习曲线 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Python支持 | ✅ redis-py | ✅ redis-py | ✅ redis-py |
| 社区活跃度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 文档完善度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **推荐指数** | **⭐⭐⭐⭐⭐** | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Redis缓存层架构                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ 数据缓存层   │    │ 会话管理层   │    │ 分布式锁层   │     │
│  │              │    │              │    │              │     │
│  │ • 行情缓存   │    │ • Token存储  │    │ • 任务锁     │     │
│  │ • 因子缓存   │    │ • 用户会话   │    │ • 资源锁     │     │
│  │ • 配置缓存   │    │ • 权限缓存   │    │ • 限流锁     │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│         │                   │                    │              │
│         └───────────────────┴────────────────────┘              │
│                            │                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    消息队列层                            │   │
│  │  • Redis Streams (实时数据推送)                          │   │
│  │  • Pub/Sub (事件通知)                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 核心功能实现

### 3.1 数据缓存

```python
import redis
import json
from typing import Optional, Any, List
from datetime import timedelta

class DataCache:
    """数据缓存管理器"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
    
    def cache_realtime_price(self, symbol: str, price: float, ttl: int = 5):
        """缓存实时价格（5秒过期）"""
        key = f"price:realtime:{symbol}"
        self.client.setex(key, ttl, str(price))
    
    def get_realtime_prices(self, symbols: List[str]) -> dict:
        """批量获取实时价格"""
        pipe = self.client.pipeline()
        for symbol in symbols:
            pipe.get(f"price:realtime:{symbol}")
        results = pipe.execute()
        return {s: float(r) for s, r in zip(symbols, results) if r}
    
    def cache_factor_values(self, factor_id: str, values: dict, ttl: int = 3600):
        """缓存因子值（1小时过期）"""
        key = f"factor:{factor_id}"
        self.client.setex(key, ttl, json.dumps(values))
    
    def get_factor_values(self, factor_id: str) -> Optional[dict]:
        """获取因子值"""
        key = f"factor:{factor_id}"
        data = self.client.get(key)
        return json.loads(data) if data else None
    
    def cache_market_snapshot(self, snapshot: dict, ttl: int = 60):
        """缓存市场快照（1分钟过期）"""
        key = "market:snapshot"
        self.client.setex(key, ttl, json.dumps(snapshot))
```

### 3.2 分布式锁

```python
import uuid
import time

class DistributedLock:
    """分布式锁"""
    
    def __init__(self, client: redis.Redis):
        self.client = client
    
    def acquire(self, lock_name: str, timeout: int = 10, retry_interval: float = 0.1) -> bool:
        """获取锁"""
        identifier = str(uuid.uuid4())
        lock_key = f"lock:{lock_name}"
        
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.client.set(lock_key, identifier, nx=True, ex=timeout):
                return identifier
            time.sleep(retry_interval)
        
        return None
    
    def release(self, lock_name: str, identifier: str) -> bool:
        """释放锁"""
        lock_key = f"lock:{lock_name}"
        
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        return bool(self.client.eval(script, 1, lock_key, identifier))

class TaskLock:
    """任务锁"""
    
    def __init__(self, client: redis.Redis):
        self.lock = DistributedLock(client)
    
    def __enter__(self):
        self.identifier = self.lock.acquire(self.task_name)
        if not self.identifier:
            raise Exception(f"无法获取任务锁: {self.task_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release(self.task_name, self.identifier)
```

### 3.3 消息队列（Redis Streams）

```python
class DataStream:
    """数据流（Redis Streams）"""
    
    def __init__(self, client: redis.Redis, stream_name: str):
        self.client = client
        self.stream_name = stream_name
    
    def publish(self, data: dict) -> str:
        """发布消息"""
        return self.client.xadd(self.stream_name, data)
    
    def consume(self, group: str, consumer: str, count: int = 10) -> list:
        """消费消息"""
        try:
            self.client.xgroup_create(self.stream_name, group, id='0')
        except redis.ResponseError:
            pass
        
        messages = self.client.xreadgroup(
            groupname=group,
            consumername=consumer,
            streams={self.stream_name: '>'},
            count=count
        )
        
        return messages
    
    def ack(self, group: str, message_id: str):
        """确认消息"""
        self.client.xack(self.stream_name, group, message_id)
```

---

## 4. 部署配置

### 4.1 Docker部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: zephyr_redis
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  redis_data:
```

---

## 📋 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 首席架构师 |

---

**文档结束**
