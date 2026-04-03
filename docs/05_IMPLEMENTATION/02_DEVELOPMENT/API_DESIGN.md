---
module_id: IMPL_API_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部署
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行中
---


# API设计规范

> 清风量化系统 v5.0 - API设计蓝图
> **索引**: `DEV.API.001`
> **开发时间**: 5h
> **核心定位**: 统一模块间通信接口，确保系统各层模块能有效交互


## 1. API设计原则

### 1.1 核心原则

| 原则 | 说明 | 优先级 |
|------|------|--------|
| **一致性** | 统一响应格式、错误码、命名 | 必须 |
| **简洁性** | 接口职责单一，不过度封装 | 必须 |
| **可测试** | 接口可独立于业务逻辑测试 | 必须 |
| **版本化** | API版本控制，支持平滑升级 | 应该 |
| **文档化** | 自动生成OpenAPI/Swagger文档 | 应该 |

### 1.2 接口分层

```
┌─────────────────────────────────────────────┐
│           External API (外部接口)            │
│    FastAPI Routes → 人/外部系统调用           │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│           Internal API (内部接口)             │
│    Module Methods → 模块间调用                 │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│           Data Interface (数据接口)           │
│    Repository Pattern → 数据访问              │
└─────────────────────────────────────────────┘
```


## 2. 统一响应格式

### 2.1 响应结构

```python
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """统一API响应格式"""

    code: int = 0                    # 状态码: 0=成功, >0=错误
    message: str = "success"          # 消息描述
    data: Optional[T] = None         # 响应数据
    request_id: Optional[str] = None # 请求追踪ID

    class Config:
        json_schema_extra = {
            "example": {
                "code": 0,
                "message": "success",
                "data": {"stock_code": "000001", "close": 10.5},
                "request_id": "req_abc123"
            }
        }
```

### 2.2 错误码定义

| 错误码 | 范围 | 说明 |
|--------|------|------|
| 0 | 0xx | 成功 |
| 1000-1999 | 1xxx | 数据相关错误 |
| 2000-2999 | 2xxx | 策略相关错误 |
| 3000-3999 | 3xxx | 风控相关错误 |
| 4000-4999 | 4xxx | 执行相关错误 |
| 5000-5999 | 5xxx | 系统相关错误 |

```python
class ErrorCode:
    # 数据错误 (1000-1999)
    DATA_NOT_FOUND = 1001
    DATA_INVALID = 1002
    DATA_TIMEOUT = 1003
    DATA_SOURCE_UNAVAILABLE = 1004

    # 策略错误 (2000-2999)
    STRATEGY_NOT_FOUND = 2001
    STRATEGY_INVALID = 2002
    STRATEGY_ALREADY_RUNNING = 2003

    # 风控错误 (3000-3999)
    RISK_LIMIT_EXCEEDED = 3001
    RISK_POSITION_LIMIT = 3002
    RISK_DRAWDOWN_LIMIT = 3003

    # 执行错误 (4000-4999)
    ORDER_REJECTED = 4001
    ORDER_TIMEOUT = 4002
    INSUFFICIENT_CAPITAL = 4003

    # 系统错误 (5000-5999)
    SYSTEM_ERROR = 5001
    CONFIG_ERROR = 5002
    AUTH_ERROR = 5003
```


## 3. 模块接口定义

### 3.1 DataHub接口

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd

