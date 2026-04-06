---
module_id: AUTHSYSTEMBLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理员
responsibility:
  - 因子计算
  - 交易执行
  - 回测系统
layer: Layer 2 (Alpha因子层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准---


﻿---
module_id: AUTH_SYSTEM_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 系统架构师
layer: Layer 8 (人机交互层)
module_id: 8.3
module_name: 认证授权系统
standard_type: 专业量化机构系统蓝图
applicable_scope: ZephyrAlpha认证授权
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 蓝图设计
---

# 认证授权系统模块蓝图

> **版本**: v1.0
> **创建日期**: 2026-04-06
> **技术方案**: FastAPI-Users + JWT
> **优先级**: P0（核心模块）

---

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

---

## 二、技术选型

### 2.1 核心技术栈

```
┌─────────────────────────────────────────────────────────┐
│                  认证系统技术栈                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐      ┌─────────────┐                 │
│  │ FastAPI-Users│◄────│   SQLite    │                 │
│  │ (认证框架)  │      │  (数据库)   │                 │
│  └──────┬──────┘      └─────────────┘                 │
│         │                                               │
│         │                                               │
│         ▼                                               │
│  ┌─────────────┐                                       │
│  │    JWT      │                                       │
│  │  (令牌)     │                                       │
│  └─────────────┘                                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 技术选型理由

| 技术 | 选型理由 |
|------|---------|
| **FastAPI-Users** | FastAPI官方推荐，功能完整 |
| **SQLite** | 轻量级，无需额外服务 |
| **JWT** | 无状态认证，易于扩展 |

---

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

---

## 四、用户角色设计

### 4.1 角色定义

| 角色 | 权限 | 说明 |
|------|------|------|
| **admin** | 全部权限 | 系统管理员 |
| **trader** | 交易权限 | 交易员 |
| **researcher** | 研究权限 | 研究员 |
| **viewer** | 只读权限 | 观察者 |

### 4.2 权限矩阵

| 功能 | admin | trader | researcher | viewer |
|------|-------|--------|-----------|--------|
| 查看监控 | ✅ | ✅ | ✅ | ✅ |
| 执行交易 | ✅ | ✅ | ❌ | ❌ |
| 运行回测 | ✅ | ✅ | ✅ | ❌ |
| 修改配置 | ✅ | ❌ | ❌ | ❌ |
| 用户管理 | ✅ | ❌ | ❌ | ❌ |

---

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

---

## 六、API接口设计

### 6.1 认证接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/auth/jwt/login` | POST | 用户登录 |
| `/auth/jwt/logout` | POST | 用户登出 |
| `/auth/register` | POST | 用户注册 |
| `/auth/forgot-password` | POST | 忘记密码 |
| `/auth/reset-password` | POST | 重置密码 |

### 6.2 用户接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/users/me` | GET | 获取当前用户 |
| `/users/me` | PATCH | 更新用户信息 |
| `/users/{id}` | GET | 获取用户信息 |
| `/users/{id}` | DELETE | 删除用户 |

---

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

---

## 八、参考资料

| 资源 | 链接 |
|------|------|
| FastAPI-Users官方文档 | https://fastapi-users.github.io/fastapi-users/ |
| JWT介绍 | https://jwt.io/ |
| FastAPI安全 | https://fastapi.tiangolo.com/tutorial/security/ |

---

**文档状态**: 🟢 活跃
**下次更新**: 2026-04-13
**维护周期**: 每周审查
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 8: 人机交互层
##### 0.1. 未知模块
- **模块ID**: 8.3
- **蓝图文档**: [AUTH_SYSTEM_BLUEPRINT.md](./08_HUMAN_AI_INTERFACE\03_AUTH\AUTH_SYSTEM_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: ZephyrAlpha认证授权
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **未知模块** | ZephyrAlpha认证授权 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active
