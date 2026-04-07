---
module_id: DATA_SUBSCRIPTION_SERVICE_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构蓝图
applicable_scope: Layer 1 数据�?
compliance_level: 专业标准
responsibility:
  - 数据订阅服务
  - 数据订阅管理
  - 消息推�?
  - 实时数据分发
layer: "Layer 1 (数据�?"
---

# 数据订阅服务蓝图

> **核心职责**: 实时数据分发、数据订阅管理、消息推�?
> **职责边界**: 
> - �?本模块负责：实时数据推送、订阅管理、消息队�?
> - �?本模块不负责：数据存储、数据处理、API服务

## 核心定位

**单一职责**: 实时数据分发与订阅管�?

### 职责边界

| 负责 | 不负�?|
|------|--------|
| �?实时数据推�?| �?数据存储 |
| �?订阅管理 | �?数据处理 |
| �?消息队列 | �?API服务 |
| �?消费者组 | �?数据清洗 |
| �?消息持久�?| �?数据质量 |

---

## 1. 技术选型

### 1.1 为什么选择Redis Streams

| 特�?| Redis Streams | Kafka | RabbitMQ |
|------|---------------|-------|----------|
| 吞吐�?| ⭐⭐⭐⭐ | ⭐⭐⭐⭐�?| ⭐⭐�?|
| 延迟 | ⭐⭐⭐⭐�?| ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 持久�?| �?�?| �?�?| �?�?|
| 部署复杂�?| ⭐⭐⭐⭐�?| ⭐⭐ | ⭐⭐�?|
| 学习曲线 | ⭐⭐⭐⭐�?| ⭐⭐�?| ⭐⭐⭐⭐ |
| 个人适用�?| ⭐⭐⭐⭐�?| ⭐⭐�?| ⭐⭐⭐⭐ |
| **推荐指数** | **⭐⭐⭐⭐�?* | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────�?
�?                   数据订阅服务架构                              �?
├─────────────────────────────────────────────────────────────────�?
�?                                                                �?
�? ┌──────────────�?   ┌──────────────�?   ┌──────────────�?    �?
�? �?数据发布�?  �?   �?消息队列�?  �?   �?数据消费�?  �?    �?
�? �?             �?   �?             �?   �?             �?    �?
�? �?�?行情发布   �?   �?�?Streams    �?   �?�?订阅管理   �?    �?
�? �?�?因子发布   �?   �?�?消费者组   �?   �?�?消息分发   �?    �?
�? �?�?事件发布   �?   �?�?消息确认   �?   �?�?错误处理   �?    �?
�? └──────────────�?   └──────────────�?   └──────────────�?    �?
�?        �?                  �?                   �?             �?
�?        └───────────────────┴────────────────────�?             �?
�?                           �?                                   �?
�? ┌─────────────────────────────────────────────────────────�?  �?
�? �?                   订阅类型                              �?  �?
�? �? �?行情订阅 (实时价格)                                   �?  �?
�? �? �?因子订阅 (因子更新)                                   �?  �?
�? �? �?事件订阅 (系统事件)                                   �?  �?
�? └─────────────────────────────────────────────────────────�?  �?
�?                                                                �?
└─────────────────────────────────────────────────────────────────�?
```

---

## 3. 核心功能实现

### 3.1 数据发布服务

```python
import redis
import json
from typing import Dict, List
from datetime import datetime

class DataPublisher:
    """数据发布�?""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def publish_price(self, symbol: str, price_data: Dict):
        """发布实时价格"""
        stream_name = f"stream:price:{symbol}"
        message = {
            "symbol": symbol,
            "price": price_data["price"],
            "volume": price_data.get("volume", 0),
            "timestamp": datetime.now().isoformat()
        }
        return self.redis.xadd(stream_name, message)
    
    def publish_factor(self, factor_id: str, factor_data: Dict):
        """发布因子更新"""
        stream_name = f"stream:factor:{factor_id}"
        message = {
            "factor_id": factor_id,
            "values": json.dumps(factor_data["values"]),
            "timestamp": datetime.now().isoformat()
        }
        return self.redis.xadd(stream_name, message)
    
    def publish_event(self, event_type: str, event_data: Dict):
        """发布系统事件"""
        stream_name = "stream:events"
        message = {
            "event_type": event_type,
            "data": json.dumps(event_data),
            "timestamp": datetime.now().isoformat()
        }
        return self.redis.xadd(stream_name, message)
```

### 3.2 订阅管理服务

```python
class SubscriptionManager:
    """订阅管理�?""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.subscriptions = {}
    
    def subscribe(self, client_id: str, stream_type: str, stream_id: str):
        """订阅数据�?""
        key = f"subscription:{client_id}"
        stream_name = f"stream:{stream_type}:{stream_id}"
        
        self.redis.sadd(key, stream_name)
        
        if stream_name not in self.subscriptions:
            self.subscriptions[stream_name] = set()
        self.subscriptions[stream_name].add(client_id)
        
        return True
    
    def unsubscribe(self, client_id: str, stream_type: str, stream_id: str):
        """取消订阅"""
        key = f"subscription:{client_id}"
        stream_name = f"stream:{stream_type}:{stream_id}"
        
        self.redis.srem(key, stream_name)
        
        if stream_name in self.subscriptions:
            self.subscriptions[stream_name].discard(client_id)
        
        return True
    
    def get_subscriptions(self, client_id: str) -> List[str]:
        """获取客户端订阅列�?""
        key = f"subscription:{client_id}"
        return list(self.redis.smembers(key))
```

### 3.3 消费者服�?

```python
import asyncio
from typing import Callable

class DataConsumer:
    """数据消费�?""
    
    def __init__(self, redis_client: redis.Redis, group_name: str, consumer_name: str):
        self.redis = redis_client
        self.group_name = group_name
        self.consumer_name = consumer_name
        self.running = False
    
    async def consume(
        self,
        stream_name: str,
        callback: Callable,
        count: int = 10,
        block: int = 1000
    ):
        """消费数据�?""
        try:
            self.redis.xgroup_create(stream_name, self.group_name, id='0')
        except redis.ResponseError:
            pass
        
        self.running = True
        
        while self.running:
            messages = self.redis.xreadgroup(
                groupname=self.group_name,
                consumername=self.consumer_name,
                streams={stream_name: '>'},
                count=count,
                block=block
            )
            
            if messages:
                for stream, msgs in messages:
                    for msg_id, data in msgs:
                        try:
                            await callback(data)
                            self.redis.xack(stream_name, self.group_name, msg_id)
                        except Exception as e:
                            print(f"处理消息失败: {e}")
    
    def stop(self):
        """停止消费"""
        self.running = False
```

---

## 4. WebSocket推�?

```python
from fastapi import WebSocket, WebSocketDisconnect
import asyncio

class WebSocketManager:
    """WebSocket连接管理�?""
    
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, client_id: str, websocket: WebSocket):
        """建立连接"""
        await websocket.accept()
        if client_id not in self.connections:
            self.connections[client_id] = []
        self.connections[client_id].append(websocket)
    
    def disconnect(self, client_id: str, websocket: WebSocket):
        """断开连接"""
        if client_id in self.connections:
            self.connections[client_id].remove(websocket)
    
    async def broadcast(self, client_id: str, message: dict):
        """广播消息"""
        if client_id in self.connections:
            for ws in self.connections[client_id]:
                await ws.send_json(message)
```

---

## 📋 变更历史

| 版本 | 日期 | 变更内容 | 作�?|
|------|------|---------|------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 首席架构�?|

---

**文档结束**
