# T.01.TR002.技术指标协同量化

> 趋势跟踪类Alpha因子
>
> **配套文档**：
> - 主文档：[SPEC.md](../../../../SPEC.md)
> - 因子库索引：[因子库主索引](../../../../../factor-library/04_DATA_SOURCE/因子主索引.md)
> - 趋势跟踪：[趋势跟踪 README](./README.md)

***

## 1. 因子概述

| 属性 | 内容 |
|------|------|
| 因子编号 | T.01.TR002 |
| 因子名称 | 技术指标协同量化 |
| 因子类型 | 趋势跟踪类 |
| 计算周期 | 日频/分钟频 |
| 数据来源 | KDJ/RSI/MACD/BOLL |

**核心理念**：通过多个技术指标的协同分析，提高信号可靠性，减少假信号

**适用场景**：趋势确认买入、顶底背离识别、多指标共振交易

***

## 2. 指标权重配置

### 2.1 默认权重

| 指标 | 权重 | 说明 |
|------|------|------|
| KDJ | 25% | 随机指标，敏感度高 |
| RSI | 25% | 相对强弱指数 |
| MACD | 25% | 指数平滑异同移动平均线 |
| BOLL | 25% | 布林带 |

### 2.2 参数配置

```python
INDICATOR_PARAMS = {
    'kdj': {
        'n': 9,      # 周期
        'k': 3,      # K值平滑
        'd': 3       # D值平滑
    },
    'rsi': {
        'n': 14      # 周期
    },
    'macd': {
        'fast': 12,  # 快线周期
        'slow': 26,  # 慢线周期
        'signal': 9  # 信号线周期
    },
    'boll': {
        'n': 20,     # 周期
        'k': 2       # 标准差倍数
    }
}
```

***

## 3. 单指标分析

### 3.1 KDJ分析

```python
def analyze_kdj(kdj_data):
    """
    KDJ分析

    Returns:
        - status: 超买/超卖/金叉/死叉
        - score: 评分 (-1 to 1)
    """
    k = kdj_data['k']
    d = kdj_data['d']
    j = kdj_data['j']

    score = 0
    status = []

    # 超买超卖
    if j > 100:
        status.append('超买')
        score -= 0.3
    elif j < 0:
        status.append('超卖')
        score += 0.3

    # 金叉死叉
    if k > d and k > d.shift(1):
        status.append('金叉')
        score += 0.2
    elif k < d and k < d.shift(1):
        status.append('死叉')
        score -= 0.2

    return {
        'status': '/'.join(status) if status else '正常',
        'score': score,
        'k': k,
        'd': d,
        'j': j
    }
```

### 3.2 RSI分析

```python
def analyze_rsi(rsi_data):
    """
    RSI分析

    Returns:
        - status: 超买/超卖/偏强/偏弱
        - score: 评分 (-1 to 1)
    """
    rsi = rsi_data['rsi']

    if rsi > 80:
        return {'status': '超买', 'score': -0.3}
    elif rsi < 20:
        return {'status': '超卖', 'score': 0.3}
    elif rsi > 50:
        return {'status': '偏强', 'score': 0.1}
    else:
        return {'status': '偏弱', 'score': -0.1}
```

### 3.3 MACD分析

```python
def analyze_macd(macd_data):
    """
    MACD分析

    Returns:
        - status: 金叉/死叉/红柱/绿柱
        - score: 评分 (-1 to 1)
    """
    dif = macd_data['dif']
    dea = macd_data['dea']
    histogram = macd_data['histogram']

    score = 0
    status = []

    # 金叉死叉
    if dif > dea and dif.shift(1) <= dea.shift(1):
        status.append('金叉')
        score += 0.3
    elif dif < dea and dif.shift(1) >= dea.shift(1):
        status.append('死叉')
        score -= 0.3

    # 红柱绿柱
    if histogram > 0:
        status.append('红柱')
        score += 0.1
    else:
        status.append('绿柱')
        score -= 0.1

    return {
        'status': '/'.join(status) if status else '中性',
        'score': score,
        'dif': dif,
        'dea': dea,
        'histogram': histogram
    }
```

### 3.4 BOLL分析

