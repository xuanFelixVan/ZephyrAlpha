---
module_id: AUTO_GENERATED_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: '2026-04-07'
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
- 交易策略设计与实施管理与优化维护
module_id: DOC_API_CONTRACT_001
version: 5.3.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: ﻠ۵ﮒﺕﮔﮔ۰۲ﮔﭘﮔﮒﺕ?standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮔ۰۲
applicable_scope: ﮒ۷ﻝﺏﭨﻝﭨ?compliance_level: ﻛﺕﻛﺕﮔﮒ
parent_document: INDEX.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?
---


# API_Contract.md - ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨﮔ۷۰ﮒﻠﺑﻠﻛﺟ۰ﻟ۶ﻟ


## 1. ﻠﻛﺟ۰ﮒﮒ

- **ﮔﺙﮒﺙ**: JSON
- **ﻝﺙﻝ**: UTF-8
- **ﮔﭘﻠﺑﮔ?*: ISO 8601 ﮔﺙﮒﺙﺅﺙUTCﺅﺙ?- **ﮔﺍﮒﺙﻝﺎﺝﮒﭦ?*: float64ﺅﺙ?ﮒﻟﮔﭖ؟ﻝﺗﮔﺍﺅﺙ
- **ﻠﻟﺁﺁﮒ۳ﻝ**: ﻟﺟﮒ `error` ﮒﮔ؟ﭖﺅﺙﮒﮒ،ﻠﻟﺁﺁﻝﮒﮔﭘﮔ?

## 2. ﮔﺕﮒﺟﮔ۴ﮒ۲ﮒ؟ﻛﺗ

### 2.1 DataHub ﻗ?FactorCalculator

**ﮒﻟﺛ**: ﻛﺙﻠﮔﮒﮒﮒﺕﮒﭦﮔﺍﮔ؟

**ﻟﺁﺓﮔﺎﮔﺙﮒﺙ**:
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

**ﮒﮒﭦﮔﺙﮒﺙ**:
```json
{
  "status": "success",
  "timestamp": "2026-03-28T10:00:00Z",
  "data_id": "DATA_20260328_100000_000001",
  "records_received": 1,
  "records_valid": 1
}
```

**ﻠﻟﺁﺁﮒﮒﭦ**:
```json
{
  "status": "error",
  "error_code": "DATA_001",
  "error_message": "Invalid OHLCV data",
  "timestamp": "2026-03-28T10:00:00Z"
}
```


### 2.2 FactorCalculator ﻗ?StrategyEngine

**ﮒﻟﺛ**: ﻛﺙﻠﻟ؟۰ﻝ؟ﮒﻝﮒﮒﮒ?
**ﻟﺁﺓﮔﺎﮔﺙﮒﺙ**:
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

**ﮒﮒﭦﮔﺙﮒﺙ**:
```json
{
  "status": "success",
  "timestamp": "2026-03-28T10:00:00Z",
  "factors_processed": 2,
  "factors_valid": 2,
  "strategy_signal": "BUY"
}
```


### 2.3 StrategyEngine ﻗ?RiskManager

**ﮒﻟﺛ**: ﻛﺙﻠﻝﻝ۴ﻛﺟ۰ﮒﺓﮒﮒ۳ﺑﮒﺁﺕﻛﺟ۰ﮔﺁ

**ﻟﺁﺓﮔﺎﮔﺙﮒﺙ**:
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

**ﮒﮒﭦﮔﺙﮒﺙ**:
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

**ﮔﻝﭨﮒﮒﭦ**:
```json
{
  "status": "rejected",
  "timestamp": "2026-03-28T10:00:00Z",
  "risk_check": "FAIL",
  "rejection_reason": "Position limit exceeded",
  "rejection_code": "RISK_001"
}
```


### 2.4 RiskManager ﻗ?TradeExecutor

**ﮒﻟﺛ**: ﻛﺙﻠﮒﺓﺎﮔﺗﮒﻝﻛﭦ۳ﮔﻟ؟۱ﮒ?
**ﻟﺁﺓﮔﺎﮔﺙﮒﺙ**:
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

**ﮒﮒﭦﮔﺙﮒﺙ**:
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


