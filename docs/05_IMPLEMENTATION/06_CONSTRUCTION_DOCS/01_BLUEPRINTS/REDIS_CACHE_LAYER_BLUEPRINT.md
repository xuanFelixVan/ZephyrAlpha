---
module_id: REDIS_CACHE_LAYER_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 1 æ°æ®å±?
compliance_level: ä¸ä¸æ å
responsibility:
  - Redisç¼å­å±?
  - æ°æ®ç¼å­
  - ä¼è¯ç®¡ç
  - åå¸å¼é
layer: Layer 5.1 (数据处理)
---

# Redisç¼å­å±éæèå?

> **æ ¸å¿èè´£**: æ°æ®ç¼å­ãä¼è¯ç®¡çãåå¸å¼éãæ¶æ¯éå?
> **èè´£è¾¹ç**: 
> - â?æ¬æ¨¡åè´è´£ï¼ç­ç¹æ°æ®ç¼å­ãä¼è¯ç®¡çãåå¸å¼éãè½»éæ¶æ¯éå?
> - â?æ¬æ¨¡åä¸è´è´£ï¼æä¹åå­å¨ï¼TimescaleDB/ClickHouseï¼ãå¤§æ°æ®å¤ç

## æ ¸å¿å®ä½

**åä¸èè´£**: æ°æ®ç¼å­ãä¼è¯ç®¡çãåå¸å¼é?

### èè´£è¾¹ç

| è´è´£ | ä¸è´è´?|
|------|--------|
| â?å®æ¶è¡æç¼å­ | â?æä¹åæ°æ®å­å?|
| â?å å­å¼ç¼å­?| â?å¤§è§æ¨¡æ°æ®åæ?|
| â?ä¼è¯ç®¡ç | â?æ°æ®æ¸æ´å¤ç |
| â?åå¸å¼é | â?æ°æ®è¡ç¼è¿½è¸?|
| â?æ¶æ¯éåï¼è½»éï¼ | â?éåæ¶æ¯ç³»ç» |

---

## 1. ææ¯éå

### 1.1 ä¸ºä»ä¹éæ©Redis

| ç¹æ?| Redis | KeyDB | Dragonfly |
|------|-------|-------|-----------|
| æ§è½ | â­â­â­â­ | â­â­â­â­â­?| â­â­â­â­â­?|
| çæ?| â­â­â­â­â­?| â­â­â­?| â­â­ |
| å­¦ä¹ æ²çº¿ | â­â­â­â­â­?| â­â­â­â­â­?| â­â­â­â­ |
| Pythonæ¯æ | â?redis-py | â?redis-py | â?redis-py |
| ç¤¾åºæ´»è·åº?| â­â­â­â­â­?| â­â­â­?| â­â­ |
| ææ¡£å®ååº?| â­â­â­â­â­?| â­â­â­?| â­â­ |
| **æ¨èææ°** | **â­â­â­â­â­?* | â­â­â­â­ | â­â­â­?|

---

## 2. æ¶æè®¾è®¡

### 2.1 æ´ä½æ¶æ

```
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                   Redisç¼å­å±æ¶æ?                              â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                                                                â?
â? ââââââââââââââââ?   ââââââââââââââââ?   ââââââââââââââââ?    â?
â? â?æ°æ®ç¼å­å±?  â?   â?ä¼è¯ç®¡çå±?  â?   â?åå¸å¼éå±?  â?    â?
â? â?             â?   â?             â?   â?             â?    â?
â? â?â?è¡æç¼å­   â?   â?â?Tokenå­å¨  â?   â?â?ä»»å¡é?    â?    â?
â? â?â?å å­ç¼å­   â?   â?â?ç¨æ·ä¼è¯   â?   â?â?èµæºé?    â?    â?
â? â?â?éç½®ç¼å­   â?   â?â?æéç¼å­   â?   â?â?éæµé?    â?    â?
â? ââââââââââââââââ?   ââââââââââââââââ?   ââââââââââââââââ?    â?
â?        â?                  â?                   â?             â?
â?        âââââââââââââââââââââ´âââââââââââââââââââââ?             â?
â?                           â?                                   â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â? â?                   æ¶æ¯éåå±?                           â?  â?
â? â? â?Redis Streams (å®æ¶æ°æ®æ¨é?                          â?  â?
â? â? â?Pub/Sub (äºä»¶éç¥)                                    â?  â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â?                                                                â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
```

