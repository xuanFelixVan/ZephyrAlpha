---
module_id: THIRD_PARTY_API_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席蓝图架构师
standard_type: 专业量化机构第三方接口集成标准
applicable_scope: 多引擎接口集成
compliance_level: 专业机构标准
parent_document: P0-01_Database_Design_Document.md
implementation_status: 进行中
---

# 第三方接口集成设计（专业量化机构标准）

> 清风量化系统 v5.0 - 专业量化机构标准第三方接口集成设计
> **集成引擎**: vn.py, RQAlpha, Backtrader, QMT, Backtesting.py
> **设计原则**: 接口统一、适配器模式、松耦合、易扩展

## 📋 接口集成概述

### 引擎集成架构

```
┌─────────────────────────────────────────────────────────────┐
│                    统一引擎接口层                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          EngineInterface (统一接口)                   │  │
│  │  - create_order()    创建订单                         │  │
│  │  - cancel_order()    取消订单                         │  │
│  │  - query_order()     查询订单                         │  │
│  │  - query_position()  查询持仓                         │  │
│  │  - query_account()   查询账户                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ 适配器模式
┌─────────────────────────────────────────────────────────────┐
│                    引擎适配器层                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │VnpyAdapter│ │RQAlphaAdapter│ │BacktraderAdapter│ │QMTAdapter│ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│  ┌──────────┐                                              │
│  │BacktestingAdapter│                                      │
│  └──────────┘                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓ 第三方引擎
┌─────────────────────────────────────────────────────────────┐
│                    第三方引擎层                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │   vn.py  │ │  RQAlpha │ │Backtrader│ │   QMT    │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│  ┌──────────┐                                              │
│  │Backtesting.py│                                          │
│  └──────────┘                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. 统一引擎接口 (EngineInterface)

### 1.1 接口定义

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

class EngineInterface(ABC):
    """统一引擎接口"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化引擎"""
        pass
    
    @abstractmethod
    async def connect(self) -> bool:
        """连接引擎"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """断开连接"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        pass
    
    @abstractmethod
    async def create_order(
        self,
        account_id: int,
        stock_code: str,
        exchange: str,
        direction: str,
        order_type: str,
        price: Decimal,
        quantity: int
    ) -> Dict[str, Any]:
        """创建订单"""
        pass
    
    @abstractmethod
    async def cancel_order(
        self,
        order_id: str
    ) -> bool:
        """取消订单"""
        pass
    
    @abstractmethod
    async def query_order(
        self,
        order_id: str
    ) -> Dict[str, Any]:
        """查询订单"""
        pass
    
    @abstractmethod
    async def query_orders(
        self,
        account_id: int,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """查询订单列表"""
        pass
    
    @abstractmethod
    async def query_position(
        self,
        account_id: int,
        stock_code: str
    ) -> Dict[str, Any]:
        """查询持仓"""
        pass
    
    @abstractmethod
    async def query_positions(
        self,
        account_id: int
    ) -> List[Dict[str, Any]]:
        """查询持仓列表"""
        pass
    
    @abstractmethod
    async def query_account(
        self,
        account_id: int
    ) -> Dict[str, Any]:
        """查询账户"""
        pass
    
    @abstractmethod
    async def subscribe_market_data(
        self,
        stock_codes: List[str]
    ) -> bool:
        """订阅行情"""
        pass
    
    @abstractmethod
    async def unsubscribe_market_data(
        self,
        stock_codes: List[str]
    ) -> bool:
        """取消订阅行情"""
        pass
    
    @abstractmethod
    async def get_market_data(
        self,
        stock_code: str
    ) -> Dict[str, Any]:
        """获取行情数据"""
        pass
```

---

## 2. vn.py引擎适配器 (VnpyAdapter)

### 2.1 适配器实现

