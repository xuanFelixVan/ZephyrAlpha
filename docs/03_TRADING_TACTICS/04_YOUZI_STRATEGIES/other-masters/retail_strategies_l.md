---
module_id: TACTICS_YOUZI_OTHER_L_001
version: 3.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
responsibility:
  - 交易策略、战术执行
standard_type: 专业量化机构文档
applicable_scope: 全系�?
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 进行�?
---
---


# 游资策略补充（二�? S106-S120
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 顶级游资交易思想量化提炼（遗漏附录整合）
>
> **来源**：量化策略专业分层方案_v3.0 附录BS/BT/BU/BV/BW/BX/BY/BZ
>
> **配套文档**�?
> - 主文档：
> - 策略池索引：[index.md](08_HUMAN_AI_INTERFACE/index.md)
> - 策略一：[retail-strategies-k.md](./retail-strategies-k.md) - S091-S105

---

> **说明**：这些策略来�?8位游资悟道心法补充内容，已抽象为量化规则

---

## 1. 乔帮主完整策略体�?(S106)

> **来源**：附录BS - 乔帮主完整量化策略体�?
>
> **核心**：从1万到10亿的游资成长之路

### S106A: 乔帮主核心理�?

```python
class QiaoBangZhuCore:
    """
    乔帮主核心理念量�?
    """

    CORE_PRINCIPLES = {
        '控制回撤': {
            '核心理念': '赚钱靠运气，亏钱靠实�?,
            '执行': '单笔亏损不超过总资金的2%',
            '进阶': '回撤控制是复利核�?
        },
        '超短精髓': {
            '定义': '以天为单位计算收�?,
            '优势': '中长线回撤时超短不回�?,
            '目标': '每天�?%，一�?�?
        },
        '仓位管理': {
            '60%以下': '观望',
            '60%-70%': '小仓出击',
            '70%-80%': '中仓出击',
            '80%-90%': '大仓出击',
            '90%以上': '满仓'
        }
    }

    def check_position_by_market(self, market_data):
        """
        根据市场强度确定仓位
        """
        profit_effect = market_data.get('赚钱效应', 0.5)
        panic_effect = market_data.get('恐慌效应', 0.5)

        if profit_effect < 0.4:
            return {'position': 0, 'action': '观望'}
        elif profit_effect < 0.5:
            return {'position': 0.1, 'action': '小仓'}
        elif profit_effect < 0.6:
            return {'position': 0.3, 'action': '中仓'}
        elif profit_effect < 0.7:
            return {'position': 0.6, 'action': '大仓'}
        else:
            return {'position': 1.0, 'action': '满仓'}
```

### S106B: 低吸与追涨区�?

```python
class QiaoBangZhuEntry:
    """
    乔帮主：低吸与追涨量化区�?
    核心：买入瞬间是越来越贵还是越来越便�?
    """

    ENTRY_TYPES = {
        '绿盘追涨': {
            '定义': '追涨时是绿盘，价格是全天相对高点',
            '买入状�?: '拉升状�?,
            '风险': '较高'
        },
        '红盘追涨': {
            '定义': '追涨时是红盘，价格是全天相对高点',
            '买入状�?: '拉升状�?,
            '风险': '中等'
        },
        '绿盘低吸': {
            '定义': '低吸时是绿盘，价格是全天相对低点',
            '买入状�?: '下跌状�?,
            '风险': '中等'
        },
        '红盘低吸': {
            '定义': '低吸时是红盘，价格是全天相对低点',
            '买入状�?: '下跌状�?,
            '风险': '较低'
        }
    }

    def classify_entry_type(self, entry_price, today_open, today_low, today_high):
        """
        区分低吸和追�?
        """
        if entry_price > entry_price.shift(1):
            if entry_price >= today_open:
                return {'type': '红盘追涨', 'risk': '中等'}
            else:
                return {'type': '绿盘追涨', 'risk': '较高'}
        else:
            if entry_price >= today_open:
                return {'type': '红盘低吸', 'risk': '较低'}
            else:
                return {'type': '绿盘低吸', 'risk': '中等'}
```

