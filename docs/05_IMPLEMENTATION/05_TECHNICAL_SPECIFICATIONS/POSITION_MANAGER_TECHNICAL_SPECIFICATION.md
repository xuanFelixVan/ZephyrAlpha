---
module_id: POSITION_MANAGER_SPEC_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟
responsibility:
  - 扩展功能、辅助模块
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵
applicable_scope: Layer 5 ﻝ­ﻝ۴ﮔ۶ﻟ۰?| ﻛﺕﮒ۰ﮔﭘﮔ: ﻛﺕﻝﭦ۶ﮔﭘﻠﺑﮔ۰ﮔﭘﻟﮒﮔﭘﮔ
compliance_level: ﻛﺕﻛﺕﮔ ﮒ
parent_document: ../INDEX.md
implementation_status: ﻟﺟﻟ۰?
---
---


# PositionManagerﮔﻛﭨﻝ؟۰ﻝﮒ۷ﮔ۷۰ﮒﮔﮔﺁﻟ۶ﮔ ﺙﻛﺗ۵
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.3 - PositionManagerﮔﻛﭨﻝ؟۰ﻝﮒ۷ﮔ۷۰ﮒﻟﺁ۵ﻝﭨﮔﮔﺁﻟ؟ﺝ?
> **ﮔ۷۰ﮒID**: `POSITION_MANAGER_001`
> **ﻝﮔ؛**: v1.0.0
> **ﻝ?*: ?ﮔ­۲ﮒﺙ


## 1. ﮔ۵ﻟﺟﺍ

### 1.1 ﻟ؟ﺝﻟ؟۰ﻟﮔﺁﻛﺕﻛﺕﮒ۰ﻝ؟?
- **ﻛﺕﮒ۰ﻠ?*: ﻝﺏﭨﻝﭨﻠﻟ۵ﻝﭨﻛﺕﻝﮔﻛﭨﻝ؟۰ﻝﮒ۷ﻟﺟﻟ۰ﮔﻛﭨﻟ؟۰ﻝ؟ﮒﻝ؟۰?
- **ﮔﮔﺁﻝ?*: 
  - ﮔﻛﭨﻟ؟۰ﻝ؟ﮒ۳ﮔﺅﺙﮔﻛﭨﻟ؟۰ﻝ؟ﮔﭘﮒﮔﮔ؛ﻙﮒﺕﮒﺙﻙﻝﻛﭦﻝ­ﮒ۳ﻛﺕ۹ﻝﭨﺑﮒﭦ۵
  - ﮔﻛﭨﮔﺑﮔﺍﻠ۱ﻝﺗﺅﺙﻛﭦ۳ﮔﻠ۱ﻝﺗﮒﺁﺙﻟﺑﮔﻛﭨﮔﺑﮔﺍﻠ۱?
  - ﮔﻛﭨﮔ۴ﻟﺁ۱ﮒ۳ﮔ ﺓﺅﺙﻠﻟ۵ﮔﺁﮔﮒ۳ﻝ۶ﮔﻛﭨﮔ۴ﻟﺁ۱ﮔﺗ?
  - ﻠ۲ﻠ۸ﮔ۶ﮒﭘﻛﺕ۴ﮔ ﺙﺅﺙﮔﻛﭨﻠﻟ۵ﻛﺕ۴ﮔ ﺙﻝﻠ۲ﻠ۸ﮔ۶ﮒﭘ
- **ﻠ۱ﮔﻛﭨ?*: 
  - ﮒﭨﭦﻝ،ﻝﭨﻛﺕﻝﮔﻛﭨﻟ؟۰ﻝ؟ﮔﭦ?
  - ﮔﻛﺝﻠ،ﮔﻝﮔﻛﭨﮔﺑﮔﺍﮔﭦ?
  - ﮔﺁﮔﮒ۳ﻝ۶ﮔﻛﭨﮔ۴ﻟﺁ۱ﮔﺗﮒﺙ
  - ﮒ؟ﻝﺍﻛﺕ۴ﮔ ﺙﻝﮔﻛﭨﻠ۲ﻠ۸ﮔ۶?

### 1.2 ﮔﮔﺁﮒ؟ﻛﺛﻛﺕﮔﭘﮔﮒﺎﮒﺛ?
- **Layerﮒ؟ﻛﺛ**: Layer 5 - ﻝ­ﻝ۴ﮔ۶ﻟ۰?(ﻝ؛۵ﮒARCHITECTURE.mdﮒ؟ﻛﺗ)
- **ﮔ۷۰ﮒﻝﺎﭨﮒ،**: ﮔ ﺕﮒﺟﮔﻛﭨﻝ؟۰ﻝﮔ۷۰ﮒ
- **ﮔﭘﮔﻟ۶ﻟﺎ**: Layer 5ﻝ­ﻝ۴ﮔ۶ﻟ۰ﮔ ﺕﮒﺟﺅﺙﻟﺑﻟﺑ۲ﮔﻛﭨﻟ؟۰ﻝ؟ﮒﻝ؟۰ﻝ

### 1.3 ﻝﮔ؛ﻛﺟ۰ﮔﺁ
| ﻝﮔ؛ | ﮔ۴ﮔ | ﻛﺛ?| ﮒﮔﺑﻟﺁﺑﮔ | ﻝ?|
|------|------|------|----------|------|
| v1.0.0 | 2026-04-02 | ﻠ۵ﮒﺕ­ﮔﮔﺁﻟﺁﮒ؟۰ﮒ؟ | ﮒﮒ۶ﻝﮔ؛ | Active |

---

## 2. ﻟﺁ۵ﻝﭨﮔﭘﮔﻟ؟ﺝﻟ؟۰

### 2.1 ﻝﺏﭨﻝﭨﮔﭘﮔ?
```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
?                   Layer 5: ﻝ­ﻝ۴ﮔ۶ﻟ۰?                      ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
?                                                            ?
? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ?
? ?       PositionManager (ﮔﻛﭨﻝ؟۰ﻝﮒ۷ﻛﺕﭨﮔ۷۰ﮒ)              ? ?
? ? - ﮔﻛﭨﻟ؟۰ﻝ؟                                            ? ?
? ? - ﮔﻛﭨﮔﺑﮔﺍ                                            ? ?
? ? - ﮔﻛﭨﮔ۴ﻟﺁ۱                                            ? ?
? ? - ﻠ۲ﻠ۸ﮔ۶ﮒﭘ                                            ? ?
? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ?
?                          ?                                 ?
? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ?
? ?         ﮔ ﺕﮒﺟﻝﭨﻛﭨﭘ                                      ? ?
? ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ? ?
? ? ﻗPositionCalc ?ﻗPositionUpdt ?ﻗPositionQuery? ? ?
? ? ﻗﮔﻛﭨﻟ؟۰ﻝ؟ﮒ۷    ? ﻗﮔﻛﭨﮔﺑﮔﺍﮒ۷   ? ﻗﮔﻛﭨﮔ۴ﻟﺁ۱ﮒ۷   ? ? ?
? ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ? ?
? ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ? ?
? ? ﻗRiskControl ?ﻗPositionRepo ?ﻗPositionCache? ? ?
? ? ﻗﻠ۲ﻠ۸ﮔ۶ﮒﭘﮒ۷    ? ﻗﮔﻛﭨﻛﭨ?    ? ﻗﮔﻛﭨﻝﺙ?    ? ? ?
? ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ? ?
? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ?
?                          ?                                 ?
? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ?
? ?         ﮔﺍﮔ؟ﮒ­ﮒ۷?                                  ? ?
? ? - PostgreSQL (ﮔﻛﺗﮒﮒ­?                           ? ?
? ? - Redis (ﻝﺙﮒ­)                                      ? ?
? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ?
?                                                            ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
```

