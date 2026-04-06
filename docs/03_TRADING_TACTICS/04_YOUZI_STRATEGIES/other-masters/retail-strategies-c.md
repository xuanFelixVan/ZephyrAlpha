---
module_id: TACTICS_YOUZI_OTHER_C_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
standard_type: 专业量化机构文档
applicable_scope: 全系�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?
responsibility:
  - 市场状态识别 (Layer 4)
---

# 游资量化策略�?- 第三部分
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 顶级游资交易思想量化提炼（三�?
>
> **配套文档**�?
> - 主文档：
> - 策略池索引：[index.md](../../05_STRATEGY_POOL/index.md)

***

> **说明**：这些策略来自A股顶级游资的经验总结，已抽象为量化规则，需历史回测验证有效性后再入�?

***

## 1. 赵老哥龙头战法

### S021: 二板定龙头策�?

| 属�?| 内容 |
|------|------|
| 策略编号 | S021 |
| 策略名称 | 二板定龙�?|
| 来源 | 赵老哥 |
| 适用市场 | 妖股周期、牛�?|
| 风险等级 | �?|

**核心理念**：一板能看出来个毛，二板才是确认

**量化规则**�?
- 从昨日首板中筛选二板候�?
- 一板后次日高开幅度�?%-7%
- 回调不破一板最高价80%
- 10点前封板
- 同题材有一板跟�?

```python
class SecondBoardDragonStrategy(BaseStrategy):
    """二板定龙头策�?""

    def __init__(self):
        super().__init__("二板定龙�?, "S021")
        self.market_states = [MarketState.YAO, MarketState.BULL]
        self.parameters = {
            'open_ratio_min': 0.03,
            'open_ratio_max': 0.07,
            'pullback_ratio': 0.80,
            'seal_time_limit': '10:00',
        }

    def select_second_board(self, yesterday_first_board_stocks):
        """
        从昨日首板中选取二板候�?
        """
        candidates = []
        params = self.parameters

        for stock in yesterday_first_board_stocks:
            score = 0

            open_ratio = stock['open_ratio']
            if params['open_ratio_min'] <= open_ratio <= params['open_ratio_max']:
                score += 0.30
            elif open_ratio > params['open_ratio_max']:
                score += 0.10

            if stock['lowest_price'] > stock['yesterday_high'] * params['pullback_ratio']:
                score += 0.25

            if stock['seal_time'] <= params['seal_time_limit']:
                score += 0.25

            if stock.get('same_theme_first_board', 0) >= 1:
                score += 0.20

            if score >= 0.70:
                candidates.append({
                    'stock': stock,
                    'score': score
                })

        return sorted(candidates, key=lambda x: x['score'], reverse=True)

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        if stock_data.get('连续板数', 0) < 2:
            return None

        open_ratio = stock_data.get('竞价涨幅', 0)
        if not (params['open_ratio_min'] <= open_ratio <= params['open_ratio_max'] * 2):
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.80,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.95,
            target_price=stock_data['close'] * 1.20,
            strategy_name=self.name,
            position_size=0.15,
            holding_period=3
        )
```

***

### S022: 新题材判断策�?

| 属�?| 内容 |
|------|------|
| 策略编号 | S022 |
| 策略名称 | 新题材判�?|
| 来源 | 赵老哥 |
| 适用市场 | 所有市�?|
| 风险等级 | �?|

**量化规则**�?
- 有故事：重大政策、业绩拐点、并购重组等
- 大量资金活跃：成交额 > 10�?
- 市场认同度高：板块内多个涨停

