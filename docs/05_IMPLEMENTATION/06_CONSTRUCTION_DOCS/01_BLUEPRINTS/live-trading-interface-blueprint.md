---
module_id: LIVE_TRADING_INTERFACE_001_5970
version: 1.0.0
status: Active
priority: P0
created_date: 2026-04-08
last_updated: 2026-04-08
owner: 首席文档架构师
responsibility:
- 券商API接口集成
standard_type: 专业量化机构蓝图
compliance_level: 专业标准
layer: layer_08
---



# 实盘交易接口蓝图



> **核心职责**: 提供券商API接口集成，支持实盘交易执行、订单管理和账户管理

> **职责边界**:

> - ✅ 本文档负责：券商API接口集成、实盘交易执行、订单管理、账户管理

> - ❌ 本文档不负责：策略逻辑（由策略引擎负责）、风险控制（由风控模块负责）、数据获取（由数据模块负责）

>

> **上游模块**:

> - 策略引擎（STRATEGY_ENGINE_001）：提供交易信号

> - 智能执行引擎（SMART_EXECUTION_ENGINE_001）：提供执行算法

> - 风险控制模块（RISK_CONTROL_001）：提供风险限制和约束条件



## 核心定位



负责实盘交易接口模块的设计与构建，提供券商API接口集成、实盘交易执行、订单管理和账户管理功能，是Layer 5策略执行层的关键模块，连接策略引擎和券商交易系统。



## 接口与契约（蓝图终稿）



### API 契约索引



本模块遵循系统统一接口规范，详见 `API_Contract.md`。



### 核心接口定义



| 接口名称 | 索引 | 说明 |

|----------|------|------|

| 券商连接/鉴权 | API.TRADE.001 | 连接、鉴权与会话状态查询 |

| 下单/撤单/回报 | API.TRADE.002 | 订单生命周期与成交回报 |

| 账户/持仓查询 | API.TRADE.003 | 资金、持仓、风险敞口查询 |



### 数据格式规范



- 输入格式: `order_request/account_request`

- 输出格式: `order_ack/order_report/account_snapshot`

- 时间戳格式: ISO 8601 UTC



## 验收标准（可检查）



- 能在至少 1 个模拟/沙盒环境跑通端到端：连接→下单→回报→撤单/成交回报可追溯。

- 关键性能指标可测量：接口响应时间/下单延迟等指标有明确阈值口径与验证方法。

- 对外接口/事件能在 `API_Contract.md` 中定位到契约入口（或在“已知限制”列出未闭合项）。



## 已知限制



- 不同券商 API 字段口径与异常语义存在差异；实施阶段需固化适配层、异常映射与回归用例集合，并回填契约真源。



## 设计目标



### 主要目标



1. **券商API集成**: 集成多种券商API接口，支持实盘交易

2. **订单执行**: 执行交易订单，支持多种订单类型

3. **账户管理**: 管理交易账户，查询资金和持仓

4. **订单管理**: 管理订单生命周期，支持订单查询和撤销



### 质量目标



- 订单执行延迟: < 500ms

- 订单成功率: ≥ 99.9%

- 系统可用性: ≥ 99.5%

- API响应时间: < 200ms



## 开源方案选型



### 推荐方案: Vnpy + QMT/XtQuant



| 属性 | 详情 |

|------|------|

| **Vnpy** | 开源量化交易框架，25k+ Stars，支持多券商接口 |

| **QMT** | 国内主流券商支持的交易接口，免费使用 |

| **XtQuant** | QMT的Python API，易于集成 |

| **License** | MIT / Apache 2.0 |

| **语言** | Python |



**选择理由**:

1. **Vnpy**: 功能全面，支持多券商接口，社区活跃

2. **QMT**: 国内主流券商支持，免费使用，稳定可靠

3. **XtQuant**: Python API，易于集成和开发

4. **个人友好**: 免费开源，适合个人使用

5. **实盘支持**: 支持A股、期货、期权等多种市场



**对比其他方案**:



| 方案 | Stars | 优点 | 缺点 | 推荐度 |

|------|-------|------|------|--------|

| **Vnpy** | 25k+ | 功能全面、支持多券商 | 学习曲线陡峭 | ⭐⭐⭐⭐⭐ |

| **QMT/XtQuant** | - | 国内主流、免费、稳定 | 仅支持国内券商 | ⭐⭐⭐⭐⭐ |

