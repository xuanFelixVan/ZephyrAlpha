---
module_id: DOC_API_CONTRACT_001
version: 5.3.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: ﻠ۵ﮒﺕ­ﮔﮔ۰۲ﮔﭘﮔﮒﺕ?standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮔ۰۲
applicable_scope: ﮒ۷ﻝﺏﭨﻝﭨ?compliance_level: ﻛﺕﻛﺕﮔ ﮒ
parent_document: INDEX.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?---


# API_Contract.md - ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵

> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨﮔ۷۰ﮒﻠﺑﻠﻛﺟ۰ﻟ۶ﻟ


## 1. ﻠﻛﺟ۰ﮒﮒ

- **ﮔ ﺙﮒﺙ**: JSON
- **ﻝﺙﻝ **: UTF-8
- **ﮔﭘﻠﺑﮔ?*: ISO 8601 ﮔ ﺙﮒﺙﺅﺙUTCﺅﺙ?- **ﮔﺍﮒﺙﻝﺎﺝﮒﭦ?*: float64ﺅﺙ?ﮒ­ﻟﮔﭖ؟ﻝﺗﮔﺍﺅﺙ
- **ﻠﻟﺁﺁﮒ۳ﻝ**: ﻟﺟﮒ `error` ﮒ­ﮔ؟ﭖﺅﺙﮒﮒ،ﻠﻟﺁﺁﻝ ﮒﮔﭘﮔ?

## 2. ﮔ ﺕﮒﺟﮔ۴ﮒ۲ﮒ؟ﻛﺗ

### 2.1 DataHub ﻗ?FactorCalculator

**ﮒﻟﺛ**: ﻛﺙ ﻠﮔ ﮒﮒﮒﺕﮒﭦﮔﺍﮔ؟

**ﻟﺁﺓﮔﺎﮔ ﺙﮒﺙ**:
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

**ﮒﮒﭦﮔ ﺙﮒﺙ**:
```json
{
  "status": "success",
  "timestamp": "2026-03-28T10:00:00Z",
  "data_id": "DATA_20260328_100000_000001",
  "records_received": 1,
  "records_valid": 1
}
```

**ﻠﻟﺁﺁﮒﮒﭦ**:
```json
{
  "status": "error",
  "error_code": "DATA_001",
  "error_message": "Invalid OHLCV data",
  "timestamp": "2026-03-28T10:00:00Z"
}
```


### 2.2 FactorCalculator ﻗ?StrategyEngine

**ﮒﻟﺛ**: ﻛﺙ ﻠﻟ؟۰ﻝ؟ﮒﻝﮒ ﮒ­ﮒ?
**ﻟﺁﺓﮔﺎﮔ ﺙﮒﺙ**:
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

**ﮒﮒﭦﮔ ﺙﮒﺙ**:
```json
{
  "status": "success",
  "timestamp": "2026-03-28T10:00:00Z",
  "factors_processed": 2,
  "factors_valid": 2,
  "strategy_signal": "BUY"
}
```


### 2.3 StrategyEngine ﻗ?RiskManager

**ﮒﻟﺛ**: ﻛﺙ ﻠﻝ­ﻝ۴ﻛﺟ۰ﮒﺓﮒﮒ۳ﺑﮒﺁﺕﻛﺟ۰ﮔﺁ

**ﻟﺁﺓﮔﺎﮔ ﺙﮒﺙ**:
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

**ﮒﮒﭦﮔ ﺙﮒﺙ**:
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

**ﮔﻝﭨﮒﮒﭦ**:
```json
{
  "status": "rejected",
  "timestamp": "2026-03-28T10:00:00Z",
  "risk_check": "FAIL",
  "rejection_reason": "Position limit exceeded",
  "rejection_code": "RISK_001"
}
```


### 2.4 RiskManager ﻗ?TradeExecutor

**ﮒﻟﺛ**: ﻛﺙ ﻠﮒﺓﺎﮔﺗﮒﻝﻛﭦ۳ﮔﻟ؟۱ﮒ?
**ﻟﺁﺓﮔﺎﮔ ﺙﮒﺙ**:
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

**ﮒﮒﭦﮔ ﺙﮒﺙ**:
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


