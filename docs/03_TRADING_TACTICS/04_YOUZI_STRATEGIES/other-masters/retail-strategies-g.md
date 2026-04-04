---
module_id: TACTICS_YOUZI_OTHER_G_001
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
---

# 游资量化策略�?- 第七部分

> 顶级游资交易思想量化提炼（七�?
>
> **配套文档**�?
> - 主文档：
> - 策略池索引：[index.md](../../05_STRATEGY_POOL/index.md)

***

> **说明**：这些策略来自A股顶级游资的经验总结，已抽象为量化规则，需历史回测验证有效性后再入�?

***

## 1. 徐翔/泽熙投资策略

### S050: 泽熙逆向思维投资

| 属�?| 内容 |
|------|------|
| 策略编号 | S050 |
| 策略名称 | 泽熙逆向思维投资 |
| 来源 | 徐翔/泽熙 |
| 适用市场 | 任何市场 |
| 风险等级 | �?|
| 持仓周期 | 5-30�?|

**核心理念**：市场最热门时要警惕，别人贪婪我恐惧，别人恐惧我贪婪

**量化规则**�?
- 市场报告一片看好时悄悄出局
- 行情最火爆、涨停满屏时心生寒意
- 逆向投资：跌停板买入，涨停板卖出

```python
class ZexiReverseThinkingQuantifier(BaseStrategy):
    """泽熙逆向思维投资"""

    CORE_PRINCIPLES = {
        '逆向思维': {
            '市场最热门时要警惕': '特别警惕',
            '别人贪婪我恐�?: '卖在阶段顶部',
            '别人恐惧我贪�?: '买在阶段底部'
        },
        '卖出信号': {
            '报告一致�?: '市场报告一片看�?,
            '凌厉上涨': '股价凌厉上涨',
            '操作': '悄悄出局'
        },
        '买入信号': {
            '恐慌时刻': '市场最恐慌�?,
            '跌停�?: '可考虑买入',
            '前提': '有基本面支撑'
        }
    }

    def __init__(self):
        super().__init__("泽熙逆向思维投资", "S050")
        self.market_states = [MarketState.ANY]
        self.parameters = {
            'hot_sector_threshold': 0.8,
            'limit_down_to_buy': True,
            'limit_up_to_sell': True
        }

    def detect_reverse_timing(self, market_data):
        """
        检测逆向操作时机
        """
        params = self.parameters
        signals = {}

        if market_data.get('赚钱效应', 0.5) > params['hot_sector_threshold']:
            signals['市场过热'] = -0.3

        if market_data.get('涨停家数', 0) > 100:
            signals['涨停满屏'] = -0.3

        if market_data.get('跌停家数', 0) > 50:
            signals['市场恐慌'] = 0.3

        if market_data.get('报告一致�?, 0) > 0.8:
            signals['一致预�?] = -0.2

        total = sum(signals.values())

        if total < -0.3:
            return {'action': '减仓', 'confidence': abs(total)}
        elif total > 0.3:
            return {'action': '关注', 'confidence': total}

        return {'action': '观望', 'confidence': 0}
```

**逆向信号**�?
| 信号 | 评分 | 操作 |
|------|------|------|
| 市场过热（赚钱效�?80%�?| -0.3 | 减仓 |
| 涨停满屏�?100家） | -0.3 | 减仓 |
| 市场恐慌（跌�?50家） | +0.3 | 关注买入 |
| 报告一致预期（>80%�?| -0.2 | 减仓 |

***

## 2. 著名刺客实战策略

### S051: 著名刺客�?0万到800�?

| 属�?| 内容 |
|------|------|
| 策略编号 | S051 |
| 策略名称 | 著名刺客实战 |
| 来源 | 著名刺客 |
| 适用市场 | 强势市场 |
| 风险等级 | �?|
| 持仓周期 | 1-3�?|

**核心理念**：跟庄操作、涨停板战法、强势股回调

**量化规则**�?
- 只做强势股回�?
- 涨停板敢死队
- 跟庄操作：看龙虎榜席�?

