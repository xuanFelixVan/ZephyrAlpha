﻿---
module_id: TACTICS_STRATEGY_SPEC_S001_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
standard_type: 专业量化机构文档
applicable_scope: 全系?
compliance_level: 初始标准
parent_document: INDEX.md
implementation_status: 进行?
responsibility:
  - 市场状态识别 (Layer 4)
---


# Strategy_Spec_S001.md - 均线趋势跟踪策略
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 基于双均线交叉的趋势追踪策略


## 1. 策略逻辑描述

### 1.1 核心哲学

**赚钱逻辑**?句话?
1. 当短期均线（MA5）上穿长期均线（MA20）时，市场进入上升趋势，发出买入信号
2. 当短期均线（MA5）下穿长期均线（MA20）时，市场进入下降趋势，发出卖出信号
3. 通过跟踪趋势方向，在趋势初期介入，在趋势反转时及时止?

### 1.2 适用条件

| 项目 | ?|
|------|-----|
| 适用标的 | A股主板（沪深300成分股） |
| 操作周期 | 1小时K?|
| 市场状?| 趋势市（排除震荡市） |
| 风险等级 | 中等 |


## 2. 信号计算公式

### 2.1 均线计算

$$MA_5 = \frac{\sum_{i=0}^{4} Close_i}{5}$$

$$MA_{20} = \frac{\sum_{i=0}^{19} Close_i}{20}$$

### 2.2 信号生成

$$Signal = \begin{cases}
BUY & \text{if } MA_5 > MA_{20} \text{ AND } MA_5[-1] \leq MA_{20}[-1] \\
SELL & \text{if } MA_5 < MA_{20} \text{ AND } MA_5[-1] \geq MA_{20}[-1] \\
HOLD & \text{otherwise}
\end{cases}$$

其中 $[-1]$ 表示前一个时间步的?

### 2.3 置信度计?

$$Confidence = \frac{|MA_5 - MA_{20}|}{MA_{20}} \times 100\%$$

- 置信?> 2% 时，信号强度??
- 置信?1%-2% 时，信号强度??
- 置信?< 1% 时，信号强度??


## 3. 伪代码验?

```python
def calculate_signal(close_prices, ma5_period=5, ma20_period=20):
    """
    计算均线交叉信号
    
    Args:
        close_prices: 收盘价列?[100, 101, 102, ...]
        ma5_period: MA5周期（默??
        ma20_period: MA20周期（默?0?
    
    Returns:
        signal: "BUY" / "SELL" / "HOLD"
        confidence: 0.0 - 1.0
    """
    
    # Step 1: 计算MA5和MA20
    ma5_current = mean(close_prices[-5:])
    ma5_previous = mean(close_prices[-6:-1])
    
    ma20_current = mean(close_prices[-20:])
    ma20_previous = mean(close_prices[-21:-1])
    
    # Step 2: 检测交?
    if ma5_current > ma20_current and ma5_previous <= ma20_previous:
        signal = "BUY"
    elif ma5_current < ma20_current and ma5_previous >= ma20_previous:
        signal = "SELL"
    else:
        signal = "HOLD"
    
    # Step 3: 计算置信?
    confidence = abs(ma5_current - ma20_current) / ma20_current
    
    return signal, confidence

# 测试用例
close_prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
                110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120]
signal, confidence = calculate_signal(close_prices)
print(f"Signal: {signal}, Confidence: {confidence:.2%}")
# 预期输出: Signal: BUY, Confidence: 0.91%
```


## 4. 输入输出规范

### 4.1 输入数据

| 字段 | 类型 | 说明 |
|------|------|------|
| timestamp | string | ISO 8601时间?|
| symbol | string | 股票代码（如000001.SZ?|
| ohlcv | object | OHLCV数据 |
| ohlcv.close | float | 收盘?|
| ohlcv.volume | int | 成交?|

### 4.2 输出信号

```json
{
  "timestamp": "2026-03-28T10:00:00Z",
  "symbol": "000001.SZ",
  "strategy_id": "S001_TREND_FOLLOW",
  "signal": "BUY",
  "confidence": 0.0091,
  "target_price": 121.0,
  "stop_loss": 98.0,
  "position_size": 1000
}
```


## 5. 风险控制

### 5.1 止损设置

$$StopLoss = EntryPrice \times (1 - StopLossRatio)$$

其中 $StopLossRatio = 2\%$

### 5.2 止盈设置

$$TakeProfit = EntryPrice \times (1 + TakeProfitRatio)$$

其中 $TakeProfitRatio = 5\%$

### 5.3 仓位管理

| 信号强度 | 仓位比例 |
|---------|---------|
| 强（>2%?| 100% |
| 中（1%-2%?| 50% |
| 弱（<1%?| 25% |


## 6. 异常处理

### 6.1 数据缺失

**处理方式**: 使用前向填充（Forward Fill?

```python
if close_price is None:
    close_price = previous_close_price
```

### 6.2 断网/延迟

**处理方式**: 缓存最?00根K线，使用本地数据

```python
if network_error:
    use_cached_data(last_100_bars)
    log_warning("Using cached data due to network error")
```

### 6.3 极端行情

**处理方式**: 触发熔断机制

```python
if price_change > 10%:  # 单根K线涨?10%
    trigger_circuit_breaker()
    log_alert("Circuit breaker triggered")
```


## 7. 回测验证标准

| 指标 | 目标?| 说明 |
|------|--------|------|
| 夏普比率 | > 1.5 | 风险调整收益 |
| 最大回?| < 15% | 最坏情况损?|
| 胜率 | > 50% | 盈利交易占比 |
| 盈亏?| > 1.5 | 平均盈利/平均亏损 |
| 年化收益 | > 15% | 年均收益?|


## 8. 参数说明

| 参数 | 默认?| 范围 | 说明 |
|------|--------|------|------|
| MA5周期 | 5 | 3-10 | 短期均线周期 |
| MA20周期 | 20 | 15-30 | 长期均线周期 |
| 止损比例 | 2% | 1%-5% | 单笔最大亏?|
| 止盈比例 | 5% | 3%-10% | 单笔目标收益 |
| 最大仓?| 100% | 50%-100% | 单个策略最大仓?|


## 9. 注意事项

- ⚠️ 该策略在趋势市表现良好，在震荡市容易产生虚假信号
- ⚠️ 需要配合市场状态识别模块（Layer 1）使?
- ⚠️ 参数需要根据不同标的进行优?
- ⚠️ 需要定期回测验证，至少每月一?


## 10. 相关文档

| 文档 | 说明 |
|------|------|
| [API_Contract.md](03_TRADING_TACTICS/API_Contract.md) | 接口规范 |
| [02_ALPHA_FACTORS/](02_FACTOR_LIBRARY\02_ALPHA_FACTORS) | 因子?|
| [05_BACKTEST/](../02_FACTOR_LIBRARY/05_BACKTEST/) | 回测报告 |


**版本**: 1.0 | **更新**: 2026-03-28 | **状?*: Draft