| **EasyTrader** | 8k+ | 简单易用 | 功能相对简单 | ⭐⭐⭐⭐ |

| **自研** | - | 完全定制 | 开发成本高 | ⭐⭐⭐ |



**最终选择**: Vnpy（框架） + QMT/XtQuant（券商接口）



**开源集成方案**:

```python

from vnpy.event import EventEngine

from vnpy.trader.engine import MainEngine

from vnpy.trader.ui import MainWindow, create_qapp

from vnpy.gateway.ctp import CtpGateway

from vnpy.gateway.xt import XtGateway



class LiveTradingInterface:

    """实盘交易接口 - 基于Vnpy"""



    def __init__(self):

        self.event_engine = EventEngine()

        self.main_engine = MainEngine(self.event_engine)



        self.main_engine.add_gateway(CtpGateway)

        self.main_engine.add_gateway(XtGateway)



    def connect_broker(self, gateway_name: str, setting: dict):

        """连接券商"""

        self.main_engine.connect(setting, gateway_name)



    def send_order(self, req: OrderRequest):

        """发送订单"""

        return self.main_engine.send_order(req, req.gateway_name)

```



## 核心功能设计



### 1. 券商接口管理



```python

from typing import Dict, List, Optional

from dataclasses import dataclass

from datetime import datetime

from enum import Enum

import logging



class BrokerType(Enum):

    """券商类型"""

    QMT = "QMT"

    CTP = "CTP"

    XTP = "XTP"

    VNPY = "VNPY"



@dataclass

class BrokerConfig:

    """券商配置"""

    broker_type: BrokerType

    broker_name: str

    account_id: str

    password: str

    broker_api: str

    md_address: str

    td_address: str

    app_id: str

    auth_code: str



class BrokerInterfaceManager:

    """券商接口管理器"""



    def __init__(self):

        self.brokers: Dict[str, BrokerConfig] = {}

        self.connections: Dict[str, bool] = {}

        self.logger = logging.getLogger(__name__)



    def add_broker(self, config: BrokerConfig) -> bool:

        """添加券商配置"""

        try:

            self.brokers[config.broker_name] = config

            self.connections[config.broker_name] = False

            self.logger.info(f"Added broker: {config.broker_name}")

            return True

        except Exception as e:

            self.logger.error(f"Failed to add broker: {e}")

            return False



    def connect_broker(self, broker_name: str) -> bool:

        """连接券商"""

        try:

            config = self.brokers.get(broker_name)

            if not config:

                self.logger.error(f"Broker not found: {broker_name}")

                return False



            if config.broker_type == BrokerType.QMT:

                return self._connect_qmt(config)

            elif config.broker_type == BrokerType.CTP:

                return self._connect_ctp(config)

            else:

                self.logger.error(f"Unsupported broker type: {config.broker_type}")

                return False



        except Exception as e:

            self.logger.error(f"Failed to connect broker: {e}")

            return False



    def _connect_qmt(self, config: BrokerConfig) -> bool:

        """连接QMT"""

        try:

            from xtquant import xtdata

            from xtquant.xttrader import XtQuantTrader



            trader = XtQuantTrader(config.broker_api, config.account_id)

            trader.connect()



            self.connections[config.broker_name] = True

            self.logger.info(f"Connected to QMT: {config.broker_name}")

            return True



        except Exception as e:

            self.logger.error(f"Failed to connect QMT: {e}")

            return False



    def _connect_ctp(self, config: BrokerConfig) -> bool:

        """连接CTP"""

        try:

            from vnpy.gateway.ctp import CtpGateway



            self.connections[config.broker_name] = True

            self.logger.info(f"Connected to CTP: {config.broker_name}")

            return True



        except Exception as e:

            self.logger.error(f"Failed to connect CTP: {e}")

            return False

```



### 2. 订单执行引擎