```python
class FamousAssassinSystem(BaseStrategy):
    """著名刺客实战系统"""

    CORE_PRINCIPLES = {
        '跟庄操作': {
            '龙虎�?: '观察席位',
            '机构买入': '积极信号',
            '游资卖出': '警惕'
        },
        '涨停板战�?: {
            '封板坚定': '首�?,
            '炸板率低': '重要',
            '换手充分': '必要条件'
        },
        '强势股回�?: {
            '回调幅度': '5%-15%',
            '缩量': '量能萎缩',
            '支撑�?: '均线支撑'
        }
    }

    def __init__(self):
        super().__init__("著名刺客实战", "S051")
        self.market_states = [MarketState.YAO, MarketState.BULL]
        self.parameters = {
            'min_limitup_days': 1,
            'max_pullback': 0.15,
            'min_volume_ratio': 0.7
        }

    def analyze_limitup_stocks(self, stock_data):
        """
        分析涨停股机�?
        """
        params = self.parameters

        is_limitup = stock_data.get('is_limit_up', False)
        continuous_days = stock_data.get('连续涨停天数', 0)

        if not is_limitup or continuous_days < params['min_limitup_days']:
            return {'can_buy': False, 'reason': '非涨停或非连�?}

        pullback = (stock_data.get('最高价', 0) - stock_data['close']) / stock_data.get('最高价', 1)
        if pullback > params['max_pullback']:
            return {'can_buy': False, 'reason': '回调过大'}

        volume_ratio = stock_data['成交�?] / stock_data.get('均量', stock_data['成交�?])
        if volume_ratio < params['min_volume_ratio']:
            return {'can_buy': False, 'reason': '量能不足'}

        return {'can_buy': True, 'confidence': 0.7, 'pullback': pullback}
```

**买入条件**�?
- 连板�?�?
- 回调幅度5%-15%
- 量比�?.7
- 均线有支�?

***

## 3. 实战案例涨停启明�?

### S052: 涨停启明星策�?

| 属�?| 内容 |
|------|------|
| 策略编号 | S052 |
| 策略名称 | 涨停启明�?|
| 来源 | 综合 |
| 适用市场 | 弱势市场 |
| 风险等级 | �?|
| 持仓周期 | 3-10�?|

**核心理念**：弱势转折点搏击法，涨停启明星形�?

**量化规则**�?
- 市场连续普跌后出现涨停阳�?
- 连板股绝迹时率先反弹
- 领头羊：关键支撑位不跌破，走�?连板

```python
class LimitUpMorningStar(BaseStrategy):
    """涨停启明星策�?""

    CORE_PRINCIPLES = {
        '市场转折点识�?: {
            '连续普跌': '连续多个交易日大多数股票下跌',
            '连板股绝�?: '3连板及以上个股数量稀�?,
            '接力氛围冰冷': '市场空间板被压制'
        },
        '领头羊选择': {
            '逆势抗跌': '关键支撑位不跌破',
            '技术确�?: '走出2连板形�?,
            '反弹确认': '次日市场企稳反弹'
        }
    }

    def __init__(self):
        super().__init__("涨停启明�?, "S052")
        self.market_states = [MarketState.BEAR, MarketState.SHOCK]
        self.parameters = {
            'continuous_decline_days': 3,
            'limitup_3board_count': 2,
            'min_continuous_limitup': 2
        }

    def detect_morning_star(self, market_data, stock_data):
        """
        检测涨停启明星信号
        """
        params = self.parameters

        continuous_decline = market_data.get('连续下跌天数', 0) >= params['continuous_decline_days']
        few_3board = market_data.get('3连板以上数量', 999) <= params['limitup_3board_count']

        if not (continuous_decline and few_3board):
            return {'is_morning_star': False, 'reason': '未满足市场条�?}

        is_anti_declining = stock_data['close'] > stock_data.get('关键支撑', stock_data['close'])
        has_2board = stock_data.get('连续涨停天数', 0) >= params['min_continuous_limitup']

        if is_anti_declining and has_2board:
            return {
                'is_morning_star': True,
                'confidence': 0.8,
                'action': '积极买入'
            }

        return {'is_morning_star': False, 'reason': '个股条件不满�?}
```

**买入条件**�?
- 市场连续下跌�?�?
- 3连板以上个股�?�?
- 个股逆势抗跌
- 走出2连板形�?

***

## 4. 综合量化交易清单

### S053: 综合量化交易清单

| 属�?| 内容 |
|------|------|
| 策略编号 | S053 |
| 策略名称 | 综合量化交易清单 |
| 来源 | 综合 |
| 适用市场 | 任何市场 |
| 风险等级 | �?|
| 持仓周期 | 1-10�?|

**核心理念**：完整选股/买入/卖出/仓位清单 checklist

**量化规则**�?
- 选股：涨�?7%，放量阳线，涨停优先
- 题材：市场认可的故事，资金活跃，符合热点
- 买入：二板定龙头�?0点前封板，跟风股出现
- 卖出：亏�?%止损，涨15-30%卖一�?

