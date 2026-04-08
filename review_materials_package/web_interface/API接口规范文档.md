---
module_id: T.06.UI003
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席蓝图架构师
standard_type: 专业量化机构设计标准
applicable_scope: Web管理界面API接口规范
compliance_level: 初始设计
---

# API接口规范文档

> 清风量化交易系统 v5.2 - Web管理界面API接口规范
> **索引**: `DESIGN_005`
> **关联文档**: 
> - [Web管理界面架构设计](T.06.UI001.web_management_interface_architecture_design.md)
> - [前端组件结构图](前端组件结构图.md)
> - [系统API设计规范](../../docs/05_IMPLEMENTATION/02_DEVELOPMENT/API_DESIGN.md)

## 1. 概述

### 1.1 文档范围
本规范定义**Web管理界面**专用的API接口，包括：
- **RESTful API**: 前端与后端数据交互接口
- **WebSocket API**: 实时数据推送接口
- **认证授权API**: 用户认证和权限管理接口
- **文件上传/下载API**: 配置文件导入导出接口

### 1.2 设计原则
| 原则 | 说明 | 实现要求 |
|------|------|----------|
| **RESTful设计** | 遵循RESTful架构风格 | 资源导向、HTTP方法语义化 |
| **一致性** | 统一响应格式、错误处理 | 所有接口返回标准APIResponse格式 |
| **安全性** | 认证授权、数据加密 | JWT认证、HTTPS加密、输入验证 |
| **版本控制** | API版本管理 | URL路径版本控制 (v1, v2) |
| **文档化** | 接口文档自动生成 | OpenAPI/Swagger文档自动生成 |

### 1.3 版本信息
| 版本 | 发布时间 | 主要特性 | 兼容性 |
|------|----------|----------|--------|
| v1.0 | 2026-04-02 | 基础CRUD接口、实时推送 | 初始版本 |
| v1.1 | 计划 | 批量操作、高级查询 | 向下兼容v1.0 |
| v2.0 | 计划 | GraphQL支持、流式响应 | 不兼容v1.x |

## 2. 基础规范

### 2.1 统一响应格式

#### 2.1.1 成功响应
```json
{
  "code": 0,
  "message": "success",
  "data": {
    // 业务数据
  },
  "request_id": "req_abc123def456",
  "timestamp": "2026-04-02T12:00:00Z"
}
```

#### 2.1.2 错误响应
```json
{
  "code": 1001,
  "message": "数据不存在",
  "data": null,
  "request_id": "req_abc123def456",
  "timestamp": "2026-04-02T12:00:00Z",
  "details": {
    "field": "engine_id",
    "value": "engine_001",
    "suggestion": "请检查引擎ID是否正确"
  }
}
```

### 2.2 错误码定义

#### 2.2.1 通用错误码 (0-999)
| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
| 0 | 成功 | 200 |
| 1 | 参数错误 | 400 |
| 2 | 认证失败 | 401 |
| 3 | 权限不足 | 403 |
| 4 | 资源不存在 | 404 |
| 5 | 请求方法不允许 | 405 |
| 6 | 请求超时 | 408 |
| 7 | 系统内部错误 | 500 |
| 8 | 服务不可用 | 503 |

#### 2.2.2 Web界面专用错误码 (6000-6999)
| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
| 6001 | 仪表板数据获取失败 | 500 |
| 6002 | 交易数据查询失败 | 500 |
| 6003 | 性能数据计算失败 | 500 |
| 6004 | 配置保存失败 | 500 |
| 6005 | 配置验证失败 | 400 |
| 6006 | 系统健康检查失败 | 500 |
| 6007 | 日志查询失败 | 500 |
| 6008 | 文件上传失败 | 500 |
| 6009 | 文件下载失败 | 500 |
| 6010 | 实时推送连接失败 | 500 |

### 2.3 认证与授权

#### 2.3.1 JWT认证
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 2.3.2 权限角色
| 角色 | 权限说明 | API访问范围 |
|------|----------|-------------|
| **admin** | 管理员 | 所有API |
| **operator** | 操作员 | 读写交易数据、只读配置 |
| **viewer** | 观察员 | 只读所有数据 |
| **guest** | 访客 | 只读公开数据 |

