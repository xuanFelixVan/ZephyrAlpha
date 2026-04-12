---
module_id: P0_03_INTERNAL_SERVICE_INTERFACE_DESIGN
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - ﮒﻠ۷ﮔﮒ۰ﮔ۴ﮒ۲ﻟﺝﻟ۰ﺅﺙﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮒﺅﺙ文档
layer: layer_05
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮒﻠ۷ﮔﮒ۰ﮔ۴ﮒ۲ﮔﮒ
applicable_scope: ﮒ۷ﻝﺏﭨﻝﭨﮔﮒ۰ﮔ۴ﮒ?
compliance_level: ﻛﺕﻛﺕﮔﭦﮔﮔﮒ
parent_document: P0-01_Database_Design_Document.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?---
> **核心职责**: 文档内容说明
> **ﮔﭘﮔﮔ۷۰ﮒﺙ**: ﮒﺝ؟ﮔﮒ۰ﮔﭘﮔ?+ DDDﻠ۱ﮒﻠ۸ﺎﮒ۷ﻟ؟ﺝﻟ؟۰
> **ﮔ۴ﮒ۲ﮒﻟ؟؟**: RESTful API + gRPC
> **ﻟ؟ﺝﻟ؟۰ﮒﮒ**: ﮔ۴ﮒ۲ﮒﻟ۰ﻙﮒ۴ﻝﭦ۵ﻛﺙﮒﻙﮔﺝﻟ۵ﮒﻙﻠ،ﮒﻟ
1. **功能完整性**: 确保文档内容完整，满足使用需求
2. **易用性**: 提高文档可读性，便于快速理解
3. **可维护性**: 文档结构清晰，便于后续维护
4. **一致性**: 确保文档格式和风格统一
> **职责边界**:
  - 文档完整性: 100%
  - 格式规范性: 100%
  - 内容准确性: 100%
---
## 1. ﻟﺑ۵ﮔﺓﮔﮒ۰ﮔ۴ﮒ۲ (AccountService)



### 1.1 ﮔﮒ۰ﮔ۵ﻟﺟﺍ



**ﮔﮒ۰ﮒﻝ۶ﺍ**: AccountService  

**ﮔﮒ۰ﻟﻟﺑ۲**: ﻟﺑ۵ﮔﺓﻝ؟۰ﻝﻙﻟﭖﻠﻝ؟۰ﻝﻙﻟﺑ۵ﮔﺓﮒﺟ،ﻝ? 

**ﻛﺝﻟﭖﮔﮒ۰**: PositionService, OrderService  

**ﮔﺍﮔ؟ﻟ؟ﺟﻠ؟**: AccountRepository



### 1.2 ﮔ۴ﮒ۲ﮒ؟ﻛﺗ



#### 1.2.1 ﮒﮒﭨﭦﻟﺑ۵ﮔﺓ



**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `POST /api/v1/accounts`



**ﻟﺁﺓﮔﺎﮒﮔﺍ**:

```json

{

  "account_name": "ﻠﭨﻟ؟۳ﮔ۷۰ﮔﻟﺑ۵ﮔﺓ",

  "account_type": "simulation",

  "initial_capital": 1000000.0000,

  "broker": "ﮒﮔﺏﺍﻟﺁﮒﺕ"

}

```



**ﮒﮒﭦﻝﭨﮔ**:

```json

{

  "code": 200,

  "message": "ﻟﺑ۵ﮔﺓﮒﮒﭨﭦﮔﮒ",

  "data": {

    "id": 1,

    "account_code": "ACC_20260402_001",

    "account_name": "ﻠﭨﻟ؟۳ﮔ۷۰ﮔﻟﺑ۵ﮔﺓ",

    "account_type": "simulation",

    "broker": "ﮒﮔﺏﺍﻟﺁﮒﺕ",

    "initial_capital": 1000000.0000,

    "current_capital": 1000000.0000,

    "available_cash": 1000000.0000,

    "frozen_cash": 0.0000,

    "total_assets": 1000000.0000,

    "total_pnl": 0.0000,

    "max_drawdown": 0.000000,

    "status": "active",

    "created_at": "2026-04-02T10:00:00Z",

    "updated_at": "2026-04-02T10:00:00Z"

  }

}

```



**ﻛﺕﮒ۰ﻟ۶ﮒ**:

1. ﻟﺑ۵ﮔﺓﻝﺙﻝﻟ۹ﮒ۷ﻝﮔﺅﺙACC_YYYYMMDD_XXX

2. ﮒﮒ۶ﻟﭖﻠﮒﺟﻠ۰ﭨ > 0

3. ﮒ؟ﻝﻟﺑ۵ﮔﺓﮒﺟﻠ۰ﭨﮒ۰،ﮒﮒﺕﮒﮒﻝ۶ﺍ



---



#### 1.2.2 ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ



**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/accounts/{account_id}`



**ﻟﺁﺓﮔﺎﮒﮔﺍ**:

- `account_id`: ﻟﺑ۵ﮔﺓIDﺅﺙﻟﺓﺁﮒﺝﮒﮔﺍﺅﺙ



**ﮒﮒﭦﻝﭨﮔ**:

```json

{

  "code": 200,

  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",

  "data": {

    "id": 1,

    "account_code": "ACC_20260402_001",

    "account_name": "ﻠﭨﻟ؟۳ﮔ۷۰ﮔﻟﺑ۵ﮔﺓ",

    "account_type": "simulation",

    "broker": "ﮒﮔﺏﺍﻟﺁﮒﺕ",

    "initial_capital": 1000000.0000,

    "current_capital": 950000.0000,

    "available_cash": 750000.0000,

    "frozen_cash": 200000.0000,

    "total_assets": 1200000.0000,

    "total_pnl": 200000.0000,

    "max_drawdown": 0.050000,

    "status": "active",

    "created_at": "2026-04-02T10:00:00Z",

    "updated_at": "2026-04-02T15:30:00Z",

    "positions": [

      {

        "stock_code": "600000.SH",

        "stock_name": "ﮔﭖ۵ﮒﻠﭘﻟ۰",

        "quantity": 10000,

        "market_value": 128000.0000

      }

    ]

  }

}