class IDataHub(ABC):
    """数据中心接口"""

    @abstractmethod
    def get_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        fields: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """获取OHLCV数据

        参数:
            symbol: 股票代码 (e.g. "000001.SZ")
            start_date: 开始日期 (e.g. "2026-01-01")
            end_date: 结束日期 (e.g. "2026-03-28")
            fields: 可选字段列表

        返回:
            DataFrame with columns: date, open, high, low, close, volume

        异常:
            DataNotFoundError: 数据不存在
            DataTimeoutError: 数据获取超时
        """
        pass

    @abstractmethod
    def get_fundamental(
        self,
        symbol: str,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """获取基本面数据

        参数:
            symbol: 股票代码
            fields: 可选字段列表

        返回:
            基本面数据字典
        """
        pass

    @abstractmethod
    def list_symbols(self, market: str = "A") -> List[str]:
        """获取股票列表

        参数:
            market: 市场代码 (e.g. "A", "HK")

        返回:
            股票代码列表
        """
        pass
```

### 3.2 FactorCalculator接口

```python
class IFactorCalculator(ABC):
    """因子计算器接口"""

    @abstractmethod
    def calculate(
        self,
        factor_name: str,
        symbol: str,
        date: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[float]:
        """计算单个因子值

        参数:
            factor_name: 因子名称
            symbol: 股票代码
            date: 日期
            params: 因子参数

        返回:
            因子值，None表示计算失败
        """
        pass

    @abstractmethod
    def batch_calculate(
        self,
        factor_name: str,
        symbols: List[str],
        start_date: str,
        end_date: str,
        params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """批量计算因子

        参数:
            factor_name: 因子名称
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            params: 因子参数

        返回:
            DataFrame with columns: date, symbol, value
        """
        pass

    @abstractmethod
    def validate_factor(
        self,
        factor_name: str,
        ic_threshold: float = 0.03
    ) -> Dict[str, Any]:
        """验证因子有效性

        参数:
            factor_name: 因子名称
            ic_threshold: IC阈值

        返回:
            {'ic': float, 'ir': float, 'valid': bool}
        """
        pass
```

### 3.3 StrategyEngine接口

```python
class IStrategyEngine(ABC):
    """策略引擎接口"""

    @abstractmethod
    def generate_signals(
        self,
        strategy_id: str,
        symbols: List[str],
        date: str
    ) -> List[Signal]:
        """生成交易信号

        参数:
            strategy_id: 策略ID
            symbols: 股票列表
            date: 日期

        返回:
            信号列表
        """
        pass

    @abstractmethod
    def get_position(
        self,
        strategy_id: str,
        symbol: str
    ) -> Position:
        """获取持仓

        参数:
            strategy_id: 策略ID
            symbol: 股票代码

        返回:
            持仓信息
        """
        pass

    @abstractmethod
    def update_position(
        self,
        strategy_id: str,
        symbol: str,
        volume: int,
        price: float
    ) -> None:
        """更新持仓

        参数:
            strategy_id: 策略ID
            symbol: 股票代码
            volume: 持仓量（正买入，负卖出）
            price: 价格
        """
        pass
```

### 3.4 RiskManager接口

```python
class IRiskManager(ABC):
    """风险管理器接口"""

    @abstractmethod
    def check_order(
        self,
        order: Order,
        current_positions: List[Position]
    ) -> OrderCheckResult:
        """检查订单是否通过风控

        参数:
            order: 订单
            current_positions: 当前持仓

        返回:
            {'approved': bool, 'reason': str, 'modified': Order}
        """
        pass

    @abstractmethod
    def calculate_risk_metrics(
        self,
        positions: List[Position],
        portfolio_value: float
    ) -> RiskMetrics:
        """计算风险指标

        参数:
            positions: 持仓列表
            portfolio_value: 组合市值

        返回:
            风险指标
        """
        pass

    @abstractmethod
    def check_drawdown(
        self,
        current_value: float,
        peak_value: float
    ) -> bool:
        """检查回撤是否超限

        参数:
            current_value: 当前值
            peak_value: 历史峰值

        返回:
            True表示超限，需要处理
        """
        pass
```


## 4. FastAPI路由设计

### 4.1 路由结构

```
/api/v1/
├── /data
│   ├── GET  /ohlcv/{symbol}     # 获取K线数据
│   ├── GET  /fundamental/{symbol} # 获取基本面
│   └── GET  /symbols            # 获取股票列表
│
├── /factors
│   ├── GET  /{factor_name}      # 计算因子
│   ├── POST /batch             # 批量计算
│   └── GET  /validate/{name}   # 验证因子
│
├── /strategies
│   ├── GET  /                   # 策略列表
│   ├── POST /signals           # 生成信号
│   ├── GET  /{id}/positions    # 获取持仓
│   └── POST /{id}/orders      # 下单
│
├── /risk
│   ├── POST /check_order       # 风控检查
│   ├── GET  /metrics           # 风险指标
│   └── GET  /limits            # 风险限额
│
└── /system
    ├── GET  /health            # 健康检查
    ├── GET  /version           # 版本信息
    └── GET  /config            # 配置信息
```

### 4.2 示例路由

```python
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

router = APIRouter(prefix="/api/v1", tags=["data"])

@router.get("/data/ohlcv/{symbol}")
async def get_ohlcv(
    symbol: str,
    start_date: str = Query(..., description="开始日期"),
    end_date: str = Query(..., description="结束日期"),
    fields: Optional[str] = Query(None, description="字段列表，逗号分隔")
) -> APIResponse[pd.DataFrame]:
    """获取OHLCV数据"""

    try:
        field_list = fields.split(",") if fields else None
        data = data_hub.get_ohlcv(symbol, start_date, end_date, field_list)
        return APIResponse(data=data)
    except DataNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取OHLCV失败: {e}")
        raise HTTPException(status_code=500, detail="内部错误")
```


## 5. 接口版本控制

### 5.1 URL版本控制

```
/api/v1/data/ohlcv     # v1版本
/api/v2/data/ohlcv     # v2版本
```

### 5.2 兼容性策略

```python
# v1 → v2 兼容策略
class DataAPIV2:
    """v2版本数据API"""

    async def get_ohlcv(self, symbol: str, **kwargs):
        # v2新增参数有默认值，兼容v1调用
        include_extended = kwargs.get('include_extended', False)

        # 调用v1逻辑
        result = await self.v1_get_ohlcv(symbol, **kwargs)

        # v2扩展
        if include_extended:
            result['extended'] = self._calculate_extended(result)

        return result
```


## 6. 接口文档

### 6.1 OpenAPI集成

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="清风量化交易系统API",
    description="量化交易系统的RESTful API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="清风量化交易系统API",
        version="1.0.0",
        description="量化交易系统的RESTful API",
        routes=app.routes,
    )

    # 添加认证信息
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```


## 7. 上下接口映射

| 接口 | 上游(调用者) | 下游(被调用) | 索引 |
|------|-------------|-------------|------|
| DataHub.get_ohlcv | FactorCalculator, StrategyEngine | 数据源(AKShare/Tushare) | DATA.001 |
| FactorCalculator.calculate | StrategyEngine | DataHub | FACT.001 |
| StrategyEngine.generate_signals | API Layer | FactorCalculator, RiskManager | STRAT.001 |
| RiskManager.check_order | StrategyEngine, TradeExecutor | Config, Positions | RISK.001 |
| TradeExecutor.execute | StrategyEngine | Broker API | EXEC.001 |


## 8. 开发任务分解(5h)

| 任务 | 时间 | 交付物 |
|------|------|--------|
| 响应格式标准化 | 1h | APIResponse基类, ErrorCode定义 |
| 模块接口定义 | 2h | IDataHub, IFactorCalculator等接口 |
| FastAPI路由 | 1.5h | REST API实现 |
| 文档集成 | 0.5h | OpenAPI/Swagger配置 |


**维护者**: 清风量化系统
**索引**: `DEV.API.001`
**最后更新**: 2026-03-29
