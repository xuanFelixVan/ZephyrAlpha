---
module_id: DOC_API_CONTRACT_001
version: 5.1.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 专业标准
parent_document: INDEX.md
implementation_status: 进行中
---


# API_Contract.md - 接口契约

> 清风量化系统模块间通信规范


## 1. 通信原则

- **格式**: JSON
- **编码**: UTF-8
- **时间戳**: ISO 8601 格式（UTC）
- **数值精度**: float64（8字节浮点数）
- **错误处理**: 返回 `error` 字段，包含错误码和消息


## 2. 核心接口定义

### 2.1 DataHub → FactorCalculator

**功能**: 传递标准化市场数据

**请求格式**:
```json
{
  "timestamp": "2026-03-28T10:00:00Z",
  "symbol": "000001.SZ",
  "ohlcv": {
    "open": 100.0,
    "high": 102.5,
    "low": 99.5,
    "close": 101.0,
    "volume": 1000000
  },
  "indicators": {
    "ma5": 100.5,
    "ma20": 99.8,
    "ma60": 98.5
  },
  "metadata": {
    "data_source": "akshare",
    "frequency": "1H",
    "quality_score": 0.95
  }
}
```

**响应格式**:
```json
{
  "status": "success",
  "timestamp": "2026-03-28T10:00:00Z",
  "data_id": "DATA_20260328_100000_000001",
  "records_received": 1,
  "records_valid": 1
}
```

**错误响应**:
```json
{
  "status": "error",
  "error_code": "DATA_001",
  "error_message": "Invalid OHLCV data",
  "timestamp": "2026-03-28T10:00:00Z"
}
```


### 2.2 FactorCalculator → StrategyEngine

**功能**: 传递计算后的因子值

**请求格式**:
```json
{
  "timestamp": "2026-03-28T10:00:00Z",
  "symbol": "000001.SZ",
  "factors": {
    "ALPHA_001_TREND": {
      "value": 0.85,
      "signal": "BUY",
      "confidence": 0.92,
      "calculation_time_ms": 12
    },
    "ALPHA_002_MEAN_REVERSION": {
      "value": -0.45,
      "signal": "SELL",
      "confidence": 0.78,
      "calculation_time_ms": 8
    }
  },
  "metadata": {
    "factor_count": 2,
    "calculation_version": "1.0",
    "data_quality": 0.95
  }
}
```

**响应格式**:
```json
{
  "status": "success",
  "timestamp": "2026-03-28T10:00:00Z",
  "factors_processed": 2,
  "factors_valid": 2,
  "strategy_signal": "BUY"
}
```


### 2.3 StrategyEngine → RiskManager

**功能**: 传递策略信号和头寸信息

**请求格式**:
```json
{
  "timestamp": "2026-03-28T10:00:00Z",
  "symbol": "000001.SZ",
  "strategy_id": "S001_TREND_FOLLOW",
  "signal": {
    "action": "BUY",
    "confidence": 0.92,
    "target_price": 102.5,
    "stop_loss": 99.0
  },
  "position": {
    "current_shares": 1000,
    "current_value": 101000,
    "entry_price": 101.0,
    "entry_time": "2026-03-28T09:30:00Z"
  },
  "metadata": {
    "strategy_version": "1.0",
    "market_regime": "UPTREND",
    "signal_strength": 0.92
  }
}
```

**响应格式**:
```json
{
  "status": "success",
  "timestamp": "2026-03-28T10:00:00Z",
  "risk_check": "PASS",
  "approved_action": "BUY",
  "approved_quantity": 500,
  "risk_metrics": {
    "portfolio_var": 0.02,
    "max_drawdown": 0.05,
    "position_limit_utilization": 0.45
  }
}
```

**拒绝响应**:
```json
{
  "status": "rejected",
  "timestamp": "2026-03-28T10:00:00Z",
  "risk_check": "FAIL",
  "rejection_reason": "Position limit exceeded",
  "rejection_code": "RISK_001"
}
```


### 2.4 RiskManager → TradeExecutor

**功能**: 传递已批准的交易订单

