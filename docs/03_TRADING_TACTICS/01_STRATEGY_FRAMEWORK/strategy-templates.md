---
module_id: 03_TRADING_TACTICS_01_STRATEGY_FRAMEWORK_STRATEGY_TEMPLATES
layer: layer_03
version: 1.0.0
status: Active
responsibility:
  - Strategy Templates相关业务
created_date: 2026-04-01
last_updated: 2026-04-07
owner: 首席文档架构?
standard_type: 专业量化机构模板标准
applicable_scope: 文档模板与规范
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
---

## 1. 策略分类体系



```

策略模板

├── 趋势跟踪策略

?  ├── 移动均线交叉策略

?  ├── 唐奇安通道策略

?  ├── 布林带趋势策?

?  └── MACD趋势策略

├── 均值回归策?

?  ├── 布林带回归策?

?  ├── RSI超买超卖策略

?  ├── 配对交易策略

?  └── 网格交易策略

├── 市场中性策?

?  ├── Alpha套利策略

?  ├── 统计套利策略

?  └── 因子中性策?

├── 事件驱动策略

?  ├── 财报发布策略

?  ├── 分析师评级策?

?  └── 股权激励策?

├── 多因子选股策略

?  ├── 价值成长策?

?  ├── 质量动量策略

?  └── 综合打分策略

└── 择时策略

    ├── 技术指标择?

    ├── 宏观择时

    └── 情绪择时

```



---



## 2. 策略基类设计



```python

from abc import ABC, abstractmethod

from dataclasses import dataclass

from typing import Dict, List, Optional, Any

from enum import Enum

import pandas as pd

import numpy as np



class StrategyStatus(Enum):

    INITIALIZING = "initializing"

    RUNNING = "running"

    PAUSED = "paused"

    STOPPED = "stopped"



@dataclass

class Signal:

    """交易信号"""

    symbol: str

    direction: int          # 1: 做多, -1: 做空, 0: 无信?

    strength: float         # 信号强度 0-1

    signal_type: str         # 'entry', 'exit', 'adjust'

    price: float            # 信号产生时的价格

    timestamp: pd.Timestamp

    metadata: Dict[str, Any] = None



@dataclass

class Position:

    """持仓信息"""

    symbol: str

    quantity: int

    entry_price: float

    current_price: float

    unrealized_pnl: float

    direction: str          # 'long', 'short'



class StrategyBase(ABC):

    """策略基类"""



    def __init__(self, config: Dict):

        self.config = config

        self.name = config.get('name', 'BaseStrategy')

        self.status = StrategyStatus.INITIALIZING

        self.positions: Dict[str, Position] = {}

        self.signals: List[Signal] = []

        self.params = self._init_params()



    @abstractmethod

    def initialize(self):

        """初始化策略参数和数据"""

        pass



    @abstractmethod

    def handle_data(self, data: pd.DataFrame) -> List[Signal]:

        """处理市场数据，生成信?



        参数:

            data: 包含 OHLCV 等数据的 DataFrame



        返回:

            Signal 列表

        """

        pass



    @abstractmethod

    def risk_check(self, signal: Signal, data: pd.DataFrame) -> bool:

        """风控检?



        返回:

            True: 信号通过，可以执?

            False: 信号被风控拦?

        """

        pass



    def on_order_status(self, order_id: str, status: str, fill_price: float):

        """订单状态更新回?""

        pass



    def _init_params(self) -> Dict:

        """初始化策略参?""

        return {}



    def get_state(self) -> Dict:

        """获取策略当前状?""

        return {

            'name': self.name,

            'status': self.status.value,

            'positions': {k: vars(v) for k, v in self.positions.items()},

            'params': self.params

        }

```



---



## 3. 趋势跟踪策略模板



### 3.1 移动均线交叉策略



