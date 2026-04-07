---
module_id: BACKTEST_ENGINE_GUIDE_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ?
responsibility:
  - 实施指南、部署文档
  - 回测系统
  - 绩效分析
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮒ؟ﮔﺛﮔﮒ
applicable_scope: ﮒﮔﭖﮒﺙﮔﮔ۷۰ﮒﮒ؟ﮔﺛ
compliance_level: ﻛﺕﻛﺕﮔ ﮒ
parent_document: ../README.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?---


# ﮒﮔﭖﮒﺙﮔﮒ؟ﮔﺛﮔﮒ
> **核心职责**: 使用指南和教程
> **职责边界**: 
> - ✅ 本文档负责：使用指南和教程相关内容
> - ❌ 本文档不负责：其他模块内容


> **ﻝﮔ؛**: v1.0
> **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02
> **ﻟﻟﺑ۲**: ﮔﮒﺁﺙBacktesting.pyﮒﮔﭖﮒﺙﮔﻝﻠﮔﮒﻠﻠ
> **ﮒ؟ﮔﺛﮒ۷ﮔ**: 2ﮒ۷ﺅﺙWeek 3-4ﺅﺙ?
> **ﻛﺙﮒﻝﭦ?*: P0

---

## ﻭ ﮒ؟ﮔﺛﮔ۵ﻟ۶

### ﻝ؟ﮔ 

ﻠﮔBacktesting.pyﮒﺙﮔﭦﮒﮔﭖﮒﺙﮔﺅﺙﮒ؟ﻝﺍﻛﺕﻝﺏﭨﻝﭨﻝ­ﻝ۴ﮔ۰ﮔﭘﻝﮔ ﻝﺙﮒﺁﺗﮔ۴ﻙ?

### ﮔ ﺕﮒﺟﮒﻟﺛ

- **ﻝ­ﻝ۴ﻠﻠ**: ﮒﺍﻝﺏﭨﻝﭨﻝ­ﻝ۴ﻠﻠﻛﺕﭦBacktesting.pyﮔ ﺙﮒﺙ
- **ﮔﺍﮔ؟ﻟﺛ؛ﮔ۱**: ﮒ؟ﻝﺍﮔﺍﮔ؟ﮔ ﺙﮒﺙﻟﺛ؛ﮔ۱
- **ﻝﭨﮔﻝﭨﻛﺕ**: ﻝﭨﻛﺕﮒﮔﭖﻝﭨﮔﮔ ﺙﮒﺙ
- **ﮔ۶ﻟﺛﻛﺙﮒ**: ﻛﺙﮒﮒﮔﭖﮔ۶ﻟﺛ
- **ﮔ۴ﮒﻝﮔ**: ﻟ۹ﮒ۷ﻝﮔﮒﮔﭖﮔ۴ﮒ

### ﮒﻟﻟﮒ?

- [ﻛﺕﻛﺕﻠﮒﻝﺏﭨﻝﭨﮒ؟ﮔﺛﻟﮒﺝ](01_FRAMEWORK/PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md)

---

## ﻭﺅﺕ?ﮔﭘﮔﻟ؟ﺝﻟ؟۰

### ﮔ۷۰ﮒﻝﭨﮔ

```
src/backtest/
ﻗﻗﻗ __init__.py                 # ﮔ۷۰ﮒﮒﮒ۶ﮒ?
ﻗﻗﻗ adapter.py                  # BacktestingPyAdapterﻠﻠﮒ?
ﻗﻗﻗ strategy_wrapper.py         # ﻝ­ﻝ۴ﮒﻟ۲ﮒ?
ﻗﻗﻗ data_converter.py           # ﮔﺍﮔ؟ﻟﺛ؛ﮔ۱ﮒ?
ﻗﻗﻗ result_formatter.py         # ﻝﭨﮔﮔ ﺙﮒﺙﮒﮒ۷
ﻗﻗﻗ report_generator.py         # ﮔ۴ﮒﻝﮔﮒ?
ﻗﻗﻗ exceptions.py               # ﻟ۹ﮒ؟ﻛﺗﮒﺙﮒﺕ?
ﻗﻗﻗ tests/                      # ﮒﮒﮔﭖﻟﺁ
    ﻗﻗﻗ test_adapter.py
    ﻗﻗﻗ test_strategy_wrapper.py
    ﻗﻗﻗ test_data_converter.py
    ﻗﻗﻗ test_result_formatter.py
```

### ﻝﺎﭨﻟ؟ﺝﻟ؟?

