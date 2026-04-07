---
module_id: 03_TRADING_TACTICS_04_YOUZI_STRATEGIES_RETAIL_STRATEGIES_H
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理团队
responsibility:
  - retail-strategies-h.md文档
---

﻿---
module_id: TACTICS_YOUZI_OTHER_H_001
version: 1.6.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 交易策略设计与实施管理与优化维护
standard_type: 专业量化机构文档
applicable_scope: 全系?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?---


# retail-strategies-h.md
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


# 游资策略补充 (S059-S067)

> 遗漏内容整合补充
>
> **版本**：v1.6
> **日期**?026-03-28
> **策略?*：清风量化交易系?.0
>
> **配套文档**?
> -  - 估值分?

---

## 1. PE/PB/PS估值体?(S059)

> 来源：附录P
>
> 价值投资估值三剑客

### 1.1 估值指标计?

```python
class ValuationCalculator:
    """
    估值计算器
    PE/PB/PS三位一?
    """

    def calc_pe(self, price: float, eps: float) -> float:
        """市盈?""
        return price / eps if eps > 0 else None

    def calc_pb(self, price: float, book_per_share: float) -> float:
        """市净?""
        return price / book_per_share if book_per_share > 0 else None

    def calc_ps(self, price: float, revenue_per_share: float) -> float:
        """市销?""
        return price / revenue_per_share if revenue_per_share > 0 else None

    def comprehensive_valuation(self, stock_data: dict) -> dict:
        """
        综合估?

        返回:
            valuation: 估值结?
        """
        price = stock_data['close']

        pe = self.calc_pe(price, stock_data.get('eps', 0))
        pb = self.calc_pb(price, stock_data.get('book_per_share', 0))
        ps = self.calc_ps(price, stock_data.get('revenue_per_share', 0))

        pe_hist = stock_data.get('pe_history', [])
        pb_hist = stock_data.get('pb_history', [])

        pe_percentile = self.calc_percentile(pe, pe_hist)
        pb_percentile = self.calc_percentile(pb, pb_hist)

        return {
            'pe': round(pe, 2) if pe else None,
            'pb': round(pb, 2) if pb else None,
            'ps': round(ps, 2) if ps else None,
            'pe_percentile': pe_percentile,
            'pb_percentile': pb_percentile,
            'recommendation': self.get_valuation_recommendation(pe_percentile, pb_percentile)
        }

    def calc_percentile(self, value: float, history: list) -> float:
        """计算历史分位"""
        if not history or value is None:
            return None
        sorted_hist = sorted(history)
        return sum(1 for x in sorted_hist if x < value) / len(sorted_hist) * 100

    def get_valuation_recommendation(self, pe_pct: float, pb_pct: float) -> str:
        """估值建?""
        if pe_pct and pe_pct < 20 and pb_pct and pb_pct < 20:
            return '低估，建议买?
        elif pe_pct and pe_pct > 80:
            return '高估，建议卖?
        return '估值合?
```

### 1.2 估值选股策略

```python
class ValuationStockSelector:
    """
    估值选股?
    """

    def select_by_valuation(self, stock_universe: list,
                          valuation_data: dict) -> list:
        """
        按估值筛?

        条件?
        - PE < 行业均?
        - PB < 3
        - PE历史分位 < 30%
        """
        selected = []

        for code in stock_universe:
            val = valuation_data.get(code)

            if not val:
                continue

            if val['pe_percentile'] and val['pe_percentile'] > 30:
                continue

            if val['pb'] and val['pb'] > 3:
                continue

            selected.append({
                'code': code,
                'pe': val['pe'],
                'pb': val['pb'],
                'pe_percentile': val['pe_percentile'],
                'score': self.calc_value_score(val)
            })

        return sorted(selected, key=lambda x: x['score'], reverse=True)

    def calc_value_score(self, val: dict) -> float:
        """计算价值得?""
        score = 0

        if val.get('pe_percentile'):
            score += (100 - val['pe_percentile']) * 0.5

        if val.get('pb') and val['pb'] < 2:
            score += 30
        elif val.get('pb') and val['pb'] < 3:
            score += 15

        return score
```

---

