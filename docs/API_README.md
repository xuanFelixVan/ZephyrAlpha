# ZephyrAlpha API文档

## 🚀 快速启动

### 方法1: 使用启动脚本（推荐）

```bash
python run_api.py
```

### 方法2: 使用uvicorn

```bash
uvicorn src.api.main:app --reload --port 8000
```

### 方法3: 直接运行

```bash
python -m src.api.main
```

## 📚 API文档访问

启动API服务后，可以通过以下地址访问文档：

| 文档类型 | 地址 | 说明 |
|---------|------|------|
| **Swagger UI** | http://localhost:8000/docs | 交互式API文档，可直接测试API |
| **ReDoc** | http://localhost:8000/redoc | 美观的API文档展示 |
| **OpenAPI JSON** | http://localhost:8000/openapi.json | OpenAPI 3.1规范文件 |

## 🎯 核心功能

### 1. 健康检查

```bash
# 系统健康检查
curl http://localhost:8000/health

# 就绪检查
curl http://localhost:8000/health/ready

# 存活检查
curl http://localhost:8000/health/live
```

### 2. 策略管理

```bash
# 获取策略列表
curl http://localhost:8000/api/strategies/

# 获取单个策略
curl http://localhost:8000/api/strategies/strategy_001

# 创建策略
curl -X POST http://localhost:8000/api/strategies/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "双均线策略",
    "description": "基于双均线的趋势跟踪策略",
    "strategy_type": "trend_following",
    "parameters": {
      "short_window": 20,
      "long_window": 60
    }
  }'

# 更新策略
curl -X PUT http://localhost:8000/api/strategies/strategy_001 \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "short_window": 15,
      "long_window": 50
    }
  }'

# 删除策略
curl -X DELETE http://localhost:8000/api/strategies/strategy_001
```

### 3. 回测系统

```bash
# 执行回测
curl -X POST http://localhost:8000/api/backtest/run \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": "strategy_001",
    "start_date": "2025-01-01T00:00:00",
    "end_date": "2025-12-31T00:00:00",
    "initial_capital": 1000000.0
  }'

# 获取回测结果
curl http://localhost:8000/api/backtest/results/backtest_20260405100000

# 获取交易记录
curl http://localhost:8000/api/backtest/results/backtest_20260405100000/trades

# 获取净值曲线
curl http://localhost:8000/api/backtest/results/backtest_20260405100000/equity
```

### 4. 监控系统

```bash
# 获取系统指标
curl http://localhost:8000/api/monitoring/system

# 获取交易指标
curl http://localhost:8000/api/monitoring/trading

# 获取风险指标
curl http://localhost:8000/api/monitoring/risk

# 获取预警列表
curl http://localhost:8000/api/monitoring/alerts

# 获取监控仪表板
curl http://localhost:8000/api/monitoring/dashboard
```

## 🔐 认证方式（待实现）

API支持两种认证方式：

### 1. JWT Token认证

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/strategies/
```

### 2. API Key认证

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
  http://localhost:8000/api/strategies/
```

## 📊 API响应格式

所有API响应采用统一的JSON格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": "2026-04-05T10:00:00Z"
}
```

## 🛠️ 开发指南

### 添加新的API路由

1. 在 `src/api/routes/` 创建新的路由文件
2. 在 `src/api/main.py` 中导入并注册路由

示例：

```python
# src/api/routes/custom.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/custom")
async def custom_endpoint():
    return {"message": "custom endpoint"}

# src/api/main.py
from src.api.routes import custom

app.include_router(custom.router, prefix="/api/custom", tags=["custom"])
```

### 使用Swagger UI测试API

1. 访问 http://localhost:8000/docs
2. 点击要测试的API端点
3. 点击 "Try it out"
4. 填写参数
5. 点击 "Execute" 执行请求

## 📝 注意事项

1. **生产环境**: 请配置HTTPS和认证
2. **性能优化**: 考虑使用Gunicorn + Uvicorn
3. **监控**: 集成Prometheus监控
4. **日志**: 配置日志收集和分析

## 🚀 部署建议

### 使用Gunicorn + Uvicorn

```bash
gunicorn src.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### 使用Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📖 更多信息

- FastAPI官方文档: https://fastapi.tiangolo.com/
- OpenAPI规范: https://spec.openapis.org/oas/v3.1.html
- Swagger UI: https://swagger.io/tools/swagger-ui/
