---

module_id: RETAIL_STRATEGIES_D_001

version: 1.0.0

status: Active

created_date: 2026-04-07

last_updated: '2026-04-07'

owner: 个人开发者

standard_type: 专业量化机构文档

responsibility:

- 交易策略设计与实施管理与优化维护

module_id: TACTICS_YOUZI_OTHER_D_001

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






# 游资量化策略?- 第四部分

> **核心职责**: 文档内容说明

> **职责边界**: 

> - ✅ 本文档负责：文档内容说明相关内容

> - ❌ 本文档不负责：其他模块内容





> 顶级游资交易思想量化提炼（四?

>

> **配套文档**?

> - 主文档：

> - 策略池索引：index.md



***



> **说明**：这些策略来自A股顶级游资的经验总结，已抽象为量化规则，需历史回测验证有效性后再入?



***



## 1. Asking局部炒单策略



### S029: Asking局部炒单策略



| 属?| 内容 |

|------|------|

| 策略编号 | S029 |

| 策略名称 | Asking局部炒?|

| 来源 | Asking |

| 适用市场 | 强势市场、热点明?|

| 风险等级 | ?|

| 持仓周期 | 1-3?|



**核心理念**：只做模式内交易，控制回撤，赚钱靠运气，亏钱靠实现



**量化规则**?

- 只做强势股（涨幅>5%?

- 只做热点板块

- 出现买入信号才交?

- 单笔亏损不超过总资金的2%

- 连续3笔亏损后强制休息



```python

class AskingScalpingStrategy(BaseStrategy):

    """Asking局部炒单策?""



    CORE_PRINCIPLES = {

        '模式内交?: {

            '定义': '只做自己熟悉的形?,

            '关键?: '没出现信号坚决不交易',

            '执行?: '90%以上执行?

        },

        '控制回撤': {

            '核心理念': '赚钱靠运气，亏钱靠实?,

            '风控原则': '单笔亏损不超过总资金的2%',

            '连续亏损': '3笔后强制休息'

        },

        '短线精髓': {

            '持仓时间': '次日必走',

            '操作周期': '持有一到三天最?,

            '卖出标准': '不涨停就?

        }

    }



    def __init__(self):

        super().__init__("Asking局部炒?, "S029")

        self.market_states = [MarketState.YAO, MarketState.BULL, MarketState.SHOCK]

        self.parameters = {

            'min_rise_ratio': 0.05,

            'volume_ratio': 1.5,

            'auction_rise_min': 0.05,

            'near_ma_threshold': -0.02,

            'signal_threshold': 0.6,

            'max_position': 0.2,

            'stop_loss_ratio': 0.02,

            'profit_target_ratio': 0.05

        }



    def check_trade_eligibility(self, stock_data, market_data):

        """

        检查是否符合交易模?

        """

        params = self.parameters

        is_strong = stock_data['涨幅'] > params['min_rise_ratio']

        is_hot = stock_data.get('所属板?) in market_data.get('热点板块', [])

        has_signal = self.detect_buy_signal(stock_data)



        if is_strong and is_hot and has_signal:

            return {

                'eligible': True,

                'action': '可交?,

                'max_position': params['max_position']

            }



        return {

            'eligible': False,

            'action': '空仓等待',

            'reason': '不符合模式内交易'

        }



    def detect_buy_signal(self, stock_data):

        """

        检测买入信?

        """

        params = self.parameters

        signals = {}



        volume_ratio = stock_data['成交?] / stock_data['均量']

        if volume_ratio > params['volume_ratio']:

            if stock_data['价格'] > stock_data.get('压力?, stock_data['close']):

                signals['放量突破'] = 0.4



        auction_rise = stock_data.get('竞价涨幅', 0)

        if auction_rise > params['auction_rise_min']:

            signals['竞价强势'] = 0.3



        near_ma = stock_data.get('分时距均?, 0)

        if near_ma > params['near_ma_threshold']:

            signals['均线支撑'] = 0.3



        total_score = sum(signals.values())

        return total_score >= params['signal_threshold']



    def generate_signal(self, market_data, stock_data, market_state):

        eligibility = self.check_trade_eligibility(stock_data, market_data)

        if not eligibility['eligible']:

            return None



        return TradingSignal(

            code=stock_data['code'],

            signal=SignalType.BUY,

            confidence=0.75,

            entry_price=stock_data['close'],

            stop_loss=stock_data['close'] * (1 - self.parameters['stop_loss_ratio']),

            target_price=stock_data['close'] * (1 + self.parameters['profit_target_ratio']),

            position_ratio=eligibility['max_position'],

            strategy_name=self.name

        )



    def execute_sell(self, holding_stock):

        """

        执行卖出

        """

        params = self.parameters

        current_price = holding_stock['current_price']

        cost_price = holding_stock['cost_price']

        profit_ratio = (current_price - cost_price) / cost_price

        is_limit_up = holding_stock.get('is_limit_up', False)



        if not is_limit_up:

            return {'action': '清仓', 'reason': '不涨停就?}



        if profit_ratio >= params['profit_target_ratio']:

            return {'action': '卖出一?, 'reason': '涨幅达标'}



        if profit_ratio <= -params['stop_loss_ratio']:

            return {'action': '止损', 'reason': '亏损超过2%'}



        return {'action': '持有'}

```



