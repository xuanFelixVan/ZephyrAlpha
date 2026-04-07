---
module_id: THIRD_PARTY_API_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﻟﮒﺝﮔﭘﮔﮒﺕ?
responsibility:
  - 实施指南、部署文档
  - 组合优化
  - 交易执行
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﻝ؛؛ﻛﺕﮔﺗﮔ۴ﮒ۲ﻠﮔﮔ ﮒ?
applicable_scope: ﮒ۳ﮒﺙﮔﮔ۴ﮒ۲ﻠﮔ?
compliance_level: ﻛﺕﻛﺕﮔﭦﮔﮔ ﮒ
parent_document: P0-01_Database_Design_Document.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?---


# ﻝ؛؛ﻛﺕﮔﺗﮔ۴ﮒ۲ﻠﮔﻟ؟ﺝﻟ؟۰ﺅﺙﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒﺅﺙ?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.0 - ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒﻝ؛؛ﻛﺕﮔﺗﮔ۴ﮒ۲ﻠﮔﻟ؟ﺝﻟ؟?
> **ﻠﮔﮒﺙﮔ**: vn.py, RQAlpha, Backtrader, QMT, Backtesting.py
> **ﻟ؟ﺝﻟ؟۰ﮒﮒ**: ﮔ۴ﮒ۲ﻝﭨﻛﺕﻙﻠﻠﮒ۷ﮔ۷۰ﮒﺙﻙﮔﺝﻟ۵ﮒﻙﮔﮔ۸ﮒﺎ

## ﻭ ﮔ۴ﮒ۲ﻠﮔﮔ۵ﻟﺟﺍ

### ﮒﺙﮔﻠﮔﮔﭘﮔ

```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﻝﭨﻛﺕﮒﺙﮔﮔ۴ﮒ۲ﮒﺎ?                            ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ?         EngineInterface (ﻝﭨﻛﺕﮔ۴ﮒ۲)                   ﻗ? ﻗ?
ﻗ? ﻗ? - create_order()    ﮒﮒﭨﭦﻟ؟۱ﮒ                         ﻗ? ﻗ?
ﻗ? ﻗ? - cancel_order()    ﮒﮔﭘﻟ؟۱ﮒ                         ﻗ? ﻗ?
ﻗ? ﻗ? - query_order()     ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ                         ﻗ? ﻗ?
ﻗ? ﻗ? - query_position()  ﮔ۴ﻟﺁ۱ﮔﻛﭨ                         ﻗ? ﻗ?
ﻗ? ﻗ? - query_account()   ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ                         ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
                            ﻗ?ﻠﻠﮒ۷ﮔ۷۰ﮒﺙ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﮒﺙﮔﻠﻠﮒ۷ﮒﺎ                               ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗVnpyAdapterﻗ?ﻗRQAlphaAdapterﻗ?ﻗBacktraderAdapterﻗ?ﻗQMTAdapterﻗ?ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                                             ﻗ?
ﻗ? ﻗBacktestingAdapterﻗ?                                     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                                             ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
                            ﻗ?ﻝ؛؛ﻛﺕﮔﺗﮒﺙﮔ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﻝ؛؛ﻛﺕﮔﺗﮒﺙﮔﮒﺎ                               ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗ?  vn.py  ﻗ?ﻗ? RQAlpha ﻗ?ﻗBacktraderﻗ?ﻗ?  QMT    ﻗ?     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                                             ﻗ?
ﻗ? ﻗBacktesting.pyﻗ?                                         ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?                                             ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
```

---

## 1. ﻝﭨﻛﺕﮒﺙﮔﮔ۴ﮒ۲ (EngineInterface)

### 1.1 ﮔ۴ﮒ۲ﮒ؟ﻛﺗ

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

