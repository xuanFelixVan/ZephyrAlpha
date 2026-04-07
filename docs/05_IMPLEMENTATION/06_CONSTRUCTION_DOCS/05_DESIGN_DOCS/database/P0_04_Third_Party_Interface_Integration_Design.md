---
module_id: P0_04_THIRD_PARTY_INTERFACE_INTEGRATION_DESIGN
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - ﻝﻛﺕﮔﺗﮔ۴ﮒ۲ﻠﮔﻟﺝﻟ۰ﺅﺙﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮒﺅﺙ文档
---

﻿---
module_id: THIRD_PARTY_API_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕﻟﮒﺝﮔﭘﮔﮒﺕ?
responsibility:
  - 系统实施与部署管理与优化维护
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﻝ؛؛ﻛﺕﮔﺗﮔ۴ﮒ۲ﻠﮔﮔﮒ?
applicable_scope: ﮒ۳ﮒﺙﮔﮔ۴ﮒ۲ﻠﮔ?
compliance_level: ﻛﺕﻛﺕﮔﭦﮔﮔﮒ
parent_document: P0-01_Database_Design_Document.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?---


# ﻝ؛؛ﻛﺕﮔﺗﮔ۴ﮒ۲ﻠﮔﻟ؟ﺝﻟ؟۰ﺅﺙﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮒﺅﺙ?

## 核心定位

提供第三方接口集成的详细设计，包含接口对接、数据转换、异常处理等，支持外部系统集成。


> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.0 - ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮒﻝ؛؛ﻛﺕﮔﺗﮔ۴ﮒ۲ﻠﮔﻟ؟ﺝﻟ؟?
> **ﻠﮔﮒﺙﮔ**: vn.py, RQAlpha, Backtrader, QMT, Backtesting.py
> **ﻟ؟ﺝﻟ؟۰ﮒﮒ**: ﮔ۴ﮒ۲ﻝﭨﻛﺕﻙﻠﻠﮒ۷ﮔ۷۰ﮒﺙﻙﮔﺝﻟ۵ﮒﻙﮔﮔ۸ﮒﺎ


## 设计目标

### 主要目标

1. **功能完整性**: 确保文档内容完整，满足使用需求
2. **易用性**: 提高文档可读性，便于快速理解
3. **可维护性**: 文档结构清晰，便于后续维护
4. **一致性**: 确保文档格式和风格统一

### 质量目标

- 文档完整性: 100%
- 格式规范性: 100%
- 内容准确性: 100%


## ﻭ ﮔ۴ﮒ۲ﻠﮔﮔ۵ﻟﺟﺍ

### ﮒﺙﮔﻠﮔﮔﭘﮔ

```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﻝﭨﻛﺕﮒﺙﮔﮔ۴ﮒ۲ﮒﺎ?                            ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ?         EngineInterface (ﻝﭨﻛﺕﮔ۴ﮒ۲)                   ﻗ? ﻗ?
ﻗ? ﻗ? - create_order()    ﮒﮒﭨﭦﻟ؟۱ﮒ                         ﻗ? ﻗ?
ﻗ? ﻗ? - cancel_order()    ﮒﮔﭘﻟ؟۱ﮒ                         ﻗ? ﻗ?
ﻗ? ﻗ? - query_order()     ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ                         ﻗ? ﻗ?
ﻗ? ﻗ? - query_position()  ﮔ۴ﻟﺁ۱ﮔﻛﭨ                         ﻗ? ﻗ?
ﻗ? ﻗ? - query_account()   ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ                         ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
                            ﻗ?ﻠﻠﮒ۷ﮔ۷۰ﮒﺙ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﮒﺙﮔﻠﻠﮒ۷ﮒﺎ                               ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗVnpyAdapterﻗ?ﻗRQAlphaAdapterﻗ?ﻗBacktraderAdapterﻗ?ﻗQMTAdapterﻗ?ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                                             ﻗ?
ﻗ? ﻗBacktestingAdapterﻗ?                                     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                                             ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
                            ﻗ?ﻝ؛؛ﻛﺕﮔﺗﮒﺙﮔ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﻝ؛؛ﻛﺕﮔﺗﮒﺙﮔﮒﺎ                               ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗ?  vn.py  ﻗ?ﻗ? RQAlpha ﻗ?ﻗBacktraderﻗ?ﻗ?  QMT    ﻗ?     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                                             ﻗ?
ﻗ? ﻗBacktesting.pyﻗ?                                         ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                                             ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
```