### 2.4 请求限制
| 限制类型 | 限制值 | 说明 |
|----------|--------|------|
| **频率限制** | 100次/分钟 | 每个IP地址 |
| **并发连接** | 10个 | 每个用户 |
| **请求体大小** | 10MB | 文件上传除外 |
| **响应时间** | 30秒超时 | 长请求需使用异步 |

## 3. RESTful API 接口

### 3.1 认证授权接口

#### 3.1.1 用户登录
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

**响应**:
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "user_001",
      "username": "admin",
      "role": "admin",
      "permissions": ["*"]
    },
    "expires_in": 86400
  }
}
```

#### 3.1.2 用户登出
```http
POST /api/v1/auth/logout
Authorization: Bearer {token}
```

#### 3.1.3 获取当前用户信息
```http
GET /api/v1/auth/me
Authorization: Bearer {token}
```

### 3.2 仪表板接口

#### 3.2.1 获取仪表板概览数据
```http
GET /api/v1/dashboard/overview
Authorization: Bearer {token}
```

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "summary": {
      "total_engines": 5,
      "active_engines": 4,
      "total_trades_today": 128,
      "total_volume_today": 1250000.50,
      "system_health_score": 98.5
    },
    "engine_status": [
      {
        "engine_id": "engine_vnpy_001",
        "engine_type": "vn.py",
        "status": "running",
        "cpu_usage": 45.2,
        "memory_usage": 320.5,
        "trade_count_today": 56,
        "last_heartbeat": "2026-04-02T11:59:30Z"
      },
      // 其他引擎状态
    ],
    "recent_alerts": [
      {
        "id": "alert_001",
        "level": "warning",
        "message": "引擎 vn.py 内存使用率超过80%",
        "timestamp": "2026-04-02T11:45:00Z",
        "acknowledged": false
      }
    ]
  }
}
```

#### 3.2.2 获取引擎详细状态
```http
GET /api/v1/dashboard/engines/{engine_id}/status
Authorization: Bearer {token}
```

#### 3.2.3 启动/停止引擎
```http
POST /api/v1/dashboard/engines/{engine_id}/start
POST /api/v1/dashboard/engines/{engine_id}/stop
Authorization: Bearer {token}
```

### 3.3 交易监控接口

#### 3.3.1 查询交易记录
```http
GET /api/v1/trades
Authorization: Bearer {token}
Query Parameters:
  - start_date: string (YYYY-MM-DD)   # 开始日期
  - end_date: string (YYYY-MM-DD)     # 结束日期
  - symbol: string                    # 股票代码
  - engine_id: string                 # 引擎ID
  - side: string (buy/sell)           # 买卖方向
  - page: integer = 1                 # 页码
  - page_size: integer = 50           # 每页数量
  - sort_by: string = "timestamp"     # 排序字段
  - sort_order: string = "desc"       # 排序方向
```

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "trades": [
      {
        "trade_id": "trade_20240402_001",
        "timestamp": "2026-04-02T09:30:15Z",
        "symbol": "000001.SZ",
        "side": "buy",
        "price": 10.50,
        "quantity": 1000,
        "volume": 10500.00,
        "commission": 5.25,
        "net_amount": 10505.25,
        "engine_id": "engine_vnpy_001",
        "strategy_id": "strategy_macd_001"
      }
    ],
    "pagination": {
      "current_page": 1,
      "page_size": 50,
      "total_count": 128,
      "total_pages": 3
    },
    "summary": {
      "total_trades": 128,
      "total_volume": 1250000.50,
      "buy_count": 65,
      "sell_count": 63,
      "avg_price": 12.45
    }
  }
}
```

#### 3.3.2 获取单笔交易详情
```http
GET /api/v1/trades/{trade_id}
Authorization: Bearer {token}
```

#### 3.3.3 导出交易数据
```http
GET /api/v1/trades/export
Authorization: Bearer {token}
Query Parameters: (同查询接口)
Accept: text/csv, application/json
```

### 3.4 性能分析接口

#### 3.4.1 获取性能指标
```http
GET /api/v1/performance/metrics
Authorization: Bearer {token}
Query Parameters:
  - time_range: string (1d, 7d, 30d, 90d, 1y)  # 时间范围
  - engine_id: string                          # 引擎ID，可选
  - strategy_id: string                        # 策略ID，可选
  - metrics: string[]                          # 指标列表，可选
