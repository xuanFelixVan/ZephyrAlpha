---
module_id: UNIFIED_DATA_API_GATEWAY_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 1 æ°æ®å±?
compliance_level: ä¸ä¸æ å
responsibility:
  - ç»ä¸æ°æ®APIç½å³
  - æ°æ®æ¥è¯¢æå¡
  - APIè®¤è¯ææ
  - éæµçæ­
layer: Layer 5 (策略执行层)
---

# ç»ä¸æ°æ®APIç½å³èå¾

> **æ ¸å¿èè´£**: ç»ä¸æ°æ®è®¿é®å¥å£ãè®¤è¯ææãéæµçæ­ãç¼å­ç­ç?
> **èè´£è¾¹ç**: 
> - â?æ¬æ¨¡åè´è´£ï¼ç»ä¸APIå¥å£ãè®¤è¯ææãéæµçæ­ãç¼å­ãGraphQLæ¯æ
> - â?æ¬æ¨¡åä¸è´è´£ï¼æ°æ®å­å¨ãæ°æ®å¤çãæ°æ®è®¢é?

## æ ¸å¿å®ä½

**åä¸èè´£**: ç»ä¸æ°æ®è®¿é®å¥å£ä¸APIç®¡ç

### èè´£è¾¹ç

| è´è´£ | ä¸è´è´?|
|------|--------|
| â?RESTful API | â?æ°æ®å­å¨ |
| â?GraphQL API | â?æ°æ®å¤ç |
| â?è®¤è¯ææ | â?æ°æ®è®¢é |
| â?éæµçæ­ | â?æ°æ®æ¸æ´ |
| â?ç¼å­ç­ç¥ | â?æ°æ®è´¨é |

---

## 1. ææ¯éå

### 1.1 ä¸ºä»ä¹éæ©FastAPI + Strawberry

| ç¹æ?| FastAPI | Flask | Django |
|------|---------|-------|--------|
| æ§è½ | â­â­â­â­â­?| â­â­â­?| â­â­â­â­ |
| å¼æ­¥æ¯æ | â?åç | â?éæ©å± | â?æ¯æ |
| ç±»åæç¤º | â?Pydantic | â?æ?| â­â­â­?|
| èªå¨ææ¡£ | â?OpenAPI | â?éæ©å± | â?æ¯æ |
| å­¦ä¹ æ²çº¿ | â­â­â­â­â­?| â­â­â­â­â­?| â­â­â­?|
| GraphQL | â?Strawberry | â?Ariadne | â?Graphene |
| **æ¨èææ°** | **â­â­â­â­â­?* | â­â­â­â­ | â­â­â­â­ |

---

## 2. æ¶æè®¾è®¡

### 2.1 æ´ä½æ¶æ

```
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                   ç»ä¸æ°æ®APIç½å³æ¶æ                           â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
â?                                                                â?
â? ââââââââââââââââ?   ââââââââââââââââ?   ââââââââââââââââ?    â?
â? â?APIå¥å£å±?   â?   â?è®¤è¯ææå±?  â?   â?éæµçæ­å±?  â?    â?
â? â?             â?   â?             â?   â?             â?    â?
â? â?â?REST API   â?   â?â?JWTè®¤è¯    â?   â?â?éæµæ§å¶   â?    â?
â? â?â?GraphQL    â?   â?â?API Key    â?   â?â?çæ­éçº§   â?    â?
â? â?â?WebSocket  â?   â?â?æéæ§å¶   â?   â?â?è´è½½åè¡¡   â?    â?
â? ââââââââââââââââ?   ââââââââââââââââ?   ââââââââââââââââ?    â?
â?        â?                  â?                   â?             â?
â?        âââââââââââââââââââââ´âââââââââââââââââââââ?             â?
â?                           â?                                   â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â? â?                   ç¼å­å±?                               â?  â?
â? â? â?Redisç¼å­ (ç­ç¹æ°æ®)                                  â?  â?
â? â? â?ååºç¼å­ (æ¥è¯¢ç»æ)                                   â?  â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â?                           â?                                   â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â? â?                   æ°æ®æºå±                              â?  â?
â? â? â?TimescaleDB (å®æ¶æ°æ®)                                â?  â?
â? â? â?ClickHouse (åå²æ°æ®)                                 â?  â?
â? â? â?Redis (ç¼å­æ°æ®)                                      â?  â?
â? âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?  â?
â?                                                                â?
âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?
```

---

## 3. æ ¸å¿åè½å®ç°

### 3.1 RESTful API

```python
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="Zephyr Quant Data API",
    description="ç»ä¸æ°æ®APIç½å³",
    version="1.0.0"
)

security = HTTPBearer()

class KlineRequest(BaseModel):
    symbol: str
    interval: str
    start_date: str
    end_date: str

class KlineResponse(BaseModel):
    open_time: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int

@app.get("/api/v1/klines/{symbol}", response_model=List[KlineResponse])
@cache(expire=60)
async def get_klines(
    symbol: str,
    interval: str = Query(default="1d"),
    start_date: str = Query(...),
    end_date: str = Query(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """è·åKçº¿æ°æ?""
    pass

@app.get("/api/v1/factors/{factor_id}")
@cache(expire=300)
async def get_factor_values(
    factor_id: str,
    symbols: List[str] = Query(...),
    date: str = Query(...)
):
    """è·åå å­å?""
    pass

@app.get("/api/v1/prices/realtime")
async def get_realtime_prices(
    symbols: List[str] = Query(...)
):
    """è·åå®æ¶ä»·æ ¼"""
    pass
```

### 3.2 GraphQL API

```python
import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional

@strawberry.type
class Kline:
    open_time: str
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int

@strawberry.type
class Query:
    @strawberry.field
    async def klines(
        self,
        symbol: str,
        interval: str = "1d",
        start_date: str = "",
        end_date: str = ""
    ) -> List[Kline]:
        pass
    
    @strawberry.field
    async def factor_values(
        self,
        factor_id: str,
        symbols: List[str],
        date: str
    ) -> List[dict]:
        pass

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
```

### 3.3 è®¤è¯ææ

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload
```

### 3.4 éæµçæ­

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/klines/{symbol}")
@limiter.limit("100/minute")
async def get_klines(request: Request, symbol: str):
    pass
```

---

## 4. é¨ç½²éç½®

### 4.1 Dockeré¨ç½²

```yaml
version: '3.8'

services:
  api-gateway:
    build: .
    container_name: zephyr_api_gateway
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - TIMESCALEDB_URL=postgresql://zephyr:password@timescaledb:5432/zephyr
      - CLICKHOUSE_URL=clickhouse://clickhouse:9000/zephyr
    depends_on:
      - redis
      - timescaledb
      - clickhouse
    restart: unless-stopped
```

---

## ð åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | ä½è?|
|------|------|---------|------|
| v1.0.0 | 2026-04-07 | åå§çæ¬åå»º | é¦å¸­æ¶æå¸?|

---

**ææ¡£ç»æ**