---

## 1. ﻝﭨﻛﺕﮒﺙﮔﮔ۴ﮒ۲ (EngineInterface)

### 1.1 ﮔ۴ﮒ۲ﮒ؟ﻛﺗ

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

class EngineInterface(ABC):
    """ﻝﭨﻛﺕﮒﺙﮔﮔ۴ﮒ۲"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """ﮒﮒ۶ﮒﮒﺙﮔ?""
        pass
    
    @abstractmethod
    async def connect(self) -> bool:
        """ﻟﺟﮔ۴ﮒﺙﮔ"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
"""ﮔﮒﺙﻟﺟﮔ۴"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """ﮒ۴ﮒﭦﺓﮔ۲ﮔ?""
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
        """ﮒﮒﭨﭦﻟ؟۱ﮒ"""
        pass
    
    @abstractmethod
    async def cancel_order(
        self,
        order_id: str
    ) -> bool:
        """ﮒﮔﭘﻟ؟۱ﮒ"""
        pass
    
    @abstractmethod
    async def query_order(
        self,
        order_id: str
    ) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ"""
        pass
    
    @abstractmethod
    async def query_orders(
        self,
        account_id: int,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮒﻟ۰۷"""
        pass
    
    @abstractmethod
    async def query_position(
        self,
        account_id: int,
        stock_code: str
    ) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﮔﻛﭨ"""
        pass
    
    @abstractmethod
    async def query_positions(
        self,
        account_id: int
    ) -> List[Dict[str, Any]]:
        """ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒﻟ۰۷"""
        pass
    
    @abstractmethod
    async def query_account(
        self,
        account_id: int
    ) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ"""
        pass
    
    @abstractmethod
    async def subscribe_market_data(
        self,
        stock_codes: List[str]
    ) -> bool:
        """ﻟ؟۱ﻠﻟ۰ﮔ"""
        pass
    
    @abstractmethod
    async def unsubscribe_market_data(
        self,
        stock_codes: List[str]
    ) -> bool:
        """ﮒﮔﭘﻟ؟۱ﻠﻟ۰ﮔ"""
        pass
    
    @abstractmethod
    async def get_market_data(
        self,
        stock_code: str
    ) -> Dict[str, Any]:
        """ﻟﺓﮒﻟ۰ﮔﮔﺍﮔ؟"""
        pass