```python
class NewThemeQuantifier(BaseStrategy):
    """新题材判断量化策�?""

    def __init__(self):
        super().__init__("新题材判�?, "S022")
        self.market_states = [s for s in MarketState]
        self.parameters = {
            'min_turnover': 1e9,
            'min_limit_up_count': 3,
            'policy_weight': 0.40,
            'capital_weight': 0.30,
            'recognition_weight': 0.30,
        }

    def identify_new_theme(self, market_data, theme_data):
        """
        判断是否是新题材
        """
        params = self.parameters

        has_story = self.check_theme_story(theme_data, market_data)
        has_capital = theme_data.get('板块成交�?, 0) > params['min_turnover']
        has_recognition = theme_data.get('板块涨停�?, 0) >= params['min_limit_up_count']

        total_score = (
            has_story * params['policy_weight'] +
            has_capital * params['capital_weight'] +
            has_recognition * params['recognition_weight']
        )

        if total_score >= 0.6:
            return {
                'is_new_theme': True,
                'confidence': total_score,
                'action': '积极关注'
            }

        return {
            'is_new_theme': False,
            'confidence': total_score,
            'action': '观望'
        }

    def check_theme_story(self, theme_data, market_data):
        """
        检查题材是否有故事（政策、业绩等�?
        """
        policy_score = theme_data.get('政策关联�?, 0)
        event_score = theme_data.get('重大事件', 0)
        return min((policy_score + event_score) / 2, 1.0)
```

***

## 2. 情绪周期五阶段量�?

### S023: 情绪周期五阶段策�?

| 属�?| 内容 |
|------|------|
| 策略编号 | S023 |
| 策略名称 | 情绪周期五阶�?|
| 来源 | 情绪周期理论 |
| 适用市场 | 所有市�?|
| 风险等级 | �?|

**核心理念**：冰点→回暖→发酵→高潮→退�?

**量化规则**�?

| 阶段 | 涨停家数 | 跌停家数 | 炸板�?| 连板股数 | 操作策略 |
|------|----------|----------|--------|----------|----------|
| 冰点 | <20 | >30 | >50% | 0 | 观望，等待转�?|
| 回暖 | 20-50 | 10-30 | 30-50% | >=2 | 试探买入 |
| 发酵 | 50-100 | <10 | <30% | >=3 | 积极参与 |
| 高潮 | >100 | <5 | <20% | >=5 | 谨慎追高 |
| 退�?| 下降 | 增加 | 上升 | 减少 | 减仓出局 |

```python
class EmotionCycleFiveStagesStrategy(BaseStrategy):
    """情绪周期五阶段策�?""

    def __init__(self):
        super().__init__("情绪周期五阶�?, "S023")
        self.market_states = [s for s in MarketState]
        self.parameters = {
            '冰点': {
                '涨停家数_max': 20,
                '跌停家数_min': 30,
                '炸板率_min': 0.50,
                'action': '观望',
                'position': 0.0
            },
            '回暖': {
                '涨停家数_min': 20,
                '涨停家数_max': 50,
                '跌停家数_max': 30,
                '炸板率_max': 0.50,
                '连板股数_min': 2,
                'action': '试探买入',
                'position': 0.20
            },
            '发酵': {
                '涨停家数_min': 50,
                '涨停家数_max': 100,
                '跌停家数_max': 10,
                '炸板率_max': 0.30,
                '连板晋级率_min': 0.70,
                'action': '积极参与',
                'position': 0.40
            },
            '高潮': {
                '涨停家数_min': 100,
                '跌停家数_max': 5,
                '炸板率_max': 0.20,
                'action': '谨慎追高',
                'position': 0.25
            },
            '退�?: {
                '涨停家数_max': 50,
                '跌停家数_min': 20,
                'action': '减仓出局',
                'position': 0.10
            }
        }

    def identify_stage(self, market_data):
        """
        识别当前市场情绪阶段
        """
        params = self.parameters
        limit_up = market_data.get('涨停家数', 0)
        limit_down = market_data.get('跌停家数', 0)
        break_rate = market_data.get('炸板�?, 0)
        continuous_boards = market_data.get('连板股数', 0)

        if limit_up < params['冰点']['涨停家数_max'] and limit_down > params['冰点']['跌停家数_min']:
            return {'stage': '冰点', **params['冰点']}
        elif params['回暖']['涨停家数_min'] <= limit_up <= params['回暖']['涨停家数_max']:
            if limit_down <= params['回暖']['跌停家数_max']:
                return {'stage': '回暖', **params['回暖']}
        elif params['发酵']['涨停家数_min'] <= limit_up <= params['发酵']['涨停家数_max']:
            if break_rate <= params['发酵']['炸板率_max']:
                return {'stage': '发酵', **params['发酵']}
        elif limit_up > params['高潮']['涨停家数_min']:
            return {'stage': '高潮', **params['高潮']}
        else:
            return {'stage': '退�?, **params['退�?]}

        return {'stage': '未知', 'action': '观察', 'position': 0.0}

    def generate_signal(self, market_data, stock_data, market_state):
        stage_info = self.identify_stage(market_data)
        stage = stage_info['stage']

        if stage == '冰点':
            return None
        elif stage == '退�?:
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.SELL,
                confidence=0.70,
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * 1.02,
                target_price=stock_data['close'] * 0.95,
                strategy_name=self.name,
                position_size=-stage_info['position'],
                holding_period=1
            )
        else:
            if stock_data.get('is_leader', False) or stock_data.get('连续板数', 0) >= 2:
                return TradingSignal(
                    code=stock_data['code'],
                    signal=SignalType.BUY,
                    confidence=0.75,
                    entry_price=stock_data['close'],
                    stop_loss=stock_data['close'] * 0.95,
                    target_price=stock_data['close'] * 1.15,
                    strategy_name=self.name,
                    position_size=stage_info['position'],
                    holding_period=3
                )

        return None
```

