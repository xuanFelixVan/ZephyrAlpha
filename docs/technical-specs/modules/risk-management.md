# 风险管理

> 量化风控架构
>
> **配套文档**：
> - 主文档：[SPEC.md](../SPEC.md)
> - Barra优化器：[architecture/barra-optimizer.md](./architecture/barra-optimizer.md)

***

## 1. 风控指标体系

| 风控类型 | 指标 | 阈值 | 处理方式 |
|----------|------|------|----------|
| 市场风险 | VaR (99%, 1日) | 组合2% | 降仓 |
| 市场风险 | 最大回撤 | 10% | 预警+减仓 |
| 流动性风险 | 持仓集中度 | 单票20% | 限制加仓 |
| 流动性风险 | 日内成交量占比 | 30% | 分批减仓 |
| 交易风险 | 单笔亏损 | 2% | 自动止损 |
| 交易风险 | 日内交易频率 | 100次 | 暂停交易 |
| 合规风险 | 持股限制 | 5%举牌线 | 预警 |

***

## 2. 风控Python实现

```python
class RiskManager:
    """风险管理系统"""

    def __init__(self):
        self.limits = {
            'max_var': 0.02,
            'max_drawdown': 0.10,
            'max_concentration': 0.20,
            'max_volume_ratio': 0.30,
            'max_single_loss': 0.02,
            'max_daily_trades': 100,
            'alert_line': 0.05
        }

    def calculate_var(self, returns: list, confidence: float = 0.99) -> float:
        """计算VaR"""
        if not returns:
            return 0.0

        sorted_returns = sorted(returns)
        index = int(len(returns) * (1 - confidence))

        return abs(sorted_returns[index]) if index < len(sorted_returns) else 0.0

    def calculate_drawdown(self, equity_curve: list) -> float:
        """计算最大回撤"""
        peak = equity_curve[0]
        max_dd = 0.0

        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd

        return max_dd

    def check_concentration(self, positions: dict) -> tuple:
        """检查持仓集中度"""
        for code, position in positions.items():
            ratio = position['volume'] * position['price'] / position['total_value']
            if ratio > self.limits['max_concentration']:
                return False, f"{code}集中度{ratio*100:.1f}%超限"

        return True, "集中度合规"

    def check_daily_trades(self, trade_count: int) -> tuple:
        """检查日内交易次数"""
        if trade_count > self.limits['max_daily_trades']:
            return False, f"交易次数{trade_count}超限"
        return True, "交易次数合规"

    def execute_risk_check(self, portfolio: dict, market_data: dict) -> dict:
        """执行风控检查"""
        result = {
            'approved': True,
            'warnings': [],
            'actions': []
        }

        returns = market_data.get('daily_returns', [])
        var = self.calculate_var(returns)
        if var > self.limits['max_var']:
            result['approved'] = False
            result['actions'].append('reduce_position')
            result['warnings'].append(f'VaR超限: {var*100:.2f}%')

        drawdown = self.calculate_drawdown(market_data.get('equity_curve', [1.0]))
        if drawdown > self.limits['max_drawdown']:
            result['approved'] = False
            result['actions'].append('stop_trading')
            result['warnings'].append(f'回撤超限: {drawdown*100:.2f}%')

        conc_ok, conc_msg = self.check_concentration(portfolio.get('positions', {}))
        if not conc_ok:
            result['warnings'].append(conc_msg)

        trades_ok, trades_msg = self.check_daily_trades(portfolio.get('daily_trade_count', 0))
        if not trades_ok:
            result['warnings'].append(trades_msg)
            result['approved'] = False

        return result
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-27 | 新增风险管理文档 |
