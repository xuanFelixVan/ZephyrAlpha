---
module_id: SIGNAL_GENERATION
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 信号生成系统文档
---

﻿---
module_id: EXEC_SIGNAL_GENERATION_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 交易执行系统设计与优化与实施指导
standard_type: 专业量化机构交易执行标准
applicable_scope: 交易执行与监?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
---
---


# 信号生成系统
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 策略信号到交易订单的转换引擎
>
> **版本**: v1.0
> **更新**: 2026-03-28
> **优先?*: P0 - 核心系统

---

## 1. 概述

信号生成系统是策略与执行之间的桥梁，负责将策略产生的因子信号转化为可执行的交易信号?

```
因子信号 ?信号生成 ?订单信号 ?交易执行
     ?          ?          ?
  Layer 2    本模?     Layer 5
```

---

## 2. 信号类型

### 2.1 信号分类

| 信号类型 | 说明 | 示例 |
|----------|------|------|
| BUY | 买入信号 | 因子值高于阈?|
| SELL | 卖出信号 | 因子值低于阈?|
| HOLD | 持有信号 | 无显著信?|
| COVER | 买回信号 | 做空时平?|
| SHORT | 卖出信号 | 做空时开?|

### 2.2 信号强度

| 强度等级 | 范围 | 说明 |
|----------|------|------|
| STRONG_BUY | >= 0.8 | 强烈买入 |
| BUY | 0.5 - 0.8 | 买入 |
| NEUTRAL | -0.5 - 0.5 | 中?|
| SELL | -0.8 - -0.5 | 卖出 |
| STRONG_SELL | <= -0.8 | 强烈卖出 |

---

## 3. 信号生成流程

```
┌─────────────────────────────────────────────────────────────?
?                   信号生成流程                              ?
├─────────────────────────────────────────────────────────────?
? 1. 因子信号输入  ? 2. 信号计算  ? 3. 信号过滤  ? 4. 输出  ?
└─────────────────────────────────────────────────────────────?
```

```python
class SignalGenerator:
    """信号生成?""

    def __init__(self, config: dict):
        self.min_signal_strength = config.get('min_signal_strength', 0.5)
        self.confirmation_enabled = config.get('confirmation_enabled', True)
        self.volume_filter_enabled = config.get('volume_filter_enabled', True)

    def generate(self, factor_signals: pd.DataFrame, market_data: dict) -> pd.DataFrame:
        """生成交易信号"""
        # 步骤1: 计算原始信号
        raw_signals = self._calculate_raw_signals(factor_signals)

        # 步骤2: 信号过滤
        filtered_signals = self._filter_signals(raw_signals, market_data)

        # 步骤3: 信号确认
        confirmed_signals = self._confirm_signals(filtered_signals, market_data)

        return confirmed_signals

    def _calculate_raw_signals(self, factor_signals: pd.DataFrame) -> pd.DataFrame:
        """计算原始信号"""
        # 将因子值标准化到[-1, 1]区间
        normalized = (factor_signals - factor_signals.mean()) / factor_signals.std()
        return normalized.clip(-1, 1)

    def _filter_signals(self, signals: pd.DataFrame, market_data: dict) -> pd.DataFrame:
        """过滤信号"""
        filtered = signals.copy()

        # 流动性过?
        if self.volume_filter_enabled:
            liquid_stocks = market_data.get('liquid_stocks', signals.columns)
            filtered = filtered[liquid_stocks]

        return filtered

    def _confirm_signals(self, signals: pd.DataFrame, market_data: dict) -> pd.DataFrame:
        """确认信号"""
        if not self.confirmation_enabled:
            return signals

        confirmed = signals.copy()

        # 需要多个信号源确认
        for stock in confirmed.columns:
            if self._has_volume_confirmation(stock, market_data):
                confirmed[stock] *= 1.2  # 成交量确认后增强信号

        return confirmed.clip(-1, 1)
```

---

## 4. 多信号合?

### 4.1 简单加权平?