```



---



#### 1.2.3 ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮒﻟ۰۷



**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/accounts`



**ﻟﺁﺓﮔﺎﮒﮔﺍ**:

- `account_type`: ﻟﺑ۵ﮔﺓﻝﺎﭨﮒﺅﺙﮒﺁﻠﺅﺙ

- `status`: ﻟﺑ۵ﮔﺓﻝﭘﮔﺅﺙﮒﺁﻠﺅﺙ

- `page`: ﻠ۰ﭖﻝﺅﺙﻠﭨﻟ؟?ﺅﺙ?

- `page_size`: ﮔﺁﻠ۰ﭖﮔﺍﻠﺅﺙﻠﭨﻟ؟?0ﺅﺙ?



**ﮒﮒﭦﻝﭨﮔ**:

```json

{

  "code": 200,

  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",

  "data": {

    "total": 10,

    "page": 1,

    "page_size": 20,

    "accounts": [

      {

        "id": 1,

        "account_code": "ACC_20260402_001",

        "account_name": "ﻠﭨﻟ؟۳ﮔ۷۰ﮔﻟﺑ۵ﮔﺓ",

        "account_type": "simulation",

        "total_assets": 1200000.0000,

        "total_pnl": 200000.0000,

        "status": "active"

      }

    ]

  }

}

```



---



#### 1.2.4 ﮔﺑﮔﺍﻟﺑ۵ﮔﺓﻝﭘﮔ?



**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `PUT /api/v1/accounts/{account_id}/status`



**ﻟﺁﺓﮔﺎﮒﮔﺍ**:

```json

{

  "status": "frozen",

  "reason": "ﻠ۲ﮔ۶ﻟ۶۵ﮒ"

}

```



**ﮒﮒﭦﻝﭨﮔ**:

```json

{

  "code": 200,

  "message": "ﻝﭘﮔﮔﺑﮔﺍﮔﮒ?,

  "data": {

    "id": 1,

    "status": "frozen",

    "updated_at": "2026-04-02T16:00:00Z"

  }

}

```



**ﻛﺕﮒ۰ﻟ۶ﮒ**:

1. ﻝﭘﮔﻟﺛ؛ﮔ۱ﺅﺙactive ﻗ?frozen ﻗ?closed

2. closedﻝﭘﮔﻛﺕﮒﺁﻠ?

3. ﮒﭨﻝﭨﻟﺑ۵ﮔﺓﮔﭘﻠﻟ۵ﻟ؟ﺍﮒﺛﮒﮒ?



---



#### 1.2.5 ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶



**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/accounts/{account_id}/snapshots`



**ﻟﺁﺓﮔﺎﮒﮔﺍ**:

- `account_id`: ﻟﺑ۵ﮔﺓIDﺅﺙﻟﺓﺁﮒﺝﮒﮔﺍﺅﺙ

- `start_date`: ﮒﺙﮒ۶ﮔ۴ﮔﺅﺙﮒﺁﻠﺅﺙ

- `end_date`: ﻝﭨﮔﮔ۴ﮔﺅﺙﮒﺁﻠﺅﺙ

- `page`: ﻠ۰ﭖﻝﺅﺙﻠﭨﻟ؟?ﺅﺙ?

- `page_size`: ﮔﺁﻠ۰ﭖﮔﺍﻠﺅﺙﻠﭨﻟ؟?0ﺅﺙ?



**ﮒﮒﭦﻝﭨﮔ**:

```json

{

  "code": 200,

  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",

  "data": {

    "total": 90,

    "page": 1,

    "page_size": 30,

    "snapshots": [

      {

        "snapshot_date": "2026-04-02",

        "total_assets": 1200000.0000,

        "available_cash": 750000.0000,

        "total_market_value": 450000.0000,

        "daily_pnl": 10000.0000,

        "daily_pnl_pct": 0.008400,

        "cumulative_pnl": 200000.0000,

        "cumulative_pnl_pct": 0.200000,

        "max_drawdown": 0.050000,

        "sharpe_ratio": 1.500000,

        "win_rate": 0.650000

      }

    ]

  }

}

```



---



### 1.3 Repositoryﮔ۴ﮒ۲



#### 1.3.1 AccountRepository



```python

from abc import ABC, abstractmethod

from typing import List, Optional

from datetime import date

from decimal import Decimal



class AccountRepository(ABC):

    """ﻟﺑ۵ﮔﺓﻛﭨﮒ۷ﮔ۴ﮒ۲"""

    

    @abstractmethod

    async def create(self, account: Account) -> Account:

        """ﮒﮒﭨﭦﻟﺑ۵ﮔﺓ"""

        pass

    

    @abstractmethod

    async def find_by_id(self, account_id: int) -> Optional[Account]:

"""ﮔﺗﮔ؟IDﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ"""

        pass

    

    @abstractmethod

    async def find_by_code(self, account_code: str) -> Optional[Account]:

