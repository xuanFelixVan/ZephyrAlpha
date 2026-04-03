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

# 涨停板量化

> 涨停板量化分析体系
>
> **配套文档**：
> - 主文档：
> - 形态识别：[pattern-recognition.md](../99_ARCHIVE/pattern-recognition.md)

***

## 1. 涨停板量化体系

### 1.1 涨停板分类

| 分类维度 | 类型 | 量化标准 |
|----------|------|----------|
| 板数 | 首板 | 首次涨停 |
| | 二板 | 连续第二个涨停 |
| | 三板及以上 | 连续涨停≥3 |
| 封板时间 | 早板 | 10:00前封板 |
| | 中板 | 10:00-14:00封板 |
| | 尾板 | 14:00后封板 |
| 封板力度 | 一字板 | 开盘即涨停 |
| | 实体板 | 有实体涨幅的涨停 |
| | 秒封板 | 涨停后成交额<1000万 |

***

## 2. 涨停板量化Python实现

### 2.1 涨停板基础分析

```python
class LimitUpAnalyzer:
    """涨停板分析"""

    def __init__(self):
        self.limit_up_stocks = []

    def is_limit_up(self, stock_data, limit_rate=0.10):
        """判断是否涨停"""
        change_pct = stock_data['change_pct']
        return abs(change_pct - limit_rate * 100) < 0.1

    def get_limit_up_info(self, stock_data):
        """获取涨停板信息"""
        return {
            'code': stock_data['code'],
            'name': stock_data['name'],
            'close': stock_data['close'],
            'change_pct': stock_data['change_pct'],
            'turnover': stock_data['turnover'],
            'seal_time': stock_data.get('seal_time', None),
            'open_count': stock_data.get('open_count', 0),
            'seal_amount': stock_data.get('seal_amount', 0),
            'float_market_cap': stock_data.get('float_market_cap', 0)
        }

    def calculate_seal_strength(self, seal_amount, turnover, limit_up_price):
        """计算封板力度"""
        if turnover == 0:
            return 0
        return (seal_amount / turnover) * 100

    def identify_limit_up_type(self, stock_data):
        """识别涨停板类型"""
        seal_time = stock_data.get('seal_time', '15:00')

        if stock_data['open'] == stock_data['high']:
            return '一字板'

        if stock_data.get('open_count', 0) == 0:
            return '秒封板'

        if seal_time < '10:00':
            return '早板'
        elif seal_time < '14:00':
            return '中板'
        else:
            return '尾板'
```

***

### 2.2 连板股量化

```python
class ConsecutiveLimitUpAnalyzer:
    """连板股分析"""

    def __init__(self):
        self.consecutive_stocks = {}

    def add_limit_up(self, code, date, limit_up_data):
        """添加涨停记录"""
        if code not in self.consecutive_stocks:
            self.consecutive_stocks[code] = []

        self.consecutive_stocks[code].append({
            'date': date,
            'limit_up': limit_up_data
        })

    def get_consecutive_count(self, code, current_date):
        """获取连板数"""
        if code not in self.consecutive_stocks:
            return 0

        records = self.consecutive_stocks[code]
        consecutive = 0

        for record in reversed(records):
            if record['date'] == current_date:
                if record['limit_up']:
                    consecutive += 1
                else:
                    break
            else:
                break

        return consecutive

    def is_leader_candidate(self, code, current_date, threshold=4):
        """判断是否为龙头候选"""
        consecutive = self.get_consecutive_count(code, current_date)

        if consecutive >= threshold:
            return {
                'is_leader': True,
                'consecutive': consecutive,
                'recommendation': '龙头确认'
            }

        return {
            'is_leader': False,
            'consecutive': consecutive,
            'recommendation': '跟风'
        }
```

***

## 3. 涨停板情绪量化

### 3.1 涨停板情绪指标

| 指标 | 计算方式 | 含义 |
|------|----------|------|
| 涨停家数 | 当日涨停股票数量 | 市场热度 |
| 连板股比例 | 连续涨停股/涨停股 | 接力情况 |
| 炸板率 | 炸板股数/涨停股数 | 封板成功率 |
| 跌停家数 | 当日跌停股票数量 | 市场恐慌程度 |
| 涨停溢价 | 次日平均高开幅度 | 赚钱效应 |