### 2.2 Layerﮒ؟ﻛﺛﻟﺁ۵ﻝﭨﻟﺁﺑﮔ
- **Layerﮒﺛﮒﺎ**: Layer 5 - ﻝ­ﻝ۴ﮔ۶ﻟ۰?
- **ﻟﻟﺑ۲ﻟﮒﺑ**: ﮔﻛﭨﻟ؟۰ﻝ؟ﻙﮔﻛﭨﮔﺑﮔﺍﻙﮔﻛﭨﮔ۴ﻟﺁ۱ﻙﻠ۲ﻠ۸ﮔ۶?
- **ﻛﺕﻛﺕﮒﺎﮔ۴?*: 
  - ﻛﺕﮒﺎﻛﺝﻟﭖ: Layer 5 QMTExecutor (ﮔﻛﺝﻛﭦ۳ﮔﮔ۶ﻟ۰ﻝﭨﮔ)
  - ﻛﺕﮒﺎﻛﺝﻟﭖ: Layer 6 ﻝﭨﮒﻛﺙﮒ?(ﮔﻛﺝﮔﻛﭨﻛﺟ۰ﮔﺁ)

### 2.3 ﮔ۷۰ﮒﻟﻟﺑ۲ﻛﺕﻟﺝﺗﻝﮒ؟?
- **ﮔ ﺕﮒﺟﻟﻟﺑ۲**: ﮔﻛﭨﻟ؟۰ﻝ؟ﻙﮔﻛﭨﮔﺑﮔﺍﻙﮔﻛﭨﮔ۴ﻟﺁ۱ﻙﻠ۲ﻠ۸ﮔ۶?
- **ﻟﻟﺑ۲ﻟﺝﺗﻝ**: 
  - ?ﮔ؛ﮔ۷۰ﮒﻟﺑ? ﮔﻛﭨﻟ؟۰ﻝ؟ﻙﮔﻛﭨﮔﺑﮔﺍﻙﮔﻛﭨﮔ۴ﻟﺁ۱ﻙﻠ۲ﻠ۸ﮔ۶?
  - ?ﮔ؛ﮔ۷۰ﮒﻛﺕﻟﺑﻟﺑ۲: ﻛﭦ۳ﮔﮔ۶ﻟ۰ﻙﻝ­ﻝ۴ﮒﺏﻝ­ﻙﮔﺍﮔ؟ﻟﺓﮒﻙﻠ۲ﻠ۸ﮔ۷۰?
- **ﮔ۴ﮒ۲ﮒ۴ﻝﭦ۵**: ﮔﻛﺝﻝﭨﻛﺕﻝPython APIﮔ۴ﮒ۲

### 2.4 ﻛﺝﻟﭖﮒﺏﻝﺏﭨ
| ﻛﺝﻟﭖﮔ۷۰ﮒ | ﻛﺝﻟﭖﻝﺎﭨﮒ | ﮔ۴ﮒ۲ﮔﺗﮒﺙ | ﻝﮔ؛ﻟ۵ﮔﺎ | ﮒ۳ﮔﺏ۷ |
|----------|----------|----------|----------|------|
| psycopg2 | ﮒﺙﭦﻛﺝ?| Python?| >=2.9 | PostgreSQLﻠ۸ﺎﮒ۷ |
| redis | ﮒﺙﭦﻛﺝ?| Python?| >=4.0 | Redisﮒ؟۱ﮔﺓ?|
| decimal | ﮒﺙﭦﻛﺝ?| Pythonﮔ ﮒ?| >=3.8 | ﻠ،ﻝﺎﺝﮒﭦ۵ﻟ؟۰?|

---

## 3. ﮔ۴ﮒ۲ﮒ؟ﻛﺗ

### 3.1 APIﮔ۴ﮒ۲ﻟ۶ﻟ

