---
module_id: FACTOR_DOC_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管理
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# 技术指标完整参数表

> 量化交易系统中所有技术指标的标准化定义、参数配置和计算公式

---

## 1. 指标分类体系

```
技术指标
├── 趋势跟踪指标
│   ├── 移动平均类 (MA, EMA, SMA, WMA)
│   ├── 趋势强度类 (ADX, Aroon)
│   └── 趋势轨道类 (BBANDS, SAR, Keltner)
├── 动量振荡指标
│   ├── 振荡器类 (RSI, Stoch, W%R, CCI)
│   └── 动量类 (MOM, ROC, CMF)
├── 成交量指标
│   ├── 量价类 (OBV, VWAP, MFI, VR)
│   └── 量价确认类 (VPT, AD)
├── 波动率指标
│   ├── 波动率类 (ATR, StdDev)
│   └── 通道类 (BBANDS, KC)
└── 市场广度指标
    ├── 广度类 (ADR, ADL, MCL)
    └── 情绪类 (put_call_ratio, VIX)
```

---

## 2. 趋势跟踪指标

### 2.1 移动平均类

#### SMA - 简单移动平均

```python
def sma(close: pd.Series, period: int) -> pd.Series:
    """简单移动平均

    公式: SMA = (P1 + P2 + ... + Pn) / n

    参数:
        period: 计算周期
    返回:
        SMA序列
    """
    return close.rolling(window=period).mean()
```

| 参数 | 默认值 | 常用值 | 说明 |
|------|--------|--------|------|
| period | 20 | 5, 10, 20, 30, 60 | 计算周期 |

#### EMA - 指数移动平均

```python
def ema(close: pd.Series, period: int) -> pd.Series:
    """指数移动平均

    公式: EMA = (Close - EMA_prev) * k + EMA_prev
          k = 2 / (period + 1)

    参数:
        period: 计算周期
    """
    return close.ewm(span=period, adjust=False).mean()
```

| 参数 | 默认值 | 常用值 | 说明 |
|------|--------|--------|------|
| period | 12 | 12, 26, 9, 50, 200 | 计算周期 |

#### MACD - 指数平滑异同移动平均线

```python
def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """MACD指标

    DIF = EMA(fast) - EMA(slow)
    DEA = EMA(DIF, signal)
    MACD = (DIF - DEA) * 2

    参数:
        fast: 快线周期 (默认12)
        slow: 慢线周期 (默认26)
        signal: 信号线周期 (默认9)
    """
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()

    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd = (dif - dea) * 2

    return pd.DataFrame({
        'DIF': dif,
        'DEA': dea,
        'MACD': macd
    })
```

| 参数 | 默认值 | 常用值 | 说明 |
|------|--------|--------|------|
| fast_period | 12 | 12 | 快线周期 |
| slow_period | 26 | 26 | 慢线周期 |
| signal_period | 9 | 9 | 信号线周期 |

---

### 2.2 趋势强度类

#### ADX - 平均趋向指数

```python
def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14):
    """ADX平均趋向指数

    +DI = (上升动向的N日平均值 / TR) * 100
    -DI = (下降动向的N日平均值 / TR) * 100
    DX = (|+DI - -DI| / |+DI + -DI|) * 100
    ADX = DX的N日平均值

    参数:
        high: 最高价
        low: 最低价
        close: 收盘价
        period: 计算周期 (默认14)
    """
    # 计算True Range
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # 计算动向
    plus_dm = where((high - high.shift(1)) > (low.shift(1) - low),
                     where((high - high.shift(1)) > 0, high - high.shift(1), 0), 0)
    minus_dm = where((low.shift(1) - low) > (high - high.shift(1)),
                      where((low.shift(1) - low) > 0, low.shift(1) - low, 0), 0)

    # 计算平滑值
    plus_di = 100 * (plus_dm.rolling(period).mean() / tr.rolling(period).mean())
    minus_di = 100 * (minus_dm.rolling(period).mean() / tr.rolling(period).mean())

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(period).mean()

    return pd.DataFrame({
        'ADX': adx,
        '+DI': plus_di,
        '-DI': minus_di
    })
```