class EngineInterface(ABC):
    """ﻝﭨﻛﺕﮒﺙﮔﮔ۴ﮒ۲"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """ﮒﮒ۶ﮒﮒﺙﮔ?""
        pass
    
    @abstractmethod
    async def connect(self) -> bool:
        """ﻟﺟﮔ۴ﮒﺙﮔ"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """ﮔ­ﮒﺙﻟﺟﮔ۴"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """ﮒ۴ﮒﭦﺓﮔ۲ﮔ?""
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
        """ﮒﮒﭨﭦﻟ؟۱ﮒ"""
        pass
    
    @abstractmethod
    async def cancel_order(
        self,
        order_id: str
    ) -> bool:
        """ﮒﮔﭘﻟ؟۱ﮒ"""
        pass
    
    @abstractmethod
    async def query_order(
        self,
        order_id: str
    ) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ"""
        pass
    
    @abstractmethod
    async def query_orders(
        self,
        account_id: int,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮒﻟ۰۷"""
        pass
    
    @abstractmethod
    async def query_position(
        self,
        account_id: int,
        stock_code: str
    ) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﮔﻛﭨ"""
        pass
    
    @abstractmethod
    async def query_positions(
        self,
        account_id: int
    ) -> List[Dict[str, Any]]:
        """ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒﻟ۰۷"""
        pass
    
    @abstractmethod
    async def query_account(
        self,
        account_id: int
    ) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ"""
        pass
    
    @abstractmethod
    async def subscribe_market_data(
        self,
        stock_codes: List[str]
    ) -> bool:
        """ﻟ؟۱ﻠﻟ۰ﮔ"""
        pass
    
    @abstractmethod
    async def unsubscribe_market_data(
        self,
        stock_codes: List[str]
    ) -> bool:
        """ﮒﮔﭘﻟ؟۱ﻠﻟ۰ﮔ"""
        pass
    
    @abstractmethod
    async def get_market_data(
        self,
        stock_code: str
    ) -> Dict[str, Any]:
        """ﻟﺓﮒﻟ۰ﮔﮔﺍﮔ؟"""
        pass
```

---

## 2. vn.pyﮒﺙﮔﻠﻠﮒ?(VnpyAdapter)

### 2.1 ﻠﻠﮒ۷ﮒ؟ﻝ?

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
    """vn.pyﮒﺙﮔﻠﻠﮒ?""
    
    def __init__(self, engine_id: str, config: Dict[str, Any]):
        self.engine_id = engine_id
        self.config = config
        self.event_engine = None
        self.main_engine = None
        self.gateway_name = config.get('gateway', 'CTP')
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """ﮒﮒ۶ﮒvn.pyﮒﺙﮔ"""
        try:
            self.event_engine = EventEngine()
            self.main_engine = MainEngine(self.event_engine)
            
            # ﮔﺓﭨﮒ ﻝﺛﮒﺏ
            if self.gateway_name == 'CTP':
                from vnpy.trader.gateway import CtpGateway
                self.main_engine.add_gateway(CtpGateway)
            
            return True
        except Exception as e:
            print(f"vn.pyﮒﮒ۶ﮒﮒ۳ﺎﻟﺑ? {e}")
            return False
    
    async def connect(self) -> bool:
        """ﻟﺟﮔ۴vn.pyﮒﺙﮔ"""
        try:
            # ﻟﺟﮔ۴ﻝﺛﮒﺏ
            self.main_engine.connect(self.config, self.gateway_name)
            return True
        except Exception as e:
            print(f"vn.pyﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """ﮔ­ﮒﺙﻟﺟﮔ۴"""
        try:
            self.main_engine.close()
            return True
        except Exception as e:
            print(f"vn.pyﮔ­ﮒﺙﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """ﮒ۴ﮒﭦﺓﮔ۲ﮔ?""
        try:
            # ﮔ۲ﮔ۴ﮒﺙﮔﻝﭘﮔ?
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
        """ﮒﮒﭨﭦﻟ؟۱ﮒ"""
        try:
            # ﻟﺛ؛ﮔ۱ﮔﺗﮒ
            vn_direction = Direction.LONG if direction == 'buy' else Direction.SHORT
            
            # ﻟﺛ؛ﮔ۱ﻟ؟۱ﮒﻝﺎﭨﮒ
            vn_order_type = OrderType.LIMIT if order_type == 'limit' else OrderType.MARKET
            
            # ﻟﺛ؛ﮔ۱ﻛﭦ۳ﮔﮔ
            vn_exchange = Exchange.SHFE if exchange == 'SH' else Exchange.CZCE
            
            # ﮒﮒﭨﭦﻟ؟۱ﮒﻟﺁﺓﮔﺎ
            req = OrderRequest(
                symbol=stock_code,
                exchange=vn_exchange,
                direction=vn_direction,
                type=vn_order_type,
                price=float(price),
                volume=quantity,
                reference=f"ZEPHYR_{account_id}"
            )
            
            # ﮒﻠﻟ؟۱ﮒ?
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
        """ﮒﮔﭘﻟ؟۱ﮒ"""
        try:
            # ﻟﺓﮒﻟ؟۱ﮒﻛﺟ۰ﮔﺁ
            order = self.main_engine.get_order(order_id)
            
            if not order:
                return False
            
            # ﮒﮒﭨﭦﮒﮔﭘﻟﺁﺓﮔﺎ
            req = CancelRequest(
                orderid=order_id,
                symbol=order.symbol,
                exchange=order.exchange
            )
            
            # ﮒﮔﭘﻟ؟۱ﮒ
            self.main_engine.cancel_order(req, self.gateway_name)
            
            return True
        except Exception as e:
            print(f"ﮒﮔﭘﻟ؟۱ﮒﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def query_order(self, order_id: str) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ"""
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
            print(f"ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮒ۳ﺎﻟﺑ۴: {e}")
            return {}
    
    async def query_orders(
        self,
        account_id: int,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮒﻟ۰۷"""
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
            print(f"ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮒﻟ۰۷ﮒ۳ﺎﻟﺑ۴: {e}")
            return []
    
    async def query_position(
        self,
        account_id: int,
        stock_code: str
    ) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﮔﻛﭨ"""
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
            print(f"ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒ۳ﺎﻟﺑ۴: {e}")
            return {}
    
    async def query_positions(self, account_id: int) -> List[Dict[str, Any]]:
        """ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒﻟ۰۷"""
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
            print(f"ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒﻟ۰۷ﮒ۳ﺎﻟﺑ۴: {e}")
            return []
    
    async def query_account(self, account_id: int) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ"""
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
            print(f"ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮒ۳ﺎﻟﺑ۴: {e}")
            return {}
    
    async def subscribe_market_data(self, stock_codes: List[str]) -> bool:
        """ﻟ؟۱ﻠﻟ۰ﮔ"""
        try:
            for stock_code in stock_codes:
                self.main_engine.subscribe(stock_code, self.gateway_name)
            
            return True
        except Exception as e:
            print(f"ﻟ؟۱ﻠﻟ۰ﮔﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def unsubscribe_market_data(self, stock_codes: List[str]) -> bool:
        """ﮒﮔﭘﻟ؟۱ﻠﻟ۰ﮔ"""
        # vn.pyﮔﻛﺕﮔﺁﮔﮒﮔﭘﻟ؟۱ﻠ
        return True
    
    async def get_market_data(self, stock_code: str) -> Dict[str, Any]:
        """ﻟﺓﮒﻟ۰ﮔﮔﺍﮔ؟"""
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
            print(f"ﻟﺓﮒﻟ۰ﮔﮔﺍﮔ؟ﮒ۳ﺎﻟﺑ۴: {e}")
            return {}
```

