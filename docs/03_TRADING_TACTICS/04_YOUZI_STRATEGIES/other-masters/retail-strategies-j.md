---
module_id: TACTICS_DOC_001
version: 1.8.0
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

# retail-strategies-j.md

# 游资策略补充 (S077-S090)

> 遗漏内容整合补充第三部分
>
> **版本**：v1.8
> **日期**：2026-03-28
> **策略池**：清风量化交易系统4.0
>
> **配套文档**：
> - [retail-strategies-i.md](./retail-strategies-i.md) - S068-S076
> -  - 市场状态

---

## 1. 赢面计算与仓位管理 (S077)

> 来源：附录BL
>
> 万狮虎养家心法核心

### 1.1 赢面计算

```python
class WinProbabilityCalculator:
    """
    赢面计算器
    综合考虑市场环境、个股特征、催化剂
    """

    def calc_win_probability(self, market_data, stock_data):
        """
        计算赢面
        """
        factors = {}

        if market_data['趋势'] == '上升':
            factors['市场趋势'] = 0.3
        elif market_data['趋势'] == '震荡':
            factors['市场趋势'] = 0.15
        else:
            factors['市场趋势'] = 0

        if market_data['赚钱效应'] > 0.6:
            factors['赚钱效应'] = 0.25
        elif market_data['赚钱效应'] > 0.4:
            factors['赚钱效应'] = 0.15
        else:
            factors['赚钱效应'] = 0

        if stock_data['RSI'] < 70 and stock_data['RSI'] > 30:
            factors['个股动量'] = 0.2
        else:
            factors['个股动量'] = 0

        if stock_data.get('催化剂', None):
            factors['催化剂'] = 0.25
        else:
            factors['催化剂'] = 0

        total_win_prob = sum(factors.values())

        return {
            'win_probability': total_win_prob,
            'factors': factors,
            'action': '买入' if total_win_prob >= 0.6 else '观望' if total_win_prob >= 0.5 else '放弃'
        }

    def calc_position_by_win_prob(self, win_prob):
        """
        根据赢面计算仓位
        """
        if win_prob > 0.8:
            return {'仓位': 1.0, '类型': '满仓'}
        elif win_prob > 0.7:
            return {'仓位': 0.8, '类型': '重仓'}
        elif win_prob > 0.6:
            return {'仓位': 0.5, '类型': '半仓'}
        elif win_prob >= 0.5:
            return {'仓位': 0.3, '类型': '轻仓'}
        else:
            return {'仓位': 0, '类型': '空仓'}
```

### 1.2 操作频率量化

```python
class OperationFrequencyController:
    """
    操作频率量化
    行情好：多操作；行情差：少操作
    """

    def calc_optimal_frequency(self, market_data):
        """
        计算最优操作频率
        """
        profit_ratio = market_data['赚钱效应']

        if profit_ratio > 0.6:
            return {
                '行情': '好',
                '操作频率': '高',
                '每日交易次数上限': 5,
                '持仓时间': '1-3天',
                '成功率要求': 0.6
            }
        elif profit_ratio > 0.4:
            return {
                '行情': '中',
                '操作频率': '中',
                '每日交易次数上限': 3,
                '持仓时间': '3-5天',
                '成功率要求': 0.5
            }
        else:
            return {
                '行情': '差',
                '操作频率': '低',
                '每日交易次数上限': 1,
                '持仓时间': '5-10天',
                '成功率要求': 0.4
            }
```

---

## 2. 实战案例量化分析 (S078)

> 来源：附录BJ
>
> 实战案例量化

### 2.1 超跌反弹实操

```python
class OvershootReboundPractice:
    """
    超跌反弹实操量化
    """

    def check_environment(self, market_data):
        """
        环境判断
        """
        conditions = {}

        conditions['大盘超跌'] = (
            market_data['连续下跌天数'] >= 3 and
            market_data['累计跌幅'] > 0.05
        )

        conditions['市场温度低'] = market_data['市场温度'] < 50
        conditions['恐慌效应高'] = market_data['恐慌效应'] > 0.5

        return conditions

    def select_stock(self, overshoot_stocks):
        """
        选股
        前期强势股、曾经赚过大钱的板块、分时底背离
        """
        candidates = []

        for stock in overshoot_stocks:
            score = 0

            if stock['前期涨幅排名'] <= 20:
                score += 0.3

            if stock['板块历史收益'] > 0:
                score += 0.3

            if stock['分时底背离']:
                score += 0.4

            if score >= 0.7:
                candidates.append({'stock': stock, 'score': score})

        return sorted(candidates, key=lambda x: x['score'], reverse=True)

    def execute_buy(self, stock):
        """
        买入
        缩量回调到均线、分时不创新低，放量阳线出现
        """
        buy_signals = {
            '缩量回调到均线': stock['成交量'] < stock['最高成交量'] * 0.5,
            '分时不创新低': stock['分时低点'] > stock['昨日收盘'],
            '放量阳线': stock['涨幅'] > 0.03 and stock['成交量'] > stock['均量'] * 1.5
        }

        if sum(buy_signals.values()) >= 2:
            return {
                'action': '买入',
                'entry_price': stock['当前价格'],
                'stop_loss': stock['买入价'] * 0.95
            }

        return {'action': '观望'}

    def execute_sell(self, holding_stock):
        """
        卖出
        反弹滞涨卖、5%止损、3天不涨卖
        """
        if holding_stock['涨幅'] > 0.15 and holding_stock['成交量缩量']:
            return {'action': '卖出', 'reason': '反弹滞涨'}

        if holding_stock['亏损比例'] >= 0.05:
            return {'action': '止损', 'reason': '亏损5%'}

        if holding_stock['持有天数'] >= 3 and holding_stock['累计涨跌'] < 0.02:
            return {'action': '卖出', 'reason': '3天不涨'}

        return {'action': '持有'}
```

