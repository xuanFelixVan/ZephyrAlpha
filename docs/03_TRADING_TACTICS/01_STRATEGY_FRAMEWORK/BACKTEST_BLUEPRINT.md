---
module_id: TACTICS_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
standard_type: 专业量化机构蓝图
applicable_scope: 全系统架构设�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 设计阶段
---


# Backtrader回测蓝图

> 清风量化系统 v5.0 - Backtrader回测系统
> **索引**: `STRAT.001`
> **开发时�?*: 35h
> **核心定位**: 实现"策略 �?Backtrader回测 �?绩效分析 �?Optuna优化"的完整回测闭�?


## 1. 设计原则

| 原则 | 说明 |
|------|------|
| **Backtrader主力** | 使用Backtrader作为回测引擎 |
| **事件驱动** | 完整的事件驱动回�?|
| **成本真实** | 手续费、滑点、冲击成本全部模�?|
| **Optuna优化** | 使用Optuna进行参数优化 |


## 2. Backtrader集成架构

### 2.1 系统架构

```
┌─────────────────────────────────────────────────────────────�?
�?                   回测系统架构                                �?
├─────────────────────────────────────────────────────────────�?
�?                                                            �?
�? ┌─────────────�?                                          �?
�? �?  策略      �?◀── �?AI设计                             �?
�? └──────┬──────�?                                          �?
�?        �?                                                  �?
�?        �?                                                  �?
�? ┌─────────────────────────────────────────────────────────┐│
�? �?             Backtrader Engine                         ││
�? �? - Cerebro  - Data Feeds  - Observers  - Analyzers    ││
�? └─────────────────────────────────────────────────────────┘│
�?        �?                                                  �?
�?        �?                                                  �?
�? ┌─────────────�?                                          �?
�? �? 绩效分析   �?◀── empyrical/PyFolio                    �?
�? └─────────────�?                                          �?
�?        �?                                                  �?
�?        �?                                                  �?
�? ┌─────────────�?                                          �?
�? �? Optuna优化 �?◀── 参数自动搜索                          �?
�? └─────────────�?                                          �?
└─────────────────────────────────────────────────────────────�?
```

### 2.2 回测流程

```
1. 策略设计 �?2. 数据准备 �?3. Backtrader配置 �?4. 回测执行
                                                        �?
8. 报告生成 �?7. 参数优化 �?6. 结果分析 �?5. 结果输出
```


## 3. 核心实现

### 3.1 数据馈�?

```python
import backtrader as bt
import pandas as pd

class PandasDataFeed(bt.feeds.PandasData):
    """Pandas数据馈�?

    索引: STRAT.001-M01
    """

    params = (
        ('datetime', 'date'),
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
        ('openinterest', -1),
    )

class DataFeedFactory:
    """数据馈送工�?

    索引: STRAT.001-M02
    上游: DataHub
    下游: Backtrader Engine
    """

    def create_ohlcv_feed(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        freq: str = 'daily'
    ) -> PandasDataFeed:
        """创建OHLCV数据馈�?

        参数:
            symbol: 股票代码
            start_date: 开始日�?
            end_date: 结束日期
            freq: 频率 (daily/weekly/monthly)

        返回:
            Backtrader数据馈�?
        """
        # 从DataHub获取数据
        data = DataHub.get_ohlcv(symbol, start_date, end_date)

        # 转换日期格式
        data['date'] = pd.to_datetime(data['date'])
        data = data.set_index('date')

        # Backtrader需要按时间排序
        data = data.sort_index()

        # 创建数据馈�?
        feed = PandasDataFeed(dataname=data)

        return feed
```

### 3.2 策略基类

```python
class BaseStrategy(bt.Strategy):
    """策略基类

    索引: STRAT.001-M03
    """

    params = (
        ('printlog', False),
    )

    def __init__(self):
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.trades = []

    def log(self, txt, dt=None):
        """日志"""
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        """订单通知"""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        """交易通知"""
        if trade.isclosed:
            self.log(f'TRADE PROFIT, GROSS {trade.pnl:.2f}, NET {trade.pnlcomm:.2f}')
            self.trades.append({
                'entry_date': bt.num2date(trade.dtopen).date(),
                'exit_date': bt.num2date(trade.dtclose).date(),
                'pnl': trade.pnlcomm
            })
```

### 3.3 策略模板