#### 3.1.1 ﻛﺕﭨﮔ۴ﮒ۲ﻝﺎﭨ
```python
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
import psycopg2
import redis
import json
import logging


class OrderSide(Enum):
    """ﻟ؟۱ﮒﮔﺗﮒﮔﻛﺕﺝ"""
    BUY = "buy"
    SELL = "sell"


@dataclass
class Position:
    """ﮔﻛﭨﻛﺟ۰ﮔﺁ"""
    position_id: int
    account_id: int
    stock_code: str
    stock_name: str
    exchange: str
    quantity: int
    available_quantity: int
    frozen_quantity: int
    avg_cost: Decimal
    current_price: Decimal
    market_value: Decimal
    unrealized_pnl: Decimal
    unrealized_pnl_pct: Decimal
    realized_pnl: Decimal
    position_pct: Decimal
    first_buy_date: date
    last_trade_date: date


@dataclass
class PositionSnapshot:
    """ﮔﻛﭨﮒﺟ،ﻝ۶"""
    snapshot_id: int
    account_id: int
    snapshot_date: date
    total_market_value: Decimal
    total_unrealized_pnl: Decimal
    positions: List[Position]


class PositionRepository:
    """ﮔﻛﭨﻛﭨﮒ۷"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)
        self._init_connection()
    
    def _init_connection(self) -> None:
        """ﮒﮒ۶ﮒﮔﺍﮔ؟ﮒﭦﻟﺟﮔ۴"""
        self.conn = psycopg2.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            database=self.db_config['database'],
            user=self.db_config['user'],
            password=self.db_config['password']
        )
        self.logger.info("Position repository initialized")
    
    def create_position(
        self,
        account_id: int,
        stock_code: str,
        stock_name: str,
        exchange: str,
        quantity: int,
        avg_cost: Decimal
    ) -> Position:
        """ﮒﮒﭨﭦﮔﻛﭨ
        
        ﮒﮔﺍ:
            account_id: ﻟﺑ۵ﮔﺓID
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            stock_name: ﻟ۰ﻝ۴۷ﮒﻝ۶ﺍ
            exchange: ﻛﭦ۳ﮔﮔ
            quantity: ﮔﺍﻠ
            avg_cost: ﮒﺗﺏﮒﮔﮔ؛
            
        ﻟﺟﮒ:
            ﮔﻛﭨﻛﺟ۰ﮔﺁ
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO positions (
                account_id, stock_code, stock_name, exchange,
                quantity, available_quantity, frozen_quantity,
                avg_cost, current_price, market_value,
                unrealized_pnl, unrealized_pnl_pct, realized_pnl,
                position_pct, first_buy_date, last_trade_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            account_id, stock_code, stock_name, exchange,
            quantity, 0, 0, avg_cost, Decimal('0'), Decimal('0'),
            Decimal('0'), Decimal('0'), Decimal('0'),
            Decimal('0'), date.today(), date.today()
        ))
        
        position_id = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        
        return Position(
            position_id=position_id,
            account_id=account_id,
            stock_code=stock_code,
            stock_name=stock_name,
            exchange=exchange,
            quantity=quantity,
            available_quantity=0,
            frozen_quantity=0,
            avg_cost=avg_cost,
            current_price=Decimal('0'),
            market_value=Decimal('0'),
            unrealized_pnl=Decimal('0'),
            unrealized_pnl_pct=Decimal('0'),
            realized_pnl=Decimal('0'),
            position_pct=Decimal('0'),
            first_buy_date=date.today(),
            last_trade_date=date.today()
        )
    
    def find_by_account(
        self,
        account_id: int,
        stock_code: Optional[str] = None
    ) -> List[Position]:
        """ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮔﻛﭨ
        
        ﮒﮔﺍ:
            account_id: ﻟﺑ۵ﮔﺓID
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ ﺅﺙﮒﺁﻠﺅﺙ
            
        ﻟﺟﮒ:
            ﮔﻛﭨﮒﻟ۰۷
        """
        cursor = self.conn.cursor()
        
        if stock_code:
            cursor.execute('''
                SELECT id, account_id, stock_code, stock_name, exchange,
                       quantity, available_quantity, frozen_quantity,
                       avg_cost, current_price, market_value,
                       unrealized_pnl, unrealized_pnl_pct, realized_pnl,
                       position_pct, first_buy_date, last_trade_date
                FROM positions
                WHERE account_id = %s AND stock_code = %s
            ''', (account_id, stock_code))
        else:
            cursor.execute('''
                SELECT id, account_id, stock_code, stock_name, exchange,
                       quantity, available_quantity, frozen_quantity,
                       avg_cost, current_price, market_value,
                       unrealized_pnl, unrealized_pnl_pct, realized_pnl,
                       position_pct, first_buy_date, last_trade_date
                FROM positions
                WHERE account_id = %s
            ''', (account_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        
        positions = []
        for row in rows:
            positions.append(Position(
                position_id=row[0],
                account_id=row[1],
                stock_code=row[2],
                stock_name=row[3],
                exchange=row[4],
                quantity=row[5],
                available_quantity=row[6],
                frozen_quantity=row[7],
                avg_cost=row[8],
                current_price=row[9],
                market_value=row[10],
                unrealized_pnl=row[11],
                unrealized_pnl_pct=row[12],
                realized_pnl=row[13],
                position_pct=row[14],
                first_buy_date=row[15],
                last_trade_date=row[16]
            ))
        
        return positions
    
    def update_position(
        self,
        position_id: int,
        quantity: int,
        available_quantity: int,
        frozen_quantity: int,
        avg_cost: Decimal,
        current_price: Decimal,
        market_value: Decimal,
        unrealized_pnl: Decimal,
        unrealized_pnl_pct: Decimal,
        realized_pnl: Decimal,
        position_pct: Decimal
    ) -> bool:
        """ﮔﺑﮔﺍﮔﻛﭨ
        
        ﮒﮔﺍ:
            position_id: ﮔﻛﭨID
            quantity: ﮔﺍﻠ
            available_quantity: ﮒﺁﻝ۷ﮔﺍﻠ
            frozen_quantity: ﮒﭨﻝﭨﮔﺍﻠ
            avg_cost: ﮒﺗﺏﮒﮔﮔ؛
            current_price: ﮒﺛﮒﻛﭨﺓﮔ ﺙ
            market_value: ﮒﺕ?
            unrealized_pnl: ﮔﭖ؟ﮒ۷ﻝﻛﭦ
            unrealized_pnl_pct: ﮔﭖ؟ﮒ۷ﻝﻛﭦﮔﺁﻛﺝ
            realized_pnl: ﮒﺓﺎﮒ؟ﻝﺍﻝ?
            position_pct: ﻛﭨﻛﺛﮒ ﮔﺁ
            
        ﻟﺟﮒ:
            ﮔﺁﮒ۵ﮔﮒ
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            UPDATE positions SET
                quantity = %s,
                available_quantity = %s,
                frozen_quantity = %s,
                avg_cost = %s,
                current_price = %s,
                market_value = %s,
                unrealized_pnl = %s,
                unrealized_pnl_pct = %s,
                realized_pnl = %s,
                position_pct = %s,
                last_trade_date = %s
            WHERE id = %s
        ''', (
            quantity, available_quantity, frozen_quantity,
            avg_cost, current_price, market_value,
            unrealized_pnl, unrealized_pnl_pct, realized_pnl,
            position_pct, date.today(), position_id
        ))
        
        self.conn.commit()
        cursor.close()
        
        return True


class PositionCache:
    """ﮔﻛﭨﻝﺙﮒ­"""
    
    def __init__(self, redis_config: Dict[str, Any]):
        self.redis_client = redis.Redis(
            host=redis_config['host'],
            port=redis_config['port'],
            db=redis_config.get('db', 0),
            password=redis_config.get('password'),
            decode_responses=True
        )
        self.logger = logging.getLogger(__name__)
    
    def get_position(
        self,
        account_id: int,
        stock_code: str
    ) -> Optional[Position]:
        """ﻟﺓﮒﮔﻛﭨﻝﺙﮒ­
        
        ﮒﮔﺍ:
            account_id: ﻟﺑ۵ﮔﺓID
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            
        ﻟﺟﮒ:
            ﮔﻛﭨﻛﺟ۰ﮔﺁﺅﺙﮒ۵ﮔﮒ­ﮒ۷ﺅﺙ
        """
        key = f"position:{account_id}:{stock_code}"
        data = self.redis_client.get(key)
        
        if data:
            position_dict = json.loads(data)
            return Position(**position_dict)
        
        return None
    
    def set_position(
        self,
        position: Position,
        ttl: int = 3600
    ) -> None:
        """ﻟ؟ﺝﻝﺛ؟ﮔﻛﭨﻝﺙﮒ­
        
        ﮒﮔﺍ:
            position: ﮔﻛﭨﻛﺟ۰ﮔﺁ
            ttl: ﻟﺟﮔﮔﭘﻠﺑﺅﺙﻝ۶?
        """
        key = f"position:{position.account_id}:{position.stock_code}"
        
        position_dict = {
            'position_id': position.position_id,
            'account_id': position.account_id,
            'stock_code': position.stock_code,
            'stock_name': position.stock_name,
            'exchange': position.exchange,
            'quantity': position.quantity,
            'available_quantity': position.available_quantity,
            'frozen_quantity': position.frozen_quantity,
            'avg_cost': str(position.avg_cost),
            'current_price': str(position.current_price),
            'market_value': str(position.market_value),
            'unrealized_pnl': str(position.unrealized_pnl),
            'unrealized_pnl_pct': str(position.unrealized_pnl_pct),
            'realized_pnl': str(position.realized_pnl),
            'position_pct': str(position.position_pct),
            'first_buy_date': position.first_buy_date.isoformat(),
            'last_trade_date': position.last_trade_date.isoformat()
        }
        
        self.redis_client.setex(key, ttl, json.dumps(position_dict))
    
    def delete_position(
        self,
        account_id: int,
        stock_code: str
    ) -> None:
        """ﮒ ﻠ۳ﮔﻛﭨﻝﺙﮒ­
        
        ﮒﮔﺍ:
            account_id: ﻟﺑ۵ﮔﺓID
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
        """
        key = f"position:{account_id}:{stock_code}"
        self.redis_client.delete(key)


class PositionCalculator:
    """ﮔﻛﭨﻟ؟۰ﻝ؟?""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_market_value(
        self,
        quantity: int,
        current_price: Decimal
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﮒﺕ?
        
        ﮒﮔﺍ:
            quantity: ﮔﺍﻠ
            current_price: ﮒﺛﮒﻛﭨﺓﮔ ﺙ
            
        ﻟﺟﮒ:
            ﮒﺕ?
        """
        return Decimal(quantity) * current_price
    
    def calculate_unrealized_pnl(
        self,
        quantity: int,
        avg_cost: Decimal,
        current_price: Decimal
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﮔﭖ؟ﮒ۷ﻝﻛﭦ
        
        ﮒﮔﺍ:
            quantity: ﮔﺍﻠ
            avg_cost: ﮒﺗﺏﮒﮔﮔ؛
            current_price: ﮒﺛﮒﻛﭨﺓﮔ ﺙ
            
        ﻟﺟﮒ:
            ﮔﭖ؟ﮒ۷ﻝﻛﭦ
        """
        return Decimal(quantity) * (current_price - avg_cost)
    
    def calculate_unrealized_pnl_pct(
        self,
        avg_cost: Decimal,
        current_price: Decimal
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﮔﭖ؟ﮒ۷ﻝﻛﭦﮔﺁﻛﺝ
        
        ﮒﮔﺍ:
            avg_cost: ﮒﺗﺏﮒﮔﮔ؛
            current_price: ﮒﺛﮒﻛﭨﺓﮔ ﺙ
            
        ﻟﺟﮒ:
            ﮔﭖ؟ﮒ۷ﻝﻛﭦﮔﺁﻛﺝ
        """
        if avg_cost == Decimal('0'):
            return Decimal('0')
        
        return (current_price - avg_cost) / avg_cost
    
    def calculate_position_pct(
        self,
        market_value: Decimal,
        total_value: Decimal
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﻛﭨﻛﺛﮒ ﮔﺁ
        
        ﮒﮔﺍ:
            market_value: ﮒﺕ?
            total_value: ﮔﭨﻟﭖ?
            
        ﻟﺟﮒ:
            ﻛﭨﻛﺛﮒ ﮔﺁ
        """
        if total_value == Decimal('0'):
            return Decimal('0')
        
        return market_value / total_value


class PositionUpdater:
    """ﮔﻛﭨﮔﺑﮔﺍ?""
    
    def __init__(
        self,
        repository: PositionRepository,
        cache: PositionCache,
        calculator: PositionCalculator
    ):
        self.repository = repository
        self.cache = cache
        self.calculator = calculator
        self.logger = logging.getLogger(__name__)
    
    def update_position_from_trade(
        self,
        account_id: int,
        stock_code: str,
        side: OrderSide,
        quantity: int,
        price: Decimal,
        total_value: Decimal
    ) -> Position:
        """ﮔ ﺗﮔ؟ﮔﻛﭦ۳ﮔﺑﮔﺍﮔﻛﭨ
        
        ﮒﮔﺍ:
            account_id: ﻟﺑ۵ﮔﺓID
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            side: ﻛﺗﺍﮒﮔﺗﮒ
            quantity: ﮔﺍﻠ
            price: ﻛﭨﺓﮔ ﺙ
            total_value: ﮔﭨﻟﭖ?
            
        ﻟﺟﮒ:
            ﮔﺑﮔﺍﮒﻝﮔﻛﭨ
        """
        positions = self.repository.find_by_account(account_id, stock_code)
        
        if side == OrderSide.BUY:
            return self._add_position(
                account_id, stock_code, quantity, price, total_value, positions
            )
        else:
            return self._reduce_position(
                account_id, stock_code, quantity, price, total_value, positions
            )
    
    def _add_position(
        self,
        account_id: int,
        stock_code: str,
        quantity: int,
        price: Decimal,
        total_value: Decimal,
        positions: List[Position]
    ) -> Position:
        """ﮒ۱ﮒ ﮔﻛﭨ
        
        ﮒﮔﺍ:
            account_id: ﻟﺑ۵ﮔﺓID
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            quantity: ﮔﺍﻠ
            price: ﻛﭨﺓﮔ ﺙ
            total_value: ﮔﭨﻟﭖ?
            positions: ﻝﺍﮔﮔﻛﭨ
            
        ﻟﺟﮒ:
            ﮔﺑﮔﺍﮒﻝﮔﻛﭨ
        """
        cost = Decimal(quantity) * price
        
        if positions:
            position = positions[0]
            
            new_quantity = position.quantity + quantity
            new_cost = position.avg_cost * position.quantity + cost
            new_avg_cost = new_cost / Decimal(new_quantity)
            
            market_value = self.calculator.calculate_market_value(new_quantity, price)
            unrealized_pnl = self.calculator.calculate_unrealized_pnl(new_quantity, new_avg_cost, price)
            unrealized_pnl_pct = self.calculator.calculate_unrealized_pnl_pct(new_avg_cost, price)
            position_pct = self.calculator.calculate_position_pct(market_value, total_value)
            
            self.repository.update_position(
                position.position_id,
                new_quantity,
                position.available_quantity,
                position.frozen_quantity,
                new_avg_cost,
                price,
                market_value,
                unrealized_pnl,
                unrealized_pnl_pct,
                position.realized_pnl,
                position_pct
            )
            
            updated_position = Position(
                position_id=position.position_id,
                account_id=account_id,
                stock_code=stock_code,
                stock_name=position.stock_name,
                exchange=position.exchange,
                quantity=new_quantity,
                available_quantity=position.available_quantity,
                frozen_quantity=position.frozen_quantity,
                avg_cost=new_avg_cost,
                current_price=price,
                market_value=market_value,
                unrealized_pnl=unrealized_pnl,
                unrealized_pnl_pct=unrealized_pnl_pct,
                realized_pnl=position.realized_pnl,
                position_pct=position_pct,
                first_buy_date=position.first_buy_date,
                last_trade_date=date.today()
            )
            
            self.cache.set_position(updated_position)
            
            return updated_position
        else:
            position = self.repository.create_position(
                account_id, stock_code, stock_code, "SH",
                quantity, price
            )
            
            market_value = self.calculator.calculate_market_value(quantity, price)
            unrealized_pnl = self.calculator.calculate_unrealized_pnl(quantity, price, price)
            unrealized_pnl_pct = self.calculator.calculate_unrealized_pnl_pct(price, price)
            position_pct = self.calculator.calculate_position_pct(market_value, total_value)
            
            self.repository.update_position(
                position.position_id,
                quantity,
                0,
                0,
                price,
                price,
                market_value,
                unrealized_pnl,
                unrealized_pnl_pct,
                Decimal('0'),
                position_pct
            )
            
            updated_position = Position(
                position_id=position.position_id,
                account_id=account_id,
                stock_code=stock_code,
                stock_name=stock_code,
                exchange="SH",
                quantity=quantity,
                available_quantity=0,
                frozen_quantity=0,
                avg_cost=price,
                current_price=price,
                market_value=market_value,
                unrealized_pnl=unrealized_pnl,
                unrealized_pnl_pct=unrealized_pnl_pct,
                realized_pnl=Decimal('0'),
                position_pct=position_pct,
                first_buy_date=date.today(),
                last_trade_date=date.today()
            )
            
            self.cache.set_position(updated_position)
            
            return updated_position
    
    def _reduce_position(
        self,
        account_id: int,
        stock_code: str,
        quantity: int,
        price: Decimal,
        total_value: Decimal,
        positions: List[Position]
    ) -> Position:
        """ﮒﮒﺍﮔﻛﭨ
        
        ﮒﮔﺍ:
            account_id: ﻟﺑ۵ﮔﺓID
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            quantity: ﮔﺍﻠ
            price: ﻛﭨﺓﮔ ﺙ
            total_value: ﮔﭨﻟﭖ?
            positions: ﻝﺍﮔﮔﻛﭨ
            
        ﻟﺟﮒ:
            ﮔﺑﮔﺍﮒﻝﮔﻛﭨ
        """
        if not positions:
            raise ValueError(f"No position found for {stock_code}")
        
        position = positions[0]
        
        if quantity > position.quantity:
            raise ValueError(f"Insufficient position: {position.quantity} < {quantity}")
        
        new_quantity = position.quantity - quantity
        
        realized_pnl = Decimal(quantity) * (price - position.avg_cost)
        total_realized_pnl = position.realized_pnl + realized_pnl
        
        market_value = self.calculator.calculate_market_value(new_quantity, price)
        unrealized_pnl = self.calculator.calculate_unrealized_pnl(new_quantity, position.avg_cost, price)
        unrealized_pnl_pct = self.calculator.calculate_unrealized_pnl_pct(position.avg_cost, price)
        position_pct = self.calculator.calculate_position_pct(market_value, total_value)
        
        self.repository.update_position(
            position.position_id,
            new_quantity,
            position.available_quantity,
            position.frozen_quantity,
            position.avg_cost,
            price,
            market_value,
            unrealized_pnl,
            unrealized_pnl_pct,
            total_realized_pnl,
            position_pct
        )
        
        updated_position = Position(
            position_id=position.position_id,
            account_id=account_id,
            stock_code=stock_code,
            stock_name=position.stock_name,
            exchange=position.exchange,
            quantity=new_quantity,
            available_quantity=position.available_quantity,
            frozen_quantity=position.frozen_quantity,
            avg_cost=position.avg_cost,
            current_price=price,
            market_value=market_value,
            unrealized_pnl=unrealized_pnl,
            unrealized_pnl_pct=unrealized_pnl_pct,
            realized_pnl=total_realized_pnl,
            position_pct=position_pct,
            first_buy_date=position.first_buy_date,
            last_trade_date=date.today()
        )
        
        self.cache.set_position(updated_position)
        
        return updated_position


class PositionQuery:
    """ﮔﻛﭨﮔ۴ﻟﺁ۱?""
    
    def __init__(
        self,
        repository: PositionRepository,
        cache: PositionCache
    ):
        self.repository = repository
        self.cache = cache
        self.logger = logging.getLogger(__name__)
    
    def get_position(
        self,
        account_id: int,
        stock_code: str
    ) -> Optional[Position]:
        """ﻟﺓﮒﮔﻛﭨ
        
        ﮒﮔﺍ:
            account_id: ﻟﺑ۵ﮔﺓID
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            
        ﻟﺟﮒ:
            ﮔﻛﭨﻛﺟ۰ﮔﺁﺅﺙﮒ۵ﮔﮒ­ﮒ۷ﺅﺙ
        """
        position = self.cache.get_position(account_id, stock_code)
        
        if position:
            return position
        
        positions = self.repository.find_by_account(account_id, stock_code)
        
        if positions:
            position = positions[0]
            self.cache.set_position(position)
            return position
        
        return None
    
    def get_all_positions(
        self,
        account_id: int
    ) -> List[Position]:
        """ﻟﺓﮒﮔﮔﮔ?
        
        ﮒﮔﺍ:
            account_id: ﻟﺑ۵ﮔﺓID
            
        ﻟﺟﮒ:
            ﮔﻛﭨﮒﻟ۰۷
        """
        return self.repository.find_by_account(account_id)


class RiskController:
    """ﻠ۲ﻠ۸ﮔ۶ﮒﭘ?""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def check_position_limit(
        self,
        position: Position,
        max_position_pct: Decimal
    ) -> bool:
        """ﮔ۲ﮔ۴ﮔﻛﭨﻛﺕ?
        
        ﮒﮔﺍ:
            position: ﮔﻛﭨﻛﺟ۰ﮔﺁ
            max_position_pct: ﮔﮒ۳۶ﮔﻛﭨﮔﺁ?
            
        ﻟﺟﮒ:
            ﮔﺁﮒ۵ﻠﻟﺟ
        """
        return position.position_pct <= max_position_pct
    
    def get_position_limit(
        self,
        total_value: Decimal,
        current_price: Decimal,
        max_position_pct: Decimal,
        current_quantity: int = 0
    ) -> int:
        """ﻟﺓﮒﮔﻛﭨﻛﺕﻠ
        
        ﮒﮔﺍ:
            total_value: ﮔﭨﻟﭖ?
            current_price: ﮒﺛﮒﻛﭨﺓﮔ ﺙ
            max_position_pct: ﮔﮒ۳۶ﮔﻛﭨﮔﺁ?
            current_quantity: ﮒﺛﮒﮔﻛﭨﮔﺍﻠ
            
        ﻟﺟﮒ:
            ﮔﮒ۳۶ﮒﺁﻛﺗﺍﮒ۴ﮔﺍﻠ
        """
        if current_price == Decimal('0'):
            return 0
        
        max_total_quantity = int(total_value * max_position_pct / current_price)
        
        return max(0, max_total_quantity - current_quantity)


class PositionManager:
    """ﮔﻛﭨﻝ؟۰ﻝﮒ۷ﻛﺕﭨ?""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        self.repository = PositionRepository(config['db_config'])
        self.cache = PositionCache(config['redis_config'])
        self.calculator = PositionCalculator()
        self.updater = PositionUpdater(self.repository, self.cache, self.calculator)
        self.query = PositionQuery(self.repository, self.cache)
        self.risk_controller = RiskController(config.get('risk_config', {}))
        
        self.logger = logging.getLogger(__name__)
    
    def update_position(
        self,
        account_id: int,
        stock_code: str,
        side: OrderSide,
        quantity: int,
        price: Decimal,
        total_value: Decimal
    ) -> Position:
        """ﮔﺑﮔﺍﮔﻛﭨ
        
        ﮒﮔﺍ:
            account_id: ﻟﺑ۵ﮔﺓID
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            side: ﻛﺗﺍﮒﮔﺗﮒ
            quantity: ﮔﺍﻠ
            price: ﻛﭨﺓﮔ ﺙ
            total_value: ﮔﭨﻟﭖ?
            
        ﻟﺟﮒ:
            ﮔﺑﮔﺍﮒﻝﮔﻛﭨ
        """
        return self.updater.update_position_from_trade(
            account_id, stock_code, side, quantity, price, total_value
        )
    
    def get_position(
        self,
        account_id: int,
        stock_code: str
    ) -> Optional[Position]:
        """ﻟﺓﮒﮔﻛﭨ
        
        ﮒﮔﺍ:
            account_id: ﻟﺑ۵ﮔﺓID
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            
        ﻟﺟﮒ:
            ﮔﻛﭨﻛﺟ۰ﮔﺁﺅﺙﮒ۵ﮔﮒ­ﮒ۷ﺅﺙ
        """
        return self.query.get_position(account_id, stock_code)
    
    def get_all_positions(
        self,
        account_id: int
    ) -> List[Position]:
        """ﻟﺓﮒﮔﮔﮔ?
        
        ﮒﮔﺍ:
            account_id: ﻟﺑ۵ﮔﺓID
            
        ﻟﺟﮒ:
            ﮔﻛﭨﮒﻟ۰۷
        """
        return self.query.get_all_positions(account_id)
    
    def check_position_limit(
        self,
        position: Position
    ) -> bool:
        """ﮔ۲ﮔ۴ﮔﻛﭨﻛﺕ?
        
        ﮒﮔﺍ:
            position: ﮔﻛﭨﻛﺟ۰ﮔﺁ
            
        ﻟﺟﮒ:
            ﮔﺁﮒ۵ﻠﻟﺟ
        """
        max_position_pct = Decimal(str(self.config.get('max_position_pct', 0.1)))
        return self.risk_controller.check_position_limit(position, max_position_pct)
    
    def get_position_limit(
        self,
        total_value: Decimal,
        current_price: Decimal,
        stock_code: str,
        account_id: int
    ) -> int:
        """ﻟﺓﮒﮔﻛﭨﻛﺕﻠ
        
        ﮒﮔﺍ:
            total_value: ﮔﭨﻟﭖ?
            current_price: ﮒﺛﮒﻛﭨﺓﮔ ﺙ
            stock_code: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ 
            account_id: ﻟﺑ۵ﮔﺓID
            
        ﻟﺟﮒ:
            ﮔﮒ۳۶ﮒﺁﻛﺗﺍﮒ۴ﮔﺍﻠ
        """
        max_position_pct = Decimal(str(self.config.get('max_position_pct', 0.1)))
        
        position = self.get_position(account_id, stock_code)
        current_quantity = position.quantity if position else 0
        
        return self.risk_controller.get_position_limit(
            total_value, current_price, max_position_pct, current_quantity
        )
```