#### BacktestingPyAdapter - ﻠﻠﮒ?

```python
from typing import Dict, Any, Optional, List
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd

class BacktestingPyAdapter:
    """Backtesting.pyﻠﻠﮒ?- ﮒﺍﻝﺏﭨﻝﭨﻝ­ﻝ۴ﻠﻠﻛﺕﭦBacktesting.pyﮔ ﺙﮒﺙ"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.data_converter = DataConverter()
        self.result_formatter = ResultFormatter()
    
    def run_backtest(
        self,
        strategy,
        data: pd.DataFrame,
        cash: float = 100000,
        commission: float = 0.002,
        **kwargs
    ) -> Dict[str, Any]:
        """ﻟﺟﻟ۰ﮒﮔﭖ"""
        bt_strategy = StrategyWrapper.wrap(strategy)
        
        bt_data = self.data_converter.convert(data)
        
        bt = Backtest(
            bt_data,
            bt_strategy,
            cash=cash,
            commission=commission,
            **kwargs
        )
        
        stats = bt.run()
        
        result = self.result_formatter.format(stats)
        
        return result
    
    def optimize(
        self,
        strategy,
        data: pd.DataFrame,
        optimize_params: Dict[str, List[Any]],
        maximize: str = "Return [%]",
        **kwargs
    ) -> Dict[str, Any]:
        """ﻛﺙﮒﻝ­ﻝ۴ﮒﮔﺍ"""
        bt_strategy = StrategyWrapper.wrap(strategy)
        bt_data = self.data_converter.convert(data)
        
        bt = Backtest(
            bt_data,
            bt_strategy,
            **kwargs
        )
        
        stats = bt.optimize(**optimize_params, maximize=maximize)
        
        result = self.result_formatter.format(stats)
        
        return result
```

#### StrategyWrapper - ﻝ­ﻝ۴ﮒﻟ۲ﮒ?

```python
from backtesting import Strategy
from typing import Dict, Any

class StrategyWrapper(Strategy):
    """ﻝ­ﻝ۴ﮒﻟ۲ﮒ?- ﮒﺍﻝﺏﭨﻝﭨﻝ­ﻝ۴ﮒﻟ۲ﻛﺕﭦBacktesting.pyﮔ ﺙﮒﺙ"""
    
    system_strategy = None
    
    def init(self):
        """ﮒﮒ۶ﮒﻝ­ﻝ?""
        if self.system_strategy:
            self.system_strategy.initialize({
                "data": self.data,
                "broker": self.broker
            })
    
    def next(self):
        """ﮔﺁﻛﺕ۹barﻟﺍﻝ۷"""
        if self.system_strategy:
            bar_data = {
                "open": self.data.Open[-1],
                "high": self.data.High[-1],
                "low": self.data.Low[-1],
                "close": self.data.Close[-1],
                "volume": self.data.Volume[-1]
            }
            
            signal = self.system_strategy.on_bar(bar_data)
            
            if signal:
                self._execute_signal(signal)
    
    def _execute_signal(self, signal: Dict[str, Any]):
        """ﮔ۶ﻟ۰ﻛﺟ۰ﮒﺓ"""
        action = signal.get("action")
        size = signal.get("size", 1)
        
        if action == "buy":
            self.buy(size=size)
        elif action == "sell":
            self.sell(size=size)
        elif action == "close":
            self.position.close()
    
    @classmethod
    def wrap(cls, system_strategy):
        """ﮒﻟ۲ﻝﺏﭨﻝﭨﻝ­ﻝ۴"""
        class WrappedStrategy(cls):
            pass
        
        WrappedStrategy.system_strategy = system_strategy
        
        return WrappedStrategy
```

#### DataConverter - ﮔﺍﮔ؟ﻟﺛ؛ﮔ۱ﮒ?