### S106C: 赢面与仓位关�?

```python
    WIN_PROBABILITY_MATRIX = {
        'below_60': {'position': 0, 'action': '观望'},
        '60_to_70': {'position': 0.1, 'action': '小仓出击'},
        '70_to_80': {'position': 0.3, 'action': '中仓出击'},
        '80_to_90': {'position': 0.6, 'action': '大仓出击'},
        'above_90': {'position': 1.0, 'action': '满仓'}
    }

    def calc_position_by_win_prob(self, win_prob, profit_space, loss_space):
        """
        根据赢面计算仓位
        """
        space_ratio = profit_space / loss_space if loss_space > 0 else 0
        combined_win = win_prob * min(space_ratio / 3, 1.5)

        if combined_win < 0.6:
            return {'position': 0, 'action': '观望'}
        elif combined_win < 0.7:
            return {'position': 0.1, 'action': '小仓出击'}
        elif combined_win < 0.8:
            return {'position': 0.3, 'action': '中仓出击'}
        elif combined_win < 0.9:
            return {'position': 0.6, 'action': '大仓出击'}
        else:
            return {'position': 1.0, 'action': '满仓'}
```

### S106D: 分时起爆点检�?

```python
class QiaoBangZhuBoomPoint:
    """
    乔帮主：量能决定一�?
    核心：攻在量中，无量不上
    """

    VOLUME_PRINCIPLES = {
        '分时起爆': {
            '核心': '量能代表资金，资金决定一�?,
            '买入信号': '攻在量中，无量不�?,
            '卖出信号': '退在量后，缩量无法维持'
        },
        '起爆点特�?: {
            '条件1': '必然爆量',
            '条件2': '无量无视价格',
            '条件3': '有量才安�?
        }
    }

    def detect_boom_point(self, stock_data):
        """
        检测分时起爆点
        """
        current_volume = stock_data['成交�?]
        avg_volume = stock_data['均量']
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0

        if volume_ratio < 1.5:
            return {'is_boom': False, 'reason': '量能不足'}

        price_change = stock_data['涨幅']
        if price_change > 3 and volume_ratio > 2:
            return {
                'is_boom': True,
                'confidence': min(volume_ratio / 5, 1.0),
                'action': '买入'
            }

        return {'is_boom': False, 'reason': '不符合起爆条�?}
```

### S106E: 抄底策略

```python
class QiaoBangZhuBottom:
    """
    乔帮主：抄底策略量化
    """

    BOTTOM_HUNTING = {
        '牛股抄底条件': {
            '条件1': '强势板块龙头�?,
            '条件2': '超跌后缩量均匀',
            '条件3': '等待反弹开长阳',
            '进阶': '顺利涨停可次日冲高卖'
        },
        '止损原则': {
            '硬止�?: '-8%',
            '时间止损': '5日不涨离�?
        }
    }

    def check_bottom_opportunity(self, stock_data, sector_data):
        """
        检查抄底机�?
        """
        is_sector_leader = sector_data.get('leader_stock') == stock_data['code']

        decline_ratio = (stock_data['最高价'] - stock_data['当前�?]) / stock_data['最高价']
        volume_ratio = stock_data['成交�?] / stock_data['均量']
        is_oversold = decline_ratio > 0.20 and volume_ratio < 0.7

        volume_stable = stock_data['成交量StdDev'] / stock_data['成交量Mean'] < 0.3

        if is_sector_leader and is_oversold and volume_stable:
            return {'opportunity': True, 'confidence': 0.8, 'action': '可抄�?}

        return {'opportunity': False, 'confidence': 0.2, 'action': '等待'}
```

---

## 2. 小鳄鱼操盘手法补�?(S107)

> **来源**：附录BS - 小鳄鱼操盘补�?

### S107A: 二板四种买入方式

