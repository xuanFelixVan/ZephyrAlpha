---
module_id: TACTICS_DOC_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# 游资量化策略库 - 第五部分

> 顶级游资交易思想量化提炼（五）
>
> **配套文档**：
> - 主文档：
> - 策略池索引：[index.md](../../05_STRATEGY_POOL/index.md)

***

> **说明**：这些策略来自A股顶级游资的经验总结，已抽象为量化规则，需历史回测验证有效性后再入池

***

## 1. 陈兄波段操作策略

### S032: 陈兄/安子元波段操作策略

| 属性 | 内容 |
|------|------|
| 策略编号 | S032 |
| 策略名称 | 陈兄波段操作 |
| 来源 | 陈兄/安子元 |
| 适用市场 | 趋势市场 |
| 风险等级 | 中 |
| 持仓周期 | 5-20天 |

**核心理念**：趋势为王、趋势线操作，上升趋势只看多不做空

**量化规则**：
- 上升趋势：MA5>MA10>MA20，回调买入
- 下降趋势：MA5<MA10<MA20，反弹卖出
- 震荡趋势：高抛低吸
- 波段目标：短线10%-20%，中线30%-50%
- 止损：-8%

```python
class SwingTraderQuantifier(BaseStrategy):
    """陈兄/安子元波段操作量化策略"""

    CORE_PRINCIPLES = {
        '趋势为王': {
            '上升趋势': '只看多不做空',
            '下降趋势': '只看空不做多',
            '震荡趋势': '高抛低吸'
        },
        '趋势线操作': {
            '上升趋势线': '回调买入点',
            '下降趋势线': '反弹卖出点',
            '突破确认': '放量突破2%'
        },
        '波段目标': {
            '短线': '10%-20%',
            '中线': '30%-50%',
            '止损': '-8%'
        }
    }

    def __init__(self):
        super().__init__("陈兄波段操作", "S032")
        self.market_states = [MarketState.BULL, MarketState.SHOCK]
        self.parameters = {
            'ma_short': 5,
            'ma_medium': 10,
            'ma_long': 20,
            'entry_ratio': 0.98,
            'stop_loss_ratio': 0.92,
            'profit_target_short': 0.15,
            'profit_target_medium': 0.30
        }

    def detect_trend(self, price_data):
        """
        检测趋势
        """
        ma_short = price_data.get(f"MA{self.parameters['ma_short']}")
        ma_long = price_data.get(f"MA{self.parameters['ma_long']}")
        current_price = price_data['close']

        if current_price > ma_short > ma_long:
            return {
                'trend': '上升',
                'action': '逢低买入',
                'support_levels': [ma_short, ma_long]
            }

        if current_price < ma_short < ma_long:
            return {
                'trend': '下降',
                'action': '逢高卖出',
                'resistance_levels': [ma_short, ma_long]
            }

        return {
            'trend': '震荡',
            'action': '高抛低吸',
            'range': [ma_long * 0.95, ma_short * 1.05]
        }

    def generate_signal(self, market_data, stock_data, market_state):
        trend_info = self.detect_trend(stock_data)

        if trend_info['trend'] == '上升':
            for level in trend_info['support_levels']:
                if stock_data['close'] >= level * self.parameters['entry_ratio']:
                    return TradingSignal(
                        code=stock_data['code'],
                        signal=SignalType.BUY,
                        confidence=0.75,
                        entry_price=level,
                        stop_loss=level * self.parameters['stop_loss_ratio'],
                        target_price=level * (1 + self.parameters['profit_target_short']),
                        position_ratio=0.20,
                        strategy_name=self.name
                    )

        elif trend_info['trend'] == '震荡':
            lower = trend_info['range'][0]
            upper = trend_info['range'][1]
            if stock_data['close'] <= lower * 1.02:
                return TradingSignal(
                    code=stock_data['code'],
                    signal=SignalType.BUY,
                    confidence=0.70,
                    entry_price=lower,
                    stop_loss=lower * 0.95,
                    target_price=upper,
                    position_ratio=0.15,
                    strategy_name=self.name
                )

        return None

    def execute_sell(self, holding_stock):
        """
        波段卖出
        """
        current_price = holding_stock['current_price']
        cost_price = holding_stock['cost_price']
        profit_ratio = (current_price - cost_price) / cost_price

        ma5 = holding_stock.get('MA5')
        ma10 = holding_stock.get('MA10')
        ma20 = holding_stock.get('MA20')

        if ma5 and ma10 and ma5 < ma10:
            return {'action': '止损', 'reason': 'MA5死叉MA10'}

        if current_price < ma20:
            return {'action': '止损', 'reason': '跌破MA20'}

        if profit_ratio >= self.parameters['profit_target_short']:
            return {'action': '止盈', 'reason': '达到目标位'}

        return {'action': '持有'}
```