```python
import pandas as pd
from typing import Dict, Any

class DataConverter:
    """ﮔﺍﮔ؟ﻟﺛ؛ﮔ۱ﮒ?- ﮒﺍﻝﺏﭨﻝﭨﮔﺍﮔ؟ﮔ ﺙﮒﺙﻟﺛ؛ﮔ۱ﻛﺕﭦBacktesting.pyﮔ ﺙﮒﺙ"""
    
    def convert(self, data: pd.DataFrame) -> pd.DataFrame:
        """ﻟﺛ؛ﮔ۱ﮔﺍﮔ؟ﮔ ﺙﮒﺙ"""
        bt_data = data.copy()
        
        column_mapping = {
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume"
        }
        
        bt_data = bt_data.rename(columns=column_mapping)
        
        required_columns = ["Open", "High", "Low", "Close", "Volume"]
        for col in required_columns:
            if col not in bt_data.columns:
                raise ValueError(f"Missing required column: {col}")
        
        return bt_data
    
    def convert_from_bt(self, bt_data: pd.DataFrame) -> pd.DataFrame:
        """ﻛﭨBacktesting.pyﮔ ﺙﮒﺙﻟﺛ؛ﮔ۱ﮒﻝﺏﭨﻝﭨﮔ ﺙﮒﺙ?""
        system_data = bt_data.copy()
        
        column_mapping = {
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        }
        
        system_data = system_data.rename(columns=column_mapping)
        
        return system_data
```

#### ResultFormatter - ﻝﭨﮔﮔ ﺙﮒﺙﮒﮒ۷

```python
from typing import Dict, Any
import pandas as pd

class ResultFormatter:
    """ﻝﭨﮔﮔ ﺙﮒﺙﮒﮒ۷ - ﻝﭨﻛﺕﮒﮔﭖﻝﭨﮔﮔ ﺙﮒﺙ"""
    
    def format(self, stats) -> Dict[str, Any]:
        """ﮔ ﺙﮒﺙﮒﮒﮔﭖﻝﭨﮔ?""
        return {
            "performance": self._format_performance(stats),
            "trades": self._format_trades(stats),
            "equity_curve": self._format_equity_curve(stats),
            "drawdown": self._format_drawdown(stats),
            "metrics": self._format_metrics(stats)
        }
    
    def _format_performance(self, stats) -> Dict[str, Any]:
        """ﮔ ﺙﮒﺙﮒﻝﭨ۸ﮔﮔﮔ ?""
        return {
            "total_return": stats["Return [%]"],
            "annual_return": stats["Return (Ann.) [%]"],
            "sharpe_ratio": stats["Sharpe Ratio"],
            "sortino_ratio": stats["Sortino Ratio"],
            "max_drawdown": stats["Max. Drawdown [%]"],
            "win_rate": stats["Win Rate [%]"],
            "profit_factor": stats["Profit Factor"]
        }
    
    def _format_trades(self, stats) -> List[Dict[str, Any]]:
        """ﮔ ﺙﮒﺙﮒﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ?""
        trades = []
        
        if hasattr(stats, "_trades"):
            for trade in stats._trades:
                trades.append({
                    "entry_time": trade.EntryTime,
                    "exit_time": trade.ExitTime,
                    "entry_price": trade.EntryPrice,
                    "exit_price": trade.ExitPrice,
                    "size": trade.Size,
                    "pnl": trade.PnL,
                    "return_pct": trade.ReturnPct
                })
        
        return trades
    
    def _format_equity_curve(self, stats) -> pd.Series:
        """ﮔ ﺙﮒﺙﮒﮔﻝﮔﺎﻝﭦ?""
        if hasattr(stats, "_equity_curve"):
            return stats._equity_curve
        return pd.Series()
    
    def _format_drawdown(self, stats) -> pd.Series:
        """ﮔ ﺙﮒﺙﮒﮒﮔ۳ﮔﺎﻝﭦ?""
        if hasattr(stats, "_drawdown"):
            return stats._drawdown
        return pd.Series()
    
    def _format_metrics(self, stats) -> Dict[str, Any]:
        """ﮔ ﺙﮒﺙﮒﮒﭘﻛﭨﮔﮔ ?""
        return {
            "start_date": stats["Start"],
            "end_date": stats["End"],
            "duration": stats["Duration"],
            "exposure_time": stats["Exposure Time [%]"],
            "trades_count": stats["# Trades"],
            "avg_trade_duration": stats["Avg. Trade Duration"]
        }
```

---

## ﻭ ﮒ؟ﮔﺛﮔ­۴ﻠ۹۳

### Step 1: ﮒ؟ﻟ۲ﻛﺝﻟﭖﺅﺙ?0ﮒﻠﺅﺙ?

```bash
# ﮒ؟ﻟ۲Backtesting.py
pip install backtesting

# ﮒ؟ﻟ۲ﮒﭘﻛﭨﻛﺝﻟﭖ
pip install pandas numpy matplotlib
```