### 3.2 ﮔ۶ﻟﺛﮔﮔ ﻟ۵ﮔﺎ
| ﮔ۶ﻟﺛﮔﮔ  | ﻝ؟ﮔ ?| ﮔﭖﻠﮔﺗﮔﺏ |
|----------|--------|----------|
| ﮔﻛﭨﮔﺑﮔﺍﮔﭘﻠﺑ | < 50ms | ﮒﮔ؛۰ﮔﺑﮔﺍ |
| ﮔﻛﭨﮔ۴ﻟﺁ۱ﮔﭘﻠﺑ | < 20ms | ﮒﮔ؛۰ﮔ۴ﻟﺁ۱ |
| ﻝﺙﮒ­ﮒﺛﻛﺕ­?| ?90% | ﻝﺙﮒ­ﻝﮔ۶ |
| ﮔﺍﮔ؟ﻛﺕﻟ?| 100% | ﮔﺍﮔ؟ﻠ۹ﻟﺁ |

### 3.3 ﮒ؟ﮒ۷ﮔﭦﮒﭘ
- **ﮔﺍﮔ؟ﻛﺕﻟ?*: ﻛﺛﺟﻝ۷ﮔﺍﮔ؟ﮒﭦﻛﭦﮒ۰ﻛﺟﻟﺁﮔﺍﮔ؟ﻛﺕﻟ?
- **ﮒﺗﭘﮒﮔ۶ﮒﭘ**: ﻛﺛﺟﻝ۷ﻛﺗﻟ۶ﻠﮔ۶ﮒﭘﮒﺗﭘﮒﮔﺑ?
- **ﮔﺍﮔ؟ﮒ۳ﻛﭨﺛ**: ﮒ؟ﮔﮒ۳ﻛﭨﺛﮔﻛﭨﮔﺍﮔ؟