**买入条件**：
- 上升趋势：回踩MA5/MA10获得支撑（+0.4分）
- 震荡趋势：价格触及震荡下沿（+0.3分）
- 放量突破趋势线（+0.3分）

**卖出条件**：
- MA5死叉MA10
- 跌破MA20
- 达到目标位

**风险控制**：
- 止损：-8%
- 波段目标：15%-30%

***

## 2. 清秋首板战法策略

### S033: 清秋/牛脾气首板战法

| 属性 | 内容 |
|------|------|
| 策略编号 | S033 |
| 策略名称 | 清秋首板战法 |
| 来源 | 清秋/牛脾气 |
| 适用市场 | 强势市场 |
| 风险等级 | 高 |
| 持仓周期 | 1-2天 |

**核心理念**：首板后次日高开、封单比例，不连板就走

**量化规则**：
- 个股首板：近期第一次涨停
- 板块首板：同一板块率先涨停
- 10点前封板更好
- 次日高开>5%买入，封单比>3%
- 止损：-3%

```python
class FirstLimitUpQuantifier(BaseStrategy):
    """清秋/牛脾气首板战法量化策略"""

    CORE_PRINCIPLES = {
        '首板筛选': {
            '个股首板': '近期第一次涨停',
            '板块首板': '同一板块率先涨停',
            '时间优先': '10点前封板更好'
        },
        '次日操作': {
            '高开': '+5%以上开盘',
            '买入条件': '封单比>3%',
            '卖出时机': '不连板就走'
        },
        '风险控制': {
            '仓位': '单股不超过20%',
            '止损': '-3%无条件止损',
            '空仓信号': '连败3次休息'
        }
    }

    def __init__(self):
        super().__init__("清秋首板战法", "S033")
        self.market_states = [MarketState.YAO, MarketState.BULL]
        self.parameters = {
            'first_limitup_days': 20,
            'seal_ratio_min': 3.0,
            'seal_time_max': 10,
            'open_ratio_min': 0.05,
            'stop_loss_ratio': 0.03
        }

    def analyze_first_limitup(self, stock_data, market_data):
        """
        分析首板机会
        """
        params = self.parameters
        signals = {}

        recent_limitup_count = stock_data.get('近期涨停次数', 0)
        if recent_limitup_count == 0:
            signals['个股首板'] = 0.2

        sector_rank = stock_data.get('板块涨停顺序', 999)
        if sector_rank == 1:
            signals['板块龙头'] = 0.3

        seal_amount = stock_data.get('涨停封单金额', 0)
        turnover = stock_data.get('成交额', 1)
        seal_ratio = seal_amount / turnover if turnover > 0 else 0
        if seal_ratio > params['seal_ratio_min']:
            signals['封单充足'] = 0.3

        seal_time = stock_data.get('封板时间', 12)
        if seal_time <= params['seal_time_max']:
            signals['早盘封板'] = 0.2

        total_score = sum(signals.values())

        if total_score >= 0.6:
            return {
                'is_good': True,
                'score': total_score,
                'action': '可参与'
            }

        return {'is_good': False, 'score': total_score, 'action': '观望'}

    def execute_next_day(self, holding_stock, next_day_data):
        """
        次日操作执行
        """
        params = self.parameters
        open_ratio = next_day_data.get('竞价涨幅', 0)

        if open_ratio >= 0.07:
            return {'action': '卖出', 'reason': '高开溢价'}

        if open_ratio < -params['stop_loss_ratio']:
            return {'action': '止损', 'reason': '低开超过3%'}

        if next_day_data.get('is_limit_up', False):
            return {'action': '继续持有', 'reason': '连板中'}

        return {'action': '卖出', 'reason': '未连板'}
```