```python
class SmallCrocodileSecondBoard:
    """
    小鳄鱼：二板四种买入方式量化
    """

    BUY_METHODS = {
        '低吸': '分时调整后刚拐头向上',
        '半路': '分时开始向上进�?,
        '打板': '即将打板或刚打板',
        '竞价': '集合竞价直接买入'
    }

    NEXT_DAY_OPEN = {
        '一字涨停板': {'action': '可放�?, 'reason': '无法买入'},
        '大幅高开(7%+)缩量秒板': {'action': '视情�?, 'reason': '谨慎参与'},
        '大幅高开(7%+)下杀': {'action': '低吸、打�?, 'reason': '盘中机会'},
        '小幅高开(3%-7%)': {'action': '低吸、打板、竞�?, 'reason': '正常参与'},
        '平开、低开': {'action': '视情�?, 'reason': '需要分�?}
    }

    LOW_INFLOW_STANDARD = {
        '调整幅度': (0.10, 0.25),
        '成交量缩�?: '< 最高量50%',
        '均线支撑': '回调�?0日或20日均�?
    }

    def analyze_second_board(self, stock_data):
        """
        分析二板机会
        """
        is_limit_up = stock_data.get('is_limit_up', False)
        open_count = stock_data.get('开板次�?, 0)

        if not is_limit_up:
            return {'type': '非涨�?, 'action': '不适用'}

        if open_count == 0:
            return {'type': '一字板', 'action': '可放�?}
        elif open_count <= 2:
            return {'type': '实体�?, 'action': '可参�?}
        else:
            return {'type': '烂板', 'action': '谨慎'}
```

### S107B: 人气股反�?

```python
class SmallCrocodileAntiPackage:
    """
    小鳄鱼：人气股反包量�?
    """

    ANTI_PACKAGE = {
        '超级人气�?: {
            '条件': '市场总龙�?,
            '涨幅': '> 100%',
            '调整': '> 30%'
        },
        '一般股': {
            '条件': '必须是主线品�?,
            '调整': '20%-30%',
            '跟风': '有板块跟�?
        }
    }

    def check_anti_package(self, stock_data):
        """
        检查反包机�?
        """
        total_rise = stock_data.get('总涨�?, 0)
        current_decline = stock_data.get('回调幅度', 0)
        has_sector_follow = stock_data.get('跟风数量', 0) > 0

        if total_rise > 1.0:
            if current_decline > 0.30:
                return {'can_anti': True, 'type': '超级人气�?, 'confidence': 0.8}
        else:
            if 0.20 <= current_decline <= 0.30 and has_sector_follow:
                return {'can_anti': True, 'type': '一般股', 'confidence': 0.6}

        return {'can_anti': False}
```

---

## 3. Asking/局部炒单策�?(S108)

> **来源**：附录BT - Asking/局部炒单量化策�?

### S108A: Asking核心理念

```python
class AskingQuantifier:
    """
    Asking：只做模式内交易，控制回�?
    """

    CORE_PRINCIPLES = {
        '模式内交�?: {
            '定义': '只做自己熟悉的形�?,
            '关键�?: '没出现信号坚决不交易',
            '执行�?: '90%以上执行�?
        },
        '控制回撤': {
            '核心理念': '赚钱靠运气，亏钱靠实�?,
            '风控原则': '单笔亏损不超过总资金的2%',
            '连续亏损': '3笔后强制休息'
        },
        '短线精髓': {
            '持仓时间': '次日必走',
            '操作周期': '持有一到三天最�?,
            '卖出标准': '不涨停就�?
        }
    }

    def check_trade_eligibility(self, stock_data, market_data):
        """
        检查是否符合交易模�?
        """
        is_strong = stock_data['涨幅'] > 5
        is_hot = stock_data['所属板�?] in market_data['热点板块']
        has_signal = self.detect_buy_signal(stock_data)

        if is_strong and is_hot and has_signal:
            return {'eligible': True, 'action': '可交�?, 'max_position': 0.2}

        return {'eligible': False, 'action': '空仓等待'}

    def detect_buy_signal(self, stock_data):
        """
        检测买入信�?
        """
        signals = {}

        if stock_data['成交�?] > stock_data['均量'] * 1.5:
            if stock_data['价格'] > stock_data['压力�?]:
                signals['放量突破'] = 0.4

        if stock_data['竞价涨幅'] > 0.05:
            signals['竞价强势'] = 0.3

        if stock_data['分时距均�?] > -0.02:
            signals['均线支撑'] = 0.3

        total_score = sum(signals.values())
        return total_score >= 0.6
```

