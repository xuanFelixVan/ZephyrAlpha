---
module_id: EXEC_SIMULATION_BP_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-02
owner: 首席文档架构�?
standard_type: 专业量化机构蓝图
applicable_scope: 全系统架构设�?
compliance_level: 初始标准
parent_document: ../README.md
implementation_status: 设计阶段
implementation_progress: 0%
---


# 模拟交易蓝图（简化版�?

> 清风量化系统 v5.0 的模拟交易方�?
> **索引**: `SIM_001`
> **说明**: 整合现有TradeExecutor模块，简化模拟交易设�?


## 1. 设计原则

| 原则 | 说明 |
|------|------|
| 复用现有模块 | 模拟交易复用TradeExecutor，仅改变执行�?|
| 真实市场模拟 | 模拟撮合尽可能接近实�?|
| 完整日志 | 所有交易记录完整保存，便于复盘 |


## 2. 模拟交易架构

### 2.1 架构�?

```
┌─────────────────────────────────────────────────────────────�?
�?                   模拟交易�?                                �?
├─────────────────────────────────────────────────────────────�?
�?                                                            �?
�? ┌───────────────────�?                                    �?
�? �?  SimulatedBroker �?�?模拟券商(模拟真实broker行为)       �?
�? └─────────┬─────────�?                                    �?
�?           �?                                                �?
�?           �?                                                �?
�? ┌───────────────────�?                                    �?
�? �?  OrderMatcher   �?�?模拟撮合引擎                        �?
�? �?  (T+0/T+1)      �?  支持市价/限价/止损�?              �?
�? └─────────┬─────────�?                                    �?
�?           �?                                                �?
�?           �?                                                �?
�? ┌───────────────────�?                                    �?
�? �?  SimulatedAccount�?�?模拟账户(资金/持仓/盈亏)           �?
�? └───────────────────�?                                    �?
�?                                                            �?
└─────────────────────────────────────────────────────────────�?
                            �?
                    TradeExecutor
                    (复用实盘代码)
```

### 2.2 与实盘代码对�?

| 组件 | 实盘 | 模拟交易 |
|------|------|----------|
| TradeExecutor | �?相同 | �?相同 |
| OrderMatcher | 真实市场 | 模拟撮合 |
| Broker | 券商API | SimulatedBroker |
| Account | 真实账户 | SimulatedAccount |
| 数据�?| 实时行情 | 历史/实时数据 |


## 3. 核心模块设计

### 3.1 模拟撮合引擎

```python
class OrderMatcher:
    """订单撮合引擎

    索引: SIM_001-M01
    上游: TradeExecutor
    下游: SimulatedAccount
    """

    def __init__(self, slippage_model: SlippageModel = None):
        self.pending_orders = []
        self.slippage_model = slippage_model or FixedSlippage()

    def submit_order(self, order: Order, market_data: MarketData) -> OrderResult:
        """提交订单

        参数:
            order: 订单
            market_data: 市场数据

        返回:
            订单执行结果
        """
        if order.order_type == 'market':
            return self._execute_market_order(order, market_data)
        elif order.order_type == 'limit':
            return self._execute_limit_order(order, market_data)
        elif order.order_type == 'stop':
            return self._execute_stop_order(order, market_data)

    def _execute_market_order(self, order: Order, market_data: MarketData) -> OrderResult:
        """执行市价�?

        模拟逻辑:
        - 买入: �?ask 价格成交
        - 卖出: �?bid 价格成交
        - 加上滑点
        """
        symbol = order.symbol
        price = market_data.get_price(symbol)

        if order.action == 'buy':
            exec_price = price.ask * (1 + self.slippage_model.get_slippage('buy'))
        else:
            exec_price = price.bid * (1 - self.slippage_model.get_slippage('sell'))

        return OrderResult(
            order_id=order.order_id,
            status='filled',
            filled_price=exec_price,
            filled_quantity=order.quantity,
            commission=self._calculate_commission(exec_price, order.quantity)
        )

    def _execute_limit_order(self, order: Order, market_data: MarketData) -> OrderResult:
        """执行限价�?""
        symbol = order.symbol
        price = market_data.get_price(symbol)

        if order.action == 'buy' and price.bid <= order.price:
            return self._execute_market_order(order, market_data)
        elif order.action == 'sell' and price.ask >= order.price:
            return self._execute_market_order(order, market_data)
        else:
            return OrderResult(
                order_id=order.order_id,
                status='pending'
            )
```

### 3.2 模拟账户