**买入条件**：
- 个股首板（+0.2分）
- 板块龙头（+0.3分）
- 封单比>3%（+0.3分）
- 10点前封板（+0.2分）
- 总分≥0.6

**卖出条件**：
- 高开>7%开盘卖出
- 低开>3%止损
- 未连板卖出

**风险控制**：
- 单股仓位：≤20%
- 止损：-3%
- 连败3次休息

***

## 3. 灯芯人情绪周期策略

### S034: 山西L/灯芯人情绪周期

| 属性 | 内容 |
|------|------|
| 策略编号 | S034 |
| 策略名称 | 灯芯人情绪周期 |
| 来源 | 山西L/灯芯人 |
| 适用市场 | 任何市场 |
| 风险等级 | 高 |
| 持仓周期 | 1-5天 |

**核心理念**：情绪周期、龙头见顶规律，启动期重仓买入，退潮期空仓等待

**量化规则**：
- 启动期：龙头股出现，重仓买入
- 发酵期：板块扩散，持有或加仓
- 高潮期：全民讨论，分批卖出
- 退潮期：龙头跌停，空仓等待
- 龙头见顶：缩量加速/尾盘炸板/地天板

```python
class EmotionCycleQuantifier(BaseStrategy):
    """山西L/灯芯人情绪周期量化策略"""

    CORE_PRINCIPLES = {
        '情绪周期': {
            '启动期': '龙头股出现',
            '发酵期': '板块扩散',
            '高潮期': '全民讨论',
            '退潮期': '龙头跌停'
        },
        '龙头见顶规律': {
            '缩量加速': '高位连续缩量',
            '尾盘炸板': '封单撤除',
            '地天板': '主力出货'
        },
        '操作节奏': {
            '启动期': '重仓买入',
            '发酵期': '持有或加仓',
            '高潮期': '分批卖出',
            '退潮期': '空仓等待'
        }
    }

    def __init__(self):
        super().__init__("灯芯人情绪周期", "S034")
        self.market_states = [MarketState.ANY]
        self.parameters = {
            'limit_up_count_bull': 100,
            'limit_up_count_normal': 50,
            'limit_down_count': 30,
            'volume_ratio': 1.5,
            'consecutive_shrink_days': 3,
            'top_time_threshold': 14.5
        }

    def detect_emotion_cycle(self, market_data):
        """
        检测市场情绪周期
        """
        params = self.parameters
        indicators = {}

        limit_up_count = market_data.get('涨停家数', 0)
        limit_down = market_data.get('跌停家数', 0)

        if limit_down > params['limit_down_count']:
            return {
                'cycle': '退潮期',
                'action': '空仓等待',
                'confidence': 0.4
            }

        if limit_up_count > params['limit_up_count_bull']:
            return {
                'cycle': '高潮期',
                'action': '分批卖出',
                'confidence': 0.3
            }

        if limit_up_count > params['limit_up_count_normal']:
            return {
                'cycle': '发酵期',
                'action': '持有',
                'confidence': 0.3
            }

        return {
            'cycle': '启动期',
            'action': '积极买入',
            'confidence': 0.5
        }

    def detect_leader_top(self, leader_stock):
        """
        检测龙头见顶信号
        """
        params = self.parameters
        signals = []

        consecutive_days = leader_stock.get('连续缩量天数', 0)
        if consecutive_days >= params['consecutive_shrink_days']:
            signals.append(('缩量加速', 0.8))

        if leader_stock.get('炸板时间', 0) >= params['top_time_threshold']:
            signals.append(('尾盘炸板', 0.7))

        if leader_stock.get('涨幅', 0) > 0.09 and leader_stock.get('最低价') == leader_stock.get('跌停价'):
            signals.append(('地天板', 0.9))

        if signals:
            strongest = max(signals, key=lambda x: x[1])
            return {
                'is_top': True,
                'pattern': strongest[0],
                'confidence': strongest[1],
                'action': '卖出'
            }

        return {'is_top': False, 'action': '继续持有'}
```