"""ﮔﺗﮔ؟ﻝﺙﻝﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ"""

        pass

    

    @abstractmethod

    async def find_all(

        self,

        account_type: Optional[str] = None,

        status: Optional[str] = None,

        page: int = 1,

        page_size: int = 20

    ) -> List[Account]:

        """ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮒﻟ۰۷"""

        pass

    

    @abstractmethod

    async def update(self, account: Account) -> Account:

        """ﮔﺑﮔﺍﻟﺑ۵ﮔﺓ"""

        pass

    

    @abstractmethod

    async def update_status(

        self,

        account_id: int,

        status: str,

        reason: Optional[str] = None

    ) -> bool:

        """ﮔﺑﮔﺍﻟﺑ۵ﮔﺓﻝﭘﮔ?""

        pass

    

    @abstractmethod

    async def update_capital(

        self,

        account_id: int,

        current_capital: Decimal,

        available_cash: Decimal,

        frozen_cash: Decimal,

        total_assets: Decimal

    ) -> bool:

        """ﮔﺑﮔﺍﻟﺑ۵ﮔﺓﻟﭖﻠ"""

        pass

    

    @abstractmethod

    async def create_snapshot(self, snapshot: AccountSnapshot) -> AccountSnapshot:

        """ﮒﮒﭨﭦﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶"""

        pass

    

    @abstractmethod

    async def find_snapshots(

        self,

        account_id: int,

        start_date: Optional[date] = None,

        end_date: Optional[date] = None,

        page: int = 1,

        page_size: int = 30

    ) -> List[AccountSnapshot]:

        """ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶"""

        pass

```



---



## 2. ﮔﻛﭨﮔﮒ۰ﮔ۴ﮒ۲ (PositionService)



### 2.1 ﮔﮒ۰ﮔ۵ﻟﺟﺍ



**ﮔﮒ۰ﮒﻝ۶ﺍ**: PositionService  

**ﮔﮒ۰ﻟﻟﺑ۲**: ﮔﻛﭨﻝ؟۰ﻝﻙﮔﻛﭨﮔ۴ﻟﺁ۱ﻙﮔﻛﭨﮒﮒ? 

**ﻛﺝﻟﭖﮔﮒ۰**: AccountService, TradeService  

**ﮔﺍﮔ؟ﻟ؟ﺟﻠ؟**: PositionRepository



### 2.2 ﮔ۴ﮒ۲ﮒ؟ﻛﺗ



#### 2.2.1 ﮔ۴ﻟﺁ۱ﮔﻛﭨ



**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/accounts/{account_id}/positions`



**ﻟﺁﺓﮔﺎﮒﮔﺍ**:

- `account_id`: ﻟﺑ۵ﮔﺓIDﺅﺙﻟﺓﺁﮒﺝﮒﮔﺍﺅﺙ

- `stock_code`: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝﺅﺙﮒﺁﻠﺅﺙ



**ﮒﮒﭦﻝﭨﮔ**:

```json

{

  "code": 200,

  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",

  "data": {

    "total_market_value": 450000.0000,

    "positions": [

      {

        "id": 1,

        "stock_code": "600000.SH",

        "stock_name": "ﮔﭖ۵ﮒﻠﭘﻟ۰",

        "exchange": "SH",

        "quantity": 10000,

        "available_quantity": 8000,

        "frozen_quantity": 2000,

        "avg_cost": 10.5000,

        "current_price": 12.8000,

        "market_value": 128000.0000,

        "unrealized_pnl": 23000.0000,

        "unrealized_pnl_pct": 0.219048,

        "realized_pnl": 5000.0000,

        "position_pct": 0.106667,

        "first_buy_date": "2026-01-15",

        "last_trade_date": "2026-04-02"

      }

    ]

  }

}

```



---



#### 2.2.2 ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒﮒﺎ



**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/positions/{position_id}/history`



**ﻟﺁﺓﮔﺎﮒﮔﺍ**:

- `position_id`: ﮔﻛﭨIDﺅﺙﻟﺓﺁﮒﺝﮒﮔﺍﺅﺙ

- `start_date`: ﮒﺙﮒ۶ﮔ۴ﮔﺅﺙﮒﺁﻠﺅﺙ

- `end_date`: ﻝﭨﮔﮔ۴ﮔﺅﺙﮒﺁﻠﺅﺙ

- `change_type`: ﮒﮔﺑﻝﺎﭨﮒﺅﺙﮒﺁﻠﺅﺙ

- `page`: ﻠ۰ﭖﻝﺅﺙﻠﭨﻟ؟?ﺅﺙ?

- `page_size`: ﮔﺁﻠ۰ﭖﮔﺍﻠﺅﺙﻠﭨﻟ؟?0ﺅﺙ?



**ﮒﮒﭦﻝﭨﮔ**:

```json

{

  "code": 200,

  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",

  "data": {

    "total": 15,

    "page": 1,

    "page_size": 50,

    "history": [

      {

        "id": 1,

        "position_id": 1,

        "stock_code": "600000.SH",

        "change_type": "buy",

        "quantity_before": 5000,

        "quantity_after": 10000,

        "quantity_change": 5000,

        "price": 11.2000,

        "amount": 56000.0000,

        "trade_id": 12345,

        "created_at": "2026-04-02T10:30:00Z"

      }

    ]

  }

}

```



---



### 2.3 Repositoryﮔ۴ﮒ۲



#### 2.3.1 PositionRepository



```python

from abc import ABC, abstractmethod

from typing import List, Optional

from datetime import date

from decimal import Decimal



class PositionRepository(ABC):

    """ﮔﻛﭨﻛﭨﮒ۷ﮔ۴ﮒ۲"""

    

    @abstractmethod

    async def create(self, position: Position) -> Position:

        """ﮒﮒﭨﭦﮔﻛﭨ"""

        pass

    

    @abstractmethod

    async def find_by_id(self, position_id: int) -> Optional[Position]:

"""ﮔﺗﮔ؟IDﮔ۴ﻟﺁ۱ﮔﻛﭨ"""

        pass

    

    @abstractmethod

    async def find_by_account_and_stock(

        self,

        account_id: int,

        stock_code: str

    ) -> Optional[Position]:

"""ﮔﺗﮔ؟ﻟﺑ۵ﮔﺓﮒﻟ۰ﻝ۴۷ﮔ۴ﻟﺁ۱ﮔﻛﭨ?""

        pass

    

    @abstractmethod

    async def find_by_account(

        self,

        account_id: int,

        stock_code: Optional[str] = None

    ) -> List[Position]:

        """ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮔﻛﭨ"""

        pass

    

    @abstractmethod

    async def update(self, position: Position) -> Position:

        """ﮔﺑﮔﺍﮔﻛﭨ"""

        pass

    

    @abstractmethod

    async def update_quantity(

        self,

        position_id: int,

        quantity: int,

        available_quantity: int,

        frozen_quantity: int,

        avg_cost: Decimal

    ) -> bool:

        """ﮔﺑﮔﺍﮔﻛﭨﮔﺍﻠ"""

        pass

    

    @abstractmethod

    async def update_price(

        self,

        position_id: int,

        current_price: Decimal,

        market_value: Decimal,

        unrealized_pnl: Decimal,

        unrealized_pnl_pct: Decimal

    ) -> bool:

