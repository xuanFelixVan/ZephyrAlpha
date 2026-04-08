---
module_id: PATTERN_RECOGNITION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: '2026-04-07'
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
- 交易策略、战术执行
- 系统架构
- 文档治理
module_id: TACTICS_ARCH_PATTERN_RECOG_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 因子计算
  - 系统架构
  - 文档治理
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
---


# 形态识?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> K线形态量化识?
>
> **配套文档**?
> - 主文档：[../../INDEX.md](../INDEX.md)
> - 技术指标：
***

## 1. 底部反转形?

### 1.1 锤子线（Hammer?

| 属?| 内容 |
|------|------|
| 形态名?| 锤子?|
| 形态类别| 底部反转 |
| 量化标准 | 下影线≥2倍实体，上影线≤10%全长 |

```python
class HammerPattern:
    """锤子线识?""

    def identify(self, df, index):
        candle = df.iloc[index]
        body = abs(candle['close'] - candle['open'])
        upper_shadow = candle['high'] - max(candle['close'], candle['open'])
        lower_shadow = min(candle['close'], candle['open']) - candle['low']
        total_range = candle['high'] - candle['low']

        if lower_shadow >= 2 * body and upper_shadow <= 0.1 * total_range:
            return True
        return False
```

***

### 1.2 吞没形态（Engulfing?

| 属?| 内容 |
|------|------|
| 形态名?| 吞没形?|
| 形态类别| 底部反转 |
| 量化标准 | 第一根K线实体小，第二根完全包裹第一?|

```python
class EngulfingPattern:
    """吞没形态识?""

    def identify(self, df, index):
        if index < 1:
            return False

        prev = df.iloc[index - 1]
        curr = df.iloc[index]

        prev_body = abs(prev['close'] - prev['open'])
        curr_body = abs(curr['close'] - curr['open'])

        prev_isBearish = prev['close'] < prev['open']
        curr_isBullish = curr['close'] > curr['open']

        curr_contains_prev = (
            curr['high'] >= prev['high'] and
            curr['low'] <= prev['low']
        )

        if (curr_isBullish and prev_isBearish and
            curr_body > prev_body and curr_contains_prev):
            return True

        return False
```

***

### 1.3 早晨之星（Morning Star?

| 属?| 内容 |
|------|------|
| 形态名?| 早晨之星 |
| 形态类别| 底部反转 |
| 量化标准 | 三日组合：下跌→十字星→上涨 |

```python
class MorningStarPattern:
    """早晨之星识别"""

    def identify(self, df, index):
        if index < 2:
            return False

        d1 = df.iloc[index - 2]
        d2 = df.iloc[index - 1]
        d3 = df.iloc[index]

        d1_bearish = d1['close'] < d1['open']
        d2_small_body = abs(d2['close'] - d2['open']) < 0.3 * (d2['high'] - d2['low'])
        d3_bullish = d3['close'] > d3['open']

        if d1_bearish and d2_small_body and d3_bullish:
            return True

        return False
```

***

## 2. 顶部反转形?

### 2.1 射击之星（Shooting Star?

| 属?| 内容 |
|------|------|
| 形态名?| 射击之星 |
| 形态类别| 顶部反转 |
| 量化标准 | 上影线≥2倍实体，下影线≤10%全长 |

```python
class ShootingStarPattern:
    """射击之星识别"""

    def identify(self, df, index):
        candle = df.iloc[index]
        body = abs(candle['close'] - candle['open'])
        upper_shadow = candle['high'] - max(candle['close'], candle['open'])
        lower_shadow = min(candle['close'], candle['open']) - candle['low']
        total_range = candle['high'] - candle['low']

        if upper_shadow >= 2 * body and lower_shadow <= 0.1 * total_range:
            return True
        return False
```

***

### 2.2 乌云盖顶（Dark Cloud Cover?

| 属?| 内容 |
|------|------|
| 形态名?| 乌云盖顶 |
| 形态类别| 顶部反转 |
| 量化标准 | 上涨后高开低走，跌破前一日实?0% |