```

---

## 2. vn.pyﮒﺙﮔﻠﻠﮒ?(VnpyAdapter)

### 2.1 ﻠﻠﮒ۷ﮒ؟ﻝ?

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
    """vn.pyﮒﺙﮔﻠﻠﮒ?""
    
    def __init__(self, engine_id: str, config: Dict[str, Any]):
        self.engine_id = engine_id
        self.config = config
        self.event_engine = None
        self.main_engine = None
        self.gateway_name = config.get('gateway', 'CTP')
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """ﮒﮒ۶ﮒvn.pyﮒﺙﮔ"""
        try:
            self.event_engine = EventEngine()
            self.main_engine = MainEngine(self.event_engine)
            
# ﮔﺓﭨﮒﻝﺛﮒﺏ
            if self.gateway_name == 'CTP':
                from vnpy.trader.gateway import CtpGateway
                self.main_engine.add_gateway(CtpGateway)
            
            return True
        except Exception as e:
            print(f"vn.pyﮒﮒ۶ﮒﮒ۳ﺎﻟﺑ? {e}")
            return False
    
    async def connect(self) -> bool:
        """ﻟﺟﮔ۴vn.pyﮒﺙﮔ"""
        try:
            # ﻟﺟﮔ۴ﻝﺛﮒﺏ
            self.main_engine.connect(self.config, self.gateway_name)
            return True
        except Exception as e:
            print(f"vn.pyﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def disconnect(self) -> bool:
"""ﮔﮒﺙﻟﺟﮔ۴"""
        try:
            self.main_engine.close()
            return True
        except Exception as e:
print(f"vn.pyﮔﮒﺙﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """ﮒ۴ﮒﭦﺓﮔ۲ﮔ?""
        try:
            # ﮔ۲ﮔ۴ﮒﺙﮔﻝﭘﮔ?
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
        """ﮒﮒﭨﭦﻟ؟۱ﮒ"""
        try:
            # ﻟﺛ؛ﮔ۱ﮔﺗﮒ
            vn_direction = Direction.LONG if direction == 'buy' else Direction.SHORT
            
            # ﻟﺛ؛ﮔ۱ﻟ؟۱ﮒﻝﺎﭨﮒ
            vn_order_type = OrderType.LIMIT if order_type == 'limit' else OrderType.MARKET
            
            # ﻟﺛ؛ﮔ۱ﻛﭦ۳ﮔﮔ
            vn_exchange = Exchange.SHFE if exchange == 'SH' else Exchange.CZCE
            
            # ﮒﮒﭨﭦﻟ؟۱ﮒﻟﺁﺓﮔﺎ
            req = OrderRequest(
                symbol=stock_code,
                exchange=vn_exchange,
                direction=vn_direction,
                type=vn_order_type,
                price=float(price),
                volume=quantity,
                reference=f"ZEPHYR_{account_id}"
            )
            
            # ﮒﻠﻟ؟۱ﮒ?
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
        """ﮒﮔﭘﻟ؟۱ﮒ"""
        try:
            # ﻟﺓﮒﻟ؟۱ﮒﻛﺟ۰ﮔﺁ
            order = self.main_engine.get_order(order_id)
            
            if not order:
                return False
            
            # ﮒﮒﭨﭦﮒﮔﭘﻟﺁﺓﮔﺎ
            req = CancelRequest(
                orderid=order_id,
                symbol=order.symbol,
                exchange=order.exchange
            )
            
            # ﮒﮔﭘﻟ؟۱ﮒ
            self.main_engine.cancel_order(req, self.gateway_name)
            
            return True
        except Exception as e:
            print(f"ﮒﮔﭘﻟ؟۱ﮒﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def query_order(self, order_id: str) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ"""
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
            print(f"ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮒ۳ﺎﻟﺑ۴: {e}")
            return {}
    
    async def query_orders(
        self,
        account_id: int,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮒﻟ۰۷"""
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
            print(f"ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮒﻟ۰۷ﮒ۳ﺎﻟﺑ۴: {e}")
            return []
    
    async def query_position(
        self,
        account_id: int,
        stock_code: str
    ) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﮔﻛﭨ"""
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
            print(f"ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒ۳ﺎﻟﺑ۴: {e}")
            return {}
    
    async def query_positions(self, account_id: int) -> List[Dict[str, Any]]:
        """ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒﻟ۰۷"""
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
            print(f"ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒﻟ۰۷ﮒ۳ﺎﻟﺑ۴: {e}")
            return []
    
    async def query_account(self, account_id: int) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ"""
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
            print(f"ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮒ۳ﺎﻟﺑ۴: {e}")
            return {}
    
    async def subscribe_market_data(self, stock_codes: List[str]) -> bool:
        """ﻟ؟۱ﻠﻟ۰ﮔ"""
        try:
            for stock_code in stock_codes:
                self.main_engine.subscribe(stock_code, self.gateway_name)
            
            return True
        except Exception as e:
            print(f"ﻟ؟۱ﻠﻟ۰ﮔﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def unsubscribe_market_data(self, stock_codes: List[str]) -> bool:
        """ﮒﮔﭘﻟ؟۱ﻠﻟ۰ﮔ"""
        # vn.pyﮔﻛﺕﮔﺁﮔﮒﮔﭘﻟ؟۱ﻠ
        return True
    
    async def get_market_data(self, stock_code: str) -> Dict[str, Any]:
        """ﻟﺓﮒﻟ۰ﮔﮔﺍﮔ؟"""
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
            print(f"ﻟﺓﮒﻟ۰ﮔﮔﺍﮔ؟ﮒ۳ﺎﻟﺑ۴: {e}")
            return {}
```

