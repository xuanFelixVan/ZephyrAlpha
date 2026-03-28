# T.01.SE001.选股量化标准

> 选股量化标准体系
>
> **策略编号**：T.01.SE001
> **所属模块**：02_ALPHA_FACTORS
> **文档类型**：Alpha因子
> **优先级**：P1
>
> **配套文档**：
> - [T.01.VA001.估值分析.md](./03_价值投资/T.01.VA001.估值分析.md) - 估值分析
> - [T.00.MR003.市场结构博弈.md](../01_MARKET_REGIME/T.00.MR003.市场结构博弈.md) - 支撑阻力

---

## 1. 支撑位与压力位量化

```python
class SupportResistanceQuantifier:
    """
    支撑位与压力位量化

    核心理论：
    - 支撑位：价格下跌时的强支撑区域
    - 压力位：价格上涨时的强阻力区域
    - 支撑压力位可相互转化
    """

    def __init__(self):
        self.lookback = 60
        self.cluster_tolerance = 0.02

    def find_support_resistance(self, price_data: pd.DataFrame,
                              lookback: int = 60) -> dict:
        """
        寻找支撑位和压力位

        参数:
            price_data: 价格数据
            lookback: 回溯天数

        返回:
            levels: 支撑阻力位
        """
        highs = price_data['high'].rolling(5).max()
        lows = price_data['low'].rolling(5).min()

        pivot_high = self.find_pivots(highs, 'high')
        pivot_low = self.find_pivots(lows, 'low')

        resistance_levels = self.cluster_levels(pivot_high, tolerance=self.cluster_tolerance)
        support_levels = self.cluster_levels(pivot_low, tolerance=self.cluster_tolerance)

        current_price = price_data['close'].iloc[-1]

        return {
            'resistance': resistance_levels,
            'support': support_levels,
            'current_distance': self.calc_distance_from_levels(
                current_price,
                support_levels,
                resistance_levels
            )
        }

    def find_pivots(self, series: pd.Series, direction: str) -> list:
        """
        寻找极值点

        参数:
            series: 价格序列
            direction: 'high' 或 'low'

        返回:
            pivots: 极值点列表
        """
        pivots = []
        for i in range(2, len(series) - 2):
            if direction == 'high':
                if (series.iloc[i] > series.iloc[i-1] and
                    series.iloc[i] > series.iloc[i-2] and
                    series.iloc[i] > series.iloc[i+1] and
                    series.iloc[i] > series.iloc[i+2]):
                    pivots.append(series.iloc[i])
            else:
                if (series.iloc[i] < series.iloc[i-1] and
                    series.iloc[i] < series.iloc[i-2] and
                    series.iloc[i] < series.iloc[i+1] and
                    series.iloc[i] < series.iloc[i+2]):
                    pivots.append(series.iloc[i])
        return pivots

    def cluster_levels(self, pivots: list, tolerance: float = 0.02) -> list:
        """
        聚类分析找关键位

        参数:
            pivots: 极值点列表
            tolerance: 聚类容差

        返回:
            clustered_levels: 聚类后的关键位
        """
        if not pivots:
            return []

        sorted_pivots = sorted(pivots)
        clusters = []
        current_cluster = [sorted_pivots[0]]

        for pivot in sorted_pivots[1:]:
            if pivot <= current_cluster[-1] * (1 + tolerance):
                current_cluster.append(pivot)
            else:
                clusters.append(current_cluster)
                current_cluster = [pivot]

        clusters.append(current_cluster)

        return [sum(c) / len(c) for c in clusters]

    def calc_distance_from_levels(self, current_price: float,
                                 support: list,
                                 resistance: list) -> dict:
        """
        计算当前价格与支撑/压力位的距离
        """
        nearest_support = min([s for s in support if s < current_price],
                             default=current_price * 0.9)
        nearest_resistance = min([r for r in resistance if r > current_price],
                                default=current_price * 1.1)

        return {
            'distance_to_support': (current_price - nearest_support) / current_price,
            'distance_to_resistance': (nearest_resistance - current_price) / current_price,
            'trading_range': (nearest_resistance - nearest_support) / current_price,
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance
        }
```

---

## 2. 优质价值股筛选量化