**买入条件**：
- 启动期：重仓买入龙头
- 发酵期：持有或加仓

**卖出条件**：
- 高潮期：分批卖出
- 龙头见顶信号任一出现

**风险控制**：
- 退潮期：空仓等待
- 龙头见顶立即卖出

***

## 4. 章盟主三线归一策略

### S035: 章盟主三线归一战法

| 属性 | 内容 |
|------|------|
| 策略编号 | S035 |
| 策略名称 | 章盟主三线归一 |
| 来源 | 章盟主 |
| 适用市场 | 强势市场 |
| 风险等级 | 中 |
| 持仓周期 | 3-10天 |

**核心理念**：MA5/MA10/MA20三线同时向上发散，成交量阶梯式放大

**量化规则**：
- 三线多头：MA5>MA10>MA20
- 股价在三条均线之上
- 成交量呈现阶梯式放大
- 回踩MA5买入，止损MA20

```python
class ZhangMengzhuThreeLinesSystem(BaseStrategy):
    """章盟主三线归一战法量化"""

    CORE_PRINCIPLES = {
        '三线定义': {
            '均线': 'MA5、MA10、MA20',
            '多头排列': 'MA5 > MA10 > MA20',
            '条件1': '股价在三条均线之上',
            '条件2': '成交量阶梯式放大'
        },
        '买入条件': {
            '三线多头排列': True,
            '股价回踩MA5获得支撑': True,
            '成交量配合': '成交量 > 均量1.3倍'
        },
        '卖出条件': {
            'MA5向下死叉MA10': True,
            '股价跌破MA20': True,
            '放量滞涨': '成交量放大但价格不涨'
        }
    }

    def __init__(self):
        super().__init__("章盟主三线归一", "S035")
        self.market_states = [MarketState.BULL, MarketState.YAO]
        self.parameters = {
            'ma_periods': [5, 10, 20],
            'volume_ratio': 1.3,
            'stop_loss_ratio': 0.08
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
        avg_volume = stock_data.get('均量', volume)

        is_bullish = ma5 > ma10 > ma20
        price_above = price > ma5
        volume_increasing = volume > avg_volume * self.parameters['volume_ratio']

        if is_bullish and price_above and volume_increasing:
            return {
                'signal': '三线归一',
                'action': '买入',
                'confidence': 0.8
            }

        return {'signal': '不符合', 'action': '等待'}

    def generate_signal(self, market_data, stock_data, market_state):
        check = self.check_three_lines(stock_data)
        if check['signal'] != '三线归一':
            return None

        return TradingSignal(
            code=stock_data['code'],
            signal=SignalType.BUY,
            confidence=check['confidence'],
            entry_price=stock_data['close'],
            stop_loss=stock_data['MA20'],
            target_price=stock_data['close'] * 1.20,
            position_ratio=0.20,
            strategy_name=self.name
        )
```

**买入条件**：
- MA5>MA10>MA20多头排列
- 股价在均线上方
- 成交量>均量1.3倍

**卖出条件**：
- MA5死叉MA10
- 股价跌破MA20
- 放量滞涨

***

## 5. 佛山游资策略

### S036: 佛山游资量化策略

| 属性 | 内容 |
|------|------|
| 策略编号 | S036 |
| 策略名称 | 佛山游资 |
| 来源 | 佛山季华六路 |
| 适用市场 | 热点明确 |
| 风险等级 | 高 |
| 持仓周期 | 1-2天 |

**核心理念**：隔日超短线，一夜情，消息股/影子股/低位滞涨股

**量化规则**：
- 消息股四标准：转折性/认知不充分/资金认可/低位滞涨
- 影子股策略：跟随龙头，相似度>70%
- 超跌人气股：大盘跌>1%，个股回调>20%

