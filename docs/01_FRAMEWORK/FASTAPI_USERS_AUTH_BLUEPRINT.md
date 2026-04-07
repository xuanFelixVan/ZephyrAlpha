---
module_id: FASTAPI_USERS_AUTH_BLUEPRINT
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: FASTAPI_USERS_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席架构师
responsibility:
  - 系统架构蓝图设计与实施指导与实施方案
layer: Layer 8 (人机交互层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
---
---
---


﻿---
module_id: FASTAPI_USERS_AUTH_001
version: 1.0.0
status: Active
created_date: 2026-04-05
last_updated: 2026-04-05
owner: 系统架构师
standard_type: 专业量化机构蓝图
applicable_scope: Layer 8 - FastAPI-Users认证权限系统
compliance_level: 顶级专业标准
reference_models: ["Bridgewater Access Control", "Two Sigma Authentication", "Citadel Permission Management"]
related_documents:
  - HUMAN_AI_INTERACTION_BLUEPRINT.md
  - GRAFANA_MONITORING_BLUEPRINT.md
parent_document: ./HUMAN_AI_INTERACTION_BLUEPRINT.md
implementation_status: 蓝图设计完成
layer: Layer 8 (人机交互层)
responsibility_boundary: |
  本文档负责FastAPI-Users认证权限系统设计，包括：
  - 用户认证管理
  - 权限控制管理
  - 角色管理
  
  人机交互层战略规划请参考：HUMAN_AI_INTERACTION_BLUEPRINT.md
---

# FastAPI-Users认证权限系统蓝图
> **核心职责**: Fastapi Users Auth蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：Fastapi Users Auth蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容


> **版本**: v1.0  
> **创建日期**: 2026-04-05  
> **实施周期**: 3天  
> **目标**: 构建专业级认证权限系统，使用FastAPI-Users替代自研认证

---

## 📋 执行摘要

### 核心定位

FastAPI-Users认证权限系统是Layer 8人机交互层的**安全网关**，负责：
- 用户身份认证
- 权限访问控制
- API密钥管理
- 会话安全管理

### 开源优先策略

**核心原则**: 使用成熟开源认证框架，不自研认证系统

| 组件 | 开源项目 | 成熟度 | 适用场景 |
|------|---------|--------|---------|
| **个人使用** | FastAPI-Users | ⭐⭐⭐⭐⭐ | 单用户/小团队 |
| **团队使用** | Keycloak | ⭐⭐⭐⭐⭐ | 多用户/企业级 |
| **轻量方案** | FastAPI-Security | ⭐⭐⭐⭐ | API密钥认证 |

---

## 一、系统架构设计

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│              FastAPI-Users认证权限系统架构                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │          认证层 (Authentication)                           │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │ │
│  │  │JWT Token │  │ API Key  │  │ Session  │               │ │
│  │  │  认证    │  │   认证   │  │  认证    │               │ │
│  │  └──────────┘  └──────────┘  └──────────┘               │ │
│  └───────────────────────────────────────────────────────────┘ │
│                           ↓                                     │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │          授权层 (Authorization)                            │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ 角色权限管理 (Role-Based Access Control)            │ │ │
│  │  │ ├── 管理员 (Admin) - 全部权限                       │ │ │
│  │  │ ├── 交易员 (Trader) - 交易权限                      │ │ │
│  │  │ ├── 风险管理员 (Risk Manager) - 风险权限            │ │ │
│  │  │ └── 观察者 (Viewer) - 只读权限                      │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                           ↓                                     │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │          数据层 (Data Layer)                               │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │ │
│  │  │用户数据库│  │权限数据库│  │会话存储  │               │ │
│  │  │(SQLite)  │  │(SQLite)  │  │(Redis)   │               │ │
│  │  └──────────┘  └──────────┘  └──────────┘               │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、核心组件实现

### 2.1 FastAPI-Users配置

```python
from fastapi import FastAPI, Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from models import User, Base
from schemas import UserCreate, UserRead, UserUpdate


DATABASE_URL = "sqlite+aiosqlite:///./users.db"

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret="SECRET_KEY", lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsersUser, int

app = FastAPI()

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

current_active_user = fastapi_users.current_user(active=True)
```

### 2.2 用户模型与角色

```python
from sqlalchemy import Boolean, Integer, String, Column
from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy.orm import relationship


class Role:
    ADMIN = "admin"
    TRADER = "trader"
    RISK_MANAGER = "risk_manager"
    VIEWER = "viewer"


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    role = Column(String, default=Role.VIEWER, nullable=False)
    
    permissions = relationship("Permission", back_populates="user")


class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    resource = Column(String, nullable=False)
    action = Column(String, nullable=False)
    
    user = relationship("User", back_populates="permissions")
```

### 2.3 权限装饰器

```python
from functools import wraps
from fastapi import HTTPException, status


def require_role(required_role: str):
    """角色权限装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user=Depends(current_active_user), **kwargs):
            if user.role != required_role and user.role != Role.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator


def require_permission(resource: str, action: str):
    """细粒度权限装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user=Depends(current_active_user), **kwargs):
            if user.role == Role.ADMIN:
                return await func(*args, user=user, **kwargs)
            
            has_permission = any(
                p.resource == resource and p.action == action
                for p in user.permissions
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {resource}:{action}"
                )
            
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator
```

### 2.4 API密钥认证

```python
from fastapi.security import APIKeyHeader
from fastapi import Security

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key_user(api_key: str = Security(api_key_header)):
    """API密钥认证"""
    if not api_key:
        return None
    
    user = await get_user_by_api_key(api_key)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return user


async def get_current_user(
    user=Depends(current_active_user),
    api_key_user=Depends(get_api_key_user)
):
    """支持JWT和API密钥双重认证"""
    return user or api_key_user
```

---

## 三、权限矩阵设计

### 3.1 角色权限矩阵

| 资源 | Admin | Trader | Risk Manager | Viewer |
|------|-------|--------|--------------|--------|
| **交易执行** | ✅ | ✅ | ❌ | ❌ |
| **策略管理** | ✅ | ✅ | ❌ | 👁️ |
| **风险监控** | ✅ | 👁️ | ✅ | 👁️ |
| **绩效报告** | ✅ | ✅ | ✅ | 👁️ |
| **系统配置** | ✅ | ❌ | ❌ | ❌ |
| **用户管理** | ✅ | ❌ | ❌ | ❌ |

### 3.2 API端点权限

```python
from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/trade/execute")
@require_role(Role.TRADER)
async def execute_trade(
    trade_request: TradeRequest,
    user=Depends(current_active_user)
):
    """执行交易 - 需要Trader角色"""
    pass


@router.get("/risk/report")
@require_permission("risk", "read")
async def get_risk_report(user=Depends(current_active_user)):
    """查看风险报告 - 需要risk:read权限"""
    pass


@router.put("/system/config")
@require_role(Role.ADMIN)
async def update_system_config(
    config: SystemConfig,
    user=Depends(current_active_user)
):
    """更新系统配置 - 需要Admin角色"""
    pass
```

---

## 四、实施计划

### 4.1 实施阶段

| 阶段 | 时间 | 目标 | 交付物 |
|------|------|------|--------|
| **阶段1** | 第1天 | FastAPI-Users集成 | 基础认证系统 |
| **阶段2** | 第2天 | 权限系统实现 | 角色权限控制 |
| **阶段3** | 第3天 | API密钥管理 | API认证支持 |

### 4.2 配置示例

```yaml
auth:
  jwt:
    secret_key: "your-secret-key-here"
    algorithm: "HS256"
    expire_minutes: 60
  
  api_key:
    header_name: "X-API-Key"
    expire_days: 365
  
  roles:
    admin:
      permissions: ["*"]
    trader:
      permissions:
        - "trade:*"
        - "strategy:read"
        - "strategy:write"
        - "report:read"
    risk_manager:
      permissions:
        - "risk:*"
        - "report:read"
    viewer:
      permissions:
        - "*:read"
```

---

## 五、最佳实践

### 5.1 安全建议

| 实践 | 说明 | 重要性 |
|------|------|--------|
| **密钥管理** | 使用环境变量存储密钥 | ⭐⭐⭐⭐⭐ |
| **HTTPS** | 生产环境必须使用HTTPS | ⭐⭐⭐⭐⭐ |
| **密码哈希** | 使用bcrypt哈希密码 | ⭐⭐⭐⭐⭐ |
| **会话过期** | 设置合理的会话过期时间 | ⭐⭐⭐⭐ |

---

## 六、总结

FastAPI-Users认证权限系统通过**开源优先策略**，实现了：

1. **多种认证方式** - JWT + API Key
2. **灵活权限控制** - RBAC + 细粒度权限
3. **安全可靠** - 行业标准安全实践
4. **易于集成** - FastAPI原生支持

**核心优势**:
- ✅ 使用成熟开源框架
- ✅ 实施周期短（3天）
- ✅ 安全性高
- ✅ 可扩展性强

**下一步**:
1. 集成FastAPI-Users（第1天）
2. 实现权限系统（第2天）
3. 添加API密钥支持（第3天）
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 8: 人机交互层
##### 0.001. Fastapi Users Auth Blueprint
- **模块ID**: FASTAPI_USERS_AUTH_BLUEPRINT_001
- **蓝图文档**: [FASTAPI_USERS_AUTH_BLUEPRINT.md](01_FRAMEWORK\FASTAPI_USERS_AUTH_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: Layer 8 - FastAPI-Users认证权限系统
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Fastapi Users Auth Blueprint** | Layer 8 - FastAPI-Users认证权限系统 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-05 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-05 | **状态**: Active