"""ﮔﺑﮔﺍﮔﻛﭨﻛﭨﺓﮔﺙ"""

        pass

    

    @abstractmethod

    async def create_history(self, history: PositionHistory) -> PositionHistory:

        """ﮒﮒﭨﭦﮔﻛﭨﮒﮒﺎ"""

        pass

    

    @abstractmethod

    async def find_history(

        self,

        position_id: int,

        start_date: Optional[date] = None,

        end_date: Optional[date] = None,

        change_type: Optional[str] = None,

        page: int = 1,

        page_size: int = 50

    ) -> List[PositionHistory]:

        """ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒﮒﺎ"""

        pass

```



---



## 3. ﻟ؟۱ﮒﮔﮒ۰ﮔ۴ﮒ۲ (OrderService)



### 3.1 ﮔﮒ۰ﮔ۵ﻟﺟﺍ



**ﮔﮒ۰ﮒﻝ۶ﺍ**: OrderService  

**ﮔﮒ۰ﻟﻟﺑ۲**: ﻟ؟۱ﮒﻝ؟۰ﻝﻙﻟ؟۱ﮒﮔ۶ﻟ۰ﻙﻟ؟۱ﮒﮔ۴ﻟﺁ? 

**ﻛﺝﻟﭖﮔﮒ۰**: AccountService, PositionService, EngineService  

**ﮔﺍﮔ؟ﻟ؟ﺟﻠ؟**: OrderRepository



### 3.2 ﮔ۴ﮒ۲ﮒ؟ﻛﺗ



#### 3.2.1 ﮒﮒﭨﭦﻟ؟۱ﮒ



**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `POST /api/v1/orders`



**ﻟﺁﺓﮔﺎﮒﮔﺍ**:

```json

{

  "account_id": 1,

  "signal_id": 100,

  "strategy_id": "STRAT_001",

  "stock_code": "600000.SH",

  "exchange": "SH",

  "direction": "buy",

  "order_type": "limit",

  "order_price": 12.5000,

  "order_quantity": 10000,

  "engine_id": "VNPY_001"

}

```



**ﮒﮒﭦﻝﭨﮔ**:

```json

{

  "code": 200,

  "message": "ﻟ؟۱ﮒﮒﮒﭨﭦﮔﮒ",

  "data": {

    "id": 1,

    "order_code": "ORD_20260402_001",

    "account_id": 1,

    "signal_id": 100,

    "strategy_id": "STRAT_001",

    "stock_code": "600000.SH",

    "stock_name": "ﮔﭖ۵ﮒﻠﭘﻟ۰",

    "exchange": "SH",

    "direction": "buy",

    "order_type": "limit",

    "order_price": 12.5000,

    "order_quantity": 10000,

    "filled_quantity": 0,

    "filled_amount": 0.0000,

    "status": "pending",

    "engine_id": "VNPY_001",

    "created_at": "2026-04-02T10:00:00Z",

    "updated_at": "2026-04-02T10:00:00Z"

  }

}

```



**ﻛﺕﮒ۰ﻟ۶ﮒ**:

1. ﻟ؟۱ﮒﻝﺙﻝﻟ۹ﮒ۷ﻝﮔﺅﺙORD_YYYYMMDD_XXX

2. ﻛﺗﺍﮒ۴ﻟ؟۱ﮒﺅﺙﮔ۲ﮔ۴ﮒﺁﻝ۷ﻟﭖﻠﮔﺁﮒ۵ﮒﻟﭘ?

3. ﮒﮒﭦﻟ؟۱ﮒﺅﺙﮔ۲ﮔ۴ﮒﺁﻝ۷ﮔﻛﭨﮔﺁﮒ۵ﮒﻟﭘ?

4. ﻠ۲ﮔ۶ﮔ۲ﮔ۴ﺅﺙﻟﺍﻝ۷RiskServiceﻟﺟﻟ۰ﻠ۲ﮔ۶ﮔ۲ﮔ?



---



#### 3.2.2 ﮔﻛﭦ۳ﻟ؟۱ﮒ



**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `POST /api/v1/orders/{order_id}/submit`



**ﻟﺁﺓﮔﺎﮒﮔﺍ**:

- `order_id`: ﻟ؟۱ﮒIDﺅﺙﻟﺓﺁﮒﺝﮒﮔﺍﺅﺙ



**ﮒﮒﭦﻝﭨﮔ**:

```json