```python
class FoshanTraderSystem(BaseStrategy):
    """佛山游资量化策略"""

    CORE_PRINCIPLES = {
        '消息股筛选四标准': {
            '转折性': '有趋势转折点',
            '认知不充分': '利好未被市场充分预期',
            '资金认可': '有资金持续买入',
            '低位滞涨': '相对低位启动'
        },
        '影子股策略': {
            '条件1': '有率先走强的龙头股',
            '条件2': '影子股与龙头有多重相似性',
            '条件3': '最好是首板',
            '影子相似度': '>=70%',
            '涨停时间差': '<=30分钟'
        },
        '低位滞涨股策略': {
            '跟风涨幅': '>=3%',
            '板块涨停数': '>=3只'
        }
    }

    def __init__(self):
        super().__init__("佛山游资", "S036")
        self.market_states = [MarketState.YAO, MarketState.SHOCK]
        self.parameters = {
            'position_threshold': 0.30,
            'volume_ratio_min': 1.5,
            'market_cap_max': 50,
            'follow_rise_min': 0.03,
            'sector_limitup_min': 3,
            'oversold_market_drop': 0.01,
            'oversold_stock_drop': 0.20,
            'oversold_volume_ratio': 2.0
        }

    def select_message_stock(self, stock_data, market_data):
        """
        消息股筛选
        """
        params = self.parameters
        score = 0

        if stock_data.get('位置', 100) <= params['position_threshold'] * 100:
            score += 0.25

        if stock_data.get('消息刺激时间', 999) <= 3:
            score += 0.25

        if stock_data.get('主力净流入', 0) > 0:
            score += 0.25

        if stock_data.get('量比', 0) >= params['volume_ratio_min']:
            score += 0.25

        if score >= 0.75:
            return {'action': '可买入', 'score': score}

        return {'action': '观望', 'score': score}

    def select_shadow_stock(self, leader_stock, candidate_stocks):
        """
        影子股筛选
        """
        params = self.parameters
        candidates = []

        for stock in candidate_stocks:
            similarity = self._calc_similarity(leader_stock, stock)
            time_diff = stock.get('涨停时间差', 999)

            if similarity >= params.get('影子相似度', 70) and time_diff <= 30:
                candidates.append((stock, similarity))

        if candidates:
            best = max(candidates, key=lambda x: x[1])
            return {'action': '可买入', 'stock': best[0], 'similarity': best[1]}

        return {'action': '观望'}
```

**买入条件**：
- 消息股4标准符合≥3个
- 影子股相似度>70%
- 低位滞涨：跟风涨幅>3%，板块涨停>3只

**卖出条件**：
- 次日不涨停卖出
- 达到目标位卖出

***

## 6. 金田路游资策略

### S037: 金田路涨停板敢死队

| 属性 | 内容 |
|------|------|
| 策略编号 | S037 |
| 策略名称 | 金田路涨停板敢死队 |
| 来源 | 金田路 |
| 适用市场 | 龙头明确 |
| 风险等级 | 高 |
| 持仓周期 | 1-3天 |

**核心理念**：转折点买龙头，3板之后才确认龙头

**量化规则**：
- 龙头确认：连续3板以上
- 跟风股数≥2只
- 换手率≥15%
- 封单金额≥1亿

```python
class JinTianRoadSystem(BaseStrategy):
    """金田路游资量化策略"""

    CORE_STRATEGY = {
        '风格': '涨停板敢死队',
        '特点': '转折点买龙头',
        '确认方式': '3板之后才确认龙头'
    }

    def __init__(self):
        super().__init__("金田路涨停板敢死队", "S037")
        self.market_states = [MarketState.BULL, MarketState.YAO]
        self.parameters = {
            'min_limitup_days': 3,
            'follow_stock_min': 2,
            'turnover_min': 0.15,
            'seal_amount_min': 100000000
        }

    def check_leader_confirmation(self, stock_data):
        """
        龙头确认检查
        3板定龙头
        """
        params = self.parameters
        continuous_limitup = stock_data.get('连续涨停天数', 0)

        if continuous_limitup >= params['min_limitup_days']:
            return {
                'is_confirmed': True,
                'confidence': 0.9,
                'action': '可参与'
            }
        elif continuous_limitup == 2:
            return {
                'is_confirmed': False,
                'confidence': 0.5,
                'action': '观察'
            }

        return {
            'is_confirmed': False,
            'confidence': 0.2,
            'action': '等待'
        }
```

**买入条件**：
- 连续涨停≥3天
- 跟风股≥2只
- 换手率≥15%
- 封单≥1亿