```python
class ValueStockScreener:
    """
    优质价值股筛选量化

    筛选标准：
    - 行业龙头地位
    - 主营业务清晰
    - 现金流稳定
    - 周期弹性适中
    """

    SCREENING_CRITERIA = {
        'industry_leader': {
            'weight': 0.30,
            'market_share': 0.10,
            'description': '行业市占率>10%'
        },
        'core_business': {
            'weight': 0.20,
            'revenue_concentration': 0.70,
            'description': '主营收入占比>70%'
        },
        'cash_flow': {
            'weight': 0.30,
            'operating_cf_ratio': 0.80,
            'description': '经营现金流/净利润>80%'
        },
        'cyclical_beta': {
            'weight': 0.20,
            'beta_range': (0.8, 1.5),
            'description': 'Beta在0.8-1.5之间'
        }
    }

    def screen(self, stock_universe: list) -> list:
        """
        筛选优质价值股

        参数:
            stock_universe: 候选股票列表

        返回:
            qualified: 符合条件的股票
        """
        qualified = []

        for stock in stock_universe:
            scores = []

            if self.check_industry_leader(stock):
                scores.append(('industry_leader', 0.30))

            if self.check_core_business(stock):
                scores.append(('core_business', 0.20))

            if self.check_cash_flow(stock):
                scores.append(('cash_flow', 0.30))

            if self.check_cyclical_beta(stock):
                scores.append(('cyclical', 0.20))

            total_score = sum(s[1] for s in scores)

            if total_score >= 0.70:
                qualified.append({
                    'stock': stock,
                    'score': total_score,
                    'strengths': [s[0] for s in scores]
                })

        return sorted(qualified, key=lambda x: x['score'], reverse=True)

    def check_industry_leader(self, stock: dict) -> bool:
        """
        检查行业地位
        """
        return stock.get('market_share', 0) > 0.10

    def check_core_business(self, stock: dict) -> bool:
        """
        检查主营清晰度
        """
        return stock.get('revenue_concentration', 0) > 0.70

    def check_cash_flow(self, stock: dict) -> bool:
        """
        检查现金流
        """
        cf_ratio = stock.get('operating_cash_flow', 0) / max(stock.get('net_profit', 1), 1)
        return cf_ratio > 0.80

    def check_cyclical_beta(self, stock: dict) -> bool:
        """
        检查周期弹性
        """
        beta = stock.get('beta', 1.0)
        return 0.8 <= beta <= 1.5
```

---

## 3. 分红分析量化

```python
class DividendAnalyzer:
    """
    分红分析量化

    分红类型：
    - 分红+送股：最优
    - 分红：现金回报
    - 送股：扩张股本
    - 配股：需谨慎
    """

    def analyze_dividend(self, stock_data: dict) -> dict:
        """
        分析分红类型和影响

        参数:
            stock_data: 股票数据

        返回:
            analysis: 分红分析
        """
        dividend_type = self.classify_dividend(stock_data)

        return {
            'type': dividend_type,
            'ex_right_date': self.calc_ex_right_date(stock_data),
            'price_adjustment': self.calc_price_adjustment(stock_data),
            'action': self.get_action(dividend_type)
        }

    def classify_dividend(self, stock_data: dict) -> str:
        """
        分类分红类型
        """
        has_dividend = stock_data.get('dividend', 0) > 0
        has_bonus = stock_data.get('bonus_shares', 0) > 0
        has_rights = stock_data.get('rights_issue', 0) > 0

        if has_dividend and has_bonus:
            return '分红+送股'
        elif has_dividend:
            return '分红'
        elif has_bonus:
            return '送股'
        elif has_rights:
            return '配股'
        else:
            return '无分红'

    def calc_ex_right_date(self, stock_data: dict) -> str:
        """
        计算除权除息日
        """
        return stock_data.get('ex_right_date', '未知')

    def calc_price_adjustment(self, stock_data: dict) -> float:
        """
        计算除权价格调整
        """
        dividend = stock_data.get('dividend', 0)
        bonus = stock_data.get('bonus_shares', 0)
        price = stock_data.get('price', 0)

        if price == 0:
            return 0

        adjustment = dividend + bonus * price * 0.1

        return adjustment

    def get_action(self, dividend_type: str) -> str:
        """
        获取操作建议
        """
        actions = {
            '分红+送股': '优质信号，可持有',
            '分红': '现金回报，稳健',
            '送股': '扩张股本，关注',
            '配股': '需谨慎，摊薄收益',
            '无分红': '成长型，不关注'
        }
        return actions.get(dividend_type, '未知')
```

