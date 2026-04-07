---
module_id: DATA_SUBSCRIPTION_SERVICE_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 1 æ°æ®å±?
compliance_level: ä¸ä¸æ å
responsibility:
  - æ°æ®è®¢éæå¡
  - æ°æ®è®¢éç®¡ç
  - æ¶æ¯æ¨é?
  - å®æ¶æ°æ®åå
layer: "Layer 1 (æ°æ®å±?"
---

# æ°æ®è®¢éæå¡èå¾

## 核心定位

负责数据订阅服务的设计与实现，基于发布订阅技术，提供数据变更推送，支持实时数据同步。


## æ ¸å¿å®ä½

**åä¸èè´£**: å®æ¶æ°æ®ååä¸è®¢éç®¡ç?

### èè´£è¾¹ç

| è´è´£ | ä¸è´è´?|
|------|--------|
| â?å®æ¶æ°æ®æ¨é?| â?æ°æ®å­å¨ |
| â?è®¢éç®¡ç | â?æ°æ®å¤ç |
| â?æ¶æ¯éå | â?APIæå¡ |
| â?æ¶è´¹èç» | â?æ°æ®æ¸æ´ |
| â?æ¶æ¯æä¹å?| â?æ°æ®è´¨é |

---

## 1. ææ¯éå

### 1.1 ä¸ºä»ä¹éæ©Redis Streams

| ç¹æ?| Redis Streams | Kafka | RabbitMQ |
|------|---------------|-------|----------|
| ååé?| â­â­â­â­ | â­â­â­â­â­?| â­â­â­?|
| å»¶è¿ | â­â­â­â­â­?| â­â­â­â­ | â­â­â­â­ |
| æä¹å?| â?ä¸?| â?å¼?| â?å¼?|
| é¨ç½²å¤æåº?| â­â­â­â­â­?| â­â­ | â­â­â­?|
| å­¦ä¹ æ²çº¿ | â­â­â­â­â­?| â­â­â­?| â­â­â­â­ |
| ä¸ªäººéç¨æ?| â­â­â­â­â­?| â­â­â­?| â­â­â­â­ |
| **æ¨èææ°** | **â­â­â­â­â­?* | â­â­â­â­ | â­â­â­â­ |

---

## 2. æ¶æè®¾è®¡

### 2.1 æ´ä½æ¶æ

```
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                   æ°æ®è®¢éæå¡æ¶æ                              â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                                                                â?
â? ââââââââââââââââ?   ââââââââââââââââ?   ââââââââââââââââ?    â?
â? â?æ°æ®åå¸å±?  â?   â?æ¶æ¯éåå±?  â?   â?æ°æ®æ¶è´¹å±?  â?    â?
â? â?             â?   â?             â?   â?             â?    â?
â? â?â?è¡æåå¸   â?   â?â?Streams    â?   â?â?è®¢éç®¡ç   â?    â?
â? â?â?å å­åå¸   â?   â?â?æ¶è´¹èç»   â?   â?â?æ¶æ¯åå   â?    â?
â? â?â?äºä»¶åå¸   â?   â?â?æ¶æ¯ç¡®è®¤   â?   â?â?éè¯¯å¤ç   â?    â?
â? ââââââââââââââââ?   ââââââââââââââââ?   ââââââââââââââââ?    â?
â?        â?                  â?                   â?             â?
â?        âââââââââââââââââââââ´âââââââââââââââââââââ?             â?
â?                           â?                                   â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â? â?                   è®¢éç±»å                              â?  â?
â? â? â?è¡æè®¢é (å®æ¶ä»·æ ¼)                                   â?  â?
â? â? â?å å­è®¢é (å å­æ´æ°)                                   â?  â?
â? â? â?äºä»¶è®¢é (ç³»ç»äºä»¶)                                   â?  â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â?                                                                â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
```

---

## 3. æ ¸å¿åè½å®ç°

### 3.1 æ°æ®åå¸æå¡