**卖出条件**：
- 破板卖出
- 达到目标位卖出

***

## 7. 作手新一/小鳄鱼策略

### S038: 新生代游资量化

| 属性 | 内容 |
|------|------|
| 策略编号 | S038 |
| 策略名称 | 作手新一/小鳄鱼 |
| 来源 | 作手新一/小鳄鱼 |
| 适用市场 | 强势市场 |
| 风险等级 | 高 |
| 持仓周期 | 1-2天 |

**核心理念**：手法激进、反应迅速，次新/龙头/情绪股，二板四种买入方式

**量化规则**：
- 低吸：分时调整后刚拐头向上，回调≥5%
- 半路：分时开始向上进攻，上涨角度>45度
- 打板：即将打板或刚打板，距涨停<2%
- 竞价：集合竞价直接买入，涨幅>5%

```python
class NewGenerationTraderSystem(BaseStrategy):
    """作手新一/小鳄鱼新生代游资量化"""

    CORE_PRINCIPLES = {
        '风格': '新生代游资',
        '特点': '手法激进、反应迅速',
        '偏好': '次新、龙头、情绪股'
    }

    def __init__(self):
        super().__init__("新生代游资", "S038")
        self.market_states = [MarketState.YAO, MarketState.BULL]
        self.parameters = {
            'low_pullback_ratio': 0.05,
            'half_road_angle': 45,
            'near_limit_ratio': 0.02,
            'auction_rise_ratio': 0.05
        }

    def select_second_board_method(self, stock_data, intraday_data):
        """
        选择二板买入方式
        """
        params = self.parameters

        if intraday_data.get('回调幅度', 0) >= params['low_pullback_ratio']:
            return {'method': '低吸', 'confidence': 0.7}

        if intraday_data.get('上涨角度', 0) > params['half_road_angle']:
            return {'method': '半路', 'confidence': 0.6}

        if intraday_data.get('距涨停', 1) < params['near_limit_ratio']:
            return {'method': '打板', 'confidence': 0.8}

        if intraday_data.get('竞价涨幅', 0) > params['auction_rise_ratio']:
            return {'method': '竞价', 'confidence': 0.7}

        return {'method': '观望', 'confidence': 0.3}
```

**买入方式**：
- 低吸：回调≥5%后拐头
- 半路：上涨角度>45度
- 打板：距涨停<2%
- 竞价：竞价涨幅>5%

**卖出条件**：
- 次日不连板卖出
- 炸板卖出

***

## 8. 打板三种方法策略

### S039: 打板三种方法量化

| 属性 | 内容 |
|------|------|
| 策略编号 | S039 |
| 策略名称 | 打板三种方法 |
| 来源 | 游资通用 |
| 适用市场 | 强势市场 |
| 风险等级 | 极高 |
| 持仓周期 | 1天 |

**核心理念**：扫板/排板/回封板，根据市场情况选择最优打板方式

**量化规则**：
- 扫板：成交量超过近期最大，放量涨停前直接扫入
- 排板：等大单被吃掉后排队
- 回封板：涨停被砸开后承接强劲，分歧转一致时买入

```python
class ThreeTypesOfLimitUp(BaseStrategy):
    """打板三种方法量化"""

    def __init__(self):
        super().__init__("打板三种方法", "S039")
        self.market_states = [MarketState.YAO]
        self.parameters = {
            'sweep_volume_ratio': 2.0,
            'queue_wait_time': 5,
            'backseal_volume_ratio': 1.5,
            'backseal_max_drop': 0.05,
            'backseal_time_limit': 14.5
        }

    def select_board_method(self, stock_data):
        """
        选择打板方式
        """
        params = self.parameters
        volume_ratio = stock_data.get('量比', 1)
        max_volume = stock_data.get('近期最大成交量', 0)
        current_volume = stock_data.get('成交量', 0)

        if max_volume > 0 and current_volume > max_volume * 1.5:
            return {'method': '扫板', 'action': '涨停前直接扫入'}

        if stock_data.get('今日炸板', False):
            if stock_data.get('最大跌幅', 0) > -params['backseal_max_drop']:
                if volume_ratio >= params['backseal_volume_ratio']:
                    return {'method': '回封板', 'action': '等待回封'}

        return {'method': '排板', 'action': '排队等待'}
```

