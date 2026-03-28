# 全成本模型

> 交易成本量化体系
>
> **配套文档**：
> - 主文档：[SPEC.md](../SPEC.md)
> - JSON Schemas：[architecture/json-schemas.md](./architecture/json-schemas.md)

***

## 1. 交易成本分类

| 成本类型 | 细分 | 计算方式 | 估算难度 |
|----------|------|----------|----------|
| **显性成本** | 佣金 | 固定费率 | 低 |
| | 印花税 | 卖出时收取 | 低 |
| **隐性成本** | 滑点 | 期望成交价vs实际成交价 | 中 |
| | 冲击成本 | 大额订单对价格的影响 | 高 |
| | 机会成本 | 未成交导致的收益损失 | 高 |

***

## 2. A股显性成本计算

| 费用类型 | 费率 | 收取方式 | 最低收费 |
|----------|------|----------|----------|
| 佣金 | 0.03%（默认，可调整） | 双向收取 | 5元/笔 |
| 印花税 | 0.1%（仅卖出） | 单向收取 | - |
| 过户费 | 0.001%（沪市） | 双向收取 | 1元/笔 |

***

## 3. Python实现

```python
def calculate_commission(trade_amount: float, rate: float = 0.0003) -> float:
    """计算佣金"""
    commission = trade_amount * rate
    return max(commission, 5.0)

def calculate_stamp_duty(trade_amount: float, direction: str = 'sell') -> float:
    """计算印花税（仅卖出收取）"""
    if direction == 'sell':
        return trade_amount * 0.001
    return 0.0

def calculate_transfer_fee(trade_amount: float, market: str = 'SH') -> float:
    """计算过户费（仅沪市）"""
    if market == 'SH':
        fee = trade_amount * 0.00001
        return max(fee, 1.0)
    return 0.0

def calculate_total_explicit_cost(trade_amount: float,
                                   direction: str = 'buy',
                                   market: str = 'SH',
                                   commission_rate: float = 0.0003) -> dict:
    """计算总显性成本"""
    commission = calculate_commission(trade_amount, commission_rate)
    stamp_duty = calculate_stamp_duty(trade_amount, direction)
    transfer_fee = calculate_transfer_fee(trade_amount, market)

    total = commission + stamp_duty + transfer_fee
    cost_rate = total / trade_amount

    return {
        'commission': commission,
        'stamp_duty': stamp_duty,
        'transfer_fee': transfer_fee,
        'total_cost': total,
        'cost_rate': cost_rate
    }
```

***

## 4. 隐性成本计算

| 滑点来源 | 计算公式 | 说明 |
|----------|----------|------|
| **价差成本** | $SpreadCost = (ask - bid)/midprice / 2$ | 买卖价差50% |
| **冲击成本** | $ImpactCost = 0.1 × OrderSize/ADV × σ$ | 订单占比×波动率 |
| **延迟成本** | $DelayCost = σ × sqrt(延迟分钟/240)$ | 时间损失 |

```python
def calculate_slippage(order_value: float, adv: float, volatility: float,
                      bid: float, ask: float) -> dict:
    """计算滑点成本"""
    spread_cost = (ask - bid) / ((ask + bid) / 2) / 2
    impact_cost = 0.1 * (order_value / adv) * volatility
    total_rate = spread_cost + impact_cost
    return {
        'spread': spread_cost,
        'impact': impact_cost,
        'total_rate': total_rate,
        'total': order_value * total_rate
    }
```

***

## 5. 年化成本估算

| 公式 | 说明 |
|------|------|
| $AnnualCost = 2 × Turnover × CostRate$ | 买卖双边×换手率 |
| $CostToReturn = AnnualCost / ExpectedReturn$ | 成本占收益比 |
| $NetReturn = ExpectedReturn - AnnualCostRate$ | 扣除成本后收益 |

***

## 6. 成本控制阈值

| 成本类型 | 预警阈值 | 熔断阈值 |
|----------|----------|----------|
| 单笔交易成本 | >0.2% | >0.3% |
| 年化成本率 | >收益30% | >收益50% |

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 整合附录J内容 |