### S108B: Asking卖出策略

```python
    SELL_RULES = {
        '不涨停就�?: {
            '条件': '当日涨幅<涨停�?,
            '时间': '14:30�?,
            '执行': '必须卖出'
        },
        '涨幅达标�?: {
            '条件': '盈利达到5%以上',
            '操作': '卖出一�?,
            '剩余': '移动止损'
        },
        '亏损处理': {
            '止损�?: '-2%',
            '执行': '无条件止�?
        }
    }

    def execute_sell(self, holding_stock):
        """
        执行卖出
        """
        current_price = holding_stock['current_price']
        cost_price = holding_stock['cost_price']
        profit_ratio = (current_price - cost_price) / cost_price
        is_limit_up = holding_stock.get('is_limit_up', False)

        if not is_limit_up:
            return {'action': '清仓', 'reason': '不涨停就�?}

        if profit_ratio >= 0.05:
            return {'action': '卖出一�?, 'reason': '涨幅达标'}

        if profit_ratio <= -0.02:
            return {'action': '止损', 'reason': '亏损超过2%'}

        return {'action': '持有'}
```

---

## 4. 令胡冲超跌反�?(S109)

> **来源**：附录BU - 令胡冲超跌反弹量�?

```python
class LingHuChongQuantifier:
    """
    令胡冲：判断跌不动、买跌不买涨
    """

    CORE_PRINCIPLES = {
        '判断跌不�?: {
            '核心': '连续下跌后缩�?,
            '标志': '地量+十字�?,
            '预期': '反弹将至'
        },
        '买跌不买�?: {
            '核心': '逆向思维',
            '买点': '恐慌杀跌时买入',
            '卖点': '反弹高点卖出'
        },
        '快进快出': {
            '持仓': '1-3�?,
            '目标': '5%-15%',
            '止损': '-3%'
        }
    }

    def detect_bottom_signal(self, stock_data):
        """
        检测底部信�?
        """
        signals = {}

        if stock_data.get('连续下跌天数', 0) >= 3:
            signals['连续下跌'] = 0.2

        if stock_data['成交�?] < stock_data['均量'] * 0.5:
            signals['地量'] = 0.3

        if stock_data.get('kline_type') == '十字�?:
            signals['十字�?] = 0.3

        if stock_data['偏离均线比例'] < -0.15:
            signals['严重超跌'] = 0.2

        total_score = sum(signals.values())

        if total_score >= 0.6:
            return {'is_bottom': True, 'score': total_score, 'action': '可买�?}

        return {'is_bottom': False, 'score': total_score, 'action': '等待'}

    SELL_STRATEGY = {
        '目标�?: {'ma5': '+5%', 'ma10': '+10%', '前期支撑�?: '+15%'},
        '卖出信号': {'放量大阴�?: '立即卖出', '滞涨': '高开后低�?}
    }

    def check_sell_timing(self, holding_stock):
        """
        检查卖出时�?
        """
        profit_ratio = holding_stock['profit_ratio']
        volume_ratio = holding_stock['成交�?] / holding_stock['均量']

        if holding_stock['涨幅'] < -0.03 and volume_ratio > 1.5:
            return {'action': '清仓', 'reason': '放量大阴�?}

        if profit_ratio >= 0.15:
            return {'action': '清仓', 'reason': '达到目标�?}

        if profit_ratio > 0.05 and holding_stock['分时走势'] == '高开低走':
            return {'action': '卖出一�?, 'reason': '滞涨'}

        return {'action': '持有'}
```