```python
class MomentumStrategy(BaseStrategy):
    """动量策略模板

    索引: STRAT.001-M04
    """

    params = (
        ('period', 20),
        ('threshold', 0.02),
        ('printlog', False),
    )

    def __init__(self):
        super().__init__()
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0].close,
            period=self.params.period
        )

    def next(self):
        """策略逻辑"""
        if self.order:
            return

        if not self.position:
            # 无持仓，检查买入信�?
            if self.datas[0].close > self.sma * (1 + self.params.threshold):
                self.log(f'BUY CREATE, Price: {self.datas[0].close[0]:.2f}')
                self.order = self.buy()
        else:
            # 有持仓，检查卖出信�?
            if self.datas[0].close < self.sma:
                self.log(f'SELL CREATE, Price: {self.datas[0].close[0]:.2f}')
                self.order = self.sell()


class MeanReversionStrategy(BaseStrategy):
    """均值回归策略模�?

    索引: STRAT.001-M05
    """

    params = (
        ('period', 20),
        ('std_dev', 2.0),
        ('printlog', False),
    )

    def __init__(self):
        super().__init__()
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0].close,
            period=self.params.period
        )
        self.std = bt.indicators.StandardDeviation(
            self.datas[0].close,
            period=self.params.period
        )

    def next(self):
        """策略逻辑"""
        if self.order:
            return

        z_score = (self.datas[0].close[0] - self.sma[0]) / self.std[0]

        if not self.position:
            if z_score < -self.params.std_dev:
                self.order = self.buy()
        else:
            if z_score > self.params.std_dev / 2:
                self.order = self.sell()
```


## 4. 回测引擎

### 4.1 回测执行�?

```python
class BacktestEngine:
    """回测引擎

    索引: STRAT.001-M06
    """

    def __init__(self, initial_cash: float = 1000000):
        self.initial_cash = initial_cash
        self.cerebro = None

    def run(
        self,
        strategy_class: type,
        symbols: List[str],
        start_date: str,
        end_date: str,
        params: dict = None,
        commission: float = 0.0003
    ) -> BacktestResult:
        """运行回测

        参数:
            strategy_class: 策略�?
            symbols: 股票列表
            start_date: 开始日�?
            end_date: 结束日期
            params: 策略参数
            commission: 手续费率

        返回:
            BacktestResult
        """
        # 1. 创建Cerebro
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(self.initial_cash)
        cerebro.broker.setcommission(commission=commission)

        # 2. 添加策略
        cerebro.addstrategy(strategy_class, **(params or {}))

        # 3. 添加数据
        for symbol in symbols:
            datafeed = DataFeedFactory().create_ohlcv_feed(
                symbol, start_date, end_date
            )
            cerebro.adddata(datafeed, name=symbol)

        # 4. 添加分析�?
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

        # 5. 运行
        results = cerebro.run()

        # 6. 获取结果
        strategy = results[0]
        return self._parse_results(strategy, cerebro.broker.getvalue())

    def _parse_results(
        self,
        strategy: BaseStrategy,
        final_value: float
    ) -> BacktestResult:
        """解析结果"""
        sharpe = strategy.analyzers.sharpe.get_analysis().get('shararatio', 0)
        drawdown = strategy.analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', 0)
        returns = strategy.analyzers.returns.get_analysis()

        return BacktestResult(
            initial_value=self.initial_cash,
            final_value=final_value,
            total_return=(final_value - self.initial_cash) / self.initial_cash,
            sharpe_ratio=sharpe or 0,
            max_drawdown=drawdown / 100 if drawdown else 0,
            trades=strategy.trades,
            ohlcv_data=strategy.datas[0].lines.getlinealiases()
        )
```

### 4.2 Optuna集成

```python
class OptunaOptimizer:
    """Optuna参数优化�?

    索引: STRAT.001-M07
    """

    def __init__(self):
        self.study = None

    def optimize(
        self,
        strategy_class: type,
        symbols: List[str],
        start_date: str,
        end_date: str,
        param_space: dict,
        objective: str = 'sharpe',
        n_trials: int = 100
    ) -> OptimizationResult:
        """优化参数

        参数:
            strategy_class: 策略�?
            symbols: 股票列表
            param_space: 参数空间
            objective: 优化目标
            n_trials: 试验次数

        返回:
            OptimizationResult
        """
        def objective_fn(trial):
            params = {
                name: trial.suggest_int(name, *space)
                for name, space in param_space.items()
            }

            engine = BacktestEngine()
            result = engine.run(
                strategy_class, symbols, start_date, end_date, params
            )

            if objective == 'sharpe':
                return result.sharpe_ratio
            elif objective == 'return':
                return result.total_return
            elif objective == 'inverse_drawdown':
                return result.total_return / (result.max_drawdown + 0.001)

        # 创建研究
        study = optuna.create_study(
            direction='maximize',
            study_name=f'optimize_{strategy_class.__name__}'
        )
        study.optimize(objective_fn, n_trials=n_trials)

        return OptimizationResult(
            best_params=study.best_params,
            best_value=study.best_value,
            trials=study.trials
        )
```


