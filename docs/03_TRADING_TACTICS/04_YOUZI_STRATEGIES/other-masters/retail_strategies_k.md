---
module_id: 03_TRADING_TACTICS_04_YOUZI_STRATEGIES_RETAIL_STRATEGIES_K
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理团队
responsibility:
  - retail-strategies-k.md文档
---

﻿---
module_id: TACTICS_YOUZI_OTHER_K_001
version: 1.9.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 交易策略设计与实施管理与优化维护
standard_type: 专业量化机构文档
applicable_scope: 全系?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
---
---


# retail-strategies-k.md
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


# 游资策略补充 (S091-S105)

> 遗漏内容整合补充第四部分
>
> **版本**：v1.9
> **日期**?026-03-28
> **策略?*：清风量化交易系?.0
>
> **配套文档**?
> -  - 量能周期

---

## 1. 欢乐海岸妖股战法 (S091)

> 来源：附录CB
>
> 欢乐海岸妖股量化体系

### 1.1 妖股定义标准

```python
class HuanLeHaiAnSystem:
    """
    欢乐海岸妖股战法量化
    妖股制造机，擅长龙头股高位接力
    """

    MONSTER_STOCK_CRITERIA = {
        '连续涨停?: '>=5?,
        '期间换手?: '>=15%（排除一字板?,
        '带动板块跟风': '>=3只关联股涨停',
        '市场影响?: '成为市场情绪标杆'
    }

    def check_monster_stock(self, stock_data):
        """
        检查是否是妖股
        """
        continuous_limitup = stock_data.get('连续涨停天数', 0)
        avg_turnover = stock_data.get('期间换手?, 0)
        sector_follow = stock_data.get('跟风股数', 0)

        if continuous_limitup >= 5 and avg_turnover >= 15 and sector_follow >= 3:
            return {
                'is_monster': True,
                'action': '妖股确认',
                'confidence': 0.9
            }

        return {'is_monster': False, 'action': '普通股?}

    def select_buy_point(self, stock_data):
        """
        选择买点
        """
        continuous_days = stock_data.get('连续涨停天数', 0)

        if continuous_days == 1:
            return {'point': '首板', 'action': '换手充分时买?}
        elif continuous_days <= 5:
            return {'point': '连板', 'action': '放量回封时买?}
        else:
            return {'point': '龙回?, 'action': '回落20%后再次放?}
```

### 1.2 龙回头战?

```python
class DragonPullbackStrategy:
    """
    龙回头战?
    """

    def select_pullback_opportunity(self, stock_data):
        """
        选择龙回头机?
        """
        pullback_ratio = stock_data.get('回落幅度', 0)
        volume = stock_data.get('成交?, 0)
        avg_volume = stock_data.get('均量', 1)

        if 0.15 <= pullback_ratio <= 0.30 and volume > avg_volume * 1.5:
            return {
                'action': '买入',
                'pullback_ratio': pullback_ratio,
                'volume_surge': volume / avg_volume
            }

        return {'action': '观望'}
```

---

## 2. 热点优先级量?(S092)

> 来源：附录CB
>
> 热点优先级量化体?

### 2.1 优先级规?

```python
class HotSectorPrioritySystem:
    """
    热点优先级量?
    """

    PRIORITY_RULES = {
        '第一优先?: {
            '类型': '前期人气?,
            '特征': '妖股/龙头/反复炒作?,
            '操作': '股性活跃，识别度高'
        },
        '第二优先?: {
            '类型': '强势?,
            '特征': '直接受益概念?,
            '操作': '集合竞价抢筹，放量换手板'
        },
        '第三优先?: {
            '类型': '跟风?,
            '特征': '涨停时间排序',
            '操作': '溢价递减'
        }
    }

    def select_by_priority(self, sector_stocks):
        """
        按优先级选股
        """
        candidates = []

        for stock in sector_stocks:
            if stock.get('是人气股', False):
                priority = 1
            elif stock.get('是强势股', False):
                priority = 2
            else:
                priority = 3

            candidates.append({'stock': stock, 'priority': priority})

        return sorted(candidates, key=lambda x: x['priority'])
```

---

## 3. 竞价分析量化 (S093)

> 来源：附录CC
>
> 竞价分析量化体系