---

## 4. 动量反转选股

```python
class MomentumReversalSelector:
    """
    动量反转选股器

    核心理念：
    - 动量：强者恒强，趋势延续
    - 反转：超卖反弹，均值回归
    """

    def __init__(self):
        self.momentum_lookback = 60
        self.reversal_lookback = 20

    def select_momentum_stocks(self, stock_universe: list,
                              market_data: dict) -> list:
        """
        动量选股

        条件：
        - 近60日涨幅前30%
        - 相对行业超额收益>0
        - 成交量持续放大
        """
        candidates = []

        for stock in stock_universe:
            price_data = market_data[stock['code']]

            momentum = self.calc_momentum(price_data)
            excess_return = self.calc_excess_return(stock, price_data, market_data)
            volume_trend = self.calc_volume_trend(price_data)

            if momentum >= 0.15 and excess_return > 0 and volume_trend > 0:
                candidates.append({
                    'stock': stock,
                    'momentum': momentum,
                    'excess_return': excess_return,
                    'volume_trend': volume_trend,
                    'score': momentum + excess_return + volume_trend * 0.5
                })

        return sorted(candidates, key=lambda x: x['score'], reverse=True)[:50]

    def select_reversal_stocks(self, stock_universe: list,
                              market_data: dict) -> list:
        """
        反转选股

        条件：
        - 近20日跌幅前30%
        - RSI<40 超卖
        - 缩量到地量水平
        """
        candidates = []

        for stock in stock_universe:
            price_data = market_data[stock['code']]

            reversal = self.calc_reversal(price_data)
            rsi = self.calc_rsi(price_data)
            volume_shrink = self.calc_volume_shrink(price_data)

            if reversal <= -0.15 and rsi < 40 and volume_shrink < 0.5:
                candidates.append({
                    'stock': stock,
                    'reversal': reversal,
                    'rsi': rsi,
                    'score': abs(reversal) + (40 - rsi) / 40
                })

        return sorted(candidates, key=lambda x: x['score'], reverse=True)[:50]

    def calc_momentum(self, price_data: pd.DataFrame) -> float:
        """
        计算动量
        """
        current_price = price_data['close'].iloc[-1]
        past_price = price_data['close'].iloc[-self.momentum_lookback]

        return (current_price - past_price) / past_price

    def calc_excess_return(self, stock: dict,
                          price_data: pd.DataFrame,
                          market_data: dict) -> float:
        """
        计算超额收益
        """
        stock_return = self.calc_momentum(price_data)
        industry_return = market_data.get(stock['industry'], {}).get('return', 0)

        return stock_return - industry_return

    def calc_volume_trend(self, price_data: pd.DataFrame) -> float:
        """
        计算成交量趋势
        """
        recent_vol = price_data['volume'].iloc[-10:].mean()
        earlier_vol = price_data['volume'].iloc[-30:-10].mean()

        return (recent_vol - earlier_vol) / earlier_vol if earlier_vol > 0 else 0

    def calc_reversal(self, price_data: pd.DataFrame) -> float:
        """
        计算反转幅度
        """
        return -self.calc_momentum(price_data)

    def calc_rsi(self, price_data: pd.DataFrame, period: int = 14) -> float:
        """
        计算RSI
        """
        delta = price_data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi.iloc[-1]

    def calc_volume_shrink(self, price_data: pd.DataFrame) -> float:
        """
        计算缩量程度
        """
        recent_vol = price_data['volume'].iloc[-5:].mean()
        avg_vol = price_data['volume'].rolling(20).mean().iloc[-1]

        return recent_vol / avg_vol if avg_vol > 0 else 1
```

---

## 5. 综合选股评分模型

