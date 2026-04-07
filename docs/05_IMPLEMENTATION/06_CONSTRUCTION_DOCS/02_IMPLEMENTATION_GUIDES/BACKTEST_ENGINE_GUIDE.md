---
module_id: BACKTEST_ENGINE_GUIDE
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - BACKTEST_ENGINE操作指南
---

﻿---
module_id: BACKTEST_ENGINE_GUIDE_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕﮔﭘﮔﮒﺕ?
responsibility:
  - 操作指南编写与使用说明与系统维护管理
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮒ؟ﮔﺛﮔﮒ
applicable_scope: ﮒﮔﭖﮒﺙﮔﮔ۷۰ﮒﮒ؟ﮔﺛ
compliance_level: ﻛﺕﻛﺕﮔﮒ
parent_document: ../README.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?---


# ﮒﮔﭖﮒﺙﮔﮒ؟ﮔﺛﮔﮒ

## 核心定位

提供回测引擎的使用指南，包含配置方法、运行流程、结果分析等，支持策略回测验证。


> **核心职责**: 使用指南和教程
> **职责边界**: 
> - ✅ 本文档负责：使用指南和教程相关内容
> - ❌ 本文档不负责：其他模块内容


> **ﻝﮔ؛**: v1.0
> **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02
> **ﻟﻟﺑ۲**: ﮔﮒﺁﺙBacktesting.pyﮒﮔﭖﮒﺙﮔﻝﻠﮔﮒﻠﻠ
> **ﮒ؟ﮔﺛﮒ۷ﮔ**: 2ﮒ۷ﺅﺙWeek 3-4ﺅﺙ?
> **ﻛﺙﮒﻝﭦ?*: P0

---


## 设计目标

### 主要目标

1. **功能完整性**: 确保文档内容完整，满足使用需求
2. **易用性**: 提高文档可读性，便于快速理解
3. **可维护性**: 文档结构清晰，便于后续维护
4. **一致性**: 确保文档格式和风格统一

### 质量目标

- 文档完整性: 100%
- 格式规范性: 100%
- 内容准确性: 100%


## ﻭ ﮒ؟ﮔﺛﮔ۵ﻟ۶

### ﻝ؟ﮔ

ﻠﮔBacktesting.pyﮒﺙﮔﭦﮒﮔﭖﮒﺙﮔﺅﺙﮒ؟ﻝﺍﻛﺕﻝﺏﭨﻝﭨﻝﻝ۴ﮔ۰ﮔﭘﻝﮔﻝﺙﮒﺁﺗﮔ۴ﻙ?

### ﮔﺕﮒﺟﮒﻟﺛ

- **ﻝﻝ۴ﻠﻠ**: ﮒﺍﻝﺏﭨﻝﭨﻝﻝ۴ﻠﻠﻛﺕﭦBacktesting.pyﮔﺙﮒﺙ
- **ﮔﺍﮔ؟ﻟﺛ؛ﮔ۱**: ﮒ؟ﻝﺍﮔﺍﮔ؟ﮔﺙﮒﺙﻟﺛ؛ﮔ۱
- **ﻝﭨﮔﻝﭨﻛﺕ**: ﻝﭨﻛﺕﮒﮔﭖﻝﭨﮔﮔﺙﮒﺙ
- **ﮔ۶ﻟﺛﻛﺙﮒ**: ﻛﺙﮒﮒﮔﭖﮔ۶ﻟﺛ
- **ﮔ۴ﮒﻝﮔ**: ﻟ۹ﮒ۷ﻝﮔﮒﮔﭖﮔ۴ﮒ

### ﮒﻟﻟﮒ?

- ﻛﺕﻛﺕﻠﮒﻝﺏﭨﻝﭨﮒ؟ﮔﺛﻟﮒﺝ

---

## ﻭﺅﺕ?ﮔﭘﮔﻟ؟ﺝﻟ؟۰

### ﮔ۷۰ﮒﻝﭨﮔ