## 3. ﻠﻟﺁﺁﻝ ﻟ۶ﻟ?
| ﻠﻟﺁﺁﻝ ?| ﮒ،ﻛﺗ | ﮒ۳ﻝﮔﺗﮒﺙ |
|--------|------|---------|
| DATA_001 | ﮔﺍﮔ؟ﮔ ﺙﮒﺙﻠﻟﺁﺁ | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺓﺏﻟﺟﻟﺁ۴ﮔﺍﮔ؟ |
| DATA_002 | ﮔﺍﮔ؟ﻝﺙﭦﮒ۳ﺎ | ﻛﺛﺟﻝ۷ﮒﮒﮒ۰،ﮒ |
| FACTOR_001 | ﮒ ﮒ­ﻟ؟۰ﻝ؟ﮒ۳ﺎﻟﺑ۴ | ﻛﺛﺟﻝ۷ﮒ۳ﻠﮒ ﮒ­?|
| SIGNAL_001 | ﻛﺟ۰ﮒﺓﻝﮔﮒ۳ﺎﻟﺑ۴ | ﻛﺕﮒﮒﭦﻛﭦ۳ﮔﻛﺟ۰ﮒ?|
| RISK_001 | ﻠ۲ﻠ۸ﮔ۲ﮔ۴ﮒ۳ﺎﻟﺑ?| ﮔﻝﭨﻛﭦ۳ﮔ |
| EXEC_001 | ﮔ۶ﻟ۰ﮒ۳ﺎﻟﺑ۴ | ﻠﻟﺁ3ﮔ؛۰ﺅﺙﮒ۳ﺎﻟﺑ۴ﮒﮒﻟ­?|


## 4. ﮔﺍﮔ؟ﻝﺎﭨﮒﻟ۶ﻟ

### ﮒﭦﻝ۰ﻝﺎﭨﮒ

| ﻝﺎﭨﮒ | ﻟﺁﺑﮔ | ﻝ۳ﭦﻛﺝ |
|------|------|------|
| timestamp | ISO 8601 UTCﮔﭘﻠﺑ | "2026-03-28T10:00:00Z" |
| symbol | ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ  | "000001.SZ" |
| float | ﮔﭖ؟ﻝﺗﮔ?| 101.5 |
| int | ﮔﺑﮔﺍ | 1000 |
| string | ﮒ­ﻝ؛۵ﻛﺕ?| "BUY" |
| boolean | ﮒﺕﮒﺍﮒ?| true/false |

### ﮒ۳ﮒﻝﺎﭨﮒ

```python
# OHLCV ﮔﺍﮔ؟
class OHLCV:
    open: float
    high: float
    low: float
    close: float
    volume: int

# ﮒ ﮒ­ﮒ?class FactorValue:
    value: float
    signal: str  # "BUY" / "SELL" / "HOLD"
    confidence: float  # 0.0 - 1.0
    calculation_time_ms: int

# ﻛﭦ۳ﮔﻛﺟ۰ﮒﺓ
class TradeSignal:
    action: str  # "BUY" / "SELL" / "HOLD"
    confidence: float
    target_price: float
    stop_loss: float
```


## 5. ﻝﮔ؛ﮒﮒ

