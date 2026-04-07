---
module_id: BREADTH_INDICATORS_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 因子工程团队
responsibility:
  - 因子计算、因子库管理
standard_type: 通用文档
applicable_scope: 全系统
compliance_level: 专业标准
---
---



# 市场广度指标
> **核心职责**: 市场宽度指标定义和计算，涉及市场广度指标
> **职责边界**: 
> - ✅ 本文档负责：市场宽度指标定义和计算相关内容
> - ❌ 本文档不负责：具体实现细节、其他模块内容


> 涨跌比率、腾落指标、市场广度分�?

---

## 1. 广度指标概述

| 指标 | 名称 | 说明 | 用�?|
|------|------|------|------|
| ADR | 涨跌比率 | N日内上涨家数/下跌家数 | 市场情绪 |
| ADL | 腾落指标 | 每日上涨-下跌家数累计 | 趋势确认 |
| MCL | 麦克连指�?| 基于ADL的动量振�?| 广度动量 |
| NDR | 涨跌家数�?| 上涨家数-下跌家数 | 资金轮动 |

---

## 2. 基础广度指标计算

```python
import pandas as pd
import numpy as np
from typing import List

class BreadthIndicators:
    """市场广度指标计算"""

    def calculate_adr(
        self,
        advance: pd.Series,      # 上涨家数
        decline: pd.Series,      # 下跌家数
        window: int = 10
    ) -> pd.Series:
        """计算涨跌比率 (Advance-Decline Ratio)

        ADR = N日内上涨家数之和 / N日内下跌家数之和

        参数�?
            advance: 上涨家数序列
            decline: 下跌家数序列
            window: 计算窗口

        返回�?
            ADR序列
        """
        adv_sum = advance.rolling(window).sum()
        dec_sum = decline.rolling(window).sum()

        adr = adv_sum / dec_sum
        adr[dec_sum == 0] = np.inf  # 避免除零

        return adr

    def calculate_adl(
        self,
        advance: pd.Series,
        decline: pd.Series
    ) -> pd.Series:
        """计算腾落指标 (Advance-Decline Line)

        ADL = Σ(上涨家数 - 下跌家数)

        返回�?
            ADL累计序列
        """
        net = advance - decline
        adl = net.cumsum()
        return adl

    def calculate_mcl(
        self,
        adl: pd.Series,
        short_period: int = 19,
        long_period: int = 39
    ) -> pd.Series:
        """计算麦克连指�?(McClellan Oscillator)

        MCL = ADL的短期EMA - ADL的长期EMA

        参数�?
            adl: ADL序列
            short_period: 短期EMA周期（默�?9�?
            long_period: 长期EMA周期（默�?9�?

        返回�?
            MCL序列
        """
        ema_short = adl.ewm(span=short_period).mean()
        ema_long = adl.ewm(span=long_period).mean()

        mcl = ema_short - ema_long
        return mcl
```

---

## 3. 广度动量指标

```python
    def calculate_adl_momentum(
        self,
        adl: pd.Series,
        period: int = 10
    ) -> pd.Series:
        """计算ADL动量

        ADL动量 = ADL - ADL的N日前�?
        """
        return adl - adl.shift(period)

    def calculate_adl_rate_of_change(
        self,
        adl: pd.Series,
        period: int = 10
    ) -> pd.Series:
        """计算ADL变化�?

        ROC = (ADL - ADL_N日前) / ADL_N日前 * 100
        """
        adl_change = adl - adl.shift(period)
        roc = (adl_change / adl.shift(period)) * 100
        return roc

    def calculate_simplified_mcl(
        self,
        advance: pd.Series,
        decline: pd.Series,
        short_period: int = 19,
        long_period: int = 39
    ) -> pd.Series:
        """计算简化版麦克连指标（直接用涨跌家数）

        使用简化公式：
        MCL = EMA(上涨-下跌, 19) - EMA(上涨-下跌, 39)
        """
        net = advance - decline
        ema_short = net.ewm(span=short_period).mean()
        ema_long = net.ewm(span=long_period).mean()

        return ema_short - ema_long
```

---

## 4. 市场广度因子

```python
class BreadthFactor:
    """市场广度因子"""

    def build_breadth_momentum_factor(
        self,
        index_components: List[str],
        end_date: str,
        lookback: int = 20
    ) -> pd.Series:
        """构建广度动量因子

        因子逻辑�?
        - 上涨家数占比 > 50%：市场偏�?
        - ADL创新高：趋势确认
        - MCL > 0：动量偏�?
        """
        # 获取成分股收益率
        returns = self.get_stock_returns(index_components, end_date, lookback)

        # 计算每日上涨/下跌家数
        advance = (returns > 0).sum(axis=1)
        decline = (returns < 0).sum(axis=1)
        unchanged = (returns == 0).sum(axis=1)

        # 计算广度指标
        breadth = BreadthIndicators()
        adr = breadth.calculate_adr(advance, decline, window=10)
        adl = breadth.calculate_adl(advance, decline)
        mcl = breadth.calculate_simplified_mcl(advance, decline)

        # 构建综合因子
        # 归一化各指标
        adr_norm = (adr - adr.mean()) / adr.std()
        adl_norm = (adl - adl.mean()) / adl.std()
        mcl_norm = (mcl - mcl.mean()) / mcl.std()

        # 等权合成
        composite = (adr_norm + adl_norm + mcl_norm) / 3

        return composite

    def build_sector_breadth_factor(
        self,
        sector: str,
        end_date: str
    ) -> pd.DataFrame:
        """构建行业广度因子

        计算各行业的涨跌家数�?
        """
        stocks = self.get_sector_stocks(sector)
        returns = self.get_stock_returns(stocks, end_date, 1)

        sector_advance = (returns > 0).sum(axis=1).iloc[-1]
        sector_decline = (returns < 0).sum(axis=1).iloc[-1]

        breadth_ratio = sector_advance / (sector_advance + sector_decline)

        return {
            'sector': sector,
            'advance_count': int(sector_advance),
            'decline_count': int(sector_decline),
            'breadth_ratio': breadth_ratio
        }
```

