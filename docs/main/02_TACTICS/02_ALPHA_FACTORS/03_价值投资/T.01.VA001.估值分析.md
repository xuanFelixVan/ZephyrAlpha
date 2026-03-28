# T.01.VA001.估值分析

> PE/PB/PS估值体系与价值选股
>
> **策略编号**：T.01.VA001
> **所属模块**：02_ALPHA_FACTORS/03_价值投资
> **文档类型**：Alpha因子
> **优先级**：P2
>
> **配套文档**：
> - [retail-strategies-h.md](../../trading-tactics/strategy-pool/retail-strategies-h.md) - S059估值体系
> - [T.03.RF002.申万行业因子.md](../../factor-library/03_RISK_FACTORS/2_行业因子.md) - 行业分类

---

## 1. 估值指标体系

```python
class ValuationMetrics:
    """
    估值指标体系

    三剑客：
    - PE (市盈率)：盈利与价格的关系
    - PB (市净率)：净资产与价格的关系
    - PS (市销率)：收入与价格的关系
    """

    def __init__(self):
        self.thresholds = {
            'pe_low': 0,
            'pe_high': 50,
            'pb_low': 0,
            'pb_high': 5,
            'ps_low': 0,
            'ps_high': 10
        }

    def calc_pe(self, price: float, eps: float) -> float:
        """
        市盈率 (P/E Ratio)

        公式: PE = 股价 / 每股收益
        意义：盈利收益率的倒数，反映收回成本的时间
        """
        if eps <= 0:
            return None
        return price / eps

    def calc_pb(self, price: float, book_per_share: float) -> float:
        """
        市净率 (P/B Ratio)

        公式: PB = 股价 / 每股净资产
        意义：相对于净资产的价格溢价
        """
        if book_per_share <= 0:
            return None
        return price / book_per_share

    def calc_ps(self, price: float, revenue_per_share: float) -> float:
        """
        市销率 (P/S Ratio)

        公式: PS = 股价 / 每股营业收入
        意义：相对于销售收入的价格溢价
        """
        if revenue_per_share <= 0:
            return None
        return price / revenue_per_share

    def calc_peg(self, pe: float, growth_rate: float) -> float:
        """
        PEG比率

        公式: PEG = PE / (增长率 * 100)
        意义：PE与增长率的比值，<1可能被低估
        """
        if pe is None or growth_rate <= 0:
            return None
        return pe / (growth_rate * 100)
```

---

## 2. 历史分位计算

```python
class ValuationPercentile:
    """
    估值历史分位计算
    """

    def __init__(self):
        self.history_length = 250

    def calc_percentile(self, current_value: float,
                       history: list) -> float:
        """
        计算历史分位

        公式: percentile = (小于当前值的数量 / 总数量) * 100

        参数:
            current_value: 当前估值
            history: 历史估值序列

        返回:
            percentile: 历史分位 (0-100)
        """
        if not history or current_value is None:
            return None

        sorted_history = sorted(history)
        count_below = sum(1 for x in sorted_history if x < current_value)

        percentile = (count_below / len(sorted_history)) * 100

        return percentile

    def calc_historical_avg(self, history: list) -> float:
        """计算历史均值"""
        if not history:
            return None
        return sum(history) / len(history)

    def calc_historical_std(self, history: list) -> float:
        """计算历史标准差"""
        import numpy as np
        if not history:
            return None
        return np.std(history)

    def is_undervalued(self, current_pe: float, history: list,
                      threshold: float = 30) -> bool:
        """
        判断是否低估

        参数:
            current_pe: 当前PE
            history: 历史PE序列
            threshold: 分位阈值

        返回:
            is_undervalued: 是否低估
        """
        percentile = self.calc_percentile(current_pe, history)
        return percentile is not None and percentile < threshold

    def is_overvalued(self, current_pe: float, history: list,
                     threshold: float = 70) -> bool:
        """
        判断是否高估
        """
        percentile = self.calc_percentile(current_pe, history)
        return percentile is not None and percentile > threshold
```

---

## 3. 行业相对估值