***

## 3. 主力伏击战法

### S024: 箱体突破策略

| 属�?| 内容 |
|------|------|
| 策略编号 | S024 |
| 策略名称 | 箱体突破 |
| 来源 | 主力伏击战法 |
| 适用市场 | 震荡市、熊市反�?|
| 风险等级 | �?|

**核心理念**：用箱体横盘锁定主力吸筹痕迹

**量化规则**�?
- 箱体横盘：股价在一定区间内震荡，高�?20%，持�?0天以�?
- 吸筹确认：缩量调整，不破箱体下沿
- 突破信号：放量突破箱体上沿（涨幅>2%�?
- 回调买入：突破后缩量回踩箱体上沿

```python
class BoxBreakoutStrategy(BaseStrategy):
    """箱体突破策略"""

    def __init__(self):
        super().__init__("箱体突破", "S024")
        self.market_states = [MarketState.VOLATILE, MarketState.BEAR]
        self.parameters = {
            'box_height_max': 0.20,
            'box_days_min': 20,
            'breakout_ratio': 1.02,
            'volume_ratio': 1.5,
            'pullback_volume_ratio': 0.8,
        }

    def detect_box_formation(self, price_data):
        """
        检测箱体形�?
        """
        params = self.parameters
        highs = price_data['近期高点']
        lows = price_data['近期低点']

        box_height = (highs.max() - lows.min()) / lows.min()
        box_days = len(price_data)

        if box_height < params['box_height_max'] and box_days >= params['box_days_min']:
            return {
                'is_box': True,
                'box_top': highs.max(),
                'box_bottom': lows.min(),
                'box_mid': (highs.max() + lows.min()) / 2,
                'action': '观察等待突破'
            }

        return {'is_box': False}

    def check_breakout_signal(self, stock_data, box_data):
        """
        检查突破信�?
        """
        params = self.parameters
        current_price = stock_data['close']
        box_top = box_data['box_top']
        volume = stock_data['成交�?]
        avg_volume = stock_data['均量']

        if current_price > box_top * params['breakout_ratio']:
            if volume > avg_volume * params['volume_ratio']:
                return {
                    'breakout': True,
                    'action': '突破确认，可买入',
                    'confidence': 0.80
                }

        return {'breakout': False, 'action': '等待'}

    def check_pullback_entry(self, stock_data, box_data):
        """
        检查回调买入信�?
        """
        params = self.parameters
        current_price = stock_data['close']
        box_top = box_data['box_top']
        volume = stock_data['成交�?]
        avg_volume = stock_data['均量']

        if current_price >= box_top * 0.98 and current_price <= box_top * 1.02:
            if volume < avg_volume * params['pullback_volume_ratio']:
                return {
                    'pullback_buy': True,
                    'action': '缩量回踩，可买入',
                    'confidence': 0.75
                }

        return {'pullback_buy': False, 'action': '等待'}

    def generate_signal(self, market_data, stock_data, market_state):
        box_data = self.detect_box_formation(stock_data)
        if not box_data.get('is_box', False):
            return None

        breakout = self.check_breakout_signal(stock_data, box_data)
        if breakout.get('breakout', False):
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.BUY,
                confidence=breakout['confidence'],
                entry_price=stock_data['close'],
                stop_loss=box_data['box_bottom'],
                target_price=box_data['box_top'] * 1.30,
                strategy_name=self.name,
                position_size=0.20,
                holding_period=10
            )

        pullback = self.check_pullback_entry(stock_data, box_data)
        if pullback.get('pullback_buy', False):
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.BUY,
                confidence=pullback['confidence'],
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * 0.97,
                target_price=box_data['box_top'] * 1.25,
                strategy_name=self.name,
                position_size=0.15,
                holding_period=7
            )

        return None
```