### Step 2: ﮒ؟ﻝﺍDataConverterﺅﺙ?ﮒﺍﮔﭘﺅﺙ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒ؟ﻝﺍﮔﺍﮔ؟ﮔ ﺙﮒﺙﻟﺛ؛ﮔ۱
- [ ] ﮒ۳ﻝﻝﺙﭦﮒ۳ﺎﮔﺍﮔ؟
- [ ] ﻝﺙﮒﮒﮒﮔﭖﻟﺁ

**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﻗ?ﮔﺍﮔ؟ﮔ ﺙﮒﺙﻟﺛ؛ﮔ۱ﮔ­۲ﻝ۰؟
- ﻗ?ﻝﺙﭦﮒ۳ﺎﮔﺍﮔ؟ﮒ۳ﻝﮒ؟ﮒ
- ﻗ?ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?> 90%

### Step 3: ﮒ؟ﻝﺍStrategyWrapperﺅﺙ?ﮒﺍﮔﭘﺅﺙ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒ؟ﻝﺍﻝ­ﻝ۴ﮒﻟ۲
- [ ] ﮒ؟ﻝﺍﻛﺟ۰ﮒﺓﮔ۶ﻟ۰
- [ ] ﮒ۳ﻝﻝ­ﻝ۴ﻝﭘﮔ?
- [ ] ﻝﺙﮒﮒﮒﮔﭖﻟﺁ

**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﻗ?ﻝ­ﻝ۴ﮒﻟ۲ﮔ­۲ﻝ۰؟
- ﻗ?ﻛﺟ۰ﮒﺓﮔ۶ﻟ۰ﮔ­۲ﻝ۰؟
- ﻗ?ﻝﭘﮔﻝ؟۰ﻝﮒ؟ﮒ?
- ﻗ?ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?> 90%

### Step 4: ﮒ؟ﻝﺍResultFormatterﺅﺙ?ﮒﺍﮔﭘﺅﺙ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒ؟ﻝﺍﻝﭨﮔﮔ ﺙﮒﺙﮒ?
- [ ] ﮒ؟ﻝﺍﮔﮔ ﻟ؟۰ﻝ؟
- [ ] ﻝﺙﮒﮒﮒﮔﭖﻟﺁ

**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﻗ?ﻝﭨﮔﮔ ﺙﮒﺙﻝﭨﻛﺕ
- ﻗ?ﮔﮔ ﻟ؟۰ﻝ؟ﮔ­۲ﻝ۰؟
- ﻗ?ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?> 90%

### Step 5: ﮒ؟ﻝﺍBacktestingPyAdapterﺅﺙ?ﮒﺍﮔﭘﺅﺙ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒ؟ﻝﺍﮒﮔﭖﻟﺟﻟ۰
- [ ] ﮒ؟ﻝﺍﮒﮔﺍﻛﺙﮒ
- [ ] ﻝﺙﮒﮒﮒﮔﭖﻟﺁ

**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﻗ?ﮒﮔﭖﻟﺟﻟ۰ﮔ­۲ﻝ۰؟
- ﻗ?ﮒﮔﺍﻛﺙﮒﮔ­۲ﻝ۰؟
- ﻗ?ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?> 90%

### Step 6: ﻠﮔﮔﭖﻟﺁﺅﺙ?.5ﮒﺍﮔﭘﺅﺙ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒﮒﭨﭦﮔﭖﻟﺁﻝ­ﻝ۴
- [ ] ﮔﭖﻟﺁﮒ؟ﮔﺑﮔﭖﻝ۷
- [ ] ﮔ۶ﻟﺛﮔﭖﻟﺁ
- [ ] ﮔﮔ۰۲ﻝﺙﮒ

**ﻠ۹ﮔﭘﮔ ﮒ**:
- ﻗ?ﮒ؟ﮔﺑﮔﭖﻝ۷ﮒﺁﮔ­۲ﮒﺕﺕﻟﺟﻟ۰?
- ﻗ?ﮔ۶ﻟﺛﮔﮔ ﻟﺝﺝﮔ 
- ﻗ?ﮔﮔ۰۲ﮒ؟ﮔﺑ

---

## ﻗ?ﻠ۹ﮔﭘﮔ ﮒ

### ﮒﻟﺛﻠ۹ﮔﭘ