---

## 4. ﮔﺍﮔ؟ﮔ۷۰ﮒﻛﺕﮒ­?

### 4.1 ﮔ ﺕﮒﺟﮔﺍﮔ؟ﻝﭨﮔ

#### 4.1.1 ﮔﻛﭨﻟ۰۷ﮔ۷۰?
```sql
CREATE TABLE positions (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(50),
    exchange VARCHAR(10) NOT NULL,
    quantity BIGINT NOT NULL DEFAULT 0,
    available_quantity BIGINT NOT NULL DEFAULT 0,
    frozen_quantity BIGINT NOT NULL DEFAULT 0,
    avg_cost DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
    current_price DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
    market_value DECIMAL(20,4) NOT NULL DEFAULT 0.0000,
    unrealized_pnl DECIMAL(20,4) NOT NULL DEFAULT 0.0000,
    unrealized_pnl_pct DECIMAL(12,6) NOT NULL DEFAULT 0.000000,
    realized_pnl DECIMAL(20,4) NOT NULL DEFAULT 0.0000,
    position_pct DECIMAL(12,6) NOT NULL DEFAULT 0.000000,
    first_buy_date DATE,
    last_trade_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_positions_account ON positions(account_id);
CREATE INDEX idx_positions_stock ON positions(stock_code);
CREATE INDEX idx_positions_account_stock ON positions(account_id, stock_code);
```