```python

class MATrendStrategy(StrategyBase):

    """移动均线交叉趋势策略"""



    def _init_params(self) -> Dict:

        return {

            'fast_ma_period': 10,      # 快线周期

            'slow_ma_period': 30,      # 慢线周期

            'ma_type': 'SMA',          # 均线类型: SMA, EMA

            'position_size': 0.1,      # 仓位比例

            'stop_loss_pct': 0.02,     # 止损比例

            'take_profit_pct': 0.05    # 止盈比例

        }



    def initialize(self):

        self.status = StrategyStatus.RUNNING



    def handle_data(self, data: pd.DataFrame) -> List[Signal]:

        signals = []



        # 计算均线

        if self.params['ma_type'] == 'SMA':

            fast_ma = data['close'].rolling(self.params['fast_ma_period']).mean()

            slow_ma = data['close'].rolling(self.params['slow_ma_period']).mean()

        else:

            fast_ma = data['close'].ewm(self.params['fast_ma_period']).mean()

            slow_ma = data['close'].ewm(self.params['slow_ma_period']).mean()



        # 金叉做多

        if fast_ma.iloc[-1] > slow_ma.iloc[-1] and fast_ma.iloc[-2] <= slow_ma.iloc[-2]:

            signal = Signal(

                symbol=data['symbol'].iloc[-1],

                direction=1,

                strength=min((fast_ma.iloc[-1] - slow_ma.iloc[-1]) / slow_ma.iloc[-1] * 10, 1.0),

                signal_type='entry',

                price=data['close'].iloc[-1],

                timestamp=data['timestamp'].iloc[-1]

            )

            if self.risk_check(signal, data):

                signals.append(signal)



        # 死叉做空/平仓

        elif fast_ma.iloc[-1] < slow_ma.iloc[-1] and fast_ma.iloc[-2] >= slow_ma.iloc[-2]:

            signal = Signal(

                symbol=data['symbol'].iloc[-1],

                direction=0,  # 平仓

                strength=1.0,

                signal_type='exit',

                price=data['close'].iloc[-1],

                timestamp=data['timestamp'].iloc[-1]

            )

            signals.append(signal)



        return signals



    def risk_check(self, signal: Signal, data: pd.DataFrame) -> bool:

        # 基础风控检?

        if signal.strength < 0.1:

            return False

        return True

```



### 3.2 唐奇安通道策略



```python

class DonchianChannelStrategy(StrategyBase):

    """唐奇安通道突破策略"""



    def _init_params(self) -> Dict:

        return {

            'entry_period': 20,         # 入场通道周期

            'exit_period': 10,         # 出场通道周期

            'atr_period': 14,           # ATR周期

            'atr_multiplier': 2.0,     # ATR倍数

            'position_size': 0.1

        }



    def initialize(self):

        self.status = StrategyStatus.RUNNING



    def handle_data(self, data: pd.DataFrame) -> List[Signal]:

        signals = []



        # 计算唐奇安通道

        upper_channel = data['high'].rolling(self.params['entry_period']).max()

        lower_channel = data['low'].rolling(self.params['entry_period']).min()

        exit_upper = data['high'].rolling(self.params['exit_period']).max()

        exit_lower = data['low'].rolling(self.params['exit_period']).min()



        # ATR止损

        tr = self._calculate_tr(data)

        atr = tr.rolling(self.params['atr_period']).mean()



        current_price = data['close'].iloc[-1]

        symbol = data['symbol'].iloc[-1]



        # 突破上轨入场

        if data['high'].iloc[-1] > upper_channel.iloc[-2]:

            signal = Signal(

                symbol=symbol,

                direction=1,

                strength=min((current_price - upper_channel.iloc[-2]) / atr.iloc[-1], 1.0),

                signal_type='entry',

                price=current_price,

                timestamp=data['timestamp'].iloc[-1],

                metadata={

                    'stop_loss': current_price - self.params['atr_multiplier'] * atr.iloc[-1]

                }

            )

            if self.risk_check(signal, data):

                signals.append(signal)



        # 跌破出场通道或ATR止损

        elif data['low'].iloc[-1] < exit_lower.iloc[-2]:

            signal = Signal(

                symbol=symbol,

                direction=0,

                strength=1.0,

                signal_type='exit',

                price=current_price,

                timestamp=data['timestamp'].iloc[-1]

            )

            signals.append(signal)



        return signals



    def _calculate_tr(self, data: pd.DataFrame) -> pd.Series:

        tr1 = data['high'] - data['low']

        tr2 = abs(data['high'] - data['close'].shift(1))

        tr3 = abs(data['low'] - data['close'].shift(1))

        return pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

```



---



## 4. 均值回归策略模块



### 4.1 布林带回归策略



