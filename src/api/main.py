"""
ZephyrAlpha量化交易系统 API主入口

提供完整的RESTful API接口，包括：
- Swagger UI交互式文档
- ReDoc美观文档
- OpenAPI 3.1规范

访问地址：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from datetime import datetime
from typing import Dict, Any

from src.api.routes import health, strategies, backtest, monitoring


def custom_openapi():
    """
    自定义OpenAPI规范
    
    添加：
    - 详细的API描述
    - 联系信息
    - 许可证信息
    - 服务器列表
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="ZephyrAlpha量化交易系统API",
        version="1.0.0",
        description="""
## 🎯 系统简介

ZephyrAlpha是一个专业级量化交易系统，提供完整的策略开发、回测、实盘交易功能。

## 📚 核心功能

### 1. 策略管理
- 策略创建、更新、删除
- 策略参数配置
- 策略性能评估

### 2. 回测系统
- 历史数据回测
- 多策略组合回测
- 绩效分析报告

### 3. 实时监控
- 交易信号监控
- 风险指标监控
- 系统状态监控

### 4. 数据服务
- 市场数据查询
- 因子数据查询
- 交易记录查询

## 🔐 认证方式

支持两种认证方式：
1. **JWT Token认证** - 用于Web应用
2. **API Key认证** - 用于程序化调用

## 📊 响应格式

所有API响应采用统一的JSON格式：
```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": "2026-04-05T10:00:00Z"
}
```

## 🚀 快速开始

1. 查看API文档: `/docs`
2. 获取API密钥: `/api/auth/api-key`
3. 调用API接口

## 📖 更多信息

- GitHub: https://github.com/your-org/zephyr-alpha
- 文档: https://docs.zephyr-alpha.com
- 社区: https://community.zephyr-alpha.com
        """,
        routes=app.routes,
        tags=[
            {
                "name": "health",
                "description": "系统健康检查",
            },
            {
                "name": "strategies",
                "description": "策略管理操作",
            },
            {
                "name": "backtest",
                "description": "回测相关操作",
            },
            {
                "name": "monitoring",
                "description": "监控相关操作",
            },
        ],
    )
    
    openapi_schema["info"]["contact"] = {
        "name": "ZephyrAlpha团队",
        "email": "support@zephyr-alpha.com",
        "url": "https://zephyr-alpha.com",
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
    
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "本地开发服务器",
        },
        {
            "url": "https://api.zephyr-alpha.com",
            "description": "生产环境服务器",
        },
    ]
    
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Token认证，格式: Bearer {token}",
        },
        "apiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API密钥认证，在请求头中添加 X-API-Key",
        },
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = FastAPI(
    title="ZephyrAlpha量化交易系统API",
    description="专业级量化交易系统RESTful API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {"name": "health", "description": "系统健康检查"},
        {"name": "strategies", "description": "策略管理"},
        {"name": "backtest", "description": "回测系统"},
        {"name": "monitoring", "description": "实时监控"},
    ],
)

app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(strategies.router, prefix="/api/strategies", tags=["strategies"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["backtest"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])


@app.get("/", response_model=Dict[str, Any])
async def root():
    """
    API根路径
    
    返回系统基本信息和可用端点
    """
    return {
        "name": "ZephyrAlpha量化交易系统API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "health": "/health",
            "strategies": "/api/strategies",
            "backtest": "/api/backtest",
            "monitoring": "/api/monitoring",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