| ﮒﻟﺛ | ﻠ۹ﮔﭘﮔ ﮒ | ﮔﭖﻟﺁﮔﺗﮔﺏ |
|------|---------|---------|
| **ﻝ­ﻝ۴ﻠﻠ** | ﻝ­ﻝ۴ﮒﺁﮔ­۲ﻝ۰؟ﻠﻠ | ﻠﮔﮔﭖﻟﺁ |
| **ﮔﺍﮔ؟ﻟﺛ؛ﮔ۱** | ﮔﺍﮔ؟ﮔ ﺙﮒﺙﻟﺛ؛ﮔ۱ﮔ­۲ﻝ۰؟ | ﮒﮒﮔﭖﻟﺁ |
| **ﻝﭨﮔﻝﭨﻛﺕ** | ﻝﭨﮔﮔ ﺙﮒﺙﻝﭨﻛﺕ | ﮒﮒﮔﭖﻟﺁ |
| **ﮒﮔﺍﻛﺙﮒ** | ﮒﮔﺍﻛﺙﮒﮔ­۲ﻝ۰؟ | ﻠﮔﮔﭖﻟﺁ |
| **ﮔ۴ﮒﻝﮔ** | ﮔ۴ﮒﮒﺁﮔ­۲ﻝ۰؟ﻝﮔ?| ﻠﮔﮔﭖﻟﺁ |

### ﮔ۶ﻟﺛﻠ۹ﮔﭘ

| ﮔﮔ  | ﻝ؟ﮔ ﮒ?| ﮔﭖﻟﺁﮔﺗﮔﺏ |
|------|--------|---------|
| **ﮒﮔﭖﻠﮒﭦ۵** | > 1000 bars/s | ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| **ﮒﮒ­ﮒ ﻝ۷** | < 500MB | ﮒﮒ­ﮒﮔ |
| **ﮔ۴ﮒﻝﮔﮔﭘﻠﺑ** | < 5s | ﮔ۶ﻟﺛﮔﭖﻟﺁ |

### ﻟﺑ۷ﻠﻠ۹ﮔﭘ

| ﮔﮔ  | ﻝ؟ﮔ ﮒ?| ﮔﭖﻟﺁﮔﺗﮔﺏ |
|------|--------|---------|
| **ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?* | > 90% | pytest --cov |
| **ﻛﭨ۲ﻝ ﮒ۳ﮔﮒﭦ?* | < 10 | radon cc |
| **ﻛﭨ۲ﻝ ﻠﮒ۳ﻝ?* | < 5% | pylint |
| **ﮔﮔ۰۲ﮒ؟ﮔﺑﮔ?* | 100% | ﮔﮔ۰۲ﮒ؟۰ﮔ۴ |

---

## ﻭ۶۹ ﮔﭖﻟﺁﻝ­ﻝ۴

### ﮒﮒﮔﭖﻟﺁ

```python
# tests/test_adapter.py
import pytest
import pandas as pd
from backtest.adapter import BacktestingPyAdapter
from backtest.data_converter import DataConverter

class TestBacktestingPyAdapter:
    
    def test_data_converter(self):
        converter = DataConverter()
        
        data = pd.DataFrame({
            "open": [100, 101, 102],
            "high": [105, 106, 107],
            "low": [95, 96, 97],
            "close": [102, 103, 104],
            "volume": [1000, 1100, 1200]
        })
        
        bt_data = converter.convert(data)
        
        assert "Open" in bt_data.columns
        assert "High" in bt_data.columns
        assert "Low" in bt_data.columns
        assert "Close" in bt_data.columns
        assert "Volume" in bt_data.columns
```

### ﻠﮔﮔﭖﻟﺁ

```python
# tests/test_integration.py
import pytest
import pandas as pd
from backtest.adapter import BacktestingPyAdapter
from strategy.base import BaseStrategy

class TestStrategy(BaseStrategy):
    def initialize(self, context):
        pass
    
    def on_bar(self, bar):
        if bar["close"] > bar["open"]:
            return {"action": "buy", "size": 1}
        return None

class TestBacktestIntegration:
    
    def test_full_backtest(self):
        adapter = BacktestingPyAdapter()
        strategy = TestStrategy("test_strategy")
        
        data = pd.DataFrame({
            "open": [100, 101, 102, 103, 104],
            "high": [105, 106, 107, 108, 109],
            "low": [95, 96, 97, 98, 99],
            "close": [102, 103, 104, 105, 106],
            "volume": [1000, 1100, 1200, 1300, 1400]
        })
        
        result = adapter.run_backtest(strategy, data)
        
        assert "performance" in result
        assert "trades" in result
        assert "equity_curve" in result
```

---

## ﻭ ﮔ۶ﻟﺛﻛﺙﮒ

### ﮔﺍﮔ؟ﻝﺙﮒ­