```python
class ComprehensiveChecklist(BaseStrategy):
    """综合量化交易清单"""

    def __init__(self):
        super().__init__("综合量化交易清单", "S053")
        self.market_states = [MarketState.ANY]
        self.parameters = {
            'min_rise_ratio': 0.07,
            'min_volume_ratio': 1.5,
            'min_turnover_rate': 0.10,
            'max_turnover_rate': 0.30,
            'stop_loss_ratio': 0.07,
            'profit_take1_ratio': 0.15,
            'profit_take2_ratio': 0.30,
            'trail_stop_ratio': 0.08
        }

    def check_stock_selection(self, stock_data):
        """
        选股清单检�?
        """
        params = self.parameters
        checks = {}

        checks['涨幅>7%'] = stock_data.get('涨幅', 0) > params['min_rise_ratio']
        checks['放量阳线'] = (
            stock_data.get('涨幅', 0) > params['min_rise_ratio'] and
            stock_data.get('成交�?, 0) > stock_data.get('均量', 0) * params['min_volume_ratio']
        )
        checks['涨停优先'] = stock_data.get('is_limit_up', False)
        checks['相对低位'] = stock_data.get('距年内低�?, 0) > 0.2

        passed = sum(checks.values())
        return {'eligible': passed >= 3, 'passed_count': passed, 'checks': checks}

    def check_buy_conditions(self, stock_data, market_data):
        """
        买入清单检�?
        """
        params = self.parameters
        checks = {}

        checks['二板'] = stock_data.get('连续涨停天数', 0) >= 2
        checks['早盘封板'] = stock_data.get('封板时间', 24) <= 10
        checks['有跟�?] = market_data.get('跟风涨停�?, 0) >= 1
        checks['换手充分'] = params['min_turnover_rate'] < stock_data.get('换手�?, 0) < params['max_turnover_rate']

        passed = sum(checks.values())
        return {'eligible': passed >= 3, 'passed_count': passed, 'checks': checks}

    def check_sell_conditions(self, holding_stock):
        """
        卖出清单检�?
        """
        params = self.parameters
        checks = {}

        loss_ratio = holding_stock.get('亏损比例', 0)
        profit_ratio = holding_stock.get('盈利比例', 0)
        trail_ratio = holding_stock.get('距最高点回落比例', 0)

        checks['亏损7%止损'] = loss_ratio >= params['stop_loss_ratio']
        checks['�?5%卖一�?] = profit_ratio >= params['profit_take1_ratio']
        checks['�?0%清仓'] = profit_ratio >= params['profit_take2_ratio']
        checks['回落8%清仓'] = trail_ratio >= params['trail_stop_ratio']

        if checks['亏损7%止损']:
            return {'action': '止损', 'reason': '亏损超过7%'}
        if checks['�?0%清仓'] or checks['回落8%清仓']:
            return {'action': '清仓', 'reason': '达到目标位或回落'}
        if checks['�?5%卖一�?]:
            return {'action': '卖出一�?, 'reason': '�?5%部分止盈'}

        return {'action': '持有'}
```

**选股清单**（通过�?项）�?
| 条件 | 标准 |
|------|------|
| 涨幅>7% | �?|
| 放量阳线 | 涨幅>7% + 量比>1.5 |
| 涨停优先 | is_limit_up=True |
| 相对低位 | 距年内低�?20% |

**买入清单**（通过�?项）�?
| 条件 | 标准 |
|------|------|
| 二板 | 连续涨停�?�?|
| 早盘封板 | 封板时间�?0:00 |
| 有跟�?| 跟风涨停数≥1 |
| 换手充分 | 换手�?0%-30% |

**卖出清单**�?
| 条件 | 操作 |
|------|------|
| 亏损�?% | 止损 |
| 涨≥15% | 卖出一�?|
| 涨≥30%或回�?% | 清仓 |

***

## 5. 万狮虎养家心�?

### S054: 万狮虎择时系�?

| 属�?| 内容 |
|------|------|
| 策略编号 | S054 |
| 策略名称 | 万狮虎择时系�?|
| 来源 | 万狮�?|
| 适用市场 | 任何市场 |
| 风险等级 | �?|
| 持仓周期 | 1-10�?|

**核心理念**：赢�?50%才操作，赢面决定仓位

