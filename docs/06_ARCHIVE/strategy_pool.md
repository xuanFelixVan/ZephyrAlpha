---
module_id: STRATEGY_POOL
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 策略v10文档
---

﻿---
module_id: ARCHIVE_STRATEGY_POOL_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
standard_type: 专业量化机构文档
applicable_scope: 全系?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
responsibility:
  - 归档文档、历史版本

---
---

# 策略?v1.0
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 清风量化多策略系统的策略池管理框?
>
> **配套文档**?
> - 主文档：
> - 因子库：
> - 战术手册：../trading-tactics/tactics_manual.md
>
> **版本说明**?
> - v1.0：初始版本，整合游资量化策略和策略池管理框架

***

## 目录

1. [策略池概述](#1-策略池概?
2. [策略分类体系](#2-策略分类体系)
3. [策略接口标准](#3-策略接口标准)
4. [策略池管理器](#4-策略池管理器)
5. [策略选择机制](#5-策略选择机制)
6. [策略池配置](#6-策略池配?
7. [游资量化策略库](#7-游资量化策略?
8. [行业精选策略库](#8-行业精选策略库)

***

## 1. 策略池概?

### 1.1 策略池定?

> **策略?*是量化交易系统的核心组件，负责管?0-50种交易策略，根据市场状态动态选择和分配权重?

```
┌─────────────────────────────────────────────────────────────?
?                     策略池系?                             ?
├─────────────────────────────────────────────────────────────?
? 前置层输??策略选择??策略权重分配 ?信号输出          ?
?      ?             ?             ?             ?       ?
? 市场状?        匹配策略        动态权?      聚合信号   ?
└─────────────────────────────────────────────────────────────?
```

### 1.2 策略池容量规?

| 策略类型 | 策略数量 | 占比 |
|----------|----------|------|
| 趋势跟踪?| 8-10?| 25% |
| 均值回归类 | 6-8?| 20% |
| 动量?| 6-8?| 20% |
| 短线交易?| 8-10?| 25% |
| 套利?| 3-5?| 10% |
| **合计** | **30-50?* | 100% |

### 1.3 市场状态适配矩阵

| 市场状?| 趋势?| 均值回?| 动量?| 短线?| 套利?|
|----------|--------|----------|--------|--------|--------|
| 牛市 | ⭐⭐⭐⭐?| ?| ⭐⭐?| ⭐⭐ | ?|
| 熊市 | ?| ⭐⭐ | ?| ⭐⭐⭐⭐?| ⭐⭐ |
| 震荡?| ⭐⭐ | ⭐⭐⭐⭐?| ⭐⭐?| ⭐⭐ | ⭐⭐?|
| 妖股周期 | ?| ?| ⭐⭐?| ⭐⭐⭐⭐?| ?|
| 混沌状?| ?| ⭐⭐ | ?| ⭐⭐ | ⭐⭐⭐⭐ |

***

## 2. 策略分类体系

### 2.1 趋势跟踪类策略（8-10种）

| 策略编号 | 策略名称 | 核心逻辑 | 适用市场 | 风险等级 |
|----------|----------|----------|----------|----------|
| T001 | 均线趋势策略 | MA5>MA20>MA60多头排列 | 牛市 | ?|
| T002 | MACD趋势策略 | DIF>DEA且MACD柱状线放?| 牛市 | ?|
| T003 | ADX趋势确认策略 | ADX>25?DI>-DI | 趋势?| 中低 |
| T004 | 趋势突破策略 | 价格突破20日高?| 趋势?| ?|
| T005 | 布林带趋势策?| 中轨向上+价格在上轨运?| 牛市 | ?|
| T006 | ATR趋势策略 | 趋势强度>2倍ATR | 趋势?| ?|
| T007 | 均线金叉策略 | MA5上穿MA20 | 任意 | 中低 |
| T008 | 趋势线突破策?| 价格突破趋势?| 趋势?| ?|
| T009 | 多周期共振策?| 日线+周线趋势一?| 牛市 | ?|
| T010 | 趋势回调策略 | 回调至EMA55企稳 | 牛市回调 | ?|

### 2.2 均值回归类策略?-8种）

| 策略编号 | 策略名称 | 核心逻辑 | 适用市场 | 风险等级 |
|----------|----------|----------|----------|----------|
| M001 | RSI超卖策略 | RSI<30且拐头向?| 震荡?| ?|
| M002 | 布林带回归策?| 价格触及下轨+缩量 | 震荡?| 中低 |
| M003 | KDJ超卖策略 | KDJ<20金叉 | 超卖反弹 | ?|
| M004 | 波动率收缩策?|ATR收缩至均线下?| 突破?| ?|
| M005 | 乖离率策?| 价格偏离MA20过远 | 均值回?| 中低 |
| M006 | 量价背离策略 | 价格新低+量能缩量 | 反弹 | ?|
| M007 | 支撑位策?| 回踩重要支撑位企?| 任意 | 中低 |
| M008 | 缩量整理策略 | 量比<0.8+振幅<3% | 整理后突?| ?|

### 2.3 动量类策略（6-8种）

| 策略编号 | 策略名称 | 核心逻辑 | 适用市场 | 风险等级 |
|----------|----------|----------|----------|----------|
| P001 | 动量加速策?| 连续3日上?成交量放?| 强势市场 | ?|
| P002 | 板块动量策略 | 所属板块涨?3% | 板块轮动 | ?|
| P003 | 资金流入策略 | 机构净流入>1?| 资金推动 | ?|
| P004 | 动量反转策略 | 前期强势股回调后反弹 | 轮动 | ?|
| P005 | 北向资金策略 | 北向连续净流入3?| 外资主导 | ?|
| P006 | 相对强弱策略 | 个股RS>板块RS | 强势?| 中低 |
| P007 | 动量攒旗策略 | 旗形整理后突?| 趋势中继 | ?|
| P008 | 加速突破策?| 成交量放??涨幅>5% | 突破 | ?|

### 2.4 短线交易类策略（8-10种）

| 策略编号 | 策略名称 | 核心逻辑 | 适用市场 | 风险等级 |
|----------|----------|----------|----------|----------|
| S001 | 首板策略 | 首次涨停+封单>1?| 妖股周期 | 极高 |
| S002 | 连板策略 | 连续涨停>=2?| 强势市场 | 极高 |
| S003 | 龙头股策?| 板块龙头+涨停 | 热点轮动 | ?|
| S004 | 涨停回封策略 | 开板后回封+时间<30?| 强势市场 | ?|
| S005 | 尾盘策略 | 14:30后涨?-8% | 短线 | ?|
| S006 | 集合竞价策略 | 竞价涨幅2-5% | 短线 | ?|
| S007 | 炸板反抽策略 | 涨停炸板后反?| 超跌反弹 | ?|
| S008 | 弱势抄底策略 | 大盘下跌>1%+个股抗跌 | 逆势 | ?|
| S009 | 情绪转折策略 | 跌停家数减少+翘板 | 情绪底部 | ?|
| S010 | 游资席位策略 | 机构席位买入+次日溢价 | 跟庄 | ?|

### 2.5 套利类策略（3-5种）

| 策略编号 | 策略名称 | 核心逻辑 | 适用市场 | 风险等级 |
|----------|----------|----------|----------|----------|
| A001 | 期现套利策略 | 期货升贴水回?| 任意 | ?|
| A002 | 跨品种套利策?| 相关品种价差回归 | 商品 | 中低 |
| A003 | 统计套利策略 | 均值回?协整关系 | 统计机会 | ?|
| A004 | 南北向套利策?| 沪深港通价?| 跨境 | ?|
| A005 | 可转债套利策?| 转股价值偏?| 低波?| ?|

***

## 3. 策略接口标准

### 3.1 策略基类定义

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

### 3.2 策略注册装饰?

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

### 3.3 策略实现示例

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
                stop_loss = ma20 * 0.97  # 止损设在中轨下方3%
                target = current_price * 1.1  # 目标涨幅10%

                return TradingSignal(
                    code=stock_data['code'],
                    signal=SignalType.BUY,
                    confidence=0.75,
                    entry_price=current_price,
                    stop_loss=stop_loss,
                    target_price=target,
                    strategy_name=self.name,
                    position_size=0.15,  # 趋势明确?5%仓位
                    holding_period=10
                )

        return None
```

***

## 4. 策略池管理器

### 4.1 策略池管理器?

```python
class StrategyPool:
    """策略池管理器"""

    def __init__(self, max_strategies: int = 50):
        self.strategies: Dict[str, BaseStrategy] = {}
        self.strategy_weights: Dict[str, float] = {}
        self.max_strategies = max_strategies
        self.market_state = MarketState.VOLATILE
        self.enabled_strategies: Set[str] = set()

    def register_strategy(self, strategy: BaseStrategy) -> bool:
        """
        注册策略到策略池
        """
        if len(self.strategies) >= self.max_strategies:
            return False

        if strategy.strategy_id in self.strategies:
            return False

        self.strategies[strategy.strategy_id] = strategy
        self.enabled_strategies.add(strategy.strategy_id)
        return True

    def unregister_strategy(self, strategy_id: str) -> bool:
        """注销策略"""
        if strategy_id in self.strategies:
            del self.strategies[strategy_id]
            self.enabled_strategies.discard(strategy_id)
            return True
        return False

    def set_market_state(self, market_state: MarketState):
        """设置市场状?""
        self.market_state = market_state

    def select_strategies(self,
                         min_sharpe: float = 0.5,
                         max_strategies: int = 10) -> List[BaseStrategy]:
        """
        根据市场状态选择策略

        参数:
            min_sharpe: 最小夏普比率要?
            max_strategies: 最多选择的策略数?

        返回:
            符合条件的策略列表，按夏普比率降序排?
        """
        candidates = []

        for strategy_id in self.enabled_strategies:
            strategy = self.strategies[strategy_id]

            # 检查是否适用于当前市场状?
            if self.market_state not in strategy.get_applicable_states():
                continue

            # 检查绩?
            perf = strategy.get_performance()
            if perf.sharpe_ratio < min_sharpe:
                continue

            candidates.append((strategy, perf.sharpe_ratio))

        # 按夏普比率降序排?
        candidates.sort(key=lambda x: x[1], reverse=True)

        return [s[0] for s in candidates[:max_strategies]]

    def allocate_weights(self, selected_strategies: List[BaseStrategy]) -> Dict[str, float]:
        """
        策略权重分配

        方法: 基于夏普比率的，风险平价分配

        返回:
            策略ID -> 权重 的字?
        """
        if not selected_strategies:
            return {}

        # 计算总夏普比?
        total_sharpe = sum(
            s.get_performance().sharpe_ratio
            for s in selected_strategies
        )

        if total_sharpe == 0:
            return {s.strategy_id: 1.0/len(selected_strategies)
                   for s in selected_strategies}

        # 基于夏普比率分配权重
        weights = {}
        for strategy in selected_strategies:
            sharpe = strategy.get_performance().sharpe_ratio
            weights[strategy.strategy_id] = sharpe / total_sharpe

        return weights

    def generate_composite_signal(self,
                                  stock_code: str,
                                  market_data: pd.DataFrame,
                                  stock_data: pd.DataFrame) -> List[TradingSignal]:
        """
        生成复合信号

        流程:
        1. 选择适合当前市场状态的策略
        2. 分配策略权重
        3. 各策略分别生成信?
        4. 按权重聚合信?
        """
        # 选择策略
        selected = self.select_strategies(max_strategies=10)
        if not selected:
            return []

        # 分配权重
        self.strategy_weights = self.allocate_weights(selected)

        # 生成各策略信?
        all_signals = []
        for strategy in selected:
            signal = strategy.generate_signal(
                market_data, stock_data, self.market_state
            )
            if signal:
                signal.confidence *= self.strategy_weights[strategy.strategy_id]
                all_signals.append(signal)

        # 按置信度排序
        all_signals.sort(key=lambda x: x.confidence, reverse=True)

        return all_signals
```

### 4.2 策略池管理器配置

```python
# 策略池配?
STRATEGY_POOL_CONFIG = {
    'max_strategies': 50,              # 最大策略数?
    'default_selection': 10,            # 默认选择策略数量
    'min_sharpe_for_selection': 0.3,   # 选择策略的最低夏普比?
    'min_confidence_threshold': 0.4,   # 信号最小置信度阈?
    'max_position_per_strategy': 0.2,  # 单策略最大仓?
    'market_state_update_freq': 'daily' # 市场状态更新频?
}

# 策略参数配置模板
STRATEGY_PARAM_TEMPLATES = {
    'T001': {  # 均线趋势策略
        'ma_short': 5,
        'ma_medium': 20,
        'ma_long': 60,
        'min_volume_ratio': 1.5
    },
    'S001': {  # 首板策略
        'min_limit_up_amount': 1e8,     # 最小封单金??
        'max_float_market_cap': 100e8,  # 最大流通市?00?
        'max_turnover_rate': 15,        # 最大换手率15%
        'max_open_times': 2              # 最大开板次??
    },
    'M001': {  # RSI超卖策略
        'rsi_period': 14,
        'rsi_oversold': 30,
        'rsi_threshold': 40           # 拐头向上的阈?
    }
}
```

***

## 5. 策略选择机制

### 5.1 基于市场状态的动态选择

```python
class MarketStateStrategySelector:
    """基于市场状态的策略选择?""

    STATE_STRATEGY_CONFIG = {
        MarketState.BULL: {
            'primary': ['T001', 'T002', 'T005', 'P001', 'P003'],
            'secondary': ['M005', 'S006'],
            'weights': {'primary': 0.7, 'secondary': 0.3}
        },
        MarketState.BEAR: {
            'primary': ['S008', 'S009'],
            'secondary': ['M001', 'M003'],
            'weights': {'primary': 0.6, 'secondary': 0.4}
        },
        MarketState.VOLATILE: {
            'primary': ['M001', 'M002', 'M005', 'M007'],
            'secondary': ['T007', 'P006'],
            'weights': {'primary': 0.6, 'secondary': 0.4}
        },
        MarketState.YAO: {
            'primary': ['S001', 'S002', 'S003', 'S004'],
            'secondary': ['S007', 'S010'],
            'weights': {'primary': 0.8, 'secondary': 0.2}
        },
        MarketState.CHAOS: {
            'primary': ['A001', 'A002', 'A003', 'A004'],
            'secondary': [],
            'weights': {'primary': 1.0, 'secondary': 0.0}
        }
    }

    def select_for_state(self,
                        market_state: MarketState,
                        available_strategies: Dict[str, BaseStrategy]
                        ) -> List[tuple]:
        """
        根据市场状态选择策略及权?

        返回:
            [(strategy, weight), ...]
        """
        config = self.STATE_STRATEGY_CONFIG.get(market_state, {})
        primary_ids = config.get('primary', [])
        secondary_ids = config.get('secondary', [])
        weights = config.get('weights', {'primary': 1.0, 'secondary': 0.0})

        selected = []
        primary_weight = weights.get('primary', 1.0)
        secondary_weight = weights.get('secondary', 0.0)

        for sid in primary_ids:
            if sid in available_strategies:
                selected.append((available_strategies[sid], primary_weight))

        for sid in secondary_ids:
            if sid in available_strategies:
                selected.append((available_strategies[sid], secondary_weight))

        # 归一化权?
        total = sum(w for _, w in selected)
        if total > 0:
            selected = [(s, w/total) for s, w in selected]

        return selected
```

### 5.2 策略绩效动态调?

```python
class StrategyPerformanceTracker:
    """策略绩效追踪?""

    def __init__(self, lookback_periods: int = 20):
        self.lookback_periods = lookback_periods
        self.performance_history: Dict[str, List[float]] = {}
        self.signal_history: Dict[str, List[TradingSignal]] = {}

    def record_signal(self, strategy_id: str, signal: TradingSignal, actual_return: float):
        """记录信号和实际收?""
        if strategy_id not in self.signal_history:
            self.signal_history[strategy_id] = []
            self.performance_history[strategy_id] = []

        self.signal_history[strategy_id].append(signal)
        self.performance_history[strategy_id].append(actual_return)

        # 保持固定窗口
        if len(self.performance_history[strategy_id]) > self.lookback_periods:
            self.performance_history[strategy_id].pop(0)
            self.signal_history[strategy_id].pop(0)

    def calculate_recent_performance(self, strategy_id: str) -> StrategyPerformance:
        """计算近期绩效"""
        returns = self.performance_history.get(strategy_id, [])
        if not returns:
            return StrategyPerformance(0, 0, 0, 0, 0, 0)

        wins = [r for r in returns if r > 0]
        total_trades = len(returns)

        return StrategyPerformance(
            win_rate=len(wins) / total_trades if total_trades > 0 else 0,
            avg_return=np.mean(returns),
            max_drawdown=self._calculate_max_drawdown(returns),
            sharpe_ratio=self._calculate_sharpe(returns),
            total_trades=total_trades,
            avg_holding_days=5.0  # 简化处?
        )

    def update_strategy_performance(self,
                                   strategy: BaseStrategy,
                                   strategy_id: str):
        """更新策略绩效"""
        strategy.performance = self.calculate_recent_performance(strategy_id)

    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """计算最大回?""
        cumulative = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        return abs(np.min(drawdown)) if len(drawdown) > 0 else 0

    def _calculate_sharpe(self, returns: List[float], risk_free: float = 0.02) -> float:
        """计算夏普比率"""
        if len(returns) < 2:
            return 0
        excess_returns = np.array(returns) - risk_free / 252
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252) if np.std(excess_returns) > 0 else 0
```

***

## 6. 策略池配?

### 6.1 策略池初始化配置

```python
def initialize_strategy_pool() -> StrategyPool:
    """
    初始化策略池

    流程:
    1. 创建策略池实?
    2. 注册所有策?
    3. 设置策略参数
    4. 加载历史绩效
    """
    pool = StrategyPool(max_strategies=50)

    # 注册趋势类策?
    pool.register_strategy(MaTrendStrategy())
    pool.register_strategy(MacdTrendStrategy())
    pool.register_strategy(AdxTrendStrategy())
    pool.register_strategy(BreakoutStrategy())

    # 注册均值回归类策略
    pool.register_strategy(RsiOversoldStrategy())
    pool.register_strategy(BollingerBandStrategy())
    pool.register_strategy(KdjOversoldStrategy())

    # 注册动量类策?
    pool.register_strategy(MomentumAccelerateStrategy())
    pool.register_strategy(SectorMomentumStrategy())
    pool.register_strategy(FundFlowStrategy())

    # 注册短线交易类策?
    pool.register_strategy(FirstLimitUpStrategy())
    pool.register_strategy(ConsecutiveLimitUpStrategy())
    pool.register_strategy(DragonStockStrategy())
    pool.register_strategy(LimitBackfillStrategy())

    # 注册套利类策?
    pool.register_strategy(ArbitrageStrategy())

    return pool

# 策略池单?
strategy_pool_instance = None

def get_strategy_pool() -> StrategyPool:
    """获取策略池单?""
    global strategy_pool_instance
    if strategy_pool_instance is None:
        strategy_pool_instance = initialize_strategy_pool()
    return strategy_pool_instance
```

### 6.2 策略信号聚合配置

```python
SIGNAL_AGGREGATION_CONFIG = {
    'min_strategies_for_signal': 2,     # 触发信号的最少策略数
    'signal_aggregation_method': 'weighted_confidence',  # 置信度加?
    'position_sizing': {
        'method': 'kelly_fraction',      # 凯利公式
        'kelly_fraction': 0.5,           # 凯利半仓
        'max_position': 0.3,             # 最大仓?0%
        'min_position': 0.05             # 最小仓?%
    },
    'risk_control': {
        'max_strategies_per_stock': 3,  # 单只股票最多策略数
        'max_total_positions': 20,       # 最大持仓数?
        'correlation_threshold': 0.7     # 持仓相关性阈?
    }
}
```

***

## 7. 游资量化策略?

> 本章节来源：附录Q/BC/BE/BF/BG?- 顶级游资交易思想体系量化提炼
>
> **说明**：这些策略来自A股顶级游资的经验总结，已抽象为量化规则，需历史回测验证有效性后再入?

### 7.1 Asking（邱宝裕）核心策?

#### S011: 只做超强势股策略

| 属?| 内容 |
|------|------|
| 策略编号 | S011 |
| 策略名称 | 只做超强势股 |
| 来源 | Asking（邱宝裕?|
| 适用市场 | 妖股周期、牛?|
| 风险等级 | 极高 |

**量化规则**?
- 涨幅 > 5%
- 成交?> 10?
- 换手?> 10%
- 属于热点板块

```python
class UltraStrongStockStrategy(BaseStrategy):
    """只做超强势股策略"""

    def __init__(self):
        super().__init__("只做超强势股", "S011")
        self.market_states = [MarketState.YAO, MarketState.BULL]
        self.parameters = {
            'min_change_pct': 5.0,      # 最小涨?%
            'min_turnover': 1e9,       # 最小成交额10?
            'min_turnover_rate': 10.0, # 最小换手率10%
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 涨幅过滤
        if stock_data['change_pct'] < params['min_change_pct']:
            return None

        # 成交额过?
        if stock_data['turnover'] < params['min_turnover']:
            return None

        # 换手率过?
        if stock_data['turnover_rate'] < params['min_turnover_rate']:
            return None

        # 热点板块过滤
        if not stock_data.get('is_hot_sector', False):
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.85,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.95,
            target_price=stock_data['close'] * 1.15,
            strategy_name=self.name,
            position_size=0.10,  # 高风险策略，仓位控制?0%
            holding_period=3
        )
```

#### S012: 守株待兔策略

| 属?| 内容 |
|------|------|
| 策略编号 | S012 |
| 策略名称 | 守株待兔（超跌反弹） |
| 来源 | Asking（邱宝裕?|
| 适用市场 | 熊市反弹、震荡市 |
| 风险等级 | ?|

**量化规则**?
- 已有2个大阳线以上（超强势股）
- 回调至MA5附近
- 缩量整理
- 等待反弹信号

```python
class WaitAndJumpStrategy(BaseStrategy):
    """守株待兔策略"""

    def __init__(self):
        super().__init__("守株待兔", "S012")
        self.market_states = [MarketState.BEAR, MarketState.VOLATILE]
        self.parameters = {
            'min_up_days': 2,            # 至少2个大阳线
            'min_up_pct': 5.0,          # 每根阳线至少5%
            'ma5_distance': 0.02,       # 距离MA5不超?%
            'volume_ratio_max': 0.8,    # 缩量整理
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 检查连续上?
        up_count = 0
        for i in range(params['min_up_days']):
            if stock_data[f'd_{i}_change_pct'] >= params['min_up_pct']:
                up_count += 1

        if up_count < params['min_up_days']:
            return None

        # 回调至MA5附近
        ma5 = stock_data['ma5']
        current = stock_data['close']
        if abs(current - ma5) / ma5 > params['ma5_distance']:
            return None

        # 缩量整理
        if stock_data['volume_ratio'] > params['volume_ratio_max']:
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.70,
            entry_price=current,
            stop_loss=ma5 * 0.97,
            target_price=current * 1.08,
            strategy_name=self.name,
            position_size=0.15,
            holding_period=5
        )
```

### 7.2 炒股养家情绪策略

#### S013: 情绪转折策略

| 属?| 内容 |
|------|------|
| 策略编号 | S013 |
| 策略名称 | 情绪转折策略 |
| 来源 | 炒股养家 |
| 适用市场 | 妖股周期、情绪底?|
| 风险等级 | ?|

**量化规则**?
- 赚钱效应强时敢于重仓
- 亏钱效应弥漫时空?
- 跌停家数减少+翘板

```python
class SentimentReversalStrategy(BaseStrategy):
    """情绪转折策略"""

    def __init__(self):
        super().__init__("情绪转折", "S013")
        self.market_states = [MarketState.YAO, MarketState.VOLATILE]
        self.parameters = {
            'profit_ratio_threshold': 0.6,   # 赚钱效应阈?0%
            'limit_down_decrease': 10,       # 跌停家数减少
            'rebound_candidates': 5,          # 翘板候选数?
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 赚钱效应评估
        profit_ratio = market_data['上涨家数'] / market_data['总交易家?]
        if profit_ratio < params['profit_ratio_threshold']:
            return None

        # 跌停家数减少
        limit_down_change = market_data['limit_down_count_yesterday'] - market_data['limit_down_count_today']
        if limit_down_change < params['limit_down_decrease']:
            return None

        # 有翘板候?
        rebound_count = self.count_rebound_candidates(market_data)
        if rebound_count < params['rebound_candidates']:
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.75,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.95,
            target_price=stock_data['close'] * 1.12,
            strategy_name=self.name,
            position_size=0.12,
            holding_period=3
        )
```

### 7.3 五日线战?

#### T011: 五日线趋势策?

| 属?| 内容 |
|------|------|
| 策略编号 | T011 |
| 策略名称 | 五日线趋势策?|
| 来源 | 明王心法 |
| 适用市场 | 牛市、震荡市 |
| 风险等级 | ?|

**量化规则**?
- 大盘?日线上方：右侧交易，积极操作
- 大盘?日线下方：左侧交易，谨慎操作
- 买入?日线收复 + 成交量逆转 + 强势板块

```python
class FiveDayLineStrategy(BaseStrategy):
    """五日线战?""

    def __init__(self):
        super().__init__("五日线战?, "T011")
        self.market_states = [MarketState.BULL, MarketState.VOLATILE]
        self.parameters = {
            'position_threshold': 0.01,    # 偏离阈?%
            'volume_reversal': True,       # 成交量逆转
        }

    def check_market_position(self, index_close, ma5):
        position = (index_close - ma5) / ma5
        if position > self.parameters['position_threshold']:
            return {'position': 'above', 'action': '右侧交易', 'limit': 0.8}
        elif position < -self.parameters['position_threshold']:
            return {'position': 'below', 'action': '左侧交易', 'limit': 0.3}
        return {'position': 'near', 'action': '观望', 'limit': 0.5}

    def generate_signal(self, market_data, stock_data, market_state):
        ma5 = stock_data['ma5']
        current = stock_data['close']

        # 5日线收复
        if current < ma5:
            return None

        # 成交量逆转确认
        if self.parameters['volume_reversal']:
            if not self.check_volume_reversal(stock_data):
                return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.70,
            entry_price=current,
            stop_loss=ma5 * 0.97,
            target_price=current * 1.08,
            strategy_name=self.name,
            position_size=0.15,
            holding_period=5
        )
```

### 7.4 反弹三定律策?

#### M009: 反弹三定律策?

| 属?| 内容 |
|------|------|
| 策略编号 | M009 |
| 策略名称 | 反弹三定?|
| 来源 | 明王心法 |
| 适用市场 | 熊市反弹、震荡市 |
| 风险等级 | ?|

**量化规则**?
- 第一定律：成交量逆转
- 第二定律?日线收复
- 第三定律：强势板块出?
- 共振越多，信号越?

```python
class ReboundThreeLawsStrategy(BaseStrategy):
    """反弹三定律策?""

    def __init__(self):
        super().__init__("反弹三定?, "M009")
        self.market_states = [MarketState.BEAR, MarketState.VOLATILE]
        self.parameters = {
            '共振阈?: 2,  # 至少2个条件触?
        }

    def generate_signal(self, market_data, stock_data, market_state):
       共振 = 0

        # 第一定律：成交量逆转
        if self.check_volume_reversal(stock_data):
            共振 += 1

        # 第二定律?日线收复
        if stock_data['close'] > stock_data['ma5']:
            共振 += 1

        # 第三定律：强势板块出?
        if stock_data.get('is_strong_sector', False):
            共振 += 1

        if 共振 < self.parameters['共振阈?]:
            return None

        confidence = 共振 / 3
        position_size = 0.15 if 共振 == 2 else 0.25

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=confidence,
            entry_price=stock_data['close'],
            stop_loss=stock_data['ma5'] * 0.97,
            target_price=stock_data['close'] * 1.10,
            strategy_name=self.name,
            position_size=position_size,
            holding_period=5
        )
```

### 7.5 二板定龙头策?

#### S014: 二板定龙头策?

| 属?| 内容 |
|------|------|
| 策略编号 | S014 |
| 策略名称 | 二板定龙?|
| 来源 | 赵老哥 |
| 适用市场 | 妖股周期 |
| 风险等级 | 极高 |

**量化规则**?
- 从昨日首板中选取二板候?
- 一板后次日高开幅度?%-7%
- 回调不破一板最高价80%
- 10点前封板
- 同题材有一板跟?

```python
class SecondBoardDragonStrategy(BaseStrategy):
    """二板定龙头策?""

    def __init__(self):
        super().__init__("二板定龙?, "S014")
        self.market_states = [MarketState.YAO]
        self.parameters = {
            'open_ratio_min': 0.03,      # 高开最?%
            'open_ratio_max': 0.07,      # 高开最?%
            'low_protection': 0.80,      # 回调不破一板最?0%
            'seal_time_limit': '10:00',   # 10点前封板
            'min_score': 0.70,           # 最小评?
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 高开幅度筛?
        open_ratio = stock_data['open_ratio']
        if not (params['open_ratio_min'] <= open_ratio <= params['open_ratio_max']):
            return None

        # 回调不破一板最高价80%
        yesterday_high = stock_data['yesterday_high']
        today_low = stock_data['low']
        if today_low < yesterday_high * params['low_protection']:
            return None

        # 10点前封板
        if stock_data['seal_time'] > params['seal_time_limit']:
            return None

        # 同题材有一板跟?
        if stock_data.get('same_theme_first_board', 0) < 1:
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.85,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.93,
            target_price=stock_data['close'] * 1.20,
            strategy_name=self.name,
            position_size=0.10,
            holding_period=3
        )
```

### 7.6 超短线最高境界策?

#### S015: 独股一箭策?

| 属?| 内容 |
|------|------|
| 策略编号 | S015 |
| 策略名称 | 独股一箭（超短线） |
| 来源 | 独股一?|
| 适用市场 | 妖股周期（强势环境） |
| 风险等级 | 极高 |

**量化规则**?
- 只攻不守，满仓一只股?
- 第二天不管盈亏都?
- 5日线附近买，不追?
- 冲高无量坚决?
- 热点和强势股可忽略大?

```python
class DuguYijianStrategy(BaseStrategy):
    """独股一箭超短线策略"""

    def __init__(self):
        super().__init__("独股一?, "S015")
        self.market_states = [MarketState.YAO]
        self.parameters = {
            'ma5_distance': 0.02,        # 5日线附近2%
            'chong_gao_volume_ratio': 0.5, # 冲高无量标准
            'profit_target': 0.09,         # 目标涨幅9%
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 环境判断：赚钱效?
        profit_ratio = market_data['上涨家数'] / market_data['总交易家?]
        if profit_ratio < 0.5 and not stock_data.get('is_hot_stock', False):
            return None

        # 5日线附近
        ma5 = stock_data['ma5']
        current = stock_data['close']
        if abs(current - ma5) / ma5 > params['ma5_distance']:
            return None

        # 有题?热点
        if not (stock_data.get('has_theme', False) and stock_data.get('is_hot', False)):
            return None

        position = 1.0 if stock_data.get('is_hot_stock', False) else 0.5

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.80,
            entry_price=current,
            stop_loss=current * 0.97,
            target_price=current * (1 + params['profit_target']),
            strategy_name=self.name,
            position_size=position,
            holding_period=1  # 超短线，次日必须?
        )

    def exit_signal(self, position_data):
        """超短线卖出信?""
        current = position_data['current_price']
        entry = position_data['entry_price']
        volume_ratio = position_data['volume_ratio']

        # 冲高无量坚决?
        if volume_ratio < 0.5 and current > entry * 1.05:
            return {'action': '卖出', 'reason': '冲高无量'}

        # 涨停差一点就?
        limit_up = entry * 1.10
        if current < limit_up and current >= entry * 1.09:
            return {'action': '卖出', 'reason': '涨停差一?}

        return None  # 持有至收?
```

### 7.7 仓位管理策略

#### R001: 动态仓位管理策?

| 属?| 内容 |
|------|------|
| 策略编号 | R001 |
| 策略名称 | 动态仓位管?|
| 来源 | 龙飞?|
| 适用市场 | 所有市?|
| 风险等级 | 低（风控策略?|

**量化规则**?
- 赢面仓位量化?0%以下观望?0%-70%小仓?0%-80%中仓?0%-90%大仓?0%以上全仓
- 动态回撤线：距最高点回撤10%分仓防守
- 半仓操作原则：盈利后才动用另一?

```python
class DynamicPositionStrategy(BaseStrategy):
    """动态仓位管理策?""

    def __init__(self):
        super().__init__("动态仓位管?, "R001")
        self.market_states = [
            MarketState.BULL,
            MarketState.BEAR,
            MarketState.VOLATILE,
            MarketState.YAO,
            MarketState.CHAOS
        ]
        self.parameters = {
            'win_rate_threshold': 0.6,     # 赢面60%以下观望
            'small_position': 0.2,          # 小仓20%
            'medium_position': 0.4,         # 中仓40%
            'large_position': 0.6,          # 大仓60%
            'max_position': 0.8,            # 最?0%
            'drawdown_protection': 0.10,   # 回撤10%防守
        }

    def calculate_position(self, win_probability, market_state):
        """
        根据赢面计算仓位
        """
        params = self.parameters

        if win_probability < params['win_rate_threshold']:
            return 0  # 观望

        elif win_probability < 0.70:
            return params['small_position']

        elif win_probability < 0.80:
            return params['medium_position']

        elif win_probability < 0.90:
            return params['large_position']

        else:
            return params['max_position']

    def check_drawdown_protection(self, current_value, peak_value):
        """
        回撤保护检?
        """
        drawdown = (peak_value - current_value) / peak_value

        if drawdown >= self.parameters['drawdown_protection']:
            return {
                'action': '减仓',
                'ratio': 0.5,
                'reason': f'回撤{drawdown*100:.1f}%，触发保?
            }

        return None
```

### 7.8 新题材判断策?

#### S016: 新题材策?

| 属?| 内容 |
|------|------|
| 策略编号 | S016 |
| 策略名称 | 新题材判?|
| 来源 | 赵老哥 |
| 适用市场 | 妖股周期 |
| 风险等级 | ?|

**量化规则**?
- 有故事：重大政策、业绩拐点、并购重组等
- 大量资金活跃：成交额 > 10?
- 市场认同度高：板块内多个涨停

```python
class NewThemeStrategy(BaseStrategy):
    """新题材策?""

    def __init__(self):
        super().__init__("新题材判?, "S016")
        self.market_states = [MarketState.YAO]
        self.parameters = {
            'min_turnover': 1e9,           # 最小成交额10?
            'min_sector_limit_up': 3,      # 板块最少涨停数
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 成交?> 10?
        if stock_data['turnover'] < params['min_turnover']:
            return None

        # 有故事（重大事项?
        if not stock_data.get('has_major_event', False):
            return None

        # 板块内多个涨?
        sector_limit_up = stock_data.get('sector_limit_up_count', 0)
        if sector_limit_up < params['min_sector_limit_up']:
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.80,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.95,
            target_price=stock_data['close'] * 1.18,
            strategy_name=self.name,
            position_size=0.15,
            holding_period=5
        )
```

### 7.9 游资策略汇总表

| 策略编号 | 策略名称 | 来源 | 适用市场 | 风险 | 核心逻辑 |
|----------|----------|------|----------|------|----------|
| S011 | 只做超强势股 | Asking | 妖股/牛市 | 极高 | 涨幅>5%+成交?10?换手?10% |
| S012 | 守株待兔 | Asking | 熊市/震荡 | ?| 回调至MA5+缩量整理 |
| S013 | 情绪转折 | 炒股养家 | 妖股/情绪?| ?| 赚钱效应+跌停减少+翘板 |
| T011 | 五日线战?| 明王 | 牛市/震荡 | ?| 5日线收复+成交量逆转 |
| M009 | 反弹三定?| 明王 | 熊市/震荡 | ?| 成交量逆转+5日线收复+强势板块 |
| S014 | 二板定龙?| 赵老哥 | 妖股 | 极高 | 高开3-7%+回调不破80%+10点前封板 |
| S015 | 独股一?| 独股一?| 妖股 | 极高 | 满仓一?次日?冲高无量?|
| R001 | 动态仓位管?| 龙飞?| 所?| ?| 赢面仓位+回撤保护 |
| S016 | 新题材判?| 赵老哥 | 妖股 | ?| 有故?成交?10?板块涨停 |
| S017 | 半仓盈利加仓 | Asking | 所?| ?| 半仓盈利>5%后才能加?|
| S018 | 情绪两分?| 炒股养家 | 所?| ?| 极冷区加仓，极热区减?|
| S019 | 情绪六分?| 炒股养家 | 所?| ?| 按情绪分区动态调整仓?|
| S020 | 弱势转折?| 炒股养家 | 妖股/反弹 | 极高 | 连续普跌+领头?连板 |
| R002 | 稳定复利风控 | 退?| 所?| ?| 不大?回撤10%分仓 |
| M010 | 下跌三阶?| 炒股养家 | 熊市/震荡 | ?| ??末三期策略不?|

***

### 7.10 Asking半仓盈利加仓策略

#### S017: 半仓盈利加仓策略

| 属?| 内容 |
|------|------|
| 策略编号 | S017 |
| 策略名称 | 半仓盈利加仓 |
| 来源 | Asking（邱宝裕?|
| 适用市场 | 所有市?|
| 风险等级 | ?|

**量化规则**?
- 半仓操作：初始仓?0%
- 盈利后才能动用另一半资?
- 盈利标准：现有仓位盈?5%
- 加仓后迅速盈利，可再动剩余资?

```python
class HalfPositionAddStrategy(BaseStrategy):
    """半仓盈利加仓策略"""

    def __init__(self):
        super().__init__("半仓盈利加仓", "S017")
        self.market_states = [
            MarketState.BULL, MarketState.VOLATILE,
            MarketState.BEAR, MarketState.YAO
        ]
        self.parameters = {
            'initial_position': 0.50,     # 初始半仓
            'profit_threshold': 0.05,      # 盈利5%才能加仓
            'second_add_threshold': 0.08, # 第二次加仓盈?%
        }
        self.position_phases = {}  # 记录每只股票仓位阶段

    def calculate_position(self, stock_code, current_profit):
        """
        根据盈利计算仓位
        """
        if stock_code not in self.position_phases:
            self.position_phases[stock_code] = 1  # 第一阶段：初始半?

        phase = self.position_phases[stock_code]
        params = self.parameters

        if phase == 1 and current_profit > params['profit_threshold']:
            # 进入第二阶段：全?
            self.position_phases[stock_code] = 2
            return 1.0, "加仓至满?

        elif phase == 2 and current_profit > params['second_add_threshold']:
            # 进入第三阶段：超仓（使用备用资金?
            self.position_phases[stock_code] = 3
            return 1.5, "盈利丰厚，动用备用资?

        elif current_profit < -0.03:
            # 止损：退回第一阶段
            self.position_phases[stock_code] = 1
            return 0.5, "止损，回调半?

        return self.position_phases.get(stock_code, 1) * 0.5, "持有"
```

### 7.11 炒股养家情绪策略

#### S018: 情绪两分法策?

| 属?| 内容 |
|------|------|
| 策略编号 | S018 |
| 策略名称 | 情绪两分?|
| 来源 | 炒股养家 |
| 适用市场 | 所有市?|
| 风险等级 | ?|

**量化规则**?
- 极冷区（上涨家数<40%）：加仓
- 极热区（上涨家数>70%）：减仓
- 参考指标：880005涨跌家数

```python
class SentimentTwoDivisionsStrategy(BaseStrategy):
    """情绪两分法策?""

    def __init__(self):
        super().__init__("情绪两分?, "S018")
        self.market_states = [
            MarketState.BULL, MarketState.VOLATILE,
            MarketState.BEAR, MarketState.CHAOS
        ]
        self.parameters = {
            'hot_threshold': 0.70,        # 70%为极热区
            'cold_threshold': 0.40,        # 40%为极冷区
            'add_position': 0.30,         # 极冷区加?0%
            'reduce_position': 0.20,       # 极热区减?0%
        }

    def get_market_sentiment(self, market_data):
        """
        获取市场情绪
        """
        rise_count = market_data.get('上涨家数', 0)
        total_count = market_data.get('总交易家?, 1)
        ratio = rise_count / total_count if total_count > 0 else 0.5
        return ratio

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters
        sentiment = self.get_market_sentiment(market_data)

        if sentiment > params['hot_threshold']:
            # 极热区：减仓
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.SELL,
                confidence=0.75,
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * 0.97,
                target_price=stock_data['close'] * 1.02,
                strategy_name=self.name,
                position_size=-params['reduce_position'],  # 减仓
                holding_period=1
            )

        elif sentiment < params['cold_threshold']:
            # 极冷区：加仓
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.BUY,
                confidence=0.70,
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * 0.95,
                target_price=stock_data['close'] * 1.15,
                strategy_name=self.name,
                position_size=params['add_position'],
                holding_period=10
            )

        return None  # 正常区间，观?
```

#### S019: 情绪六分法策?

| 属?| 内容 |
|------|------|
| 策略编号 | S019 |
| 策略名称 | 情绪六分?|
| 来源 | 炒股养家 |
| 适用市场 | 所有市?|
| 风险等级 | ?|

**量化规则**?
- 极热区（>66%上涨）：大幅减仓
- 过热区（55%-66%）：逐步减仓
- 微热区（51%-55%）：谨慎
- 微冷区（45%-50%）：观察
- 过冷区（35%-45%）：观望
- 极冷区（<35%）：加仓机会

```python
class SentimentSixDivisionsStrategy(BaseStrategy):
    """情绪六分法策?""

    def __init__(self):
        super().__init__("情绪六分?, "S019")
        self.market_states = [s for s in MarketState]
        self.parameters = {
            'extreme_hot': 0.66,      # 极热?
            'over_hot': 0.55,         # 过热?
            'slight_hot': 0.51,        # 微热?
            'slight_cold': 0.45,       # 微冷?
            'over_cold': 0.35,         # 过冷?
        }

    def get_sentiment_zone(self, sentiment_ratio):
        """
        获取情绪分区
        """
        p = self.parameters
        if sentiment_ratio > p['extreme_hot']:
            return {'zone': '极热?, 'action': '大幅减仓', 'position_change': -0.30}
        elif sentiment_ratio > p['over_hot']:
            return {'zone': '过热?, 'action': '逐步减仓', 'position_change': -0.15}
        elif sentiment_ratio > p['slight_hot']:
            return {'zone': '微热?, 'action': '谨慎持有', 'position_change': 0}
        elif sentiment_ratio > p['slight_cold']:
            return {'zone': '微冷?, 'action': '观察等待', 'position_change': 0}
        elif sentiment_ratio > p['over_cold']:
            return {'zone': '过冷?, 'action': '观望', 'position_change': 0.10}
        else:
            return {'zone': '极冷?, 'action': '加仓机会', 'position_change': 0.25}

    def generate_signal(self, market_data, stock_data, market_state):
        sentiment = market_data.get('上涨家数', 0) / market_data.get('总交易家?, 1)
        zone_info = self.get_sentiment_zone(sentiment)

        if zone_info['position_change'] > 0:
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.BUY,
                confidence=min(zone_info['position_change'] * 2, 0.9),
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * 0.95,
                target_price=stock_data['close'] * 1.12,
                strategy_name=self.name,
                position_size=zone_info['position_change'],
                holding_period=5
            )
        elif zone_info['position_change'] < 0:
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.SELL,
                confidence=min(abs(zone_info['position_change']) * 2, 0.9),
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * 1.02,
                target_price=stock_data['close'] * 0.98,
                strategy_name=self.name,
                position_size=zone_info['position_change'],
                holding_period=1
            )

        return None
```

#### S020: 弱势转折点搏击策?

| 属?| 内容 |
|------|------|
| 策略编号 | S020 |
| 策略名称 | 弱势转折点搏击（涨停启明星） |
| 来源 | 炒股养家 |
| 适用市场 | 妖股周期、反弹市 |
| 风险等级 | 极高 |

**量化规则**?
- 市场连续普跌后出现转折迹?
- 领头羊：在市场最糟糕时逆势抗跌+2连板
- 次日市场企稳反弹确认

```python
class WeakMarketTurnStrategy(BaseStrategy):
    """弱势转折点搏击策?""

    def __init__(self):
        super().__init__("弱势转折?, "S020")
        self.market_states = [MarketState.YAO, MarketState.VOLATILE]
        self.parameters = {
            'consecutive_drop_days': 3,       # 连续下跌天数
            'limit_up_count_threshold': 5,   # 连板股数量稀?
            'space_board_suppressed': True,  # 空间板被压制
        }

    def check_market_turn_signals(self, market_data):
        """
        检查市场转折信?
        """
        # 连续普跌
        consecutive_drops = 0
        for i in range(self.parameters['consecutive_drop_days']):
            if market_data.get(f'd_{i}_rise_ratio', 1) < 0.5:
                consecutive_drops += 1

        if consecutive_drops < self.parameters['consecutive_drop_days']:
            return {'can_turn': False, 'reason': '未出现连续普?}

        # 连板股绝?
        limit_up_count = market_data.get('连板股数?, 100)
        if limit_up_count > self.parameters['limit_up_count_threshold']:
            return {'can_turn': False, 'reason': '连板股仍然活?}

        return {'can_turn': True, 'phase': '等待领头?}

    def select_leader_stock(self, candidate_stocks):
        """
        选择领头?
        条件：在市场最糟糕时逆势抗跌 + 走出2连板
        """
        for stock in candidate_stocks:
            # 逆势抗跌
            if stock['relative_change'] < -0.02:  # 跌幅小于大盘
                continue

            # 走出2连板
            if stock.get('连续板数', 0) >= 2:
                return stock

        return None

    def generate_signal(self, market_data, stock_data, market_state):
        turn_signals = self.check_market_turn_signals(market_data)
        if not turn_signals.get('can_turn', False):
            return None

        leader = self.select_leader_stock([stock_data])
        if not leader:
            return None

        # 次日市场企稳确认
        if market_data.get('index_change', 0) > -0.01:
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.BUY,
                confidence=0.85,
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * 0.92,
                target_price=stock_data['close'] * 1.25,
                strategy_name=self.name,
                position_size=0.15,
                holding_period=5
            )

        return None
```

### 7.12 退神稳定复利风控策?

#### R002: 稳定复利风控策略

| 属?| 内容 |
|------|------|
| 策略编号 | R002 |
| 策略名称 | 稳定复利风控 |
| 来源 | 退?|
| 适用市场 | 所有市?|
| 风险等级 | 低（风控策略?|

**量化规则**?
- 稳定复利，慢就是?
- 设置动态回撤线：距最高点回撤10%，触发分仓防?
- 单只仓位不超50%
- 永不大赔

```python
class StableCompoundStrategy(BaseStrategy):
    """稳定复利风控策略"""

    def __init__(self):
        super().__init__("稳定复利风控", "R002")
        self.market_states = [s for s in MarketState]
        self.parameters = {
            'max_single_position': 0.50,     # 单只最大仓?0%
            'drawdown_line': 0.10,           # 回撤10%分仓防守
            'compound_rate': 0.02,           # 月复合增长目?%
        }

    def check_drawdown_protection(self, current_value, peak_value):
        """
        检查回撤保?
        """
        drawdown = (peak_value - current_value) / peak_value

        if drawdown >= self.parameters['drawdown_line']:
            return {
                'triggered': True,
                'action': '分仓防守',
                'reduce_ratio': 0.5,
                'reason': f'回撤{drawdown*100:.1f}%，触?0%回撤?
            }

        return {'triggered': False}

    def calculate_safe_position(self, current_value, peak_value, target_profit):
        """
        计算安全仓位
        核心：不大赔为生命线
        """
        max_pos = self.parameters['max_single_position']

        # 检查回?
        protection = self.check_drawdown_protection(current_value, peak_value)
        if protection['triggered']:
            return max_pos * protection['reduce_ratio']

        # 根据目标收益和风险确定仓?
        if target_profit > 0.20:  # 高确定性机?
            return max_pos
        elif target_profit > 0.10:  # 中确定?
            return max_pos * 0.7
        else:  # 低确定?
            return max_pos * 0.5

    def validate_not_big_loss(self, current_profit):
        """
        验证不大?
        """
        if current_profit < -0.10:  # 亏损超过10%
            return {
                'valid': False,
                'action': '止损出局',
                'reason': '亏损?0%，触发不大赔红线'
            }
        return {'valid': True}
```

### 7.13 下跌三阶段策?

#### M010: 下跌三阶段策?

| 属?| 内容 |
|------|------|
| 策略编号 | M010 |
| 策略名称 | 下跌三阶?|
| 来源 | 炒股养家 |
| 适用市场 | 熊市、震荡市 |
| 风险等级 | ?|

**量化规则**?
- 初期：做强势股回调反?
- 中期：做超跌?
- 末期：做新强势股（场外资金入场）

```python
class DeclineThreePhasesStrategy(BaseStrategy):
    """下跌三阶段策?""

    def __init__(self):
        super().__init__("下跌三阶?, "M010")
        self.market_states = [MarketState.BEAR, MarketState.VOLATILE]
        self.parameters = {
            'early_phase_days': 5,      # 初期：连续下跌前5?
            'mid_phase_days': 15,       # 中期：连续下?-15?
            'late_phase_signal': 'new_money',  # 末期：新资金入场信号
        }

    def identify_decline_phase(self, market_data):
        """
        识别下跌阶段
        """
        consecutive_drop_days = 0
        for i in range(30):  # 检查最?0?
            if market_data.get(f'd_{i}_change', 0) < 0:
                consecutive_drop_days += 1
            else:
                break

        if consecutive_drop_days <= self.parameters['early_phase_days']:
            return 'early'  # 初期
        elif consecutive_drop_days <= self.parameters['mid_phase_days']:
            return 'mid'   # 中期
        else:
            return 'late'  # 末期

    def generate_signal(self, market_data, stock_data, market_state):
        phase = self.identify_decline_phase(market_data)

        if phase == 'early':
            # 初期：做强势股回调反?
            if stock_data['relative_strength'] > 0.05:  # 相对大盘强势
                return TradingSignal(
                    code=stock_data['code'],
                    signal=SignalType.BUY,
                    confidence=0.65,
                    entry_price=stock_data['close'],
                    stop_loss=stock_data['close'] * 0.96,
                    target_price=stock_data['close'] * 1.08,
                    strategy_name=f"下跌初期-{self.name}",
                    position_size=0.20,
                    holding_period=3
                )

        elif phase == 'mid':
            # 中期：做超跌?
            if stock_data['change_pct'] < -0.15:  # 跌幅超过15%
                return TradingSignal(
                    code=stock_data['code'],
                    signal=SignalType.BUY,
                    confidence=0.60,
                    entry_price=stock_data['close'],
                    stop_loss=stock_data['close'] * 0.93,
                    target_price=stock_data['close'] * 1.10,
                    strategy_name=f"下跌中期-{self.name}",
                    position_size=0.15,
                    holding_period=5
                )

        else:  # late
            # 末期：做新强势股（场外资金入场）
            if market_data.get('new_money_signal', False):  # 新资金入场信?
                if stock_data['volume_ratio'] > 2.0:  # 成交量放?
                    return TradingSignal(
                        code=stock_data['code'],
                        signal=SignalType.BUY,
                        confidence=0.75,
                        entry_price=stock_data['close'],
                        stop_loss=stock_data['close'] * 0.95,
                        target_price=stock_data['close'] * 1.15,
                        strategy_name=f"下跌末期-{self.name}",
                        position_size=0.25,
                        holding_period=5
                    )

        return None
```

***

## 8. 行业精选策略库

> 本章来源：附录V - 科技股选股量化逻辑体系

### 8.1 科技股选股核心因子

| 因子 | 标准 | 量化公式 |
| ------ | ---- | -------- |
| 研发占比 | 研发占比 > 5%(硬科技) OR > 3%(软科技) | 研发费用 / 营业收入  100% |
| 国产替代逻辑 | 卡脖子技术方?| 替代空间 > 100亿人民币 |
| 想象空间 | 技术领先市场容?| 目标市值空?> 5倍当前市?|
| 研发人员占比 | 研发人员 / 总员?| > 20% |
| 专利数量 | 发明专利 | > 100?OR 专利增?> 30% |

### 8.2 科技股估值辅助指?

| 估值方?| 适用场景 | 标准 |
| ---------- | ------------ | ---- |
| PS估?| 尚未盈利的成长期科技?| PS < 10?高速增? OR PS < 5?稳定增长) |
| PB估?| 半导?硬件类科技?| PB < 10?合理) OR PB < 5?低估) |
| EV/Revenue | 云计?SaaS类科技?| EV/Revenue < 10?|

### 8.3 科技股选股Python实现

```python
class TechStockSelector(BaseStrategy):
    """科技股选股策略"""

    def __init__(self):
        super().__init__("科技股精?, "T001")
        self.market_states = [MarketState.BULL, MarketState.VOLATILE]
        self.parameters = {
            'min_rd_ratio_hard': 0.05,      # 硬科技研发占比>5%
            'min_rd_ratio_soft': 0.03,      # 软科技研发占比>3%
            'min_replacement_space': 100e8,  # 替代空间>100?
            'min_target_market_cap': 5.0,   # 目标市值空?5?
            'min_rd_personnel_ratio': 0.20, # 研发人员>20%
            'min_patent_count': 100,         # 专利>100?
            'max_ps': 10,                    # PS估值上?
            'max_pb': 10,                    # PB估值上?
        }

    def evaluate_rd_investment(self, stock_data):
        """
        评估研发投入
        """
        rd_ratio = stock_data['rd_expense'] / stock_data['revenue']

        is_hard_tech = stock_data.get('is_hard_tech', False)
        min_rd = self.parameters['min_rd_ratio_hard'] if is_hard_tech else self.parameters['min_rd_ratio_soft']

        if rd_ratio < min_rd:
            return {'pass': False, 'reason': f'研发占比{rd_ratio*100:.1f}%低于{min_rd*100:.1f}%'}

        return {'pass': True, 'score': min(rd_ratio / min_rd, 2.0)}

    def evaluate_replacement_logic(self, stock_data):
        """
        评估国产替代逻辑
        """
        replacement_space = stock_data.get('replacement_space', 0)
        if replacement_space < self.parameters['min_replacement_space']:
            return {'pass': False, 'reason': f'替代空间{replacement_space/1e8:.0f}?{self.parameters["min_replacement_space"]/1e8:.0f}?}

        return {'pass': True, 'score': min(replacement_space / 500e8, 2.0)}

    def evaluate_valuation(self, stock_data):
        """
        评估估值水?
        """
        is_hard_tech = stock_data.get('is_hard_tech', False)
        max_ps = self.parameters['max_ps']
        max_pb = self.parameters['max_pb']

        ps = stock_data.get('ps_ratio', 100)
        pb = stock_data.get('pb_ratio', 100)

        if is_hard_tech:
            if ps > max_ps:
                return {'pass': False, 'reason': f'PS{ps:.1f}倍超过{max_ps}?}
        else:
            if pb > max_pb:
                return {'pass': False, 'reason': f'PB{pb:.1f}倍超过{max_pb}?}

        return {'pass': True, 'score': 1.0}

    def generate_signal(self, market_data, stock_data, market_state):
        """
        生成科技股选股信号
        """
        results = []
        results.append(('研发投入', self.evaluate_rd_investment(stock_data)))
        results.append(('替代逻辑', self.evaluate_replacement_logic(stock_data)))
        results.append(('估?, self.evaluate_valuation(stock_data)))

        all_pass = all(r[1]['pass'] for r in results)
        if not all_pass:
            failed = [r[0] for r in results if not r[1]['pass']]
            return None

        total_score = sum(r[1]['score'] for r in results)
        confidence = min(total_score / 5.0, 1.0)

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=confidence,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.90,
            target_price=stock_data['close'] * 1.30,
            strategy_name=self.name,
            position_size=0.15,
            holding_period=20
        )
```

### 8.4 科技股行业分?

| 科技类别 | 代表行业 | 硬科技/软科技 | 估值偏?|
|----------|----------|----------------|----------|
| 半导?| 芯片设计/制?设备 | 硬科技 | PS/PB |
| 新能?| 光伏/锂电/储能 | 硬科技 | PS |
| 云计?| SaaS/IaaS | 软科技 | PS/EV |
| 人工智能 | 算法/应用 | 软科技 | PS |
| 生物医药 | 创新?器械 | 硬科技 | PS/PB |

***

## 9. 事件驱动策略?

> 本章来源：全网搜索补?- 2024-2025年主流事件驱动量化策?

### 9.1 业绩超预期策?

#### E001: 财报业绩超预期策?

| 属?| 内容 |
|------|------|
| 策略编号 | E001 |
| 策略名称 | 业绩超预期策?|
| 适用市场 | 所有市?|
| 风险等级 | ?|

**量化规则**?
- 业绩公告后净利润增?> 分析师预?0%以上
- 营收增?> 20%
- 毛利率环比提?
- 股价跳空高开 > 3%

```python
class EarningsSurpriseStrategy(BaseStrategy):
    """业绩超预期策?""

    def __init__(self):
        super().__init__("业绩超预?, "E001")
        self.market_states = [MarketState.BULL, MarketState.VOLATILE]
        self.parameters = {
            'profit_beat_threshold': 0.10,    # 业绩超预?0%
            'min_revenue_growth': 0.20,         # 营收增?20%
            'min_gap_open': 0.03,               # 跳空高开>3%
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 业绩超预?
        actual_profit = stock_data.get('actual_profit_growth', 0)
        expected_profit = stock_data.get('expected_profit_growth', 0)
        if actual_profit < expected_profit * (1 + params['profit_beat_threshold']):
            return None

        # 营收增?
        revenue_growth = stock_data.get('revenue_growth', 0)
        if revenue_growth < params['min_revenue_growth']:
            return None

        # 跳空高开
        gap_open = stock_data.get('gap_open_ratio', 0)
        if gap_open < params['min_gap_open']:
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.75,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.95,
            target_price=stock_data['close'] * 1.15,
            strategy_name=self.name,
            position_size=0.15,
            holding_period=10
        )
```

### 9.2 并购重组策略

#### E002: 并购重组事件策略

| 属?| 内容 |
|------|------|
| 策略编号 | E002 |
| 策略名称 | 并购重组事件策略 |
| 适用市场 | 牛市、主题炒?|
| 风险等级 | ?|

**量化规则**?
- 上市公司发布并购重组公告
- 标的资产与主业相关度?
- 估值溢价合理（PE<20?
- 股价尚未反映（停牌前涨幅<50%?

```python
class M\&AStrategy(BaseStrategy):
    """并购重组策略"""

    def __init__(self):
        super().__init__("并购重组", "E002")
        self.market_states = [MarketState.BULL, MarketState.YAO]
        self.parameters = {
            'min_relatedness': 0.7,           # 资产相关?70%
            'max_pe_ratio': 20,               # PE<20
            'max_prior_return': 0.50,        # 停牌前涨?50%
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 并购公告
        if not stock_data.get('has_ma_announcement', False):
            return None

        # 资产相关?
        relatedness = stock_data.get('asset_relatedness', 0)
        if relatedness < params['min_relatedness']:
            return None

        # 估值合?
        pe_ratio = stock_data.get('pe_ratio', 100)
        if pe_ratio > params['max_pe_ratio']:
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.80,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.90,
            target_price=stock_data['close'] * 1.25,
            strategy_name=self.name,
            position_size=0.10,
            holding_period=15
        )
```

### 9.3 高管增持策略

#### E003: 高管/大股东增持策?

| 属?| 内容 |
|------|------|
| 策略编号 | E003 |
| 策略名称 | 高管增持策略 |
| 适用市场 | 所有市?|
| 风险等级 | ?|

**量化规则**?
- 高管或大股东增持 > 1000万元
- 增持比例 > 0.5%
- 增持后持股比?> 30%
- 增持时股价相对低?

```python
class InsiderBuyStrategy(BaseStrategy):
    """高管增持策略"""

    def __init__(self):
        super().__init__("高管增持", "E003")
        self.market_states = [s for s in MarketState]
        self.parameters = {
            'min_amount': 1000e4,             # 增持>1000?
            'min_ratio': 0.005,              # 增持比例>0.5%
            'min_hold_ratio': 0.30,          # 增持后持?30%
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 增持金额
        buy_amount = stock_data.get('insider_buy_amount', 0)
        if buy_amount < params['min_amount']:
            return None

        # 增持比例
        buy_ratio = stock_data.get('insider_buy_ratio', 0)
        if buy_ratio < params['min_ratio']:
            return None

        # 增持后持?
        hold_ratio = stock_data.get('insider_hold_ratio', 0)
        if hold_ratio < params['min_hold_ratio']:
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.70,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.93,
            target_price=stock_data['close'] * 1.12,
            strategy_name=self.name,
            position_size=0.15,
            holding_period=20
        )
```

### 9.4 事件驱动策略汇总表

| 策略编号 | 策略名称 | 适用市场 | 风险 | 核心逻辑 |
|----------|----------|----------|------|----------|
| E001 | 业绩超预?| 牛市/震荡 | ?| 业绩增?预期+跳空高开 |
| E002 | 并购重组 | 牛市/妖股 | ?| 资产相关+估值合?|
| E003 | 高管增持 | 所?| ?| 增持金额>1000?比例>0.5% |

***

## 10. 价值与红利策略?

> 本章来源：全网搜索补?- 2024年主流价值投资量化策?

### 10.1 高股息策?

#### V001: 稳定高股息策?

| 属?| 内容 |
|------|------|
| 策略编号 | V001 |
| 策略名称 | 稳定高股息策?|
| 适用市场 | 所有市场（防御性） |
| 风险等级 | ?|

**量化规则**?
- 股息?> 3%
- 连续3年分?
- 利润增?> 5%
- PE < 20?

```python
class HighDividendStrategy(BaseStrategy):
    """高股息策?""

    def __init__(self):
        super().__init__("高股?, "V001")
        self.market_states = [s for s in MarketState]
        self.parameters = {
            'min_dividend_yield': 0.03,      # 股息?3%
            'min_consecutive_years': 3,       # 连续3年分?
            'min_profit_growth': 0.05,        # 利润增?5%
            'max_pe': 20,                     # PE<20
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 股息?
        dividend_yield = stock_data.get('dividend_yield', 0)
        if dividend_yield < params['min_dividend_yield']:
            return None

        # 连续分红
        consecutive = stock_data.get('consecutive_dividend_years', 0)
        if consecutive < params['min_consecutive_years']:
            return None

        # 估?
        pe = stock_data.get('pe_ratio', 100)
        if pe > params['max_pe']:
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.75,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.90,
            target_price=stock_data['close'] * 1.10,
            strategy_name=self.name,
            position_size=0.20,
            holding_period=30
        )
```

### 10.2 困境反转策略

#### V002: 困境反转策略

| 属?| 内容 |
|------|------|
| 策略编号 | V002 |
| 策略名称 | 困境反转策略 |
| 适用市场 | 震荡市、熊市末?|
| 风险等级 | 中高 |

**量化规则**?
- PE处于历史低位?20%分位?
- 营收连续2季度回升
- 行业景气度开始回?
- 机构开始上调评?

```python
class TurnaroundStrategy(BaseStrategy):
    """困境反转策略"""

    def __init__(self):
        super().__init__("困境反转", "V002")
        self.market_states = [MarketState.VOLATILE, MarketState.BEAR]
        self.parameters = {
            'pe_percentile': 0.20,           # PE<20%分位
            'min_revenue_growth_quarter': 2,  # 营收连续回升季度?
            'upgrade_count': 1,               # 机构上调评级次数
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # PE低位
        pe_percentile = stock_data.get('pe_percentile', 1.0)
        if pe_percentile > params['pe_percentile']:
            return None

        # 营收回升
        revenue_growth_quarter = stock_data.get('revenue_growth_quarters', 0)
        if revenue_growth_quarter < params['min_revenue_growth_quarter']:
            return None

        # 机构上调
        upgrade_count = stock_data.get('institution_upgrade_count', 0)
        if upgrade_count < params['upgrade_count']:
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.70,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.92,
            target_price=stock_data['close'] * 1.20,
            strategy_name=self.name,
            position_size=0.15,
            holding_period=25
        )
```

### 10.3 ESG量化选股策略

#### V003: ESG量化选股策略

| 属?| 内容 |
|------|------|
| 策略编号 | V003 |
| 策略名称 | ESG量化选股策略 |
| 适用市场 | 牛市、长期投?|
| 风险等级 | 中低 |

**量化规则**?
- ESG评分 > A?
- 环境评分 > 80?
- 社会评分 > 70?
- 公司治理评分 > 70?

```python
class ESGScoreStrategy(BaseStrategy):
    """ESG量化选股策略"""

    def __init__(self):
        super().__init__("ESG选股", "V003")
        self.market_states = [MarketState.BULL, MarketState.VOLATILE]
        self.parameters = {
            'min_esg_rating': 'A',            # ESG评级>A
            'min_env_score': 80,             # 环境>80
            'min_social_score': 70,          # 社会>70
            'min_governance_score': 70,      # 治理>70
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # ESG评级
        esg_rating = stock_data.get('esg_rating', 'C')
        if esg_rating < params['min_esg_rating']:
            return None

        # 环境评分
        env_score = stock_data.get('environmental_score', 0)
        if env_score < params['min_env_score']:
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.70,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.92,
            target_price=stock_data['close'] * 1.15,
            strategy_name=self.name,
            position_size=0.15,
            holding_period=30
        )
```

### 10.4 价值红利策略汇总表

| 策略编号 | 策略名称 | 适用市场 | 风险 | 核心逻辑 |
|----------|----------|----------|------|----------|
| V001 | 稳定高股?| 所有（防御?| ?| 股息?3%+连分3?PE<20 |
| V002 | 困境反转 | 震荡/熊市 | 中高 | PE低位+营收回升+机构上调 |
| V003 | ESG量化选股 | 牛市/长期 | 中低 | ESG评级A+各维度达标准 |

***

## 11. Smart Money与北向资金策略库

> 本章来源：全网搜索补?- 2024年主力资金追踪量化策?

### 11.1 主力资金动向策略

#### M001: 主力资金连续流入策略

| 属?| 内容 |
|------|------|
| 策略编号 | M001 |
| 策略名称 | 主力资金连续流入策略 |
| 适用市场 | 所有市?|
| 风险等级 | ?|

**量化规则**?
- 主力资金连续净流入 > 3?
- 3日主力净流入 > 5?
- 股价涨幅 < 5%（尚未启动）
- 换手率温和放?

```python
class MainForceFlowStrategy(BaseStrategy):
    """主力资金连续流入策略"""

    def __init__(self):
        super().__init__("主力资金流入", "M001")
        self.market_states = [MarketState.BULL, MarketState.VOLATILE]
        self.parameters = {
            'min_consecutive_days': 3,        # 连续流入3?
            'min_net_flow_3d': 5e8,           # 3日净流入>5?
            'max_price_rise': 0.05,          # 涨幅<5%
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 连续净流入
        consecutive_days = stock_data.get('main_force_consecutive_days', 0)
        if consecutive_days < params['min_consecutive_days']:
            return None

        # 3日净流入
        net_flow_3d = stock_data.get('main_force_net_flow_3d', 0)
        if net_flow_3d < params['min_net_flow_3d']:
            return None

        # 涨幅控制
        price_rise = stock_data.get('change_pct', 0)
        if price_rise > params['max_price_rise']:
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.75,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.95,
            target_price=stock_data['close'] * 1.15,
            strategy_name=self.name,
            position_size=0.15,
            holding_period=15
        )
```

### 11.2 北向资金策略

#### M002: 北向资金持仓策略

| 属?| 内容 |
|------|------|
| 策略编号 | M002 |
| 策略名称 | 北向资金持仓策略 |
| 适用市场 | 所有市?|
| 风险等级 | ?|

**量化规则**?
- 北向持股比例 > 5%
- 北向持股比例持续提升
- 股价处于相对低位
- 行业配置偏好消费/金融

```python
class NorthMoneyStrategy(BaseStrategy):
    """北向资金策略"""

    def __init__(self):
        super().__init__("北向资金", "M002")
        self.market_states = [MarketState.BULL, MarketState.VOLATILE]
        self.parameters = {
            'min_hold_ratio': 0.05,          # 持股比例>5%
            'min_increase_rate': 0.10,        # 持股比例提升>10%
            'sector_preference': ['消费', '金融'],  # 偏好行业
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 北向持股
        hold_ratio = stock_data.get('north_hold_ratio', 0)
        if hold_ratio < params['min_hold_ratio']:
            return None

        # 持股提升
        increase_rate = stock_data.get('north_hold_increase_rate', 0)
        if increase_rate < params['min_increase_rate']:
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.70,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.93,
            target_price=stock_data['close'] * 1.12,
            strategy_name=self.name,
            position_size=0.15,
            holding_period=20
        )
```

### 11.3 北向资金流入策略

#### M003: 北向资金连续流入策略

| 属?| 内容 |
|------|------|
| 策略编号 | M003 |
| 策略名称 | 北向资金连续流入策略 |
| 适用市场 | 外资主导行情 |
| 风险等级 | ?|

**量化规则**?
- 北向资金连续净流入 > 5?
- 期间累计净流入 > 10?
- 大盘处于上升通道
- 重点配置沪深300成分?

```python
class NorthMoneyInflowStrategy(BaseStrategy):
    """北向资金连续流入策略"""

    def __init__(self):
        super().__init__("北向资金流入", "M003")
        self.market_states = [MarketState.BULL]
        self.parameters = {
            'min_consecutive_days': 5,        # 连续5日净流入
            'min_total_flow': 10e8,           # 累计流入>10?
            'only_hs300': True,               # 仅沪?00成分
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 北向连续流入
        consecutive = stock_data.get('north_consecutive_days', 0)
        if consecutive < params['min_consecutive_days']:
            return None

        # 累计流入
        total_flow = stock_data.get('north_total_flow_5d', 0)
        if total_flow < params['min_total_flow']:
            return None

        # 仅沪?00
        if params['only_300'] and not stock_data.get('is_hs300', False):
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.80,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.95,
            target_price=stock_data['close'] * 1.18,
            strategy_name=self.name,
            position_size=0.20,
            holding_period=15
        )
```

### 11.4 Smart Money策略汇总表

| 策略编号 | 策略名称 | 适用市场 | 风险 | 核心逻辑 |
|----------|----------|----------|------|----------|
| M001 | 主力资金连续流入 | 牛市/震荡 | ?| 主力连流3?净流入>5?|
| M002 | 北向持仓策略 | 所?| ?| 北向持股>5%+比例提升 |
| M003 | 北向资金连续流入 | 牛市 | ?| 北向连流5?累计>10?|

***

## 12. 行业轮动与统计套利策略库

> 本章来源：全网搜索补?- 2024年板块轮动与套利量化策略

### 12.1 行业轮动策略

#### S001: 板块动量轮动策略

| 属?| 内容 |
|------|------|
| 策略编号 | S001 |
| 策略名称 | 板块动量轮动策略 |
| 适用市场 | 结构性行?|
| 风险等级 | ?|

**量化规则**?
- 行业指数20日动量排名Top20%
- 行业成交量放?> 1.5?
- 行业资金净流入
- 龙头股已启动

```python
class SectorMomentumRotationStrategy(BaseStrategy):
    """板块动量轮动策略"""

    def __init__(self):
        super().__init__("板块动量轮动", "S001")
        self.market_states = [MarketState.BULL, MarketState.VOLATILE]
        self.parameters = {
            'momentum_rank_percentile': 0.20, # 动量排名Top20%
            'min_volume_ratio': 1.5,           # 量比>1.5
            'min_net_flow': 0,                 # 资金净流入
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 行业动量排名
        momentum_rank = stock_data.get('sector_momentum_rank', 1.0)
        if momentum_rank > params['momentum_rank_percentile']:
            return None

        # 量比放大
        volume_ratio = stock_data.get('sector_volume_ratio', 1.0)
        if volume_ratio < params['min_volume_ratio']:
            return None

        # 资金净流入
        net_flow = stock_data.get('sector_net_flow', 0)
        if net_flow < params['min_net_flow']:
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.70,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.95,
            target_price=stock_data['close'] * 1.12,
            strategy_name=self.name,
            position_size=0.15,
            holding_period=15
        )
```

### 12.2 配对交易策略

#### S002: 统计套利配对交易

| 属?| 内容 |
|------|------|
| 策略编号 | S002 |
| 策略名称 | 配对交易策略 |
| 适用市场 | 震荡?|
| 风险等级 | ?|

**量化规则**?
- 两股票历史相关?> 0.8
- 当前价差偏离均?> 2倍标准差
- 预期价差回归
- 行业/业务高度相似

```python
class PairTradingStrategy(BaseStrategy):
    """配对交易策略"""

    def __init__(self):
        super().__init__("配对交易", "S002")
        self.market_states = [MarketState.VOLATILE, MarketState.CHAOS]
        self.parameters = {
            'min_correlation': 0.80,           # 历史相关?0.8
            'z_score_threshold': 2.0,         # 价差偏离>2倍标准差
            'min_halflife': 5,                 # 回归半周?5?
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 相关?
        correlation = stock_data.get('pair_correlation', 0)
        if correlation < params['min_correlation']:
            return None

        # 价差Z-score
        z_score = stock_data.get('spread_z_score', 0)
        if abs(z_score) < params['z_score_threshold']:
            return None

        # 判断多空方向
        if z_score > 0:
            # 价差过高，做空价差（卖stock_a买stock_b?
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.SELL,
                confidence=0.75,
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * 1.03,
                target_price=stock_data['close'] * 0.98,
                strategy_name=self.name,
                position_size=0.10,
                holding_period=10
            )
        else:
            # 价差过低，做多价?
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.BUY,
                confidence=0.75,
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * 0.97,
                target_price=stock_data['close'] * 1.05,
                strategy_name=self.name,
                position_size=0.10,
                holding_period=10
            )
```

### 12.3 行业轮动与套利策略汇总表

| 策略编号 | 策略名称 | 适用市场 | 风险 | 核心逻辑 |
|----------|----------|----------|------|----------|
| S001 | 板块动量轮动 | 牛市/结构 | ?| 动量Top20%+量比>1.5 |
| S002 | 配对交易 | 震荡 | ?| 相关>0.8+价差偏离2σ |

***

## 13. 小市值与指数增强策略?

> 本章来源：全网搜索补?- 2024年小市值与指数增强量化策略

### 13.1 小市值低波动策略

#### S003: 小市值低波动策略

| 属?| 内容 |
|------|------|
| 策略编号 | S003 |
| 策略名称 | 小市值低波动策略 |
| 适用市场 | 结构性行情、中小票活跃?|
| 风险等级 | 中高 |

**量化规则**?
- 全市场股票池剔除ST、上市不??
- 选取过去20日波动率最低的100?
- 3个月涨幅最小的50?
- 因子做市值行业中性化处理

```python
class SmallCapLowVolatilityStrategy(BaseStrategy):
    """小市值低波动策略"""

    def __init__(self):
        super().__init__("小市值低波动", "S003")
        self.market_states = [MarketState.VOLATILE, MarketState.BULL]
        self.parameters = {
            'min_listed_days': 250,           # 上市??
            'top_volatility_percentile': 0.20, # 波动率最?0%
            'top_return_percentile': 0.15,     # 涨幅最?5%
            'stock_pool_size': 100,           # 选取100?
        }

    def filter_stocks(self, stock_data):
        """过滤股票?""
        filtered = []

        for stock in stock_data:
            # 剔除ST
            if stock.get('is_st', False):
                continue
            # 剔除上市不满1?
            if stock.get('listed_days', 0) < self.parameters['min_listed_days']:
                continue
            filtered.append(stock)

        return filtered

    def rank_by_volatility(self, stocks):
        """按波动率排名"""
        ranked = sorted(stocks,
                       key=lambda x: x.get('volatility_20d', float('inf')),
                       reverse=False)
        return ranked[:self.parameters['stock_pool_size']]

    def rank_by_return(self, stocks):
        """按涨幅排?""
        ranked = sorted(stocks,
                       key=lambda x: x.get('return_3m', 0),
                       reverse=False)
        return ranked[:50]

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 过滤
        filtered = self.filter_stocks(stock_data)

        # 低波动排?
        low_vol = self.rank_by_volatility(filtered)

        # 小涨幅排?
        low_return = self.rank_by_return(filtered)

        # 取交?
        candidates = [s for s in low_vol if s in low_return]

        if not candidates:
            return None

        stock = candidates[0]

        return TradingSignal(
            code=stock['code'],
            signal=SignalType.BUY,
            confidence=0.70,
            entry_price=stock['close'],
            stop_loss=stock['close'] * 0.92,
            target_price=stock['close'] * 1.15,
            strategy_name=self.name,
            position_size=0.10,
            holding_period=20
        )
```

### 13.2 指数增强策略

#### I001: 中证2000指数增强策略

| 属?| 内容 |
|------|------|
| 策略编号 | I001 |
| 策略名称 | 中证2000指数增强策略 |
| 适用市场 | 结构性行情、小盘股活跃 |
| 风险等级 | ?|

**量化规则**?
- 对标中证2000指数
- 行业权重与指数相?
- 风格因子控制市值、行业偏?
- 追求稳定超额收益

```python
class IndexEnhancementStrategy(BaseStrategy):
    """指数增强策略"""

    def __init__(self):
        super().__init__("指数增强", "I001")
        self.market_states = [MarketState.BULL, MarketState.VOLATILE]
        self.parameters = {
            'target_index': '中证2000',        # 目标指数
            'max_industry_deviation': 0.02,   # 行业偏离<2%
            'max_size_deviation': 0.10,        # 市值偏?10%
            'min_alpha_factor': 0.01,         # Alpha因子阈?
            'max_stock_weight': 0.03,          # 单只权重<3%
        }

    def calculate_industry_weight(self, stock_data, target_index_weights):
        """计算行业权重"""
        stock_industry_weights = {}

        for stock in stock_data:
            industry = stock.get('industry', 'Unknown')
            weight = stock.get('weight', 0)
            stock_industry_weights[industry] = stock_industry_weights.get(industry, 0) + weight

        return stock_industry_weights

    def check_deviation(self, current_weights, target_weights):
        """检查偏离度"""
        for industry, target in target_weights.items():
            current = current_weights.get(industry, 0)
            deviation = abs(current - target)
            if deviation > self.parameters['max_industry_deviation']:
                return False, f"{industry}偏离{deviation*100:.1f}%超过2%"

        return True, "偏离度合?

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 计算当前持仓行业权重
        current_industry = self.calculate_industry_weight(stock_data, {})

        # 获取指数目标权重
        target_weights = market_data.get(f'{params["target_index"]}_weights', {})

        # 检查偏?
        valid, msg = self.check_deviation(current_industry, target_weights)
        if not valid:
            return None

        # 选取Alpha因子最强的股票
        candidates = sorted(stock_data,
                           key=lambda x: x.get('alpha_factor', 0),
                           reverse=True)

        if not candidates or candidates[0].get('alpha_factor', 0) < params['min_alpha_factor']:
            return None

        stock = candidates[0]

        return TradingSignal(
            code=stock['code'],
            signal=SignalType.BUY,
            confidence=0.75,
            entry_price=stock['close'],
            stop_loss=stock['close'] * 0.95,
            target_price=stock['close'] * 1.10,
            strategy_name=self.name,
            position_size=0.15,
            holding_period=15
        )
```

### 13.3 小市值与指数增强策略汇总表

| 策略编号 | 策略名称 | 适用市场 | 风险 | 核心逻辑 |
|----------|----------|----------|------|----------|
| S003 | 小市值低波动 | 震荡/结构 | 中高 | 波动率最?涨幅最?|
| I001 | 中证2000指数增强 | 牛市/小盘 | ?| 对标指数+稳定超额 |

***

## 14. 可转债与多因子策略库

> 本章来源：全网搜索补?- 2024年可转债量化与择时策略

### 14.1 可转债量化策?

#### C001: 可转债多策略

| 属?| 内容 |
|------|------|
| 策略编号 | C001 |
| 策略名称 | 可转债量化多策略 |
| 适用市场 | 所有市场（低波动环境） |
| 风险等级 | 低中 |

**量化规则**?
- 转股溢价?< 20%
- 纯债溢价率 < 30%
- 剩余规模 < 5?
- 正股波动?> 30%

```python
class ConvertibleBondStrategy(BaseStrategy):
    """可转债量化策?""

    def __init__(self):
        super().__init__("可转债多策略", "C001")
        self.market_states = [MarketState.VOLATILE, MarketState.CHAOS]
        self.parameters = {
            'max_conversion_premium': 0.20,    # 转股溢价<20%
            'max_pure_bond_premium': 0.30,     # 纯债溢?30%
            'max_scale': 5e8,                   # 剩余规模<5?
            'min_stock_volatility': 0.30,       # 正股波动>30%
        }

    def evaluate_conversion_opportunity(self, cb_data):
        """评估转股机会"""
        params = self.parameters

        # 转股溢价?
        conv_premium = cb_data.get('conversion_premium', 1.0)
        if conv_premium > params['max_conversion_premium']:
            return False, f"转股溢价{conv_premium*100:.1f}%过高"

        # 纯债溢价率
        bond_premium = cb_data.get('pure_bond_premium', 1.0)
        if bond_premium > params['max_pure_bond_premium']:
            return False, f"纯债溢价{bond_premium*100:.1f}%过高"

        # 规模
        scale = cb_data.get('cb_scale', float('inf'))
        if scale > params['max_scale']:
            return False, f"规模{scale/1e8:.1f}亿过?

        # 正股波动
        stock_vol = cb_data.get('stock_volatility', 0)
        if stock_vol < params['min_stock_volatility']:
            return False, f"正股波动{stock_vol*100:.1f}%不足"

        return True, "满足条件"

    def generate_signal(self, market_data, stock_data, market_state):
        valid, msg = self.evaluate_conversion_opportunity(stock_data)
        if not valid:
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.75,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.95,
            target_price=stock_data['close'] * 1.12,
            strategy_name=self.name,
            position_size=0.15,
            holding_period=15
        )
```

### 14.2 多因子择时策?

#### T012: 多因子机器学习择时策?

| 属?| 内容 |
|------|------|
| 策略编号 | T012 |
| 策略名称 | 多因子机器学习择?|
| 适用市场 | 所有市?|
| 风险等级 | ?|

**量化规则**?
- 选取有效择时因子：动?估?情绪/趋势
- 机器学习模型预测收益?
- 预期收益?> 阈值时做多
- DTW择时策略年化36%

```python
class MultiFactorTimingStrategy(BaseStrategy):
    """多因子择时策?""

    def __init__(self):
        super().__init__("多因子择?, "T012")
        self.market_states = [MarketState.BULL, MarketState.VOLATILE, MarketState.BEAR]
        self.parameters = {
            'min_return_threshold': 0.02,      # 预期收益>2%
            'max_drawdown_limit': 0.15,        # 最大回撤限?5%
            'features': ['momentum', 'valuation', 'sentiment', 'trend'],
            'model_type': 'random_forest',     # 随机森林模型
        }

    def extract_features(self, market_data):
        """提取择时因子"""
        features = {}

        # 动量因子
        features['momentum'] = market_data.get('index_return_20d', 0)

        # 估值因?
        features['valuation'] = market_data.get('pe_percentile', 0.5)

        # 情绪因子
        features['sentiment'] = market_data.get('sentiment_index', 0.5)

        # 趋势因子
        features['trend'] = market_data.get('adx', 0)

        return features

    def predict_return(self, features, model):
        """预测未来收益?""
        feature_vector = [features[f] for f in self.parameters['features']]
        return model.predict([feature_vector])[0]

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 提取因子
        features = self.extract_features(market_data)

        # 预测收益（简化版?
        predicted_return = sum(features.values()) / len(features)

        # 收益阈?
        if predicted_return < params['min_return_threshold']:
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.SELL,
                confidence=0.60,
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * 1.02,
                target_price=stock_data['close'] * 0.98,
                strategy_name=self.name,
                position_size=-0.10,
                holding_period=5
            )

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=min(predicted_return * 10, 0.9),
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.95,
            target_price=stock_data['close'] * (1 + predicted_return),
            strategy_name=self.name,
            position_size=0.15,
            holding_period=10
        )
```

### 14.3 行业配置策略

#### S004: 多维度行业配置策?

| 属?| 内容 |
|------|------|
| 策略编号 | S004 |
| 策略名称 | 多维度行业配置策?|
| 适用市场 | 牛市、震荡市 |
| 风险等级 | ?|

**量化规则**?
- 动量维度?0日行业动量排?
- 估值维度：PE历史分位?
- 情绪维度：行业资金净流入
- 景气维度：行业净利润增?

```python
class MultiDimensionalSectorStrategy(BaseStrategy):
    """多维度行业配置策?""

    def __init__(self):
        super().__init__("多维度行业配?, "S004")
        self.market_states = [MarketState.BULL, MarketState.VOLATILE]
        self.parameters = {
            'momentum_weight': 0.30,           # 动量权重30%
            'valuation_weight': 0.25,           # 估值权?5%
            'sentiment_weight': 0.25,           # 情绪权重25%
            'fundamental_weight': 0.20,        # 基本面权?0%
            'top_sectors': 3,                  # 配置?行业
        }

    def calculate_dimension_score(self, sector, dimension):
        """计算单维度得?""
        if dimension == 'momentum':
            return sector.get('momentum_20d_rank', 0.5)
        elif dimension == 'valuation':
            return 1 - sector.get('pe_percentile', 0.5)  # 低估值高?
        elif dimension == 'sentiment':
            return sector.get('net_flow_rank', 0.5)
        elif dimension == 'fundamental':
            return sector.get('profit_growth_rank', 0.5)
        return 0.5

    def calculate_composite_score(self, sector):
        """计算综合得分"""
        params = self.parameters
        dims = ['momentum', 'valuation', 'sentiment', 'fundamental']
        weights = [params['momentum_weight'], params['valuation_weight'],
                   params['sentiment_weight'], params['fundamental_weight']]

        score = sum(self.calculate_dimension_score(sector, d) * w
                    for d, w in zip(dims, weights))
        return score

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        # 获取所有行?
        sectors = market_data.get('sectors', [])

        # 计算综合得分
        scored = [(s, self.calculate_composite_score(s)) for s in sectors]

        # 排序
        ranked = sorted(scored, key=lambda x: x[1], reverse=True)

        # 取前N
        top_sectors = [s[0]['industry'] for s in ranked[:params['top_sectors']]]

        # 检查个股所属行?
        stock_industry = stock_data.get('industry', '')
        if stock_industry not in top_sectors:
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.70,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.95,
            target_price=stock_data['close'] * 1.12,
            strategy_name=self.name,
            position_size=0.15,
            holding_period=15
        )
```

### 14.4 可转债与多因子策略汇总表

| 策略编号 | 策略名称 | 适用市场 | 风险 | 核心逻辑 |
|----------|----------|----------|------|----------|
| C001 | 可转债多策略 | 震荡/低波?| 低中 | 转股溢价<20%+规模<5?|
| T012 | 多因子择?| 所?| ?| 机器学习+动量/估?情绪 |
| S004 | 多维度行业配?| 牛市/震荡 | ?| 动量+估?情绪+基本?|

***

## 15. CTA商品期货策略?

> 本章来源：全网搜索补?- 2024年量化CTA策略

### 15.1 趋势追踪CTA策略

#### CTA001: 商品期货趋势追踪策略

| 属?| 内容 |
|------|------|
| 策略编号 | CTA001 |
| 策略名称 | 商品期货趋势追踪策略 |
| 适用市场 | 商品期货、股指期?|
| 风险等级 | 中高 |

**量化规则**?
- 20日均?> 60日均线，多头趋势
- ATR通道突破上轨做多
- 趋势反转止损

```python
class CTATrendFollowingStrategy(BaseStrategy):
    """CTA趋势追踪策略"""

    def __init__(self):
        super().__init__("CTA趋势追踪", "CTA001")
        self.market_states = [MarketState.BULL, MarketState.VOLATILE]
        self.parameters = {
            'fast_ma': 20,                # 快速均?
            'slow_ma': 60,                # 慢速均?
            'atr_period': 20,             # ATR周期
            'atr_multiplier': 2.0,        # ATR倍数
            'stop_loss_atr': 3.0,         # 止损ATR
        }

    def calculate_trend_signal(self, data):
        """计算趋势信号"""
        fast_ma = data['close'].rolling(self.parameters['fast_ma']).mean()
        slow_ma = data['close'].rolling(self.parameters['slow_ma']).mean()

        if fast_ma > slow_ma:
            return 'LONG'
        elif fast_ma < slow_ma:
            return 'SHORT'
        return 'NEUTRAL'

    def calculate_entry_price(self, data):
        """计算入场价格"""
        atr = self.calculate_atr(data, self.parameters['atr_period'])
        upper_band = data['close'].iloc[-1] + atr * self.parameters['atr_multiplier']
        return upper_band

    def calculate_stop_loss(self, entry_price, atr):
        """计算止损价格"""
        return entry_price - atr * self.parameters['stop_loss_atr']

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        trend = self.calculate_trend_signal(stock_data)
        atr = self.calculate_atr(stock_data, params['atr_period'])
        entry_price = self.calculate_entry_price(stock_data)

        if trend == 'LONG':
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.BUY,
                confidence=0.75,
                entry_price=entry_price,
                stop_loss=self.calculate_stop_loss(entry_price, atr),
                target_price=entry_price * 1.05,
                strategy_name=self.name,
                position_size=0.15,
                holding_period=20
            )

        return None
```

### 15.2 CTA策略汇总表

| 策略编号 | 策略名称 | 适用市场 | 风险 | 核心逻辑 |
|----------|----------|----------|------|----------|
| CTA001 | 趋势追踪CTA | 商品/股指期货 | 中高 | 均线金叉+ATR突破 |

***

## 16. 高频交易策略?

> 本章来源：全网搜索补?- 2024年高频量化交易策?

### 16.1 日内T+0策略

#### HFT001: 股票日内T+0策略

| 属?| 内容 |
|------|------|
| 策略编号 | HFT001 |
| 策略名称 | 日内T+0策略 |
| 适用市场 | A股（底仓支持?|
| 风险等级 | ?|

**量化规则**?
- 持有现货底仓
- 15分钟K线均值回?
- 日内高点卖、低点买
- 严格执行止盈止损

```python
class IntradayT0Strategy(BaseStrategy):
    """日内T+0策略"""

    def __init__(self):
        super().__init__("日内T+0", "HFT001")
        self.market_states = [MarketState.BULL, MarketState.VOLATILE]
        self.parameters = {
            'kline_period': 15,             # 15分钟K?
            'mean_reversion_threshold': 0.01,  # 均值回复阈?%
            'profit_target': 0.005,         # 止盈0.5%
            'loss_limit': 0.003,            # 止损0.3%
            'max_daily_trades': 10,         # 每日最?0?
        }

    def calculate_ma15(self, data):
        """计算15分钟均线"""
        return data['close'].rolling(10).mean()

    def detect_mean_reversion_signal(self, data):
        """检测均值回复信?""
        ma = self.calculate_ma15(data)
        current_price = data['close'].iloc[-1]
        deviation = (current_price - ma.iloc[-1]) / ma.iloc[-1]

        if deviation < -self.parameters['mean_reversion_threshold']:
            return 'BUY'  # 价格低于均线，买?
        elif deviation > self.parameters['mean_reversion_threshold']:
            return 'SELL'  # 价格高于均线，卖?

        return 'HOLD'

    def check_trade_limits(self, trade_count):
        """检查交易次数限?""
        return trade_count < self.parameters['max_daily_trades']

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        if not self.check_trade_limits(stock_data.get('daily_trade_count', 0)):
            return None

        signal = self.detect_mean_reversion_signal(stock_data)

        if signal == 'BUY':
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.BUY,
                confidence=0.70,
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * (1 - params['loss_limit']),
                target_price=stock_data['close'] * (1 + params['profit_target']),
                strategy_name=self.name,
                position_size=0.05,
                holding_period=1
            )
        elif signal == 'SELL':
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.SELL,
                confidence=0.70,
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * (1 + params['loss_limit']),
                target_price=stock_data['close'] * (1 - params['profit_target']),
                strategy_name=self.name,
                position_size=0.05,
                holding_period=1
            )

        return None
```

### 16.2 高频策略汇总表

| 策略编号 | 策略名称 | 适用市场 | 风险 | 核心逻辑 |
|----------|----------|----------|------|----------|
| HFT001 | 日内T+0 | A股底?| ?| 均值回?严格止损 |

***

## 17. 期权量化策略?

> 本章来源：全网搜索补?- 2024年期权量化策?

### 17.1 备兑看涨期权策略

#### OPT001: 备兑看涨期权策略

| 属?| 内容 |
|------|------|
| 策略编号 | OPT001 |
| 策略名称 | 备兑看涨期权策略 |
| 适用市场 | 所有（需期权账户?|
| 风险等级 | 中低 |

**量化规则**?
- 持有标的股票或ETF
- 卖出虚值看涨期?
- 收取权利金增强收?
- 标的上涨被行权则止盈

```python
class CoveredCallStrategy(BaseStrategy):
    """备兑看涨期权策略"""

    def __init__(self):
        super().__init__("备兑看涨", "OPT001")
        self.market_states = [MarketState.VOLATILE, MarketState.BULL]
        self.parameters = {
            'moneyness': 0.05,              # 虚?%
            'days_to_expiry': 30,          # 30天到?
            'min_premium': 0.01,           # 最低权利金
            'delta_target': 0.30,           # 目标Delta
        }

    def select_option(self, stock_data, option_chain):
        """选择期权"""
        target_strike = stock_data['close'] * (1 + self.parameters['moneyness'])

        for option in option_chain:
            if option['strike'] >= target_strike and option['days_to_expiry'] == self.parameters['days_to_expiry']:
                if option['premium'] >= self.parameters['min_premium']:
                    return option

        return None

    def calculate_break_even(self, stock_price, premium):
        """计算盈亏平衡?""
        return stock_price - premium

    def calculate_max_profit(self, entry_price, strike_price, premium):
        """计算最大盈?""
        if strike_price > entry_price:
            return (strike_price - entry_price + premium) * 100
        return premium * 100

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        option = self.select_option(stock_data, market_data.get('option_chain', []))

        if option is None:
            return None

        break_even = self.calculate_break_even(stock_data['close'], option['premium'])
        max_profit = self.calculate_max_profit(stock_data['close'], option['strike'], option['premium'])

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.75,
            entry_price=stock_data['close'],
            stop_loss=break_even * 0.95,
            target_price=option['strike'],
            strategy_name=self.name,
            position_size=0.20,
            holding_period=params['days_to_expiry']
        )
```

### 17.2 期权策略汇总表

| 策略编号 | 策略名称 | 适用市场 | 风险 | 核心逻辑 |
|----------|----------|----------|------|----------|
| OPT001 | 备兑看涨期权 | 所?| 中低 | 持有标的+卖虚值购 |

***

## 18. 市场中性策略库

> 本章来源：全网搜索补?- 2024年量化对冲策?

### 18.1 Alpha对冲中性策?

#### N001: 市场中性策?

| 属?| 内容 |
|------|------|
| 策略编号 | N001 |
| 策略名称 | 市场中性策?|
| 适用市场 | 所有（需期货/期权对冲?|
| 风险等级 | 中低 |

**量化规则**?
- 选取Alpha因子强的股票
- 期货/期权对冲Beta
- 剥离市场风险
- 追求稳定绝对收益

```python
class MarketNeutralStrategy(BaseStrategy):
    """市场中性策?""

    def __init__(self):
        super().__init__("市场中?, "N001")
        self.market_states = [MarketState.VOLATILE, MarketState.BEAR]
        self.parameters = {
            'long_count': 20,              # 多头20?
            'short_count': 20,             # 空头20?
            'hedge_ratio': 0.90,           # 对冲比例90%
            'alpha_threshold': 0.02,       # Alpha阈?%
            'max_drawdown': 0.05,          # 最大回?%
        }

    def select_long_stocks(self, stock_pool):
        """选取多头股票"""
        scored = sorted(stock_pool,
                       key=lambda x: x.get('alpha_factor', 0),
                       reverse=True)
        return scored[:self.parameters['long_count']]

    def select_short_stocks(self, stock_pool):
        """选取空头股票"""
        scored = sorted(stock_pool,
                       key=lambda x: x.get('alpha_factor', 0))
        return scored[:self.parameters['short_count']]

    def calculate_hedge_amount(self, long_value, beta):
        """计算对冲数量"""
        return long_value * beta * self.parameters['hedge_ratio']

    def generate_signals(self, market_data, stock_pool, market_state):
        params = self.parameters

        longs = self.select_long_stocks(stock_pool)
        shorts = self.select_short_stocks(stock_pool)

        signals = []

        for stock in longs:
            signals.append(TradingSignal(
                code=stock['code'],
                signal=SignalType.BUY,
                confidence=0.75,
                entry_price=stock['close'],
                stop_loss=stock['close'] * (1 - params['max_drawdown']),
                target_price=stock['close'] * (1 + params['alpha_threshold']),
                strategy_name=self.name,
                position_size=1.0 / params['long_count'],
                holding_period=30
            ))

        for stock in shorts:
            signals.append(TradingSignal(
                code=stock['code'],
                signal=SignalType.SELL,
                confidence=0.75,
                entry_price=stock['close'],
                stop_loss=stock['close'] * (1 + params['max_drawdown']),
                target_price=stock['close'] * (1 - params['alpha_threshold']),
                strategy_name=self.name,
                position_size=1.0 / params['short_count'],
                holding_period=30
            ))

        return signals
```

### 18.2 中性策略汇总表

| 策略编号 | 策略名称 | 适用市场 | 风险 | 核心逻辑 |
|----------|----------|----------|------|----------|
| N001 | 市场中?| 所?| 中低 | Alpha选股+期货对冲 |

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 初始版本，整合游资量化策略和策略池管理框?|
| v1.1 | 2026-03-26 | 补充附录Q/BC/BE/BF/BG游资量化策略 |
| v1.2 | 2026-03-27 | 新增事件驱动/价值红?Smart Money/行业轮动策略?|
| v1.3 | 2026-03-27 | 新增小市值低波动/指数增强/可转?多因子择?行业配置策略 |
| v1.4 | 2026-03-27 | 新增CTA/高频交易/期权量化/市场中性策略库 |