```python
class DataConverter:
    
    def __init__(self):
        self._cache = {}
    
    def convert(self, data: pd.DataFrame) -> pd.DataFrame:
        cache_key = hash(data.values.tobytes())
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        bt_data = self._convert_impl(data)
        self._cache[cache_key] = bt_data
        
        return bt_data
```

### ﮒﺗﭘﻟ۰ﮒﮔﭖ

```python
from concurrent.futures import ProcessPoolExecutor

class BacktestingPyAdapter:
    
    def run_parallel_backtests(
        self,
        strategies: List,
        data: pd.DataFrame,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """ﮒﺗﭘﻟ۰ﻟﺟﻟ۰ﮒ۳ﻛﺕ۹ﮒﮔﭖ"""
        with ProcessPoolExecutor() as executor:
            futures = [
                executor.submit(self.run_backtest, strategy, data, **kwargs)
                for strategy in strategies
            ]
            
            results = [future.result() for future in futures]
        
        return results
```

---

## ﻭ۷ ﮒﺕﺕﻟ۶ﻠ؟ﻠ۱

### Q1: ﮔﺍﮔ؟ﮔ ﺙﮒﺙﻛﺕﮒﺗﻠ?

**ﻠ؟ﻠ۱**: ValueError: Missing required column: Open

**ﻟ۶۲ﮒﺏﮔﺗﮔ۰**:
```python
# ﻝ۰؟ﻛﺟﮔﺍﮔ؟ﮒﮒﮔ­۲ﻝ۰؟
data = data.rename(columns={
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close",
    "volume": "Volume"
})
```

### Q2: ﻝ­ﻝ۴ﮒﮒ۶ﮒﮒ۳ﺎﻟﺑ?

**ﻠ؟ﻠ۱**: AttributeError: 'NoneType' object has no attribute 'initialize'

**ﻟ۶۲ﮒﺏﮔﺗﮔ۰**:
```python
# ﻝ۰؟ﻛﺟﻝ­ﻝ۴ﮔ­۲ﻝ۰؟ﮒﻟ۲
class WrappedStrategy(StrategyWrapper):
    system_strategy = your_strategy
```

### Q3: ﮒﮒ­ﮒ ﻝ۷ﻟﺟﻠ،

**ﻠ؟ﻠ۱**: MemoryError: Unable to allocate array

**ﻟ۶۲ﮒﺏﮔﺗﮔ۰**:
```python
# ﮒﮔﺗﮒ۳ﻝﮔﺍﮔ؟
def run_backtest_in_batches(self, data, batch_size=10000):
    results = []
    
    for i in range(0, len(data), batch_size):
        batch = data.iloc[i:i+batch_size]
        result = self.run_backtest(batch)
        results.append(result)
    
    return results
```

---

## ﻭ ﮒﻟﻟﭖﮔ?

### ﮒﻠ۷ﮔﮔ۰۲

- [ﻛﺕﻛﺕﻠﮒﻝﺏﭨﻝﭨﮒ؟ﮔﺛﻟﮒﺝ](01_FRAMEWORK/PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md)

### ﮒ۳ﻠ۷ﻟﭖﮔﭦ

- [Backtesting.pyﮒ؟ﮔﺗﮔﮔ۰۲](https://kernc.github.io/backtesting.py/)
- [Backtesting.py GitHub](https://github.com/kernc/backtesting.py)
- [ﻠﮒﮒﮔﭖﮔﻛﺛﺏﮒ؟ﻟﺓﭖ](https://www.quantstart.com/articles/Quantitative-Trading-Research-Platform)

---

## ﻭ ﮔﺑﮔﺍﻟ؟ﺍﮒﺛ

| ﮔ۴ﮔ | ﻝﮔ؛ | ﮔﺑﮔﺍﮒﮒ؟ﺗ | ﮔﺑﮔﺍﻛﭦ?|
|------|------|---------|--------|
| 2026-04-02 | v1.0 | ﮒﮒﭨﭦﮒﮔﭖﮒﺙﮔﮒ؟ﮔﺛﮔﮒ | ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ?|

---

## ﻭ ﻟﻝﺏﭨﮔﺗﮒﺙ

**ﮔﮔ۰۲ﻝﭨﺑﮔ۳ﻟ?*: ﻠ۵ﮒﺕ­ﮔﭘﮔﮒﺕ? 
**ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02  
**ﮔﮒﮔﺑﮔ?*: 2026-04-02  
**ﻝﮔ؛**: v1.0