```python

class BollingerBandReversionStrategy(StrategyBase):

    """布林带均值回归策?""



    def _init_params(self) -> Dict:

        return {

            'bb_period': 20,            # 布林带周?

            'bb_std': 2.0,             # 标准差倍数

            'entry_threshold': 0.9,    # 入场阈?(0-1, 0.9为下轨附?

            'exit_threshold': 0.5,     # 出场阈?(0.5为中?

            'position_size': 0.1

        }



    def handle_data(self, data: pd.DataFrame) -> List[Signal]:

        signals = []



        # 计算布林?

        middle = data['close'].rolling(self.params['bb_period']).mean()

        std = data['close'].rolling(self.params['bb_period']).std()

        upper = middle + self.params['bb_std'] * std

        lower = middle - self.params['bb_std'] * std



        # 计算%B

        pct_b = (data['close'] - lower) / (upper - lower)



        current_price = data['close'].iloc[-1]

        symbol = data['symbol'].iloc[-1]



        # %B接近0（下轨附近）入场做多

        if pct_b.iloc[-1] < 0.1 and pct_b.iloc[-2] >= 0.1:

            signal = Signal(

                symbol=symbol,

                direction=1,

                strength=1.0 - pct_b.iloc[-1] / 0.1,

                signal_type='entry',

                price=current_price,

                timestamp=data['timestamp'].iloc[-1]

            )

            if self.risk_check(signal, data):

                signals.append(signal)



        # %B回到0.5（中轨）附近出场

        elif pct_b.iloc[-1] > 0.5 and pct_b.iloc[-2] <= 0.5:

            signal = Signal(

                symbol=symbol,

                direction=0,

                strength=pct_b.iloc[-1] - 0.5,

                signal_type='exit',

                price=current_price,

                timestamp=data['timestamp'].iloc[-1]

            )

            signals.append(signal)



        return signals

```



### 4.2 配对交易策略



```python

class PairTradingStrategy(StrategyBase):

    """配对交易策略"""



    def _init_params(self) -> Dict:

        return {

            'lookback_period': 60,      # 回看周期

            'entry_threshold': 2.0,     # 入场标准差倍数

            'exit_threshold': 0.5,      # 出场标准差倍数

            'pair': ('stock_a', 'stock_b'),  # 配对标的

            'position_size': 0.1

        }



    def initialize(self):

        self.spread_history = []

        self.status = StrategyStatus.RUNNING



    def handle_data(self, data: pd.DataFrame) -> List[Signal]:

        signals = []



        pair = self.params['pair']

        stock_a = data[data['symbol'] == pair[0]]['close']

        stock_b = data[data['symbol'] == pair[1]]['close']



        if len(stock_a) < self.params['lookback_period']:

            return signals



        # 计算价差

        hedge_ratio = self._calculate_hedge_ratio(stock_a, stock_b)

        spread = stock_a - hedge_ratio * stock_b



        # 计算z-score

        z_score = (spread.iloc[-1] - spread.rolling(self.params['lookback_period']).mean().iloc[-1]) / \

                  spread.rolling(self.params['lookback_period']).std().iloc[-1]



        current_price_a = stock_a.iloc[-1]

        current_price_b = stock_b.iloc[-1]



        # Z-score < -entry_threshold: A被低估，B被高估，买入A做空B

        if z_score < -self.params['entry_threshold']:

            signals.append(Signal(

                symbol=pair[0],

                direction=1,

                strength=min(abs(z_score) / self.params['entry_threshold'], 1.0),

                signal_type='entry',

                price=current_price_a,

                timestamp=data['timestamp'].iloc[-1]

            ))

            signals.append(Signal(

                symbol=pair[1],

                direction=-1,

                strength=min(abs(z_score) / self.params['entry_threshold'], 1.0),

                signal_type='entry',

                price=current_price_b,

                timestamp=data['timestamp'].iloc[-1]

            ))



        # Z-score > exit_threshold: 平仓

        elif abs(z_score) < self.params['exit_threshold']:

            signals.append(Signal(

                symbol=pair[0],

                direction=0,

                strength=1.0,

                signal_type='exit',

                price=current_price_a,

                timestamp=data['timestamp'].iloc[-1]

            ))

            signals.append(Signal(

                symbol=pair[1],

                direction=0,

                strength=1.0,

                signal_type='exit',

                price=current_price_b,

                timestamp=data['timestamp'].iloc[-1]

            ))



        return signals



    def _calculate_hedge_ratio(self, stock_a: pd.Series, stock_b: pd.Series) -> float:

        """计算对冲比率（简单线性回归）"""

        from scipy.stats import linregress

        slope, _, _, _, _ = linregress(stock_b, stock_a)

        return slope

```



---



## 5. 多因子选股策略模板