### 4.2 ﻝﺙﮒ­ﻝ­ﻝ۴
| ﻝﺙﮒ­ﻝﺎﭨﮒ | TTL | ﮔﺓﮔﺎﺍﻝ­ﻝ۴ | ﮔﮒ۳۶ﮒ؟ﺗ?|
|----------|-----|----------|----------|
| ﮔﻛﭨﻝﺙﮒ­ | 1ﮒﺍﮔﭘ | LRU | 10000ﮔ۰ﻟ؟ﺍ?|
| ﮒﺟ،ﻝ۶ﻝﺙﮒ­ | 1?| LRU | 365ﻛﭨﺛﮒﺟ،?|

### 4.3 ﮔﺍﮔ؟ﮔﻛﺗ?
- **ﮔﻛﺗﮒﻠ?*: ﮔﮔﮔﻛﭨﮔﺍﮔ؟ﻠﻟ۵ﮔﻛﺗﮒﮒ­ﮒ۷
- **ﮒ­ﮒ۷ﮔ ﺙﮒﺙ**: PostgreSQLﮔﺍﮔ؟?
- **ﮒ۳ﻛﭨﺛﻝ­ﻝ۴**: ﮔﺁﮔ۴ﮒ۳ﻛﭨﺛ

---

## 5. ﻝ؟ﮔﺏﮒ؟ﻝﺍﻟﺁﺑﮔ