***

### S025: 主力四步循环策略

| 属�?| 内容 |
|------|------|
| 策略编号 | S025 |
| 策略名称 | 主力四步循环 |
| 来源 | 主力伏击战法 |
| 适用市场 | 所有市�?|
| 风险等级 | �?|

**核心理念**：主力行为四步循环：吸筹→洗盘→拉升→出�?

**量化规则**�?

| 阶段 | 特征 | 量化信号 | 散户应对 |
|------|------|----------|----------|
| 吸筹 | 低位悄悄�?| 缩量横盘/地量 | 别割�?|
| 洗盘 | 把散户洗出去 | 缩量下跌/尾盘打压 | 别被吓走 |
| 拉升 | 快速拉高赚�?| 放量突破/缩量回调 | 拿稳 |
| 出货 | 高位偷偷�?| 高位放量滞涨 | 快跑 |

```python
class MainForceCycleStrategy(BaseStrategy):
    """主力四步循环策略"""

    def __init__(self):
        super().__init__("主力四步循环", "S025")
        self.market_states = [s for s in MarketState]
        self.parameters = {
            'accumulation': {
                'volume_ratio_max': 0.5,
                'price_change_max': 0.05,
            },
            'wash': {
                'volume_ratio_max': 0.6,
                'price_drop_max': 0.10,
            },
            'rally': {
                'volume_ratio_min': 1.5,
                'price_change_min': 0.05,
            },
            'distribution': {
                'volume_ratio_min': 2.0,
                'price_stagnation': True,
            }
        }

    def identify_phase(self, stock_data, history_data):
        """
        识别主力行为阶段
        """
        params = self.parameters
        volume_ratio = stock_data['成交�?] / stock_data['均量']
        price_change = stock_data['涨跌�?]

        if volume_ratio < params['accumulation']['volume_ratio_max']:
            if abs(price_change) < params['accumulation']['price_change_max']:
                return {'phase': '吸筹', 'action': '持有观望', 'confidence': 0.75}

        if volume_ratio < params['wash']['volume_ratio_max']:
            if price_change < 0 and abs(price_change) < params['wash']['price_drop_max']:
                return {'phase': '洗盘', 'action': '逢低买入', 'confidence': 0.70}

        if volume_ratio > params['rally']['volume_ratio_min']:
            if price_change > params['rally']['price_change_min']:
                return {'phase': '拉升', 'action': '积极持有', 'confidence': 0.85}

        if volume_ratio > params['distribution']['volume_ratio_min']:
            if params['distribution']['price_stagnation']:
                return {'phase': '出货', 'action': '果断卖出', 'confidence': 0.90}

        return {'phase': '未知', 'action': '观望', 'confidence': 0.0}

    def generate_signal(self, market_data, stock_data, market_state):
        phase_info = self.identify_phase(stock_data, market_data)
        phase = phase_info['phase']

        if phase == '吸筹':
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.HOLD,
                confidence=phase_info['confidence'],
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * 0.95,
                target_price=stock_data['close'] * 1.10,
                strategy_name=self.name,
                position_size=0.10,
                holding_period=15
            )
        elif phase == '洗盘':
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.BUY,
                confidence=phase_info['confidence'],
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * 0.95,
                target_price=stock_data['close'] * 1.15,
                strategy_name=self.name,
                position_size=0.15,
                holding_period=10
            )
        elif phase == '拉升':
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.BUY,
                confidence=phase_info['confidence'],
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * 0.93,
                target_price=stock_data['close'] * 1.25,
                strategy_name=self.name,
                position_size=0.25,
                holding_period=5
            )
        elif phase == '出货':
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.SELL,
                confidence=phase_info['confidence'],
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * 1.02,
                target_price=stock_data['close'] * 0.90,
                strategy_name=self.name,
                position_size=-0.30,
                holding_period=1
            )

        return None
```