## 3. ﻠﻟﺁﺁﻝﻟ۶ﻟ?
| ﻠﻟﺁﺁﻝ?| ﮒ،ﻛﺗ | ﮒ۳ﻝﮔﺗﮒﺙ |
|--------|------|---------|
| DATA_001 | ﮔﺍﮔ؟ﮔﺙﮒﺙﻠﻟﺁﺁ | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺓﺏﻟﺟﻟﺁ۴ﮔﺍﮔ؟ |
| DATA_002 | ﮔﺍﮔ؟ﻝﺙﭦﮒ۳ﺎ | ﻛﺛﺟﻝ۷ﮒﮒﮒ۰،ﮒ |
| FACTOR_001 | ﮒﮒﻟ؟۰ﻝ؟ﮒ۳ﺎﻟﺑ۴ | ﻛﺛﺟﻝ۷ﮒ۳ﻠﮒﮒ?|
| SIGNAL_001 | ﻛﺟ۰ﮒﺓﻝﮔﮒ۳ﺎﻟﺑ۴ | ﻛﺕﮒﮒﭦﻛﭦ۳ﮔﻛﺟ۰ﮒ?|
| RISK_001 | ﻠ۲ﻠ۸ﮔ۲ﮔ۴ﮒ۳ﺎﻟﺑ?| ﮔﻝﭨﻛﭦ۳ﮔ |
| EXEC_001 | ﮔ۶ﻟ۰ﮒ۳ﺎﻟﺑ۴ | ﻠﻟﺁ3ﮔ؛۰ﺅﺙﮒ۳ﺎﻟﺑ۴ﮒﮒﻟ?|


## 4. ﮔﺍﮔ؟ﻝﺎﭨﮒﻟ۶ﻟ

### ﮒﭦﻝ۰ﻝﺎﭨﮒ

| ﻝﺎﭨﮒ | ﻟﺁﺑﮔ | ﻝ۳ﭦﻛﺝ |
|------|------|------|
| timestamp | ISO 8601 UTCﮔﭘﻠﺑ | "2026-03-28T10:00:00Z" |
| symbol | ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ | "000001.SZ" |
| float | ﮔﭖ؟ﻝﺗﮔ?| 101.5 |
| int | ﮔﺑﮔﺍ | 1000 |
| string | ﮒﻝ؛۵ﻛﺕ?| "BUY" |
| boolean | ﮒﺕﮒﺍﮒ?| true/false |

### ﮒ۳ﮒﻝﺎﭨﮒ

```python
# OHLCV ﮔﺍﮔ؟
class OHLCV:
    open: float
    high: float
    low: float
    close: float
    volume: int

# ﮒﮒﮒ?class FactorValue:
    value: float
    signal: str  # "BUY" / "SELL" / "HOLD"
    confidence: float  # 0.0 - 1.0
    calculation_time_ms: int

# ﻛﭦ۳ﮔﻛﺟ۰ﮒﺓ
class TradeSignal:
    action: str  # "BUY" / "SELL" / "HOLD"
    confidence: float
    target_price: float
    stop_loss: float
```


## 5. ﻝﮔ؛ﮒﮒ