**请求格式**:
```json
{
  "timestamp": "2026-03-28T10:00:00Z",
  "order_id": "ORD_20260328_000001",
  "symbol": "000001.SZ",
  "action": "BUY",
  "quantity": 500,
  "order_type": "MARKET",
  "price_limit": 102.0,
  "time_in_force": "DAY",
  "metadata": {
    "strategy_id": "S001_TREND_FOLLOW",
    "risk_approved": true,
    "approval_time": "2026-03-28T10:00:00Z"
  }
}
```

**响应格式**:
```json
{
  "status": "success",
  "timestamp": "2026-03-28T10:00:00Z",
  "order_id": "ORD_20260328_000001",
  "execution_status": "FILLED",
  "filled_quantity": 500,
  "filled_price": 101.8,
  "execution_time": "2026-03-28T10:00:05Z",
  "commission": 50.9
}
```


## 3. 错误码规范

| 错误码 | 含义 | 处理方式 |
|--------|------|---------|
| DATA_001 | 数据格式错误 | 记录日志，跳过该数据 |
| DATA_002 | 数据缺失 | 使用前向填充 |
| FACTOR_001 | 因子计算失败 | 使用备选因子 |
| SIGNAL_001 | 信号生成失败 | 不发出交易信号 |
| RISK_001 | 风险检查失败 | 拒绝交易 |
| EXEC_001 | 执行失败 | 重试3次，失败则告警 |


## 4. 数据类型规范

### 基础类型

| 类型 | 说明 | 示例 |
|------|------|------|
| timestamp | ISO 8601 UTC时间 | "2026-03-28T10:00:00Z" |
| symbol | 股票代码 | "000001.SZ" |
| float | 浮点数 | 101.5 |
| int | 整数 | 1000 |
| string | 字符串 | "BUY" |
| boolean | 布尔值 | true/false |

### 复合类型

```python
# OHLCV 数据
class OHLCV:
    open: float
    high: float
    low: float
    close: float
    volume: int

# 因子值
class FactorValue:
    value: float
    signal: str  # "BUY" / "SELL" / "HOLD"
    confidence: float  # 0.0 - 1.0
    calculation_time_ms: int

# 交易信号
class TradeSignal:
    action: str  # "BUY" / "SELL" / "HOLD"
    confidence: float
    target_price: float
    stop_loss: float
```


## 5. 版本协商

### 版本号格式
```
{major}.{minor}.{patch}
```

### 兼容性规则
- **主版本不兼容**: 接口结构改变
- **次版本向后兼容**: 新增可选字段
- **补丁版本向后兼容**: Bug修复

### 版本检查
```json
{
  "interface_version": "1.0",
  "supported_versions": ["1.0", "1.1"]
}
```


## 6. 超时规范

| 操作 | 超时时间 | 说明 |
|------|----------|------|
| 数据采集 | 30s | 单次API调用 |
| 因子计算 | 5s | 单个因子 |
| 策略信号 | 2s | 单个策略 |
| 风险检查 | 1s | 风控审批 |
| 交易执行 | 10s | 订单提交 |


## 7. 重试策略

```
重试条件: 网络错误、超时、临时服务不可用
重试次数: 最多3次
重试间隔: 指数退避（1s, 2s, 4s）
最大等待: 7s
```


## 8. 日志规范

每个接口调用必须记录：
```json
{
  "timestamp": "2026-03-28T10:00:00Z",
  "interface": "FactorCalculator → StrategyEngine",
  "request_id": "REQ_20260328_000001",
  "status": "success",
  "latency_ms": 12,
  "data_size_bytes": 1024
}
```


## 9. 模块接口定义

### 9.1 DataHub接口

```python
class IDataHub(ABC):
    """数据中心接口

    索引: API.DH.001
    Layer: Layer 0
    上游: 数据源(AKShare/Tushare)
    下游: FactorCalculator, Monitor
    状态: 规划中 (v5.1阶段尚未实现)
    """

    @abstractmethod
    def get_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        fields: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """获取OHLCV数据"""
        pass

    @abstractmethod
    def get_fundamental(
        self,
        symbol: str,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """获取基本面数据"""
        pass

    @abstractmethod
    def list_symbols(self, market: str = "A") -> List[str]:
        """获取股票列表"""
        pass
```