```

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "time_range": {
      "start": "2026-03-01T00:00:00Z",
      "end": "2026-04-02T23:59:59Z"
    },
    "metrics": {
      "sharpe_ratio": 1.85,
      "max_drawdown": -0.125,
      "win_rate": 0.58,
      "profit_factor": 1.92,
      "avg_return": 0.0015,
      "volatility": 0.025,
      "sortino_ratio": 2.31,
      "calmar_ratio": 0.48
    },
    "equity_curve": [
      {"date": "2026-03-01", "value": 1000000},
      {"date": "2026-03-02", "value": 1001250},
      // 更多数据点
    ],
    "drawdown_curve": [
      {"date": "2026-03-01", "value": 0},
      {"date": "2026-03-02", "value": -0.012},
      // 更多数据点
    ]
  }
}
```

#### 3.4.2 获取交易分布
```http
GET /api/v1/performance/trade-distribution
Authorization: Bearer {token}
Query Parameters:
  - time_range: string (1d, 7d, 30d, 90d, 1y)
  - group_by: string (symbol, engine, strategy, hour_of_day)
```

#### 3.4.3 获取绩效报告
```http
GET /api/v1/performance/report
Authorization: Bearer {token}
Query Parameters:
  - format: string (html, pdf, json) = "json"
  - include_charts: boolean = true
```

### 3.5 配置管理接口

#### 3.5.1 获取引擎配置
```http
GET /api/v1/config/engines
Authorization: Bearer {token}
```

#### 3.5.2 获取单个引擎配置
```http
GET /api/v1/config/engines/{engine_id}
Authorization: Bearer {token}
```

#### 3.5.3 更新引擎配置
```http
PUT /api/v1/config/engines/{engine_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "config": {
    "broker": "simulator",
    "account_id": "sim_account_001",
    "commission_rate": 0.0003,
    "min_commission": 5.0,
    "slippage": 0.001,
    "trade_time": "09:30-15:00",
    "auto_start": true
  }
}
```

#### 3.5.4 获取策略配置
```http
GET /api/v1/config/strategies
Authorization: Bearer {token}
```

#### 3.5.5 更新策略配置
```http
PUT /api/v1/config/strategies/{strategy_id}
Authorization: Bearer {token}
```

#### 3.5.6 获取风险限额配置
```http
GET /api/v1/config/risk-limits
Authorization: Bearer {token}
```

#### 3.5.7 更新风险限额配置
```http
PUT /api/v1/config/risk-limits/{limit_id}
Authorization: Bearer {token}
```

### 3.6 系统健康接口

#### 3.6.1 获取系统健康状态
```http
GET /api/v1/system/health
Authorization: Bearer {token}
```

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "overall_status": "healthy",
    "components": [
      {
        "name": "数据库",
        "status": "healthy",
        "response_time": 45,
        "last_check": "2026-04-02T12:00:00Z"
      },
      {
        "name": "Redis缓存",
        "status": "healthy",
        "response_time": 12,
        "last_check": "2026-04-02T12:00:00Z"
      },
      {
        "name": "vn.py引擎",
        "status": "degraded",
        "response_time": 350,
        "last_check": "2026-04-02T12:00:00Z",
        "details": "内存使用率85%"
      }
    ],
    "metrics": {
      "cpu_usage": 65.2,
      "memory_usage": 4.2,
      "disk_usage": 45.8,
      "network_io": 125.5,
      "api_request_rate": 12.5
    }
  }
}
```

#### 3.6.2 查询系统日志
```http
GET /api/v1/system/logs
Authorization: Bearer {token}
Query Parameters:
  - level: string (info, warning, error, debug)
  - component: string
  - start_time: string (ISO 8601)
  - end_time: string (ISO 8601)
  - keyword: string
  - page: integer = 1
  - page_size: integer = 100
```

#### 3.6.3 获取告警历史
```http
GET /api/v1/system/alerts
Authorization: Bearer {token}
Query Parameters:
  - level: string (info, warning, error, critical)
  - acknowledged: boolean
  - start_time: string
  - end_time: string