---

## 5. 92科比/局部价值投�?(S110)

> **来源**：附录BV - 92科比/局部价值投资量�?

```python
class ValueInvestorQuantifier:
    """
    92科比：合理估值买入、耐心持有
    """

    CORE_PRINCIPLES = {
        '合理估�?: {
            '方法': '市净�?股息率综合评�?,
            '低估标准': '市净�?1.5且股息率>3%'
        },
        '耐心持有': {
            '周期': '3-6个月',
            '关键': '不受短期波动影响'
        },
        '止损原则': {
            '硬止�?: '-15%',
            '软止�?: '-10%考虑减仓'
        }
    }

    def evaluate_valuation(self, stock_data):
        """
        评估估�?
        """
        pb = stock_data['市净�?]
        dividend_yield = stock_data['股息�?]
        pe = stock_data['市盈�?]

        score = 0

        if pb < 1.0:
            score += 0.4
        elif pb < 1.5:
            score += 0.2

        if dividend_yield > 5:
            score += 0.3
        elif dividend_yield > 3:
            score += 0.2

        if 5 < pe < 15:
            score += 0.3

        if score >= 0.6:
            return {'undervalued': True, 'score': score, 'action': '可买�?}

        return {'undervalued': False, 'score': score, 'action': '等待'}

    HOLD_RULES = {
        '持有条件': {'基本面稳�?: True, '估值未高估': 'PE<20'},
        '卖出标准': {'高估': 'PE>30', '泡沫': '市净�?3'}
    }

    def should_hold(self, stock_data, original_data):
        """
        判断是否继续持有
        """
        current_pb = stock_data['市净�?]
        original_pb = original_data['市净�?]

        if current_pb >= original_pb * 2:
            return {'action': '减仓50%', 'reason': '估值翻�?}

        if stock_data['业绩增�?] < -0.20:
            return {'action': '清仓', 'reason': '基本面恶�?}

        if stock_data['总收益率'] >= 0.50:
            return {'action': '减仓50%', 'reason': '达到50%目标'}

        return {'action': '继续持有'}
```

---

## 6. 陈兄/安子元波段操�?(S111)

> **来源**：附录BW - 陈兄/安子元波段操作量�?

```python
class SwingTraderQuantifier:
    """
    陈兄/安子元：趋势为王、趋势线操作
    """

    CORE_PRINCIPLES = {
        '趋势为王': {
            '上升趋势': '只看多不做空',
            '下降趋势': '只看空不做多',
            '震荡趋势': '高抛低吸'
        },
        '波段目标': {
            '短线': '10%-20%',
            '中线': '30%-50%',
            '止损': '-8%'
        }
    }

    def detect_trend(self, price_data):
        """
        检测趋�?
        """
        ma_short = price_data['ma20']
        ma_long = price_data['ma60']
        current_price = price_data['close']

        if current_price > ma_short > ma_long:
            return {'trend': '上升', 'action': '逢低买入', 'support': ma_short}
        if current_price < ma_short < ma_long:
            return {'trend': '下降', 'action': '逢高卖出', 'resistance': ma_short}
        return {'trend': '震荡', 'action': '高抛低吸'}

    STOP_LOSS_RULES = {
        '硬止�?: '-8%',
        '逻辑止损': {'上升趋势破坏': '收盘跌破MA20'},
        '时间止损': {'短线': '5日不�?, '中线': '20日不�?}
    }

    def find_entry_point(self, stock_data, trend_info):
        """
        寻找波段买入�?
        """
        if trend_info['trend'] == '上升':
            support = trend_info['support']
            if stock_data['当前�?] >= support * 0.98:
                return {
                    'action': '买入',
                    'entry': support,
                    'stop_loss': support * 0.92,
                    'target': support * 1.15
                }
        elif trend_info['trend'] == '震荡':
            lower = trend_info.get('range', [0, 0])[0]
            if stock_data['当前�?] <= lower * 1.02:
                return {
                    'action': '买入',
                    'entry': lower,
                    'stop_loss': lower * 0.95,
                    'target': lower * 1.20
                }
        return {'action': '等待'}
```