***

## 4. 一夜持股法（杨永兴战法�?

### S026: 一夜持股法策略

| 属�?| 内容 |
|------|------|
| 策略编号 | S026 |
| 策略名称 | 一夜持股法 |
| 来源 | 杨永�?|
| 适用市场 | 牛市、震荡市 |
| 风险等级 | �?|

**核心理念**：尾盘买入，次日早盘卖出

**量化规则**�?
- 买入时间�?4:30 - 14:50
- 选股标准：上升通道、缩量调整、不能追�?
- 仓位：不超过30%
- 次日高开：直接卖�?
- 次日平开：冲高卖�?
- 次日低开：视情况持有或止�?

```python
class OneNightHoldingStrategy(BaseStrategy):
    """一夜持股法策略"""

    def __init__(self):
        super().__init__("一夜持股法", "S026")
        self.market_states = [MarketState.BULL, MarketState.VOLATILE]
        self.parameters = {
            'buy_time_start': '14:30',
            'buy_time_end': '14:50',
            'max_position': 0.30,
            'sell_time': '10:00',
            'high_open_threshold': 0.03,
            'low_open_threshold': -0.03,
        }

    def check_entry_time(self, current_time):
        """
        检查是否在买入时间窗口
        """
        params = self.parameters
        hour = current_time.hour
        minute = current_time.minute

        if hour == 14 and minute >= 30:
            return True
        if hour == 14 and minute <= 59:
            return True

        return False

    def check_entry_conditions(self, stock_data):
        """
        检查买入条�?
        """
        trend = self.check_trend(stock_data)
        volume = self.check_volume(stock_data)

        return trend == '上升' and volume == '缩量'

    def check_trend(self, stock_data):
        """
        检查趋势：上升通道
        """
        ma5 = stock_data.get('ma5', 0)
        ma10 = stock_data.get('ma10', 0)
        ma20 = stock_data.get('ma20', 0)
        current = stock_data['close']

        if ma5 > ma10 > ma20 and current > ma5:
            return '上升'
        elif ma5 < ma10 < ma20 and current < ma5:
            return '下降'
        return '震荡'

    def check_volume(self, stock_data):
        """
        检查量能：缩量调整
        """
        volume_ratio = stock_data['成交�?] / stock_data['均量']
        if volume_ratio < 0.8:
            return '缩量'
        elif volume_ratio > 1.2:
            return '放量'
        return '正常'

    def execute_next_morning(self, holding_stock, next_open_data):
        """
        次日早盘执行
        """
        params = self.parameters
        open_ratio = next_open_data.get('竞价涨幅', 0)

        if open_ratio > params['high_open_threshold']:
            return {'action': '卖出', 'reason': '高开', 'profit_ratio': open_ratio}
        elif open_ratio < params['low_open_threshold']:
            return {'action': '止损', 'reason': '低开', 'profit_ratio': open_ratio}
        else:
            return {'action': '冲高卖出', 'reason': '平开', 'profit_ratio': 0}

    def generate_signal(self, market_data, stock_data, market_state):
        params = self.parameters

        if not self.check_entry_conditions(stock_data):
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=0.65,
            entry_price=stock_data['close'],
            stop_loss=stock_data['close'] * 0.97,
            target_price=stock_data['close'] * 1.05,
            strategy_name=self.name,
            position_size=params['max_position'],
            holding_period=1
        )
```

***

## 5. 做T仓位管理与决策规�?

### S027: 做T仓位管理策略