```

#### 3.6.4 确认告警
```http
POST /api/v1/system/alerts/{alert_id}/acknowledge
Authorization: Bearer {token}
```

### 3.7 文件操作接口

#### 3.7.1 上传配置文件
```http
POST /api/v1/files/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

Form Data:
  - file: File (配置文件)
  - file_type: string (engine_config, strategy_config, risk_config)
  - engine_id: string (可选)
  - strategy_id: string (可选)
```

#### 3.7.2 下载配置文件
```http
GET /api/v1/files/download/{file_id}
Authorization: Bearer {token}
```

#### 3.7.3 获取文件列表
```http
GET /api/v1/files
Authorization: Bearer {token}
Query Parameters:
  - file_type: string
  - engine_id: string
  - start_time: string
  - end_time: string
```

## 4. WebSocket API 接口

### 4.1 连接建立

#### 4.1.1 连接URL
```
ws://localhost:8000/api/v1/ws?token={jwt_token}
```

#### 4.1.2 连接协议
```json
// 客户端发送连接请求
{
  "type": "connect",
  "client_id": "web_ui_001",
  "subscriptions": ["trades", "engine_status", "alerts"]
}

// 服务端响应
{
  "type": "connected",
  "server_time": "2026-04-02T12:00:00Z",
  "client_id": "web_ui_001",
  "message": "连接成功"
}
```

### 4.2 实时事件推送

#### 4.2.1 交易执行事件
```json
{
  "type": "trade_executed",
  "data": {
    "trade_id": "trade_20240402_001",
    "timestamp": "2026-04-02T09:30:15Z",
    "symbol": "000001.SZ",
    "side": "buy",
    "price": 10.50,
    "quantity": 1000,
    "volume": 10500.00,
    "engine_id": "engine_vnpy_001",
    "strategy_id": "strategy_macd_001"
  },
  "event_id": "event_001",
  "timestamp": "2026-04-02T09:30:15Z"
}
```

#### 4.2.2 引擎状态更新事件
```json
{
  "type": "engine_status_updated",
  "data": {
    "engine_id": "engine_vnpy_001",
    "status": "running",
    "cpu_usage": 45.2,
    "memory_usage": 320.5,
    "trade_count_today": 57,
    "last_heartbeat": "2026-04-02T12:00:30Z"
  },
  "event_id": "event_002",
  "timestamp": "2026-04-02T12:00:30Z"
}
```

#### 4.2.3 告警事件
```json
{
  "type": "alert_triggered",
  "data": {
    "alert_id": "alert_002",
    "level": "warning",
    "message": "引擎 vn.py CPU使用率超过80%",
    "component": "engine_vnpy_001",
    "timestamp": "2026-04-02T12:01:00Z",
    "details": {
      "metric": "cpu_usage",
      "value": 82.5,
      "threshold": 80.0
    }
  },
  "event_id": "event_003",
  "timestamp": "2026-04-02T12:01:00Z"
}
```

#### 4.2.4 性能指标更新事件
```json
{
  "type": "performance_updated",
  "data": {
    "timestamp": "2026-04-02T12:00:00Z",
    "metrics": {
      "sharpe_ratio": 1.86,
      "max_drawdown": -0.124,
      "win_rate": 0.581
    }
  },
  "event_id": "event_004",
  "timestamp": "2026-04-02T12:00:00Z"
}
```

### 4.3 客户端订阅管理

#### 4.3.1 订阅事件
```json
// 客户端发送订阅请求
{
  "type": "subscribe",
  "subscriptions": ["trades", "engine_status", "alerts"]
}

// 服务端响应
{
  "type": "subscription_updated",
  "data": {
    "current_subscriptions": ["trades", "engine_status", "alerts"],
    "message": "订阅成功"
  }
}
```

#### 4.3.2 取消订阅
```json
// 客户端发送取消订阅请求
{
  "type": "unsubscribe",
  "subscriptions": ["alerts"]
}
```

### 4.4 心跳与连接保持

#### 4.4.1 客户端心跳
```json
// 客户端定期发送心跳
{
  "type": "ping",
  "client_id": "web_ui_001",
  "timestamp": "2026-04-02T12:00:00Z"
}