---

## 7. 清秋/牛脾气首板战�?(S112)

> **来源**：附录BX - 清秋/牛脾气首板战法量�?

```python
class FirstLimitUpQuantifier:
    """
    清秋/牛脾气：首板后次日高开、封单比�?
    """

    CORE_PRINCIPLES = {
        '首板筛�?: {
            '个股首板': '近期第一次涨�?,
            '板块首板': '同一板块率先涨停',
            '时间优先': '10点前封板更好'
        },
        '次日操作': {
            '高开': '+5%以上开�?,
            '买入条件': '封单�?3%',
            '卖出时机': '不连板就�?
        },
        '风险控制': {
            '仓位': '单股不超�?0%',
            '止损': '-3%无条件止�?
        }
    }

    def analyze_first_limitup(self, stock_data):
        """
        分析首板机会
        """
        is_first = stock_data.get('近期涨停次数', 0) == 0
        is_sector_leader = stock_data.get('板块涨停顺序', 0) == 1

        seal_amount = stock_data.get('涨停封单金额', 0)
        turnover = stock_data['成交�?]
        seal_ratio = seal_amount / turnover if turnover > 0 else 0

        seal_time = stock_data.get('封板时间', 12)
        is_early_seal = seal_time <= 10

        score = 0
        if is_first: score += 0.2
        if is_sector_leader: score += 0.3
        if seal_ratio > 3: score += 0.3
        if is_early_seal: score += 0.2

        return {'is_good': score >= 0.6, 'score': score, 'recommendation': '可参�? if score >= 0.6 else '观望'}

    NEXT_DAY_RULES = {
        '高开操作': {
            '高开>7%': {'action': '开盘卖�?, 'reason': '溢价�?},
            '高开5-7%': {'action': '持有观察', 'reason': '等待连板'},
            '高开<5%': {'action': '视情�?, 'reason': '结合市场'}
        },
        '低开操作': {
            '低开>3%': {'action': '观望', 'reason': '可能是坑'},
            '低开<3%': {'action': '等待反弹', 'reason': '找机会出'}
        }
    }
```

---

## 8. 山西L/灯芯人情绪周�?(S113)

> **来源**：附录BY - 山西L/灯芯人情绪周期量�?