---

## 5. 广度与价格背�?

```python
class BreadthDivergence:
    """广度背离分析"""

    def detect_adl_price_divergence(
        self,
        index_price: pd.Series,
        adl: pd.Series,
        window: int = 20
    ) -> List[dict]:
        """检测ADL与价格的背离

        逻辑�?
        - 价格创新高但ADL未创新高：顶背离（看跌）
        - 价格创新低但ADL未创新低：底背离（看涨）
        """
        divergences = []

        # 计算价格和ADL的N日高低点
        for i in range(window, len(index_price)):
            current_date = index_price.index[i]

            # 价格是否创新�?
            price_window = index_price.iloc[i-window:i]
            is_price_high = index_price.iloc[i] >= price_window.max()

            # ADL是否创新�?
            adl_window = adl.iloc[i-window:i]
            is_adl_high = adl.iloc[i] >= adl_window.max()

            # 顶背离：价格新高但ADL未新�?
            if is_price_high and not is_adl_high:
                divergences.append({
                    'date': current_date,
                    'type': 'bearish',  # 顶背�?
                    'price': index_price.iloc[i],
                    'adl': adl.iloc[i],
                    'strength': self._calculate_divergence_strength(
                        index_price.iloc[i], price_window.max(),
                        adl.iloc[i], adl_window.max()
                    )
                })

            # 底背离：价格新低但ADL未新�?
            is_price_low = index_price.iloc[i] <= price_window.min()
            is_adl_low = adl.iloc[i] <= adl_window.min()

            if is_price_low and not is_adl_low:
                divergences.append({
                    'date': current_date,
                    'type': 'bullish',  # 底背�?
                    'price': index_price.iloc[i],
                    'adl': adl.iloc[i],
                    'strength': self._calculate_divergence_strength(
                        adl_window.min(), adl.iloc[i],
                        price_window.min(), index_price.iloc[i]
                    )
                })

        return divergences

    def _calculate_divergence_strength(
        self,
        price_high1: float,
        price_high2: float,
        adl_high1: float,
        adl_high2: float
    ) -> float:
        """计算背离强度"""
        price_diff = (price_high1 - price_high2) / price_high2
        adl_diff = (adl_high1 - adl_high2) / abs(adl_high2) if adl_high2 != 0 else 0

        return abs(price_diff - adl_diff)
```

---

## 6. 市场广度监控面板

```python
class BreadthMonitor:
    """广度指标监控"""

    def generate_daily_report(
        self,
        advance: int,
        decline: int,
        index_change: float
    ) -> dict:
        """生成每日广度报告"""
        total = advance + decline
        advance_ratio = advance / total if total > 0 else 0.5

        # 市场情绪判断
        if advance_ratio > 0.6:
            sentiment = '强烈看涨'
        elif advance_ratio > 0.52:
            sentiment = '偏看�?
        elif advance_ratio < 0.4:
            sentiment = '强烈看跌'
        elif advance_ratio < 0.48:
            sentiment = '偏看�?
        else:
            sentiment = '中�?

        return {
            'date': pd.Timestamp.now(),
            'advance_count': advance,
            'decline_count': decline,
            'advance_ratio': advance_ratio,
            'index_change': index_change,
            'sentiment': sentiment,
            'breadth_confirms_price': (
                (index_change > 0 and advance_ratio > 0.5) or
                (index_change < 0 and advance_ratio < 0.5)
            )
        }
```

---

## 7. 指标参数配置

```yaml
breadth_indicators:
  adr:
    window: 10
    overbought_threshold: 1.5   # ADR > 1.5 谨慎
    oversold_threshold: 0.67     # ADR < 0.67 关注

  mcl:
    short_period: 19
    long_period: 39
    bullish_threshold: 50        # MCL > 50 看涨
    bearish_threshold: -50      # MCL < -50 看跌

  adl:
    bullish_confirmation: "ADL创新�?
    bearish_confirmation: "ADL创新�?

  alerts:
    - condition: "ADR连续3�?> 1.5"
      message: "市场可能过热"
    - condition: "ADR连续3�?< 0.67"
      message: "市场可能见底"
    - condition: "MCL从负转正"
      message: "广度动量转多"
```

---

**版本**: 1.0 | **更新**: 2026-03-28

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