### 9.2 FactorCalculator接口

```python
class IFactorCalculator(ABC):
    """因子计算器接口

    索引: API.FC.001
    Layer: Layer 2
    上游: DataHub
    下游: StrategyEngine
    """

    @abstractmethod
    def calculate(
        self,
        factor_name: str,
        symbol: str,
        date: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[float]:
        """计算单个因子值"""
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
        """批量计算因子"""
        pass
```

### 9.3 StrategyEngine接口

```python
class IStrategyEngine(ABC):
    """策略引擎接口

    索引: API.SE.001
    Layer: Layer 3
    上游: FactorCalculator, RiskManager
    下游: RiskManager, TradeExecutor
    """

    @abstractmethod
    def generate_signals(
        self,
        strategy_id: str,
        symbols: List[str],
        date: str
    ) -> List[Signal]:
        """生成交易信号"""
        pass

    @abstractmethod
    def get_position(
        self,
        strategy_id: str,
        symbol: str
    ) -> Position:
        """获取持仓"""
        pass
```

### 9.4 RiskManager接口

```python
class IRiskManager(ABC):
    """风险管理器接口

    索引: API.RM.001
    Layer: Layer 3
    上游: StrategyEngine, TradeExecutor
    下游: StrategyEngine, TradeExecutor
    """

    @abstractmethod
    def check_order(
        self,
        order: Order,
        current_positions: List[Position]
    ) -> OrderCheckResult:
        """检查订单是否通过风控"""
        pass

    @abstractmethod
    def calculate_risk_metrics(
        self,
        positions: List[Position],
        portfolio_value: float
    ) -> RiskMetrics:
        """计算风险指标"""
        pass
```

### 9.5 模块依赖关系图

```
                    ┌─────────────┐
                    │   DataHub   │◄────────── 数据源 (AKShare/Tushare)
                    └──────┬──────┘
                           │ push/pull
                           ▼
                    ┌─────────────┐
                    │FactorCalc   │
                    └──────┬──────┘
                           │ push
                           ▼
                    ┌─────────────┐
                    │StrategyEng  │
                    └──────┬──────┘
                           │ push
                           ▼
                    ┌─────────────┐
                    │RiskManager  │
                    └──────┬──────┘
                           │ callback/block
                           ▼
                    ┌─────────────┐
                    │TradeExecutor│
                    └──────┬──────┘
                           │ report
                           ▼
                    ┌─────────────┐
                    │   Monitor   │
                    └──────┬──────┘
                           │ alert
                           ▼
                    ┌─────────────┐
                    │   人(监督)  │
                    └─────────────┘
```

### 9.6 版本管理

| 模块 | 版本 | 状态 | 最后更新 |
|------|------|------|----------|
| DataHub | 1.0 | ✅ 稳定 | 2026-03-28 |
| FactorCalculator | 1.0 | ✅ 稳定 | 2026-03-28 |
| StrategyEngine | 1.0 | ✅ 稳定 | 2026-03-28 |
| RiskManager | 1.0 | ✅ 稳定 | 2026-03-28 |
| TradeExecutor | 1.0 | ✅ 稳定 | 2026-03-28 |
| Monitor | 1.0 | ✅ 稳定 | 2026-03-28 |


## 10. 索引清单

| 索引 | 模块/接口 | Layer | 状态 |
|------|-----------|-------|------|
| API.DH.001 | DataHub接口 | 0 | ✅ |
| API.FC.001 | FactorCalculator接口 | 2 | ✅ |
| API.SE.001 | StrategyEngine接口 | 3 | ✅ |
| API.RM.001 | RiskManager接口 | 3 | ✅ |
| API.TE.001 | TradeExecutor接口 | 4 | ✅ |
| API.MO.001 | Monitor接口 | 6 | ✅ |


**版本**: 1.1 | **更新**: 2026-03-29 | **状态**: ✅ 活跃
