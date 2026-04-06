---
module_id: INTERNAL_API_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﻟﮒﺝﮔﭘﮔﮒﺕ?
responsibility:
  - 因子计算
  - 交易执行
  - 数据源
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮒﻠ۷ﮔﮒ۰ﮔ۴ﮒ۲ﮔ ﮒ
applicable_scope: ﮒ۷ﻝﺏﭨﻝﭨﮔﮒ۰ﮔ۴ﮒ?
compliance_level: ﻛﺕﻛﺕﮔﭦﮔﮔ ﮒ
parent_document: P0-01_Database_Design_Document.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?---


# ﮒﻠ۷ﮔﮒ۰ﮔ۴ﮒ۲ﻟ؟ﺝﻟ؟۰ﺅﺙﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒﺅﺙ

> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.0 - ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒﮒﻠ۷ﮔﮒ۰ﮔ۴ﮒ۲ﻟ؟ﺝﻟ؟۰
> **ﮔﭘﮔﮔ۷۰ﮒﺙ**: ﮒﺝ؟ﮔﮒ۰ﮔﭘﮔ?+ DDDﻠ۱ﮒﻠ۸ﺎﮒ۷ﻟ؟ﺝﻟ؟۰
> **ﮔ۴ﮒ۲ﮒﻟ؟؟**: RESTful API + gRPC
> **ﻟ؟ﺝﻟ؟۰ﮒﮒ**: ﮔ۴ﮒ۲ﮒﻟ۰ﻙﮒ۴ﻝﭦ۵ﻛﺙﮒﻙﮔﺝﻟ۵ﮒﻙﻠ،ﮒﻟ

## ﻭ ﮔ۴ﮒ۲ﻟ؟ﺝﻟ؟۰ﮔ۵ﻟﺟﺍ

### ﮔﮒ۰ﮔﭘﮔﮒﮒﺎ

```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﮒﭦﻝ۷ﮒﺎ?(Application Layer)                ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗ? ﻛﭦ۳ﮔﮒﭦﻝ۷ﮔﮒ۰ ﻗ? ﻗ? ﻝ­ﻝ۴ﮒﭦﻝ۷ﮔﮒ۰ ﻗ? ﻗ? ﻠ۲ﮔ۶ﮒﭦﻝ۷ﮔﮒ۰ ﻗ?     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
                            ﻗ?API Gateway
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﮔﮒ۰ﮒﺎ?(Service Layer)                    ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗ? ﻟﺑ۵ﮔﺓﮔﮒ۰     ﻗ? ﻗ? ﮔﻛﭨﮔﮒ۰     ﻗ? ﻗ? ﻟ؟۱ﮒﮔﮒ۰     ﻗ?     ﻗ?
ﻗ? ﻗ?AccountServiceﻗ? ﻗPositionServiceﻗ? ﻗ?OrderService ﻗ?     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗ? ﻛﭦ۳ﮔﮔﮒ۰     ﻗ? ﻗ? ﻛﺟ۰ﮒﺓﮔﮒ۰     ﻗ? ﻗ? ﮒﺙﮔﮔﮒ۰     ﻗ?     ﻗ?
ﻗ? ﻗ?TradeService ﻗ? ﻗSignalService ﻗ? ﻗEngineService ﻗ?     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
                            ﻗ?Repository Interface
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﻠ۱ﮒﮒﺎ?(Domain Layer)                     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗ? ﻟﺑ۵ﮔﺓﻟﮒ     ﻗ? ﻗ? ﮔﻛﭨﻟﮒ     ﻗ? ﻗ? ﻟ؟۱ﮒﻟﮒ     ﻗ?     ﻗ?
ﻗ? ﻗAccountAggregateﻗ?ﻗPositionAggregateﻗ?ﻗOrderAggregateﻗ?   ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗ? ﻛﭦ۳ﮔﻟﮒ     ﻗ? ﻗ? ﻛﺟ۰ﮒﺓﻟﮒ     ﻗ? ﻗ? Sagaﻟﮒ     ﻗ?     ﻗ?
ﻗ? ﻗTradeAggregate ﻗ? ﻗSignalAggregateﻗ? ﻗSagaAggregate ﻗ?     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
                            ﻗ?Repository Implementation
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﮒﭦﻝ۰ﻟ؟ﺝﮔﺛﮒﺎ?(Infrastructure Layer)          ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗ? ﻗ?PostgreSQL   ﻗ? ﻗ?   Redis     ﻗ? ﻗ?ClickHouse   ﻗ?     ﻗ?
ﻗ? ﻗ? (ﻛﺕﭨﮔﺍﮔ؟ﮒﭦ)   ﻗ? ﻗ? (ﮒ؟ﮔﭘﻝﺙﮒ­)  ﻗ? ﻗ?(ﮔﭘﮒﭦﮔﺍﮔ؟)   ﻗ?     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?     ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
```

---

