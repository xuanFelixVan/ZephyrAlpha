# 股票强度分析

> 个股强度分析量化体系
>
> **配套文档**：
> - 主文档：[SPEC.md](../SPEC.md)
> - 监控系统：[monitoring.md](./monitoring.md)

***

## 1. 强度分析核心框架

| 分析维度 | 指标 | 计算方法 | 权重 |
|----------|------|----------|------|
| 动量强度 | N日收益率 | (Close_N - Close_0) / Close_0 | 25% |
| 相对强度 | vs指数超额收益 | 个股收益 - 指数收益 | 25% |
| 资金强度 | 机构净流入占比 | 机构净流入 / 流通市值 | 20% |
| 形态强度 | 技术形态评分 | 综合K线形态打分 | 20% |
| 波动强度 | 收益稳定性 | 1 / 日收益标准差 | 10% |

***

## 2. 强度选股Python实现

```python
class StockStrengthAnalyzer:
    """股票强度分析"""

    def __init__(self, data_source):
        self.data = data_source

    def calculate_momentum_strength(self, stock_code: str, periods: list = [5, 20, 60]) -> dict:
        """计算动量强度"""
        result = {}
        for period in periods:
            returns = self.get_stock_return(stock_code, period)
            result[f'momentum_{period}d'] = returns
        return result

    def calculate_relative_strength(self, stock_code: str, index_code: str = 'sh000300') -> float:
        """计算相对强度（vs指数）"""
        stock_return = self.get_stock_return(stock_code, 20)
        index_return = self.get_index_return(index_code, 20)
        return stock_return - index_return

    def calculate_fund_strength(self, stock_code: str) -> float:
        """计算资金强度"""
        fund_flow = self.get_fund_flow(stock_code)
        market_cap = self.get_float_market_cap(stock_code)
        return fund_flow / market_cap

    def calculate_form_strength(self, stock_code: str) -> float:
        """计算形态强度"""
        pattern_score = self.identify_patterns(stock_code)
        return pattern_score

    def calculate_volatility_strength(self, stock_code: str, period: int = 20) -> float:
        """计算波动强度（收益稳定性）"""
        returns = self.get_daily_returns(stock_code, period)
        volatility = returns.std()
        return 1 / volatility if volatility > 0 else 0

    def get_comprehensive_strength(self, stock_code: str) -> dict:
        """
        计算综合强度得分
        """
        momentum = self.calculate_momentum_strength(stock_code)
        relative = self.calculate_relative_strength(stock_code)
        fund = self.calculate_fund_strength(stock_code)
        form = self.calculate_form_strength(stock_code)
        volatility = self.calculate_volatility_strength(stock_code)

        momentum_score = self._normalize(momentum['momentum_20d'])
        relative_score = self._normalize(relative)
        fund_score = self._normalize(fund)
        form_score = self._normalize(form)
        volatility_score = self._normalize(volatility)

        comprehensive = (
            momentum_score * 0.25 +
            relative_score * 0.25 +
            fund_score * 0.20 +
            form_score * 0.20 +
            volatility_score * 0.10
        )

        return {
            'comprehensive_score': comprehensive,
            'momentum_score': momentum_score,
            'relative_score': relative_score,
            'fund_score': fund_score,
            'form_score': form_score,
            'volatility_score': volatility_score
        }

    @staticmethod
    def _normalize(value: float, min_val: float = None, max_val: float = None) -> float:
        """归一化到0-1"""
        if max_val is None or min_val is None:
            return (value - min_val) / (max_val - min_val) if max_val != min_val else 0.5
        return value


class StrengthRanking:
    """强度排名"""

    def __init__(self, analyzer: StockStrengthAnalyzer):
        self.analyzer = analyzer

    def rank_stocks(self, stock_codes: list) -> pd.DataFrame:
        """
        对股票池进行强度排名
        """
        results = []

        for code in stock_codes:
            try:
                strength = self.analyzer.get_comprehensive_strength(code)
                results.append({
                    'code': code,
                    **strength
                })
            except Exception as e:
                print(f"Error processing {code}: {e}")
                continue

        df = pd.DataFrame(results)
        df = df.sort_values('comprehensive_score', ascending=False)
        df['rank'] = range(1, len(df) + 1)

        return df
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 整合附录N内容 |