```
src/backtest/
ﻗﻗﻗ __init__.py                 # ﮔ۷۰ﮒﮒﮒ۶ﮒ?
ﻗﻗﻗ adapter.py                  # BacktestingPyAdapterﻠﻠﮒ?
ﻗﻗﻗ strategy_wrapper.py         # ﻝﻝ۴ﮒﻟ۲ﮒ?
ﻗﻗﻗ data_converter.py           # ﮔﺍﮔ؟ﻟﺛ؛ﮔ۱ﮒ?
ﻗﻗﻗ result_formatter.py         # ﻝﭨﮔﮔﺙﮒﺙﮒﮒ۷
ﻗﻗﻗ report_generator.py         # ﮔ۴ﮒﻝﮔﮒ?
ﻗﻗﻗ exceptions.py               # ﻟ۹ﮒ؟ﻛﺗﮒﺙﮒﺕ?
ﻗﻗﻗ tests/                      # ﮒﮒﮔﭖﻟﺁ
    ﻗﻗﻗ test_adapter.py
    ﻗﻗﻗ test_strategy_wrapper.py
    ﻗﻗﻗ test_data_converter.py
    ﻗﻗﻗ test_result_formatter.py
```

### ﻝﺎﭨﻟ؟ﺝﻟ؟?

#### BacktestingPyAdapter - ﻠﻠﮒ?

```python
from typing import Dict, Any, Optional, List
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd

class BacktestingPyAdapter:
"""Backtesting.pyﻠﻠﮒ?- ﮒﺍﻝﺏﭨﻝﭨﻝﻝ۴ﻠﻠﻛﺕﭦBacktesting.pyﮔﺙﮒﺙ"""
    
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
        """ﻟﺟﻟ۰ﮒﮔﭖ"""
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
"""ﻛﺙﮒﻝﻝ۴ﮒﮔﺍ"""
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

#### StrategyWrapper - ﻝﻝ۴ﮒﻟ۲ﮒ?

```python
from backtesting import Strategy
from typing import Dict, Any

class StrategyWrapper(Strategy):
"""ﻝﻝ۴ﮒﻟ۲ﮒ?- ﮒﺍﻝﺏﭨﻝﭨﻝﻝ۴ﮒﻟ۲ﻛﺕﭦBacktesting.pyﮔﺙﮒﺙ"""
    
    system_strategy = None
    
    def init(self):
"""ﮒﮒ۶ﮒﻝﻝ?""
        if self.system_strategy:
            self.system_strategy.initialize({
                "data": self.data,
                "broker": self.broker
            })
    
    def next(self):
        """ﮔﺁﻛﺕ۹barﻟﺍﻝ۷"""
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
        """ﮔ۶ﻟ۰ﻛﺟ۰ﮒﺓ"""
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
"""ﮒﻟ۲ﻝﺏﭨﻝﭨﻝﻝ۴"""
        class WrappedStrategy(cls):
            pass
        
        WrappedStrategy.system_strategy = system_strategy
        
        return WrappedStrategy
```

#### DataConverter - ﮔﺍﮔ؟ﻟﺛ؛ﮔ۱ﮒ?

```python
import pandas as pd
from typing import Dict, Any

class DataConverter:
"""ﮔﺍﮔ؟ﻟﺛ؛ﮔ۱ﮒ?- ﮒﺍﻝﺏﭨﻝﭨﮔﺍﮔ؟ﮔﺙﮒﺙﻟﺛ؛ﮔ۱ﻛﺕﭦBacktesting.pyﮔﺙﮒﺙ"""
    
    def convert(self, data: pd.DataFrame) -> pd.DataFrame:
"""ﻟﺛ؛ﮔ۱ﮔﺍﮔ؟ﮔﺙﮒﺙ"""
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
"""ﻛﭨBacktesting.pyﮔﺙﮒﺙﻟﺛ؛ﮔ۱ﮒﻝﺏﭨﻝﭨﮔﺙﮒﺙ?""
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

#### ResultFormatter - ﻝﭨﮔﮔﺙﮒﺙﮒﮒ۷