## 2. 区间三强选股 (S060)

> 来源：附录AB
>
> 动量选股策略

### 2.1 选股逻辑

```python
class IntervalStrongSelector:
    """
    区间三强选股?

    选择条件?
    1. 区间涨幅?0%
    2. 相对行业超额收益?0%
    3. 区间换手率适中
    """

    def __init__(self):
        self.lookback_periods = [20, 60, 120]

    def select_interval_strong(self, stock_universe: list,
                             market_data: dict,
                             lookback: int = 60) -> list:
        """
        区间三强选股

        参数:
            stock_universe: 股票?
            market_data: 市场数据
            lookback: 回溯?

        返回:
            selected: 选中股票
        """
        candidates = []

        for code in stock_universe:
            price_data = market_data[code]

            interval_return = self.calc_interval_return(price_data, lookback)

            industry_return = market_data.get('industry_return', {}).get(code, 0)
            excess_return = interval_return - industry_return

            turnover_rate = self.calc_avg_turnover(price_data, lookback)

            if self.check_criteria(interval_return, excess_return, turnover_rate):
                candidates.append({
                    'code': code,
                    'interval_return': interval_return,
                    'excess_return': excess_return,
                    'turnover_rate': turnover_rate,
                    'strength_score': interval_return + excess_return * 2
                })

        return sorted(candidates, key=lambda x: x['strength_score'], reverse=True)[:50]

    def calc_interval_return(self, price_data: dict, lookback: int) -> float:
        """计算区间收益"""
        current_price = price_data['close'].iloc[-1]
        past_price = price_data['close'].iloc[-lookback]

        return (current_price - past_price) / past_price

    def calc_avg_turnover(self, price_data: dict, lookback: int) -> float:
        """计算平均换手?""
        return price_data['turnover_rate'].iloc[-lookback:].mean()

    def check_criteria(self, interval_ret: float,
                      excess_ret: float,
                      turnover: float) -> bool:
        """检查是否满足条?""
        if interval_ret < 0:
            return False

        if turnover < 5 or turnover > 200:
            return False

        return True
```

---

## 3. 指数情绪背离 (S061)

> 来源：附录AP
>
> 市场情绪与指数背离分?

### 3.1 背离识别

```python
class SentimentDivergenceAnalyzer:
    """
    情绪背离分析?

    背离类型?
    - 顶背离：指数新高但情绪不跟随
    - 底背离：指数新低但情绪不跟随
    """

    def detect_divergence(self, index_data: dict,
                        sentiment_data: dict) -> list:
        """
        检测背?

        参数:
            index_data: 指数数据
            sentiment_data: 情绪数据

        返回:
            divergences: 背离信号
        """
        divergences = []

        price_trend = self.calc_price_trend(index_data['close'])
        sentiment_trend = self.calc_sentiment_trend(sentiment_data['index'])

        if self.is_top_divergence(price_trend, sentiment_trend):
            divergences.append({
                'type': '顶背?,
                'signal': '看跌',
                'strength': '?
            })

        if self.is_bottom_divergence(price_trend, sentiment_trend):
            divergences.append({
                'type': '底背?,
                'signal': '看涨',
                'strength': '?
            })

        return divergences

    def is_top_divergence(self, price_trend: dict,
                        sentiment_trend: dict) -> bool:
        """顶背?""
        return (price_trend['direction'] == 'up' and
                price_trend['strength'] > sentiment_trend['strength'])

    def is_bottom_divergence(self, price_trend: dict,
                           sentiment_trend: dict) -> bool:
        """底背?""
        return (price_trend['direction'] == 'down' and
                sentiment_trend['direction'] == 'up')
```

---

## 4. 仓位管理与止损止?(S062)

> 来源：附录AX
>
> 完整仓位管理体系

### 4.1 仓位管理