## 5. 绩效分析

### 5.1 绩效分析�?

```python
class PerformanceAnalyzer:
    """绩效分析�?

    索引: STRAT.001-M08
    上游: BacktestEngine
    下游: wandb
    """

    def analyze(self, result: BacktestResult) -> PerformanceReport:
        """分析绩效

        参数:
            result: 回测结果

        返回:
            绩效报告
        """
        # 使用empyrical计算风险指标
        returns = pd.Series([t['pnl'] for t in result.trades])

        return PerformanceReport(
            total_return=result.total_return,
            sharpe_ratio=empyrical.sharpe_ratio(returns) if len(returns) > 0 else 0,
            max_drawdown=empyrical.max_drawdown(returns) if len(returns) > 0 else 0,
            calmar_ratio=empyrical.calmar_ratio(returns) if len(returns) > 0 else 0,
            win_rate=len(returns[returns > 0]) / len(returns) if len(returns) > 0 else 0,
            avg_win=returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0,
            avg_loss=returns[returns < 0].mean() if len(returns[returns < 0]) > 0 else 0,
            profit_loss_ratio=abs(returns[returns > 0].mean() / returns[returns < 0].mean()) if len(returns[returns < 0]) > 0 else 0
        )

    def generate_report(self, result: BacktestResult) -> str:
        """生成报告"""
        report = self.analyze(result)
        return f"""
# 回测报告

## 基本信息
- 初始资金: {result.initial_value:,.2f}
- 最终资�? {result.final_value:,.2f}
- 总收益率: {report.total_return:.2%}

## 风险指标
| 指标 | �?|
|------|-----|
| 夏普比率 | {report.sharpe_ratio:.2f} |
| 最大回�?| {report.max_drawdown:.2%} |
| 卡玛比率 | {report.calmar_ratio:.2f} |

## 交易统计
| 指标 | �?|
|------|-----|
| 交易次数 | {len(result.trades)} |
| 胜率 | {report.win_rate:.2%} |
| 平均盈利 | {report.avg_win:,.2f} |
| 平均亏损 | {report.avg_loss:,.2f} |
| 盈亏�?| {report.profit_loss_ratio:.2f} |
"""
```


## 6. API接口

### 6.1 回测API

```python
# API: /api/v1/backtest

class BacktestAPI:
    """回测API

    索引: API_BACKTEST_001
    """

    @router.post("/backtest")
    def run_backtest(config: BacktestConfig) -> BacktestResult:
        """运行回测

        参数:
            config: {
                strategy: 'momentum' | 'mean_reversion' | 'custom',
                symbols: ['000001', '000002'],
                start_date: '2020-01-01',
                end_date: '2024-01-01',
                params: {'period': 20, 'threshold': 0.02}
            }
        """

    @router.post("/backtest/optimize")
    def optimize_backtest(config: OptimizeConfig) -> OptimizationResult:
        """优化回测参数"""

    @router.get("/backtest/{task_id}")
    def get_backtest_result(task_id: str) -> BacktestResult:
        """获取回测结果"""
```


## 7. 开发任务分�?

### 7.1 任务分解 (35h)

| 任务 | 时间 | 说明 |
|------|------|------|
| Backtrader环境 | 3h | 安装+配置 |
| 数据馈送封�?| 4h | PandasDataFeed |
| 策略基类 | 6h | BaseStrategy |
| 策略模板 | 8h | Momentum/MeanReversion |
| 回测引擎 | 6h | BacktestEngine |
| Optuna集成 | 4h | 参数优化 |
| 绩效分析 | 4h | empyrical/PyFolio |


## 8. 相关文档

| 文档 | 说明 |
|------|------|
| [overview.md](./overview.md) | 策略体系概述 |
| [lifecycle.md](./lifecycle.md) | 策略生命周期管理 |
| [STRATEGY_ENGINE_BLUEPRINT.md](./STRATEGY_ENGINE_BLUEPRINT.md) | 策略引擎开发蓝�?|
| [API_Contract.md](../API_Contract.md) | 系统API契约 |


**文档版本**: v1.0  
**最后更�?*: 2026-04-01  
**维护�?*: 策略研发中心