```python
from typing import Dict, Any
import pandas as pd

class ResultFormatter:
"""ﻝﭨﮔﮔﺙﮒﺙﮒﮒ۷ - ﻝﭨﻛﺕﮒﮔﭖﻝﭨﮔﮔﺙﮒﺙ"""
    
    def format(self, stats) -> Dict[str, Any]:
"""ﮔﺙﮒﺙﮒﮒﮔﭖﻝﭨﮔ?""
        return {
            "performance": self._format_performance(stats),
            "trades": self._format_trades(stats),
            "equity_curve": self._format_equity_curve(stats),
            "drawdown": self._format_drawdown(stats),
            "metrics": self._format_metrics(stats)
        }
    
    def _format_performance(self, stats) -> Dict[str, Any]:
"""ﮔﺙﮒﺙﮒﻝﭨ۸ﮔﮔﮔ?""
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
"""ﮔﺙﮒﺙﮒﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ?""
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
"""ﮔﺙﮒﺙﮒﮔﻝﮔﺎﻝﭦ?""
        if hasattr(stats, "_equity_curve"):
            return stats._equity_curve
        return pd.Series()
    
    def _format_drawdown(self, stats) -> pd.Series:
"""ﮔﺙﮒﺙﮒﮒﮔ۳ﮔﺎﻝﭦ?""
        if hasattr(stats, "_drawdown"):
            return stats._drawdown
        return pd.Series()
    
    def _format_metrics(self, stats) -> Dict[str, Any]:
"""ﮔﺙﮒﺙﮒﮒﭘﻛﭨﮔﮔ?""
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

## ﻭ ﮒ؟ﮔﺛﮔ۴ﻠ۹۳

### Step 1: ﮒ؟ﻟ۲ﻛﺝﻟﭖﺅﺙ?0ﮒﻠﺅﺙ?

```bash
# ﮒ؟ﻟ۲Backtesting.py
pip install backtesting