### 3.1 竞价分析核心

```python
class AuctionAnalysisSystem:
    """
    竞价分析量化体系
    核心：分析集合竞价的大单小单组合
    """

    def analyze_auction_pattern(self, auction_data):
        """
        分析竞价模式
        """
        last_minute_sell = auction_data.get('最?分钟大单卖出', False)
        two_buy_orders = auction_data.get('两笔大单买入', False)
        auction_volume = auction_data.get('竞价成交?, 0)
        prev_auction_volume = auction_data.get('昨日竞价成交?, 0)

        if last_minute_sell and two_buy_orders:
            return {'pattern': '异动', 'action': '警惕', 'confidence': 0.7}

        if auction_volume < prev_auction_volume * 0.8:
            return {'pattern': '缩量健康', 'action': '可持?, 'confidence': 0.8}

        return {'pattern': '正常', 'action': '观望'}

    AUCTION_HEALTHY = {
        '竞价缩量': '次日竞价<前日竞价80%',
        '大单托价': '人为造开盘价特征',
        '真实竞价': '大单买卖均衡'
    }
```

---

## 4. 卡位与抢帽子 (S094)

> 来源：附录CC
>
> 卡位与抢帽子量化

### 4.1 卡位检?

```python
class PositionTakingSystem:
    """
    卡位与抢帽子量化
    """

    def detect_position_taking(self, sector_stocks, leader_stock):
        """
        检测卡位机?
        """
        candidates = []

        for stock in sector_stocks:
            if stock['code'] == leader_stock['code']:
                continue

            if stock['封板时间'] < leader_stock['封板时间']:
                candidates.append({
                    'stock': stock,
                    'type': '卡位',
                    'action': '谨慎追入'
                })

        return candidates

    def check_hat_switching(self, stock_data):
        """
        检查抢帽子机会
        """
        if stock_data['成交?] < 100000000:
            return {'action': '不适合', 'reason': '流动性不?}

        day_range = stock_data['日内振幅']
        if day_range < 0.03:
            return {'action': '不适合', 'reason': '振幅太小'}

        return {'action': '可参?, 'reason': '满足条件'}
```

---

## 5. 先锋龙头判断 (S095)

> 来源：附录CC
>
> 先锋龙头判断量化

### 5.1 先锋识别

```python
class PioneerDragonIdentifier:
    """
    先锋龙头判断量化
    """

    def identify_pioneer(self, sector_stocks):
        """
        识别先锋?
        """
        sorted_stocks = sorted(
            sector_stocks,
            key=lambda x: x.get('封板时间', 999),
            reverse=False
        )

        if sorted_stocks:
            return {
                'pioneer': sorted_stocks[0],
                'time': sorted_stocks[0].get('封板时间', 'unknown')
            }

        return {'pioneer': None}

    def check_leader_qualification(self, stock_data, sector_data):
        """
        检查龙头资?
        """
        is_unique = stock_data.get('板块唯一龙头', False)
        has_support = len(sector_data.get('涨停股列?, [])) >= 2
        turnover = stock_data.get('换手?, 0)

        if is_unique and has_support and turnover >= 0.15:
            return {'is_leader': True, 'action': '龙头确认'}

        return {'is_leader': False, 'action': '等待确认'}
```

---

## 6. 目标价计?(S096)

> 来源：附录CC
>
> 目标价计算量?

### 6.1 比价?

```python
class TargetPriceCalculationSystem:
    """
    目标价计算量?
    方法：比价法 + 市场容量?
    """

    def calc_target_by_comparison(self, stock_data, sector_data):
        """
        比价法计算目标价
        """
        sector_avg_increase = sector_data.get('行业平均涨幅', 0)
        suspend_period_increase = sector_data.get('停牌期间行业涨幅', 0)
        should_increase = suspend_period_increase * 1.2

        return {
            'target_price': stock_data['停牌前价?] * (1 + should_increase),
            'increase_ratio': should_increase,
            'method': '比价?
        }

    def calc_target_by_capacity(self, stock_data, market_data):
        """
        市场容量法计算目标价
        """
        base_height = stock_data.get('历史高度', 0.50)
        sector_capacity = market_data.get('板块容量系数', 1.0)
        sentiment_factor = market_data.get('情绪系数', 1.0)

        final_target = base_height * sector_capacity * sentiment_factor

        return {
            'target_price': stock_data['当前?] * (1 + final_target),
            'increase_ratio': final_target,
            'method': '市场容量?
        }
```