| 属�?| 内容 |
|------|------|
| 策略编号 | S027 |
| 策略名称 | 做T仓位管理 |
| 来源 | A股特色增�?|
| 适用市场 | 所有市场（日内�?|
| 风险等级 | �?|

**核心理念**：做T是A股重要的超额收益来源，需要分钟级数据和特殊因子支�?

**量化规则**�?
- 基础比例：日线仓�?× 20-30%
- 置信度调整：基础仓位 × 分钟预测置信�?
- 市场状态调整：牛市上限50%，熊市上�?0%
- 硬性限制：单日做T仓位 �?总资�?0%
- 最大做T次数：≤10�?�?
- 最小间隔时间：�?5分钟
- 冷却机制：连�?次亏损暂停做T

```python
class DayTradingPositionStrategy(BaseStrategy):
    """做T仓位管理策略"""

    def __init__(self):
        super().__init__("做T仓位管理", "S027")
        self.market_states = [s for s in MarketState]
        self.parameters = {
            'base_ratio': 0.25,
            'confidence_adjustment': True,
            'bull_max_ratio': 0.50,
            'bear_max_ratio': 0.20,
            'hard_limit': 0.50,
            'max_trades_per_day': 10,
            'min_interval_minutes': 15,
            'cooling_losses': 3,
        }
        self.daily_stats = {
            'trade_count': 0,
            'consecutive_losses': 0,
            'last_trade_time': None
        }

    def calculate_day_trade_position(self, daily_position, confidence, market_state):
        """
        计算做T仓位
        """
        params = self.parameters

        if self.daily_stats['trade_count'] >= params['max_trades_per_day']:
            return 0.0, '已达每日最大交易次�?

        if self.daily_stats['consecutive_losses'] >= params['cooling_losses']:
            return 0.0, '连续亏损，触发冷�?

        base_position = daily_position * params['base_ratio']

        if params['confidence_adjustment']:
            base_position *= confidence

        if market_state == MarketState.BULL:
            max_ratio = params['bull_max_ratio']
        elif market_state == MarketState.BEAR:
            max_ratio = params['bear_max_ratio']
        else:
            max_ratio = params['hard_limit'] / 2

        position = min(base_position, max_ratio)
        position = min(position, params['hard_limit'])

        return position, '可做T'

    def check_interval(self, current_time):
        """
        检查最小间隔时�?
        """
        params = self.parameters
        if self.daily_stats['last_trade_time'] is None:
            return True

        elapsed = (current_time - self.daily_stats['last_trade_time']).total_seconds() / 60
        return elapsed >= params['min_interval_minutes']

    def record_trade_result(self, profit):
        """
        记录交易结果
        """
        if profit > 0:
            self.daily_stats['consecutive_losses'] = 0
        else:
            self.daily_stats['consecutive_losses'] += 1

        self.daily_stats['trade_count'] += 1

    def reset_daily_stats(self):
        """
        重置每日统计
        """
        self.daily_stats = {
            'trade_count': 0,
            'consecutive_losses': 0,
            'last_trade_time': None
        }
```

***

### S028: 做T决策规则策略

| 属�?| 内容 |
|------|------|
| 策略编号 | S028 |
| 策略名称 | 做T决策规则 |
| 来源 | A股特色增�?|
| 适用市场 | 所有市场（日内�?|
| 风险等级 | �?|

**量化规则**�?

**买入信号**�?
- 技术信号：分时指标金叉 + 盘口支持（MACD金叉 + 买盘占优�?
- 资金信号：分钟级资金持续流入（连�?�?分钟净流入�?
- 波动信号：波动率回归到均值以下（波动�?< 20日均值�?.8�?
- 协同信号：与日线趋势方向一致（日线看多 + 分钟回调买点�?

**卖出信号**�?
- 止盈条件：达到目标收益率（收益率 > 1.5%�?
- 技术止损：分时指标死叉或支撑跌破（KDJ死叉 OR 价格<分时均线�?
- 时间止损：持仓超�?0分钟无盈�?
- 风险止损：波动率突然放大（ATR突破布林上轨�?