{

  "code": 200,

  "message": "ﻟ؟۱ﮒﮔﻛﭦ۳ﮔﮒ",

  "data": {

    "id": 1,

    "order_code": "ORD_20260402_001",

    "status": "submitted",

    "broker_order_id": "123456789",

    "engine_id": "VNPY_001",

    "submitted_at": "2026-04-02T10:01:00Z"

  }

}

```



**ﻛﺕﮒ۰ﻟ۶ﮒ**:

1. ﮒ۹ﮔpendingﻝﭘﮔﻝﻟ؟۱ﮒﮒﺁﻛﭨ۴ﮔﻛﭦ۳

2. ﮔﻛﭦ۳ﮒﻟﺟﻟ۰ﻠ۲ﮔ۶ﮔ۲ﮔ?

3. ﮔﻛﭦ۳ﮒﮒﭨﻝﭨﻟﭖﻠﮔﮔﻛﭨ

4. ﻟﺍﻝ۷EngineServiceﮔ۶ﻟ۰ﻟ؟۱ﮒ



---



#### 3.2.3 ﮒﮔﭘﻟ؟۱ﮒ



**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `POST /api/v1/orders/{order_id}/cancel`



**ﻟﺁﺓﮔﺎﮒﮔﺍ**:

- `order_id`: ﻟ؟۱ﮒIDﺅﺙﻟﺓﺁﮒﺝﮒﮔﺍﺅﺙ



**ﮒﮒﭦﻝﭨﮔ**:

```json

{

  "code": 200,

  "message": "ﻟ؟۱ﮒﮒﮔﭘﮔﮒ",

  "data": {

    "id": 1,

    "order_code": "ORD_20260402_001",

    "status": "cancelled",

    "cancelled_at": "2026-04-02T10:05:00Z"

  }

}

```



**ﻛﺕﮒ۰ﻟ۶ﮒ**:

1. ﮒ۹ﮔpendingﮔsubmittedﻝﭘﮔﻝﻟ؟۱ﮒﮒﺁﻛﭨ۴ﮒﮔﭘ

2. ﮒﮔﭘﮒﻠﮔﺝﮒﭨﻝﭨﻝﻟﭖﻠﮔﮔﻛﭨ?

3. ﻟﺍﻝ۷EngineServiceﮒﮔﭘﻟ؟۱ﮒ



---



#### 3.2.4 ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ



**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/orders/{order_id}`



**ﻟﺁﺓﮔﺎﮒﮔﺍ**:

- `order_id`: ﻟ؟۱ﮒIDﺅﺙﻟﺓﺁﮒﺝﮒﮔﺍﺅﺙ



**ﮒﮒﭦﻝﭨﮔ**:

```json

{

  "code": 200,

  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",

  "data": {

    "id": 1,

    "order_code": "ORD_20260402_001",

    "account_id": 1,

    "signal_id": 100,

    "strategy_id": "STRAT_001",

    "stock_code": "600000.SH",

    "stock_name": "ﮔﭖ۵ﮒﻠﭘﻟ۰",

    "exchange": "SH",

    "direction": "buy",

    "order_type": "limit",

    "order_price": 12.5000,

    "order_quantity": 10000,

    "filled_price": 12.4800,

    "filled_quantity": 10000,

    "filled_amount": 124800.0000,

    "commission": 62.4000,

    "stamp_tax": 0.0000,

    "transfer_fee": 12.4800,

    "total_cost": 124874.8800,

    "status": "filled",

    "engine_id": "VNPY_001",

    "broker_order_id": "123456789",

    "created_at": "2026-04-02T10:00:00Z",

    "updated_at": "2026-04-02T10:05:00Z",

    "filled_at": "2026-04-02T10:05:00Z"

  }

}

```



---



#### 3.2.5 ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮒﻟ۰۷



**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/orders`



**ﻟﺁﺓﮔﺎﮒﮔﺍ**:

- `account_id`: ﻟﺑ۵ﮔﺓIDﺅﺙﮒﺁﻠﺅﺙ

- `stock_code`: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝﺅﺙﮒﺁﻠﺅﺙ

- `status`: ﻟ؟۱ﮒﻝﭘﮔﺅﺙﮒﺁﻠﺅﺙ

- `direction`: ﻛﭦ۳ﮔﮔﺗﮒﺅﺙﮒﺁﻠﺅﺙ

- `start_date`: ﮒﺙﮒ۶ﮔ۴ﮔﺅﺙﮒﺁﻠﺅﺙ

- `end_date`: ﻝﭨﮔﮔ۴ﮔﺅﺙﮒﺁﻠﺅﺙ

- `page`: ﻠ۰ﭖﻝﺅﺙﻠﭨﻟ؟?ﺅﺙ?

- `page_size`: ﮔﺁﻠ۰ﭖﮔﺍﻠﺅﺙﻠﭨﻟ؟?0ﺅﺙ?



**ﮒﮒﭦﻝﭨﮔ**:

```json

{

  "code": 200,

  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",

  "data": {

    "total": 50,

    "page": 1,

    "page_size": 20,

    "orders": [

      {

        "id": 1,

        "order_code": "ORD_20260402_001",

        "account_id": 1,

        "stock_code": "600000.SH",

        "stock_name": "ﮔﭖ۵ﮒﻠﭘﻟ۰",

        "direction": "buy",

        "order_type": "limit",

        "order_price": 12.5000,

        "order_quantity": 10000,

        "filled_quantity": 10000,

        "filled_amount": 124800.0000,

        "status": "filled",

        "created_at": "2026-04-02T10:00:00Z"

      }

    ]

  }

}

```



---



### 3.3 Repositoryﮔ۴ﮒ۲



#### 3.3.1 OrderRepository



```python

from abc import ABC, abstractmethod

from typing import List, Optional

from datetime import date, datetime

from decimal import Decimal