// 服务端响应
{
  "type": "pong",
  "server_time": "2026-04-02T12:00:00Z",
  "latency": 15
}
```

#### 4.4.2 连接超时
- 心跳间隔: 30秒
- 连接超时: 90秒
- 自动重连: 支持，最大重试次数5次

## 5. 数据模型定义

### 5.1 通用数据模型

#### 5.1.1 分页响应模型
```python
from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
```

#### 5.1.2 时间范围模型
```python
class TimeRange(BaseModel):
    """时间范围模型"""
    start: str  # ISO 8601格式
    end: str    # ISO 8601格式
    timezone: str = "UTC"
```

### 5.2 业务数据模型

#### 5.2.1 引擎状态模型
```python
class EngineStatus(BaseModel):
    """引擎状态模型"""
    engine_id: str
    engine_type: str
    status: str  # running, stopped, error, starting, stopping
    cpu_usage: float  # 百分比
    memory_usage: float  # MB
    trade_count_today: int
    error_count: int
    last_heartbeat: str  # ISO 8601格式
    start_time: Optional[str] = None
    uptime_seconds: Optional[int] = None
```

#### 5.2.2 交易数据模型
```python
class Trade(BaseModel):
    """交易数据模型"""
    trade_id: str
    timestamp: str  # ISO 8601格式
    symbol: str
    side: str  # buy, sell
    price: float
    quantity: int
    volume: float
    commission: float
    net_amount: float
    engine_id: str
    strategy_id: Optional[str] = None
    account_id: Optional[str] = None
    order_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "trade_id": "trade_20240402_001",
                "timestamp": "2026-04-02T09:30:15Z",
                "symbol": "000001.SZ",
                "side": "buy",
                "price": 10.50,
                "quantity": 1000,
                "volume": 10500.00,
                "commission": 5.25,
                "net_amount": 10505.25,
                "engine_id": "engine_vnpy_001",
                "strategy_id": "strategy_macd_001"
            }
        }
```

#### 5.2.3 性能指标模型
```python
class PerformanceMetrics(BaseModel):
    """性能指标模型"""
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    avg_return: float
    volatility: float
    sortino_ratio: float
    calmar_ratio: float
    total_return: float
    annual_return: float
    benchmark_return: Optional[float] = None
    alpha: Optional[float] = None
    beta: Optional[float] = None
```

### 5.3 配置数据模型

#### 5.3.1 引擎配置模型
```python
class EngineConfig(BaseModel):
    """引擎配置模型"""
    engine_id: str
    engine_type: str
    broker: str
    account_id: str
    commission_rate: float = 0.0003
    min_commission: float = 5.0
    slippage: float = 0.001
    trade_time: str = "09:30-15:00"
    auto_start: bool = False
    max_position: Optional[float] = None
    max_order_size: Optional[float] = None
    risk_limits: Dict[str, Any] = {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "engine_id": "engine_vnpy_001",
                "engine_type": "vn.py",
                "broker": "simulator",
                "account_id": "sim_account_001",
                "commission_rate": 0.0003,
                "min_commission": 5.0,
                "slippage": 0.001,
                "trade_time": "09:30-15:00",
                "auto_start": True
            }
        }
```

## 6. API测试规范

### 6.1 测试环境
| 环境 | 地址 | 用途 |
|------|------|------|
| **开发环境** | http://localhost:8000 | 开发测试 |
| **测试环境** | http://test.api.qingfeng.com | 集成测试 |
| **预生产环境** | http://staging.api.qingfeng.com | 预发布测试 |
| **生产环境** | https://api.qingfeng.com | 生产环境 |

### 6.2 测试工具
| 工具 | 用途 | 配置 |
|------|------|------|
| **pytest** | 单元测试和集成测试 | `tests/api/` |
| **Postman** | API测试和文档 | Postman Collection |
| **Swagger UI** | 交互式API文档 | http://localhost:8000/docs |
| **Locust** | 性能测试 | `locustfile.py` |

### 6.3 测试用例示例

#### 6.3.1 认证测试
```python
import pytest
from fastapi.testclient import TestClient