---

## 7. 每日复盘量化 (S097)

> 来源：附录CC
>
> 每日复盘量化流程

### 7.1 复盘步骤

```python
class DailyReviewQuantifier:
    """
    每日复盘量化流程
    """

    REVIEW_STEPS = {
        '步骤1': '昨日热点顺势延伸预判',
        '步骤2': '新热点挖掘准?,
        '步骤3': '个股阶段划分',
        '步骤4': '先锋、龙头、助攻位?
    }

    STAGES = {
        '第一阶段': {'action': '择机介入'},
        '确立阶段': {'action': '及时上车'},
        '发酵阶段': {'action': '持有'},
        '高潮阶段': {'action': '分批卖出'},
        '反复阶段': {'action': '谨慎'}
    }

    def daily_review(self, market_data, sector_data):
        """
        执行每日复盘
        """
        return {
            '热点预判': self.predict_hot_sectors(market_data),
            '新热?: self.find_new_hot_sectors(market_data),
            '阶段分析': self.analyze_stages(sector_data),
            '自选股': self.generate_watchlist(sector_data)
        }

    def predict_hot_sectors(self, market_data):
        """
        预判热点
        """
        yesterday_hot = market_data.get('昨日热点', [])
        sentiment = market_data.get('市场情绪', 'neutral')

        if sentiment == 'bullish':
            return {'action': '延续昨日热点', 'sectors': yesterday_hot}

        return {'action': '寻找新热?, 'sectors': []}
```

---

## 8. 凡倍无名量?(S098)

> 来源：附录凡倍无?
>
> 凡倍无名量化体?

### 8.1 核心量化策略

```python
class FanbeiStrategy:
    """
    凡倍无名量化策?
    """

    def analyze_stock_personality(self, stock_data):
        """
        分析股?
        """
        score = 0

        if stock_data.get('历史连板次数', 0) >= 3:
            score += 0.3

        if stock_data.get('炸板?, 1) <= 0.3:
            score += 0.25

        if stock_data.get('溢价?, 0) >= 0.03:
            score += 0.25

        if stock_data.get('次日高开?, 0) >= 0.6:
            score += 0.2

        if score >= 0.75:
            return {'personality': '活跃', 'action': '可操?}

        return {'personality': '一?, 'action': '谨慎'}
```

---

## 9. 顶级游资汇?(S099-S105)

> 来源：附录BS
>
> 28位游资悟道心法综?

### 9.1 游资心法汇?

```python
class TopTraderMindSummary:
    """
    顶级游资心法汇?
    """

    TRADER_MIND = {
        '欢乐海岸': {
            '风格': '妖股高位接力',
            '仓位': '龙头满仓',
            '止损': '不轻易止?
        },
        '成都?: {
            '风格': '首板挖掘',
            '仓位': '分散布局',
            '止损': '-5%止损'
        },
        '佛山?: {
            '风格': '翘跌停板',
            '仓位': '跌停板重?,
            '止损': '次日必卖'
        },
        '浙江?: {
            '风格': '波段操作',
            '仓位': '逐步建仓',
            '止损': '-8%止损'
        },
        '温州?: {
            '风格': '快进快出',
            '仓位': '控盘度高',
            '止损': '严格止损'
        }
    }

    def select_by_trader_style(self, stock_data, trader_type):
        """
        按游资风格选股
        """
        style = self.TRADER_MIND.get(trader_type, {})

        if not style:
            return {'action': '未知风格'}

        if stock_data.get('风险敞口', 0) > 0.1:
            return {'action': '止损过大', 'suitable': False}

        return {
            'action': '符合风格',
            'suitable': True,
            'style': style
        }
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.9 | 2026-03-28 | 新增：欢乐海?S091)、热点优先级(S092)、竞价分?S093)、卡位抢?S094)、先锋龙?S095)、目标价计算(S096)、复盘量?S097)、凡倍无?S098)、顶级游资汇?S099-S105) |