```python
class PositionManager:
    """
    仓位管理?
    """

    def __init__(self, max_position: float = 0.30):
        self.max_position = max_position
        self.current_positions = {}

    def calc_target_position(self, signal_strength: float,
                           volatility: float,
                           account_capital: float) -> float:
        """
        计算目标仓位

        公式: position = signal_strength * (1 / volatility) * base_position
        """
        base_position = 0.10

        target = signal_strength * (1 / volatility) * base_position

        target = min(target, self.max_position)

        return target

    def adjust_for_drawdown(self, current_drawdown: float) -> float:
        """
        根据回撤调整仓位

        回撤越大，仓位越?
        """
        if current_drawdown < 0.05:
            return 1.0
        elif current_drawdown < 0.10:
            return 0.8
        elif current_drawdown < 0.15:
            return 0.5
        else:
            return 0.3
```

### 4.2 止损止盈

```python
class StopLossTakeProfit:
    """
    止损止盈策略
    """

    def __init__(self):
        self.stop_loss_pct = 0.07
        self.take_profit_pct = 0.15
        self.trailing_stop_pct = 0.05

    def calc_stop_loss(self, buy_price: float,
                     market_volatility: float) -> float:
        """
        计算止损?

        动态止损基于波动率
        """
        volatility_stop = buy_price * market_volatility * 2

        fixed_stop = buy_price * self.stop_loss_pct

        return buy_price - max(volatility_stop, fixed_stop)

    def calc_take_profit(self, buy_price: float,
                       market_state: str) -> float:
        """
        计算止盈?
        """
        if market_state == '强势':
            return buy_price * (1 + self.take_profit_pct * 1.5)
        else:
            return buy_price * (1 + self.take_profit_pct)

    def calc_trailing_stop(self, highest_price: float) -> float:
        """
        计算追踪止损
        """
        return highest_price * (1 - self.trailing_stop_pct)
```

---

## 5. 交易复盘量化 (S063)

> 来源：附录O
>
> 每日交易复盘体系

### 5.1 复盘框架

```python
class TradingReview:
    """
    交易复盘?
    """

    def daily_review(self, trades: list, market_data: dict) -> dict:
        """
        每日复盘

        返回:
            review: 复盘报告
        """
        return {
            'trade_summary': self.summarize_trades(trades),
            'performance': self.calc_performance(trades),
            'mistakes': self.identify_mistakes(trades, market_data),
            'improvements': self.suggest_improvements(trades),
            'market_analysis': self.analyze_market_environment(market_data)
        }

    def summarize_trades(self, trades: list) -> dict:
        """交易汇?""
        total_trades = len(trades)
        profitable = len([t for t in trades if t['pnl'] > 0])

        return {
            'total_trades': total_trades,
            'profitable_trades': profitable,
            'win_rate': profitable / total_trades if total_trades > 0 else 0,
            'total_pnl': sum(t['pnl'] for t in trades)
        }

    def identify_mistakes(self, trades: list, market_data: dict) -> list:
        """识别错误"""
        mistakes = []

        for trade in trades:
            if trade['pnl'] < 0:
                reason = self.analyze_loss_reason(trade, market_data)
                if reason:
                    mistakes.append(reason)

        return mistakes
```

---

## 6. 一夜持股法 (S064)

> 超短线持仓策?

### 6.1 选股条件

```python
class OvernightHoldingSelector:
    """
    一夜持股法选股?

    核心：收盘前买入，次日开盘卖?
    选股条件?
    1. 当日涨幅3-8%
    2. 成交量放?
    3. 突破关键阻力?
    4. 板块情绪高涨
    """

    def select_stocks(self, market_data: dict) -> list:
        """
        选股
        """
        candidates = []

        for code, data in market_data.items():
            if self.meet_conditions(data):
                candidates.append({
                    'code': code,
                    'change_pct': data['change_pct'],
                    'volume_ratio': data['volume_ratio'],
                    'breakout_strength': data.get('breakout_strength', 0),
                    'score': self.calc_overnight_score(data)
                })

        return sorted(candidates, key=lambda x: x['score'], reverse=True)[:20]

    def meet_conditions(self, data: dict) -> bool:
        """检查条?""
        if not (3 <= data['change_pct'] <= 8):
            return False

        if data['volume_ratio'] < 1.5:
            return False

        if not data.get('broke_resistance', False):
            return False

        return True

    def calc_overnight_score(self, data: dict) -> float:
        """计算一夜持股评?""
        return data['change_pct'] * 0.3 + data['volume_ratio'] * 0.4 + data['breakout_strength'] * 0.3
```