| 参数 | 默认值 | 常用值 | 说明 |
|------|--------|--------|------|
| period | 14 | 14, 7 | 计算周期 |

---

### 2.3 趋势轨道类

#### BBANDS - 布林带

```python
def bbands(close: pd.Series, period: int = 20, std_dev: float = 2.0):
    """布林带

    中轨 = MA(close, period)
    上轨 = 中轨 + std_dev * StdDev(close, period)
    下轨 = 中轨 - std_dev * StdDev(close, period)

    参数:
        period: 周期 (默认20)
        std_dev: 标准差倍数 (默认2.0)
    """
    middle = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()

    upper = middle + std_dev * std
    lower = middle - std_dev * std

    bandwidth = (upper - lower) / middle
    pct_b = (close - lower) / (upper - lower)

    return pd.DataFrame({
        'BBAND_UPPER': upper,
        'BBAND_MIDDLE': middle,
        'BBAND_LOWER': lower,
        'BBAND_WIDTH': bandwidth,
        'BBAND_PCTB': pct_b
    })
```

| 参数 | 默认值 | 常用值 | 说明 |
|------|--------|--------|------|
| period | 20 | 20 | 中轨周期 |
| std_dev | 2.0 | 2.0 | 标准差倍数 |

#### SAR - 抛物线指标

```python
def psar(high, low, af_start: float = 0.02, af_max: float = 0.2):
    """抛物线SAR

    参数:
        af_start: 初始加速因子 (默认0.02)
        af_max: 最大加速因子 (默认0.2)
    """
    import numpy as np

    trend = np.zeros(len(high))
    sar = np.zeros(len(high))
    af = np.zeros(len(high))

    trend[0] = 1  # 假设上涨
    sar[0] = low[0]
    af[0] = af_start

    for i in range(1, len(high)):
        sar[i] = sar[i-1] + af[i-1] * (high[i-1] - sar[i-1]) if trend[i-1] == 1 else \
                 sar[i-1] + af[i-1] * (sar[i-1] - low[i-1])

        if trend[i-1] == 1:
            if low[i] < sar[i]:
                trend[i] = -1
                sar[i] = high[i-1]
                af[i] = af_start
            else:
                trend[i] = 1
                if high[i] > high[i-1]:
                    af[i] = min(af[i-1] + af_start, af_max)
                else:
                    af[i] = af[i-1]
        else:
            if high[i] > sar[i]:
                trend[i] = 1
                sar[i] = low[i-1]
                af[i] = af_start
            else:
                trend[i] = -1
                if low[i] < low[i-1]:
                    af[i] = min(af[i-1] + af_start, af_max)
                else:
                    af[i] = af[i-1]

    return pd.DataFrame({
        'SAR': sar,
        'TREND': trend,
        'AF': af
    })
```

| 参数 | 默认值 | 常用值 | 说明 |
|------|--------|--------|------|
| af_start | 0.02 | 0.02 | 初始加速因子 |
| af_max | 0.20 | 0.20 | 最大加速因子 |

---

## 3. 动量振荡指标

### 3.1 振荡器类

#### RSI - 相对强弱指数

```python
def rsi(close: pd.Series, period: int = 14):
    """相对强弱指数

    公式:
    RS = 平均涨幅 / 平均跌幅
    RSI = 100 - 100 / (1 + RS)

    参数:
        period: 计算周期 (默认14)
    """
    delta = close.diff()

    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi
```

| 参数 | 默认值 | 常用值 | 说明 |
|------|--------|--------|------|
| period | 14 | 6, 12, 24 | 计算周期 |

#### CCI - 商品通道指数