**量化规则**�?
- 赢面计算：市场趋�?赚钱效应+个股动量+催化�?
- 赢面>80%：满�?
- 赢面>60%：半仓以�?
- 赢面<50%：空�?

```python
class WanShiHuTimingSystem(BaseStrategy):
    """万狮虎择时系�?""

    CORE_PRINCIPLES = {
        '核心原则': '赢面 > 50%才操�?,
        '仓位依据': '赢面决定仓位',
        '操作频率': '行情好：多操作；行情差：少操�?
    }

    def __init__(self):
        super().__init__("万狮虎择时系�?, "S054")
        self.market_states = [MarketState.ANY]
        self.parameters = {
            'win_prob_threshold': 0.5,
            'buy_win_prob': 0.6,
            'market_trend_weight': 0.3,
            'profit_effect_weight': 0.25,
            'momentum_weight': 0.2,
            'catalyst_weight': 0.25
        }

    def calc_win_probability(self, market_data, stock_data):
        """
        计算赢面
        """
        params = self.parameters
        factors = {}

        if market_data.get('趋势') == '上升':
            factors['市场趋势'] = params['market_trend_weight']
        elif market_data.get('趋势') == '震荡':
            factors['市场趋势'] = params['market_trend_weight'] * 0.5
        else:
            factors['市场趋势'] = 0

        profit_effect = market_data.get('赚钱效应', 0)
        if profit_effect > 0.6:
            factors['赚钱效应'] = params['profit_effect_weight']
        elif profit_effect > 0.4:
            factors['赚钱效应'] = params['profit_effect_weight'] * 0.6
        else:
            factors['赚钱效应'] = 0

        rsi = stock_data.get('RSI', 50)
        if 30 < rsi < 70:
            factors['个股动量'] = params['momentum_weight']
        else:
            factors['个股动量'] = 0

        if stock_data.get('催化�?):
            factors['催化�?] = params['catalyst_weight']
        else:
            factors['催化�?] = 0

        total_win_prob = sum(factors.values())

        if total_win_prob > 0.8:
            position = 1.0
        elif total_win_prob > 0.7:
            position = 0.8
        elif total_win_prob > 0.6:
            position = 0.5
        elif total_win_prob >= 0.5:
            position = 0.3
        else:
            position = 0

        return {
            'win_probability': total_win_prob,
            'position': position,
            'action': '买入' if total_win_prob >= params['buy_win_prob'] else '观望'
        }
```

**赢面评分**�?
| 因素 | 权重 | 条件 | 贡献 |
|------|------|------|------|
| 市场趋势 | 30% | 上升 | +0.3 |
| 赚钱效应 | 25% | >60% | +0.25 |
| 个股动量 | 20% | RSI�?0-70 | +0.2 |
| 催化�?| 25% | �?| +0.25 |

**仓位配置**�?
| 赢面 | 仓位 |
|------|------|
| >80% | 100% |
| 70%-80% | 80% |
| 60%-70% | 50% |
| 50%-60% | 30% |
| <50% | 0% |

***

## 6. 职业炒手王元杰策�?

### S055: 职业炒手完整策略

| 属�?| 内容 |
|------|------|
| 策略编号 | S055 |
| 策略名称 | 职业炒手王元�?|
| 来源 | 王元�?|
| 适用市场 | 强势市场 |
| 风险等级 | �?|
| 持仓周期 | 1-3�?|

**核心理念**：职业炒手完整体系，龙头战法

**量化规则**�?
- 龙头确认：连续涨停板
- 板块效应：跟风股数量
- 仓位管理：分仓操�?

```python
class ProfessionalTraderSystem(BaseStrategy):
    """职业炒手完整策略"""

    CORE_PRINCIPLES = {
        '龙头战法': {
            '确认龙头': '连续涨停�?,
            '板块效应': '跟风股数�?,
            '操作节奏': '分歧转一致时买入'
        },
        '仓位管理': {
            '分仓操作': True,
            '单股上限': 0.2,
            '同一板块上限': 0.4
        }
    }

    def __init__(self):
        super().__init__("职业炒手完整策略", "S055")
        self.market_states = [MarketState.YAO, MarketState.BULL]
        self.parameters = {
            'min_limitup_days': 2,
            'min_follow_stocks': 2,
            'max_single_position': 0.2,
            'max_sector_position': 0.4
        }

    def confirm_dragon(self, stock_data, sector_data):
        """
        确认龙头
        """
        params = self.parameters

        continuous_limitup = stock_data.get('连续涨停天数', 0)
        follow_stocks = sector_data.get('跟风涨停�?, 0)

        if continuous_limitup >= params['min_limitup_days'] and follow_stocks >= params['min_follow_stocks']:
            return {
                'is_dragon': True,
                'confidence': 0.8,
                'action': '积极买入'
            }

        return {'is_dragon': False, 'confidence': 0, 'action': '观察'}
```