**三种方法**：
- 扫板：量比≥2，涨停前直接扫入
- 排板：等大单消化完排队
- 回封板：炸板后跌幅<5%，量比≥1.5，14:30前回封

***

## 9. 市场炒作六阶段策略

### S040: 市场炒作六阶段量化

| 属性 | 内容 |
|------|------|
| 策略编号 | S040 |
| 策略名称 | 市场炒作六阶段 |
| 来源 | 游资通用 |
| 适用市场 | 任何市场 |
| 风险等级 | 中 |
| 持仓周期 | 阶段相关 |

**核心理念**：识别市场炒作所处阶段，根据阶段调整仓位和策略

**量化规则**：
- 启动阶段：首板涨幅≥9.5%，连板股≥2只
- 发酵阶段：跟风涨停≥3只，换手率10%-20%
- 高潮阶段：市场高度≥5板，涨停家数≥50
- 结束阶段：跌停>20只，炸板率>50%
- 反复阶段：新龙头≥3板
- 迷茫阶段：3板以上0-1只

```python
class MarketSentimentSixStages(BaseStrategy):
    """市场炒作六阶段量化判断"""

    STAGES = {
        '1_启动阶段': {
            '首板涨幅': '>=9.5%',
            '连板股数': '>=2只'
        },
        '2_发酵阶段': {
            '跟风涨停数': '>=3只',
            '换手率': '10%-20%'
        },
        '3_高潮阶段': {
            '市场高度': '>=5板',
            '涨停家数': '>=50只',
            '炸板率': '<30%'
        },
        '4_结束阶段': {
            '跌停家数': '>20只',
            '3板以上数量': 0,
            '炸板率': '>50%'
        },
        '5_反复阶段': {
            '新龙头': '>=3板'
        },
        '6_迷茫阶段': {
            '3板以上': '0-1只',
            '跌停家数': '>10只'
        }
    }

    def __init__(self):
        super().__init__("市场炒作六阶段", "S040")
        self.market_states = [MarketState.ANY]

    def detect_current_stage(self, market_data):
        """
        检测当前所处阶段
        """
        limit_up_count = market_data.get('涨停家数', 0)
        limit_down_count = market_data.get('跌停家数', 0)
        continuous_limitup = market_data.get('连板股数', 0)

        if limit_down_count > 20:
            return {'stage': '结束阶段', 'action': '空仓等待'}

        if continuous_limitup >= 5 and limit_up_count >= 50:
            return {'stage': '高潮阶段', 'action': '分批卖出'}

        if continuous_limitup >= 2 and market_data.get('新龙头出现', False):
            return {'stage': '启动阶段', 'action': '积极买入'}

        if market_data.get('跟风涨停数', 0) >= 3:
            return {'stage': '发酵阶段', 'action': '持有'}

        if market_data.get('新龙头', 0) >= 3:
            return {'stage': '反复阶段', 'action': '寻找新机会'}

        return {'stage': '迷茫阶段', 'action': '轻仓观望'}
```

**阶段操作**：
- 启动期：积极买入
- 发酵期：持有
- 高潮期：分批卖出
- 结束期：空仓等待
- 反复期：寻找新机会
- 迷茫期：轻仓观望

***

## 10. 溢价理论体系策略

### S041: 溢价理论体系量化

| 属性 | 内容 |
|------|------|
| 策略编号 | S041 |
| 策略名称 | 溢价理论体系 |
| 来源 | 游资通用 |
| 适用市场 | 任何市场 |
| 风险等级 | 中 |
| 持仓周期 | 1-5天 |

**核心理念**：大盘溢价/热点溢价/人气溢价/消息溢价综合评分

**量化规则**：
- 大盘溢价：大盘大跌末期强势股有涨停偷袭板机会
- 热点溢价：龙头有波段溢价，跟风股有套利溢价
- 人气溢价：短线反抽/中线反弹/妖股记忆
- 消息溢价：宏观政策余波/热门板块利好/个股利好