---

## 3. RQAlphaﮒﺙﮔﻠﻠﮒ?(RQAlphaAdapter)

### 3.1 ﻠﻠﮒ۷ﮒ؟ﻝ?

```python
from typing import Dict, Any, List, Optional
from decimal import Decimal
import rqalpha as rq
from rqalpha.const import SIDE, POSITION_EFFECT

class RQAlphaAdapter(EngineInterface):
    """RQAlphaﮒﺙﮔﻠﻠﮒ?""
    
    def __init__(self, engine_id: str, config: Dict[str, Any]):
        self.engine_id = engine_id
        self.config = config
        self.env = None
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """ﮒﮒ۶ﮒRQAlphaﮒﺙﮔ"""
        try:
            # ﮒﮒﭨﭦRQAlphaﻝﺁﮒ۱
            self.env = rq.create_env(config)
            return True
        except Exception as e:
            print(f"RQAlphaﮒﮒ۶ﮒﮒ۳ﺎﻟﺑ? {e}")
            return False
    
    async def connect(self) -> bool:
        """ﻟﺟﮔ۴RQAlphaﮒﺙﮔ"""
        try:
            # RQAlphaﻛﺕﻠﻟ۵ﻟﺟﮔ?
            return True
        except Exception as e:
            print(f"RQAlphaﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """ﮔ­ﮒﺙﻟﺟﮔ۴"""
        try:
            if self.env:
                self.env.stop()
            return True
        except Exception as e:
            print(f"RQAlphaﮔ­ﮒﺙﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """ﮒ۴ﮒﭦﺓﮔ۲ﮔ?""
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
        """ﮒﮒﭨﭦﻟ؟۱ﮒ"""
        try:
            # ﻟﺛ؛ﮔ۱ﮔﺗﮒ
            side = SIDE.BUY if direction == 'buy' else SIDE.SELL
            
            # ﮒﮒﭨﭦﻟ؟۱ﮒ
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
        """ﮒﮔﭘﻟ؟۱ﮒ"""
        try:
            # RQAlphaﻛﺕﮔﺁﮔﮒﮔﭘﻟ؟۱ﮒ?
            return False
        except Exception as e:
            print(f"ﮒﮔﭘﻟ؟۱ﮒﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def query_order(self, order_id: str) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ"""
        # RQAlphaﻛﺕﮔﺁﮔﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ?
        return {}
    
    async def query_orders(
        self,
        account_id: int,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮒﻟ۰۷"""
        # RQAlphaﻛﺕﮔﺁﮔﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮒﻟ۰?
        return []
    
    async def query_position(
        self,
        account_id: int,
        stock_code: str
    ) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﮔﻛﭨ"""
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
            print(f"ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒ۳ﺎﻟﺑ۴: {e}")
            return {}
    
    async def query_positions(self, account_id: int) -> List[Dict[str, Any]]:
        """ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒﻟ۰۷"""
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
            print(f"ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒﻟ۰۷ﮒ۳ﺎﻟﺑ۴: {e}")
            return []
    
    async def query_account(self, account_id: int) -> Dict[str, Any]:
        """ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ"""
        try:
            portfolio = self.env.portfolio
            
            return {
                'total_value': Decimal(str(portfolio.total_value)),
                'cash': Decimal(str(portfolio.cash)),
                'market_value': Decimal(str(portfolio.market_value)),
                'pnl': Decimal(str(portfolio.pnl))
            }
        except Exception as e:
            print(f"ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮒ۳ﺎﻟﺑ۴: {e}")
            return {}
    
    async def subscribe_market_data(self, stock_codes: List[str]) -> bool:
        """ﻟ؟۱ﻠﻟ۰ﮔ"""
        # RQAlphaﻟ۹ﮒ۷ﻟ؟۱ﻠ
        return True
    
    async def unsubscribe_market_data(self, stock_codes: List[str]) -> bool:
        """ﮒﮔﭘﻟ؟۱ﻠﻟ۰ﮔ"""
        return True
    
    async def get_market_data(self, stock_code: str) -> Dict[str, Any]:
        """ﻟﺓﮒﻟ۰ﮔﮔﺍﮔ؟"""
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
            print(f"ﻟﺓﮒﻟ۰ﮔﮔﺍﮔ؟ﮒ۳ﺎﻟﺑ۴: {e}")
            return {}
```