### ﻝﮔ؛ﮒﺓﮔ ﺙﮒﺙ?```
{major}.{minor}.{patch}
```

### ﮒﺙﮒ؟ﺗﮔ۶ﻟ۶ﮒ?- **ﻛﺕﭨﻝﮔ؛ﻛﺕﮒﺙﮒ؟ﺗ**: ﮔ۴ﮒ۲ﻝﭨﮔﮔﺗﮒ
- **ﮔ؛۰ﻝﮔ؛ﮒﮒﮒﺙﮒ؟?*: ﮔﺍﮒ۱ﮒﺁﻠﮒ­ﮔ؟?- **ﻟ۰۴ﻛﺕﻝﮔ؛ﮒﮒﮒﺙﮒ؟ﺗ**: Bugﻛﺟ؟ﮒ۳

### ﻝﮔ؛ﮔ۲ﮔ?```json
{
  "interface_version": "1.0",
  "supported_versions": ["1.0", "1.1"]
}
```


## 6. ﻟﭘﮔﭘﻟ۶ﻟ

| ﮔﻛﺛ | ﻟﭘﮔﭘﮔﭘﻠﺑ | ﻟﺁﺑﮔ |
|------|----------|------|
| ﮔﺍﮔ؟ﻠﻠ | 30s | ﮒﮔ؛۰APIﻟﺍﻝ۷ |
| ﮒ ﮒ­ﻟ؟۰ﻝ؟ | 5s | ﮒﻛﺕ۹ﮒ ﮒ­ |
| ﻝ­ﻝ۴ﻛﺟ۰ﮒﺓ | 2s | ﮒﻛﺕ۹ﻝ­ﻝ۴ |
| ﻠ۲ﻠ۸ﮔ۲ﮔ?| 1s | ﻠ۲ﮔ۶ﮒ؟۰ﮔﺗ |
| ﻛﭦ۳ﮔﮔ۶ﻟ۰ | 10s | ﻟ؟۱ﮒﮔﻛﭦ۳ |


## 7. ﻠﻟﺁﻝ­ﻝ۴

```
ﻠﻟﺁﮔ۰ﻛﭨﭘ: ﻝﺛﻝﭨﻠﻟﺁﺁﻙﻟﭘﮔﭘﻙﻛﺕﺑﮔﭘﮔﮒ۰ﻛﺕﮒﺁﻝ۷
ﻠﻟﺁﮔ؛۰ﮔﺍ: ﮔﮒ۳?ﮔ؛?ﻠﻟﺁﻠﺑﻠ: ﮔﮔﺍﻠﻠﺟﺅﺙ1s, 2s, 4sﺅﺙ?ﮔﮒ۳۶ﻝ­ﮒﺝ? 7s
```


## 8. ﮔ۴ﮒﺟﻟ۶ﻟ

ﮔﺁﻛﺕ۹ﮔ۴ﮒ۲ﻟﺍﻝ۷ﮒﺟﻠ۰ﭨﻟ؟ﺍﮒﺛﺅﺙ?```json
{
  "timestamp": "2026-03-28T10:00:00Z",
  "interface": "FactorCalculator ﻗ?StrategyEngine",
  "request_id": "REQ_20260328_000001",
  "status": "success",
  "latency_ms": 12,
  "data_size_bytes": 1024
}
```


## 9. ﮔ۷۰ﮒﮔ۴ﮒ۲ﮒ؟ﻛﺗ

### 9.1 DataHubﮔ۴ﮒ۲

```python
class IDataHub(ABC):
    """ﮔﺍﮔ؟ﻛﺕ­ﮒﺟﮔ۴ﮒ۲

    ﻝﺑ۱ﮒﺙ: API.DH.001
    Layer: Layer 0
    ﻛﺕﮔﺕﺕ: ﮔﺍﮔ؟ﮔﭦ?AKShare/Tushare)
    ﻛﺕﮔﺕﺕ: FactorCalculator, Monitor
    ﻝﭘﮔ? ﻟ۶ﮒﻛﺕ?(v5.3ﻠﭘﮔ؟ﭖﮒﺍﮔ۹ﮒ؟ﻝﺍ)
    """

    @abstractmethod
    def get_ohlcv(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        fields: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """ﻟﺓﮒOHLCVﮔﺍﮔ؟"""
        pass

    @abstractmethod
    def get_fundamental(
        self,
        symbol: str,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """ﻟﺓﮒﮒﭦﮔ؛ﻠ۱ﮔﺍﮔ?""
        pass

    @abstractmethod
    def list_symbols(self, market: str = "A") -> List[str]:
        """ﻟﺓﮒﻟ۰ﻝ۴۷ﮒﻟ۰۷"""
        pass
```

### 9.2 FactorCalculatorﮔ۴ﮒ۲

```python
class IFactorCalculator(ABC):
    """ﮒ ﮒ­ﻟ؟۰ﻝ؟ﮒ۷ﮔ۴ﮒ?
    ﻝﺑ۱ﮒﺙ: API.FC.001
    Layer: Layer 2
    ﻛﺕﮔﺕﺕ: DataHub
    ﻛﺕﮔﺕﺕ: StrategyEngine
    """

    @abstractmethod
    def calculate(
        self,
        factor_name: str,
        symbol: str,
        date: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[float]:
        """ﻟ؟۰ﻝ؟ﮒﻛﺕ۹ﮒ ﮒ­ﮒ?""
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
        """ﮔﺗﻠﻟ؟۰ﻝ؟ﮒ ﮒ­"""
        pass
```

### 9.3 StrategyEngineﮔ۴ﮒ۲

```python
class IStrategyEngine(ABC):
    """ﻝ­ﻝ۴ﮒﺙﮔﮔ۴ﮒ۲

    ﻝﺑ۱ﮒﺙ: API.SE.001
    Layer: Layer 3
    ﻛﺕﮔﺕﺕ: FactorCalculator, RiskManager
    ﻛﺕﮔﺕﺕ: RiskManager, TradeExecutor
    """

    @abstractmethod
    def generate_signals(
        self,
        strategy_id: str,
        symbols: List[str],
        date: str
    ) -> List[Signal]:
        """ﻝﮔﻛﭦ۳ﮔﻛﺟ۰ﮒﺓ"""
        pass

    @abstractmethod
    def get_position(
        self,
        strategy_id: str,
        symbol: str
    ) -> Position:
        """ﻟﺓﮒﮔﻛﭨ"""
        pass
```

### 9.4 RiskManagerﮔ۴ﮒ۲

```python
class IRiskManager(ABC):
    """ﻠ۲ﻠ۸ﻝ؟۰ﻝﮒ۷ﮔ۴ﮒ?
    ﻝﺑ۱ﮒﺙ: API.RM.001
    Layer: Layer 3
    ﻛﺕﮔﺕﺕ: StrategyEngine, TradeExecutor
    ﻛﺕﮔﺕﺕ: StrategyEngine, TradeExecutor
    """

    @abstractmethod
    def check_order(
        self,
        order: Order,
        current_positions: List[Position]
    ) -> OrderCheckResult:
        """ﮔ۲ﮔ۴ﻟ؟۱ﮒﮔﺁﮒ۵ﻠﻟﺟﻠ۲ﮔ۶"""
        pass

    @abstractmethod
    def calculate_risk_metrics(
        self,
        positions: List[Position],
        portfolio_value: float
    ) -> RiskMetrics:
        """ﻟ؟۰ﻝ؟ﻠ۲ﻠ۸ﮔﮔ """
        pass
```

### 9.5 ﮔ۷۰ﮒﻛﺝﻟﭖﮒﺏﻝﺏﭨﮒ?
```
                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                    ﻗ?  DataHub   ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ ﮔﺍﮔ؟ﮔﭦ?(AKShare/Tushare)
                    ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?                           ﻗ?push/pull
                           ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                    ﻗFactorCalc   ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?                           ﻗ?push
                           ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                    ﻗStrategyEng  ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?                           ﻗ?push
                           ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                    ﻗRiskManager  ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?                           ﻗ?callback/block
                           ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                    ﻗTradeExecutorﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?                           ﻗ?report
                           ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                    ﻗ?  Monitor   ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗ؛ﻗﻗﻗﻗﻗﻗﻗ?                           ﻗ?alert
                           ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                    ﻗ?  ﻛﭦ?ﻝﻝ۲)  ﻗ?                    ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?```

### 9.6 ﻝﮔ؛ﻝ؟۰ﻝ

| ﮔ۷۰ﮒ | ﻝﮔ؛ | ﻝﭘﮔ?| ﮔﮒﮔﺑﮔ?|
|------|------|------|----------|
| DataHub | 1.0 | ﻗ?ﻝ۷ﺏﮒ؟ | 2026-03-28 |
| FactorCalculator | 1.0 | ﻗ?ﻝ۷ﺏﮒ؟ | 2026-03-28 |
| StrategyEngine | 1.0 | ﻗ?ﻝ۷ﺏﮒ؟ | 2026-03-28 |
| RiskManager | 1.0 | ﻗ?ﻝ۷ﺏﮒ؟ | 2026-03-28 |
| TradeExecutor | 1.0 | ﻗ?ﻝ۷ﺏﮒ؟ | 2026-03-28 |
| Monitor | 1.0 | ﻗ?ﻝ۷ﺏﮒ؟ | 2026-03-28 |


## 10. ﻝﺑ۱ﮒﺙﮔﺕﮒ

| ﻝﺑ۱ﮒﺙ | ﮔ۷۰ﮒ/ﮔ۴ﮒ۲ | Layer | ﻝﭘﮔ?|
|------|-----------|-------|------|
| API.DH.001 | DataHubﮔ۴ﮒ۲ | 0 | ﻗ?|
| API.FC.001 | FactorCalculatorﮔ۴ﮒ۲ | 2 | ﻗ?|
| API.SE.001 | StrategyEngineﮔ۴ﮒ۲ | 3 | ﻗ?|
| API.RM.001 | RiskManagerﮔ۴ﮒ۲ | 3 | ﻗ?|
| API.TE.001 | TradeExecutorﮔ۴ﮒ۲ | 4 | ﻗ?|
| API.MO.001 | Monitorﮔ۴ﮒ۲ | 6 | ﻗ?|


**ﻝﮔ؛**: 1.1 | **ﮔﺑﮔﺍ**: 2026-03-29 | **ﻝﭘﮔ?*: ﻗ?ﮔﺑﭨﻟﺓ
