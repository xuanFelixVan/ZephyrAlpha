---
module_id: TACTICS_ARCH_INTERFACE_STD_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: '2026-04-07'
owner: 首席文档架构?
standard_type: 专业量化机构标准
applicable_scope: 全系统标准规范
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
responsibility:
- 市场状态识别 (Layer 4)
---
# 策略接口标准
> **核心职责**: 标准规范制定
> **职责边界**: 
> - ✅ 本文档负责：标准规范制定相关内容
> - ❌ 本文档不负责：其他模块内容


> 策略基类与接口定?
>
> **配套文档**?
> - 主文档：[../../INDEX.md](../INDEX.md)
> - 策略池概述：../05_STRATEGY_POOL/index.md

***

## 1. 策略基类定义

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, List
from enum import Enum

class MarketState(Enum):
    """市场状态枚?""
    BULL = "牛市"
    BEAR = "熊市"
    VOLATILE = "震荡?
    YAO = "妖股周期"
    CHAOS = "混沌状?

class SignalType(Enum):
    """信号类型枚举"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

@dataclass
class TradingSignal:
    """交易信号数据结构"""
    code: str                          # 股票代码
    signal: SignalType                  # 信号类型
    confidence: float                   # 置信?(0.0-1.0)
    entry_price: float                 # 建议入场?
    stop_loss: float                   # 止损?
    target_price: float               # 目标?
    strategy_name: str                 # 策略名称
    position_size: float = 0.0        # 仓位建议
    holding_period: int = 5           # 持有天数建议
    notes: str = ""                   # 备注

@dataclass
class StrategyPerformance:
    """策略绩效数据结构"""
    win_rate: float                    # 胜率
    avg_return: float                  # 平均收益?
    max_drawdown: float               # 最大回?
    sharpe_ratio: float              # 夏普比率
    total_trades: int                # 总交易次?
    avg_holding_days: float           # 平均持有天数

class BaseStrategy(ABC):
    """策略基类"""

    def __init__(self, name: str, strategy_id: str):
        self.name = name
        self.strategy_id = strategy_id
        self.market_states: List[MarketState] = []
        self.parameters: Dict = {}
        self.performance: Optional[StrategyPerformance] = None

    @abstractmethod
    def generate_signal(self,
                       market_data: pd.DataFrame,
                       stock_data: pd.DataFrame,
                       market_state: MarketState) -> Optional[TradingSignal]:
        """
        生成交易信号

        参数:
            market_data: 市场数据（大盘指数等?
            stock_data: 个股数据
            market_state: 当前市场状?

        返回:
            TradingSignal: 交易信号，无信号时返回None
        """
        pass

    def get_applicable_states(self) -> List[MarketState]:
        """获取策略适用的市场状?""
        return self.market_states

    def get_performance(self) -> StrategyPerformance:
        """获取策略绩效"""
        if self.performance is None:
            return StrategyPerformance(0, 0, 0, 0, 0, 0)
        return self.performance

    def update_parameters(self, new_params: Dict):
        """更新策略参数"""
        self.parameters.update(new_params)
```

***

## 2. 策略注册装饰?

```python
from functools import wraps

_strategies_registry = {}

def register_strategy(strategy_class):
    """策略注册装饰?""
    @wraps(strategy_class)
    def wrapper(*args, **kwargs):
        return strategy_class(*args, **kwargs)

    instance = strategy_class(*args, **kwargs)
    _strategies_registry[instance.strategy_id] = instance
    return wrapper

def get_strategy(strategy_id: str) -> Optional[BaseStrategy]:
    """获取注册策略"""
    return _strategies_registry.get(strategy_id)

def list_all_strategies() -> Dict[str, BaseStrategy]:
    """列出所有注册策?""
    return _strategies_registry.copy()
```

***

## 3. 策略实现示例

```python
@register_strategy
class MaTrendStrategy(BaseStrategy):
    """均线趋势策略"""

    def __init__(self):
        super().__init__(
            name="均线趋势策略",
            strategy_id="T001"
        )
        self.market_states = [MarketState.BULL, MarketState.VOLATILE]
        self.parameters = {
            'ma_short': 5,
            'ma_medium': 20,
            'ma_long': 60,
            'min_volume_ratio': 1.5
        }

    def generate_signal(self,
                       market_data: pd.DataFrame,
                       stock_data: pd.DataFrame,
                       market_state: MarketState) -> Optional[TradingSignal]:
        """
        均线趋势策略信号生成
        条件: MA5 > MA20 > MA60 ?成交量放?
        """
        if market_state not in self.market_states:
            return None

        params = self.parameters
        ma5 = stock_data[f'ma_{params["ma_short"]}']
        ma20 = stock_data[f'ma_{params["ma_medium"]}']
        ma60 = stock_data[f'ma_{params["ma_long"]}']
        volume_ratio = stock_data['volume'] / stock_data['ma_volume_20']

        # 多头排列条件
        if ma5 > ma20 > ma60:
            # 成交量放大确?
            if volume_ratio > params['min_volume_ratio']:
                current_price = stock_data['close']
                stop_loss = ma20 * 0.97
                target = current_price * 1.1

                return TradingSignal(
                    code=stock_data['code'],
                    signal=SignalType.BUY,
                    confidence=0.75,
                    entry_price=current_price,
                    stop_loss=stop_loss,
                    target_price=target,
                    strategy_name=self.name,
                    position_size=0.15,
                    holding_period=10
                )

        return None
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 初始版本 |