***

### 3.2 情绪分析Python实现

```python
class LimitUpSentimentAnalyzer:
    """涨停板情绪分析"""

    def __init__(self):
        self.market_data = {}

    def calculate_sentiment_index(self, date):
        """计算涨停板情绪指数"""
        limit_up_count = self.get_limit_up_count(date)
        limit_down_count = self.get_limit_down_count(date)
        break_limit_count = self.get_break_limit_count(date)

        if limit_up_count + limit_down_count == 0:
            return 50

        sentiment = (
            limit_up_count * 1.0 -
            limit_down_count * 0.8 -
            break_limit_count * 0.3
        ) / (limit_up_count + limit_down_count) * 100

        return max(0, min(100, sentiment + 50))

    def get_limit_up_count(self, date):
        """获取涨停家数"""
        return len([s for s in self.market_data.get(date, [])
                   if s.get('is_limit_up', False)])

    def get_limit_down_count(self, date):
        """获取跌停家数"""
        return len([s for s in self.market_data.get(date, [])
                   if s.get('is_limit_down', False)])

    def get_break_limit_count(self, date):
        """获取炸板家数"""
        return len([s for s in self.market_data.get(date, [])
                   if s.get('is_break_limit', False)])

    def get_emotion_zone(self, sentiment_index):
        """判断情绪区域"""
        if sentiment_index >= 80:
            return {'zone': '极热区', 'action': '减仓观望'}
        elif sentiment_index >= 65:
            return {'zone': '过热区', 'action': '谨慎追涨'}
        elif sentiment_index >= 45:
            return {'zone': '正常区', 'action': '积极参与'}
        elif sentiment_index >= 30:
            return {'zone': '过冷区', 'action': '等待机会'}
        else:
            return {'zone': '极冷区', 'action': '抄底信号'}
```

***

## 4. 涨停板量化筛选

### 4.1 首板筛选条件

| 条件类型 | 量化标准 | 说明 |
|----------|----------|------|
| 市值要求 | 流通市值<100亿 | 便于资金炒作 |
| 成交量要求 | 成交额>3亿 | 资金参与度 |
| 换手率要求 | 换手率>5% | 充分换手 |
| 封单要求 | 封单额>1亿 | 封板力度 |
| 题材要求 | 所属题材涨停≥3只 | 板块联动 |

***

### 4.2 二板筛选条件

| 条件类型 | 量化标准 | 说明 |
|----------|----------|------|
| 一板质量 | 一板为实体板 | 非一字板 |
| 高开幅度 | 3%-8% | 不过高不过低 |
| 回调幅度 | 不跌破一板最高价80% | 强势整理 |
| 封板时间 | 10:30前封板 | 强势信号 |
| 跟风效应 | 同题材有一板助攻 | 板块联动 |

***

### 4.3 龙头股筛选

```python
class DragonStockSelector:
    """龙头股筛选器"""

    def __init__(self):
        self.min_consecutive = 3
        self.sector_leader_weight = 2.0

    def select_dragon_candidates(self, limit_up_stocks):
        """筛选龙头候选"""
        candidates = []

        for stock in limit_up_stocks:
            score = 0

            if stock.get('consecutive_limit_up', 0) >= self.min_consecutive:
                score += 20

            if stock.get('sector_limit_up_count', 0) >= 3:
                score += 15 * self.sector_leader_weight

            if stock.get('follow_effect', 0) >= 3:
                score += 10

            if stock.get('fund_flow', 0) > 0:
                score += 10

            if stock.get('market_cap', 0) < 50e8:
                score += 5

            if score >= 40:
                candidates.append({
                    'code': stock['code'],
                    'name': stock['name'],
                    'score': score,
                    'consecutive': stock.get('consecutive_limit_up', 0)
                })

        return sorted(candidates, key=lambda x: x['score'], reverse=True)
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 整合附录V内容 |