---

## 3. RQAlphaﮒﺙﮔﻠﻠﮒ?(RQAlphaAdapter)

### 3.1 ﻠﻠﮒ۷ﮒ؟ﻝ?

```python
from typing import Dict, Any, List, Optional
from decimal import Decimal
import rqalpha as rq
from rqalpha.const import SIDE, POSITION_EFFECT

class RQAlphaAdapter(EngineInterface):
    """RQAlphaﮒﺙﮔﻠﻠﮒ?""
    
    def __init__(self, engine_id: str, config: Dict[str, Any]):
        self.engine_id = engine_id
        self.config = config
        self.env = None
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """ﮒﮒ۶ﮒRQAlphaﮒﺙﮔ"""
        try:
            # ﮒﮒﭨﭦRQAlphaﻝﺁﮒ۱
            self.env = rq.create_env(config)
            return True
        except Exception as e:
            print(f"RQAlphaﮒﮒ۶ﮒﮒ۳ﺎﻟﺑ? {e}")
            return False
    
    async def connect(self) -> bool:
        """ﻟﺟﮔ۴RQAlphaﮒﺙﮔ"""
        try:
            # RQAlphaﻛﺕﻠﻟ۵ﻟﺟﮔ?
            return True
        except Exception as e:
            print(f"RQAlphaﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def disconnect(self) -> bool:
"""ﮔﮒﺙﻟﺟﮔ۴"""
        try:
            if self.env:
                self.env.stop()
            return True
        except Exception as e:
print(f"RQAlphaﮔﮒﺙﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """ﮒ۴ﮒﭦﺓﮔ۲ﮔ?""
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
        """ﮒﮒﭨﭦﻟ؟۱ﮒ"""
        try:
            # ﻟﺛ؛ﮔ۱ﮔﺗﮒ
            side = SIDE.BUY if direction == 'buy' else SIDE.SELL
            
            # ﮒﮒﭨﭦﻟ؟۱ﮒ
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
        """ﮒﮔﭘﻟ؟۱ﮒ"""
        try:
            # RQAlphaﻛﺕﮔﺁﮔﮒﮔﭘﻟ؟۱ﮒ?
            return False
        except Exception as e:
            print(f"ﮒﮔﭘﻟ؟۱ﮒﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def query_order(self, order_id: str) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ"""
        # RQAlphaﻛﺕﮔﺁﮔﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ?
        return {}
    
    async def query_orders(
        self,
        account_id: int,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮒﻟ۰۷"""
        # RQAlphaﻛﺕﮔﺁﮔﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮒﻟ۰?
        return []
    
    async def query_position(
        self,
        account_id: int,
        stock_code: str
    ) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﮔﻛﭨ"""
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
            print(f"ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒ۳ﺎﻟﺑ۴: {e}")
            return {}
    
    async def query_positions(self, account_id: int) -> List[Dict[str, Any]]:
        """ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒﻟ۰۷"""
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
            print(f"ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒﻟ۰۷ﮒ۳ﺎﻟﺑ۴: {e}")
            return []
    
    async def query_account(self, account_id: int) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ"""
        try:
            portfolio = self.env.portfolio
            
            return {
                'total_value': Decimal(str(portfolio.total_value)),
                'cash': Decimal(str(portfolio.cash)),
                'market_value': Decimal(str(portfolio.market_value)),
                'pnl': Decimal(str(portfolio.pnl))
            }
        except Exception as e:
            print(f"ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮒ۳ﺎﻟﺑ۴: {e}")
            return {}
    
    async def subscribe_market_data(self, stock_codes: List[str]) -> bool:
        """ﻟ؟۱ﻠﻟ۰ﮔ"""
        # RQAlphaﻟ۹ﮒ۷ﻟ؟۱ﻠ
        return True
    
    async def unsubscribe_market_data(self, stock_codes: List[str]) -> bool:
        """ﮒﮔﭘﻟ؟۱ﻠﻟ۰ﮔ"""
        return True
    
    async def get_market_data(self, stock_code: str) -> Dict[str, Any]:
        """ﻟﺓﮒﻟ۰ﮔﮔﺍﮔ؟"""
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
            print(f"ﻟﺓﮒﻟ۰ﮔﮔﺍﮔ؟ﮒ۳ﺎﻟﺑ۴: {e}")
            return {}
```

