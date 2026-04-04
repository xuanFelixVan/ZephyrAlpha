---
module_id: TACTICS_DOC_001
version: 1.0.0
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

# 牛熊市量能周�?

> 市场周期与量能分�?
>
> **配套文档**�?
> - 主文档：
> - 技术指标：[technical-indicators.md](../99_ARCHIVE/technical-indicators.md)

***

## 1. 市场周期量化

### 1.1 牛市特征量化

| 阶段 | 特征 | 量化标准 |
|------|------|----------|
| 初期 | 估值修�?| PE底部回升>20% |
| | 成交量放�?| 量比>1.5持续 |
| | 均线多头 | MA5>MA20>MA60 |
| 中期 | 赚钱效应 | 上涨家数>60% |
| | 板块轮动 | 每日热点持续 |
| 后期 | 估值泡�?| PE>历史80%分位 |
| | 天量天价 | 成交量创历史新高 |

***

### 1.2 熊市特征量化

| 阶段 | 特征 | 量化标准 |
|------|------|----------|
| 初期 | 估值消�?| PE回落>15% |
| | 缩量下跌 | 量比<0.8 |
| | 均线空头 | MA5<MA20<MA60 |
| 中期 | 亏钱效应 | 下跌家数>60% |
| | 阴跌不断 | 指数不断新低 |
| 后期 | 情绪冰点 | 涨停<30�?|
| | 地量地价 | 成交量创地量 |

***

## 2. 量价关系量化

### 2.1 放量与缩�?

| 类型 | 量化标准 | 市场含义 |
|------|----------|----------|
| 天量 | 量比>3 | 顶部信号 |
| 放量 | 量比>1.5 | 方向确认 |
| 平量 | 量比0.8-1.2 | 观望 |
| 缩量 | 量比<0.8 | 趋势延续 |
| 地量 | 量比<0.5 | 底部信号 |

***

### 2.2 量价背离

| 类型 | 量化标准 | 信号意义 |
|------|----------|----------|
| 底背�?| 价格新低但量能放�?| 底部反转 |
| 顶背�?| 价格新高但量能萎�?| 顶部反转 |
| 二次背离 | 连续两次背离 | 确定性更�?|

***

## 3. Python实现

```python
class MarketCycleAnalyzer:
    """市场周期分析"""

    def __init__(self):
        self.market_state = 'unknown'

    def identify_market_cycle(self, index_data, lookback=60):
        """识别市场周期"""
        ma5 = index_data['close'].rolling(5).mean()
        ma20 = index_data['close'].rolling(20).mean()
        ma60 = index_data['close'].rolling(60).mean()

        current = index_data['close'].iloc[-1]

        if ma5.iloc[-1] > ma20.iloc[-1] > ma60.iloc[-1]:
            self.market_state = 'BULL'
        elif ma5.iloc[-1] < ma20.iloc[-1] < ma60.iloc[-1]:
            self.market_state = 'BEAR'
        else:
            self.market_state = 'VOLATILE'

        return self.market_state

    def calculate_volume_ratio(self, current_volume, avg_volume, period=20):
        """计算量比"""
        return current_volume / self.get_avg_volume(avg_volume, period)

    def detect_volume_price_divergence(self, price_data, volume_data):
        """检测量价背�?""
        price_trend = price_data['close'].iloc[-1] - price_data['close'].iloc[0]
        volume_trend = volume_data.iloc[-1] - volume_data.iloc[0]

        if price_trend < 0 and volume_trend > 0:
            return {'type': 'bottom_divergence', 'signal': 'bullish'}

        if price_trend > 0 and volume_trend < 0:
            return {'type': 'top_divergence', 'signal': 'bearish'}

        return {'type': 'normal', 'signal': 'neutral'}


class VolumeAnalysis:
    """量能分析"""

    def __init__(self):
        self.volume_history = []

    def calculate_volume_ma(self, period=5):
        """计算成交量均�?""
        return pd.Series(self.volume_history).rolling(period).mean()

    def is_volume_explosion(self, current_volume, threshold=3.0):
        """判断是否放量"""
        vol_ma = self.calculate_volume_ma()
        if len(vol_ma) == 0:
            return False
        return current_volume > vol_ma.iloc[-1] * threshold

    def is_volume_bottom(self, current_volume, threshold=0.5):
        """判断是否地量"""
        vol_ma = self.calculate_volume_ma()
        if len(vol_ma) == 0:
            return False
        return current_volume < vol_ma.iloc[-1] * threshold

    def get_volume_trend(self, period=5):
        """判断量能趋势"""
        if len(self.volume_history) < period:
            return 'unknown'

        recent = self.volume_history[-period:]
        first_half = sum(recent[:period//2])
        second_half = sum(recent[period//2:])

        if second_half > first_half * 1.2:
            return 'increasing'
        elif second_half < first_half * 0.8:
            return 'decreasing'
        else:
            return 'stable'
```

***

## 4. 周期转换信号

### 4.1 牛熊转换信号

| 转换类型 | 触发条件 | 确认条件 |
|----------|----------|----------|
| 牛市确立 | 指数站上MA60 | 持续3�?放量 |
| 熊市确立 | 指数跌破MA60 | 持续3�?缩量 |
| 震荡�?| MA60走平 | 指数在其上下波动 |

***

### 4.2 周期操作策略

| 市场状�?| 操作策略 | 仓位建议 |
|----------|----------|----------|
| 牛市初期 | 逢低买入 | 60-80% |
| 牛市中期 | 趋势持有 | 80-100% |
| 牛市后期 | 逐步减仓 | 40-60% |
| 熊市初期 | 清仓观望 | 0% |
| 熊市中期 | 抢反�?| 20-30% |
| 熊市末期 | 布局优质�?| 40-50% |
| 震荡�?| 高抛低吸 | 30-50% |

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 整合附录X内容 |