```python
def cci(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20):
    """商品通道指数

    公式:
    TP = (High + Low + Close) / 3
    SMA_TP = MA(TP, period)
    MAD_TP = MA(|TP - SMA_TP|, period)
    CCI = (TP - SMA_TP) / (0.015 * MAD_TP)

    参数:
        period: 计算周期 (默认20)
    """
    tp = (high + low + close) / 3
    sma_tp = tp.rolling(window=period).mean()
    mad_tp = (tp - sma_tp).abs().rolling(window=period).mean()

    cci = (tp - sma_tp) / (0.015 * mad_tp)

    return cci
```

| 参数 | 默认值 | 常用值 | 说明 |
|------|--------|--------|------|
| period | 20 | 14, 20 | 计算周期 |

#### W%R - 威廉指标

```python
def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14):
    """威廉指标

    公式:
    W%R = (N日最高价 - 收盘价) / (N日最高价 - N日最低价) * 100

    参数:
        period: 计算周期 (默认14)
    """
    highest_high = high.rolling(window=period).max()
    lowest_low = low.rolling(window=period).min()

    wr = -100 * (highest_high - close) / (highest_high - lowest_low)

    return wr
```

| 参数 | 默认值 | 常用值 | 说明 |
|------|--------|--------|------|
| period | 14 | 10, 14, 6 | 计算周期 |

---

### 3.2 动量类

#### MOM - 动量指标

```python
def momentum(close: pd.Series, period: int = 10):
    """动量指标

    公式:
    MOM = 收盘价 - N日前收盘价

    参数:
        period: 计算周期 (默认10)
    """
    return close - close.shift(period)
```

#### ROC - 变动率指标

```python
def roc(close: pd.Series, period: int = 12):
    """变动率指标

    公式:
    ROC = (收盘价 - N日前收盘价) / N日前收盘价 * 100

    参数:
        period: 计算周期 (默认12)
    """
    return ((close - close.shift(period)) / close.shift(period)) * 100
```

| 参数 | 默认值 | 常用值 | 说明 |
|------|--------|--------|------|
| period | 10 | 10, 12, 25 | 计算周期 |

---

## 4. 成交量指标

### 4.1 量价类

#### OBV - 能量潮

```python
def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """能量潮

    公式:
    OBV = 累计(IF 收盘 > 前收 THEN +成交量 ELSE -成交量)

    参数:
        无额外参数
    """
    obv = pd.Series(index=close.index, dtype=float)
    obv.iloc[0] = volume.iloc[0]

    for i in range(1, len(close)):
        if close.iloc[i] > close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
        elif close.iloc[i] < close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i-1]

    return obv
```

#### MFI - 资金流量指标

```python
def mfi(high: pd.Series, low: pd.Series, close: pd.Series,
        volume: pd.Series, period: int = 14) -> pd.Series:
    """资金流量指标

    公式:
    TP = (High + Low + Close) / 3
    MF = TP * Volume
    PMF = N日内正资金流量之和
    NMF = N日内负资金流量之和
    MFR = PMF / NMF
    MFI = 100 - 100 / (1 + MFR)

    参数:
        period: 计算周期 (默认14)
    """
    tp = (high + low + close) / 3
    mf = tp * volume

    positive_mf = mf.where(tp.diff() > 0, 0)
    negative_mf = mf.where(tp.diff() < 0, 0)

    pmf = positive_mf.rolling(window=period).sum()
    nmf = negative_mf.rolling(window=period).sum()

    mfr = pmf / nmf
    mfi = 100 - (100 / (1 + mfr))

    return mfi
```

| 参数 | 默认值 | 常用值 | 说明 |
|------|--------|--------|------|
| period | 14 | 14 | 计算周期 |

---

### 4.2 量价确认类

#### AD - 累积/派发线

```python
def ad(high: pd.Series, low: pd.Series, close: pd.Series,
       volume: pd.Series) -> pd.Series:
    """累积/派发线

    公式:
    MFV = ((Close - Low) - (High - Close)) / (High - Low) * Volume
    AD = 累计MFV
    """
    mfv = ((close - low) - (high - close)) / (high - low) * volume
    mfv = mfv.fillna(0)
    return mfv.cumsum()
```