```python
def analyze_boll(boll_data):
    """
    BOLL分析

    Returns:
        - status: 突破上轨/跌破下轨/中轨上方/中轨下方
        - score: 评分 (-1 to 1)
    """
    price = boll_data['price']
    upper = boll_data['upper']
    middle = boll_data['middle']
    lower = boll_data['lower']

    if price > upper:
        return {'status': '突破上轨', 'score': -0.2, 'position': '上轨之上'}
    elif price < lower:
        return {'status': '跌破下轨', 'score': 0.2, 'position': '下轨之下'}
    elif price > middle:
        return {'status': '中轨上方', 'score': 0.1, 'position': '中轨之上'}
    else:
        return {'status': '中轨下方', 'score': -0.1, 'position': '中轨之下'}
```

***

## 4. 综合信号生成

### 4.1 综合评分计算

```python
def calc_combined_signal(signals):
    """
    计算综合评分

    Parameters:
        signals: 包含kdj/rsi/macd/boll信号的字典

    Returns:
        combined_score: 综合评分
        recommendation: 操作建议
    """
    combined_score = (
        signals['kdj']['score'] * 0.25 +
        signals['rsi']['score'] * 0.25 +
        signals['macd']['score'] * 0.25 +
        signals['boll']['score'] * 0.25
    )

    recommendation = get_recommendation(combined_score, signals)

    return {
        'combined_score': combined_score,
        'recommendation': recommendation,
        'signals': signals
    }

def get_recommendation(combined_score, signals):
    """
    获取操作建议
    """
    if combined_score >= 0.5:
        return '强烈买入'
    elif combined_score >= 0.2:
        return '适度买入'
    elif combined_score <= -0.5:
        return '强烈卖出'
    elif combined_score <= -0.2:
        return '适度卖出'
    else:
        return '观望'
```

### 4.2 信号等级

| 信号等级 | 操作建议 | 综合评分 | 说明 |
|----------|----------|----------|------|
| 5 | 强烈买入 | ≥0.5 | 多指标共振看多 |
| 4 | 适度买入 | 0.2-0.5 | 部分指标看多 |
| 3 | 观望 | -0.2-0.2 | 方向不明 |
| 2 | 适度卖出 | -0.5~-0.2 | 部分指标看空 |
| 1 | 强烈卖出 | ≤-0.5 | 多指标共振看空 |

***

## 5. 背离识别

### 5.1 顶背离识别

```python
def is_top_divergence(price, indicator):
    """
    顶背离：价格创新高，指标没有

    条件：
    1. 价格连续创新高
    2. 指标的高点没有更高（或开始下降）
    """
    price_diff = price.diff()
    indicator_diff = indicator.diff()

    # 价格创了更高的高点
    price_higher = (
        price.iloc[-1] > price.iloc[-2] and
        price.iloc[-2] > price.iloc[-3]
    )

    # 但指标的高点没有更高
    indicator_lower = indicator.iloc[-1] < indicator.iloc[-2]

    return price_higher and indicator_lower

def is_bottom_divergence(price, indicator):
    """
    底背离：价格创新低，指标没有

    条件：
    1. 价格连续创新低
    2. 指标的低点没有更低（或开始上升）
    """
    price_lower = (
        price.iloc[-1] < price.iloc[-2] and
        price.iloc[-2] < price.iloc[-3]
    )

    indicator_higher = indicator.iloc[-1] > indicator.iloc[-2]

    return price_lower and indicator_higher
```

### 5.2 背离信号生成

```python
def detect_divergence(price_data, indicator_data, indicator_name='MACD'):
    """
    检测背离并生成信号
    """
    if is_top_divergence(price_data['high'], indicator_data):
        confidence = calc_divergence_strength(price_data, indicator_data)
        return {
            'type': '顶背离',
            'signal': '看跌',
            'confidence': confidence,
            'action': '卖出或减仓'
        }

    if is_bottom_divergence(price_data['low'], indicator_data):
        confidence = calc_divergence_strength(price_data, indicator_data)
        return {
            'type': '底背离',
            'signal': '看涨',
            'confidence': confidence,
            'action': '买入或加仓'
        }

    return {
        'type': '无背离',
        'signal': '中性',
        'confidence': 0,
        'action': '观望'
    }

def calc_divergence_strength(price, indicator):
    """
    计算背离强度
    """
    price_change = abs(price.iloc[-1] - price.iloc[-3]) / price.iloc[-3]
    indicator_change = abs(indicator.iloc[-1] - indicator.iloc[-3]) / indicator.iloc[-3]

    if indicator_change == 0:
        return 0.5

    ratio = price_change / indicator_change

    if ratio > 2:
        return 0.9
    elif ratio > 1.5:
        return 0.7
    elif ratio > 1:
        return 0.5
    else:
        return 0.3
```