```python
from typing import Dict, Any, List, Optional
from decimal import Decimal
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import (
    OrderRequest,
    CancelRequest,
    Direction,
    OrderType,
    Exchange
)

class VnpyAdapter(EngineInterface):
    """vn.py引擎适配器"""
    
    def __init__(self, engine_id: str, config: Dict[str, Any]):
        self.engine_id = engine_id
        self.config = config
        self.event_engine = None
        self.main_engine = None
        self.gateway_name = config.get('gateway', 'CTP')
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化vn.py引擎"""
        try:
            self.event_engine = EventEngine()
            self.main_engine = MainEngine(self.event_engine)
            
            # 添加网关
            if self.gateway_name == 'CTP':
                from vnpy.trader.gateway import CtpGateway
                self.main_engine.add_gateway(CtpGateway)
            
            return True
        except Exception as e:
            print(f"vn.py初始化失败: {e}")
            return False
    
    async def connect(self) -> bool:
        """连接vn.py引擎"""
        try:
            # 连接网关
            self.main_engine.connect(self.config, self.gateway_name)
            return True
        except Exception as e:
            print(f"vn.py连接失败: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """断开连接"""
        try:
            self.main_engine.close()
            return True
        except Exception as e:
            print(f"vn.py断开连接失败: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查引擎状态
            status = self.main_engine.get_gateway(self.gateway_name)
            
            return {
                'engine_id': self.engine_id,
                'status': 'healthy' if status else 'unhealthy',
                'gateway': self.gateway_name,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'engine_id': self.engine_id,
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def create_order(
        self,
        account_id: int,
        stock_code: str,
        exchange: str,
        direction: str,
        order_type: str,
        price: Decimal,
        quantity: int
    ) -> Dict[str, Any]:
        """创建订单"""
        try:
            # 转换方向
            vn_direction = Direction.LONG if direction == 'buy' else Direction.SHORT
            
            # 转换订单类型
            vn_order_type = OrderType.LIMIT if order_type == 'limit' else OrderType.MARKET
            
            # 转换交易所
            vn_exchange = Exchange.SHFE if exchange == 'SH' else Exchange.CZCE
            
            # 创建订单请求
            req = OrderRequest(
                symbol=stock_code,
                exchange=vn_exchange,
                direction=vn_direction,
                type=vn_order_type,
                price=float(price),
                volume=quantity,
                reference=f"ZEPHYR_{account_id}"
            )
            
            # 发送订单
            order_id = self.main_engine.send_order(req, self.gateway_name)
            
            return {
                'success': True,
                'order_id': order_id,
                'engine_id': self.engine_id,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        try:
            # 获取订单信息
            order = self.main_engine.get_order(order_id)
            
            if not order:
                return False
            
            # 创建取消请求
            req = CancelRequest(
                orderid=order_id,
                symbol=order.symbol,
                exchange=order.exchange
            )
            
            # 取消订单
            self.main_engine.cancel_order(req, self.gateway_name)
            
            return True
        except Exception as e:
            print(f"取消订单失败: {e}")
            return False
    
    async def query_order(self, order_id: str) -> Dict[str, Any]:
        """查询订单"""
        try:
            order = self.main_engine.get_order(order_id)
            
            if not order:
                return {}
            
            return {
                'order_id': order.vt_orderid,
                'symbol': order.symbol,
                'exchange': order.exchange.value,
                'direction': 'buy' if order.direction == Direction.LONG else 'sell',
                'order_type': 'limit' if order.type == OrderType.LIMIT else 'market',
                'price': Decimal(str(order.price)),
                'volume': order.volume,
                'traded': order.traded,
                'status': order.status.value,
                'timestamp': order.datetime.isoformat()
            }
        except Exception as e:
            print(f"查询订单失败: {e}")
            return {}
    
    async def query_orders(
        self,
        account_id: int,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """查询订单列表"""
        try:
            orders = self.main_engine.get_all_orders()
            
            result = []
            for order in orders:
                if status and order.status.value != status:
                    continue
                
                result.append({
                    'order_id': order.vt_orderid,
                    'symbol': order.symbol,
                    'exchange': order.exchange.value,
                    'direction': 'buy' if order.direction == Direction.LONG else 'sell',
                    'price': Decimal(str(order.price)),
                    'volume': order.volume,
                    'traded': order.traded,
                    'status': order.status.value
                })
            
            return result
        except Exception as e:
            print(f"查询订单列表失败: {e}")
            return []
    
    async def query_position(
        self,
        account_id: int,
        stock_code: str
    ) -> Dict[str, Any]:
        """查询持仓"""
        try:
            positions = self.main_engine.get_all_positions()
            
            for position in positions:
                if position.symbol == stock_code:
                    return {
                        'symbol': position.symbol,
                        'exchange': position.exchange.value,
                        'direction': 'long' if position.direction == Direction.LONG else 'short',
                        'volume': position.volume,
                        'frozen': position.frozen,
                        'price': Decimal(str(position.price)),
                        'pnl': Decimal(str(position.pnl))
                    }
            
            return {}
        except Exception as e:
            print(f"查询持仓失败: {e}")
            return {}
    
    async def query_positions(self, account_id: int) -> List[Dict[str, Any]]:
        """查询持仓列表"""
        try:
            positions = self.main_engine.get_all_positions()
            
            result = []
            for position in positions:
                result.append({
                    'symbol': position.symbol,
                    'exchange': position.exchange.value,
                    'direction': 'long' if position.direction == Direction.LONG else 'short',
                    'volume': position.volume,
                    'frozen': position.frozen,
                    'price': Decimal(str(position.price)),
                    'pnl': Decimal(str(position.pnl))
                })
            
            return result
        except Exception as e:
            print(f"查询持仓列表失败: {e}")
            return []
    
    async def query_account(self, account_id: int) -> Dict[str, Any]:
        """查询账户"""
        try:
            accounts = self.main_engine.get_all_accounts()
            
            if accounts:
                account = accounts[0]
                return {
                    'account_id': account.accountid,
                    'balance': Decimal(str(account.balance)),
                    'frozen': Decimal(str(account.frozen)),
                    'available': Decimal(str(account.available)),
                    'margin': Decimal(str(account.margin))
                }
            
            return {}
        except Exception as e:
            print(f"查询账户失败: {e}")
            return {}
    
    async def subscribe_market_data(self, stock_codes: List[str]) -> bool:
        """订阅行情"""
        try:
            for stock_code in stock_codes:
                self.main_engine.subscribe(stock_code, self.gateway_name)
            
            return True
        except Exception as e:
            print(f"订阅行情失败: {e}")
            return False
    
    async def unsubscribe_market_data(self, stock_codes: List[str]) -> bool:
        """取消订阅行情"""
        # vn.py暂不支持取消订阅
        return True
    
    async def get_market_data(self, stock_code: str) -> Dict[str, Any]:
        """获取行情数据"""
        try:
            tick = self.main_engine.get_tick(stock_code)
            
            if not tick:
                return {}
            
            return {
                'symbol': tick.symbol,
                'exchange': tick.exchange.value,
                'last_price': Decimal(str(tick.last_price)),
                'bid_price_1': Decimal(str(tick.bid_price_1)),
                'ask_price_1': Decimal(str(tick.ask_price_1)),
                'bid_volume_1': tick.bid_volume_1,
                'ask_volume_1': tick.ask_volume_1,
                'volume': tick.volume,
                'turnover': Decimal(str(tick.turnover)),
                'timestamp': tick.datetime.isoformat()
            }
        except Exception as e:
            print(f"获取行情数据失败: {e}")
            return {}
```