---

## 7. 次新股低?(S065)

> 来源：附录CA
>
> 次新股价值发?

### 7.1 次新股筛?

```python
class SmallCapValueSelector:
    """
    次新股低估筛选器

    上市时间?-3?
    市值：< 100?
    估值：PE < 行业均?0%
    """

    def select_small_cap_value(self, stock_universe: list) -> list:
        """
        筛选小市值价值股
        """
        selected = []

        for stock in stock_universe:
            if not self.is_small_cap(stock):
                continue

            if not self.is_value_stock(stock):
                continue

            if self.is_growing(stock):
                selected.append(stock)

        return sorted(selected, key=lambda x: x['value_score'], reverse=True)

    def is_small_cap(self, stock: dict) -> bool:
        """小市?""
        return stock.get('market_cap', float('inf')) < 100

    def is_value_stock(self, stock: dict) -> bool:
        """价值股"""
        return stock.get('pe', float('inf')) < stock.get('industry_pe', 20) * 0.5

    def is_growing(self, stock: dict) -> bool:
        """成长?""
        return stock.get('profit_growth', 0) > 10
```

---

## 8. 交易心理量化 (S066)

> 来源：附录BQ
>
> 交易心理偏差量化

### 8.1 心理偏差识别

```python
class TradingPsychologyAnalyzer:
    """
    交易心理分析?

    常见心理偏差?
    - 损失厌恶：亏损时不止?
    - 过度自信：频繁交?
    - 锚定效应：紧盯买入价
    - 从众心理：追涨杀?
    """

    def analyze_psychology(self, trades: list) -> dict:
        """
        分析交易心理
        """
        loss_aversion = self.check_loss_aversion(trades)
        overconfidence = self.check_overconfidence(trades)
        anchoring = self.check_anchoring(trades)

        return {
            'loss_aversion_score': loss_aversion,
            'overconfidence_score': overconfidence,
            'anchoring_score': anchoring,
            'main_bias': self.identify_main_bias(loss_aversion, overconfidence, anchoring)
        }

    def check_loss_aversion(self, trades: list) -> float:
        """检查损失厌?""
        losing_trades = [t for t in trades if t['pnl'] < 0]
        held_to_loss = [t for t in losing_trades if t.get('holding_days', 0) > 5]

        return len(held_to_loss) / len(losing_trades) if losing_trades else 0

    def check_overconfidence(self, trades: list) -> float:
        """检查过度自?""
        return len(trades) / 30 if len(trades) > 30 else 0
```

---

## 9. 主升龙头真经 (S067)

> 来源：附录AV
>
> 均线操作体系

### 9.1 均线战法

```python
class MovingAverageStrategy:
    """
    均线策略

    核心理念?
    - 5日线操作?
    - 10日线判断趋势
    - 20日线决策买卖
    """

    def calc_ma_signals(self, price_data: pd.DataFrame) -> dict:
        """
        计算均线信号
        """
        ma5 = price_data['close'].rolling(5).mean()
        ma10 = price_data['close'].rolling(10).mean()
        ma20 = price_data['close'].rolling(20).mean()

        current = price_data['close'].iloc[-1]

        if ma5.iloc[-1] > ma10.iloc[-1] > ma20.iloc[-1]:
            trend = '多头'
        elif ma5.iloc[-1] < ma10.iloc[-1] < ma20.iloc[-1]:
            trend = '空头'
        else:
            trend = '震荡'

        return {
            'trend': trend,
            'ma5': ma5.iloc[-1],
            'ma10': ma10.iloc[-1],
            'ma20': ma20.iloc[-1],
            'signal': self.get_trade_signal(current, ma5.iloc[-1], ma10.iloc[-1])
        }

    def get_trade_signal(self, price: float, ma5: float, ma10: float) -> str:
        """交易信号"""
        if price > ma5 > ma10:
            return '买入'
        elif price < ma5 < ma10:
            return '卖出'
        return '观望'
```

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.6 | 2026-03-28 | 新增遗漏策略内容：估值体系、区间三强、情绪背离、仓位管理、复盘量化等 |