```python
class EmotionCycleQuantifier:
    """
    山西L/灯芯人：情绪周期、龙头见顶规�?
    """

    CORE_PRINCIPLES = {
        '情绪周期': {
            '启动�?: '龙头股出�?,
            '发酵�?: '板块扩散',
            '高潮�?: '全民讨论',
            '退潮期': '龙头跌停'
        },
        '龙头见顶规律': {
            '缩量加�?: '高位连续缩量',
            '尾盘炸板': '封单撤除',
            '地天�?: '主力出货'
        },
        '操作节奏': {
            '启动�?: '重仓买入',
            '发酵�?: '持有或加�?,
            '高潮�?: '分批卖出',
            '退潮期': '空仓等待'
        }
    }

    def detect_emotion_cycle(self, market_data):
        """
        检测市场情绪周�?
        """
        indicators = {}

        if market_data.get('龙头涨跌停比', 0) > 0.8:
            indicators['龙头强势'] = 0.3

        limit_up_count = market_data.get('涨停家数', 0)
        if limit_up_count > 100:
            indicators['高潮�?] = 0.3
        elif limit_up_count > 50:
            indicators['发酵�?] = 0.3

        limit_down = market_data.get('跌停家数', 0)
        if limit_down > 30:
            indicators['退潮期'] = 0.4

        if '退潮期' in indicators:
            return {'cycle': '退潮期', 'action': '空仓等待', 'confidence': indicators['退潮期']}
        elif '高潮�? in indicators:
            return {'cycle': '高潮�?, 'action': '分批卖出', 'confidence': indicators['高潮�?]}
        elif '发酵�? in indicators:
            return {'cycle': '发酵�?, 'action': '持有', 'confidence': indicators['发酵�?]}

        return {'cycle': '启动�?, 'action': '积极买入', 'confidence': 0.5}

    LEADER_TOP_PATTERNS = {
        '缩量加�?: {'特征': '连续3天缩量涨�?, '信号强度': 0.8, '操作': '卖出'},
        '尾盘炸板': {'特征': '14:30后开�?, '信号强度': 0.7, '操作': '立即卖出'},
        '地天�?: {'特征': '从跌停拉到涨�?, '信号强度': 0.9, '操作': '卖出'}
    }

    def detect_leader_top(self, leader_stock):
        """
        检测龙头见顶信�?
        """
        signals = []

        consecutive_days = leader_stock.get('连续缩量天数', 0)
        if consecutive_days >= 3:
            signals.append(('缩量加�?, 0.8))

        if leader_stock.get('炸板时间', 0) >= 14.5:
            signals.append(('尾盘炸板', 0.7))

        if leader_stock['涨幅'] > 0.09 and leader_stock['最低价'] == leader_stock['跌停�?]:
            signals.append(('地天�?, 0.9))

        if signals:
            strongest = max(signals, key=lambda x: x[1])
            return {'is_top': True, 'pattern': strongest[0], 'confidence': strongest[1], 'action': '卖出'}

        return {'is_top': False, 'action': '继续持有'}
```

---

## 9. 宁波敢死队涨停秘�?(S114)

> **来源**：附录BS - 宁波敢死队涨停秘笈补�?

```python
class Ningbo敢死队Quantifier:
    """
    宁波敢死队：涨停板类型分�?
    """

    LIMIT_UP_TYPES = {
        '一字板': {'action': '不参�?, 'reason': '无法买入'},
        '实体�?: {'action': '最佳买�?, 'reason': '可参�?},
        '洗盘�?: {'action': '可参�?, 'reason': '涨停后开板洗�?}
    }

    LIMIT_UP_NEXT_DAY = {
        '高开>5%': {'action': '开盘卖出一�?, 'reason': '锁定利润'},
        '平开或低开': {'action': '等待冲高卖出', 'reason': '寻找高点'},
        '收盘�?涨停�?0%': {'action': '止损', 'reason': '形态破�?}
    }

    def analyze_limit_up_type(self, stock_data):
        """
        分析涨停板类�?
        """
        is_limit_up = stock_data.get('is_limit_up', False)
        open_count = stock_data.get('开板次�?, 0)
        turnover_rate = stock_data.get('换手�?, 0)

        if not is_limit_up:
            return {'type': '非涨�?, 'action': '不适用'}

        if open_count == 0 and turnover_rate < 0.05:
            return self.LIMIT_UP_TYPES['一字板']
        if open_count <= 2 and turnover_rate < 0.25:
            return self.LIMIT_UP_TYPES['洗盘�?]
        return self.LIMIT_UP_TYPES['实体�?]
```

---

## 10. 瑞鹤仙熊市策�?(S115)

> **来源**：附录BS - 瑞鹤仙熊市策略补�?

