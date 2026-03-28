# 技术指标参数体系

> 核心技术指标量化体系
>
> **配套文档**：
> - 主文档：[SPEC.md](../SPEC.md)
> - 形态识别：[pattern-recognition.md](./pattern-recognition.md)

***

## 1. 均线系统参数

### 1.1 常用均线周期配置

| 均线类型 | 参数设置 | 用途 |
|----------|----------|------|
| 短期均线 | MA5、MA10 | 短线交易、止损参考 |
| 中期均线 | MA20、MA30 | 趋势判断、支撑压力 |
| 长期均线 | MA60、MA120、MA250 | 牛熊分界、长线趋势 |

### 1.2 均线多空排列

| 排列类型 | 条件 | 信号意义 |
|----------|------|----------|
| 多头排列 | MA5>MA10>MA20>MA60 | 强烈做多 |
| 价托 | MA5上穿MA10和MA20 | 短期做多 |
| 价压 | MA5下穿MA10和MA20 | 短期做空 |
| 黄金交叉 | 短均上穿长均 | 做多信号 |
| 死亡交叉 | 短均下穿长均 | 做空信号 |

***

## 2. MACD指标参数

### 2.1 标准参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 快速EMA | 12 | 短期平滑 |
| 慢速EMA | 26 | 长期平滑 |
| DIF计算 | DIF=EMA12-EMA26 | 快线 |
| DEA线 | 9日EMA | 信号线 |
| 柱状图 | (DIF-DEA)×2 | 动量指示 |

### 2.2 MACD信号量化

| 信号类型 | 量化条件 | 交易意义 |
|----------|----------|----------|
| 金叉 | DIF上穿DEA | 做多信号 |
| 死叉 | DIF下穿DEA | 做空信号 |
| 零轴上方 | DIF>0 AND DEA>0 | 多头市场 |
| 零轴下方 | DIF<0 AND DEA<0 | 空头市场 |
| 底背离 | 价格新低但DIF未新低 | 潜在反转 |
| 顶背离 | 价格新高但DIF未新高 | 潜在反转 |

***

## 3. KDJ指标参数

### 3.1 标准参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| RSV | (Cn-Ln)/(Hn-Ln)×100 | 未成熟随机值 |
| K值 | 前一日K值×2/3+今日RSV×1/3 | 平滑K线 |
| D值 | 前一日D值×2/3+今日K×1/3 | 平滑D线 |
| J值 | 3K-2D | 敏感指标 |

### 3.2 KDJ信号量化

| 信号类型 | 量化条件 | 信号级别 |
|----------|----------|----------|
| 超卖 | K<20 AND J<0 | 强烈买入 |
| 超买 | K>80 AND J>100 | 强烈卖出 |
| 金叉 | K上穿D | 买入信号 |
| 死叉 | K下穿D | 卖出信号 |
| 多周期共振买入 | 日线+60分钟+15分钟同时超卖 | 确定性买入 |

***

## 4. RSI指标参数

### 4.1 标准参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| RSI周期 | 14 | 常用周期 |
| 短期RSI | 6 | 敏感快速 |
| 长期RSI | 24 | 稳健慢速 |

### 4.2 RSI信号量化

| 信号类型 | 量化条件 | 交易意义 |
|----------|----------|----------|
| 超卖 | RSI<30 | 潜在买入 |
| 超买 | RSI>70 | 潜在卖出 |
| 金叉 | RSI6上穿RSI24 | 短期转强 |
| 死叉 | RSI6下穿RSI24 | 短期转弱 |

***

## 5. 布林带指标参数

### 5.1 标准参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 中轨 | 20日均线(MA20) | 趋势中心 |
| 标准差倍数 | 2 | 通道宽度 |
| 上轨 | MA20+2×STD | 压力位 |
| 下轨 | MA20-2×STD | 支撑位 |

### 5.2 布林带信号量化

| 信号类型 | 量化条件 | 交易意义 |
|----------|----------|----------|
| 开口放大 | 带宽扩大>20% | 趋势启动 |
| 收口缩量 | 带宽收缩<10% | 酝酿突破 |
| 价格触下轨 | Low≤BB_lower | 潜在买入 |
| 价格触上轨 | High≥BB_upper | 潜在卖出 |
| 中轨支撑 | 回踩MA20企稳 | 持有信号 |

***

## 6. ATR指标参数

### 6.1 ATR计算

```python
def calculate_atr(high, low, close, period=14):
    """计算ATR"""
    tr = np.maximum(
        high - low,
        np.maximum(
            abs(high - close.shift(1)),
            abs(low - close.shift(1))
        )
    )
    atr = tr.rolling(window=period).mean()
    return atr
```

### 6.2 ATR应用

| 应用场景 | 计算方式 | 用途 |
|----------|----------|------|
| 止损设置 | 买入价 - 2×ATR | 跟踪止损 |
| 波动率标准化 | ATR/价格×100 | 波动率比较 |
| 仓位计算 | 风险金额/ATR | 仓位管理 |

***

## 7. Python指标库

```python
import pandas as pd
import numpy as np

class TechnicalIndicators:
    """技术指标计算库"""

    @staticmethod
    def ma(df, column='close', periods=[5, 10, 20, 60]):
        """计算均线"""
        result = {}
        for p in periods:
            result[f'ma{p}'] = df[column].rolling(window=p).mean()
        return pd.DataFrame(result)

    @staticmethod
    def macd(df, column='close', fast=12, slow=26, signal=9):
        """计算MACD"""
        ema_fast = df[column].ewm(span=fast).mean()
        ema_slow = df[column].ewm(span=slow).mean()
        dif = ema_fast - ema_slow
        dea = dif.ewm(span=signal).mean()
        macd = (dif - dea) * 2
        return {'dif': dif, 'dea': dea, 'macd': macd}

    @staticmethod
    def kdj(df, high='high', low='low', close='close', n=9, m1=3, m2=3):
        """计算KDJ"""
        low_n = df[low].rolling(window=n).min()
        high_n = df[high].rolling(window=n).max()
        rsv = (df[close] - low_n) / (high_n - low_n) * 100

        k = rsv.ewm(com=(m1 - 1)).mean()
        d = k.ewm(com=(m2 - 1)).mean()
        j = 3 * k - 2 * d

        return {'k': k, 'd': d, 'j': j}

    @staticmethod
    def rsi(df, column='close', period=14):
        """计算RSI"""
        delta = df[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def bollinger_bands(df, column='close', period=20, std_dev=2):
        """计算布林带"""
        ma = df[column].rolling(window=period).mean()
        std = df[column].rolling(window=period).std()
        upper = ma + std_dev * std
        lower = ma - std_dev * std
        return {'upper': upper, 'middle': ma, 'lower': lower}

    @staticmethod
    def atr(df, high='high', low='low', close='close', period=14):
        """计算ATR"""
        tr = np.maximum(
            df[high] - df[low],
            np.maximum(
                abs(df[high] - df[close].shift(1)),
                abs(df[low] - df[close].shift(1))
            )
        )
        return tr.rolling(window=period).mean()
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 整合附录O内容 |