```python
class StockScoringModel:
    """
    综合选股评分模型

    多维度评分：
    - 价值维度 (30%)
    - 成长维度 (25%)
    - 质量维度 (25%)
    - 动量维度 (20%)
    """

    DIMENSION_WEIGHTS = {
        'value': 0.30,
        'growth': 0.25,
        'quality': 0.25,
        'momentum': 0.20
    }

    def calculate_composite_score(self, stock: dict,
                                 price_data: pd.DataFrame,
                                 market_data: dict) -> dict:
        """
        计算综合评分

        参数:
            stock: 股票数据
            price_data: 价格数据
            market_data: 市场数据

        返回:
            scores: 各维度评分和综合评分
        """
        value_score = self.calc_value_score(stock)
        growth_score = self.calc_growth_score(stock)
        quality_score = self.calc_quality_score(stock)
        momentum_score = self.calc_momentum_score(price_data)

        composite = (
            value_score * self.DIMENSION_WEIGHTS['value'] +
            growth_score * self.DIMENSION_WEIGHTS['growth'] +
            quality_score * self.DIMENSION_WEIGHTS['quality'] +
            momentum_score * self.DIMENSION_WEIGHTS['momentum']
        )

        return {
            'value_score': round(value_score, 2),
            'growth_score': round(growth_score, 2),
            'quality_score': round(quality_score, 2),
            'momentum_score': round(momentum_score, 2),
            'composite_score': round(composite, 2),
            'rating': self.get_rating(composite)
        }

    def calc_value_score(self, stock: dict) -> float:
        """
        计算价值评分
        """
        pe = stock.get('pe', 50)
        pb = stock.get('pb', 10)
        ps = stock.get('ps', 10)

        score = 0

        if 0 < pe < 20:
            score += 40
        elif pe < 30:
            score += 25
        elif pe < 50:
            score += 10

        if 0 < pb < 2:
            score += 30
        elif pb < 4:
            score += 20
        elif pb < 6:
            score += 10

        if 0 < ps < 3:
            score += 30
        elif ps < 5:
            score += 20

        return min(100, score)

    def calc_growth_score(self, stock: dict) -> float:
        """
        计算成长评分
        """
        revenue_growth = stock.get('revenue_growth', 0)
        profit_growth = stock.get('profit_growth', 0)

        score = 0

        if revenue_growth > 20:
            score += 50
        elif revenue_growth > 10:
            score += 30
        elif revenue_growth > 0:
            score += 10

        if profit_growth > 30:
            score += 50
        elif profit_growth > 15:
            score += 30
        elif profit_growth > 0:
            score += 10

        return min(100, score)

    def calc_quality_score(self, stock: dict) -> float:
        """
        计算质量评分
        """
        roe = stock.get('roe', 0)
        gross_margin = stock.get('gross_profit_margin', 0)
        debt_ratio = stock.get('debt_to_equity', 100)

        score = 0

        if roe > 20:
            score += 40
        elif roe > 10:
            score += 25
        elif roe > 5:
            score += 10

        if gross_margin > 40:
            score += 30
        elif gross_margin > 20:
            score += 20

        if debt_ratio < 50:
            score += 30
        elif debt_ratio < 80:
            score += 20

        return min(100, score)

    def calc_momentum_score(self, price_data: pd.DataFrame) -> float:
        """
        计算动量评分
        """
        momentum_60d = self.calc_momentum(price_data, 60)
        momentum_20d = self.calc_momentum(price_data, 20)

        score = 50

        if momentum_60d > 0.20:
            score += 30
        elif momentum_60d > 0.10:
            score += 20
        elif momentum_60d > 0:
            score += 10

        if momentum_20d > momentum_60d:
            score += 20

        return min(100, max(0, score))

    def calc_momentum(self, price_data: pd.DataFrame, period: int) -> float:
        """
        计算动量
        """
        current = price_data['close'].iloc[-1]
        past = price_data['close'].iloc[-period]

        return (current - past) / past

    def get_rating(self, score: float) -> str:
        """
        评分转评级
        """
        if score >= 80:
            return 'A (优秀)'
        elif score >= 60:
            return 'B (良好)'
        elif score >= 40:
            return 'C (一般)'
        else:
            return 'D (较差)'
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 整合附录AW：选股量化标准体系 |
