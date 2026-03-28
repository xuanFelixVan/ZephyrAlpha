# T.00.MR001.市场趋势识别

> 市场趋势状态识别 - 五维市场状态综合判断

## 1. 五维市场状态体系

> **来源**：量化策略专业分层方案_v3.0 前置层五维分析

### 1.1 五维分析框架

| 维度 | 评估内容 | 量化指标 | 权重 |
|------|----------|----------|------|
| 技术面 | 价格趋势、均线系统、MACD | 上涨家数比、均线多头排列 | 25% |
| 资金面 | 资金流向、成交额变化 | 北向资金净流入、主力净流入 | 25% |
| 情绪面 | 恐慌贪婪、涨跌停家数 | 情绪指数、涨停家数 | 20% |
| 风格面 | 资金属性、板块轮动 | 机构主导/短线主导 | 15% |
| 全球面 | 外盘影响、夜盘行情 | A50、汇率 | 15% |

### 1.2 市场状态概率输出

```python
class MarketRegimeIdentifier:
    """五维市场状态识别"""

    MARKET_STATES = ['牛市', '熊市', '震荡市', '妖股周期', '混沌']

    def __init__(self):
        self.dimension_weights = {
            '技术面': 0.25,
            '资金面': 0.25,
            '情绪面': 0.20,
            '风格面': 0.15,
            '全球面': 0.15
        }

    def calculate_state_probabilities(self, market_data):
        """
        计算各市场状态概率
        """
        scores = {}

        for state in self.MARKET_STATES:
            score = 0
            for dim, weight in self.dimension_weights.items():
                dim_score = self.get_dimension_score(dim, state, market_data)
                score += dim_score * weight
            scores[state] = score

        total = sum(scores.values())
        probabilities = {k: v/total for k, v in scores.items()}

        return probabilities

    def get_dimension_score(self, dimension, state, market_data):
        """
        获取各维度对特定状态的得分
        """
        if dimension == '技术面':
            return self.score_technical(market_data, state)
        elif dimension == '资金面':
            return self.score_money_flow(market_data, state)
        elif dimension == '情绪面':
            return self.score_sentiment(market_data, state)
        elif dimension == '风格面':
            return self.score_style(market_data, state)
        elif dimension == '全球面':
            return self.score_global(market_data, state)
        return 0.5
```

***

## 2. 资金风格识别

### 2.1 资金属性分类

| 资金类型 | 特征 | 量化识别 |
|----------|------|----------|
| 机构主导 | 持续净流入、换手率适中 | 5日净流入持续为正 |
| 短线资金主导 | 涨停家数多、轮动快 | 换手率>8%、涨停>50家 |
| 混合风格 | 两者交替 | 特征不明显 |

### 2.2 资金风格判断规则

```python
MONEY_STYLE_RULES = {
    '机构主导': {
        'north_flow_5d_positive': True,
        'turnover_rate_max': 0.08,
        'limit_up_count_max': 30,
    },
    '短线资金主导': {
        'turnover_rate_min': 0.08,
        'limit_up_count_min': 50,
    },
    '混合风格': {
        'institutional_score': 0.4,
        'short_term_score': 0.4,
    }
}
```

***

## 3. 情绪指数量化

### 3.1 情绪指数计算

| 指标 | 计算方式 | 阈值说明 |
|------|----------|----------|
| 恐慌贪婪指数 | 基于涨跌家数、涨停跌停比 | 0-100 |
| 北向资金 | 当日净流入 | >30亿积极 |
| 融资融券 | 融资余额变化率 | >5%情绪亢奋 |

### 3.2 情绪状态分类

| 情绪状态 | 指数范围 | 操作建议 |
|----------|----------|----------|
| 极度恐慌 | 0-20 | 逆向布局 |
| 恐慌 | 20-40 | 谨慎乐观 |
| 中性 | 40-60 | 均衡配置 |
| 贪婪 | 60-80 | 降低仓位 |
| 极度贪婪 | 80-100 | 清仓观望 |

***

## 4. 混沌识别（市场失序）

### 4.1 混沌状态特征

> **说明**：当市场无法被明确分类为牛市/熊市/震荡市时，定义为混沌状态

| 特征 | 量化标准 |
|------|----------|
| 多周期矛盾 | 日线看多但30分钟看空 |
| 板块轮动过快 | 日内切换>5次 |
| 无明确主线 | 无板块涨幅超过3% |

### 4.2 混沌状态处理

```python
CHAOS_RULES = {
    'detection': {
        'cycle_conflict': True,
        'sector_rotation_count': 5,
        'main_line_strength': 0.03,
    },
    'response': {
        'position_reduction': 0.5,
        'avoid_momentum': True,
        'prefer_defensive': True,
    }
}
```

***

## 5. 输出格式

```json
{
  "前置判断": {
    "市场状态": {
      "牛市": 0.3,
      "熊市": 0.1,
      "震荡市": 0.5,
      "妖股周期": 0.1
    },
    "资金风格": {
      "机构主导": 0.4,
      "短线资金主导": 0.3,
      "混合风格": 0.3
    },
    "情绪指数": 65,
    "大盘涨跌预测": {
      "今日": "震荡偏多",
      "明日": "待观察"
    },
    "置信度": 0.75
  }
}
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 整合五维市场状态体系、资金风格识别、混沌识别 |