### ﻝﮔ؛ﮒﺓﮔﺙﮒﺙ?```
{major}.{minor}.{patch}
```

### ﮒﺙﮒ؟ﺗﮔ۶ﻟ۶ﮒ?- **ﻛﺕﭨﻝﮔ؛ﻛﺕﮒﺙﮒ؟ﺗ**: ﮔ۴ﮒ۲ﻝﭨﮔﮔﺗﮒ
- **ﮔ؛۰ﻝﮔ؛ﮒﮒﮒﺙﮒ؟?*: ﮔﺍﮒ۱ﮒﺁﻠﮒﮔ؟?- **ﻟ۰۴ﻛﺕﻝﮔ؛ﮒﮒﮒﺙﮒ؟ﺗ**: Bugﻛﺟ؟ﮒ۳

### ﻝﮔ؛ﮔ۲ﮔ?```json
{
  "interface_version": "1.0",
  "supported_versions": ["1.0", "1.1"]
}
```


## 6. ﻟﭘﮔﭘﻟ۶ﻟ

| ﮔﻛﺛ | ﻟﭘﮔﭘﮔﭘﻠﺑ | ﻟﺁﺑﮔ |
|------|----------|------|
| ﮔﺍﮔ؟ﻠﻠ | 30s | ﮒﮔ؛۰APIﻟﺍﻝ۷ |
| ﮒﮒﻟ؟۰ﻝ؟ | 5s | ﮒﻛﺕ۹ﮒﮒ |
| ﻝﻝ۴ﻛﺟ۰ﮒﺓ | 2s | ﮒﻛﺕ۹ﻝﻝ۴ |
| ﻠ۲ﻠ۸ﮔ۲ﮔ?| 1s | ﻠ۲ﮔ۶ﮒ؟۰ﮔﺗ |
| ﻛﭦ۳ﮔﮔ۶ﻟ۰ | 10s | ﻟ؟۱ﮒﮔﻛﭦ۳ |


## 7. ﻠﻟﺁﻝﻝ۴

```
ﻠﻟﺁﮔ۰ﻛﭨﭘ: ﻝﺛﻝﭨﻠﻟﺁﺁﻙﻟﭘﮔﭘﻙﻛﺕﺑﮔﭘﮔﮒ۰ﻛﺕﮒﺁﻝ۷
ﻠﻟﺁﮔ؛۰ﮔﺍ: ﮔﮒ۳?ﮔ؛?ﻠﻟﺁﻠﺑﻠ: ﮔﮔﺍﻠﻠﺟﺅﺙ1s, 2s, 4sﺅﺙ?ﮔﮒ۳۶ﻝﮒﺝ? 7s
```


## 8. ﮔ۴ﮒﺟﻟ۶ﻟ

ﮔﺁﻛﺕ۹ﮔ۴ﮒ۲ﻟﺍﻝ۷ﮒﺟﻠ۰ﭨﻟ؟ﺍﮒﺛﺅﺙ?```json
{
  "timestamp": "2026-03-28T10:00:00Z",
  "interface": "FactorCalculator ﻗ?StrategyEngine",
  "request_id": "REQ_20260328_000001",
  "status": "success",
  "latency_ms": 12,
  "data_size_bytes": 1024
}
```


## 9. ﮔ۷۰ﮒﮔ۴ﮒ۲ﮒ؟ﻛﺗ

### 9.1 DataHubﮔ۴ﮒ۲

```python
class IDataHub(ABC):
"""ﮔﺍﮔ؟ﻛﺕﮒﺟﮔ۴ﮒ۲

    ﻝﺑ۱ﮒﺙ: API.DH.001
    Layer: Layer 0
    ﻛﺕﮔﺕﺕ: ﮔﺍﮔ؟ﮔﭦ?AKShare/Tushare)
    ﻛﺕﮔﺕﺕ: FactorCalculator, Monitor
    ﻝﭘﮔ? ﻟ۶ﮒﻛﺕ?(v5.3ﻠﭘﮔ؟ﭖﮒﺍﮔ۹ﮒ؟ﻝﺍ)
    """

    @abstractmethod
    def get_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        fields: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """ﻟﺓﮒOHLCVﮔﺍﮔ؟"""
        pass

    @abstractmethod
    def get_fundamental(
        self,
        symbol: str,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """ﻟﺓﮒﮒﭦﮔ؛ﻠ۱ﮔﺍﮔ?""
        pass

    @abstractmethod
    def list_symbols(self, market: str = "A") -> List[str]:
        """ﻟﺓﮒﻟ۰ﻝ۴۷ﮒﻟ۰۷"""
        pass
```

### 9.2 FactorCalculatorﮔ۴ﮒ۲

```python
class IFactorCalculator(ABC):
"""ﮒﮒﻟ؟۰ﻝ؟ﮒ۷ﮔ۴ﮒ?
    ﻝﺑ۱ﮒﺙ: API.FC.001
    Layer: Layer 2
    ﻛﺕﮔﺕﺕ: DataHub
    ﻛﺕﮔﺕﺕ: StrategyEngine
    """

    @abstractmethod
    def calculate(
        self,
        factor_name: str,
        symbol: str,
        date: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[float]:
"""ﻟ؟۰ﻝ؟ﮒﻛﺕ۹ﮒﮒﮒ?""
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
"""ﮔﺗﻠﻟ؟۰ﻝ؟ﮒﮒ"""
        pass
```

### 9.3 StrategyEngineﮔ۴ﮒ۲

```python
class IStrategyEngine(ABC):
"""ﻝﻝ۴ﮒﺙﮔﮔ۴ﮒ۲

    ﻝﺑ۱ﮒﺙ: API.SE.001
    Layer: Layer 3
    ﻛﺕﮔﺕﺕ: FactorCalculator, RiskManager
    ﻛﺕﮔﺕﺕ: RiskManager, TradeExecutor
    """

    @abstractmethod
    def generate_signals(
        self,
        strategy_id: str,
        symbols: List[str],
        date: str
    ) -> List[Signal]:
        """ﻝﮔﻛﭦ۳ﮔﻛﺟ۰ﮒﺓ"""
        pass

    @abstractmethod
    def get_position(
        self,
        strategy_id: str,
        symbol: str
    ) -> Position:
        """ﻟﺓﮒﮔﻛﭨ"""
        pass
```

### 9.4 RiskManagerﮔ۴ﮒ۲

```python
class IRiskManager(ABC):
    """ﻠ۲ﻠ۸ﻝ؟۰ﻝﮒ۷ﮔ۴ﮒ?
    ﻝﺑ۱ﮒﺙ: API.RM.001
    Layer: Layer 3
    ﻛﺕﮔﺕﺕ: StrategyEngine, TradeExecutor
    ﻛﺕﮔﺕﺕ: StrategyEngine, TradeExecutor
    """

    @abstractmethod
    def check_order(
        self,
        order: Order,
        current_positions: List[Position]
    ) -> OrderCheckResult:
        """ﮔ۲ﮔ۴ﻟ؟۱ﮒﮔﺁﮒ۵ﻠﻟﺟﻠ۲ﮔ۶"""
        pass

    @abstractmethod
    def calculate_risk_metrics(
        self,
        positions: List[Position],
        portfolio_value: float
    ) -> RiskMetrics:
"""ﻟ؟۰ﻝ؟ﻠ۲ﻠ۸ﮔﮔ"""
        pass
```

### 9.5 ﮔ۷۰ﮒﻛﺝﻟﭖﮒﺏﻝﺏﭨﮒ?
```
                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                    ﻗ?  DataHub   ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ ﮔﺍﮔ؟ﮔﭦ?(AKShare/Tushare)
                    ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?                           ﻗ?push/pull
                           ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                    ﻗFactorCalc   ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?                           ﻗ?push
                           ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                    ﻗStrategyEng  ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?                           ﻗ?push
                           ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                    ﻗRiskManager  ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?                           ﻗ?callback/block
                           ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                    ﻗTradeExecutorﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?                           ﻗ?report
                           ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                    ﻗ?  Monitor   ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?                           ﻗ?alert
                           ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                    ﻗ?  ﻛﭦ?ﻝﻝ۲)  ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?```

### 9.6 ﻝﮔ؛ﻝ؟۰ﻝ

| ﮔ۷۰ﮒ | ﻝﮔ؛ | ﻝﭘﮔ?| ﮔﮒﮔﺑﮔ?|
|------|------|------|----------|
| DataHub | 1.0 | ﻗ?ﻝ۷ﺏﮒ؟ | 2026-03-28 |
| FactorCalculator | 1.0 | ﻗ?ﻝ۷ﺏﮒ؟ | 2026-03-28 |
| StrategyEngine | 1.0 | ﻗ?ﻝ۷ﺏﮒ؟ | 2026-03-28 |
| RiskManager | 1.0 | ﻗ?ﻝ۷ﺏﮒ؟ | 2026-03-28 |
| TradeExecutor | 1.0 | ﻗ?ﻝ۷ﺏﮒ؟ | 2026-03-28 |
| Monitor | 1.0 | ﻗ?ﻝ۷ﺏﮒ؟ | 2026-03-28 |


## 10. ﻝﺑ۱ﮒﺙﮔﺕﮒ

| ﻝﺑ۱ﮒﺙ | ﮔ۷۰ﮒ/ﮔ۴ﮒ۲ | Layer | ﻝﭘﮔ?|
|------|-----------|-------|------|
| API.DH.001 | DataHubﮔ۴ﮒ۲ | 0 | ﻗ?|
| API.FC.001 | FactorCalculatorﮔ۴ﮒ۲ | 2 | ﻗ?|
| API.SE.001 | StrategyEngineﮔ۴ﮒ۲ | 3 | ﻗ?|
| API.RM.001 | RiskManagerﮔ۴ﮒ۲ | 3 | ﻗ?|
| API.TE.001 | TradeExecutorﮔ۴ﮒ۲ | 4 | ﻗ?|
| API.MO.001 | Monitorﮔ۴ﮒ۲ | 6 | ﻗ?|


**ﻝﮔ؛**: 1.1 | **ﮔﺑﮔﺍ**: 2026-03-29 | **ﻝﭘﮔ?*: ﻗ?ﮔﺑﭨﻟﺓ

---

## 11. StrategyAuthoringAssistant（文字/对话 → 策略配置）子契约（增补）

> **目的**：把“文字/对话”输入转为 **可执行且可校验** 的 `StrategyConfig`，并能触发回测与报告；同时落盘审计字段，保证可复现与可追溯。

### 11.1 对象：StrategyDraft（草案）

```json
{
  "draft_id": "draft_20260408_0001",
  "user_text": "我想做一个均线趋势策略：5日上穿20日买入，下穿卖出；最大回撤不超过10%；回测2019-2024。",
  "clarifications": [
    {"question": "标的范围是什么？", "answer": "沪深300成分股"},
    {"question": "调仓频率？", "answer": "日频"},
    {"question": "交易成本假设？", "answer": "单边万三，滑点万二"}
  ],
  "missing_fields": ["benchmark_id"],
  "proposed_config": {
    "strategy_id": "SMA_CROSS_001",
    "version": "1.0.0",
    "universe": {"type": "index_components", "index_id": "CSI300"},
    "timeframe": "1D",
    "signals": {"type": "sma_cross", "fast": 5, "slow": 20},
    "risk_controls": {"max_drawdown_pct": 0.10},
    "execution_assumptions": {"commission_bps": 3, "slippage_bps": 2}
  }
}
```

### 11.2 对象：StrategyConfig（可执行配置，必须通过校验）

```json
{
  "strategy_id": "SMA_CROSS_001",
  "version": "1.0.0",
  "strategy_config_version": "cfg_20260408_0001",
  "dataset_id": "dataset_cn_equity_eod_v1",
  "seed": 42,
  "universe": {"type": "index_components", "index_id": "CSI300"},
  "timeframe": "1D",
  "signals": {"type": "sma_cross", "fast": 5, "slow": 20},
  "risk_controls": {"max_drawdown_pct": 0.10, "position_limit_pct": 0.05},
  "execution_assumptions": {"commission_bps": 3, "slippage_bps": 2},
  "backtest_plan": {
    "start_date": "2019-01-01",
    "end_date": "2024-12-31",
    "benchmark_id": "CSI300",
    "parameter_sweep": null
  }
}
```

### 11.3 API：生成草案 / 校验配置 / 触发回测 / 获取报告

#### POST /strategy_drafts

- **输入**：`user_text` + （可选）`context`（如标的范围、偏好、禁忌）
- **输出**：`StrategyDraft`

#### POST /strategy_specs/validate

- **输入**：`StrategyConfig`
- **输出**：校验结果（通过/失败 + 字段级错误）

```json
{
  "valid": false,
  "errors": [
    {"path": "backtest_plan.benchmark_id", "message": "required"},
    {"path": "signals.fast", "message": "must be < signals.slow"}
  ]
}
```

#### POST /backtests

- **输入**：`StrategyConfig`
- **输出**：`backtest_id` + 回测元信息（含审计字段回显）

#### GET /reports/{report_id}

- **输出**：报告元信息 + 可下载的产物引用（HTML/PDF/JSON）

### 11.4 审计字段（必须落盘）

- `strategy_id` / `version` / `strategy_config_version`
- `dataset_id`（数据集/口径版本）
- `seed`（随机性控制：抽样/蒙特卡洛/重采样等）
- `engine_version`（策略引擎/回测引擎版本）
- `created_at` / `created_by`（用户或 Agent）