```python
class PremiumTheorySystem(BaseStrategy):
    """溢价理论体系量化"""

    PREMIUM_TYPES = {
        '大盘溢价': {
            '大盘大跌末期': '强势股有涨停偷袭板机会',
            '大盘波段大跌末期': '涨停启明星有波段机会',
            '大盘单日大阳线': '强势股溢价提高'
        },
        '热点溢价': {
            '龙头': '波段溢价',
            '跟风股': '套利溢价',
            '低位首板': '补涨机会'
        },
        '人气溢价': {
            '短线反抽': '低吸机会',
            '中线反弹': '打板机会',
            '妖股记忆': '反复炒作'
        },
        '消息溢价': {
            '宏观政策余波': '波段机会',
            '热门板块利好': '消息刺激首板',
            '个股利好': '独立行情'
        }
    }

    def __init__(self):
        super().__init__("溢价理论体系", "S041")
        self.market_states = [MarketState.ANY]
        self.parameters = {
            'market_drop_threshold': 0.05,
            'sector_drop_threshold': 0.05,
            'score_high': 0.70,
            'score_medium': 0.40,
            'target_short': 0.05,
            'target_wave': 0.20
        }

    def calc_premium_opportunity(self, stock_data, market_data):
        """
        计算溢价机会
        """
        params = self.parameters
        premium_score = 0

        if market_data.get('近期跌幅', 0) > params['market_drop_threshold']:
            premium_score += 0.3

        if stock_data.get('是龙头', False):
            premium_score += 0.3

        if stock_data.get('妖股记忆', False):
            premium_score += 0.2

        if stock_data.get('有消息刺激', False):
            premium_score += 0.2

        if premium_score >= params['score_high']:
            return {
                'opportunity': '高',
                'action': '积极参与',
                'target': f'波段>={params["target_wave"]*100}%'
            }
        elif premium_score >= params['score_medium']:
            return {
                'opportunity': '中',
                'action': '适度参与',
                'target': f'短线{params["target_short"]*100}%'
            }

        return {
            'opportunity': '低',
            'action': '观望',
            'target': None
        }
```

**溢价评分**：
- 大盘大跌>5%：+0.3分
- 是龙头：+0.3分
- 妖股记忆：+0.2分
- 有消息刺激：+0.2分

**操作建议**：
- 高分（≥0.7）：积极参与，波段目标≥20%
- 中分（≥0.4）：适度参与，短线目标5%
- 低分（<0.4）：观望

***

## 策略汇总

| 编号 | 策略名称 | 来源 | 适用市场 | 风险 | 持仓周期 | 核心理念 |
|------|---------|------|---------|------|---------|---------|
| S032 | 陈兄波段操作 | 陈兄/安子元 | 趋势市场 | 中 | 5-20天 | 趋势为王 |
| S033 | 清秋首板战法 | 清秋/牛脾气 | 强势市场 | 高 | 1-2天 | 首板后次日高开 |
| S034 | 灯芯人情绪周期 | 山西L/灯芯人 | 任何市场 | 高 | 1-5天 | 情绪周期轮动 |
| S035 | 章盟主三线归一 | 章盟主 | 强势市场 | 中 | 3-10天 | 三线多头排列 |
| S036 | 佛山游资 | 佛山季华六路 | 热点明确 | 高 | 1-2天 | 一夜情超短线 |
| S037 | 金田路涨停板敢死队 | 金田路 | 龙头明确 | 高 | 1-3天 | 3板定龙头 |
| S038 | 作手新一/小鳄鱼 | 新生代游资 | 强势市场 | 高 | 1-2天 | 二板四种买入 |
| S039 | 打板三种方法 | 游资通用 | 强势市场 | 极高 | 1天 | 扫板/排板/回封 |
| S040 | 市场炒作六阶段 | 游资通用 | 任何市场 | 中 | 阶段相关 | 识别炒作阶段 |
| S041 | 溢价理论体系 | 游资通用 | 任何市场 | 中 | 1-5天 | 溢价综合评分 |

***

## 关联战术模块

| 战术模块 | 关联策略 |
|---------|---------|
|  | S032/S035/S040 |
|  | S034/S036 |
|  | S033/S038/S039 |