def test_login_success(client: TestClient):
    """测试登录成功"""
    response = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "token" in data["data"]
    assert data["data"]["user"]["username"] == "admin"

def test_login_failure(client: TestClient):
    """测试登录失败"""
    response = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "wrong_password"
    })
    
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == 2
```

#### 6.3.2 交易查询测试
```python
def test_get_trades_with_filters(client: TestClient, auth_headers: dict):
    """测试带过滤条件的交易查询"""
    response = client.get("/api/v1/trades", params={
        "start_date": "2026-04-01",
        "end_date": "2026-04-02",
        "symbol": "000001.SZ",
        "page": 1,
        "page_size": 10
    }, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "trades" in data["data"]
    assert "pagination" in data["data"]
    assert len(data["data"]["trades"]) <= 10
```

### 6.4 性能测试标准
| 指标 | 目标值 | 测试方法 |
|------|--------|----------|
| **API响应时间** | P95 < 200ms | 负载测试 |
| **并发处理能力** | ≥1000 QPS | 压力测试 |
| **WebSocket连接数** | ≥500 并发连接 | 连接测试 |
| **内存使用** | < 1GB | 内存分析 |
| **错误率** | < 0.1% | 稳定性测试 |

## 7. 部署与运维

### 7.1 部署配置

#### 7.1.1 Docker部署
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "web_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 7.1.2 环境变量配置
```bash
# .env 文件
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=postgresql://user:password@db:5432/qingfeng
REDIS_URL=redis://redis:6379/0
JWT_SECRET_KEY=your-secret-key
CORS_ORIGINS=["http://localhost:3000"]
```

### 7.2 监控与告警

#### 7.2.1 监控指标
| 指标 | 采集方式 | 告警阈值 |
|------|----------|----------|
| **API请求率** | Prometheus | < 10 QPS 或 > 1000 QPS |
| **API错误率** | Prometheus | > 1% |
| **API响应时间** | Prometheus | P95 > 500ms |
| **WebSocket连接数** | Prometheus | > 1000 |
| **内存使用率** | cAdvisor | > 80% |
| **CPU使用率** | cAdvisor | > 70% |

#### 7.2.2 日志配置
```python
# 日志配置
import logging
from loguru import logger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# 结构化日志
logger.add("logs/api.log", 
           rotation="100 MB", 
           retention="30 days",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
           serialize=True)  # 输出JSON格式
```

### 7.3 安全配置

#### 7.3.1 CORS配置
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://qingfeng.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)
```

#### 7.3.2 速率限制
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """速率限制中间件"""
    # 不同接口不同限制
    if request.url.path.startswith("/api/v1/auth"):
        await limiter.check(request, "10/minute")
    elif request.url.path.startswith("/api/v1/trades"):
        await limiter.check(request, "100/minute")
    else:
        await limiter.check(request, "1000/minute")
    
    response = await call_next(request)
    return response
```

## 8. 版本升级与兼容性

### 8.1 版本升级策略
| 升级类型 | 描述 | 兼容性要求 |
|----------|------|------------|
| **补丁版本** (x.y.z → x.y.z+1) | Bug修复、安全更新 | 完全兼容 |
| **次要版本** (x.y.z → x.y+1.0) | 新增功能、API扩展 | 向前兼容 |
| **主要版本** (x.y.z → x+1.0.0) | 重大变更、API不兼容 | 需要迁移 |

### 8.2 API废弃策略
1. **预告期**: 在文档中标记为"已废弃"，持续3个月
2. **警告期**: 返回警告头`X-API-Deprecated: true`，持续3个月
3. **移除期**: 完全移除废弃API，返回410状态码

### 8.3 客户端兼容性要求
| 客户端类型 | 最低API版本 | 升级要求 |
|------------|-------------|----------|
| **Web界面** | v1.0 | 自动检测API版本，支持降级 |
| **移动端App** | v1.0 | 应用商店强制更新 |
| **第三方集成** | v1.0 | 文档通知，提供迁移指南 |

---

**文档版本**: 1.0.0  
**最后更新**: 2026-04-02  
**维护者**: 首席蓝图架构师  
**索引**: `DESIGN_005`  
**状态**: ✅ 设计完成，待评审