---

## 3. RQAlpha引擎适配器 (RQAlphaAdapter)

### 3.1 适配器实现

```python
from typing import Dict, Any, List, Optional
from decimal import Decimal
import rqalpha as rq
from rqalpha.const import SIDE, POSITION_EFFECT

class RQAlphaAdapter(EngineInterface):
    """RQAlpha引擎适配器"""
    
    def __init__(self, engine_id: str, config: Dict[str, Any]):
        self.engine_id = engine_id
        self.config = config
        self.env = None
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化RQAlpha引擎"""
        try:
            # 创建RQAlpha环境
            self.env = rq.create_env(config)
            return True
        except Exception as e:
            print(f"RQAlpha初始化失败: {e}")
            return False
    
    async def connect(self) -> bool:
        """连接RQAlpha引擎"""
        try:
            # RQAlpha不需要连接
            return True
        except Exception as e:
            print(f"RQAlpha连接失败: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """断开连接"""
        try:
            if self.env:
                self.env.stop()
            return True
        except Exception as e:
            print(f"RQAlpha断开连接失败: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            return {
                'engine_id': self.engine_id,
                'status': 'healthy' if self.env else 'unhealthy',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'engine_id': self.engine_id,
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def create_order(
        self,
        account_id: int,
        stock_code: str,
        exchange: str,
        direction: str,
        order_type: str,
        price: Decimal,
        quantity: int
    ) -> Dict[str, Any]:
        """创建订单"""
        try:
            # 转换方向
            side = SIDE.BUY if direction == 'buy' else SIDE.SELL
            
            # 创建订单
            order_id = self.env.portfolio.order(
                id_or_ins=stock_code,
                amount=quantity,
                side=side,
                price=float(price),
                position_effect=POSITION_EFFECT.OPEN
            )
            
            return {
                'success': True,
                'order_id': str(order_id),
                'engine_id': self.engine_id,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        try:
            # RQAlpha不支持取消订单
            return False
        except Exception as e:
            print(f"取消订单失败: {e}")
            return False
    
    async def query_order(self, order_id: str) -> Dict[str, Any]:
        """查询订单"""
        # RQAlpha不支持查询订单
        return {}
    
    async def query_orders(
        self,
        account_id: int,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """查询订单列表"""
        # RQAlpha不支持查询订单列表
        return []
    
    async def query_position(
        self,
        account_id: int,
        stock_code: str
    ) -> Dict[str, Any]:
        """查询持仓"""
        try:
            position = self.env.portfolio.positions.get(stock_code)
            
            if not position:
                return {}
            
            return {
                'symbol': position.order_book_id,
                'quantity': position.quantity,
                'pnl': Decimal(str(position.pnl)),
                'market_value': Decimal(str(position.market_value))
            }
        except Exception as e:
            print(f"查询持仓失败: {e}")
            return {}
    
    async def query_positions(self, account_id: int) -> List[Dict[str, Any]]:
        """查询持仓列表"""
        try:
            positions = self.env.portfolio.positions
            
            result = []
            for position in positions.values():
                result.append({
                    'symbol': position.order_book_id,
                    'quantity': position.quantity,
                    'pnl': Decimal(str(position.pnl)),
                    'market_value': Decimal(str(position.market_value))
                })
            
            return result
        except Exception as e:
            print(f"查询持仓列表失败: {e}")
            return []
    
    async def query_account(self, account_id: int) -> Dict[str, Any]:
        """查询账户"""
        try:
            portfolio = self.env.portfolio
            
            return {
                'total_value': Decimal(str(portfolio.total_value)),
                'cash': Decimal(str(portfolio.cash)),
                'market_value': Decimal(str(portfolio.market_value)),
                'pnl': Decimal(str(portfolio.pnl))
            }
        except Exception as e:
            print(f"查询账户失败: {e}")
            return {}
    
    async def subscribe_market_data(self, stock_codes: List[str]) -> bool:
        """订阅行情"""
        # RQAlpha自动订阅
        return True
    
    async def unsubscribe_market_data(self, stock_codes: List[str]) -> bool:
        """取消订阅行情"""
        return True
    
    async def get_market_data(self, stock_code: str) -> Dict[str, Any]:
        """获取行情数据"""
        try:
            bar = self.env.get_bar(stock_code)
            
            if not bar:
                return {}
            
            return {
                'symbol': stock_code,
                'open': Decimal(str(bar.open)),
                'high': Decimal(str(bar.high)),
                'low': Decimal(str(bar.low)),
                'close': Decimal(str(bar.close)),
                'volume': bar.volume,
                'timestamp': bar.datetime.isoformat()
            }
        except Exception as e:
            print(f"获取行情数据失败: {e}")
            return {}
```