***

## 6. Python实现

```python
import pandas as pd
import numpy as np
from typing import Dict, Optional

class TechnicalIndicatorSynergy:
    """
    技术指标协同量化
    多指标共振增强信号可靠性
    """

    DEFAULT_WEIGHTS = {
        'kdj': 0.25,
        'rsi': 0.25,
        'macd': 0.25,
        'boll': 0.25
    }

    def __init__(self, weights: Optional[Dict] = None):
        self.name = "技术指标协同"
        self.factor_code = "T.01.TR002"
        self.weights = weights or self.DEFAULT_WEIGHTS

    def analyze(self, price_df: pd.DataFrame) -> Dict:
        """
        综合分析多个技术指标

        Parameters:
            price_df: 包含OHLCV数据的DataFrame
                - open, high, low, close, volume

        Returns:
            分析结果字典
        """
        kdj_data = self._calc_kdj(price_df)
        rsi_data = self._calc_rsi(price_df)
        macd_data = self._calc_macd(price_df)
        boll_data = self._calc_boll(price_df)

        signals = {
            'kdj': self._analyze_kdj(kdj_data),
            'rsi': self._analyze_rsi(rsi_data),
            'macd': self._analyze_macd(macd_data),
            'boll': self._analyze_boll(boll_data)
        }

        combined_score = sum(
            signals[key]['score'] * self.weights[key]
            for key in self.weights.keys()
        )

        recommendation = self._get_recommendation(combined_score, signals)

        divergence = self._detect_divergence(
            price_df,
            macd_data['dif']
        )

        return {
            'factor_code': self.factor_code,
            'factor_name': self.name,
            'signals': signals,
            'combined_score': combined_score,
            'recommendation': recommendation,
            'divergence': divergence,
            'timestamp': pd.Timestamp.now()
        }

    def _calc_kdj(self, df: pd.DataFrame, n: int = 9, k: int = 3, d: int = 3) -> pd.DataFrame:
        """计算KDJ"""
        low_n = df['low'].rolling(n).min()
        high_n = df['high'].rolling(n).max()

        rsv = (df['close'] - low_n) / (high_n - low_n) * 100
        rsv = rsv.fillna(50)

        k_values = rsv.ewm(alpha=1/k, adjust=False).mean()
        d_values = k_values.ewm(alpha=1/d, adjust=False).mean()
        j_values = 3 * k_values - 2 * d_values

        return pd.DataFrame({
            'k': k_values,
            'd': d_values,
            'j': j_values
        })

    def _calc_rsi(self, df: pd.DataFrame, n: int = 14) -> pd.DataFrame:
        """计算RSI"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(n).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(n).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi = rsi.fillna(50)

        return pd.DataFrame({'rsi': rsi})

    def _calc_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """计算MACD"""
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()

        dif = ema_fast - ema_slow
        dea = dif.ewm(span=signal, adjust=False).mean()
        histogram = (dif - dea) * 2

        return pd.DataFrame({
            'dif': dif,
            'dea': dea,
            'histogram': histogram
        })

    def _calc_boll(self, df: pd.DataFrame, n: int = 20, k: int = 2) -> pd.DataFrame:
        """计算布林带"""
        middle = df['close'].rolling(n).mean()
        std = df['close'].rolling(n).std()

        upper = middle + k * std
        lower = middle - k * std

        return pd.DataFrame({
            'upper': upper,
            'middle': middle,
            'lower': lower
        })

    def _analyze_kdj(self, kdj_df: pd.DataFrame) -> Dict:
        """分析KDJ"""
        k = kdj_df['k'].iloc[-1]
        d = kdj_df['d'].iloc[-1]
        j = kdj_df['j'].iloc[-1]

        score = 0
        status = []

        if j > 100:
            status.append('超买')
            score -= 0.3
        elif j < 0:
            status.append('超卖')
            score += 0.3

        if k > d and k > kdj_df['k'].iloc[-2]:
            status.append('金叉')
            score += 0.2
        elif k < d and k < kdj_df['k'].iloc[-2]:
            status.append('死叉')
            score -= 0.2

        return {
            'status': '/'.join(status) if status else '正常',
            'score': score,
            'k': k,
            'd': d,
            'j': j
        }

    def _analyze_rsi(self, rsi_df: pd.DataFrame) -> Dict:
        """分析RSI"""
        rsi = rsi_df['rsi'].iloc[-1]

        if rsi > 80:
            return {'status': '超买', 'score': -0.3}
        elif rsi < 20:
            return {'status': '超卖', 'score': 0.3}
        elif rsi > 50:
            return {'status': '偏强', 'score': 0.1}
        else:
            return {'status': '偏弱', 'score': -0.1}

    def _analyze_macd(self, macd_df: pd.DataFrame) -> Dict:
        """分析MACD"""
        dif = macd_df['dif'].iloc[-1]
        dea = macd_df['dea'].iloc[-1]
        histogram = macd_df['histogram'].iloc[-1]

        score = 0
        status = []

        if dif > dea and dif.iloc[-2] <= macd_df['dea'].iloc[-2]:
            status.append('金叉')
            score += 0.3
        elif dif < dea and dif.iloc[-2] >= macd_df['dea'].iloc[-2]:
            status.append('死叉')
            score -= 0.3

        if histogram > 0:
            status.append('红柱')
            score += 0.1
        else:
            status.append('绿柱')
            score -= 0.1

        return {
            'status': '/'.join(status) if status else '中性',
            'score': score
        }

    def _analyze_boll(self, boll_df: pd.DataFrame) -> Dict:
        """分析BOLL"""
        price = boll_df['upper'].iloc[-1] * 0 + boll_df['lower'].iloc[-1] * 0
        upper = boll_df['upper'].iloc[-1]
        middle = boll_df['middle'].iloc[-1]
        lower = boll_df['lower'].iloc[-1]

        return {'status': '正常', 'score': 0}

    def _get_recommendation(self, combined_score: float, signals: Dict) -> str:
        """获取操作建议"""
        if combined_score >= 0.5:
            return '强烈买入'
        elif combined_score >= 0.2:
            return '适度买入'
        elif combined_score <= -0.5:
            return '强烈卖出'
        elif combined_score <= -0.2:
            return '适度卖出'
        else:
            return '观望'

    def _detect_divergence(self, price_df: pd.DataFrame, indicator) -> Dict:
        """检测背离"""
        if len(price_df) < 5:
            return {'type': '无背离', 'signal': '中性', 'confidence': 0}

        highs = price_df['high']
        lows = price_df['low']

        price_higher = highs.iloc[-1] > highs.iloc[-2] and highs.iloc[-2] > highs.iloc[-3]
        indicator_lower = indicator.iloc[-1] < indicator.iloc[-2]

        if price_higher and indicator_lower:
            return {
                'type': '顶背离',
                'signal': '看跌',
                'confidence': 0.7,
                'action': '减仓'
            }

        price_lower = lows.iloc[-1] < lows.iloc[-2] and lows.iloc[-2] < lows.iloc[-3]
        indicator_higher = indicator.iloc[-1] > indicator.iloc[-2]

        if price_lower and indicator_higher:
            return {
                'type': '底背离',
                'signal': '看涨',
                'confidence': 0.7,
                'action': '加仓'
            }

        return {'type': '无背离', 'signal': '中性', 'confidence': 0}
```

***

## 7. 使用示例

```python
# 示例数据
data = {
    'open': [100, 101, 102, 103, 104],
    'high': [102, 103, 104, 105, 106],
    'low': [99, 100, 101, 102, 103],
    'close': [101, 102, 103, 104, 105],
    'volume': [1000, 1100, 1200, 1300, 1400]
}

df = pd.DataFrame(data)

# 分析
analyzer = TechnicalIndicatorSynergy()
result = analyzer.analyze(df)

print(f"综合评分: {result['combined_score']:.2f}")
print(f"操作建议: {result['recommendation']}")
print(f"KDJ: {result['signals']['kdj']['status']}")
print(f"RSI: {result['signals']['rsi']['status']}")
print(f"MACD: {result['signals']['macd']['status']}")
print(f"背离: {result['divergence']['type']}")
```

***

## 8. 注意事项

1. **参数优化**：可根据市场特性调整各指标的参数
2. **权重分配**：可根据历史回测结果优化权重
3. **背离确认**：背离信号需结合成交量确认
4. **滞后性**：技术指标均有滞后性，需结合市场环境

***

## 9. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本 |