# ﮒ؟ﻟ۲ﮒﭘﻛﭨﻛﺝﻟﭖ
pip install pandas numpy matplotlib
```

### Step 2: ﮒ؟ﻝﺍDataConverterﺅﺙ?ﮒﺍﮔﭘﺅﺙ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒ؟ﻝﺍﮔﺍﮔ؟ﮔﺙﮒﺙﻟﺛ؛ﮔ۱
- [ ] ﮒ۳ﻝﻝﺙﭦﮒ۳ﺎﮔﺍﮔ؟
- [ ] ﻝﺙﮒﮒﮒﮔﭖﻟﺁ

**ﻠ۹ﮔﭘﮔﮒ**:
- ﻗ?ﮔﺍﮔ؟ﮔﺙﮒﺙﻟﺛ؛ﮔ۱ﮔ۲ﻝ۰؟
- ﻗ?ﻝﺙﭦﮒ۳ﺎﮔﺍﮔ؟ﮒ۳ﻝﮒ؟ﮒ
- ﻗ?ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?> 90%

### Step 3: ﮒ؟ﻝﺍStrategyWrapperﺅﺙ?ﮒﺍﮔﭘﺅﺙ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒ؟ﻝﺍﻝﻝ۴ﮒﻟ۲
- [ ] ﮒ؟ﻝﺍﻛﺟ۰ﮒﺓﮔ۶ﻟ۰
- [ ] ﮒ۳ﻝﻝﻝ۴ﻝﭘﮔ?
- [ ] ﻝﺙﮒﮒﮒﮔﭖﻟﺁ

**ﻠ۹ﮔﭘﮔﮒ**:
- ﻗ?ﻝﻝ۴ﮒﻟ۲ﮔ۲ﻝ۰؟
- ﻗ?ﻛﺟ۰ﮒﺓﮔ۶ﻟ۰ﮔ۲ﻝ۰؟
- ﻗ?ﻝﭘﮔﻝ؟۰ﻝﮒ؟ﮒ?
- ﻗ?ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?> 90%

### Step 4: ﮒ؟ﻝﺍResultFormatterﺅﺙ?ﮒﺍﮔﭘﺅﺙ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒ؟ﻝﺍﻝﭨﮔﮔﺙﮒﺙﮒ?
- [ ] ﮒ؟ﻝﺍﮔﮔﻟ؟۰ﻝ؟
- [ ] ﻝﺙﮒﮒﮒﮔﭖﻟﺁ

**ﻠ۹ﮔﭘﮔﮒ**:
- ﻗ?ﻝﭨﮔﮔﺙﮒﺙﻝﭨﻛﺕ
- ﻗ?ﮔﮔﻟ؟۰ﻝ؟ﮔ۲ﻝ۰؟
- ﻗ?ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?> 90%

### Step 5: ﮒ؟ﻝﺍBacktestingPyAdapterﺅﺙ?ﮒﺍﮔﭘﺅﺙ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒ؟ﻝﺍﮒﮔﭖﻟﺟﻟ۰
- [ ] ﮒ؟ﻝﺍﮒﮔﺍﻛﺙﮒ
- [ ] ﻝﺙﮒﮒﮒﮔﭖﻟﺁ

**ﻠ۹ﮔﭘﮔﮒ**:
- ﻗ?ﮒﮔﭖﻟﺟﻟ۰ﮔ۲ﻝ۰؟
- ﻗ?ﮒﮔﺍﻛﺙﮒﮔ۲ﻝ۰؟
- ﻗ?ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?> 90%

### Step 6: ﻠﮔﮔﭖﻟﺁﺅﺙ?.5ﮒﺍﮔﭘﺅﺙ?

**ﻛﭨﭨﮒ۰ﮔﺕﮒ**:
- [ ] ﮒﮒﭨﭦﮔﭖﻟﺁﻝﻝ۴
- [ ] ﮔﭖﻟﺁﮒ؟ﮔﺑﮔﭖﻝ۷
- [ ] ﮔ۶ﻟﺛﮔﭖﻟﺁ
- [ ] ﮔﮔ۰۲ﻝﺙﮒ

**ﻠ۹ﮔﭘﮔﮒ**:
- ﻗ?ﮒ؟ﮔﺑﮔﭖﻝ۷ﮒﺁﮔ۲ﮒﺕﺕﻟﺟﻟ۰?
- ﻗ?ﮔ۶ﻟﺛﮔﮔﻟﺝﺝﮔ
- ﻗ?ﮔﮔ۰۲ﮒ؟ﮔﺑ

---

## ﻗ?ﻠ۹ﮔﭘﮔﮒ

### ﮒﻟﺛﻠ۹ﮔﭘ

| ﮒﻟﺛ | ﻠ۹ﮔﭘﮔﮒ | ﮔﭖﻟﺁﮔﺗﮔﺏ |
|------|---------|---------|
| **ﻝﻝ۴ﻠﻠ** | ﻝﻝ۴ﮒﺁﮔ۲ﻝ۰؟ﻠﻠ | ﻠﮔﮔﭖﻟﺁ |
| **ﮔﺍﮔ؟ﻟﺛ؛ﮔ۱** | ﮔﺍﮔ؟ﮔﺙﮒﺙﻟﺛ؛ﮔ۱ﮔ۲ﻝ۰؟ | ﮒﮒﮔﭖﻟﺁ |
| **ﻝﭨﮔﻝﭨﻛﺕ** | ﻝﭨﮔﮔﺙﮒﺙﻝﭨﻛﺕ | ﮒﮒﮔﭖﻟﺁ |
| **ﮒﮔﺍﻛﺙﮒ** | ﮒﮔﺍﻛﺙﮒﮔ۲ﻝ۰؟ | ﻠﮔﮔﭖﻟﺁ |
| **ﮔ۴ﮒﻝﮔ** | ﮔ۴ﮒﮒﺁﮔ۲ﻝ۰؟ﻝﮔ?| ﻠﮔﮔﭖﻟﺁ |

### ﮔ۶ﻟﺛﻠ۹ﮔﭘ

| ﮔﮔ | ﻝ؟ﮔﮒ?| ﮔﭖﻟﺁﮔﺗﮔﺏ |
|------|--------|---------|
| **ﮒﮔﭖﻠﮒﭦ۵** | > 1000 bars/s | ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| **ﮒﮒﮒﻝ۷** | < 500MB | ﮒﮒﮒﮔ |
| **ﮔ۴ﮒﻝﮔﮔﭘﻠﺑ** | < 5s | ﮔ۶ﻟﺛﮔﭖﻟﺁ |

### ﻟﺑ۷ﻠﻠ۹ﮔﭘ

| ﮔﮔ | ﻝ؟ﮔﮒ?| ﮔﭖﻟﺁﮔﺗﮔﺏ |
|------|--------|---------|
| **ﮒﮒﮔﭖﻟﺁﻟ۵ﻝﻝ?* | > 90% | pytest --cov |
| **ﻛﭨ۲ﻝﮒ۳ﮔﮒﭦ?* | < 10 | radon cc |
| **ﻛﭨ۲ﻝﻠﮒ۳ﻝ?* | < 5% | pylint |
| **ﮔﮔ۰۲ﮒ؟ﮔﺑﮔ?* | 100% | ﮔﮔ۰۲ﮒ؟۰ﮔ۴ |

---

## ﻭ۶۹ ﮔﭖﻟﺁﻝﻝ۴

### ﮒﮒﮔﭖﻟﺁ

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

### ﻠﮔﮔﭖﻟﺁ

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

## ﻭ ﮔ۶ﻟﺛﻛﺙﮒ

### ﮔﺍﮔ؟ﻝﺙﮒ

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

### ﮒﺗﭘﻟ۰ﮒﮔﭖ

```python
from concurrent.futures import ProcessPoolExecutor