```python
class WeightedSignalSynthesizer:
    """加权信号合成?""

    def __init__(self, weights: dict):
        """
        weights: {因子名称: 权重}
        """
        self.weights = weights
        self._validate_weights()

    def _validate_weights(self):
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"权重之和必须?，当? {total}")

    def synthesize(self, factor_data: dict) -> pd.Series:
        """合成多因子信?""
        result = None

        for factor_name, weight in self.weights.items():
            if factor_name in factor_data:
                if result is None:
                    result = factor_data[factor_name] * weight
                else:
                    result += factor_data[factor_name] * weight

        return result.fillna(0)
```

### 4.2 动态权?

```python
class DynamicWeightSynthesizer:
    """动态权重信号合?""

    def __init__(self):
        self.base_weights = {}
        self.ic_history = {}

    def update_weights(self, factor_name: str, ic_value: float):
        """根据IC更新因子权重"""
        self.ic_history[factor_name] = ic_value

        # 使用IC的softmax作为权重
        all_ics = list(self.ic_history.values())
        exp_ics = np.exp(np.array(all_ics) * 10)  # 放大差异
        total = sum(exp_ics)

        self.base_weights[factor_name] = exp_ics[list(self.ic_history.keys()).index(factor_name)] / total

    def synthesize(self, factor_data: dict) -> pd.Series:
        """动态权重合?""
        result = None

        for factor_name, weight in self.base_weights.items():
            if factor_name in factor_data:
                if result is None:
                    result = factor_data[factor_name] * weight
                else:
                    result += factor_data[factor_name] * weight

        return result.fillna(0)
```

---

## 5. 信号过滤机制

### 5.1 流动性过?

```python
class LiquidityFilter:
    """流动性过?""

    def __init__(self, min_avg_volume: float = 1000000, min_trading_days: int = 20):
        self.min_avg_volume = min_avg_volume  # 最小日均成交量
        self.min_trading_days = min_trading_days

    def filter(self, signals: pd.DataFrame, volume_data: pd.Series) -> pd.DataFrame:
        """过滤低流动性股?""
        avg_volume = volume_data.rolling(self.min_trading_days).mean()
        liquid_mask = avg_volume >= self.min_avg_volume

        filtered = signals.copy()
        filtered = filtered.where(liquid_mask, 0)

        return filtered
```

### 5.2 波动率过?

```python
class VolatilityFilter:
    """波动率过?""

    def __init__(self, min_volatility: float = 0.01, max_volatility: float = 0.5):
        self.min_volatility = min_volatility  # 最小波动率
        self.max_volatility = max_volatility  # 最大波动率

    def filter(self, signals: pd.DataFrame, returns: pd.Series, window: int = 20) -> pd.DataFrame:
        """过滤极端波动?""
        volatility = returns.rolling(window).std() * np.sqrt(252)

        low_vol_mask = volatility >= self.min_volatility
        high_vol_mask = volatility <= self.max_volatility
        vol_mask = low_vol_mask & high_vol_mask

        filtered = signals.copy()
        filtered = filtered.where(vol_mask, 0)

        return filtered
```

### 5.3 信号衰减处理

```python
class SignalDecayHandler:
    """信号衰减处理"""

    def __init__(self, decay_rate: float = 0.1):
        self.decay_rate = decay_rate  # 每日衰减?

    def apply_decay(self, signals: pd.DataFrame, holding_days: int) -> pd.DataFrame:
        """应用信号衰减"""
        decay_factor = (1 - self.decay_rate) ** holding_days
        return signals * decay_factor

    def calculate_decay_IC(self, original_ic: float, holding_days: int) -> float:
        """计算衰减后的IC"""
        return original_ic * (1 - self.decay_rate) ** holding_days
```

---

## 6. 信号质量评估

### 6.1 评估指标

| 指标 | 说明 | 评判标准 |
|------|------|----------|
| 信号胜率 | 信号产生收益的比?| > 55% |
| 信号IC | 信号与收益相关?| > 0.03 |
| 信号持续?| 信号持续时间 | > 3?|
| 信号一致?| 样本内外表现差异 | < 30% |