### 5.1 ﮔ ﺕﮒﺟﻝ؟ﮔﺏ

#### 5.1.1 ﮔﻛﭨﻟ؟۰ﻝ؟ﻝ؟ﮔﺏ
```python
def calculate_unrealized_pnl(
    self,
    quantity: int,
    avg_cost: Decimal,
    current_price: Decimal
) -> Decimal:
    """
    ﮔﭖ؟ﮒ۷ﻝﻛﭦﻟ؟۰ﻝ؟ﻝ؟ﮔﺏ
    
    ﻝ؟ﮔﺏﮒﻝ:
    ﮔﭖ؟ﮒ۷ﻝﻛﭦ = ﮔﺍﻠ * (ﮒﺛﮒﻛﭨﺓﮔ ﺙ - ﮒﺗﺏﮒﮔﮔ؛)
    
    ﮒ۳ﮔ? O(1)
    """
    return Decimal(quantity) * (current_price - avg_cost)
```

#### 5.1.2 ﮔﻛﭨﮔﺑﮔﺍﻝ؟ﮔﺏ
```python
def update_position_from_trade(
    self,
    account_id: int,
    stock_code: str,
    side: OrderSide,
    quantity: int,
    price: Decimal,
    total_value: Decimal
) -> Position:
    """
    ﮔﻛﭨﮔﺑﮔﺍﻝ؟ﮔﺏ
    
    ﻝ؟ﮔﺏﮒﻝ:
    1. ﮔ۴ﻟﺁ۱ﻝﺍﮔﮔﻛﭨ
    2. ﮔ ﺗﮔ؟ﻛﺗﺍﮒﮔﺗﮒﮔﺑﮔﺍﮔﻛﭨ
    3. ﻟ؟۰ﻝ؟ﮔﺍﻝﮔﻛﭨﮔﮔ 
    4. ﮔﺑﮔﺍﮔﺍﮔ؟ﮒﭦﮒﻝﺙﮒ­
    
    ﮒ۳ﮔ? O(1)
    """
    positions = self.repository.find_by_account(account_id, stock_code)
    
    if side == OrderSide.BUY:
        return self._add_position(
            account_id, stock_code, quantity, price, total_value, positions
        )
    else:
        return self._reduce_position(
            account_id, stock_code, quantity, price, total_value, positions
        )
```

---

## 6. ﮒ؟ﮔﺛﮔﮔﺁﮔ 

### 6.1 ﻟﺁ­ﻟ۷ﻛﺕﮔ۰?
| ﮔﮔﺁﻠﮒ | ﻝﮔ؛ﻟ۵ﮔﺎ | ﻝ?| ﻠﮔ۸ﻝﻝﺎ |
|----------|----------|------|----------|
| Python | >=3.8 | ﻛﺕﭨﻟ۵ﮒﺙﮒﻟﺁ­ﻟ۷ | ﻠﮒﻝﺏﭨﻝﭨﮔ ﮒﻟﺁ­ﻟ۷ |
| psycopg2 | >=2.9 | PostgreSQLﻠ۸ﺎﮒ۷ | ﮔﻝﻝ۷ﺏﮒ؟ |
| redis | >=4.0 | Redisﮒ؟۱ﮔﺓ?| ﻠ،ﮔ۶ﻟﺛﻝﺙﮒ­ |

### 6.2 ﻝ؛؛ﻛﺕﮔﺗﻛﺝ?
```yaml
requirements:
  - psycopg2-binary>=2.9.0
  - redis>=4.0.0
```

---

## 7. ﮔﭖﻟﺁﻝ­ﻝ۴

### 7.1 ﮒﮒﮔﭖﻟﺁ
| ﮔﭖﻟﺁ?| ﮔﭖﻟﺁﮒﮒ؟ﺗ | ﻟ۵ﻝﻝﻝ؟?|
|--------|----------|------------|
| ﮔﻛﭨﻟ؟۰ﻝ؟ | ﻟ؟۰ﻝ؟ﮔ­۲ﻝ۰؟?| 100% |
| ﮔﻛﭨﮔﺑﮔﺍ | ﮔﺑﮔﺍﮔ­۲ﻝ۰؟?| 100% |
| ﮔﻛﭨﮔ۴ﻟﺁ۱ | ﮔ۴ﻟﺁ۱ﮔ­۲ﻝ۰؟?| 100% |
| ﻠ۲ﻠ۸ﮔ۶ﮒﭘ | ﮔ۶ﮒﭘﮔ­۲ﻝ۰؟?| 100% |

### 7.2 ﻠﮔﮔﭖﻟﺁ
```python
def test_position_manager_integration():
    """ﻠﮔﮔﭖﻟﺁﻝ۳ﭦﻛﺝ"""
    config = {
        'db_config': {
            'host': 'localhost',
            'port': 5432,
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_password'
        },
        'redis_config': {
            'host': 'localhost',
            'port': 6379,
            'db': 0
        },
        'max_position_pct': 0.1
    }
    
    manager = PositionManager(config)
    
    position = manager.update_position(
        account_id=1,
        stock_code='600000.SH',
        side=OrderSide.BUY,
        quantity=100,
        price=Decimal('10.0'),
        total_value=Decimal('100000.0')
    )
    
    assert position.quantity == 100
    assert position.avg_cost == Decimal('10.0')
```

---

## 8. ﻠ۲ﻠ۸ﻛﺕﻝﭦ۵?

