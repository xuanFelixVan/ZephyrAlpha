---
module_id: ORDEREXECUTIONBLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 执行团队
responsibility:
  - 蓝图设计、架构规划
  - 交易执行
  - 数据源
layer: Layer 5 (执行层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准---


﻿---
module_id: EXEC_ORDER_EXEC_BP_001
version: 1.0.1
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


# 订单生成+执行蓝图
> **核心职责**: Order Execution蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：Order Execution蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容


> 清风量化系统 v5.0 - 订单生成与执行系�?
> **索引**: `EXEC.001`
> **开发时�?*: 40h
> **核心定位**: 实现"信号 �?订单 �?撮合 �?成交"的完整交易执行闭�?


## 1. 设计原则

| 原则 | 说明 |
|------|------|
| **vn.py集成** | 使用vn.py作为执行�?|
| **模拟/实盘切换** | 一键切换模拟和实盘 |
| **TWAP/VWAP为主** | 智能订单算法以TWAP/VWAP为主 |
| **完整日志** | 所有交易记录完整保�?|


## 2. 交易执行架构

### 2.1 系统架构

```
┌─────────────────────────────────────────────────────────────�?
�?                   交易执行架构                                �?
├─────────────────────────────────────────────────────────────�?
�?                                                            �?
�? ┌─────────────�?                                          �?
�? �?  信号      �?◀── StrategyEngine                        �?
�? └──────┬──────�?                                          �?
�?        �?                                                  �?
�?        �?                                                  �?
�? ┌─────────────────────────────────────────────────────────┐│
�? �?             订单生成�?                                 ││
�? �? - 订单类型选择  - 数量计算  - 价格确定                  ││
�? └─────────────────────────────────────────────────────────┘│
�?        �?                                                  �?
�?        �?                                                  �?
�? ┌─────────────────────────────────────────────────────────┐│
�? �?             风控检�?                                   ││
�? �? - 仓位检�? - 资金检�? - 价格检�?                   ││
�? └─────────────────────────────────────────────────────────┘│
�?        �?                                                  �?
�?        �?                                                  �?
�? ┌─────────────────────────────────────────────────────────┐│
�? �?             订单执行                                    ││
�? �? - Broker接口  - 撮合引擎  - 成交回报                  ││
�? └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────�?
```


## 3. 核心实现

### 3.1 订单生成�?

```python
class OrderGenerator:
    """订单生成�?

    索引: EXEC.001-M01
    上游: StrategyEngine
    下游: RiskChecker
    """

    def __init__(self):
        self.order_type = 'market'  # 默认市价�?

    def generate_order(
        self,
        signal: Signal,
        account: Account,
        market_data: MarketData
    ) -> Order:
        """生成订单

        参数:
            signal: 交易信号
            account: 账户信息
            market_data: 市场数据

        返回:
            Order
        """
        symbol = signal.symbol
        action = 'buy' if signal.direction > 0 else 'sell'
        quantity = self._calculate_quantity(signal, account, market_data)
        price = self._determine_price(symbol, market_data)

        order = Order(
            symbol=symbol,
            action=action,
            quantity=quantity,
            price=price,
            order_type=self.order_type,
            created_at=datetime.now()
        )

        return order

    def _calculate_quantity(
        self,
        signal: Signal,
        account: Account,
        market_data: MarketData
    ) -> int:
        """计算下单数量

        参数:
            signal: 交易信号
            account: 账户信息
            market_data: 市场数据

        返回:
            下单数量(�?
        """
        symbol = signal.symbol
        price = market_data.get_price(symbol)

        if signal.position_ratio:
            # 按仓位比例下�?
            target_value = account.total_value * signal.position_ratio
            quantity = int(target_value / price / 100) * 100  # 整手
        elif signal.position_value:
            # 按金额下�?
            quantity = int(signal.position_value / price / 100) * 100
        else:
            # 默认10%仓位
            target_value = account.total_value * 0.1
            quantity = int(target_value / price / 100) * 100

        return max(quantity, 100)  # 最�?00�?

    def _determine_price(
        self,
        symbol: str,
        market_data: MarketData
    ) -> float:
        """确定订单价格"""
        if self.order_type == 'market':
            return 0  # 市价单不需要指定价�?
        elif self.order_type == 'limit':
            price = market_data.get_price(symbol)
            return price.last
```

### 3.2 智能订单算法

```python
class SmartOrderAlgorithm:
    """智能订单算法

    索引: EXEC.001-M02
    """

    def create_twap_order(
        self,
        symbol: str,
        action: str,
        total_quantity: int,
        duration_minutes: int = 60
    ) -> list:
        """创建TWAP订单

        参数:
            symbol: 股票代码
            action: buy/sell
            total_quantity: 总数�?
            duration_minutes: 持续时间(分钟)

        返回:
            子订单列�?
        """
        interval = duration_minutes / 10  # 分成10�?
        child_quantity = total_quantity // 10

        orders = []
        for i in range(10):
            order = Order(
                symbol=symbol,
                action=action,
                quantity=child_quantity,
                order_type='limit',
                price=0,  # 市价
                parent_id=None,
                scheduled_time=datetime.now() + timedelta(minutes=i * interval)
            )
            orders.append(order)

        return orders

    def create_vwap_order(
        self,
        symbol: str,
        action: str,
        total_quantity: int,
        volume_share: float = 0.02
    ) -> list:
        """创建VWAP订单

        参数:
            symbol: 股票代码
            action: buy/sell
            total_quantity: 总数�?
            volume_share: 每笔占比

        返回:
            子订单列�?
        """
        child_quantity = int(total_quantity * volume_share)
        orders = []

        while total_quantity > 0:
            qty = min(child_quantity, total_quantity)
            order = Order(
                symbol=symbol,
                action=action,
                quantity=qty,
                order_type='limit',
                price=0
            )
            orders.append(order)
            total_quantity -= qty

        return orders

    def create_iceberg_order(
        self,
        symbol: str,
        action: str,
        total_quantity: int,
        visible_ratio: float = 0.1
    ) -> Order:
        """创建冰山订单

        参数:
            symbol: 股票代码
            action: buy/sell
            total_quantity: 总数�?
            visible_ratio: 可见的比�?

        返回:
            冰山订单
        """
        visible_quantity = int(total_quantity * visible_ratio)

        return Order(
            symbol=symbol,
            action=action,
            quantity=total_quantity,
            visible_quantity=visible_quantity,
            order_type='iceberg',
            price=0
        )
```

### 3.3 风控检�?

```python
class RiskChecker:
    """风控检查器

    索引: EXEC.001-M03
    上游: OrderGenerator
    下游: OrderExecutor
    """

    def __init__(self):
        self.rules = RiskRuleEngine()

    def check(self, order: Order, account: Account, market_data: MarketData) -> CheckResult:
        """检查订�?

        参数:
            order: 订单
            account: 账户信息
            market_data: 市场数据

        返回:
            CheckResult
        """
        violations = []

        # 1. 仓位检�?
        position_check = self._check_position(order, account)
        if not position_check.passed:
            violations.append(position_check)

        # 2. 资金检�?
        fund_check = self._check_fund(order, account, market_data)
        if not fund_check.passed:
            violations.append(fund_check)

        # 3. 价格检�?
        price_check = self._check_price(order, market_data)
        if not price_check.passed:
            violations.append(price_check)

        # 4. 规则检�?
        rule_check = self.rules.check(order, account)
        if not rule_check.passed:
            violations.append(rule_check)

        return CheckResult(
            passed=len(violations) == 0,
            violations=violations
        )

    def _check_position(self, order: Order, account: Account) -> CheckResult:
        """仓位检�?""
        if order.action == 'buy':
            pos = account.get_position(order.symbol)
            current_ratio = (pos.quantity * order.price) / account.total_value if pos else 0
            new_ratio = (pos.quantity * order.price + order.quantity * order.price) / account.total_value if pos else 0

            if new_ratio > 0.1:  # 单股不超�?0%
                return CheckResult(
                    passed=False,
                    reason=f"单股仓位超限: {new_ratio:.2%} > 10%"
                )

        return CheckResult(passed=True)

    def _check_fund(self, order: Order, account: Account, market_data: MarketData) -> CheckResult:
        """资金检�?""
        if order.action == 'buy':
            estimated_cost = order.quantity * order.price * 1.003  # 预估+手续�?
            if account.cash < estimated_cost:
                return CheckResult(
                    passed=False,
                    reason=f"资金不足: 需要{estimated_cost:.2f}, 可用{account.cash:.2f}"
                )

        return CheckResult(passed=True)
```

### 3.4 订单执行�?

```python
class OrderExecutor:
    """订单执行�?

    索引: EXEC.001-M04
    上游: RiskChecker
    下游: Broker
    """

    def __init__(self, mode: str = 'simulation'):
        """
        参数:
            mode: simulation / production
        """
        self.mode = mode
        self.broker = self._create_broker(mode)

    def execute(self, order: Order) -> ExecutionResult:
        """执行订单

        参数:
            order: 订单

        返回:
            ExecutionResult
        """
        try:
            # 1. 提交订单
            broker_order_id = self.broker.send_order(order)

            # 2. 等待成交回报
            result = self._wait_for_fill(broker_order_id, timeout=30)

            return ExecutionResult(
                success=True,
                order_id=order.id,
                broker_order_id=broker_order_id,
                filled_price=result.price,
                filled_quantity=result.quantity,
                commission=result.commission,
                filled_at=result.time
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                order_id=order.id,
                error=str(e)
            )

    def _create_broker(self, mode: str):
        """创建Broker"""
        if mode == 'simulation':
            return SimulatedBroker()
        elif mode == 'production':
            return VNpyBroker()
        else:
            raise ValueError(f"Unknown mode: {mode}")

    def _wait_for_fill(self, broker_order_id: str, timeout: int) -> FillResult:
        """等待成交"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = self.broker.get_fill_result(broker_order_id)
            if result.status == 'filled':
                return result
            time.sleep(0.1)
        raise TimeoutError(f"等待成交超时: {broker_order_id}")
```


## 4. 模拟撮合引擎

### 4.1 撮合逻辑

```python
class SimulatedBroker:
    """模拟Broker

    索引: EXEC.001-M05
    """

    def __init__(self):
        self.orders = {}

    def send_order(self, order: Order) -> str:
        """提交订单"""
        order_id = str(uuid.uuid4())
        self.orders[order_id] = {
            'order': order,
            'status': 'pending',
            'filled_price': 0,
            'filled_quantity': 0
        }

        # 异步撮合
        threading.Thread(target=self._match, args=(order_id,)).start()

        return order_id

    def _match(self, order_id: str):
        """撮合逻辑"""
        time.sleep(0.1)  # 模拟延迟

        order_data = self.orders[order_id]
        order = order_data['order']

        # 市价单立即成�?
        if order.order_type == 'market':
            # 使用昨收价模�?
            price = self._get模拟_price(order.symbol)
            slippage = price * 0.0002  # 万二滑点

            if order.action == 'buy':
                filled_price = price + slippage
            else:
                filled_price = price - slippage

            order_data['status'] = 'filled'
            order_data['filled_price'] = filled_price
            order_data['filled_quantity'] = order.quantity
            order_data['filled_time'] = datetime.now()
```


## 5. vn.py集成

### 5.1 vn.py连接�?

```python
class VNpyConnector:
    """vn.py连接�?

    索引: EXEC.001-M06
    """

    def __init__(self, gateway_name: str = 'ctp'):
        self.gateway_name = gateway_name
        self.trader = None
        self.gateway = None

    def connect(self, config: dict):
        """连接vn.py"""
        from vnpy.api.rest import RestClient
        from vnpy.trader.constant import Direction, Offset

        self.rest_client = RestClient()

        # 设置接口
        self.rest_client.connect(
            gateway_name=self.gateway_name,
            **config
        )

    def send_order(
        self,
        symbol: str,
        direction: str,
        volume: int,
        price: float = 0,
        order_type: str = 'limit'
    ) -> str:
        """发送订�?""
        if direction == 'long':
            direction = Direction.LONG
            offset = Offset.OPEN
        else:
            direction = Direction.SHORT
            offset = Offset.CLOSE

        if order_type == 'market':
            price = 0

        vt_order_id = self.rest_client.send_order(
            symbol=symbol,
            direction=direction,
            volume=volume,
            price=price,
            offset=offset
        )

        return vt_order_id

    def cancel_order(self, vt_order_id: str):
        """撤单"""
        self.rest_client.cancel_order(vt_order_id)

    def get_position(self, symbol: str) -> int:
        """获取持仓"""
        return self.rest_client.get_position(symbol)
```


## 6. API接口

### 6.1 交易API

```python
# API: /api/v1/trading

class TradingAPI:
    """交易API

    索引: API_TRADING_001
    """

    @router.post("/orders")
    def place_order(order: OrderRequest) -> OrderResponse:
        """下单

        参数:
            order: {
                symbol: '000001',
                action: 'buy' | 'sell',
                quantity: 1000,
                order_type: 'market' | 'limit',
                price: 10.0
            }
        """

    @router.delete("/orders/{order_id}")
    def cancel_order(order_id: str) -> CancelResponse:
        """撤单"""

    @router.get("/orders")
    def get_orders(status: str = None) -> List[Order]:
        """查询订单"""

    @router.get("/positions")
    def get_positions() -> List[Position]:
        """查询持仓"""

    @router.get("/account")
    def get_account() -> Account:
        """查询账户"""

    @router.post("/mode")
    def switch_mode(mode: str) -> Response:
        """切换模式
        mode: simulation / production
        """
```


## 7. 开发任务分�?

### 7.1 任务分解 (40h)

| 任务 | 时间 | 说明 |
|------|------|------|
| 订单生成�?| 6h | OrderGenerator |
| TWAP/VWAP算法 | 8h | SmartOrderAlgorithm |
| 风控检�?| 6h | RiskChecker |
| 订单执行�?| 6h | OrderExecutor |
| 模拟撮合 | 6h | SimulatedBroker |
| vn.py集成 | 4h | VNpyConnector |
| 交易API | 4h | REST API |


## 8. 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-29 | 初始版本 |


**维护�?*: 清风量化系统
**索引**: `EXEC.001`
---

## 9. 文档治理

### 9.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Exec Order Exec Bp
- **模块ID**: EXEC_ORDER_EXEC_BP_001
- **蓝图文档**: [ORDER_EXECUTION_BLUEPRINT.md](04_EXECUTION\01_ORDER_EXECUTION\ORDER_EXECUTION_BLUEPRINT.md)
- **技术规格书**: 待创建
- **职责**: 全系统架构设�?
- **状态**: Active
```

### 9.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Exec Order Exec Bp** | 全系统架构设�? | **核心模块** |

### 9.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-01 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-01 | **状态**: Active