---

## 4. ﮒﺙﮔﻝ؟۰ﻝﮔﮒ۰ (EngineManagerService)

### 4.1 ﮔﮒ۰ﮒ؟ﻝﺍ

```python
from typing import Dict, Any, List, Optional
from enum import Enum

class EngineType(Enum):
    """ﮒﺙﮔﻝﺎﭨﮒ"""
    VNPY = 'vnpy'
    RQALPHA = 'rqalpha'
    BACKTRADER = 'backtrader'
    QMT = 'qmt'
    BACKTESTING = 'backtesting'

class EngineManagerService:
    """ﮒﺙﮔﻝ؟۰ﻝﮔﮒ۰"""
    
    def __init__(self):
        self.engines: Dict[str, EngineInterface] = {}
        self.engine_configs: Dict[str, Dict[str, Any]] = {}
    
    async def register_engine(
        self,
        engine_id: str,
        engine_type: EngineType,
        config: Dict[str, Any]
    ) -> bool:
        """ﮔﺏ۷ﮒﮒﺙﮔ"""
        try:
            # ﮒﮒﭨﭦﮒﺙﮔﻠﻠﮒ?
            if engine_type == EngineType.VNPY:
                adapter = VnpyAdapter(engine_id, config)
            elif engine_type == EngineType.RQALPHA:
                adapter = RQAlphaAdapter(engine_id, config)
            else:
                raise ValueError(f"ﻛﺕﮔﺁﮔﻝﮒﺙﮔﻝﺎﭨﮒ: {engine_type}")
            
            # ﮒﮒ۶ﮒﮒﺙﮔ?
            success = await adapter.initialize(config)
            
            if success:
                self.engines[engine_id] = adapter
                self.engine_configs[engine_id] = config
                return True
            
            return False
        except Exception as e:
            print(f"ﮔﺏ۷ﮒﮒﺙﮔﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def connect_engine(self, engine_id: str) -> bool:
        """ﻟﺟﮔ۴ﮒﺙﮔ"""
        try:
            engine = self.engines.get(engine_id)
            
            if not engine:
                return False
            
            return await engine.connect()
        except Exception as e:
            print(f"ﻟﺟﮔ۴ﮒﺙﮔﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def disconnect_engine(self, engine_id: str) -> bool:
        """ﮔ­ﮒﺙﮒﺙﮔﻟﺟﮔ۴"""
        try:
            engine = self.engines.get(engine_id)
            
            if not engine:
                return False
            
            return await engine.disconnect()
        except Exception as e:
            print(f"ﮔ­ﮒﺙﮒﺙﮔﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴: {e}")
            return False
    
    async def health_check_engine(self, engine_id: str) -> Dict[str, Any]:
        """ﮒ۴ﮒﭦﺓﮔ۲ﮔ۴ﮒﺙﮔ?""
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
        """ﮒ۴ﮒﭦﺓﮔ۲ﮔ۴ﮔﮔﮒﺙﮔ?""
        results = []
        
        for engine_id in self.engines:
            result = await self.health_check_engine(engine_id)
            results.append(result)
        
        return results
    
    def get_engine(self, engine_id: str) -> Optional[EngineInterface]:
        """ﻟﺓﮒﮒﺙﮔ"""
        return self.engines.get(engine_id)
    
    def get_all_engines(self) -> List[str]:
        """ﻟﺓﮒﮔﮔﮒﺙﮔID"""
        return list(self.engines.keys())
```