**不做T条件**�?
- 流动性不足：买卖价差 > 0.2%
- 波动率过低：5分钟ATR < 20日均值�?.6
- 重大事件窗口：财�?宏观数据发布前后1小时
- 系统风险预警：大盘下�?> 2%

```python
class DayTradingDecisionStrategy(BaseStrategy):
    """做T决策规则策略"""

    def __init__(self):
        super().__init__("做T决策规则", "S028")
        self.market_states = [s for s in MarketState]
        self.parameters = {
            'buy_signals': {
                'macd_golden_cross': True,
                'buy_volume_ratio': 1.2,
                'volume_streak_count': 3,
                'volatility_threshold': 0.8,
            },
            'sell_signals': {
                'profit_target': 0.015,
                'kdj_dead_cross': True,
                'time_stop_minutes': 30,
                'atr_bollinger_break': True,
            },
            'avoid_signals': {
                'spread_threshold': 0.002,
                'low_volatility_threshold': 0.6,
                'event_window_hours': 1,
                'market_drop_warning': 0.02,
            }
        }

    def check_buy_signals(self, minute_data, daily_data):
        """
        检查做T买入信号
        """
        params = self.parameters['buy_signals']
        signals = {}

        if minute_data.get('macd_golden_cross', False):
            signals['MACD金叉'] = 0.30

        if minute_data.get('buy_volume_ratio', 0) > params['buy_volume_ratio']:
            signals['买盘占优'] = 0.25

        if minute_data.get('volume_streak_count', 0) >= params['volume_streak_count']:
            signals['连续净流入'] = 0.25

        current_vol = minute_data.get('volatility', 1)
        avg_vol = minute_data.get('volatility_ma20', 1)
        if current_vol < avg_vol * params['volatility_threshold']:
            signals['波动率回�?] = 0.20

        total_score = sum(signals.values())
        return total_score >= 0.60, signals, total_score

    def check_sell_signals(self, position_data, current_time):
        """
        检查做T卖出信号
        """
        params = self.parameters['sell_signals']
        signals = {}

        profit_ratio = position_data.get('profit_ratio', 0)
        if profit_ratio > params['profit_target']:
            signals['止盈'] = 0.40

        if position_data.get('kdj_dead_cross', False):
            signals['KDJ死叉'] = 0.30

        holding_minutes = (current_time - position_data['open_time']).total_seconds() / 60
        if holding_minutes > params['time_stop_minutes'] and profit_ratio < 0:
            signals['时间止损'] = 0.30

        if position_data.get('atr_break_bollinger', False):
            signals['波动率止�?] = 0.30

        total_score = sum(signals.values())
        return total_score >= 0.50, signals

    def check_avoid_conditions(self, market_data):
        """
        检查不做T条件
        """
        params = self.parameters['avoid_signals']
        reasons = []

        if market_data.get('买卖价差', 0) > params['spread_threshold']:
            reasons.append('流动性不�?)

        if market_data.get('5分钟ATR', 0) < market_data.get('ATR均�?, 1) * params['low_volatility_threshold']:
            reasons.append('波动率过�?)

        if market_data.get('重大事件窗口', False):
            reasons.append('重大事件窗口')

        if market_data.get('大盘涨跌�?, 0) < -params['market_drop_warning']:
            reasons.append('系统风险预警')

        return len(reasons) > 0, reasons

    def generate_signal(self, market_data, stock_data, market_state):
        avoid, avoid_reasons = self.check_avoid_conditions(market_data)
        if avoid:
            return None

        buy_score, buy_signals, buy_confidence = self.check_buy_signals(stock_data, market_data)
        if buy_score:
            return TradingSignal(
                code=stock_data['code'],
                signal=SignalType.BUY,
                confidence=buy_confidence,
                entry_price=stock_data['close'],
                stop_loss=stock_data['close'] * 0.98,
                target_price=stock_data['close'] * 1.015,
                strategy_name=self.name,
                position_size=0.05,
                holding_period=1
            )

        return None
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 整合二板定龙�?S021-S022)、情绪周期五阶段(S023)、主力伏�?S024-S025)、一夜持股法(S026)、做T策略(S027-S028) |