## 1. ﻟﺑ۵ﮔﺓﮔﮒ۰ﮔ۴ﮒ۲ (AccountService)

### 1.1 ﮔﮒ۰ﮔ۵ﻟﺟﺍ

**ﮔﮒ۰ﮒﻝ۶ﺍ**: AccountService  
**ﮔﮒ۰ﻟﻟﺑ۲**: ﻟﺑ۵ﮔﺓﻝ؟۰ﻝﻙﻟﭖﻠﻝ؟۰ﻝﻙﻟﺑ۵ﮔﺓﮒﺟ،ﻝ? 
**ﻛﺝﻟﭖﮔﮒ۰**: PositionService, OrderService  
**ﮔﺍﮔ؟ﻟ؟ﺟﻠ؟**: AccountRepository

### 1.2 ﮔ۴ﮒ۲ﮒ؟ﻛﺗ

#### 1.2.1 ﮒﮒﭨﭦﻟﺑ۵ﮔﺓ

**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `POST /api/v1/accounts`

**ﻟﺁﺓﮔﺎﮒﮔﺍ**:
```json
{
  "account_name": "ﻠﭨﻟ؟۳ﮔ۷۰ﮔﻟﺑ۵ﮔﺓ",
  "account_type": "simulation",
  "initial_capital": 1000000.0000,
  "broker": "ﮒﮔﺏﺍﻟﺁﮒﺕ"
}
```

**ﮒﮒﭦﻝﭨﮔ**:
```json
{
  "code": 200,
  "message": "ﻟﺑ۵ﮔﺓﮒﮒﭨﭦﮔﮒ",
  "data": {
    "id": 1,
    "account_code": "ACC_20260402_001",
    "account_name": "ﻠﭨﻟ؟۳ﮔ۷۰ﮔﻟﺑ۵ﮔﺓ",
    "account_type": "simulation",
    "broker": "ﮒﮔﺏﺍﻟﺁﮒﺕ",
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

**ﻛﺕﮒ۰ﻟ۶ﮒ**:
1. ﻟﺑ۵ﮔﺓﻝﺙﻝ ﻟ۹ﮒ۷ﻝﮔﺅﺙACC_YYYYMMDD_XXX
2. ﮒﮒ۶ﻟﭖﻠﮒﺟﻠ۰ﭨ > 0
3. ﮒ؟ﻝﻟﺑ۵ﮔﺓﮒﺟﻠ۰ﭨﮒ۰،ﮒﮒﺕﮒﮒﻝ۶ﺍ

---

#### 1.2.2 ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ

**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/accounts/{account_id}`

**ﻟﺁﺓﮔﺎﮒﮔﺍ**:
- `account_id`: ﻟﺑ۵ﮔﺓIDﺅﺙﻟﺓﺁﮒﺝﮒﮔﺍﺅﺙ

**ﮒﮒﭦﻝﭨﮔ**:
```json
{
  "code": 200,
  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",
  "data": {
    "id": 1,
    "account_code": "ACC_20260402_001",
    "account_name": "ﻠﭨﻟ؟۳ﮔ۷۰ﮔﻟﺑ۵ﮔﺓ",
    "account_type": "simulation",
    "broker": "ﮒﮔﺏﺍﻟﺁﮒﺕ",
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
        "stock_name": "ﮔﭖ۵ﮒﻠﭘﻟ۰",
        "quantity": 10000,
        "market_value": 128000.0000
      }
    ]
  }
}
```

---

#### 1.2.3 ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮒﻟ۰۷

