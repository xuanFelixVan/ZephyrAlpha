# 回测引擎

> 量化回测框架设计
>
> **配套文档**：
> - 主文档：[SPEC.md](../SPEC.md)
> - 全成本模型：[modules/cost-model.md](./modules/cost-model.md)

***

## 1. 回测框架设计

| 模块 | 功能 | 技术要点 |
|------|------|----------|
| 数据回放 | 历史数据模拟 | Tick级重放 |
| 撮合引擎 | 模拟订单成交 | 实时价/限价/止损 |
| 滑点模型 | 成交价格偏移 | 固定/百分比滑点 |
| 佣金计算 | 交易成本扣除 | 印花税+佣金+过户费 |
| 绩效归因 | 收益/风险指标 | 年化/夏普/最大回撤 |

***

## 2. 回测引擎Python实现

```python
class BacktestEngine:
    """回测引擎"""

    def __init__(self):
        self.initial_capital = 1000000
        self.slippage = 0.0005
        self.commission = 0.0003
        self.stamp_tax = 0.001

    def calculate_slippage(self, price: float, side: str) -> float:
        """计算滑点"""
        slippage_price = price * (1 + self.slippage) if side == 'BUY' else price * (1 - self.slippage)
        return slippage_price

    def calculate_commission(self, price: float, volume: int, side: str) -> float:
        """计算佣金"""
        turnover = price * volume
        commission = turnover * self.commission

        if side == 'SELL':
            commission += turnover * self.stamp_tax

        return commission

    def match_order(self, order: dict, market_data: dict) -> dict:
        """订单撮合"""
        order_price = order['price']
        current_price = market_data['last_price']

        if order['type'] == 'MARKET':
            exec_price = self.calculate_slippage(current_price, order['side'])
        else:
            if order['side'] == 'BUY' and order_price >= current_price:
                exec_price = self.calculate_slippage(current_price, order['side'])
            elif order['side'] == 'SELL' and order_price <= current_price:
                exec_price = self.calculate_slippage(current_price, order['side'])
            else:
                return None

        commission = self.calculate_commission(exec_price, order['volume'], order['side'])

        return {
            'exec_price': exec_price,
            'exec_volume': order['volume'],
            'commission': commission,
            'slippage': abs(exec_price - current_price) * order['volume']
        }

    def calculate_performance(self, equity_curve: list, benchmark: list = None) -> dict:
        """计算绩效指标"""
        if not equity_curve:
            return {}

        returns = [0] + [(equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1] for i in range(1, len(equity_curve))]

        total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0]
        annual_return = total_return * 252 / len(equity_curve) if len(equity_curve) > 0 else 0

        avg_return = sum(returns) / len(returns)
        std_return = (sum([(r - avg_return) ** 2 for r in returns]) / len(returns)) ** 0.5
        sharpe = (avg_return / std_return * (252 ** 0.5)) if std_return > 0 else 0

        peak = equity_curve[0]
        max_drawdown = 0
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_drawdown:
                max_drawdown = dd

        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'total_trades': len([r for r in returns if r != 0])
        }

    def run_backtest(self, strategy, data: list) -> dict:
        """运行回测"""
        equity = self.initial_capital
        equity_curve = [equity]
        positions = {}
        trades = []

        for tick in data:
            signals = strategy.generate_signal(tick)

            for signal in signals:
                order = {
                    'code': signal['code'],
                    'side': signal['side'],
                    'price': signal.get('price', tick['last_price']),
                    'volume': signal.get('volume', 100),
                    'type': signal.get('type', 'LIMIT')
                }

                match_result = self.match_order(order, tick)
                if match_result:
                    commission = match_result['commission']
                    equity -= commission

                    if order['side'] == 'BUY':
                        positions[order['code']] = positions.get(order['code'], 0) + order['volume']
                    else:
                        positions[order['code']] = positions.get(order['code'], 0) - order['volume']

                    trades.append(match_result)

            position_value = sum(
                positions.get(code, 0) * tick['last_price'] for code in positions
            )
            equity = equity + position_value - equity_curve[-1] + position_value
            equity_curve.append(equity)

        performance = self.calculate_performance(equity_curve)

        return {
            'equity_curve': equity_curve,
            'trades': trades,
            'performance': performance
        }
```

***

## 3. 回测指标汇总

| 指标 | 计算方法 | 优秀标准 |
|------|----------|----------|
| 年化收益率 | 总收益×252/交易日 | >15% |
| 夏普比率 | (年化-无风险)/波动率 | >1.5 |
| 最大回撤 | 历史最高-最低 | <15% |
| 胜率 | 盈利次数/总交易 | >50% |
| 盈亏比 | 平均盈利/平均亏损 | >1.5 |

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-27 | 新增回测引擎文档 |