```python
class IndustryRelativeValuation:
    """
    行业相对估值分析
    """

    def __init__(self):
        self.industry_pe_baseline = {}

    def calc_industry_avg_pe(self, stocks: list) -> dict:
        """
        计算行业平均PE

        参数:
            stocks: [{'industry': str, 'pe': float}, ...]

        返回:
            industry_avg_pe: 行业平均PE字典
        """
        industry_data = {}

        for stock in stocks:
            industry = stock['industry']
            pe = stock.get('pe')

            if pe is None or pe <= 0:
                continue

            if industry not in industry_data:
                industry_data[industry] = []

            industry_data[industry].append(pe)

        return {
            industry: sum(pes) / len(pes)
            for industry, pes in industry_data.items()
        }

    def calc_relative_pe(self, stock_pe: float, industry_avg_pe: float) -> float:
        """
        计算相对PE

        公式: relative_pe = stock_pe / industry_avg_pe
        < 0.8 被低估，> 1.2 被高估
        """
        if stock_pe is None or industry_avg_pe is None or industry_avg_pe == 0:
            return None
        return stock_pe / industry_avg_pe

    def select_by_relative_pe(self, stocks: list,
                           max_relative_pe: float = 0.8) -> list:
        """
        按相对PE筛选

        参数:
            stocks: 股票列表
            max_relative_pe: 最大相对PE

        返回:
            undervalued_stocks: 被低估的股票
        """
        industry_avg = self.calc_industry_avg_pe(stocks)

        selected = []

        for stock in stocks:
            industry = stock['industry']
            stock_pe = stock.get('pe')

            if industry not in industry_avg:
                continue

            relative_pe = self.calc_relative_pe(stock_pe, industry_avg[industry])

            if relative_pe is not None and relative_pe < max_relative_pe:
                selected.append({
                    **stock,
                    'relative_pe': relative_pe,
                    'industry_avg_pe': industry_avg[industry]
                })

        return sorted(selected, key=lambda x: x['relative_pe'])
```

---

## 4. 价值选股策略

```python
class ValueStockSelector:
    """
    价值选股器
    """

    def __init__(self):
        self.percentile_calculator = ValuationPercentile()
        self.industry_valuation = IndustryRelativeValuation()

    def select_value_stocks(self, stocks: list,
                         criteria: dict = None) -> list:
        """
        价值选股

        默认筛选条件：
        - PE历史分位 < 30%
        - PB历史分位 < 30%
        - 相对PE < 0.8

        参数:
            stocks: 股票列表
            criteria: 筛选条件

        返回:
            selected: 选中股票
        """
        if criteria is None:
            criteria = {
                'max_pe_percentile': 30,
                'max_pb_percentile': 30,
                'max_relative_pe': 0.8,
                'min_pe': 0,
                'max_pe': 50,
                'min_pb': 0,
                'max_pb': 5
            }

        selected = []

        for stock in stocks:
            if not self.meets_criteria(stock, criteria):
                continue

            score = self.calc_value_score(stock, criteria)
            selected.append({
                **stock,
                'value_score': score
            })

        return sorted(selected, key=lambda x: x['value_score'], reverse=True)

    def meets_criteria(self, stock: dict, criteria: dict) -> bool:
        """
        检查是否满足条件
        """
        pe = stock.get('pe')
        pb = stock.get('pb')
        pe_history = stock.get('pe_history', [])
        pb_history = stock.get('pb_history', [])

        if pe is not None:
            if pe < criteria['min_pe'] or pe > criteria['max_pe']:
                return False

            pe_pct = self.percentile_calculator.calc_percentile(pe, pe_history)
            if pe_pct and pe_pct > criteria['max_pe_percentile']:
                return False

        if pb is not None:
            if pb < criteria['min_pb'] or pb > criteria['max_pb']:
                return False

            pb_pct = self.percentile_calculator.calc_percentile(pb, pb_history)
            if pb_pct and pb_pct > criteria['max_pb_percentile']:
                return False

        return True

    def calc_value_score(self, stock: dict, criteria: dict) -> float:
        """
        计算价值得分

        分位越低得分越高
        """
        score = 0

        pe = stock.get('pe')
        pe_history = stock.get('pe_history', [])
        if pe and pe_history:
            pe_pct = self.percentile_calculator.calc_percentile(pe, pe_history)
            if pe_pct:
                score += (100 - pe_pct) * 0.5

        pb = stock.get('pb')
        pb_history = stock.get('pb_history', [])
        if pb and pb_history:
            pb_pct = self.percentile_calculator.calc_percentile(pb, pb_history)
            if pb_pct:
                score += (100 - pb_pct) * 0.3

        if stock.get('roe'):
            score += stock['roe'] * 0.2

        return score
```

---

## 5. 估值因子计算

```python
class ValuationFactor:
    """
    估值因子

    因子定义：
    - E/P：盈利收益率 = EPS / Price
    - B/P：净资产收益率 = 1 / PB
    - S/P：销售收益率 = 1 / PS
    """

    def calc_ep_factor(self, market_data: pd.DataFrame) -> pd.Series:
        """
        E/P因子 (盈利收益率)

        高E/P意味着相对低估
        """
        eps = market_data['eps']
        price = market_data['close']

        ep = eps / price

        return ep.replace([np.inf, -np.inf], np.nan)

    def calc_bp_factor(self, market_data: pd.DataFrame) -> pd.Series:
        """
        B/P因子 (净资产收益率)

        高B/P意味着相对低估
        """
        book_per_share = market_data['book_per_share']
        price = market_data['close']

        bp = book_per_share / price

        return bp.replace([np.inf, -np.inf], np.nan)

    def calc_sp_factor(self, market_data: pd.DataFrame) -> pd.Series:
        """
        S/P因子 (销售收益率)

        高S/P意味着相对低估
        """
        revenue_per_share = market_data['revenue_per_share']
        price = market_data['close']

        sp = revenue_per_share / price

        return sp.replace([np.inf, -np.inf], np.nan)

    def calc_composite_value_factor(self, market_data: pd.DataFrame) -> pd.Series:
        """
        综合价值因子

        公式: Value = (E/P + B/P + S/P) / 3
        """
        ep = self.calc_ep_factor(market_data).fillna(0)
        bp = self.calc_bp_factor(market_data).fillna(0)
        sp = self.calc_sp_factor(market_data).fillna(0)

        composite = (ep + bp + sp) / 3

        return composite.replace([np.inf, -np.inf], np.nan)
```