**买入条件**?

- 强势股（涨幅>5%?

- 热点板块

- 放量突破压力位（+0.4分）

- 竞价涨幅>5%?0.3分）

- 分时距均?-2%?0.3分）

- 总分?.6



**卖出条件**?

- 不涨停立即清单

- 盈利5%以上卖出一?

- 亏损2%止损



**风险控制**?

- 单笔最大亏损：2%

- 最大持仓：20%

- 连续3笔亏损强制休?



***



## 2. 令胡冲超跌反弹策略



### S030: 令胡冲超跌反弹策略



| 属?| 内容 |

|------|------|

| 策略编号 | S030 |

| 策略名称 | 令胡冲超跌反?|

| 来源 | 令胡?|

| 适用市场 | 弱势市场、超跌行?|

| 风险等级 | ?|

| 持仓周期 | 1-3?|



**核心理念**：判断跌不动、买跌不买涨，逆向思维



**量化规则**?

- 连续下跌后缩量（地量+十字星）

- 买跌不买涨，恐慌杀跌时买入

- 快进快出，持?-3?

- 目标收益5%-15%

- 止损3%



```python

class LingHuChongReboundStrategy(BaseStrategy):

    """令胡冲超跌反弹策?""



    CORE_PRINCIPLES = {

        '判断跌不?: {

            '核心': '连续下跌后缩?,

            '标志': '地量+十字?,

            '预期': '反弹将至'

        },

        '买跌不买?: {

            '核心': '逆向思维',

            '买点': '恐慌杀跌时买入',

            '卖点': '反弹高点卖出'

        },

        '快进快出': {

            '持仓': '1-3?,

            '目标': '5%-15%',

            '止损': '-3%'

        }

    }



    def __init__(self):

        super().__init__("令胡冲超跌反?, "S030")

        self.market_states = [MarketState.SHOCK, MarketState.BEAR]

        self.parameters = {

            'consecutive_decline_days': 3,

            'volume_ratio': 0.5,

            'deviation_ratio': -0.15,

            'score_threshold': 0.6,

            'target_ratio': 0.30,

            'stop_loss_ratio': 0.03,

            'profit_target_ma5': 0.05,

            'profit_target_ma10': 0.10,

            'profit_target_support': 0.15

        }



    def detect_bottom_signal(self, stock_data, market_data):

        """

        检测底部信?

        """

        params = self.parameters

        signals = {}



        consecutive_days = stock_data.get('连续下跌天数', 0)

        if consecutive_days >= params['consecutive_decline_days']:

            signals['连续下跌'] = 0.2



        volume_ratio = stock_data['成交?] / stock_data['均量']

        if volume_ratio < params['volume_ratio']:

            signals['地量'] = 0.3



        if stock_data.get('kline_type') == '十字?:

            signals['十字?] = 0.3



        deviation = stock_data.get('偏离均线比例', 0)

        if deviation < params['deviation_ratio']:

            signals['严重超跌'] = 0.2



        total_score = sum(signals.values())



        if total_score >= params['score_threshold']:

            return {

                'is_bottom': True,

                'score': total_score,

                'action': '可买?,

                'target_ratio': params['target_ratio']

            }



        return {

            'is_bottom': False,

            'score': total_score,

            'action': '等待'

        }



    def generate_signal(self, market_data, stock_data, market_state):

        bottom = self.detect_bottom_signal(stock_data, market_data)

        if not bottom['is_bottom']:

            return None



        return TradingSignal(

            code=stock_data['code'],

            signal=SignalType.BUY,

            confidence=0.70,

            entry_price=stock_data['close'],

            stop_loss=stock_data['close'] * (1 - self.parameters['stop_loss_ratio']),

            target_price=stock_data['close'] * (1 + self.parameters['profit_target_support']),

            position_ratio=0.15,

            strategy_name=self.name

        )



    def check_sell_timing(self, holding_stock):

        """

        检查卖出时?

        """

        params = self.parameters

        profit_ratio = holding_stock['profit_ratio']

        volume_ratio = holding_stock['成交?] / holding_stock['均量']



        if holding_stock['涨幅'] < -0.03 and volume_ratio > 1.5:

            return {'action': '清仓', 'reason': '放量大阴?}



        if profit_ratio >= params['profit_target_support']:

            return {'action': '清仓', 'reason': '达到目标?}



        if profit_ratio > params['profit_target_ma5'] and holding_stock.get('分时走势') == '高开低走':

            return {'action': '卖出一?, 'reason': '滞涨'}



        return {'action': '持有'}

```



**买入条件**?

- 连续下跌?天（+0.2分）

- 地量（成交量<均量50%）（+0.3分）

- 十字星（+0.3分）

- 偏离均线<-15%?0.2分）