```python
class RuiHeXianBearMarket:
    """
    瑞鹤仙：熊市空仓策略
    """

    EMPTY_SIGNALS = {
        '大盘3连阴': True,
        '跌幅>1%天数占比': '> 50%',
        '跌停家数': '> 50�?
    }

    ENTRY_SIGNALS = {
        '大盘缩量十字�?: True,
        '热点板块明确': True,
        '龙头股出�?: True
    }

    def check_empty_opportunity(self, market_data):
        """
        检查空仓时�?
        """
        signals = {}

        if market_data.get('consecutive_decline_days', 0) >= 3:
            signals['3连阴'] = 0.3

        big_decline_ratio = market_data.get('big_decline_days_ratio', 0)
        if big_decline_ratio > 0.5:
            signals['跌幅过大'] = 0.3

        limit_down_count = market_data.get('跌停家数', 0)
        if limit_down_count > 50:
            signals['恐慌蔓延'] = 0.4

        total_score = sum(signals.values())

        if total_score >= 0.6:
            return {'action': '空仓等待', 'confidence': total_score, 'signals': signals}

        return {'action': '继续观察', 'confidence': total_score, 'signals': signals}

    def check_entry_opportunity(self, market_data):
        """
        检查进场时�?
        """
        signals = {}

        if market_data.get('kline_type') == '十字�?:
            volume_ratio = market_data['成交�?] / market_data['均量']
            if volume_ratio < 0.8:
                signals['缩量十字�?] = 0.4

        if len(market_data.get('hot_sectors', [])) > 0:
            signals['热点明确'] = 0.3

        if market_data.get('has_leader', False):
            signals['龙头出现'] = 0.3

        total_score = sum(signals.values())

        if total_score >= 0.7:
            return {'action': '进场', 'confidence': total_score, 'signals': signals}

        return {'action': '继续等待', 'confidence': total_score, 'signals': signals}
```

---

## 11. 章盟主三线归一 (S116)

> **来源**：附录BZ - 章盟主三线归一战法

```python
class ZhangMengzhuThreeLines:
    """
    章盟主：MA5、MA10、MA20三线归一
    """

    THREE_LINES_DEFINITION = {
        '定义': 'MA5、MA10、MA20三条均线同时向上发散',
        '条件1': '股价在三条均线之�?,
        '条件2': '成交量呈现阶梯式放大',
        '多头排列': 'MA5 > MA10 > MA20'
    }

    def check_three_lines(self, stock_data):
        """
        检查三线归一条件
        """
        ma5 = stock_data['MA5']
        ma10 = stock_data['MA10']
        ma20 = stock_data['MA20']
        price = stock_data['close']
        volume = stock_data['volume']
        avg_volume = stock_data['avg_volume']

        is_bullish = ma5 > ma10 > ma20
        price_above = price > ma5
        volume_increasing = volume > avg_volume * 1.3

        if is_bullish and price_above and volume_increasing:
            return {'signal': '三线归一', 'action': '买入', 'confidence': 0.8}

        return {'signal': '未确�?, 'action': '等待'}
```

---

## 12. 综合查漏补缺要点 (S117-S120)

> **来源**：附录BS - 综合查漏补缺量化要点

### 龙头股共享特�?

```python
LEADER_SHARED_FEATURES = {
    '连板概率': '> 30%',
    '流通市�?: '< 50亿（短线�?,
    '换手�?: '> 15%',
    '首板后次日高开': '>= 5%',
    '回调深度': '10%-25%',
    '回调时间': '2-5�?,
    '缩量标准': '< 最高量30%'
}
```

### 仓位管理共享原则

```python
POSITION_SHARED_PRINCIPLES = {
    '单股最大仓�?: '20%',
    '同一板块最�?: '40%',
    '新仓试单': '10%',
    '恐慌效应>70%': '空仓信号'
}
```

### 止损共享标准

```python
STOP_LOSS_SHARED = {
    '单笔亏损': '<= 7%',
    '单日亏损': '<= 10%',
    '连续2天亏�?: '降仓50%'
}
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v2.0 | 2026-03-28 | 新增：乔帮主完整策略(S106)、小鳄鱼补充(S107)、Asking炒单(S108)、令胡冲超跌(S109)�?2科比价�?S110)、波段操�?S111)、首板战�?S112)、情绪周�?S113)、宁波敢死队(S114)、瑞鹤仙熊市(S115)、章盟主三线(S116)、综合要�?S117-S120) |