```python
class SimulatedAccount:
    """模拟账户

    索引: SIM_001-M02
    上游: OrderMatcher
    下游: PerformanceAnalyzer
    """

    def __init__(self, initial_cash: float = 1000000):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions = {}  # {symbol: Position}
        self.trades = []
        self.equity_curve = []

    def update_position(self, trade: Trade):
        """更新持仓

        参数:
            trade: 交易记录
        """
        symbol = trade.symbol
        quantity = trade.quantity if trade.action == 'buy' else -trade.quantity

        if symbol in self.positions:
            self.positions[symbol].quantity += quantity
            self.positions[symbol].avg_price = trade.price
        else:
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                avg_price=trade.price
            )

        self.cash -= trade.price * trade.quantity + trade.commission
        self.trades.append(trade)

    def get_equity(self, market_data: MarketData) -> float:
        """计算当前权益

        参数:
            market_data: 市场数据

        返回:
            当前总权�?
        """
        position_value = sum(
            pos.quantity * market_data.get_price(pos.symbol).last
            for pos in self.positions.values()
        )
        return self.cash + position_value

    def get_position(self, symbol: str) -> Position:
        """获取持仓"""
        return self.positions.get(symbol)

    def can_place_order(self, order: Order, market_data: MarketData) -> tuple:
        """检查是否可以下�?

        返回:
            (can_place, reason)
        """
        estimated_cost = order.price * order.quantity * 1.001  # 预估+手续�?

        if order.action == 'buy' and self.cash < estimated_cost:
            return False, f"资金不足: 需要{estimated_cost:.2f}, 可用{self.cash:.2f}"

        if order.action == 'sell':
            pos = self.get_position(order.symbol)
            if not pos or pos.quantity < order.quantity:
                return False, f"持仓不足: 需要{order.quantity}, 持有{pos.quantity if pos else 0}"

        return True, ""
```

### 3.3 滑点模型

```python
class SlippageModel:
    """滑点模型

    索引: SIM_001-M03
    """

    def get_slippage(self, action: str, symbol: str = None) -> float:
        """获取滑点

        参数:
            action: 'buy' or 'sell'
            symbol: 股票代码(可�?

        返回:
            滑点比例 (�?0.001 = 0.1%)
        """
        raise NotImplementedError


class FixedSlippage(SlippageModel):
    """固定滑点"""

    def __init__(self, slippage: float = 0.0005):
        self.slippage = slippage

    def get_slippage(self, action: str, symbol: str = None) -> float:
        return self.slippage


class VolumeBasedSlippage(SlippageModel):
    """基于成交量的滑点

    成交量越大，滑点越大
    """

    def __init__(self, base_slippage: float = 0.0001):
        self.base_slippage = base_slippage

    def get_slippage(self, action: str, symbol: str = None, volume: float = None) -> float:
        if volume is None:
            return self.base_slippage

        if volume > 10000000:  # 千万级成�?
            return self.base_slippage * 5
        elif volume > 1000000:  # 百万级成�?
            return self.base_slippage * 2
        else:
            return self.base_slippage
```


## 4. 模拟交易流程

### 4.1 完整流程

```python
class SimulationEngine:
    """模拟交易引擎

    索引: SIM_001-M04
    """

    def __init__(self, config: SimulationConfig):
        self.broker = SimulatedBroker()
        self.matcher = OrderMatcher(config.slippage_model)
        self.account = SimulatedAccount(config.initial_cash)
        self.market_data = config.market_data_source
        self.risk_monitor = config.risk_monitor

    def run(self, strategy: Strategy, start_date: str, end_date: str):
        """运行模拟交易

        参数:
            strategy: 策略
            start_date: 开始日�?
            end_date: 结束日期
        """
        dates = self._get_trading_dates(start_date, end_date)

        for date in dates:
            self._run_daily(date, strategy)

    def _run_daily(self, date: str, strategy: Strategy):
        """每日运行

        1. 获取市场数据
        2. 生成信号
        3. 风控检�?
        4. 执行订单
        5. 更新持仓
        6. 记录日志
        """
        market_data = self.market_data.get_data(date)

        signals = strategy.generate_signals(market_data)

        for signal in signals:
            order = self._signal_to_order(signal)

            can_place, reason = self.account.can_place_order(order, market_data)
            if not can_place:
                logger.warning(f"订单被拒�? {reason}")
                continue

            risk_check = self.risk_monitor.check(order)
            if not risk_check.passed:
                logger.warning(f"风控拒绝: {risk_check.reasons}")
                continue

            result = self.broker.execute(order, market_data)

            if result.status == 'filled':
                trade = Trade(
                    symbol=order.symbol,
                    action=order.action,
                    quantity=result.filled_quantity,
                    price=result.filled_price,
                    commission=result.commission,
                    timestamp=date
                )
                self.account.update_position(trade)

        self._record_daily_equity(date)

    def _signal_to_order(self, signal: Signal) -> Order:
        """信号转订�?""
        return Order(
            symbol=signal.symbol,
            action='buy' if signal.direction > 0 else 'sell',
            quantity=self._calculate_quantity(signal),
            order_type='market',
            price=0
        )

    def _calculate_quantity(self, signal: Signal) -> int:
        """计算下单数量

        使用固定比例或凯利公�?
        """
        return int(self.account.cash * 0.1 / signal.price)  # 10%仓位
```


## 5. 交易成本模型

### 5.1 成本配置