class BacktestingPyAdapter:
    
    def run_parallel_backtests(
        self,
        strategies: List,
        data: pd.DataFrame,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """ﮒﺗﭘﻟ۰ﻟﺟﻟ۰ﮒ۳ﻛﺕ۹ﮒﮔﭖ"""
        with ProcessPoolExecutor() as executor:
            futures = [
                executor.submit(self.run_backtest, strategy, data, **kwargs)
                for strategy in strategies
            ]
            
            results = [future.result() for future in futures]
        
        return results
```

---

## ﻭ۷ ﮒﺕﺕﻟ۶ﻠ؟ﻠ۱

### Q1: ﮔﺍﮔ؟ﮔﺙﮒﺙﻛﺕﮒﺗﻠ?

**ﻠ؟ﻠ۱**: ValueError: Missing required column: Open

**ﻟ۶۲ﮒﺏﮔﺗﮔ۰**:
```python
# ﻝ۰؟ﻛﺟﮔﺍﮔ؟ﮒﮒﮔ۲ﻝ۰؟
data = data.rename(columns={
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close",
    "volume": "Volume"
})
```

### Q2: ﻝﻝ۴ﮒﮒ۶ﮒﮒ۳ﺎﻟﺑ?

**ﻠ؟ﻠ۱**: AttributeError: 'NoneType' object has no attribute 'initialize'

**ﻟ۶۲ﮒﺏﮔﺗﮔ۰**:
```python
# ﻝ۰؟ﻛﺟﻝﻝ۴ﮔ۲ﻝ۰؟ﮒﻟ۲
class WrappedStrategy(StrategyWrapper):
    system_strategy = your_strategy
```

### Q3: ﮒﮒﮒﻝ۷ﻟﺟﻠ،

**ﻠ؟ﻠ۱**: MemoryError: Unable to allocate array

**ﻟ۶۲ﮒﺏﮔﺗﮔ۰**:
```python
# ﮒﮔﺗﮒ۳ﻝﮔﺍﮔ؟
def run_backtest_in_batches(self, data, batch_size=10000):
    results = []
    
    for i in range(0, len(data), batch_size):
        batch = data.iloc[i:i+batch_size]
        result = self.run_backtest(batch)
        results.append(result)
    
    return results
```

---

## ﻭ ﮒﻟﻟﭖﮔ?

### ﮒﻠ۷ﮔﮔ۰۲

- ﻛﺕﻛﺕﻠﮒﻝﺏﭨﻝﭨﮒ؟ﮔﺛﻟﮒﺝ

### ﮒ۳ﻠ۷ﻟﭖﮔﭦ

- [Backtesting.pyﮒ؟ﮔﺗﮔﮔ۰۲](https://kernc.github.io/backtesting.py/)
- [Backtesting.py GitHub](https://github.com/kernc/backtesting.py)
- [ﻠﮒﮒﮔﭖﮔﻛﺛﺏﮒ؟ﻟﺓﭖ](https://www.quantstart.com/articles/Quantitative-Trading-Research-Platform)

---

## ﻭ ﮔﺑﮔﺍﻟ؟ﺍﮒﺛ

| ﮔ۴ﮔ | ﻝﮔ؛ | ﮔﺑﮔﺍﮒﮒ؟ﺗ | ﮔﺑﮔﺍﻛﭦ?|
|------|------|---------|--------|
| 2026-04-02 | v1.0 | ﮒﮒﭨﭦﮒﮔﭖﮒﺙﮔﮒ؟ﮔﺛﮔﮒ | ﻠ۵ﮒﺕﮔﭘﮔﮒﺕ?|

---

## ﻭ ﻟﻝﺏﭨﮔﺗﮒﺙ

**ﮔﮔ۰۲ﻝﭨﺑﮔ۳ﻟ?*: ﻠ۵ﮒﺕﮔﭘﮔﮒﺕ?
**ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02  
**ﮔﮒﮔﺑﮔ?*: 2026-04-02  
**ﻝﮔ؛**: v1.0
