---
module_id: AUTH_SYSTEM_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
  - 蓝图设计、架构规划

---

﻿---
module_id: AUTH_SYSTEM_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 系统架构师
layer: Layer 8 (人机交互层)
module_name: 认证授权系统
standard_type: 专业量化机构系统蓝图
applicable_scope: ZephyrAlpha认证授权
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 蓝图设计
responsibility:
  - 认证授权系统，负责用户身份认证、登录管理和基础权限验证，不负责细粒度权限控制
## 一、模块概述

### 1.1 功能定位

认证授权系统负责用户身份认证和权限管理，保障系统安全。

### 1.2 核心功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 用户注册 | 邮箱注册 | P0 |
| 用户登录 | JWT认证 | P0 |
| 权限管理 | 角色权限控制 | P0 |
| 密码重置 | 邮箱验证重置 | P1 |
| 会话管理 | Token刷新 | P1 |

## 三、架构设计

### 3.1 系统架构

```
┌──────────────────────────────────────────────────────────────┐
│                    认证系统架构                                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    用户请求                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   认证中间件                           │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  1. 验证JWT Token                                │ │ │
│  │  │  2. 解析用户信息                                  │ │ │
│  │  │  3. 检查权限                                      │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│          ┌─────────────────┼─────────────────┐              │
│          ▼                 ▼                 ▼              │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐      │
│  │  登录注册   │   │  用户管理   │   │  权限控制   │      │
│  │  /auth/*    │   │  /users/*   │   │  /admin/*   │      │
│  └─────────────┘   └─────────────┘   └─────────────┘      │
│                            │                                 │
│                            ▼                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    SQLite数据库                        │ │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐        │ │
│  │  │  用户表    │ │  角色表    │ │  权限表    │        │ │
│  │  └────────────┘ └────────────┘ └────────────┘        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 认证流程

```
┌─────────────┐
│ 用户登录    │
│ 请求        │
└──────┬──────┘
       │ 1. 提交邮箱密码
       ▼
┌─────────────┐
│ 验证凭证    │
└──────┬──────┘
       │ 2. 验证成功
       ▼
┌─────────────┐
│ 生成JWT     │
│ Token       │
└──────┬──────┘
       │ 3. 返回Token
       ▼
┌─────────────┐
│ 客户端存储  │
│ Token       │
└──────┬──────┘
       │ 4. 后续请求携带Token
       ▼
┌─────────────┐
│ 验证Token   │
│ 访问资源    │
└─────────────┘
```

## 五、实施步骤

### 5.1 安装依赖

```bash
pip install fastapi-users[sqlalchemy] aiosqlite
```

### 5.2 数据库模型

```python
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

Base: DeclarativeMeta = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    role = Column(String, default="viewer")
```

### 5.3 认证配置

```python
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, CookieTransport, JWTStrategy

SECRET = "YOUR_SECRET_KEY"

cookie_transport = CookieTransport(cookie_max_age=14 * 24 * 3600)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
```

### 5.4 路由配置

```python
from fastapi import FastAPI, Depends
from fastapi_users import fastapi_users

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

@app.get("/protected-route")
def protected_route(user: User = Depends(current_active_user)):
    return f"Hello, {user.email}"
```

## 七、验收标准

### 7.1 功能验收

| 验收项 | 验收标准 | 测试方法 |
|--------|---------|---------|
| 用户注册 | 可注册新用户 | 注册测试 |
| 用户登录 | 可登录获取Token | 登录测试 |
| Token验证 | Token有效可访问 | 访问测试 |
| 权限控制 | 无权限拒绝访问 | 权限测试 |
| 密码重置 | 可重置密码 | 重置测试 |

### 7.2 安全验收

| 指标 | 目标值 | 说明 |
|------|-------|------|
| 密码加密 | bcrypt | 使用bcrypt加密 |
| Token有效期 | 1小时 | JWT有效期 |
| HTTPS | 必须 | 生产环境HTTPS |
| 密码强度 | 8位+ | 至少8位字符 |

**文档状态**: 🟢 活跃
**下次更新**: 2026-04-13
**维护周期**: 每周审查
**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active