```python

class MultiFactorSelectionStrategy(StrategyBase):

    """多因子选股策略"""



    def _init_params(self) -> Dict:

        return {

            'factors': ['PE', 'ROE', 'MOM20', 'VOLUME_RATIO'],

            'factor_weights': [0.25, 0.25, 0.25, 0.25],

            'top_n': 50,               # 选前N只股?

            'rebalance_period': 5,      # 调仓周期（交易日?

            'position_size': 0.02      # 单只股票仓位

        }



    def initialize(self):

        self.last_rebalance_date = None

        self.selected_stocks = []

        self.status = StrategyStatus.RUNNING



    def handle_data(self, data: pd.DataFrame) -> List[Signal]:

        signals = []



        current_date = data['timestamp'].iloc[-1].date()



        # 检查是否需要调?

        if self._should_rebalance(current_date):

            new_stocks = self._select_stocks(data)



            # 卖出不在新名单中的股?

            for stock in self.selected_stocks:

                if stock not in new_stocks:

                    stock_data = data[data['symbol'] == stock].iloc[-1]

                    signals.append(Signal(

                        symbol=stock,

                        direction=0,

                        strength=1.0,

                        signal_type='exit',

                        price=stock_data['close'],

                        timestamp=stock_data['timestamp']

                    ))



            # 买入新名单中的股?

            for stock in new_stocks:

                if stock not in self.selected_stocks:

                    stock_data = data[data['symbol'] == stock].iloc[-1]

                    signals.append(Signal(

                        symbol=stock,

                        direction=1,

                        strength=1.0 / len(new_stocks),

                        signal_type='entry',

                        price=stock_data['close'],

                        timestamp=stock_data['timestamp']

                    ))



            self.selected_stocks = new_stocks

            self.last_rebalance_date = current_date



        return signals



    def _should_rebalance(self, current_date) -> bool:

        if self.last_rebalance_date is None:

            return True



        trading_days = self._get_trading_days(self.last_rebalance_date, current_date)

        return trading_days >= self.params['rebalance_period']



    def _select_stocks(self, data: pd.DataFrame) -> List[str]:

        """多因子打分选股"""

        scores = {}



        for symbol in data['symbol'].unique():

            stock_data = data[data['symbol'] == symbol]

            if len(stock_data) == 0:

                continue



            score = 0.0

            for factor, weight in zip(self.params['factors'], self.params['factor_weights']):

                factor_value = self._get_factor_value(stock_data, factor)

                factor_score = self._normalize_factor(factor_value, factor)

                score += weight * factor_score



            scores[symbol] = score



        # 按分数排序，选前N?

        sorted_stocks = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return [s[0] for s in sorted_stocks[:self.params['top_n']]]



    def _get_factor_value(self, stock_data: pd.DataFrame, factor: str) -> float:

        """获取因子?""

        return stock_data[factor].iloc[-1]



    def _normalize_factor(self, value: float, factor: str) -> float:

        """因子标准化（Z-score?""

        # 简化版，实际应使用全市场截面标准化

        return (value - 0) / 1.0  # placeholder

```



---



## 6. 策略配置示例



```yaml

# config/strategies/s001_trend_follow.yaml

strategy:

  name: "S001_移动均线趋势"

  type: "trend_following"

  version: "1.0.0"



parameters:

  fast_ma_period: 10

  slow_ma_period: 30

  ma_type: "EMA"

  position_size: 0.1

  stop_loss_pct: 0.02

  take_profit_pct: 0.05



risk:

  max_position_size: 0.2

  max_drawdown: 0.15

  max_loss_per_trade: 0.02



execution:

  order_type: "limit"

  timeout: 300

  retry_count: 3

```



---



## 7. 策略生命周期状态机



```python

class StrategyLifecycle:

    """策略生命周期状态机"""



    STATES = {

        'IDEA': '创意阶段',

        'BACKTEST': '回测阶段',

        'PAPER_TRADING': '模拟交易',

        'LIVE_TRADING': '实盘运行',

        'PAUSED': '暂停',

        'OPTIMIZING': '优化?,

        'DEPRECATED': '退?

    }



    TRANSITIONS = {

        'IDEA': ['BACKTEST'],

        'BACKTEST': ['PAPER_TRADING', 'DEPRECATED'],

        'PAPER_TRADING': ['LIVE_TRADING', 'BACKTEST'],

        'LIVE_TRADING': ['PAUSED', 'OPTIMIZING', 'DEPRECATED'],

        'PAUSED': ['LIVE_TRADING', 'DEPRECATED'],

        'OPTIMIZING': ['BACKTEST', 'LIVE_TRADING'],

    }



    @classmethod

    def can_transition(cls, from_state: str, to_state: str) -> bool:

        return to_state in cls.TRANSITIONS.get(from_state, [])

```



---



**版本**: 1.0 | **更新**: 2026-03-28

