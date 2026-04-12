---

module_id: RETAIL_STRATEGIES_B_001

version: 1.0.0

status: Active

created_date: 2026-04-07

last_updated: '2026-04-07'

owner: 个人开发者

standard_type: 专业量化机构文档

responsibility:

- 交易策略设计与实施管理与优化维护

module_id: TACTICS_YOUZI_CHAOGU_001

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

layer: layer_03
---






# 游资量化策略?- 第二部分

> **核心职责**: 文档内容说明

> **职责边界**: 

> - ✅ 本文档负责：文档内容说明相关内容

> - ❌ 本文档不负责：其他模块内容





> 顶级游资交易思想量化提炼（二?

>

> **配套文档**?

> - 主文档：

> - 策略池索引：index.md

> - 游资策略第一部分：retail-strategies-a.md



***



## 1. 赵老哥核心策略



### S014: 二板定龙头策略



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

            'open_ratio_min': 0.03,

            'open_ratio_max': 0.07,

            'low_protection': 0.80,

            'seal_time_limit': '10:00',

            'min_score': 0.70,

        }



    def generate_signal(self, market_data, stock_data, market_state):

        params = self.parameters



        open_ratio = stock_data['open_ratio']

        if not (params['open_ratio_min'] <= open_ratio <= params['open_ratio_max']):

            return None



        yesterday_high = stock_data['yesterday_high']

        today_low = stock_data['low']

        if today_low < yesterday_high * params['low_protection']:

            return None



        if stock_data['seal_time'] > params['seal_time_limit']:

            return None



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



***



### S016: 新题材判断策略



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

            'min_turnover': 1e9,

            'min_sector_limit_up': 3,

        }



    def generate_signal(self, market_data, stock_data, market_state):

        params = self.parameters



        if stock_data['turnover'] < params['min_turnover']:

            return None



        if not stock_data.get('has_major_event', False):

            return None



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



***



## 2. 独股一箭核心策略



### S015: 独股一箭策略



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

            'ma5_distance': 0.02,

            'chong_gao_volume_ratio': 0.5,

            'profit_target': 0.09,

        }



    def generate_signal(self, market_data, stock_data, market_state):

        params = self.parameters



        profit_ratio = market_data['上涨家数'] / market_data['总交易家?]

        if profit_ratio < 0.5 and not stock_data.get('is_hot_stock', False):

            return None



        ma5 = stock_data['ma5']

        current = stock_data['close']

        if abs(current - ma5) / ma5 > params['ma5_distance']:

            return None



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

            holding_period=1

        )



    def exit_signal(self, position_data):

        """超短线卖出信?""

        current = position_data['current_price']

        entry = position_data['entry_price']

        volume_ratio = position_data['volume_ratio']



        if volume_ratio < 0.5 and current > entry * 1.05:

            return {'action': '卖出', 'reason': '冲高无量'}



        limit_up = entry * 1.10

        if current < limit_up and current >= entry * 1.09:

            return {'action': '卖出', 'reason': '涨停差一?}



        return None

```



***



## 3. 反弹三定律策略



### M009: 反弹三定律策略



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

            '共振阈?: 2,

        }



    def generate_signal(self, market_data, stock_data, market_state):

        共振 = 0



        if self.check_volume_reversal(stock_data):

            共振 += 1



        if stock_data['close'] > stock_data['ma5']:

            共振 += 1



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



***



## 4. 退神稳定复利风控策略



### R001: 动态仓位管理策略



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

            'win_rate_threshold': 0.6,

            'small_position': 0.2,

            'medium_position': 0.4,

            'large_position': 0.6,

            'max_position': 0.8,

            'drawdown_protection': 0.10,

        }



    def calculate_position(self, win_probability, market_state):

        params = self.parameters



        if win_probability < params['win_rate_threshold']:

            return 0



        elif win_probability < 0.70:

            return params['small_position']



        elif win_probability < 0.80:

            return params['medium_position']



        elif win_probability < 0.90:

            return params['large_position']



        else:

            return params['max_position']



    def check_drawdown_protection(self, current_value, peak_value):

        drawdown = (peak_value - current_value) / peak_value



        if drawdown >= self.parameters['drawdown_protection']:

            return {

                'action': '减仓',

                'ratio': 0.5,

                'reason': f'回撤{drawdown*100:.1f}%，触发保?

            }



        return None

```



***



### R002: 稳定复利风控策略



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

            'max_single_position': 0.50,

            'drawdown_line': 0.10,

            'compound_rate': 0.02,

        }



    def check_drawdown_protection(self, current_value, peak_value):

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

        max_pos = self.parameters['max_single_position']



        protection = self.check_drawdown_protection(current_value, peak_value)

        if protection['triggered']:

            return max_pos * protection['reduce_ratio']



        if target_profit > 0.20:

            return max_pos

        elif target_profit > 0.10:

            return max_pos * 0.7

        else:

            return max_pos * 0.5



    def validate_not_big_loss(self, current_profit):

        if current_profit < -0.10:

            return {

                'valid': False,

                'action': '止损出局',

                'reason': '亏损?0%，触发不大赔红线'

            }

        return {'valid': True}

```



***



## 5. 下跌三阶段策略



### M010: 下跌三阶段策略



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

            'early_phase_days': 5,

            'mid_phase_days': 15,

            'late_phase_signal': 'new_money',

        }



    def identify_decline_phase(self, market_data):

        consecutive_drop_days = 0

        for i in range(30):

            if market_data.get(f'd_{i}_change', 0) < 0:

                consecutive_drop_days += 1

            else:

                break



        if consecutive_drop_days <= self.parameters['early_phase_days']:

            return 'early'

        elif consecutive_drop_days <= self.parameters['mid_phase_days']:

            return 'mid'

        else:

            return 'late'



    def generate_signal(self, market_data, stock_data, market_state):

        phase = self.identify_decline_phase(market_data)



        if phase == 'early':

            if stock_data['relative_strength'] > 0.05:

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

            if stock_data['change_pct'] < -0.15:

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



        else:

            if market_data.get('new_money_signal', False):

                if stock_data['volume_ratio'] > 2.0:

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



## 更新记录



| 版本 | 日期 | 变更内容 |

|------|------|----------|

| v1.0 | 2026-03-26 | 整合附录Q/BC/BE/BF/BG游资策略第二部分 |