---

## 3. æ ¸å¿åè½å®ç°

### 3.1 æ°æ®ç¼å­

```python
import redis
import json
from typing import Optional, Any, List
from datetime import timedelta

class DataCache:
    """æ°æ®ç¼å­ç®¡çå?""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
    
    def cache_realtime_price(self, symbol: str, price: float, ttl: int = 5):
        """ç¼å­å®æ¶ä»·æ ¼ï¼?ç§è¿æï¼"""
        key = f"price:realtime:{symbol}"
        self.client.setex(key, ttl, str(price))
    
    def get_realtime_prices(self, symbols: List[str]) -> dict:
        """æ¹éè·åå®æ¶ä»·æ ¼"""
        pipe = self.client.pipeline()
        for symbol in symbols:
            pipe.get(f"price:realtime:{symbol}")
        results = pipe.execute()
        return {s: float(r) for s, r in zip(symbols, results) if r}
    
    def cache_factor_values(self, factor_id: str, values: dict, ttl: int = 3600):
        """ç¼å­å å­å¼ï¼1å°æ¶è¿æï¼?""
        key = f"factor:{factor_id}"
        self.client.setex(key, ttl, json.dumps(values))
    
    def get_factor_values(self, factor_id: str) -> Optional[dict]:
        """è·åå å­å?""
        key = f"factor:{factor_id}"
        data = self.client.get(key)
        return json.loads(data) if data else None
    
    def cache_market_snapshot(self, snapshot: dict, ttl: int = 60):
        """ç¼å­å¸åºå¿«ç§ï¼?åéè¿æï¼?""
        key = "market:snapshot"
        self.client.setex(key, ttl, json.dumps(snapshot))
```

### 3.2 åå¸å¼é

```python
import uuid
import time

class DistributedLock:
    """åå¸å¼é"""
    
    def __init__(self, client: redis.Redis):
        self.client = client
    
    def acquire(self, lock_name: str, timeout: int = 10, retry_interval: float = 0.1) -> bool:
        """è·åé?""
        identifier = str(uuid.uuid4())
        lock_key = f"lock:{lock_name}"
        
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.client.set(lock_key, identifier, nx=True, ex=timeout):
                return identifier
            time.sleep(retry_interval)
        
        return None
    
    def release(self, lock_name: str, identifier: str) -> bool:
        """éæ¾é?""
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
    """ä»»å¡é?""
    
    def __init__(self, client: redis.Redis):
        self.lock = DistributedLock(client)
    
    def __enter__(self):
        self.identifier = self.lock.acquire(self.task_name)
        if not self.identifier:
            raise Exception(f"æ æ³è·åä»»å¡é? {self.task_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release(self.task_name, self.identifier)
```

### 3.3 æ¶æ¯éåï¼Redis Streamsï¼?

```python
class DataStream:
    """æ°æ®æµï¼Redis Streamsï¼?""
    
    def __init__(self, client: redis.Redis, stream_name: str):
        self.client = client
        self.stream_name = stream_name
    
    def publish(self, data: dict) -> str:
        """åå¸æ¶æ¯"""
        return self.client.xadd(self.stream_name, data)
    
    def consume(self, group: str, consumer: str, count: int = 10) -> list:
        """æ¶è´¹æ¶æ¯"""
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
        """ç¡®è®¤æ¶æ¯"""
        self.client.xack(self.stream_name, group, message_id)
```

---

## 4. é¨ç½²éç½®

### 4.1 Dockeré¨ç½²

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

## ð åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | ä½è?|
|------|------|---------|------|
| v1.0.0 | 2026-04-07 | åå§çæ¬åå»º | é¦å¸­æ¶æå¸?|

---

**ææ¡£ç»æ**