---

## 6. 估值与市场周期

```python
class ValuationMarketCycle:
    """
    估值与市场周期关系
    """

    def __init__(self):
        self.cycle_thresholds = {
            '熊市底部_pe': 12,
            '熊市底部_pb': 1.2,
            '牛市顶部_pe': 25,
            '牛市顶部_pb': 3.0
        }

    def get_market_cycle_by_pe(self, market_pe: float) -> str:
        """
        根据PE判断市场周期
        """
        if market_pe <= self.cycle_thresholds['熊市底部_pe']:
            return '熊市底部区域'
        elif market_pe <= 18:
            return '偏低估区域'
        elif market_pe <= 22:
            return '合理估值区域'
        elif market_pe <= self.cycle_thresholds['牛市顶部_pe']:
            return '偏高估区域'
        else:
            return '牛市顶部区域'

    def get_market_cycle_by_pb(self, market_pb: float) -> str:
        """
        根据PB判断市场周期
        """
        if market_pb <= self.cycle_thresholds['熊市底部_pb']:
            return '熊市底部区域'
        elif market_pb <= 2.0:
            return '偏低估区域'
        elif market_pb <= 2.5:
            return '合理估值区域'
        elif market_pb <= self.cycle_thresholds['牛市顶部_pb']:
            return '偏高估区域'
        else:
            return '牛市顶部区域'

    def calc_expected_return(self, current_pe: float,
                          historical_pe: list,
                          growth_rate: float = 0.07) -> dict:
        """
        计算预期收益率

        基于PE回归历史均值的假设
        """
        avg_pe = sum(historical_pe) / len(historical_pe) if historical_pe else current_pe

        pe_change = (avg_pe - current_pe) / current_pe

        expected_earning = growth_rate

        total_expected = pe_change + expected_earning

        return {
            'current_pe': current_pe,
            'historical_avg_pe': avg_pe,
            'pe_contribution': round(pe_change * 100, 2),
            'earning_contribution': round(expected_earning * 100, 2),
            'total_expected_return': round(total_expected * 100, 2),
            'signal': '高估' if total_expected < 0 else '低估'
        }
```

---

## 7. 使用示例

```python
def example_value_investment():
    """
    价值投资示例
    """
    selector = ValueStockSelector()
    factor = ValuationFactor()

    stocks = [
        {
            'code': '000001',
            'pe': 8.5,
            'pb': 0.9,
            'roe': 0.12,
            'pe_history': [10, 12, 15, 14, 13, 11, 9, 8],
            'pb_history': [1.2, 1.3, 1.5, 1.4, 1.2, 1.1, 1.0, 0.9]
        },
        {
            'code': '600519',
            'pe': 35,
            'pb': 12,
            'roe': 0.30,
            'pe_history': [30, 32, 35, 38, 40, 42, 38, 35],
            'pb_history': [10, 11, 12, 13, 14, 13, 12, 12]
        }
    ]

    selected = selector.select_value_stocks(stocks)

    for stock in selected:
        print(f"\n股票: {stock['code']}")
        print(f"PE: {stock['pe']}, PB: {stock['pb']}")
        print(f"价值得分: {stock['value_score']:.2f}")

    pct_calc = ValuationPercentile()
    for stock in stocks:
        pe_pct = pct_calc.calc_percentile(stock['pe'], stock['pe_history'])
        pb_pct = pct_calc.calc_percentile(stock['pb'], stock['pb_history'])
        print(f"\n{stock['code']}:")
        print(f"PE分位: {pe_pct:.1f}%, PB分位: {pb_pct:.1f}%")
```

---

## 8. 估值指标速查表

| 指标 | 计算公式 | 优质区间 | 劣质区间 | 适用行业 |
|------|----------|----------|----------|----------|
| PE | 股价/EPS | < 15 | > 30 | 成熟行业 |
| PB | 股价/每股净资产 | < 2 | > 5 | 金融、周期 |
| PS | 股价/每股营收 | < 3 | > 10 | 零售、软件 |
| PEG | PE/增长率 | < 1 | > 2 | 成长股 |
| EV/EBITDA | 企业价值/息税折旧前利润 | < 10 | > 20 | 工业、企业 |

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 整合PE/PB/PS估值体系 |