### 6.2 评估代码

```python
class SignalQualityEvaluator:
    """信号质量评估?""

    def evaluate(self, signals: pd.DataFrame, returns: pd.Series) -> dict:
        """评估信号质量"""
        metrics = {}

        # 计算信号胜率
        metrics['win_rate'] = self._calculate_win_rate(signals, returns)

        # 计算信号IC
        metrics['signal_ic'] = self._calculate_signal_ic(signals, returns)

        # 计算信号持续?
        metrics['signal_duration'] = self._calculate_duration(signals)

        # 计算信号一致?
        metrics['consistency'] = self._calculate_consistency(signals, returns)

        return metrics

    def _calculate_win_rate(self, signals: pd.DataFrame, returns: pd.Series) -> float:
        """计算胜率"""
        aligned_returns = returns.loc[signals.index]
        correct_direction = (signals * aligned_returns) > 0
        return correct_direction.mean()

    def _calculate_signal_ic(self, signals: pd.DataFrame, returns: pd.Series) -> float:
        """计算信号IC"""
        aligned_returns = returns.loc[signals.index]
        signal_rank = signals.rank(axis=1, pct=True)
        return signal_rank.corrwith(aligned_returns, axis=1).mean()

    def _calculate_duration(self, signals: pd.DataFrame) -> float:
        """计算信号平均持续天数"""
        # 简化版本：计算非零信号的平均比?
        return (signals != 0).sum(axis=1).mean()

    def _calculate_consistency(self, signals: pd.DataFrame, returns: pd.Series) -> float:
        """计算样本内外一致?""
        mid_point = len(signals) // 2
        in_sample = signals.iloc[:mid_point]
        out_sample = signals.iloc[mid_point:]

        in_returns = returns.iloc[:mid_point]
        out_returns = returns.iloc[mid_point:]

        in_ic = self._calculate_signal_ic(in_sample, in_returns)
        out_ic = self._calculate_signal_ic(out_sample, out_returns)

        if abs(in_ic) < 0.001:
            return 0

        return 1 - abs(in_ic - out_ic) / abs(in_ic)
```

---

## 7. 配置模板

```yaml
# config/signal_generation.yaml
signal_generation:
  # 信号生成基础配置
  min_signal_strength: 0.5          # 最小信号强?
  confirmation_enabled: true       # 是否启用信号确认
  volume_filter_enabled: true      # 是否启用流动性过?

  # 信号合成配置
  synthesis:
    method: "dynamic_weight"        # simple_weighted | dynamic_weight | ml_weighted
    weights:
      momentum: 0.3
      value: 0.25
      quality: 0.25
      sentiment: 0.2

  # 过滤配置
  filters:
    liquidity:
      enabled: true
      min_avg_volume: 1000000       # 最小日均成交量
      min_trading_days: 20

    volatility:
      enabled: true
      min_volatility: 0.01
      max_volatility: 0.5

  # 衰减配置
  decay:
    enabled: true
    decay_rate: 0.1                # 每日衰减10%
    max_holding_days: 10

  # 信号质量阈?
  quality_thresholds:
    min_win_rate: 0.55
    min_signal_ic: 0.03
    max_consistency_drop: 0.3
```

---

## 8. 输出格式

```python
SignalOutput = {
    'signal': pd.DataFrame,        # 信号矩阵 (date x stock)
    'strength': pd.DataFrame,      # 信号强度 (date x stock)
    'direction': pd.DataFrame,     # 信号方向 BUY/SELL/HOLD
    'timestamp': datetime,          # 生成时间
    'metadata': {
        'factors_used': list,       # 使用的因子列?
        'filter_applied': list,     # 应用的过滤器
        'quality_metrics': dict      # 质量指标
    }
}
```

---

## 9. 目录位置

```
04_EXECUTION/
├── 01_EVENT_ENGINE/
├── 02_TRADE_EXECUTOR/
?  └── signal_generation.md      # 本文?
├── 03_MONITORING/
└── 04_AI_COMMITTEE/
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本 |