class OrderRepository(ABC):

    """ﻟ؟۱ﮒﻛﭨﮒ۷ﮔ۴ﮒ۲"""

    

    @abstractmethod

    async def create(self, order: Order) -> Order:

        """ﮒﮒﭨﭦﻟ؟۱ﮒ"""

        pass

    

    @abstractmethod

    async def find_by_id(self, order_id: int) -> Optional[Order]:

"""ﮔﺗﮔ؟IDﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ"""

        pass

    

    @abstractmethod

    async def find_by_code(self, order_code: str) -> Optional[Order]:

"""ﮔﺗﮔ؟ﻝﺙﻝﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ"""

        pass

    

    @abstractmethod

    async def find_all(

        self,

        account_id: Optional[int] = None,

        stock_code: Optional[str] = None,

        status: Optional[str] = None,

        direction: Optional[str] = None,

        start_date: Optional[date] = None,

        end_date: Optional[date] = None,

        page: int = 1,

        page_size: int = 20

    ) -> List[Order]:

        """ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮒﻟ۰۷"""

        pass

    

    @abstractmethod

    async def update(self, order: Order) -> Order:

        """ﮔﺑﮔﺍﻟ؟۱ﮒ"""

        pass

    

    @abstractmethod

    async def update_status(

        self,

        order_id: int,

        status: str,

        reject_reason: Optional[str] = None

    ) -> bool:

        """ﮔﺑﮔﺍﻟ؟۱ﮒﻝﭘﮔ?""

        pass

    

    @abstractmethod

    async def update_fill(

        self,

        order_id: int,

        filled_price: Decimal,

        filled_quantity: int,

        filled_amount: Decimal,

        commission: Decimal,

        stamp_tax: Decimal,

        transfer_fee: Decimal,

        total_cost: Decimal

    ) -> bool:

        """ﮔﺑﮔﺍﻟ؟۱ﮒﮔﻛﭦ۳ﻛﺟ۰ﮔﺁ"""

        pass

    

    @abstractmethod

    async def find_active_orders(

        self,

        account_id: int,

        stock_code: Optional[str] = None

    ) -> List[Order]:

        """ﮔ۴ﻟﺁ۱ﮔﺑﭨﻟﺓﻟ؟۱ﮒ"""

        pass

```



---



## 4. ﻛﭦ۳ﮔﮔﮒ۰ﮔ۴ﮒ۲ (TradeService)



### 4.1 ﮔﮒ۰ﮔ۵ﻟﺟﺍ



**ﮔﮒ۰ﮒﻝ۶ﺍ**: TradeService  

**ﮔﮒ۰ﻟﻟﺑ۲**: ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﻝ؟۰ﻝﻙﻛﭦ۳ﮔﮔ۴ﻟﺁ۱ﻙﻛﭦ۳ﮔﻝﭨﻟ؟? 

**ﻛﺝﻟﭖﮔﮒ۰**: OrderService, PositionService  

**ﮔﺍﮔ؟ﻟ؟ﺟﻠ؟**: TradeRepository



### 4.2 ﮔ۴ﮒ۲ﮒ؟ﻛﺗ



#### 4.2.1 ﮒﮒﭨﭦﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ



**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `POST /api/v1/trades`



**ﻟﺁﺓﮔﺎﮒﮔﺍ**:

```json

{

  "order_id": 1,

  "account_id": 1,

  "stock_code": "600000.SH",

  "direction": "buy",

  "trade_price": 12.4800,

  "trade_quantity": 10000,

  "trade_amount": 124800.0000,

  "commission": 62.4000,

  "stamp_tax": 0.0000,

  "transfer_fee": 12.4800,

  "total_cost": 124874.8800,

  "net_amount": 124874.8800,

  "engine_id": "VNPY_001",

  "broker_trade_id": "987654321",

  "traded_at": "2026-04-02T10:05:00Z"

}

```



**ﮒﮒﭦﻝﭨﮔ**:

```json

{

  "code": 200,

  "message": "ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﮒﮒﭨﭦﮔﮒ",

  "data": {

    "id": 1,

    "trade_code": "TRD_20260402_001",

    "order_id": 1,

    "account_id": 1,

    "stock_code": "600000.SH",

    "direction": "buy",

    "trade_price": 12.4800,

    "trade_quantity": 10000,

    "trade_amount": 124800.0000,

    "commission": 62.4000,

    "stamp_tax": 0.0000,

    "transfer_fee": 12.4800,

    "total_cost": 124874.8800,

    "net_amount": 124874.8800,

    "engine_id": "VNPY_001",

    "broker_trade_id": "987654321",

    "traded_at": "2026-04-02T10:05:00Z",

    "created_at": "2026-04-02T10:05:00Z"

  }

}

```



---



#### 4.2.2 ﮔ۴ﻟﺁ۱ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ



**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/trades/{trade_id}`



**ﻟﺁﺓﮔﺎﮒﮔﺍ**:

- `trade_id`: ﻛﭦ۳ﮔIDﺅﺙﻟﺓﺁﮒﺝﮒﮔﺍﺅﺙ



**ﮒﮒﭦﻝﭨﮔ**:

```json

{

  "code": 200,

  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",

  "data": {

    "id": 1,

    "trade_code": "TRD_20260402_001",

    "order_id": 1,

    "account_id": 1,

    "stock_code": "600000.SH",

    "direction": "buy",

    "trade_price": 12.4800,

    "trade_quantity": 10000,

    "trade_amount": 124800.0000,

    "commission": 62.4000,

    "stamp_tax": 0.0000,

    "transfer_fee": 12.4800,

    "total_cost": 124874.8800,

    "net_amount": 124874.8800,

    "engine_id": "VNPY_001",

    "broker_trade_id": "987654321",

    "traded_at": "2026-04-02T10:05:00Z",

    "created_at": "2026-04-02T10:05:00Z"

  }

}

```



---



#### 4.2.3 ﮔ۴ﻟﺁ۱ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﮒﻟ۰۷



**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/trades`



**ﻟﺁﺓﮔﺎﮒﮔﺍ**:

- `account_id`: ﻟﺑ۵ﮔﺓIDﺅﺙﮒﺁﻠﺅﺙ

- `stock_code`: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝﺅﺙﮒﺁﻠﺅﺙ

- `direction`: ﻛﭦ۳ﮔﮔﺗﮒﺅﺙﮒﺁﻠﺅﺙ

- `start_date`: ﮒﺙﮒ۶ﮔ۴ﮔﺅﺙﮒﺁﻠﺅﺙ

- `end_date`: ﻝﭨﮔﮔ۴ﮔﺅﺙﮒﺁﻠﺅﺙ

- `page`: ﻠ۰ﭖﻝﺅﺙﻠﭨﻟ؟?ﺅﺙ?

- `page_size`: ﮔﺁﻠ۰ﭖﮔﺍﻠﺅﺙﻠﭨﻟ؟?0ﺅﺙ?



**ﮒﮒﭦﻝﭨﮔ**:

```json

{

  "code": 200,

  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",

  "data": {

    "total": 100,

    "page": 1,

    "page_size": 20,

    "trades": [

      {

        "id": 1,

        "trade_code": "TRD_20260402_001",

        "order_id": 1,

        "account_id": 1,

        "stock_code": "600000.SH",

        "direction": "buy",

        "trade_price": 12.4800,

        "trade_quantity": 10000,

        "trade_amount": 124800.0000,

        "total_cost": 124874.8800,

        "traded_at": "2026-04-02T10:05:00Z"

      }

    ]

  }

}

```



---



### 4.3 Repositoryﮔ۴ﮒ۲



#### 4.3.1 TradeRepository



```python

from abc import ABC, abstractmethod

from typing import List, Optional

from datetime import date, datetime

from decimal import Decimal



class TradeRepository(ABC):

    """ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﻛﭨﮒ۷ﮔ۴ﮒ۲"""

    

    @abstractmethod

    async def create(self, trade: Trade) -> Trade:

        """ﮒﮒﭨﭦﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ"""

        pass

    

    @abstractmethod

    async def find_by_id(self, trade_id: int) -> Optional[Trade]:

"""ﮔﺗﮔ؟IDﮔ۴ﻟﺁ۱ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ"""

        pass

    

    @abstractmethod

    async def find_by_code(self, trade_code: str) -> Optional[Trade]:

"""ﮔﺗﮔ؟ﻝﺙﻝﮔ۴ﻟﺁ۱ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ"""

        pass

    

    @abstractmethod

    async def find_all(

        self,

        account_id: Optional[int] = None,

        stock_code: Optional[str] = None,

        direction: Optional[str] = None,

        start_date: Optional[date] = None,

        end_date: Optional[date] = None,

        page: int = 1,

        page_size: int = 20

    ) -> List[Trade]:

        """ﮔ۴ﻟﺁ۱ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﮒﻟ۰۷"""

        pass

    

    @abstractmethod

    async def find_by_order(self, order_id: int) -> List[Trade]:

"""ﮔﺗﮔ؟ﻟ؟۱ﮒﮔ۴ﻟﺁ۱ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ"""

        pass

    

    @abstractmethod

    async def calculate_statistics(

        self,

        account_id: int,

        start_date: Optional[date] = None,

        end_date: Optional[date] = None

    ) -> dict:

        """ﻟ؟۰ﻝ؟ﻛﭦ۳ﮔﻝﭨﻟ؟۰"""

        pass

```



---



## 5. ﮔ۴ﮒ۲ﻠﻝ۷ﻟ۶ﻟ



### 5.1 ﮒﮒﭦﮔﺙﮒﺙ



**ﮔﮒﮒﮒﭦ**:

```json

{

  "code": 200,

  "message": "ﮔﻛﺛﮔﮒ",

  "data": {

    // ﻛﺕﮒ۰ﮔﺍﮔ؟

  }

}

```



**ﻠﻟﺁﺁﮒﮒﭦ**:

```json

{

  "code": 400,

  "message": "ﮒﮔﺍﻠﻟﺁﺁ",

  "error": {

    "field": "account_id",

"reason": "ﻟﺑ۵ﮔﺓIDﻛﺕﮒﮒ?

  }

}

```



### 5.2 ﻠﻟﺁﺁﻝﮒ؟ﻛﺗ?



| ﻠﻟﺁﺁﻝ?| ﻟﺁﺑﮔ | ﻝ۳ﭦﻛﺝ |

|--------|------|------|

| **200** | ﮔﮒ | ﮔﻛﺛﮔﮒ |

| **400** | ﮒﮔﺍﻠﻟﺁﺁ | ﮒﮔﺍﻝﺙﭦﮒ۳ﺎﮔﮔﺙﮒﺙﻠﻟﺁ?|

| **401** | ﮔ۹ﮔﮔ?| ﮔ۹ﻝﭨﮒﺛﮔtokenﻟﺟﮔ |

| **403** | ﮔﮔﻠ?| ﮔﮔﻛﺛﮔﻠ?|

| **404** | ﻟﭖﮔﭦﻛﺕﮒﮒ?| ﻟﺑ۵ﮔﺓﻛﺕﮒﮒ?|

| **409** | ﻛﺕﮒ۰ﮒﺎﻝ۹ | ﻟﺑ۵ﮔﺓﮒﺓﺎﮒﮒ?|

| **500** | ﮔﮒ۰ﮒ۷ﻠﻟﺁ?| ﻝﺏﭨﻝﭨﮒﻠ۷ﻠﻟﺁﺁ |



### 5.3 ﮒﻠ۰ﭖﻟ۶ﻟ



**ﻟﺁﺓﮔﺎﮒﮔﺍ**:

- `page`: ﻠ۰ﭖﻝﺅﺙﻛﭨ1ﮒﺙﮒ۶ﺅﺙ

- `page_size`: ﮔﺁﻠ۰ﭖﮔﺍﻠﺅﺙﻠﭨﻟ؟?0ﺅﺙﮔﮒ۳?00ﺅﺙ?



**ﮒﮒﭦﮔﺙﮒﺙ**:

```json

{

  "code": 200,

  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",

  "data": {

    "total": 100,

    "page": 1,

    "page_size": 20,

    "items": []

  }

}

```



### 5.4 ﮔﭘﻠﺑﮔﺙﮒﺙ



- **ﮔ۴ﮔ**: `YYYY-MM-DD` (ﮒ۵? 2026-04-02)

- **ﮔﭘﻠﺑﮔ?*: `YYYY-MM-DDTHH:MM:SSZ` (ﮒ۵? 2026-04-02T10:00:00Z)

- **ﮔﭘﮒﭦ**: UTC



### 5.5 ﻠﻠ۱ﮔﺙﮒﺙ



- **ﻝﺎﺝﮒﭦ۵**: 4ﻛﺛﮒﺍﮔﺍﺅﺙDECIMAL(20,4)ﺅﺙ?

- **ﮒﻛﺛ**: ﮒﺅﺙﻛﭦﭦﮔﺍﮒﺕﺅﺙ

- **ﻝ۳ﭦﻛﺝ**: 1000000.0000



---



## 6. ﮔ۶ﻟﺛﻟ۵ﮔﺎ



### 6.1 ﮒﮒﭦﮔﭘﻠﺑ



| ﮔ۴ﮒ۲ﻝﺎﭨﮒ | ﮒﮒﭦﮔﭘﻠﺑﻟ۵ﮔﺎ | ﮒ۳ﮔﺏ۷ |

|----------|--------------|------|

| **ﮔ۴ﻟﺁ۱ﮔ۴ﮒ۲** | < 200ms | ﻝ؟ﮒﮔ۴ﻟﺁ?|

| **ﮒﻟ۰۷ﮔ۴ﮒ۲** | < 500ms | ﮒﻠ۰ﭖﮔ۴ﻟﺁ۱ |

| **ﮒﮒﭨﭦﮔ۴ﮒ۲** | < 300ms | ﮔﺍﮔ؟ﮒﮒ۴ |

| **ﮔﺑﮔﺍﮔ۴ﮒ۲** | < 300ms | ﮔﺍﮔ؟ﮔﺑﮔﺍ |

| **ﻝﭨﻟ؟۰ﮔ۴ﮒ۲** | < 1000ms | ﮒ۳ﮔﻟ؟۰ﻝ؟ |



### 6.2 ﮒﺗﭘﮒﻟ۵ﮔﺎ



- **ﮒﺗﭘﮒﻝ۷ﮔﺓﮔ?*: 100

- **QPS**: 1000

- **TPS**: 500



### 6.3 ﻝﺙﮒﻝﻝ۴



| ﮔﺍﮔ؟ﻝﺎﭨﮒ | ﻝﺙﮒﮔﭘﻠﺑ | ﻝﺙﮒﻝﻝ۴ |

|----------|----------|----------|

| **ﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁ** | 5ﮒﻠ | Redisﻝﺙﮒ |

| **ﮔﻛﭨﻛﺟ۰ﮔﺁ** | 1ﮒﻠ | Redisﻝﺙﮒ |

| **ﻟ؟۱ﮒﻛﺟ۰ﮔﺁ** | ﻛﺕﻝﺙﮒ?| ﮒ؟ﮔﭘﮔ۴ﻟﺁ۱ |

| **ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ** | ﻛﺕﻝﺙﮒ?| ﮒ؟ﮔﭘﮔ۴ﻟﺁ۱ |



---



## 7. ﮒ؟ﮒ۷ﻟ۵ﮔﺎ



### 7.1 ﻟ؟۳ﻟﺁﮔﮔ



- **ﻟ؟۳ﻟﺁﮔﺗﮒﺙ**: JWT Token

- **Tokenﮔﮔﮔ?*: 2ﮒﺍﮔﭘ

- **ﮒﺓﮔﺍToken**: 7ﮒ۳?



### 7.2 ﮔﺍﮔ؟ﮒﮒﺁ



- **ﻛﺙﻟﺝﮒﮒﺁ**: HTTPS

- **ﮔﮔﮔﺍﮔ؟**: AESﮒﮒﺁﮒﮒ۷

- **ﮒﺁﻝ**: BCryptﮒﮒﺕ



### 7.3 ﻟ؟ﺟﻠ؟ﮔ۶ﮒﭘ



- **RBAC**: ﮒﭦﻛﭦﻟ۶ﻟﺎﻝﻟ؟ﺟﻠ؟ﮔ۶ﮒ?

- **ﮔﻠﻝﺎﮒﭦ۵**: ﮔ۴ﮒ۲ﻝﭦ۶ﮒ،

- **ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ**: ﻟ؟ﺍﮒﺛﮔﮔﮔﻛﺛ?



---



**ﻝﮔ؛**: 1.0.0 | **ﮔﺑﮔﺍﮔ۴ﮔ**: 2026-04-02 | **ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ? 

**ﻛﺕﻛﺕﮔ?*: P0-4 ﻝ؛؛ﻛﺕﮔﺗﮔ۴ﮒ۲ﻠﮔﻟ؟ﺝﻟ؟

