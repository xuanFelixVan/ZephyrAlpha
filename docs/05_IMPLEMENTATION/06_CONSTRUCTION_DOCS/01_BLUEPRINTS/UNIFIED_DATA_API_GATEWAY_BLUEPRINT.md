---
module_id: UNIFIED_DATA_API_GATEWAY_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
  - 统一数据API
  - 数据查询服务
  - API认证授权
layer: "Layer 1 (数据预处理层)"
---

# 统一数据API网关蓝图

> **核心职责**: 统一数据访问入口、认证授权、限流熔断、缓存策略
> **职责边界**: 
> - ✅ 本模块负责：统一API入口、认证授权、限流熔断、缓存、GraphQL支持
> - ❌ 本模块不负责：数据存储、数据处理、数据订阅

## 核心定位

**单一职责**: 统一数据访问入口与API管理

### 职责边界

| 负责 | 不负责 |
|------|--------|
| ✅ RESTful API | ❌ 数据存储 |
| ✅ GraphQL API | ❌ 数据处理 |
| ✅ 认证授权 | ❌ 数据订阅 |
| ✅ 限流熔断 | ❌ 数据清洗 |
| ✅ 缓存策略 | ❌ 数据质量 |

---

## 1. 技术选型

### 1.1 为什么选择FastAPI + Strawberry

| 特性 | FastAPI | Flask | Django |
|------|---------|-------|--------|
| 性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 异步支持 | ✅ 原生 | ❌ 需扩展 | ✅ 支持 |
| 类型提示 | ✅ Pydantic | ❌ 无 | ⭐⭐⭐ |
| 自动文档 | ✅ OpenAPI | ❌ 需扩展 | ✅ 支持 |
| 学习曲线 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| GraphQL | ✅ Strawberry | ✅ Ariadne | ✅ Graphene |
| **推荐指数** | **⭐⭐⭐⭐⭐** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    统一数据API网关架构                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │ API入口层    │    │ 认证授权层   │    │ 限流熔断层   │     │
│  │              │    │              │    │              │     │
│  │ • REST API   │    │ • JWT认证    │    │ • 限流控制   │     │
│  │ • GraphQL    │    │ • API Key    │    │ • 熔断降级   │     │
│  │ • WebSocket  │    │ • 权限控制   │    │ • 负载均衡   │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│         │                   │                    │              │
│         └───────────────────┴────────────────────┘              │
│                            │                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    缓存层                                │   │
│  │  • Redis缓存 (热点数据)                                  │   │
│  │  • 响应缓存 (查询结果)                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    数据源层                              │   │
│  │  • TimescaleDB (实时数据)                                │   │
│  │  • ClickHouse (历史数据)                                 │   │
│  │  • Redis (缓存数据)                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 核心功能实现

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
    description="统一数据API网关",
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
    """获取K线数据"""
    pass

@app.get("/api/v1/factors/{factor_id}")
@cache(expire=300)
async def get_factor_values(
    factor_id: str,
    symbols: List[str] = Query(...),
    date: str = Query(...)
):
    """获取因子值"""
    pass

@app.get("/api/v1/prices/realtime")
async def get_realtime_prices(
    symbols: List[str] = Query(...)
):
    """获取实时价格"""
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

### 3.3 认证授权

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

### 3.4 限流熔断

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

## 4. 部署配置

### 4.1 Docker部署

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

## 📋 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 首席架构师 |

---

**文档结束**