---

## 4. ﮒﺙﮔﻝ؟۰ﻝﮔﮒ۰ (EngineManagerService)

### 4.1 ﮔﮒ۰ﮒ؟ﻝﺍ

```python
from typing import Dict, Any, List, Optional
from enum import Enum

class EngineType(Enum):
    """ﮒﺙﮔﻝﺎﭨﮒ"""
    VNPY = 'vnpy'
    RQALPHA = 'rqalpha'
    BACKTRADER = 'backtrader'
    QMT = 'qmt'
    BACKTESTING = 'backtesting'

class EngineManagerService:
    """ﮒﺙﮔﻝ؟۰ﻝﮔﮒ۰"""
    
    def __init__(self):
        self.engines: Dict[str, EngineInterface] = {}
        self.engine_configs: Dict[str, Dict[str, Any]] = {}
    
    async def register_engine(
        self,
        engine_id: str,
        engine_type: EngineType,
        config: Dict[str, Any]
    ) -> bool:
        """ﮔﺏ۷ﮒﮒﺙﮔ"""
        try:
            # ﮒﮒﭨﭦﮒﺙﮔﻠﻠﮒ?
            if engine_type == EngineType.VNPY:
                adapter = VnpyAdapter(engine_id, config)
            elif engine_type == EngineType.RQALPHA:
                adapter = RQAlphaAdapter(engine_id, config)
            else:
                raise ValueError(f"ﻛﺕﮔﺁﮔﻝﮒﺙﮔﻝﺎﭨﮒ: {engine_type}")
            
            # ﮒﮒ۶ﮒﮒﺙﮔ?
            success = await adapter.initialize(config)
            
            if success:
                self.engines[engine_id] = adapter
                self.engine_configs[engine_id] = config
                return True
            
            return False
        except Exception as e:
            print(f"ﮔﺏ۷ﮒﮒﺙﮔﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def connect_engine(self, engine_id: str) -> bool:
        """ﻟﺟﮔ۴ﮒﺙﮔ"""
        try:
            engine = self.engines.get(engine_id)
            
            if not engine:
                return False
            
            return await engine.connect()
        except Exception as e:
            print(f"ﻟﺟﮔ۴ﮒﺙﮔﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def disconnect_engine(self, engine_id: str) -> bool:
"""ﮔﮒﺙﮒﺙﮔﻟﺟﮔ۴"""
        try:
            engine = self.engines.get(engine_id)
            
            if not engine:
                return False
            
            return await engine.disconnect()
        except Exception as e:
print(f"ﮔﮒﺙﮒﺙﮔﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def health_check_engine(self, engine_id: str) -> Dict[str, Any]:
        """ﮒ۴ﮒﭦﺓﮔ۲ﮔ۴ﮒﺙﮔ?""
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
        """ﮒ۴ﮒﭦﺓﮔ۲ﮔ۴ﮔﮔﮒﺙﮔ?""
        results = []
        
        for engine_id in self.engines:
            result = await self.health_check_engine(engine_id)
            results.append(result)
        
        return results
    
    def get_engine(self, engine_id: str) -> Optional[EngineInterface]:
        """ﻟﺓﮒﮒﺙﮔ"""
        return self.engines.get(engine_id)
    
    def get_all_engines(self) -> List[str]:
        """ﻟﺓﮒﮔﮔﮒﺙﮔID"""
        return list(self.engines.keys())
```