### 8.1 ﮔﮔﺁﻠ۲?
| ﻠ۲ﻠ۸ID | ﻠ۲ﻠ۸ﮔﻟﺟﺍ | ﻠ۲ﻠ۸ﻝ­ﻝﭦ۶ | ﻝﺙﻟ۶۲ﮔ۹ﮔﺛ |
|--------|----------|----------|----------|
| R001 | ﮔﺍﮔ؟ﮒﭦﻟﺟﮔ۴ﮒ۳ﺎ?| P1 | ﮒ؟ﻝﺍﻟﺟﮔ۴ﻠﻟﺁﮔﭦﮒﭘ |
| R002 | ﻝﺙﮒ­ﮒ۳ﺎﮔ | P2 | ﮒ؟ﻝﺍﻝﺙﮒ­ﻠ۱ﻝ­ﮔﭦﮒﭘ |
| R003 | ﮒﺗﭘﮒﮔﺑﮔﺍﮒﺎﻝ۹ | P1 | ﮒ؟ﻝﺍﻛﺗﻟ۶ﻠﮔﭦ?|

### 8.2 ﻝﭦ۵ﮔﮔ۰ﻛﭨﭘ
- **ﮔﮔﺁﻝﭦ۵?*: ﻛﺝﻟﭖPostgreSQLﮒRedis
- **ﻟﭖﮔﭦﻝﭦ۵ﮔ**: ﮒﮒ­ﻛﺛﺟﻝ۷<1GBﺅﺙﻝ۲ﻝﻛﺛﺟ?10GB
- **ﮔﭘﻠﺑﻝﭦ۵ﮔ**: ﻠ۱ﻟ؟۰ﮒﺙﮒﮔﭘ?2ﮒﺍﮔﭘ
- **ﻟﺑ۷ﻠﻝﭦ۵ﮔ**: ﮔﭖﻟﺁﻟ۵ﻝﻝﻗ۴90%

---

## 9. ﻠ۹ﮔﭘﮔ ﮒ

### 9.1 ﮒﻟﺛﻠ۹ﮔﭘﮔ ﮒ
| ﮒﻟﺛ?| ﻠ۹ﮔﭘﮔ ﮒ | ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|--------|----------|----------|
| ﮔﻛﭨﻟ؟۰ﻝ؟ | ﻟ؟۰ﻝ؟ﮔ­۲ﻝ۰؟ | ﮒﮒﮔﭖﻟﺁ |
| ﮔﻛﭨﮔﺑﮔﺍ | ﮔﺑﮔﺍﮔ­۲ﻝ۰؟ | ﮒﮒﮔﭖﻟﺁ |
| ﮔﻛﭨﮔ۴ﻟﺁ۱ | ﮔ۴ﻟﺁ۱ﮔ­۲ﻝ۰؟ | ﮒﮒﮔﭖﻟﺁ |
| ﻠ۲ﻠ۸ﮔ۶ﮒﭘ | ﮔ۶ﮒﭘﮔ­۲ﻝ۰؟ | ﮒﮒﮔﭖﻟﺁ |

### 9.2 ﮔ۶ﻟﺛﻠ۹ﮔﭘﮔ ﮒ
| ﮔ۶ﻟﺛﮔﮔ  | ﻠ۹ﮔﭘﮔ ﮒ | ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|----------|----------|----------|
| ﮔﻛﭨﮔﺑﮔﺍﮔﭘﻠﺑ | < 50ms | ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| ﮔﻛﭨﮔ۴ﻟﺁ۱ﮔﭘﻠﺑ | < 20ms | ﮔ۶ﻟﺛﮔﭖﻟﺁ |
| ﻝﺙﮒ­ﮒﺛﻛﺕ­?| ?90% | ﮔ۶ﻟﺛﮔﭖﻟﺁ |

### 9.3 ﻟﺑ۷ﻠﻠ۹ﮔﭘﮔ ﮒ
| ﻟﺑ۷ﻠﮔﮔ  | ﻠ۹ﮔﭘﮔ ﮒ | ﻠ۹ﻟﺁﮔﺗﮔﺏ |
|----------|----------|----------|
| ﮔﭖﻟﺁﻟ۵ﻝ?| ?90% | pytest-cov |
| ﻛﭨ۲ﻝ ﻟﺑ۷ﻠ | ﮔ ﻛﺕ۴ﻠﻠ؟?| pylint |

---

## 10. ﮒ؟ﮔﺛﻟﺓﺁﻝﭦﺟ?

### 10.1 Phase 1: ﮔ ﺕﮒﺟﮒﻟﺛﮒﺙ?(3?
- **Day 1**: ﮔﻛﭨﻛﭨﮒ۷ﻙﮔﻛﭨﻝﺙ?
- **Day 2**: ﮔﻛﭨﻟ؟۰ﻝ؟ﮒ۷ﻙﮔﻛﭨﮔﺑﮔﺍﮒ۷
- **Day 3**: ﮔﻛﭨﮔ۴ﻟﺁ۱ﮒ۷ﻙﻠ۲ﻠ۸ﮔ۶ﮒﭘﮒ۷

---

## ﻠﮒﺛ

### A. ﻠﻝﺛ؟ﻝ۳ﭦﻛﺝ
```yaml
position_manager:
  db_config:
    host: "localhost"
    port: 5432
    database: "zephyr_alpha"
    user: "postgres"
    password: "password"
  
  redis_config:
    host: "localhost"
    port: 6379
    db: 0
    password: null
  
  risk_config:
    max_position_pct: 0.1
  
  cache:
    ttl: 3600
    max_size: 10000
```

### B. ﻠﻟﺁﺁﻝ ﮒ؟?
| ﻠﻟﺁﺁ?| ﻠﻟﺁﺁﻝﺎﭨﮒ | ﻠﻟﺁﺁﮔﻟﺟﺍ | ﮒ۳ﻝﮔﺗﮒﺙ |
|--------|----------|----------|----------|
| ERR_POS_001 | DatabaseError | ﮔﺍﮔ؟ﮒﭦﻠ?| ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻠ?|
| ERR_POS_002 | CacheError | ﻝﺙﮒ­ﻠﻟﺁﺁ | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻠﻝﭦ۶ﮒ۳?|
| ERR_POS_003 | PositionError | ﮔﻛﭨﻠﻟﺁﺁ | ﻟ؟ﺍﮒﺛﮔ۴ﮒﺟﺅﺙﻟﺟﮒﻠ?|

### C. ﮒﻟﮔ?
- [ﮔﭘﮔﮒ؟ﻛﺗ](../../01_FRAMEWORK/ARCHITECTURE.md)
- [ﮔ۷۰ﮒﻟﻟﺑ۲ﻟﺝﺗﻝ](../../01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md)
- [ﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰](../../design/database/P0-01_Database_Design_Document.md)


**ﮔﮔ۰۲ﻝﮔ؛**: v1.0.0 | **ﮒﮒﭨﭦﮔ۴ﮔ**: 2026-04-02 | **ﻝﭨﺑﮔ۳?*: ﻝ­ﻝ۴ﮔ۶ﻟ۰ﮒﺎﻟﺑﻟﺑ۲ﻛﭦﭦ