---

## 5. 波动率指标

### 5.1 波动率类

#### ATR - 平均真实波幅

```python
def atr(high: pd.Series, low: pd.Series, close: pd.Series,
        period: int = 14) -> pd.Series:
    """平均真实波幅

    公式:
    TR = Max(High - Low, |High - Close_prev|, |Low - Close_prev|)
    ATR = MA(TR, period)

    参数:
        period: 计算周期 (默认14)
    """
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()

    return atr
```

| 参数 | 默认值 | 常用值 | 说明 |
|------|--------|--------|------|
| period | 14 | 14, 20 | 计算周期 |

#### STDDEV - 标准差

```python
def stddev(close: pd.Series, period: int = 20) -> pd.Series:
    """标准差

    公式:
    STDDEV = StdDev(Close, period)

    参数:
        period: 计算周期 (默认20)
    """
    return close.rolling(window=period).std()
```

---

## 6. 指标参数速查表

### 6.1 趋势类指标

| 指标 | 参数 | 默认值 | 常用值 | 适用场景 |
|------|------|--------|--------|---------|
| SMA | period | 20 | 5,10,20,30,60 | 趋势判断、支撑阻力 |
| EMA | period | 12 | 12,26,50,200 | 趋势跟踪、均线交叉 |
| MACD | fast,slow,signal | 12,26,9 | 12,26,9 | 趋势转折、动能判断 |
| ADX | period | 14 | 14,7 | 趋势强度 |
| BBANDS | period,std | 20,2.0 | 20,2.0 | 超买超卖、波动率 |
| SAR | af_start,af_max | 0.02,0.2 | 0.02,0.2 | 止损、趋势跟踪 |
| KELTNER | period,multiplier | 20,2.0 | 20,2.0 | 趋势通道 |

### 6.2 动量类指标

| 指标 | 参数 | 默认值 | 常用值 | 适用场景 |
|------|------|--------|--------|---------|
| RSI | period | 14 | 6,12,24 | 超买超卖 |
| CCI | period | 20 | 14,20 | 趋势转折 |
| W%R | period | 14 | 10,6 | 超买超卖 |
| MOM | period | 10 | 10,12 | 动能判断 |
| ROC | period | 12 | 12,25 | 变化率 |
| Stoch | k,d,slowk,slowd | 14,3,3 | 14,3,3 | 超买超卖 |

### 6.3 成交量类指标

| 指标 | 参数 | 默认值 | 常用值 | 适用场景 |
|------|------|--------|--------|---------|
| OBV | - | - | - | 量价确认 |
| MFI | period | 14 | 14 | 资金流向 |
| VR | period | 26 | 26 | 成交量强度 |
| AD | - | - | - | 累积派发 |
| VWAP | - | - | - | 日内基准 |

### 6.4 波动率类指标

| 指标 | 参数 | 默认值 | 常用值 | 适用场景 |
|------|------|--------|--------|---------|
| ATR | period | 14 | 14,20 | 止损设置 |
| STDDEV | period | 20 | 20 | 波动率量化 |
| BBANDS_WIDTH | period,std | 20,2.0 | 20,2.0 | 波动变化 |

---

## 7. 指标依赖关系

```python
INDICATOR_DEPENDENCIES = {
    'MACD': ['EMA'],
    'BBANDS': ['SMA', 'STDDEV'],
    'SAR': [],
    'ADX': ['TR'],
    'RSI': ['MOM'],
    'CCI': ['SMA', 'MAD'],
    'MFI': ['TP', 'MOM'],
    'OBV': ['MOM'],
    'KELTNER': ['EMA', 'ATR'],
    'STOCH': ['HHV', 'LLV']
}
```

---

**版本**: 1.0 | **更新**: 2026-03-28