---

## 3. 综合量化交易清单 (S079)

> 来源：附录BK
>
> 完整交易清单

### 3.1 选股量化清单

```python
class ComprehensiveTradingChecklist:
    """
    综合量化交易清单
    """

    SELECTION_CONDITIONS = {
        '涨幅要求': ('>', 0.07, '放量阳线'),
        '成交量要求': ('>', 1.5, '倍量'),
        '换手率要求': ('>', 0.05, '5%以上'),
        '封板时间': ('<=', '14:00', '早板优先')
    }

    BUY_CONDITIONS = {
        '买入时机1': '突破5日线且放量',
        '买入时机2': '回调到支撑位缩量',
        '买入时机3': '首板后第二天高开3-7%',
        '买入时机4': '市场情绪好转时'
    }

    SELL_CONDITIONS = {
        '卖出时机1': '封板失败第一时间卖',
        '卖出时机2': '第二天冲高回落卖',
        '卖出时机3': '达到7%收益止盈',
        '卖出时机4': '亏损5%无条件止损'
    }

    POSITION_RULES = {
        '单股上限': 0.2,
        '同一板块上限': 0.4,
        '新仓试单上限': 0.1,
        '总仓位上限': 0.8
    }

    def check_selection(self, stock):
        """检查选股条件"""
        checks = {
            '涨幅': stock['change_pct'] > 0.07,
            '量比': stock['volume_ratio'] > 1.5,
            '换手率': stock['turnover_rate'] > 0.05,
            '封板时间': stock['封板时间'] <= '14:00'
        }

        passed = sum(checks.values())
        return {
            'passed': passed,
            'total': len(checks),
            'pass_rate': passed / len(checks),
            'all_passed': passed == len(checks)
        }
```

---

## 4. 游资席位量化 (S080-S089)

> 来源：附录BZ
>
> 九大游资席位量化体系

### 4.1 席位概述

```python
class TradingSeatQuantifier:
    """
    游资席位量化

    席位分类：
    - 顶级席位：光大/平安/招商等
    - 一线席位：华鑫/溧阳路等
    - 活跃席位：各券商营业部
    """

    SEAT_CATEGORIES = {
        '顶级': ['光大证券北京', '平安证券北京', '招商证券深圳'],
        '一线': ['华鑫证券上海', '溧阳路营业部', '杭州飞云江'],
        '活跃': ['各券商主力营业部']
    }

    def analyze_seat_behavior(self, seat_name, historical_data):
        """
        分析席位行为
        """
        if seat_name in self.SEAT_CATEGORIES['顶级']:
            return {
                'level': '顶级',
                'capital_scale': '大资金',
                'holding_period': '1-3天',
                'typical_action': '引导龙头'
            }
        elif seat_name in self.SEAT_CATEGORIES['一线']:
            return {
                'level': '一线',
                'capital_scale': '中等资金',
                'holding_period': '超短',
                'typical_action': '打板接力'
            }
        return {
            'level': '活跃',
            'capital_scale': '不确定',
            'holding_period': '不定',
            'typical_action': '跟随'
        }
```

### 4.2 席位跟随策略

```python
class SeatFollowStrategy:
    """
    席位跟随策略
    """

    def select_seat_stocks(self, market_data, top_seats):
        """
        选取顶级席位参与的股票
        """
        candidates = []

        for stock in market_data:
            seat_participation = stock.get('席位', [])

            for seat in seat_participation:
                if seat in top_seats:
                    candidates.append({
                        'stock': stock,
                        'seat': seat,
                        'participation_level': 'high'
                    })
                    break

        return sorted(candidates, key=lambda x: x['stock']['涨幅'], reverse=True)
```

---

## 5. 机构资金行为模式 (S090)

> 来源：附录AE
>
> 机构资金行为历史模式库

### 5.1 机构行为识别

```python
class InstitutionBehaviorDetector:
    """
    机构行为识别
    """

    BEHAVIOR_PATTERNS = {
        '建仓': {
            '特征': ['持续小单买入', '股价小幅上涨', '成交量温和放大'],
            '时间周期': '数周至数月'
        },
        '拉升': {
            '特征': ['大单连续买入', '快速拉升股价', '成交量显著放大'],
            '时间周期': '数日至数周'
        },
        '出货': {
            '特征': ['大单卖出', '股价滞涨', '成交量异常放大'],
            '时间周期': '数日至数周'
        },
        '洗盘': {
            '特征': ['对倒打压', '成交量放大但股价不跌', '尾盘拉升'],
            '时间周期': '数日至数周'
        }
    }

    def detect_behavior(self, order_flow_data):
        """
        检测机构行为
        """
        large_order_ratio = order_flow_data['large_order_amount'] / order_flow_data['total_amount']

        if large_order_ratio > 0.5 and order_flow_data['net_flow'] > 0:
            return {
                'behavior': '建仓或拉升',
                'confidence': large_order_ratio,
                'suggestion': '关注'
            }
        elif large_order_ratio > 0.4 and order_flow_data['net_flow'] < 0:
            return {
                'behavior': '出货',
                'confidence': large_order_ratio,
                'suggestion': '警惕'
            }
        elif order_flow_data.get('wash_pattern', False):
            return {
                'behavior': '洗盘',
                'confidence': 0.6,
                'suggestion': '持有'
            }

        return {'behavior': '不明', 'confidence': 0}

    def calculate_institution_position(self, stock_data):
        """
        计算机构持仓比例
        """
        return stock_data.get('机构持仓比例', 0)
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.8 | 2026-03-28 | 新增：赢面计算(S077)、实战案例(S078)、综合清单(S079)、游资席位(S080-S089)、机构行为(S090) |