---

## 4. 引擎管理服务 (EngineManagerService)

### 4.1 服务实现

```python
from typing import Dict, Any, List, Optional
from enum import Enum

class EngineType(Enum):
    """引擎类型"""
    VNPY = 'vnpy'
    RQALPHA = 'rqalpha'
    BACKTRADER = 'backtrader'
    QMT = 'qmt'
    BACKTESTING = 'backtesting'

class EngineManagerService:
    """引擎管理服务"""
    
    def __init__(self):
        self.engines: Dict[str, EngineInterface] = {}
        self.engine_configs: Dict[str, Dict[str, Any]] = {}
    
    async def register_engine(
        self,
        engine_id: str,
        engine_type: EngineType,
        config: Dict[str, Any]
    ) -> bool:
        """注册引擎"""
        try:
            # 创建引擎适配器
            if engine_type == EngineType.VNPY:
                adapter = VnpyAdapter(engine_id, config)
            elif engine_type == EngineType.RQALPHA:
                adapter = RQAlphaAdapter(engine_id, config)
            else:
                raise ValueError(f"不支持的引擎类型: {engine_type}")
            
            # 初始化引擎
            success = await adapter.initialize(config)
            
            if success:
                self.engines[engine_id] = adapter
                self.engine_configs[engine_id] = config
                return True
            
            return False
        except Exception as e:
            print(f"注册引擎失败: {e}")
            return False
    
    async def connect_engine(self, engine_id: str) -> bool:
        """连接引擎"""
        try:
            engine = self.engines.get(engine_id)
            
            if not engine:
                return False
            
            return await engine.connect()
        except Exception as e:
            print(f"连接引擎失败: {e}")
            return False
    
    async def disconnect_engine(self, engine_id: str) -> bool:
        """断开引擎连接"""
        try:
            engine = self.engines.get(engine_id)
            
            if not engine:
                return False
            
            return await engine.disconnect()
        except Exception as e:
            print(f"断开引擎连接失败: {e}")
            return False
    
    async def health_check_engine(self, engine_id: str) -> Dict[str, Any]:
        """健康检查引擎"""
        try:
            engine = self.engines.get(engine_id)
            
            if not engine:
                return {
                    'engine_id': engine_id,
                    'status': 'not_found'
                }
            
            return await engine.health_check()
        except Exception as e:
            return {
                'engine_id': engine_id,
                'status': 'error',
                'error': str(e)
            }
    
    async def health_check_all(self) -> List[Dict[str, Any]]:
        """健康检查所有引擎"""
        results = []
        
        for engine_id in self.engines:
            result = await self.health_check_engine(engine_id)
            results.append(result)
        
        return results
    
    def get_engine(self, engine_id: str) -> Optional[EngineInterface]:
        """获取引擎"""
        return self.engines.get(engine_id)
    
    def get_all_engines(self) -> List[str]:
        """获取所有引擎ID"""
        return list(self.engines.keys())
```