---

## 5. ﮔ۴ﮒ۲ﻠﮔﻟ۶ﻟ

### 5.1 ﮔﺍﮔ؟ﮔﺙﮒﺙﻟﺛ؛ﮔ۱

| ﮒﮔ؟ﭖ | ﻝﺏﭨﻝﭨﮔﺙﮒﺙ | vn.pyﮔﺙﮒﺙ | RQAlphaﮔﺙﮒﺙ |
|------|----------|-----------|-------------|
| **ﻛﭦ۳ﮔﮔﺗﮒ** | buy/sell | LONG/SHORT | BUY/SELL |
| **ﻟ؟۱ﮒﻝﺎﭨﮒ** | limit/market | LIMIT/MARKET | LIMIT/MARKET |
| **ﻛﭦ۳ﮔﮔ** | SH/SZ | SHFE/SZSE | SH/SZ |
| **ﻟ؟۱ﮒﻝﭘﮔ?* | pending/submitted/filled | NOTTRADED/TRADED | pending/filled |

### 5.2 ﻠﻟﺁﺁﮒ۳ﻝ

| ﻠﻟﺁﺁﻝﺎﭨﮒ | ﮒ۳ﻝﮔﺗﮒﺙ | ﻠﻟﺁﻝﻝ۴ |
|----------|----------|----------|
| **ﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴** | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻠﻟﺁ?| ﻠﻟﺁ3ﮔ؛۰ﺅﺙﻠﺑﻠ5ﻝ۶?|
| **ﻟ؟۱ﮒﮒ۳ﺎﻟﺑ۴** | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻠﻟﺁ?| ﻛﺕﻠﻟﺁ?|
| **ﮔ۴ﻟﺁ۱ﮒ۳ﺎﻟﺑ۴** | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻝ۸ﭦﻝﭨﮔ | ﻠﻟﺁ2ﮔ؛۰ﺅﺙﻠﺑﻠ2ﻝ۶?|
| **ﻟﭘﮔﭘ** | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻟﭘﮔﭘﻠﻟﺁ?| ﻠﻟﺁ1ﮔ؛?|

### 5.3 ﮔ۶ﻟﺛﻟ۵ﮔﺎ

| ﮔﻛﺛ | ﮒﮒﭦﮔﭘﻠﺑ | ﮒ۳ﮔﺏ۷ |
|------|----------|------|
| **ﮒﮒﭨﭦﻟ؟۱ﮒ** | < 500ms | ﮒﮒ،ﻝﺛﻝﭨﮒﭨﭘﻟﺟ |
| **ﮒﮔﭘﻟ؟۱ﮒ** | < 500ms | ﮒﮒ،ﻝﺛﻝﭨﮒﭨﭘﻟﺟ |
| **ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ** | < 300ms | ﮔ؛ﮒﺍﻝﺙﮒ |
| **ﮔ۴ﻟﺁ۱ﮔﻛﭨ** | < 300ms | ﮔ؛ﮒﺍﻝﺙﮒ |
| **ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ** | < 300ms | ﮔ؛ﮒﺍﻝﺙﮒ |

---

**ﻝﮔ؛**: 1.0.0 | **ﮔﺑﮔﺍﮔ۴ﮔ**: 2026-04-02 | **ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ? 
**ﻛﺕﻛﺕﮔ?*: P0-5 ﮒ۳ﮒﺙﮔﮒﮒﮒ۷ﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰
