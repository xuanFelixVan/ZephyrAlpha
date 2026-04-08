---
module_id: RETAIL_STRATEGIES_A_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: '2026-04-07'
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
- 交易策略设计与实施管理与优化维护
module_id: TACTICS_YOUZI_ASKING_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 交易策略设计与实施管理与优化维护
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
---


# 游资量化策略?- 第一部分
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 顶级游资交易思想量化提炼（一?
>
> **配套文档**?
> - 主文档：
> - 策略池索引：index.md

***

> **说明**：这些策略来自A股顶级游资的经验总结，已抽象为量化规则，需历史回测验证有效性后再入?

***

## 1. Asking（邱宝裕）核心策略

### S011: 只做超强势股策略

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
            'min_change_pct': 5.0,
            'min_turnover': 1e9,
            'min_turnover_rate': 10.0,
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        if stock_data['change_pct'] < params['min_change_pct']:
            return None
        if stock_data['turnover'] < params['min_turnover']:
            return None
        if stock_data['turnover_rate'] < params['min_turnover_rate']:
            return None
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
            position_size=0.10,
            holding_period=3
        )
```

***

### S012: 守株待兔策略

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
            'min_up_days': 2,
            'min_up_pct': 5.0,
            'ma5_distance': 0.02,
            'volume_ratio_max': 0.8,
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        up_count = 0
        for i in range(params['min_up_days']):
            if stock_data[f'd_{i}_change_pct'] >= params['min_up_pct']:
                up_count += 1

        if up_count < params['min_up_days']:
            return None

        ma5 = stock_data['ma5']
        current = stock_data['close']
        if abs(current - ma5) / ma5 > params['ma5_distance']:
            return None

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

***

### S017: 半仓盈利加仓策略

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
            'initial_position': 0.50,
            'profit_threshold': 0.05,
            'second_add_threshold': 0.08,
        }
        self.position_phases = {}

    def calculate_position(self, stock_code, current_profit):
        if stock_code not in self.position_phases:
            self.position_phases[stock_code] = 1

        phase = self.position_phases[stock_code]
        params = self.parameters

        if phase == 1 and current_profit > params['profit_threshold']:
            self.position_phases[stock_code] = 2
            return 1.0, "加仓至满?

        elif phase == 2 and current_profit > params['second_add_threshold']:
            self.position_phases[stock_code] = 3
            return 1.5, "盈利丰厚，动用备用资?

        elif current_profit < -0.03:
            self.position_phases[stock_code] = 1
            return 0.5, "止损，回调半?

        return self.position_phases.get(stock_code, 1) * 0.5, "持有"
```

***

## 2. 炒股养家情绪策略

### S013: 情绪转折策略

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
            'profit_ratio_threshold': 0.6,
            'limit_down_decrease': 10,
            'rebound_candidates': 5,
        }

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        profit_ratio = market_data['上涨家数'] / market_data['总交易家?]
        if profit_ratio < params['profit_ratio_threshold']:
            return None

        limit_down_change = market_data['limit_down_count_yesterday'] - market_data['limit_down_count_today']
        if limit_down_change < params['limit_down_decrease']:
            return None

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

***

### S018: 情绪两分法策略

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
            'hot_threshold': 0.70,
            'cold_threshold': 0.40,
            'add_position': 0.30,
            'reduce_position': 0.20,
        }

    def get_market_sentiment(self, market_data):
        rise_count = market_data.get('上涨家数', 0)
        total_count = market_data.get('总交易家?, 1)
        ratio = rise_count / total_count if total_count > 0 else 0.5
        return ratio

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters
        sentiment = self.get_market_sentiment(market_data)

        if sentiment > params['hot_threshold']:
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.SELL,
                confidence=0.75,
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * 0.97,
                target_price=stock_data['close'] * 1.02,
                strategy_name=self.name,
                position_size=-params['reduce_position'],
                holding_period=1
            )

        elif sentiment < params['cold_threshold']:
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

        return None
```

***

### S019: 情绪六分法策略

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
            'extreme_hot': 0.66,
            'over_hot': 0.55,
            'slight_hot': 0.51,
            'slight_cold': 0.45,
            'over_cold': 0.35,
        }

    def get_sentiment_zone(self, sentiment_ratio):
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

***

### S020: 弱势转折点搏击策略

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
            'consecutive_drop_days': 3,
            'limit_up_count_threshold': 5,
            'space_board_suppressed': True,
        }

    def check_market_turn_signals(self, market_data):
        consecutive_drops = 0
        for i in range(self.parameters['consecutive_drop_days']):
            if market_data.get(f'd_{i}_rise_ratio', 1) < 0.5:
                consecutive_drops += 1

        if consecutive_drops < self.parameters['consecutive_drop_days']:
            return {'can_turn': False, 'reason': '未出现连续普?}

        limit_up_count = market_data.get('连板股数?, 100)
        if limit_up_count > self.parameters['limit_up_count_threshold']:
            return {'can_turn': False, 'reason': '连板股仍然活?}

        return {'can_turn': True, 'phase': '等待领头?}

    def select_leader_stock(self, candidate_stocks):
        for stock in candidate_stocks:
            if stock['relative_change'] < -0.02:
                continue
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

***

## 3. 五日线战?

### T011: 五日线趋势策略

| 属?| 内容 |
|------|------|
| 策略编号 | T011 |
| 策略名称 | 五日线趋势策略|
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
            'position_threshold': 0.01,
            'volume_reversal': True,
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

        if current < ma5:
            return None

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

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 整合附录Q/BC/BE/BF/BG游资策略第一部分 |