**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/accounts`

**ﻟﺁﺓﮔﺎﮒﮔﺍ**:
- `account_type`: ﻟﺑ۵ﮔﺓﻝﺎﭨﮒﺅﺙﮒﺁﻠﺅﺙ
- `status`: ﻟﺑ۵ﮔﺓﻝﭘﮔﺅﺙﮒﺁﻠﺅﺙ
- `page`: ﻠ۰ﭖﻝ ﺅﺙﻠﭨﻟ؟?ﺅﺙ?
- `page_size`: ﮔﺁﻠ۰ﭖﮔﺍﻠﺅﺙﻠﭨﻟ؟?0ﺅﺙ?

**ﮒﮒﭦﻝﭨﮔ**:
```json
{
  "code": 200,
  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",
  "data": {
    "total": 10,
    "page": 1,
    "page_size": 20,
    "accounts": [
      {
        "id": 1,
        "account_code": "ACC_20260402_001",
        "account_name": "ﻠﭨﻟ؟۳ﮔ۷۰ﮔﻟﺑ۵ﮔﺓ",
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

#### 1.2.4 ﮔﺑﮔﺍﻟﺑ۵ﮔﺓﻝﭘﮔ?

**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `PUT /api/v1/accounts/{account_id}/status`

**ﻟﺁﺓﮔﺎﮒﮔﺍ**:
```json
{
  "status": "frozen",
  "reason": "ﻠ۲ﮔ۶ﻟ۶۵ﮒ"
}
```

**ﮒﮒﭦﻝﭨﮔ**:
```json
{
  "code": 200,
  "message": "ﻝﭘﮔﮔﺑﮔﺍﮔﮒ?,
  "data": {
    "id": 1,
    "status": "frozen",
    "updated_at": "2026-04-02T16:00:00Z"
  }
}
```

**ﻛﺕﮒ۰ﻟ۶ﮒ**:
1. ﻝﭘﮔﻟﺛ؛ﮔ۱ﺅﺙactive ﻗ?frozen ﻗ?closed
2. closedﻝﭘﮔﻛﺕﮒﺁﻠ?
3. ﮒﭨﻝﭨﻟﺑ۵ﮔﺓﮔﭘﻠﻟ۵ﻟ؟ﺍﮒﺛﮒﮒ?

---

#### 1.2.5 ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶

**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/accounts/{account_id}/snapshots`

**ﻟﺁﺓﮔﺎﮒﮔﺍ**:
- `account_id`: ﻟﺑ۵ﮔﺓIDﺅﺙﻟﺓﺁﮒﺝﮒﮔﺍﺅﺙ
- `start_date`: ﮒﺙﮒ۶ﮔ۴ﮔﺅﺙﮒﺁﻠﺅﺙ
- `end_date`: ﻝﭨﮔﮔ۴ﮔﺅﺙﮒﺁﻠﺅﺙ
- `page`: ﻠ۰ﭖﻝ ﺅﺙﻠﭨﻟ؟?ﺅﺙ?
- `page_size`: ﮔﺁﻠ۰ﭖﮔﺍﻠﺅﺙﻠﭨﻟ؟?0ﺅﺙ?

**ﮒﮒﭦﻝﭨﮔ**:
```json
{
  "code": 200,
  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",
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

### 1.3 Repositoryﮔ۴ﮒ۲

#### 1.3.1 AccountRepository

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from decimal import Decimal

class AccountRepository(ABC):
    """ﻟﺑ۵ﮔﺓﻛﭨﮒ۷ﮔ۴ﮒ۲"""
    
    @abstractmethod
    async def create(self, account: Account) -> Account:
        """ﮒﮒﭨﭦﻟﺑ۵ﮔﺓ"""
        pass
    
    @abstractmethod
    async def find_by_id(self, account_id: int) -> Optional[Account]:
        """ﮔ ﺗﮔ؟IDﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ"""
        pass
    
    @abstractmethod
    async def find_by_code(self, account_code: str) -> Optional[Account]:
        """ﮔ ﺗﮔ؟ﻝﺙﻝ ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ"""
        pass
    
    @abstractmethod
    async def find_all(
        self,
        account_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[Account]:
        """ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮒﻟ۰۷"""
        pass
    
    @abstractmethod
    async def update(self, account: Account) -> Account:
        """ﮔﺑﮔﺍﻟﺑ۵ﮔﺓ"""
        pass
    
    @abstractmethod
    async def update_status(
        self,
        account_id: int,
        status: str,
        reason: Optional[str] = None
    ) -> bool:
        """ﮔﺑﮔﺍﻟﺑ۵ﮔﺓﻝﭘﮔ?""
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
        """ﮔﺑﮔﺍﻟﺑ۵ﮔﺓﻟﭖﻠ"""
        pass
    
    @abstractmethod
    async def create_snapshot(self, snapshot: AccountSnapshot) -> AccountSnapshot:
        """ﮒﮒﭨﭦﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶"""
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
        """ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶"""
        pass
```

---

## 2. ﮔﻛﭨﮔﮒ۰ﮔ۴ﮒ۲ (PositionService)

### 2.1 ﮔﮒ۰ﮔ۵ﻟﺟﺍ

**ﮔﮒ۰ﮒﻝ۶ﺍ**: PositionService  
**ﮔﮒ۰ﻟﻟﺑ۲**: ﮔﻛﭨﻝ؟۰ﻝﻙﮔﻛﭨﮔ۴ﻟﺁ۱ﻙﮔﻛﭨﮒﮒ? 
**ﻛﺝﻟﭖﮔﮒ۰**: AccountService, TradeService  
**ﮔﺍﮔ؟ﻟ؟ﺟﻠ؟**: PositionRepository

### 2.2 ﮔ۴ﮒ۲ﮒ؟ﻛﺗ

#### 2.2.1 ﮔ۴ﻟﺁ۱ﮔﻛﭨ

**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/accounts/{account_id}/positions`

**ﻟﺁﺓﮔﺎﮒﮔﺍ**:
- `account_id`: ﻟﺑ۵ﮔﺓIDﺅﺙﻟﺓﺁﮒﺝﮒﮔﺍﺅﺙ
- `stock_code`: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ ﺅﺙﮒﺁﻠﺅﺙ

**ﮒﮒﭦﻝﭨﮔ**:
```json
{
  "code": 200,
  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",
  "data": {
    "total_market_value": 450000.0000,
    "positions": [
      {
        "id": 1,
        "stock_code": "600000.SH",
        "stock_name": "ﮔﭖ۵ﮒﻠﭘﻟ۰",
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

#### 2.2.2 ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒﮒﺎ

**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/positions/{position_id}/history`

**ﻟﺁﺓﮔﺎﮒﮔﺍ**:
- `position_id`: ﮔﻛﭨIDﺅﺙﻟﺓﺁﮒﺝﮒﮔﺍﺅﺙ
- `start_date`: ﮒﺙﮒ۶ﮔ۴ﮔﺅﺙﮒﺁﻠﺅﺙ
- `end_date`: ﻝﭨﮔﮔ۴ﮔﺅﺙﮒﺁﻠﺅﺙ
- `change_type`: ﮒﮔﺑﻝﺎﭨﮒﺅﺙﮒﺁﻠﺅﺙ
- `page`: ﻠ۰ﭖﻝ ﺅﺙﻠﭨﻟ؟?ﺅﺙ?
- `page_size`: ﮔﺁﻠ۰ﭖﮔﺍﻠﺅﺙﻠﭨﻟ؟?0ﺅﺙ?

**ﮒﮒﭦﻝﭨﮔ**:
```json
{
  "code": 200,
  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",
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

### 2.3 Repositoryﮔ۴ﮒ۲

#### 2.3.1 PositionRepository

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from decimal import Decimal

class PositionRepository(ABC):
    """ﮔﻛﭨﻛﭨﮒ۷ﮔ۴ﮒ۲"""
    
    @abstractmethod
    async def create(self, position: Position) -> Position:
        """ﮒﮒﭨﭦﮔﻛﭨ"""
        pass
    
    @abstractmethod
    async def find_by_id(self, position_id: int) -> Optional[Position]:
        """ﮔ ﺗﮔ؟IDﮔ۴ﻟﺁ۱ﮔﻛﭨ"""
        pass
    
    @abstractmethod
    async def find_by_account_and_stock(
        self,
        account_id: int,
        stock_code: str
    ) -> Optional[Position]:
        """ﮔ ﺗﮔ؟ﻟﺑ۵ﮔﺓﮒﻟ۰ﻝ۴۷ﮔ۴ﻟﺁ۱ﮔﻛﭨ?""
        pass
    
    @abstractmethod
    async def find_by_account(
        self,
        account_id: int,
        stock_code: Optional[str] = None
    ) -> List[Position]:
        """ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮔﻛﭨ"""
        pass
    
    @abstractmethod
    async def update(self, position: Position) -> Position:
        """ﮔﺑﮔﺍﮔﻛﭨ"""
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
        """ﮔﺑﮔﺍﮔﻛﭨﮔﺍﻠ"""
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
        """ﮔﺑﮔﺍﮔﻛﭨﻛﭨﺓﮔ ﺙ"""
        pass
    
    @abstractmethod
    async def create_history(self, history: PositionHistory) -> PositionHistory:
        """ﮒﮒﭨﭦﮔﻛﭨﮒﮒﺎ"""
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
        """ﮔ۴ﻟﺁ۱ﮔﻛﭨﮒﮒﺎ"""
        pass
```

---

## 3. ﻟ؟۱ﮒﮔﮒ۰ﮔ۴ﮒ۲ (OrderService)

### 3.1 ﮔﮒ۰ﮔ۵ﻟﺟﺍ

**ﮔﮒ۰ﮒﻝ۶ﺍ**: OrderService  
**ﮔﮒ۰ﻟﻟﺑ۲**: ﻟ؟۱ﮒﻝ؟۰ﻝﻙﻟ؟۱ﮒﮔ۶ﻟ۰ﻙﻟ؟۱ﮒﮔ۴ﻟﺁ? 
**ﻛﺝﻟﭖﮔﮒ۰**: AccountService, PositionService, EngineService  
**ﮔﺍﮔ؟ﻟ؟ﺟﻠ؟**: OrderRepository

### 3.2 ﮔ۴ﮒ۲ﮒ؟ﻛﺗ

#### 3.2.1 ﮒﮒﭨﭦﻟ؟۱ﮒ

**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `POST /api/v1/orders`

**ﻟﺁﺓﮔﺎﮒﮔﺍ**:
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

**ﮒﮒﭦﻝﭨﮔ**:
```json
{
  "code": 200,
  "message": "ﻟ؟۱ﮒﮒﮒﭨﭦﮔﮒ",
  "data": {
    "id": 1,
    "order_code": "ORD_20260402_001",
    "account_id": 1,
    "signal_id": 100,
    "strategy_id": "STRAT_001",
    "stock_code": "600000.SH",
    "stock_name": "ﮔﭖ۵ﮒﻠﭘﻟ۰",
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

**ﻛﺕﮒ۰ﻟ۶ﮒ**:
1. ﻟ؟۱ﮒﻝﺙﻝ ﻟ۹ﮒ۷ﻝﮔﺅﺙORD_YYYYMMDD_XXX
2. ﻛﺗﺍﮒ۴ﻟ؟۱ﮒﺅﺙﮔ۲ﮔ۴ﮒﺁﻝ۷ﻟﭖﻠﮔﺁﮒ۵ﮒﻟﭘ?
3. ﮒﮒﭦﻟ؟۱ﮒﺅﺙﮔ۲ﮔ۴ﮒﺁﻝ۷ﮔﻛﭨﮔﺁﮒ۵ﮒﻟﭘ?
4. ﻠ۲ﮔ۶ﮔ۲ﮔ۴ﺅﺙﻟﺍﻝ۷RiskServiceﻟﺟﻟ۰ﻠ۲ﮔ۶ﮔ۲ﮔ?

---

#### 3.2.2 ﮔﻛﭦ۳ﻟ؟۱ﮒ

**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `POST /api/v1/orders/{order_id}/submit`

**ﻟﺁﺓﮔﺎﮒﮔﺍ**:
- `order_id`: ﻟ؟۱ﮒIDﺅﺙﻟﺓﺁﮒﺝﮒﮔﺍﺅﺙ

**ﮒﮒﭦﻝﭨﮔ**:
```json
{
  "code": 200,
  "message": "ﻟ؟۱ﮒﮔﻛﭦ۳ﮔﮒ",
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

**ﻛﺕﮒ۰ﻟ۶ﮒ**:
1. ﮒ۹ﮔpendingﻝﭘﮔﻝﻟ؟۱ﮒﮒﺁﻛﭨ۴ﮔﻛﭦ۳
2. ﮔﻛﭦ۳ﮒﻟﺟﻟ۰ﻠ۲ﮔ۶ﮔ۲ﮔ?
3. ﮔﻛﭦ۳ﮒﮒﭨﻝﭨﻟﭖﻠﮔﮔﻛﭨ
4. ﻟﺍﻝ۷EngineServiceﮔ۶ﻟ۰ﻟ؟۱ﮒ

---

#### 3.2.3 ﮒﮔﭘﻟ؟۱ﮒ

**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `POST /api/v1/orders/{order_id}/cancel`

**ﻟﺁﺓﮔﺎﮒﮔﺍ**:
- `order_id`: ﻟ؟۱ﮒIDﺅﺙﻟﺓﺁﮒﺝﮒﮔﺍﺅﺙ

**ﮒﮒﭦﻝﭨﮔ**:
```json
{
  "code": 200,
  "message": "ﻟ؟۱ﮒﮒﮔﭘﮔﮒ",
  "data": {
    "id": 1,
    "order_code": "ORD_20260402_001",
    "status": "cancelled",
    "cancelled_at": "2026-04-02T10:05:00Z"
  }
}
```

**ﻛﺕﮒ۰ﻟ۶ﮒ**:
1. ﮒ۹ﮔpendingﮔsubmittedﻝﭘﮔﻝﻟ؟۱ﮒﮒﺁﻛﭨ۴ﮒﮔﭘ
2. ﮒﮔﭘﮒﻠﮔﺝﮒﭨﻝﭨﻝﻟﭖﻠﮔﮔﻛﭨ?
3. ﻟﺍﻝ۷EngineServiceﮒﮔﭘﻟ؟۱ﮒ

---

#### 3.2.4 ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ

**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/orders/{order_id}`

**ﻟﺁﺓﮔﺎﮒﮔﺍ**:
- `order_id`: ﻟ؟۱ﮒIDﺅﺙﻟﺓﺁﮒﺝﮒﮔﺍﺅﺙ

**ﮒﮒﭦﻝﭨﮔ**:
```json
{
  "code": 200,
  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",
  "data": {
    "id": 1,
    "order_code": "ORD_20260402_001",
    "account_id": 1,
    "signal_id": 100,
    "strategy_id": "STRAT_001",
    "stock_code": "600000.SH",
    "stock_name": "ﮔﭖ۵ﮒﻠﭘﻟ۰",
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

#### 3.2.5 ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮒﻟ۰۷

**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/orders`

**ﻟﺁﺓﮔﺎﮒﮔﺍ**:
- `account_id`: ﻟﺑ۵ﮔﺓIDﺅﺙﮒﺁﻠﺅﺙ
- `stock_code`: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ ﺅﺙﮒﺁﻠﺅﺙ
- `status`: ﻟ؟۱ﮒﻝﭘﮔﺅﺙﮒﺁﻠﺅﺙ
- `direction`: ﻛﭦ۳ﮔﮔﺗﮒﺅﺙﮒﺁﻠﺅﺙ
- `start_date`: ﮒﺙﮒ۶ﮔ۴ﮔﺅﺙﮒﺁﻠﺅﺙ
- `end_date`: ﻝﭨﮔﮔ۴ﮔﺅﺙﮒﺁﻠﺅﺙ
- `page`: ﻠ۰ﭖﻝ ﺅﺙﻠﭨﻟ؟?ﺅﺙ?
- `page_size`: ﮔﺁﻠ۰ﭖﮔﺍﻠﺅﺙﻠﭨﻟ؟?0ﺅﺙ?

**ﮒﮒﭦﻝﭨﮔ**:
```json
{
  "code": 200,
  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",
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
        "stock_name": "ﮔﭖ۵ﮒﻠﭘﻟ۰",
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

### 3.3 Repositoryﮔ۴ﮒ۲

#### 3.3.1 OrderRepository

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

class OrderRepository(ABC):
    """ﻟ؟۱ﮒﻛﭨﮒ۷ﮔ۴ﮒ۲"""
    
    @abstractmethod
    async def create(self, order: Order) -> Order:
        """ﮒﮒﭨﭦﻟ؟۱ﮒ"""
        pass
    
    @abstractmethod
    async def find_by_id(self, order_id: int) -> Optional[Order]:
        """ﮔ ﺗﮔ؟IDﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ"""
        pass
    
    @abstractmethod
    async def find_by_code(self, order_code: str) -> Optional[Order]:
        """ﮔ ﺗﮔ؟ﻝﺙﻝ ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒ"""
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
        """ﮔ۴ﻟﺁ۱ﻟ؟۱ﮒﮒﻟ۰۷"""
        pass
    
    @abstractmethod
    async def update(self, order: Order) -> Order:
        """ﮔﺑﮔﺍﻟ؟۱ﮒ"""
        pass
    
    @abstractmethod
    async def update_status(
        self,
        order_id: int,
        status: str,
        reject_reason: Optional[str] = None
    ) -> bool:
        """ﮔﺑﮔﺍﻟ؟۱ﮒﻝﭘﮔ?""
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
        """ﮔﺑﮔﺍﻟ؟۱ﮒﮔﻛﭦ۳ﻛﺟ۰ﮔﺁ"""
        pass
    
    @abstractmethod
    async def find_active_orders(
        self,
        account_id: int,
        stock_code: Optional[str] = None
    ) -> List[Order]:
        """ﮔ۴ﻟﺁ۱ﮔﺑﭨﻟﺓﻟ؟۱ﮒ"""
        pass
```

---

## 4. ﻛﭦ۳ﮔﮔﮒ۰ﮔ۴ﮒ۲ (TradeService)

### 4.1 ﮔﮒ۰ﮔ۵ﻟﺟﺍ

**ﮔﮒ۰ﮒﻝ۶ﺍ**: TradeService  
**ﮔﮒ۰ﻟﻟﺑ۲**: ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﻝ؟۰ﻝﻙﻛﭦ۳ﮔﮔ۴ﻟﺁ۱ﻙﻛﭦ۳ﮔﻝﭨﻟ؟? 
**ﻛﺝﻟﭖﮔﮒ۰**: OrderService, PositionService  
**ﮔﺍﮔ؟ﻟ؟ﺟﻠ؟**: TradeRepository

### 4.2 ﮔ۴ﮒ۲ﮒ؟ﻛﺗ

#### 4.2.1 ﮒﮒﭨﭦﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ

**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `POST /api/v1/trades`

**ﻟﺁﺓﮔﺎﮒﮔﺍ**:
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

**ﮒﮒﭦﻝﭨﮔ**:
```json
{
  "code": 200,
  "message": "ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﮒﮒﭨﭦﮔﮒ",
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

#### 4.2.2 ﮔ۴ﻟﺁ۱ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ

**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/trades/{trade_id}`

**ﻟﺁﺓﮔﺎﮒﮔﺍ**:
- `trade_id`: ﻛﭦ۳ﮔIDﺅﺙﻟﺓﺁﮒﺝﮒﮔﺍﺅﺙ

**ﮒﮒﭦﻝﭨﮔ**:
```json
{
  "code": 200,
  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",
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

#### 4.2.3 ﮔ۴ﻟﺁ۱ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﮒﻟ۰۷

**ﮔ۴ﮒ۲ﻟﺓﺁﮒﺝ**: `GET /api/v1/trades`

**ﻟﺁﺓﮔﺎﮒﮔﺍ**:
- `account_id`: ﻟﺑ۵ﮔﺓIDﺅﺙﮒﺁﻠﺅﺙ
- `stock_code`: ﻟ۰ﻝ۴۷ﻛﭨ۲ﻝ ﺅﺙﮒﺁﻠﺅﺙ
- `direction`: ﻛﭦ۳ﮔﮔﺗﮒﺅﺙﮒﺁﻠﺅﺙ
- `start_date`: ﮒﺙﮒ۶ﮔ۴ﮔﺅﺙﮒﺁﻠﺅﺙ
- `end_date`: ﻝﭨﮔﮔ۴ﮔﺅﺙﮒﺁﻠﺅﺙ
- `page`: ﻠ۰ﭖﻝ ﺅﺙﻠﭨﻟ؟?ﺅﺙ?
- `page_size`: ﮔﺁﻠ۰ﭖﮔﺍﻠﺅﺙﻠﭨﻟ؟?0ﺅﺙ?

**ﮒﮒﭦﻝﭨﮔ**:
```json
{
  "code": 200,
  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",
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

### 4.3 Repositoryﮔ۴ﮒ۲

#### 4.3.1 TradeRepository

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

class TradeRepository(ABC):
    """ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﻛﭨﮒ۷ﮔ۴ﮒ۲"""
    
    @abstractmethod
    async def create(self, trade: Trade) -> Trade:
        """ﮒﮒﭨﭦﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ"""
        pass
    
    @abstractmethod
    async def find_by_id(self, trade_id: int) -> Optional[Trade]:
        """ﮔ ﺗﮔ؟IDﮔ۴ﻟﺁ۱ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ"""
        pass
    
    @abstractmethod
    async def find_by_code(self, trade_code: str) -> Optional[Trade]:
        """ﮔ ﺗﮔ؟ﻝﺙﻝ ﮔ۴ﻟﺁ۱ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ"""
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
        """ﮔ۴ﻟﺁ۱ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﮒﻟ۰۷"""
        pass
    
    @abstractmethod
    async def find_by_order(self, order_id: int) -> List[Trade]:
        """ﮔ ﺗﮔ؟ﻟ؟۱ﮒﮔ۴ﻟﺁ۱ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ"""
        pass
    
    @abstractmethod
    async def calculate_statistics(
        self,
        account_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """ﻟ؟۰ﻝ؟ﻛﭦ۳ﮔﻝﭨﻟ؟۰"""
        pass
```

---

## 5. ﮔ۴ﮒ۲ﻠﻝ۷ﻟ۶ﻟ

### 5.1 ﮒﮒﭦﮔ ﺙﮒﺙ

**ﮔﮒﮒﮒﭦ**:
```json
{
  "code": 200,
  "message": "ﮔﻛﺛﮔﮒ",
  "data": {
    // ﻛﺕﮒ۰ﮔﺍﮔ؟
  }
}
```

**ﻠﻟﺁﺁﮒﮒﭦ**:
```json
{
  "code": 400,
  "message": "ﮒﮔﺍﻠﻟﺁﺁ",
  "error": {
    "field": "account_id",
    "reason": "ﻟﺑ۵ﮔﺓIDﻛﺕﮒ­ﮒ?
  }
}
```

### 5.2 ﻠﻟﺁﺁﻝ ﮒ؟ﻛﺗ?

| ﻠﻟﺁﺁﻝ ?| ﻟﺁﺑﮔ | ﻝ۳ﭦﻛﺝ |
|--------|------|------|
| **200** | ﮔﮒ | ﮔﻛﺛﮔﮒ |
| **400** | ﮒﮔﺍﻠﻟﺁﺁ | ﮒﮔﺍﻝﺙﭦﮒ۳ﺎﮔﮔ ﺙﮒﺙﻠﻟﺁ?|
| **401** | ﮔ۹ﮔﮔ?| ﮔ۹ﻝﭨﮒﺛﮔtokenﻟﺟﮔ |
| **403** | ﮔ ﮔﻠ?| ﮔ ﮔﻛﺛﮔﻠ?|
| **404** | ﻟﭖﮔﭦﻛﺕﮒ­ﮒ?| ﻟﺑ۵ﮔﺓﻛﺕﮒ­ﮒ?|
| **409** | ﻛﺕﮒ۰ﮒﺎﻝ۹ | ﻟﺑ۵ﮔﺓﮒﺓﺎﮒ­ﮒ?|
| **500** | ﮔﮒ۰ﮒ۷ﻠﻟﺁ?| ﻝﺏﭨﻝﭨﮒﻠ۷ﻠﻟﺁﺁ |

### 5.3 ﮒﻠ۰ﭖﻟ۶ﻟ

**ﻟﺁﺓﮔﺎﮒﮔﺍ**:
- `page`: ﻠ۰ﭖﻝ ﺅﺙﻛﭨ1ﮒﺙﮒ۶ﺅﺙ
- `page_size`: ﮔﺁﻠ۰ﭖﮔﺍﻠﺅﺙﻠﭨﻟ؟?0ﺅﺙﮔﮒ۳?00ﺅﺙ?

**ﮒﮒﭦﮔ ﺙﮒﺙ**:
```json
{
  "code": 200,
  "message": "ﮔ۴ﻟﺁ۱ﮔﮒ",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": []
  }
}
```

### 5.4 ﮔﭘﻠﺑﮔ ﺙﮒﺙ

- **ﮔ۴ﮔ**: `YYYY-MM-DD` (ﮒ۵? 2026-04-02)
- **ﮔﭘﻠﺑﮔ?*: `YYYY-MM-DDTHH:MM:SSZ` (ﮒ۵? 2026-04-02T10:00:00Z)
- **ﮔﭘﮒﭦ**: UTC

### 5.5 ﻠﻠ۱ﮔ ﺙﮒﺙ

- **ﻝﺎﺝﮒﭦ۵**: 4ﻛﺛﮒﺍﮔﺍﺅﺙDECIMAL(20,4)ﺅﺙ?
- **ﮒﻛﺛ**: ﮒﺅﺙﻛﭦﭦﮔﺍﮒﺕﺅﺙ
- **ﻝ۳ﭦﻛﺝ**: 1000000.0000

---

## 6. ﮔ۶ﻟﺛﻟ۵ﮔﺎ

### 6.1 ﮒﮒﭦﮔﭘﻠﺑ

| ﮔ۴ﮒ۲ﻝﺎﭨﮒ | ﮒﮒﭦﮔﭘﻠﺑﻟ۵ﮔﺎ | ﮒ۳ﮔﺏ۷ |
|----------|--------------|------|
| **ﮔ۴ﻟﺁ۱ﮔ۴ﮒ۲** | < 200ms | ﻝ؟ﮒﮔ۴ﻟﺁ?|
| **ﮒﻟ۰۷ﮔ۴ﮒ۲** | < 500ms | ﮒﻠ۰ﭖﮔ۴ﻟﺁ۱ |
| **ﮒﮒﭨﭦﮔ۴ﮒ۲** | < 300ms | ﮔﺍﮔ؟ﮒﮒ۴ |
| **ﮔﺑﮔﺍﮔ۴ﮒ۲** | < 300ms | ﮔﺍﮔ؟ﮔﺑﮔﺍ |
| **ﻝﭨﻟ؟۰ﮔ۴ﮒ۲** | < 1000ms | ﮒ۳ﮔﻟ؟۰ﻝ؟ |

### 6.2 ﮒﺗﭘﮒﻟ۵ﮔﺎ

- **ﮒﺗﭘﮒﻝ۷ﮔﺓﮔ?*: 100
- **QPS**: 1000
- **TPS**: 500

### 6.3 ﻝﺙﮒ­ﻝ­ﻝ۴

| ﮔﺍﮔ؟ﻝﺎﭨﮒ | ﻝﺙﮒ­ﮔﭘﻠﺑ | ﻝﺙﮒ­ﻝ­ﻝ۴ |
|----------|----------|----------|
| **ﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁ** | 5ﮒﻠ | Redisﻝﺙﮒ­ |
| **ﮔﻛﭨﻛﺟ۰ﮔﺁ** | 1ﮒﻠ | Redisﻝﺙﮒ­ |
| **ﻟ؟۱ﮒﻛﺟ۰ﮔﺁ** | ﻛﺕﻝﺙﮒ­?| ﮒ؟ﮔﭘﮔ۴ﻟﺁ۱ |
| **ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ** | ﻛﺕﻝﺙﮒ­?| ﮒ؟ﮔﭘﮔ۴ﻟﺁ۱ |

---

## 7. ﮒ؟ﮒ۷ﻟ۵ﮔﺎ

### 7.1 ﻟ؟۳ﻟﺁﮔﮔ

- **ﻟ؟۳ﻟﺁﮔﺗﮒﺙ**: JWT Token
- **Tokenﮔﮔﮔ?*: 2ﮒﺍﮔﭘ
- **ﮒﺓﮔﺍToken**: 7ﮒ۳?

### 7.2 ﮔﺍﮔ؟ﮒ ﮒﺁ

- **ﻛﺙ ﻟﺝﮒ ﮒﺁ**: HTTPS
- **ﮔﮔﮔﺍﮔ؟**: AESﮒ ﮒﺁﮒ­ﮒ۷
- **ﮒﺁﻝ **: BCryptﮒﮒﺕ

### 7.3 ﻟ؟ﺟﻠ؟ﮔ۶ﮒﭘ

- **RBAC**: ﮒﭦﻛﭦﻟ۶ﻟﺎﻝﻟ؟ﺟﻠ؟ﮔ۶ﮒ?
- **ﮔﻠﻝﺎﮒﭦ۵**: ﮔ۴ﮒ۲ﻝﭦ۶ﮒ،
- **ﮒ؟۰ﻟ؟۰ﮔ۴ﮒﺟ**: ﻟ؟ﺍﮒﺛﮔﮔﮔﻛﺛ?

---

**ﻝﮔ؛**: 1.0.0 | **ﮔﺑﮔﺍﮔ۴ﮔ**: 2026-04-02 | **ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ? 
**ﻛﺕﻛﺕﮔ­?*: P0-4 ﻝ؛؛ﻛﺕﮔﺗﮔ۴ﮒ۲ﻠﮔﻟ؟ﺝﻟ؟