**龙头确认条件**�?
| 条件 | 标准 |
|------|------|
| 连续涨停 | �?�?|
| 跟风股数�?| �?�?|

***

## 7. 游资查漏补缺

### S056: 小鳄鱼等补充策略

| 属�?| 内容 |
|------|------|
| 策略编号 | S056 |
| 策略名称 | 小鳄鱼补充策�?|
| 来源 | 小鳄鱼等 |
| 适用市场 | 强势市场 |
| 风险等级 | �?|
| 持仓周期 | 1-3�?|

**核心理念**：新生代游资手法，手法激进、反应迅�?

**量化规则**�?
- 二板四种买入方式：低�?半路/打板/竞价
- 首板筛选：题材/位置/换手

```python
class YoungCrocodileSupplement(BaseStrategy):
    """小鳄鱼等补充策略"""

    def __init__(self):
        super().__init__("小鳄鱼补充策�?, "S056")
        self.market_states = [MarketState.YAO, MarketState.BULL]
        self.parameters = {
            'low_pullback_min': 0.05,
            'half_road_angle_min': 45,
            'near_limit_max': 0.02,
            'auction_rise_min': 0.05
        }

    def select_entry_method(self, stock_data, intraday_data):
        """
        选择二板买入方式
        """
        params = self.parameters

        if intraday_data.get('回调幅度', 0) >= params['low_pullback_min']:
            return {'method': '低吸', 'confidence': 0.7}

        if intraday_data.get('上涨角度', 0) > params['half_road_angle_min']:
            return {'method': '半路', 'confidence': 0.6}

        if intraday_data.get('距涨�?, 1) < params['near_limit_max']:
            return {'method': '打板', 'confidence': 0.8}

        if intraday_data.get('竞价涨幅', 0) > params['auction_rise_min']:
            return {'method': '竞价', 'confidence': 0.7}

        return {'method': '观望', 'confidence': 0}
```

**二板买入方式**�?
| 方式 | 条件 | 信心�?|
|------|------|--------|
| 低吸 | 回调幅度�?% | 70% |
| 半路 | 上涨角度>45�?| 60% |
| 打板 | 距涨�?2% | 80% |
| 竞价 | 竞价涨幅>5% | 70% |

***

## 8. 凡倍无名策�?

### S057: 凡倍无名次新股二板

| 属�?| 内容 |
|------|------|
| 策略编号 | S057 |
| 策略名称 | 凡倍无名次新股二板 |
| 来源 | 凡倍无�?|
| 适用市场 | 强势市场 |
| 风险等级 | �?|
| 持仓周期 | 1-3�?|

**核心理念**：次新股量化分析，二板模�?

**量化规则**�?
- 次新股特征：上市时间短，筹码干净
- 二板模式：强势确�?
- 竞价分析：开盘表�?

```python
class FanbeiSubNewStock(BaseStrategy):
    """凡倍无名次新股二板"""

    def __init__(self):
        super().__init__("凡倍无名次新股二板", "S057")
        self.market_states = [MarketState.YAO, MarketState.BULL]
        self.parameters = {
            'new_stock_days_max': 365,
            'min_turnover_rate': 0.15,
            'auction_volume_min': 10000000
        }

    def check_new_stock(self, stock_data):
        """
        检查次新股特征
        """
        params = self.parameters

        days_since_listed = stock_data.get('上市天数', 999)
        if days_since_listed > params['new_stock_days_max']:
            return {'is_new_stock': False}

        turnover_rate = stock_data.get('换手�?, 0)
        if turnover_rate < params['min_turnover_rate']:
            return {'is_new_stock': False, 'reason': '换手率不�?}

        return {'is_new_stock': True, 'confidence': 0.7}

    def check_second_board(self, stock_data, auction_data):
        """
        检查二板模�?
        """
        params = self.parameters

        if not self.check_new_stock(stock_data)['is_new_stock']:
            return {'can_buy': False}

        continuous_limitup = stock_data.get('连续涨停天数', 0)
        auction_volume = auction_data.get('竞价成交�?, 0)

        if continuous_limitup >= 2 and auction_volume >= params['auction_volume_min']:
            return {'can_buy': True, 'confidence': 0.8}

        return {'can_buy': False}
```