```python
import redis
import json
from typing import Dict, List
from datetime import datetime

class DataPublisher:
    """æ°æ®åå¸å?""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def publish_price(self, symbol: str, price_data: Dict):
        """åå¸å®æ¶ä»·æ ¼"""
        stream_name = f"stream:price:{symbol}"
        message = {
            "symbol": symbol,
            "price": price_data["price"],
            "volume": price_data.get("volume", 0),
            "timestamp": datetime.now().isoformat()
        }
        return self.redis.xadd(stream_name, message)
    
    def publish_factor(self, factor_id: str, factor_data: Dict):
        """åå¸å å­æ´æ°"""
        stream_name = f"stream:factor:{factor_id}"
        message = {
            "factor_id": factor_id,
            "values": json.dumps(factor_data["values"]),
            "timestamp": datetime.now().isoformat()
        }
        return self.redis.xadd(stream_name, message)
    
    def publish_event(self, event_type: str, event_data: Dict):
        """åå¸ç³»ç»äºä»¶"""
        stream_name = "stream:events"
        message = {
            "event_type": event_type,
            "data": json.dumps(event_data),
            "timestamp": datetime.now().isoformat()
        }
        return self.redis.xadd(stream_name, message)
```

### 3.2 è®¢éç®¡çæå¡

```python
class SubscriptionManager:
    """è®¢éç®¡çå?""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.subscriptions = {}
    
    def subscribe(self, client_id: str, stream_type: str, stream_id: str):
        """è®¢éæ°æ®æµ?""
        key = f"subscription:{client_id}"
        stream_name = f"stream:{stream_type}:{stream_id}"
        
        self.redis.sadd(key, stream_name)
        
        if stream_name not in self.subscriptions:
            self.subscriptions[stream_name] = set()
        self.subscriptions[stream_name].add(client_id)
        
        return True
    
    def unsubscribe(self, client_id: str, stream_type: str, stream_id: str):
        """åæ¶è®¢é"""
        key = f"subscription:{client_id}"
        stream_name = f"stream:{stream_type}:{stream_id}"
        
        self.redis.srem(key, stream_name)
        
        if stream_name in self.subscriptions:
            self.subscriptions[stream_name].discard(client_id)
        
        return True
    
    def get_subscriptions(self, client_id: str) -> List[str]:
        """è·åå®¢æ·ç«¯è®¢éåè¡?""
        key = f"subscription:{client_id}"
        return list(self.redis.smembers(key))
```

### 3.3 æ¶è´¹èæå?

```python
import asyncio
from typing import Callable

class DataConsumer:
    """æ°æ®æ¶è´¹è?""
    
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
        """æ¶è´¹æ°æ®æµ?""
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
                            print(f"å¤çæ¶æ¯å¤±è´¥: {e}")
    
    def stop(self):
        """åæ­¢æ¶è´¹"""
        self.running = False
```

---

## 4. WebSocketæ¨é?

```python
from fastapi import WebSocket, WebSocketDisconnect
import asyncio

class WebSocketManager:
    """WebSocketè¿æ¥ç®¡çå?""
    
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, client_id: str, websocket: WebSocket):
        """å»ºç«è¿æ¥"""
        await websocket.accept()
        if client_id not in self.connections:
            self.connections[client_id] = []
        self.connections[client_id].append(websocket)
    
    def disconnect(self, client_id: str, websocket: WebSocket):
        """æ­å¼è¿æ¥"""
        if client_id in self.connections:
            self.connections[client_id].remove(websocket)
    
    async def broadcast(self, client_id: str, message: dict):
        """å¹¿æ­æ¶æ¯"""
        if client_id in self.connections:
            for ws in self.connections[client_id]:
                await ws.send_json(message)
```

---

## ð åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | ä½è?|
|------|------|---------|------|
| v1.0.0 | 2026-04-07 | åå§çæ¬åå»º | é¦å¸­æ¶æå¸?|

---

**ææ¡£ç»æ**