```python
class DarkCloudCoverPattern:
    """乌云盖顶识别"""

    def identify(self, df, index):
        if index < 1:
            return False

        prev = df.iloc[index - 1]
        curr = df.iloc[index]

        prev_bullish = prev['close'] > prev['open']
        curr_bearish = curr['close'] < curr['open']

        curr_open_above_prev = curr['open'] > prev['close']
        curr_close_below_mid = curr['close'] < (prev['open'] + prev['close']) / 2

        if prev_bullish and curr_bearish and curr_open_above_prev and curr_close_below_mid:
            return True

        return False
```

***

## 3. 持续形?

### 3.1 旗形整理（Flag?

| 属?| 内容 |
|------|------|
| 形态名?| 旗形整理 |
| 形态类别| 持续 |
| 量化标准 | 急涨/急跌后窄幅整理，量能萎缩 |

```python
class FlagPattern:
    """旗形整理识别"""

    def identify(self, df, index, lookback=10):
        if index < lookback:
            return False

        recent = df.iloc[index-lookback:index]
        first_half = recent.iloc[:lookback//2]
        second_half = recent.iloc[lookback//2:]

        first_trend = first_half['close'].iloc[-1] - first_half['close'].iloc[0]
        first_vol = first_half['volume'].mean()

        second_range = second_half['high'].max() - second_half['low'].min()
        second_vol = second_half['volume'].mean()

        flag_formation = abs(first_trend) > 0.05
        consolidation = second_range < 0.02 * first_half['close'].iloc[-1]
        volume_decline = second_vol < 0.5 * first_vol

        if flag_formation and consolidation and volume_decline:
            return True

        return False
```

***

### 3.2 三角形整理（Triangle?

| 属?| 内容 |
|------|------|
| 形态名?| 三角形整?|
| 形态类别| 持续 |
| 量化标准 | 高点下降+低点上升，收敛至顶点 |

```python
class TrianglePattern:
    """三角形整理识?""

    def identify(self, df, index, lookback=20):
        if index < lookback:
            return False

        segment = df.iloc[index-lookback:index]

        highs = segment['high']
        lows = segment['low']

        high_slope = (highs.iloc[-1] - highs.iloc[0]) / lookback
        low_slope = (lows.iloc[-1] - lows.iloc[0]) / lookback

        descending_triangle = high_slope < -0.001
        ascending_triangle = low_slope > 0.001
        symmetrical = high_slope < 0 and low_slope > 0

        if descending_triangle or ascending_triangle or symmetrical:
            return {'type': 'descending' if descending_triangle else
                           'ascending' if ascending_triangle else 'symmetrical'}

        return None
```

***

## 4. 形态识别引?

```python
class PatternRecognitionEngine:
    """形态识别引?""

    def __init__(self):
        self.patterns = {
            'hammer': HammerPattern(),
            'engulfing': EngulfingPattern(),
            'morning_star': MorningStarPattern(),
            'shooting_star': ShootingStarPattern(),
            'dark_cloud': DarkCloudCoverPattern(),
            'flag': FlagPattern(),
            'triangle': TrianglePattern(),
        }

    def scan_all_patterns(self, df, index):
        """扫描所有形?""
        results = {}

        for pattern_name, pattern in self.patterns.items():
            try:
                result = pattern.identify(df, index)
                if result:
                    results[pattern_name] = result
            except Exception as e:
                continue

        return results

    def get_bullish_signals(self, df, index):
        """获取做多信号"""
        all_patterns = self.scan_all_patterns(df, index)
        bullish = ['hammer', 'engulfing', 'morning_star']
        return {k: v for k, v in all_patterns.items() if k in bullish}

    def get_bearish_signals(self, df, index):
        """获取做空信号"""
        all_patterns = self.scan_all_patterns(df, index)
        bearish = ['shooting_star', 'dark_cloud']
        return {k: v for k, v in all_patterns.items() if k in bearish}
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 整合附录P内容 |