---

## 5. 接口集成规范

### 5.1 数据格式转换

| 字段 | 系统格式 | vn.py格式 | RQAlpha格式 |
|------|----------|-----------|-------------|
| **交易方向** | buy/sell | LONG/SHORT | BUY/SELL |
| **订单类型** | limit/market | LIMIT/MARKET | LIMIT/MARKET |
| **交易所** | SH/SZ | SHFE/SZSE | SH/SZ |
| **订单状态** | pending/submitted/filled | NOTTRADED/TRADED | pending/filled |

### 5.2 错误处理

| 错误类型 | 处理方式 | 重试策略 |
|----------|----------|----------|
| **连接失败** | 记录日志，返回错误 | 重试3次，间隔5秒 |
| **订单失败** | 记录日志，返回错误 | 不重试 |
| **查询失败** | 记录日志，返回空结果 | 重试2次，间隔2秒 |
| **超时** | 记录日志，返回超时错误 | 重试1次 |

### 5.3 性能要求

| 操作 | 响应时间 | 备注 |
|------|----------|------|
| **创建订单** | < 500ms | 包含网络延迟 |
| **取消订单** | < 500ms | 包含网络延迟 |
| **查询订单** | < 300ms | 本地缓存 |
| **查询持仓** | < 300ms | 本地缓存 |
| **查询账户** | < 300ms | 本地缓存 |

---

**版本**: 1.0.0 | **更新日期**: 2026-04-02 | **状态**: ✅ 已完成  
**下一步**: P0-5 多引擎协同器详细设计