---

## 5. ﮔ۴ﮒ۲ﻠﮔﻟ۶ﻟ

### 5.1 ﮔﺍﮔ؟ﮔ ﺙﮒﺙﻟﺛ؛ﮔ۱

| ﮒ­ﮔ؟ﭖ | ﻝﺏﭨﻝﭨﮔ ﺙﮒﺙ | vn.pyﮔ ﺙﮒﺙ | RQAlphaﮔ ﺙﮒﺙ |
|------|----------|-----------|-------------|
| **ﻛﭦ۳ﮔﮔﺗﮒ** | buy/sell | LONG/SHORT | BUY/SELL |
| **ﻟ؟۱ﮒﻝﺎﭨﮒ** | limit/market | LIMIT/MARKET | LIMIT/MARKET |
| **ﻛﭦ۳ﮔﮔ** | SH/SZ | SHFE/SZSE | SH/SZ |
| **ﻟ؟۱ﮒﻝﭘﮔ?* | pending/submitted/filled | NOTTRADED/TRADED | pending/filled |

### 5.2 ﻠﻟﺁﺁﮒ۳ﻝ

| ﻠﻟﺁﺁﻝﺎﭨﮒ | ﮒ۳ﻝﮔﺗﮒﺙ | ﻠﻟﺁﻝ­ﻝ۴ |
|----------|----------|----------|
| **ﻟﺟﮔ۴ﮒ۳ﺎﻟﺑ۴** | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻠﻟﺁ?| ﻠﻟﺁ3ﮔ؛۰ﺅﺙﻠﺑﻠ5ﻝ۶?|
| **ﻟ؟۱ﮒﮒ۳ﺎﻟﺑ۴** | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻠﻟﺁ?| ﻛﺕﻠﻟﺁ?|
| **ﮔ۴ﻟﺁ۱ﮒ۳ﺎﻟﺑ۴** | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻝ۸ﭦﻝﭨﮔ | ﻠﻟﺁ2ﮔ؛۰ﺅﺙﻠﺑﻠ2ﻝ۶?|
| **ﻟﭘﮔﭘ** | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻟﭘﮔﭘﻠﻟﺁ?| ﻠﻟﺁ1ﮔ؛?|

### 5.3 ﮔ۶ﻟﺛﻟ۵ﮔﺎ

| ﮔﻛﺛ | ﮒﮒﭦﮔﭘﻠﺑ | ﮒ۳ﮔﺏ۷ |
|------|----------|------|
| **ﮒﮒﭨﭦﻟ؟۱ﮒ** | < 500ms | ﮒﮒ،ﻝﺛﻝﭨﮒﭨﭘﻟﺟ |
| **ﮒﮔﭘﻟ؟۱ﮒ** | < 500ms | ﮒﮒ،ﻝﺛﻝﭨﮒﭨﭘﻟﺟ |
| **ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ** | < 300ms | ﮔ؛ﮒﺍﻝﺙﮒ­ |
| **ﮔ۴ﻟﺁ۱ﮔﻛﭨ** | < 300ms | ﮔ؛ﮒﺍﻝﺙﮒ­ |
| **ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ** | < 300ms | ﮔ؛ﮒﺍﻝﺙﮒ­ |

---

**ﻝﮔ؛**: 1.0.0 | **ﮔﺑﮔﺍﮔ۴ﮔ**: 2026-04-02 | **ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ? 
**ﻛﺕﻛﺕﮔ­?*: P0-5 ﮒ۳ﮒﺙﮔﮒﮒﮒ۷ﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