```python

from dataclasses import dataclass

from enum import Enum

from typing import Optional

from datetime import datetime



class OrderType(Enum):

    """订单类型"""

    MARKET = "MARKET"

    LIMIT = "LIMIT"

    STOP = "STOP"

    STOP_LIMIT = "STOP_LIMIT"



class OrderDirection(Enum):

    """订单方向"""

    BUY = "BUY"

    SELL = "SELL"



class OrderStatus(Enum):

    """订单状态"""

    PENDING = "PENDING"

    SUBMITTED = "SUBMITTED"

    PARTIAL_FILLED = "PARTIAL_FILLED"

    FILLED = "FILLED"

    CANCELLED = "CANCELLED"

    REJECTED = "REJECTED"



@dataclass

class Order:

    """订单"""

    order_id: str

    symbol: str

    exchange: str

    direction: OrderDirection

    order_type: OrderType

    quantity: int

    price: Optional[float]

    status: OrderStatus

    filled_quantity: int

    filled_price: float

    create_time: datetime

    update_time: datetime

    broker_name: str



@dataclass

class OrderRequest:

    """订单请求"""

    symbol: str

    exchange: str

    direction: OrderDirection

    order_type: OrderType

    quantity: int

    price: Optional[float]

    broker_name: str



class OrderExecutionEngine:

    """订单执行引擎"""



    def __init__(self, broker_manager: BrokerInterfaceManager):

        self.broker_manager = broker_manager

        self.orders: Dict[str, Order] = {}

        self.logger = logging.getLogger(__name__)



    def send_order(self, req: OrderRequest) -> Optional[str]:

        """发送订单"""

        try:

            if not self.broker_manager.connections.get(req.broker_name):

                self.logger.error(f"Broker not connected: {req.broker_name}")

                return None



            order_id = self._generate_order_id()



            order = Order(

                order_id=order_id,

                symbol=req.symbol,

                exchange=req.exchange,

                direction=req.direction,

                order_type=req.order_type,

                quantity=req.quantity,

                price=req.price,

                status=OrderStatus.PENDING,

                filled_quantity=0,

                filled_price=0.0,

                create_time=datetime.now(),

                update_time=datetime.now(),

                broker_name=req.broker_name

            )



            self.orders[order_id] = order



            if req.broker_name == "QMT":

                success = self._send_qmt_order(order)

            else:

                success = self._send_vnpy_order(order)



            if success:

                order.status = OrderStatus.SUBMITTED

                self.logger.info(f"Order submitted: {order_id}")

                return order_id

            else:

                order.status = OrderStatus.REJECTED

                self.logger.error(f"Order rejected: {order_id}")

                return None



        except Exception as e:

            self.logger.error(f"Failed to send order: {e}")

            return None



    def cancel_order(self, order_id: str) -> bool:

        """撤销订单"""

        try:

            order = self.orders.get(order_id)

            if not order:

                self.logger.error(f"Order not found: {order_id}")

                return False



            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:

                self.logger.error(f"Cannot cancel order with status: {order.status}")

                return False



            if order.broker_name == "QMT":

                success = self._cancel_qmt_order(order)

            else:

                success = self._cancel_vnpy_order(order)



            if success:

                order.status = OrderStatus.CANCELLED

                order.update_time = datetime.now()

                self.logger.info(f"Order cancelled: {order_id}")

                return True

            else:

                self.logger.error(f"Failed to cancel order: {order_id}")

                return False



        except Exception as e:

            self.logger.error(f"Failed to cancel order: {e}")

            return False



    def query_order(self, order_id: str) -> Optional[Order]:

        """查询订单"""

        return self.orders.get(order_id)



    def _generate_order_id(self) -> str:

        """生成订单ID"""

        import uuid

        return f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"



    def _send_qmt_order(self, order: Order) -> bool:

        """发送QMT订单"""

        try:

            from xtquant.xttrader import XtQuantTrader



            return True



        except Exception as e:

            self.logger.error(f"Failed to send QMT order: {e}")

            return False



    def _send_vnpy_order(self, order: Order) -> bool:

        """发送Vnpy订单"""

        try:

            return True



        except Exception as e:

            self.logger.error(f"Failed to send Vnpy order: {e}")

            return False

```



### 3. 账户管理



```python

from dataclasses import dataclass

from typing import Dict, List

from datetime import datetime



@dataclass

class Position:

    """持仓"""

    symbol: str

    exchange: str

    direction: str

    quantity: int

    available_quantity: int

    avg_price: float

    current_price: float

    pnl: float

    pnl_pct: float



@dataclass

class Account:

    """账户"""

    account_id: str

    broker_name: str

    balance: float

    available: float

    margin: float

    pnl: float

    positions: List[Position]

    update_time: datetime



class AccountManager:

    """账户管理器"""



    def __init__(self, broker_manager: BrokerInterfaceManager):

        self.broker_manager = broker_manager

        self.accounts: Dict[str, Account] = {}

        self.logger = logging.getLogger(__name__)



    def query_account(self, broker_name: str) -> Optional[Account]:

        """查询账户"""

        try:

            if not self.broker_manager.connections.get(broker_name):

                self.logger.error(f"Broker not connected: {broker_name}")

                return None



            if broker_name == "QMT":

                return self._query_qmt_account(broker_name)

            else:

                return self._query_vnpy_account(broker_name)



        except Exception as e:

            self.logger.error(f"Failed to query account: {e}")

            return None



    def query_positions(self, broker_name: str) -> List[Position]:

        """查询持仓"""

        try:

            account = self.query_account(broker_name)

            if account:

                return account.positions

            return []



        except Exception as e:

            self.logger.error(f"Failed to query positions: {e}")

            return []



    def _query_qmt_account(self, broker_name: str) -> Optional[Account]:

        """查询QMT账户"""

        try:

            from xtquant.xttrader import XtQuantTrader



            return Account(

                account_id="",

                broker_name=broker_name,

                balance=0.0,

                available=0.0,

                margin=0.0,

                pnl=0.0,

                positions=[],

                update_time=datetime.now()

            )



        except Exception as e:

            self.logger.error(f"Failed to query QMT account: {e}")

            return None



    def _query_vnpy_account(self, broker_name: str) -> Optional[Account]:

        """查询Vnpy账户"""

        try:

            return Account(

                account_id="",

                broker_name=broker_name,

                balance=0.0,

                available=0.0,

                margin=0.0,

                pnl=0.0,

                positions=[],

                update_time=datetime.now()

            )



        except Exception as e:

            self.logger.error(f"Failed to query Vnpy account: {e}")

            return None

```



### 4. 实盘交易管理器



```python

class LiveTradingManager:

    """实盘交易管理器"""



    def __init__(self):

        self.broker_manager = BrokerInterfaceManager()

        self.order_engine = OrderExecutionEngine(self.broker_manager)

        self.account_manager = AccountManager(self.broker_manager)

        self.logger = logging.getLogger(__name__)



    def initialize(self, broker_configs: List[BrokerConfig]) -> bool:

        """初始化"""

        try:

            for config in broker_configs:

                self.broker_manager.add_broker(config)



            self.logger.info("Live trading manager initialized")

            return True



        except Exception as e:

            self.logger.error(f"Failed to initialize: {e}")

            return False



    def connect_all_brokers(self) -> Dict[str, bool]:

        """连接所有券商"""

        results = {}

        for broker_name in self.broker_manager.brokers.keys():

            results[broker_name] = self.broker_manager.connect_broker(broker_name)

        return results



    def execute_signal(

        self,

        signal: Dict,

        broker_name: str

    ) -> Optional[str]:

        """执行交易信号"""

        try:

            req = OrderRequest(

                symbol=signal['symbol'],

                exchange=signal['exchange'],

                direction=OrderDirection[signal['direction']],

                order_type=OrderType[signal.get('order_type', 'MARKET')],

                quantity=signal['quantity'],

                price=signal.get('price'),

                broker_name=broker_name

            )



            return self.order_engine.send_order(req)



        except Exception as e:

            self.logger.error(f"Failed to execute signal: {e}")

            return None

```



## 数据模型与存储



### 数据存储设计



#### 订单记录表

```sql

CREATE TABLE live_orders (

    order_id VARCHAR(50) PRIMARY KEY,

    broker_name VARCHAR(20) NOT NULL,

    symbol VARCHAR(20) NOT NULL,

    exchange VARCHAR(20) NOT NULL,

    direction VARCHAR(10) NOT NULL,

    order_type VARCHAR(20) NOT NULL,

    quantity INT NOT NULL,

    price DECIMAL(10, 4),

    status VARCHAR(20) NOT NULL,

    filled_quantity INT NOT NULL,

    filled_price DECIMAL(10, 4),

    create_time TIMESTAMP NOT NULL,

    update_time TIMESTAMP NOT NULL,

    broker_order_id VARCHAR(50),

    INDEX idx_symbol (symbol),

    INDEX idx_status (status),

    INDEX idx_create_time (create_time)

);

```



#### 账户快照表

```sql

CREATE TABLE account_snapshots (

    snapshot_id VARCHAR(50) PRIMARY KEY,

    broker_name VARCHAR(20) NOT NULL,

    account_id VARCHAR(50) NOT NULL,

    balance DECIMAL(15, 2) NOT NULL,

    available DECIMAL(15, 2) NOT NULL,

    margin DECIMAL(15, 2) NOT NULL,

    pnl DECIMAL(15, 2) NOT NULL,

    snapshot_time TIMESTAMP NOT NULL,

    INDEX idx_broker_name (broker_name),

    INDEX idx_snapshot_time (snapshot_time)

);

```



## 实施路径（个人开发优化版）



### Phase 1: 核心功能（Week 1，共5天）



**目标**: 实现基础实盘交易功能



**任务清单**:

- [ ] 安装和配置Vnpy、QMT/XtQuant

- [ ] 实现券商接口管理器

- [ ] 实现订单执行引擎

- [ ] 实现账户管理器

- [ ] 编写单元测试



**交付物**:

- BrokerInterfaceManager类

- OrderExecutionEngine类

- AccountManager类

- 单元测试覆盖率≥80%



**个人开发建议**:

- 使用QMT作为主要券商接口（国内主流、免费）

- 优先实现市价单和限价单

- 使用SQLite存储订单记录（简化部署）



### Phase 2: 高级功能（Week 2，共5天）



**目标**: 实现高级交易功能和监控



**任务清单**:

- [ ] 实现多种订单类型（止损单、止损限价单）

- [ ] 实现订单状态监控

- [ ] 实现持仓同步

- [ ] 集成到策略引擎

- [ ] 编写集成测试



**交付物**:

- 高级订单类型支持

- 订单状态监控

- 持仓同步功能

- 集成测试覆盖率≥70%



**个人开发建议**:

- 止损单可以后续实现

- 优先保证核心功能稳定

- 持仓同步可以定时查询



### Phase 3: 优化完善（可选，Week 3）



**目标**: 实现性能优化和风控集成



**任务清单**:

- [ ] 实现订单执行性能优化

- [ ] 集成风控模块

- [ ] 实现异常处理和重连机制

- [ ] 性能测试和优化

- [ ] 文档完善



**交付物**:

- 性能优化报告

- 风控集成

- 异常处理机制

- 完整文档



**个人开发建议**:

- 这部分是可选的，根据实际需求决定

- 风控集成可以参考RISK_CONTROL_BLUEPRINT

- 异常处理可以放在最后



**总工时估算**:

- Phase 1: 5天（核心功能）

- Phase 2: 5天（高级功能）

- Phase 3: 5天（可选优化）

- **总计**: 10-15天（根据个人情况调整）



## 风险评估



### 技术风险



| 风险ID | 风险描述 | 影响程度 | 缓解措施 |

|--------|----------|----------|----------|

| TR-001 | 券商API不稳定 | 高 | 实现重连机制，使用多个券商 |

| TR-002 | 网络延迟 | 中 | 使用异步执行，优化网络配置 |

| TR-003 | 订单执行失败 | 高 | 实现订单重试机制，记录失败原因 |



### 实施风险



| 风险ID | 风险描述 | 影响程度 | 缓解措施 |

|--------|----------|----------|----------|

| IR-001 | 券商API文档不完善 | 中 | 参考Vnpy社区文档，测试验证 |

| IR-002 | 实盘交易风险 | 高 | 先在模拟环境测试，小资金试运行 |

| IR-003 | 资金安全 | 高 | 实现严格的风控，限制单笔交易金额 |



## 验收标准



### 功能验收标准



| 功能 | 验收标准 | 测试方法 |

|------|----------|----------|

| 券商连接 | 成功连接券商API | 集成测试 |

| 订单执行 | 订单成功提交和执行 | 集成测试 |

| 账户查询 | 正确查询账户信息 | 集成测试 |

| 持仓查询 | 正确查询持仓信息 | 集成测试 |



### 性能验收标准



| 指标 | 目标值 | 验收方法 |

|------|--------|----------|

| 订单执行延迟 | < 500ms | 性能测试 |

| API响应时间 | < 200ms | 性能测试 |

| 系统可用性 | ≥ 99.5% | 监控验证 |



### 质量验收标准



| 标准 | 要求 | 验收方法 |

|------|------|----------|

| 代码覆盖率 | ≥80% | pytest-cov |

| 文档完整性 | 100% | 文档审查 |

| 代码规范 | 符合PEP8 | pylint |



```
```---
```



**文档版本**: v1.0.0

**创建日期**: 2026-04-08

**最后更新**: 2026-04-08

**状态**: Active