**次新股二板条�?*�?
| 条件 | 标准 |
|------|------|
| 上市天数 | �?65�?|
| 换手�?| �?5% |
| 连续涨停 | �?�?|
| 竞价成交�?| �?000�?|

***

## 9. 顶级游资汇编

### S058: 欢乐海岸/成都帮等汇�?

| 属�?| 内容 |
|------|------|
| 策略编号 | S058 |
| 策略名称 | 顶级游资汇�?|
| 来源 | 欢乐海岸/成都帮等 |
| 适用市场 | 强势市场 |
| 风险等级 | �?|
| 持仓周期 | 1-3�?|

**核心理念**：各顶级游资风格汇总，席位资金跟踪

**量化规则**�?
- 欢乐海岸：高位锁仓，龙头战法
- 成都帮：首板操作，低位挖�?
- 资金跟踪：席位净买入

```python
class TopTraderSummary(BaseStrategy):
    """顶级游资汇�?""

    def __init__(self):
        super().__init__("顶级游资汇�?, "S058")
        self.market_states = [MarketState.YAO, MarketState.BULL]
        self.parameters = {
            'huanle_sea_limitup_days_min': 3,
            'chengdu_first_limitup': True,
            'seat_net_buy_min': 50000000
        }

    def analyze_huanle_sea(self, stock_data, lhb_data):
        """
        欢乐海岸风格分析
        """
        params = self.parameters

        continuous_limitup = stock_data.get('连续涨停天数', 0)
        seat_net_buy = lhb_data.get('欢乐海岸席位净买入', 0)

        if continuous_limitup >= params['huanle_sea_limitup_days_min'] and seat_net_buy > 0:
            return {
                'style': '欢乐海岸',
                'action': '高位锁仓',
                'confidence': 0.8
            }

        return {'style': None, 'action': '观望'}

    def analyze_chengdu(self, stock_data, lhb_data):
        """
        成都帮风格分�?
        """
        params = self.parameters

        is_first_limitup = stock_data.get('连续涨停天数', 0) == 1
        seat_net_buy = lhb_data.get('成都帮席位净买入', 0)

        if is_first_limitup and seat_net_buy > params['seat_net_buy_min']:
            return {
                'style': '成都�?,
                'action': '首板低位挖掘',
                'confidence': 0.7
            }

        return {'style': None, 'action': '观望'}
```

**顶级游资风格**�?
| 席位 | 风格 | 操作 | 条件 |
|------|------|------|------|
| 欢乐海岸 | 高位锁仓 | 龙头战法 | 连板�?�?+ 席位净买入 |
| 成都�?| 首板低位 | 低位挖掘 | 首板 + 席位净买入�?000�?|
| 金田�?| 涨停敢死�?| 龙头 | 连板�?�?|
| 佛山 | 一夜情 | 超短�?| 消息刺激 + 首板 |

***

## 策略汇�?

| 编号 | 策略名称 | 来源 | 适用市场 | 风险 | 持仓周期 | 核心理念 |
|------|---------|------|---------|------|---------|---------|
| S050 | 泽熙逆向思维 | 徐翔/泽熙 | 任何市场 | �?| 5-30�?| 别人恐惧我贪�?|
| S051 | 著名刺客实战 | 著名刺客 | 强势市场 | �?| 1-3�?| 跟庄操作 |
| S052 | 涨停启明�?| 综合 | 弱势市场 | �?| 3-10�?| 转折点搏�?|
| S053 | 综合量化清单 | 综合 | 任何市场 | �?| 1-10�?| checklist体系 |
| S054 | 万狮虎择�?| 万狮�?| 任何市场 | �?| 1-10�?| 赢面决定仓位 |
| S055 | 职业炒手 | 王元�?| 强势市场 | �?| 1-3�?| 龙头战法 |
| S056 | 小鳄鱼补�?| 小鳄�?| 强势市场 | �?| 1-3�?| 新生代手�?|
| S057 | 凡倍无名次�?| 凡倍无�?| 强势市场 | �?| 1-3�?| 次新股二�?|
| S058 | 顶级游资汇�?| 欢乐海岸�?| 强势市场 | �?| 1-3�?| 席位资金跟踪 |

***

## 关联战术模块

| 战术模块 | 关联策略 |
|---------|---------|
|  | S050/S052/S054 |
|  | S051/S055/S058 |
|  | S051/S058 |
|  | S053/S055/S056/S057 |