```yaml
# config/simulation/cost.yaml

cost_model:
  commission:
    type: "percentage"  # percentage or fixed
    rate: 0.0003         # 万三 (双向收取)
    min_commission: 5    # 最低佣�?�?

  stamp_tax:
    enabled: true
    rate: 0.001         # 千一 (仅卖出收�?
    effective_date: "2023-01-01"

  slippage:
    type: "fixed"
    rate: 0.0002        # 万二

  slippage_volume_based:
    enabled: true
    thresholds:
      - volume: 10000000
        multiplier: 5
      - volume: 1000000
        multiplier: 2
      - volume: 0
        multiplier: 1
```


## 6. 模拟交易报告

### 6.1 报告模板

```markdown
# 模拟交易报告

## 基本信息
- 策略: {strategy_name}
- 模拟�? {start_date} ~ {end_date}
- 初始资金: {initial_cash:,.2f}
- 结束权益: {final_equity:,.2f}

## 收益指标
| 指标 | �?|
|------|-----|
| 总收益率 | {total_return:.2%} |
| 年化收益�?| {annual_return:.2%} |
| 夏普比率 | {sharpe:.2f} |
| 最大回�?| {max_drawdown:.2%} |
| 卡尔玛比�?| {calmar:.2f} |

## 交易统计
| 指标 | �?|
|------|-----|
| 总交易次�?| {total_trades} |
| 盈利交易 | {winning_trades} |
| 亏损交易 | {losing_trades} |
| 胜率 | {win_rate:.2%} |
| 平均盈利 | {avg_profit:.2f} |
| 平均亏损 | {avg_loss:.2f} |
| 盈亏�?| {profit_loss_ratio:.2f} |

## 成本统计
| 指标 | �?|
|------|-----|
| 佣金总额 | {total_commission:.2f} |
| 印花税总额 | {total_stamp_tax:.2f} |
| 总交易成�?| {total_cost:.2f} |
| 成本占比 | {cost_ratio:.2%} |

## 持仓分析
{position_analysis}
```


## 7. 与现有模块集�?

### 7.1 集成�?

| 现有模块 | 集成方式 |
|----------|----------|
| TradeExecutor | 替换Broker为SimulatedBroker |
| RiskManager | 直接复用 |
| DataHub | 模拟时使用历史数据源 |
| PerformanceAnalyzer | 直接复用 |

### 7.2 配置切换

```python
# 实盘模式
production_config = {
    'broker': 'vnpy',  # 实盘券商
    'risk_monitor': RiskManager()
}

# 模拟模式
simulation_config = {
    'broker': 'simulated',  # 模拟券商
    'risk_monitor': RiskManager()  # 复用风控
}

# 一键切�?
engine = TradingEngine(
    config=simulation_config if is_simulation else production_config
)
```


## 8. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本 - 简化版设计 |
| v1.1 | 2026-04-01 | 添加多引擎架构扩展说�?|


## 9. 多引擎架构扩�?

本蓝图（简化版）为基础设计，系统已扩展�?*多引擎架�?*，支持三种主流开源交易引擎：

### 9.1 多引擎架构概�?

| 引擎 | 角色定位 | 与本蓝图的关�?|
|------|----------|----------------|
| **vn.py** | 生产级主引擎 | 本蓝图的**生产级实�?*，提供完整A股模拟交�?|
| **RQAlpha** | 专业回测引擎 | **增强回测能力**，提供专业级策略验证 |
| **Backtrader** | 功能补充引擎 | **扩展功能支持**，多资产、高级订单类�?|

### 9.2 架构演进

1. **基础设计（本蓝图�?*�?
   - 简化版模拟交易架构
   - 核心模块：SimulatedBroker、OrderMatcher、SimulatedAccount
   - 与现有TradeExecutor集成

2. **多引擎扩�?*�?
   - 统一接口层：抽象引擎接口，支持多引擎
   - 适配器模式：每个引擎实现统一接口
   - 动态切换：运行时选择最佳引�?
   - 故障转移：主引擎失败时自动切�?

### 9.3 设计原则继承

多引擎架构继承了本蓝图的核心设计原则�?
- �?**复用现有模块**：继续复用TradeExecutor、RiskManager等模�?
- �?**真实市场模拟**：各引擎都提供真实市场模拟能�?
- �?**完整日志**：统一日志记录，便于复盘分�?

### 9.4 完整多引擎设�?

详细的多引擎架构设计、接口定义、配置管理、实施路线图详见�?
**[MULTI_ENGINE_BLUEPRINT.md](MULTI_ENGINE_BLUEPRINT.md)**

该文档包含：
- 三引擎详细设计（vn.py、RQAlpha、Backtrader�?
- 统一接口层设计与实现
- 引擎工厂与多引擎协同�?
- 动态切换策略与故障转移
- 性能对比测试方案
- 三阶段实施路线图


**维护�?*: 清风量化系统
**索引**: `SIM_001` �?`SIM_002` (多引擎扩�?
**关联文档**: [MULTI_ENGINE_BLUEPRINT.md](MULTI_ENGINE_BLUEPRINT.md)
