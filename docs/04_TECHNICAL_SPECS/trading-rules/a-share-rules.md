# A股基础交易规则

> A股市场交易制度量化体系
>
> **配套文档**：
> - 主文档：[SPEC.md](../SPEC.md)
> - 全成本模型：[modules/cost-model.md](./modules/cost-model.md)

***

## 1. T+1交易制度量化

```python
class T1TradingSystem:
    """
    T+1交易制度量化
    A股当天买入，第二天才能卖出
    """

    T1_RULES = {
        '当日买入锁定': True,
        '次日解除限制': True,
        '适用范围': 'A股市场所有品种',
        '例外情况': ['ETF基金', '可转债', '期权']
    }

    def check_sell_permission(self, position, buy_date, current_date):
        """
        检查卖出权限
        """
        if buy_date == current_date:
            return {
                'can_sell': False,
                'reason': 'T+1制度：当日买入不能卖出',
                'available_date': self.next_trading_day(buy_date)
            }
        return {'can_sell': True}

    def calc_margin_impact(self, position, margin_ratio=0.25):
        """
        计算保证金影响
        T+1限制了当日对冲能力
        """
        return {
            'locked_margin': position * margin_ratio,
            'opportunity_cost': position * margin_ratio * self.market_rate(),
            'recommendation': '避免当日大幅加仓'
        }
```

***

## 2. 涨跌停板制度量化

```python
class LimitUpDownSystem:
    """
    涨跌停板制度量化
    """

    LIMIT_RULES = {
        '主板（沪市60/深市000）': {
            '涨跌停幅度': 0.10,
            'ST股票幅度': 0.05,
            '首日上市幅度': 0.44
        },
        '创业板（300）': {
            '涨跌停幅度': 0.20,
            'ST股票幅度': 0.20,
            '首日上市幅度': 0.44
        },
        '科创板（688）': {
            '涨跌停幅度': 0.20,
            'ST股票幅度': 0.20,
            '首日上市幅度':无涨跌停
        }
    }

    def check_limit_up(self, stock_code, change_pct, preclose):
        """
        检查是否涨停
        """
        limit_rate = self.get_limit_rate(stock_code)
        limit_price = preclose * (1 + limit_rate)

        if change_pct >= limit_rate * 100:
            return {
                'is_limit_up': True,
                'limit_price': limit_price,
                'limit_rate': limit_rate
            }
        return {'is_limit_up': False}
```

***

## 3. 交易费用计算

```python
TRADING_FEES = {
    '佣金': {'rate': 0.0003, 'min': 5, '双向': True},
    '印花税': {'rate': 0.001, 'min': 0, '单向': 'sell'},
    '过户费': {'rate': 0.00001, 'min': 1, '双向': True, 'market': 'SH'},
    '规费': {'rate': 0.00002, 'min': 0, '双向': True}
}
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 整合附录BM内容 |