- 总分?.6



**卖出条件**?

- 放量大阴线立即清单

- 达到目标位（+15%）清单

- 高开低走且盈?5%卖出一?



**风险控制**?

- 止损?3%

- 最大持仓：15%

- 目标收益?%-15%



***



## 3. 92科比价值投资策略



### S031: 92科比价值投资策略



| 属?| 内容 |

|------|------|

| 策略编号 | S031 |

| 策略名称 | 92科比价值投?|

| 来源 | 92科比 |

| 适用市场 | 任何市场（长期持有） |

| 风险等级 | ?|

| 持仓周期 | 3-6个月 |



**核心理念**：合理估值买入、耐心持有，价值回归需要时?



**量化规则**?

- 市净?1.5且股息率>3%为低?

- 耐心持有3-6个月

- 不受短期波动影响

- 硬止?15%，软止损-10%



```python

class ValueInvestorStrategy(BaseStrategy):

    """92科比价值投资策?""



    CORE_PRINCIPLES = {

        '合理估?: {

            '方法': '市净?股息率综合评?,

            '低估标准': '市净?1.5且股息率>3%',

            '买入时机': '低估时买?

        },

        '耐心持有': {

            '周期': '3-6个月',

            '逻辑': '价值回归需要时?,

            '关键': '不受短期波动影响'

        },

        '止损原则': {

            '硬止?: '-15%',

            '软止?: '-10%考虑减仓',

            '逻辑止损': '基本面恶化立即走'

        }

    }



    def __init__(self):

        super().__init__("92科比价值投?, "S031")

        self.market_states = [MarketState.ANY]

        self.parameters = {

            'pb_thresholds': [1.0, 1.5],

            'dividend_thresholds': [5, 3],

            'pe_range': [5, 15, 20, 30],

            'pb_high': 3,

            'score_threshold': 0.6,

            'hard_stop_loss': 0.15,

            'soft_stop_loss': 0.10

        }



    def evaluate_valuation(self, stock_data):

        """

        评估估?

        """

        params = self.parameters

        pb = stock_data['市净?]

        dividend_yield = stock_data['股息?]

        pe = stock_data['市盈?]



        score = 0



        if pb < params['pb_thresholds'][0]:

            score += 0.4

        elif pb < params['pb_thresholds'][1]:

            score += 0.2



        if dividend_yield > params['dividend_thresholds'][0]:

            score += 0.3

        elif dividend_yield > params['dividend_thresholds'][1]:

            score += 0.2



        if params['pe_range'][0] < pe < params['pe_range'][1]:

            score += 0.3



        if score >= params['score_threshold']:

            return {

                'undervalued': True,

                'score': score,

                'action': '可买?

            }



        return {

            'undervalued': False,

            'score': score,

            'action': '等待'

        }



    def generate_signal(self, market_data, stock_data, market_state):

        valuation = self.evaluate_valuation(stock_data)

        if not valuation['undervalued']:

            return None



        return TradingSignal(

            code=stock_data['code'],

            signal=SignalType.BUY,

            confidence=0.75,

            entry_price=stock_data['close'],

            stop_loss=stock_data['close'] * (1 - self.parameters['hard_stop_loss']),

            target_price=None,

            position_ratio=0.20,

            strategy_name=self.name

        )



    def should_hold(self, stock_data, original_data):

        """

        判断是否继续持有

        """

        params = self.parameters

        pe = stock_data['市盈?]

        pb = stock_data['市净?]



        if pe > params['pe_range'][3]:

            return {'action': '卖出', 'reason': '高估PE>30'}



        if pb > params['pb_high']:

            return {'action': '卖出', 'reason': '泡沫市净?3'}



        if stock_data.get('基本面恶?):

            return {'action': '卖出', 'reason': '基本面恶?}



        return {'action': '持有'}

```



**买入条件**?

- 市净?1.0?0.4分）?1.5?0.2分）

- 股息?5%?0.3分）?3%?0.2分）

- 市盈?-15?0.3分）

- 总分?.6



**持有条件**?

- 基本面稳定

- 估值未高估（PE<20?

- 无重大利?



**卖出条件**?

- PE>30高估

- 市净?3泡沫

- 基本面恶?



**风险控制**?

- 硬止损：-15%

- 软止损：-10%考虑减仓

- 最大持仓：20%



***



## 策略汇?



| 编号 | 策略名称 | 来源 | 适用市场 | 风险 | 持仓周期 | 核心理念 |

|------|---------|------|---------|------|---------|---------|

| S029 | Asking局部炒?| Asking | 强势/热点 | ?| 1-3?| 模式内交?|

| S030 | 令胡冲超跌反?| 令胡?| 弱势/超跌 | ?| 1-3?| 买跌不买?|

| S031 | 92科比价值投?| 92科比 | 任何 | ?| 3-6?| 合理估值持?|



***



## 关联战术模块



| 战术模块 | 关联策略 |

|---------|---------|

|  | S029/S030/S031 |

|  | S029/S030 |

|  | S029/S030 |

