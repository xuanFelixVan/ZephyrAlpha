﻿---
module_id: DB_REVIEW_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﻟﮒﺝﮔﭘﮔ?
responsibility:
  - 实施指南、部署文档
  - 交易执行
  - 数据源
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﻟﺁ?
applicable_scope: ﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﻟﺁﮒ؟۰ﻛﺕﻛﺙﮒ
compliance_level: ﻛﺕﻛﺕﮔﭦﮔﮔ ﮒ
parent_document: ../INDEX.md
implementation_status: ﻟﺟﻟ۰?---


# ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﻟﺁﮒ؟۰ﮔ۴?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.0 - ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﻟﺁ?
> **ﻟﺁﮒ؟۰ﮒﺁﺗﻟﺎ۰**: P0-01_Database_Design_Document.md
> **ﻟﺁﮒ؟۰ﮔ ﮒ**: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮔﺁﻟ۶ﮔ ﺙﮔ ﮒv5.3
> **ﻟﺁﮒ؟۰ﮔﺗﮔﺏ**: ﮒﺁﺗﮔﺁﮒﮔ + ﻟ۰ﻛﺕﮔﻛﺛﺏﮒ؟?+ ﻠ۲ﻠ۸ﻟﺁﻛﺙﺍ

## 1. ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﮔ ?

### 1.1 ﻟ۰ﻛﺕﮔ ﮒﮒﺁﺗﮔﺁ

| ﻟ؟ﺝﻟ؟۰ﻝﭨﺑﮒﭦ۵ | ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒ | ﮒﺛﮒﻟ؟ﺝﻟ؟۰ﮔﺗﮔ۰ | ﻝ؛۵ﮒ?| ﻟﺁﮒ؟۰ﻝﭨﻟ؟ﭦ |
|----------|------------------|--------------|--------|----------|
| **ﻟ۰۷ﻝﭨﮔﻟ؟ﺝ?* | ﮔ ﺕﮒﺟ?5-25ﻛﺕ۹ﮒ­?| 18-30ﻛﺕ۹ﮒ­?| 85% | ﻗ ﺅﺕ ﻠﻛﺙﮒ |
| **ﮔﺍﮔ؟ﻝﺎﭨﮒﻠﮔ۸** | ﻠﻠ۱DECIMAL(20,4) | DECIMAL(18,2) | 70% | ?ﻠﻟﺍﮔﺑ |
| **ﮒﮒﭦﻝ­ﻝ۴** | ﮔﮔﮒﮒﭦﺅﺙﻛﺟ??| ﮔﮒ­۲ﮒﭦ۵ﮒﮒﭦﺅﺙﻛﺟﻝ1-5?| 60% | ?ﻠﻟﺍﮔﺑ |
| **ﻝﺑ۱ﮒﺙﻝ­ﻝ۴** | ﮔ ﺕﮒﺟ?-10ﻛﺕ۹ﻝﺑ۱?| ﮒﺗﺏﮒ4ﻛﺕ۹ﻝﺑ۱?| 80% | ﻗ ﺅﺕ ﻠﻛﺙﮒ |
| **ﮔﺑﻛﺛﻝ؛۵ﮒ?* | ?0% | 75% | ?**ﻛﺕﻟﺝﺝ?* |

**ﻟﺁﮒ؟۰ﻝﭨﻟ؟ﭦ**: ﮒﺛﮒﻟ؟ﺝﻟ؟۰ﻝ؛۵ﮒ?5%ﺅﺙﻟﺓﻝ۵ﭨﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒﺅﺙ?0%ﺅﺙﻟﺟ?*15%ﻝﮒﺓ؟?*ﺅﺙﻠﻟ۵ﻟﺟﻟ۰ﻛﺙﮒﻟﺍﮔ?

---

## 2. ﻝ۰؟ﻟ؟۳?: ﻟ۰۷ﻝﭨﮔﻟ؟ﺝﻟ؟۰ﻟﺁ?

### 2.1 ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒ

**ﮔ ﺕﮒﺟﮒﮒ**: ﮒ­ﮔ؟ﭖﮔﺍﻠﻠﻛﺕ­ﺅﺙﻟﻟﺑ۲ﮒﻛﺕﺅﺙﻠﺟﮒﻟﺟﮒﭦ۵ﻟ؟ﺝ?

| ﻟ۰۷ﻝﺎﭨ?| ﻛﺕﻛﺕﮔ ﮒﮒ­ﮔ؟ﭖ?| ﻝﻝﺎ | ﻟ۰ﻛﺕﮔ۰ﻛﺝ |
|--------|----------------|------|----------|
| **ﻟﺑ۵ﮔﺓ?* | 15-20ﻛﺕ۹ﮒ­?| ﮔ ﺕﮒﺟﻛﺕﮒ۰ﮒ؟ﻛﺛﺅﺙﮒ­ﮔ؟ﭖﻠﻛﺕ­ | ﮒﺗﭨﮔﺗﻠﮒﻙﻛﺗﮒ۳ﮔ?|
| **ﮔﻛﭨ?* | 18-22ﻛﺕ۹ﮒ­?| ﻠﻟ۵ﻟﺁ۵ﻝﭨﻝﮔﻛﭨﻛﺟ۰ﮔﺁ | ﮔﮔﺎﺁﮔﻟﭖﻙﻟ۰ﮒ۳ﮔ?|
| **ﻟ؟۱ﮒ?* | 25-30ﻛﺕ۹ﮒ­?| ﻟ؟۱ﮒﻝﮒﺛﮒ۷ﮔﮒ۳ﮔﺅﺙﮒ­ﮔ؟ﭖﻟﺝ?| ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |
| **ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ?* | 15-18ﻛﺕ۹ﮒ­?| ﻛﭦ۳ﮔﮔﻝﭨﺅﺙﮒ­ﮔ؟ﭖﻝﺎﺝﻝ؟ | ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |

### 2.2 ﮒﺛﮒﻟ؟ﺝﻟ؟۰ﻟﺁﮒ؟۰

| ﻟ۰۷ﮒ | ﮒﺛﮒﮒ­ﮔ؟ﭖ?| ﻛﺕﻛﺕﮔ ﮒ | ﻟﺁﮒ؟۰ﻝﭨﮔ | ﻛﺙﮒﮒﭨﭦﻟ؟؟ |
|------|------------|----------|----------|----------|
| **accounts** | 21?| 15-20?| ﻗ ﺅﺕ ﻝ۴ﮒ۳ | ﮒﮒﺍ1-2ﻛﺕ۹ﻠﮔ ﺕﮒﺟﮒ­ﮔ؟ﭖ |
| **positions** | 20?| 18-22?| ?ﮒﮔ ﺙ | ﮔ ﻠﻟﺍﮔﺑ |
| **orders** | 30?| 25-30?| ?ﮒﮔ ﺙ | ﮔ ﻠﻟﺍﮔﺑ |
| **trades** | 18?| 15-18?| ?ﮒﮔ ﺙ | ﮔ ﻠﻟﺍﮔﺑ |

### 2.3 ﻛﺕﻛﺕﻛﺙﮒﮒﭨﭦﻟ؟؟

#### accountsﻟ۰۷ﻛﺙﮒﺅﺙﮒﮒﺍ?9ﻛﺕ۹ﮒ­ﮔ؟ﭖﺅﺙ

**ﮒﭨﭦﻟ؟؟ﮒ ﻠ۳ﻝﮒ­?*:
```sql
-- ﮒ ﻠ۳ﻛﭨ۴ﻛﺕ2ﻛﺕ۹ﮒ­ﮔ؟ﭖﺅﺙﮒﺁﻠﻟﺟﻟ؟۰ﻝ؟ﮒﺝﮒﭦ?
-- 1. total_market_valueﺅﺙﮔﭨﮒﺕﮒﺙﺅﺙ - ﮒﺁﻠﻟﺟpositionsﻟ۰۷ﻟﮒﻟ؟۰?
-- 2. daily_pnlﺅﺙﮒﺛﮔ۴ﻝﻛﭦﺅﺙ - ﮒﺁﻠﻟﺟaccount_snapshotsﻟ۰۷ﮔ۴?

-- ﻛﺙﮒﮒﻝaccountsﻟ۰۷ﺅﺙ19ﻛﺕ۹ﮒ­ﮔ؟ﭖﺅﺙ
accounts (
    id, account_code, account_name, account_type, broker,
    initial_capital, current_capital, available_cash, frozen_cash,
    total_assets, total_pnl, max_drawdown, status,
    created_at, updated_at, metadata  -- 16ﻛﺕ۹ﮒﭦﻝ۰ﮒ­ﮔ؟ﭖ
    -- ﮒ ﻠ۳: total_market_value, daily_pnl
)
```

**ﻝﻝﺎ**:
1. **ﻠﺟﮒﮔﺍﮔ؟ﮒﻛﺛ**: `total_market_value`ﮒﺁﻠﻟﺟﮔﻛﭨﻟ۰۷ﮒ؟ﮔﭘﻟ؟۰?
2. **ﮔﺍﮔ؟ﻛﺕﻟ?*: `daily_pnl`ﮒ۷account_snapshotsﻟ۰۷ﻛﺕ­ﮒﺓﺎﮔﻟ؟ﺍﮒﺛ
3. **ﻛﺕﻛﺕﮒ؟ﻟﺓﭖ**: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﻠﮒﺕﺕﮒﺍﻟ؟۰ﻝ؟ﮒ­ﮔ؟ﭖﻛﺕﮒﭦﻝ۰ﮒ­ﮔ؟ﭖﮒﻝ۵ﭨ

---

## 3. ﻝ۰؟ﻟ؟۳?: ﮔﺍﮔ؟ﻝﺎﭨﮒﻠﮔ۸ﻟﺁﮒ؟۰

### 3.1 ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒ

**ﮔ ﺕﮒﺟﮒﮒ**: ﻝﺎﺝﮒﭦ۵ﻛﺙﮒﺅﺙﮒ؟ﮒﺁﻟﺟﮒﭦ۵ﻝﺎﺝﻝ۰؟ﺅﺙﻛﺕﮒﺁﻝﺎﺝﮒﭦ۵ﻛﺕﻟﭘﺏ

| ﮒ­ﮔ؟ﭖﻝﺎﭨﮒ | ﻛﺕﻛﺕﮔ ﮒ | ﻝﻝﺎ | ﻟ۰ﻛﺕﮔ۰ﻛﺝ |
|----------|----------|------|----------|
| **ﻠﻠ۱ﮒ­ﮔ؟ﭖ** | DECIMAL(20,4) | 1. ﮔﺁﮔﻛﺕﻛﭦﺟﻝﭦ۶ﻟﭖ?br>2. ﻝﺎﺝﮒﭦ۵4ﻛﺛﮒﺍﮔﺍﺅﺙ0.0001?br>3. ﻠﺟﮒﻝﺎﺝﮒﭦ۵ﮔﮒ۳ﺎ | ﮒﺗﭨﮔﺗﻠﮒﺅﺙﻝ؟۰ﻝﻟ۶?00??|
| **ﻝﺝﮒﮔﺁﮒ­?* | DECIMAL(12,6) | 1. ﻝﺎﺝﮒﭦ۵6ﻛﺛﮒﺍﮔﺍﺅﺙ0.000001?br>2. ﮔﺁﮔﻝﺎﺝﻝ۰؟ﻟ؟۰ﻝ؟<br>3. ﻠﺟﮒﻝﺑﺁﻟ؟۰ﻟﺁﺁﮒﺓ؟ | ﻛﺗﮒ۳ﮔﻟﭖﺅﺙﻠ،ﻠ۱ﻛﭦ۳ﮔﺅﺙ |
| **ﻛﭨﺓﮔ ﺙﮒ­ﮔ؟ﭖ** | DECIMAL(12,4) | 1. ﻝﺎﺝﮒﭦ۵4ﻛﺛﮒﺍﮔﺍﺅﺙ0.0001?br>2. ﮔﺁﮔﻝﺎﺝﻝ۰؟ﻛﭨﺓﮔ ﺙ<br>3. ﮒﺙﮒ؟ﺗAﻟ۰ﮔﮒﺍﮒﮒ۷ﮒ?| ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |
| **ﮔﺍﻠﮒ­ﮔ؟ﭖ** | BIGINT | 1. ﮔﺁﮔﮒ۳۶ﮔﺍﻠﻝﭦ۶<br>2. ﻠﺟﮒﮔﭦ۱ﮒﭦ<br>3. ﮒﺙﮒ؟ﺗﮔﻛﭦ۳?| ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |

### 3.2 ﮒﺛﮒﻟ؟ﺝﻟ؟۰ﻟﺁﮒ؟۰

| ﮒ­ﮔ؟ﭖﻝﺎﭨﮒ | ﮒﺛﮒﻟ؟ﺝﻟ؟۰ | ﻛﺕﻛﺕﮔ ﮒ | ﮒﺓ؟ﻟﺓ | ﻠ۲ﻠ۸ﻝ­ﻝﭦ۶ |
|----------|----------|----------|------|----------|
| **ﻠﻠ۱ﮒ­ﮔ؟ﭖ** | DECIMAL(18,2) | DECIMAL(20,4) | ﻝﺎﺝﮒﭦ۵ﻛﺕﻟﭘﺏ | ﻭﺑ ﻠ،ﻠ۲?|
| **ﻝﺝﮒﮔﺁﮒ­?* | DECIMAL(10,4) | DECIMAL(12,6) | ﻝﺎﺝﮒﭦ۵ﻛﺕﻟﭘﺏ | ﻭ۰ ﻛﺕ­ﻠ۲?|
| **ﻛﭨﺓﮔ ﺙﮒ­ﮔ؟ﭖ** | DECIMAL(10,4) | DECIMAL(12,4) | ﻟﮒﺑﻛﺕﻟﭘﺏ | ﻭ۰ ﻛﺕ­ﻠ۲?|
| **ﮔﺍﻠﮒ­ﮔ؟ﭖ** | INTEGER | BIGINT | ﻟﮒﺑﻛﺕﻟﭘﺏ | ﻭ۰ ﻛﺕ­ﻠ۲?|

### 3.3 ﻛﺕﻛﺕﻛﺙﮒﮔﺗﮔ۰

#### ﮔﺗﮔ۰A: ﮒ۷ﻠ۱ﮔﮒﻝﺎﺝﮒﭦ۵ﺅﺙﮔ۷ﻟﺅﺙ

```sql
-- ﻠﻠ۱ﮒ­ﮔ؟ﭖﻛﺙﮒ
ALTER TABLE accounts 
    ALTER COLUMN initial_capital TYPE DECIMAL(20,4),
    ALTER COLUMN current_capital TYPE DECIMAL(20,4),
    ALTER COLUMN available_cash TYPE DECIMAL(20,4),
    ALTER COLUMN frozen_cash TYPE DECIMAL(20,4),
    ALTER COLUMN total_assets TYPE DECIMAL(20,4);

-- ﻝﺝﮒﮔﺁﮒ­ﮔ؟ﭖﻛﺙ?
ALTER TABLE accounts
    ALTER COLUMN max_drawdown TYPE DECIMAL(12,6);

ALTER TABLE positions
    ALTER COLUMN unrealized_pnl_pct TYPE DECIMAL(12,6);

-- ﻛﭨﺓﮔ ﺙﮒ­ﮔ؟ﭖﻛﺙﮒ
ALTER TABLE orders
    ALTER COLUMN order_price TYPE DECIMAL(12,4),
    ALTER COLUMN filled_price TYPE DECIMAL(12,4);

-- ﮔﺍﻠﮒ­ﮔ؟ﭖﻛﺙﮒ
ALTER TABLE positions
    ALTER COLUMN quantity TYPE BIGINT,
    ALTER COLUMN available_quantity TYPE BIGINT,
    ALTER COLUMN frozen_quantity TYPE BIGINT;

ALTER TABLE orders
    ALTER COLUMN order_quantity TYPE BIGINT,
    ALTER COLUMN filled_quantity TYPE BIGINT;
```

**ﻛﺙﮒﺟ**:
1. **ﻝﺎﺝﮒﭦ۵ﮒﻟﭘﺏ**: ﮔﺁﮔﻛﺕﻛﭦﺟﻝﭦ۶ﻟﭖﻠﻝ؟۰?
2. **ﻠﺟﮒﻟﺁﺁﮒﺓ؟**: 4ﻛﺛﮒﺍﮔﺍﻝﺎﺝﮒﭦ۵ﻠﺟﮒﻝﺑﺁﻟ؟۰ﻟﺁﺁ?
3. **ﮔ۸ﮒﺎﮔ۶ﮒﺙﭦ**: ﮔ۹ﮔ۴ﻟ۶ﮔ۷۰ﮔ۸ﮒ۳۶ﮔ ﻠﻛﺟ؟ﮔﺗ
4. **ﻛﺕﻛﺕﮔ ﮒ**: ﻝ؛۵ﮒﻠ۰ﭘﻝﭦ۶ﻠﮒﮔﭦﮔﮔ ﮒ

**ﮒ۲ﮒﺟ**:
1. **ﮒ­ﮒ۷ﮒ۱ﮒ **: ﮔﺁﻛﺕ۹ﮒ­ﮔ؟ﭖﮒ۱ﮒ 2-4ﮒ­ﻟ
2. **ﮔ۶ﻟﺛﮒﺛﺎﮒ**: ﻝﺎﺝﮒﭦ۵ﮔﮒﮒﺁﻟﺛﮒﺛﺎﮒﻟ؟۰ﻝ؟ﮔ۶ﻟﺛ?5%?

---

#### ﮔﺗﮔ۰B: ﮒﮒﺎﻝﺎﺝﮒﭦ۵ﻟ؟ﺝﻟ؟۰ﺅﺙﮔﻛﺕ­ﮔﺗﮔ۰ﺅﺙ

```sql
-- ﮔ ﺕﮒﺟﻠﻠ۱ﮒ­ﮔ؟ﭖﻛﺛﺟﻝ۷ﻠ،ﻝﺎﺝ?
accounts: initial_capital, current_capital, total_assets ?DECIMAL(20,4)

-- ﮔ؛۰ﻟ۵ﻠﻠ۱ﮒ­ﮔ؟ﭖﻛﺛﺟﻝ۷ﮔ ﮒﻝﺎﺝﮒﭦ۵
accounts: available_cash, frozen_cash ?DECIMAL(18,2)

-- ﻝﺝﮒﮔﺁﮒ­ﮔ؟ﭖﻛﺛﺟﻝ۷ﻠ،ﻝﺎﺝﮒﭦ۵
max_drawdown, pnl_pct ?DECIMAL(12,6)

-- ﻛﭨﺓﮔ ﺙﮒ­ﮔ؟ﭖﻛﺛﺟﻝ۷ﮔ ﮒﻝﺎﺝﮒﭦ۵
order_price, filled_price ?DECIMAL(10,4)
```

**ﻛﺙﮒﺟ**:
1. **ﮒﺗﺏﻟ۰۰ﮔ۶ﻟﺛ**: ﮔ ﺕﮒﺟﮒ­ﮔ؟ﭖﻠ،ﻝﺎﺝﮒﭦ۵ﺅﺙﮔ؛۰ﻟ۵ﮒ­ﮔ؟ﭖﮔ ﮒﻝﺎﺝﮒﭦ۵
2. **ﮒ­ﮒ۷ﻛﺙﮒ**: ﮒﮒﺍﮒ­ﮒ۷ﻝ۸ﭦﻠﺑﮒ ﻝ۷
3. **ﮔ۶ﻟﺛﻛﺙﮒ**: ﻠﻛﺛﻟ؟۰ﻝ؟ﮒﺙﻠ

**ﮒ۲ﮒﺟ**:
1. **ﮒ۳ﮔﮒﭦ۵ﮒ۱?*: ﻠﻟ۵ﻝﭨﺑﮔ۳ﻛﺕﮒﻝﺎﺝﮒﭦ۵ﮔ ?
2. **ﻛﺕﻟﺑﮔ۶ﻠ۲?*: ﻛﺕﮒﻝﺎﺝﮒﭦ۵ﮒﺁﻟﺛﮒﺁﺙﻟﺑﻟ؟۰ﻝ؟ﻟﺁﺁﮒﺓ؟

---

### 3.4 ﻛﺕﻛﺕﮒﭨﭦﻟ؟؟

**ﮔ۷ﻟﮔﺗﮔ۰**: **ﮔﺗﮔ۰A - ﮒ۷ﻠ۱ﮔﮒﻝﺎﺝﮒﭦ۵**

**ﻝﻝﺎ**:
1. **ﻛﺕﻛﺕﮔ ﮒ**: ﻝ؛۵ﮒﻠ۰ﭘﻝﭦ۶ﻠﮒﮔﭦﮔﮔ ﮒﺅﺙﮒﺗﭨﮔﺗﻙﻛﺗﮒ۳ﻙﮔﮔﺎﺁﺅﺙ
2. **ﻠﺟﮒﻟﺟﮒﺓ۴**: ﮔ۹ﮔ۴ﻟ۶ﮔ۷۰ﮔ۸ﮒ۳۶ﮔ ﻠﻛﺟ؟ﮔﺗﮔﺍﮔ؟?
3. **ﻝﺎﺝﮒﭦ۵ﻛﺙﮒ**: ﻠﮒﻛﭦ۳ﮔﮒﺁﺗﻝﺎﺝﮒﭦ۵ﻟ۵ﮔﺎﮔﻠ،ﺅﺙﮒ؟ﮒﺁﻟﺟﮒﭦ۵ﻝﺎﺝﻝ۰؟
4. **ﮔﮔ؛ﮒﺁﮔ۶**: ﮒ­ﮒ۷ﮒﮔ۶ﻟﺛﮔﮔ؛ﮒ۱ﮒ ﮒﺁﮔ۶?10%?

**ﮒ؟ﮔﺛﮒﭨﭦﻟ؟؟**:
1. ﻝ،ﮒﺏﻛﺟ؟ﮔﺗﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﮔ?
2. ﮔﺑﮔﺍﮔﮔﻟ۰۷ﻝﮒ­ﮔ؟ﭖﻝﺎﭨﮒﮒ؟?
3. ﻠﮔﺍﻝﮔDDLﻟﮔ؛
4. ﮔﺑﮔﺍﮔﺍﮔ؟ﮒ­ﮒﺕ

---

## 4. ﻝ۰؟ﻟ؟۳?: ﮒﮒﭦﻝ­ﻝ۴ﻟﺁﮒ؟۰

### 4.1 ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒ

**ﮔ ﺕﮒﺟﮒﮒ**: ﮒﮒﭦﻝﺎﮒﭦ۵ﻝﭨﻙﻛﺟﻝﮔﭘﻠﺑﻠﺟﻙﮔ۴ﻟﺁ۱ﮔ۶ﻟﺛ?

| ﮔﺍﮔ؟ﻝﺎﭨﮒ | ﻛﺕﻛﺕﮔ ﮒﮒﮒﭦﻝﺎﮒﭦ۵ | ﻛﺕﻛﺕﮔ ﮒﻛﺟﻝﮔﭘﻠﺑ | ﻝﻝﺎ | ﻟ۰ﻛﺕﮔ۰ﻛﺝ |
|----------|------------------|------------------|------|----------|
| **ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ** | ﮔﮔﮒﮒﭦ | 7-10?| 1. ﻝﻝ؟۰ﻟ۵ﮔﺎ<br>2. ﮒﮒﺎﮒﮔﭖ<br>3. ﮒ؟۰ﻟ؟۰ﻟﺟﺛﮔﭦﺁ | ﻟﺁﻝﻛﺙﻟ۵??|
| **ﮔﻛﭨﮒﮒﺎ** | ﮔﮔﮒﮒﭦ | 5-7?| 1. ﮔﻛﭨﮒﮔ<br>2. ﻠ۲ﻠ۸ﮒﮔﭦﺁ<br>3. ﻛﺕﻝﭨ۸ﮒﺛﮒ  | ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |
| **ﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶** | ﮔﮔﮒﮒﭦ | 5-7?| 1. ﻟﭖﻠﮔﺎﻝﭦﺟ<br>2. ﻠ۲ﻠ۸ﮒﮔ<br>3. ﻛﺕﻝﭨ۸ﻟﺁﻛﺙﺍ | ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |
| **ﻝﺏﭨﻝﭨﮔﮔ ** | ﮔﮒ۷ﮒﮒﭦ | 1-2?| 1. ﮔ۶ﻟﺛﻝﮔ۶<br>2. ﮒ؟ﺗﻠﻟ۶ﮒ<br>3. ﮒﺙﮒﺕﺕﮒﮔ | ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |

### 4.2 ﮒﺛﮒﻟ؟ﺝﻟ؟۰ﻟﺁﮒ؟۰

| ﻟ۰۷ﮒ | ﮒﺛﮒﮒﮒﭦﻝﺎﮒﭦ۵ | ﻛﺕﻛﺕﮔ ﮒ | ﮒﺛﮒﻛﺟﻝﮔﭘﻠﺑ | ﻛﺕﻛﺕﮔ ﮒ | ﻟﺁﮒ؟۰ﻝﭨﮔ |
|------|--------------|----------|--------------|----------|----------|
| **trades** | ﮔﮒ­۲?| ﮔﮔ | 5?| 7-10?| ?ﻛﺕﻟﺝﺝ?|
| **position_history** | ﮔﮒ­۲?| ﮔﮔ | 3?| 5-7?| ?ﻛﺕﻟﺝﺝ?|
| **account_snapshots** | ﮔﮒ­۲?| ﮔﮔ | 3?| 5-7?| ?ﻛﺕﻟﺝﺝ?|
| **system_metrics** | ﮔﮒ­۲?| ﮔﮒ۷ | 1?| 1-2?| ﻗ ﺅﺕ ﻠﻛﺙﮒ |

### 4.3 ﻛﺕﻛﺕﻛﺙﮒﮔﺗﮔ۰

#### ﻛﺙﮒﮔﺗﮔ۰ﺅﺙﮔﮔﮒ?+ ﮒﭨﭘﻠﺟﻛﺟﻝﮔﭘﻠﺑ

```sql
-- ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﻟ۰۷ﺅﺙﮔﮔﮒﮒﭦﺅﺙﻛﺟ?0?
CREATE TABLE trades (
    -- ﮒ­ﮔ؟ﭖﮒ؟ﻛﺗ
) PARTITION BY RANGE (traded_at);

-- ﮒﮒﭨﭦ2026?ﮔﻝﮒﮒﭦ
CREATE TABLE trades_202601 PARTITION OF trades
FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- ﮒﮒﭨﭦ2026?ﮔﻝﮒﮒﭦ
CREATE TABLE trades_202602 PARTITION OF trades
FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- ... ﻛﭨ۴ﮔ­۳ﻝﺎﭨﮔ۷ﺅﺙﮒ?20ﻛﺕ۹ﮔﮒﮒﭦ?0ﮒﺗﺑﺅﺙ

-- ﮔﻛﭨﮒﮒﺎﻟ۰۷ﺅﺙﮔﮔﮒﮒﭦﺅﺙﻛﺟ??
CREATE TABLE position_history (
    -- ﮒ­ﮔ؟ﭖﮒ؟ﻛﺗ
) PARTITION BY RANGE (created_at);

-- ﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶ﻟ۰۷ﺅﺙﮔﮔﮒﮒﭦﺅﺙﻛﺟ??
CREATE TABLE account_snapshots (
    -- ﮒ­ﮔ؟ﭖﮒ؟ﻛﺗ
) PARTITION BY RANGE (snapshot_date);

-- ﻝﺏﭨﻝﭨﮔﮔ ﻟ۰۷ﺅﺙﮔﮒ۷ﮒﮒﭦﺅﺙﻛﺟ??
CREATE TABLE system_metrics (
    -- ﮒ­ﮔ؟ﭖﮒ؟ﻛﺗ
) PARTITION BY RANGE (recorded_at);

-- ﮒﮒﭨﭦ2026ﮒﺗﺑﻝ؛؛1ﮒ۷ﻝﮒﮒﭦ
CREATE TABLE system_metrics_202601 PARTITION OF system_metrics
FOR VALUES FROM ('2026-01-01') TO ('2026-01-08');
```

#### ﮒﮒﭦﻝ؟۰ﻝﻟ۹ﮒ۷ﮒﻟ?

```python
# scripts/manage_partitions.py
import psycopg2
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def create_monthly_partition(table_name, start_date, end_date):
    """ﮒﮒﭨﭦﮔﮒﭦ۵ﮒﮒﭦ"""
    partition_name = f"{table_name}_{start_date.strftime('%Y%m')}"
    
    sql = f"""
    CREATE TABLE {partition_name} PARTITION OF {table_name}
    FOR VALUES FROM ('{start_date.strftime('%Y-%m-%d')}') 
    TO ('{end_date.strftime('%Y-%m-%d')}');
    """
    
    return sql

def create_weekly_partition(table_name, start_date, end_date):
    """ﮒﮒﭨﭦﮒ۷ﮒﭦ۵ﮒﮒﭦ"""
    partition_name = f"{table_name}_{start_date.strftime('%Y%W')}"
    
    sql = f"""
    CREATE TABLE {partition_name} PARTITION OF {table_name}
    FOR VALUES FROM ('{start_date.strftime('%Y-%m-%d')}') 
    TO ('{end_date.strftime('%Y-%m-%d')}');
    """
    
    return sql

def auto_create_partitions(conn, table_name, partition_type='monthly', months_ahead=12):
    """ﻟ۹ﮒ۷ﮒﮒﭨﭦﮔ۹ﮔ۴ﮒﮒﭦ"""
    cursor = conn.cursor()
    
    for i in range(months_ahead):
        if partition_type == 'monthly':
            start_date = datetime.now() + relativedelta(months=i)
            start_date = start_date.replace(day=1)
            end_date = start_date + relativedelta(months=1)
            sql = create_monthly_partition(table_name, start_date, end_date)
        elif partition_type == 'weekly':
            start_date = datetime.now() + timedelta(weeks=i)
            start_date = start_date - timedelta(days=start_date.weekday())
            end_date = start_date + timedelta(days=7)
            sql = create_weekly_partition(table_name, start_date, end_date)
        
        try:
            cursor.execute(sql)
            print(f"ﮒﮒﭨﭦﮒﮒﭦﮔﮒ: {sql}")
        except Exception as e:
            print(f"ﮒﮒﭨﭦﮒﮒﭦﮒ۳ﺎﻟﺑ۴: {e}")
    
    conn.commit()
    cursor.close()

# ﻛﺛﺟﻝ۷ﻝ۳ﭦﻛﺝ
conn = psycopg2.connect(
    host='localhost',
    database='zephyr_alpha',
    user='postgres',
    password='password'
)

# ﻟ۹ﮒ۷ﮒﮒﭨﭦﮔ۹ﮔ۴12ﻛﺕ۹ﮔﻝﮒ?
auto_create_partitions(conn, 'trades', 'monthly', 12)
auto_create_partitions(conn, 'position_history', 'monthly', 12)
auto_create_partitions(conn, 'account_snapshots', 'monthly', 12)
auto_create_partitions(conn, 'system_metrics', 'weekly', 52)
```

### 4.4 ﻛﺕﻛﺕﮒﭨﭦﻟ؟؟

**ﮔ۷ﻟﮔﺗﮔ۰**: **ﮔﮔﮒﮒﭦ + ﮒﭨﭘﻠﺟﻛﺟﻝﮔﭘﻠﺑ**

**ﻝﻝﺎ**:
1. **ﻝﻝ؟۰ﮒﻟ۶**: ﻟﺁﻝﻛﺙﻟ۵ﮔﺎﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﻛﺟ??
2. **ﮔ۴ﻟﺁ۱ﮔ۶ﻟﺛ**: ﮔﮔﮒﮒﭦﮔ۴ﻟﺁ۱ﮔ۶ﻟﺛﮔﺑﻛﺙﺅﺙﮒﮒﺍﮔ،ﮔﻟﮒﺑﺅﺙ
3. **ﮒﮒﺎﮒﮔﭖ**: 7-10ﮒﺗﺑﮔﺍﮔ؟ﮔﺁﮔﻠﺟﮔﻝ­ﻝ۴ﮒ?
4. **ﻛﺕﻛﺕﮔ ﮒ**: ﻝ؛۵ﮒﻠ۰ﭘﻝﭦ۶ﻠﮒﮔﭦﮔﮔ ﮒ

**ﮒ؟ﮔﺛﮒﭨﭦﻟ؟؟**:
1. ﻛﺟ؟ﮔﺗﮒﮒﭦﻝ­ﻝ۴ﻛﺕﭦﮔﮔﮒ?
2. ﮒﭨﭘﻠﺟﻛﺟﻝﮔﭘﻠﺑﻟﺏﻛﺕﻛﺕﮔ ?
3. ﮒ؟ﻝﺍﮒﮒﭦﻟ۹ﮒ۷ﻝ؟۰ﻝﻟﮔ؛
4. ﮒﭨﭦﻝ،ﮒﮒﭦﻝﮔ۶ﮒﻟ­۵ﮔﭦﮒﭘ

---

## 5. ﻝ۰؟ﻟ؟۳?: ﻝﺑ۱ﮒﺙﻝ­ﻝ۴ﻟﺁﮒ؟۰

### 5.1 ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒ

**ﮔ ﺕﮒﺟﮒﮒ**: ﻝﺑ۱ﮒﺙﮒﻟﭘﺏﻙﻟ۵ﻝﮔ۴ﻟﺁ۱ﻙﻠﺟﮒﮒ?

| ﻟ۰۷ﻝﺎﭨ?| ﻛﺕﻛﺕﮔ ﮒﻝﺑ۱ﮒﺙ?| ﮔ ﺕﮒﺟﻝﺑ۱ﮒﺙﻝﺎﭨﮒ | ﻝﻝﺎ | ﻟ۰ﻛﺕﮔ۰ﻛﺝ |
|--------|----------------|--------------|------|----------|
| **ﻟﺑ۵ﮔﺓ?* | 6-8ﻛﺕ۹ﻝﺑ۱?| B-tree + ﮒﺁﻛﺕﻝﺑ۱ﮒﺙ | ﮔ۴ﻟﺁ۱ﻠ۱ﻝﺗﻙﮒﺏﻟﮒ۳ | ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |
| **ﮔﻛﭨ?* | 8-10ﻛﺕ۹ﻝﺑ۱?| B-tree + ﮒ۳ﮒﻝﺑ۱ﮒﺙ | ﮔ۴ﻟﺁ۱ﮒ۳ﮔﻙﮒﺏﻟﮒ۳ | ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |
| **ﻟ؟۱ﮒ?* | 10-15ﻛﺕ۹ﻝﺑ۱?| B-tree + ﮒ۳ﮒﻝﺑ۱ﮒﺙ + ﻠ۷ﮒﻝﺑ۱ﮒﺙ | ﮔ۴ﻟﺁ۱ﮔﮒ۳ﮔﻙﻝﭘﮔﮒ۳ | ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |
| **ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ?* | 8-12ﻛﺕ۹ﻝﺑ۱?| B-tree + ﮒ۳ﮒﻝﺑ۱ﮒﺙ + ﮔﭘﻠﺑﻝﺑ۱ﮒﺙ | ﮔ۴ﻟﺁ۱ﻠ۱ﻝﺗﻙﮔﭘﻠﺑﻟ?| ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |

### 5.2 ﮒﺛﮒﻟ؟ﺝﻟ؟۰ﻟﺁﮒ؟۰

| ﻟ۰۷ﮒ | ﮒﺛﮒﻝﺑ۱ﮒﺙ?| ﻛﺕﻛﺕﮔ ﮒ | ﮒﺓ؟ﻟﺓ | ﻟﺁﮒ؟۰ﻝﭨﮔ |
|------|------------|----------|------|----------|
| **accounts** | 3?| 6-8?| -3~-5?| ?ﻛﺕﻟﭘﺏ |
| **positions** | 4?| 8-10?| -4~-6?| ?ﻛﺕﻟﭘﺏ |
| **orders** | 7?| 10-15?| -3~-8?| ?ﻛﺕﻟﭘﺏ |
| **trades** | 6?| 8-12?| -2~-6?| ﻗ ﺅﺕ ﻝ۴ﮒﺍ |

### 5.3 ﻛﺕﻛﺕﻛﺙﮒﮔﺗﮔ۰

#### accountsﻟ۰۷ﻝﺑ۱ﮒﺙﻛﺙﮒﺅﺙﮒ۱ﮒ ?ﻛﺕ۹ﻝﺑ۱ﮒﺙﺅﺙ

```sql
-- ﮒﺛﮒﻝﺑ۱ﮒﺙ
CREATE UNIQUE INDEX idx_accounts_code ON accounts(account_code);
CREATE INDEX idx_accounts_status ON accounts(status);
CREATE INDEX idx_accounts_created_at ON accounts(created_at);

-- ﮔﺍﮒ۱ﻝﺑ۱ﮒﺙﺅﺙﻛﺕﻛﺕﮔ ﮒﺅﺙ
CREATE INDEX idx_accounts_type ON accounts(account_type);
CREATE INDEX idx_accounts_broker ON accounts(broker) WHERE broker IS NOT NULL;
CREATE INDEX idx_accounts_total_assets ON accounts(total_assets DESC);
CREATE INDEX idx_accounts_updated_at ON accounts(updated_at);

-- ﮒ۳ﮒﻝﺑ۱ﮒﺙﺅﺙﮔ۴ﻟﺁ۱ﻛﺙﮒﺅﺙ
CREATE INDEX idx_accounts_status_type ON accounts(status, account_type);
```

**ﮔﺍﮒ۱ﻝﺑ۱ﮒﺙﻟﺁﺑﮔ**:
1. `idx_accounts_type`: ﮔﻟﺑ۵ﮔﺓﻝﺎﭨﮒﮔ۴ﻟﺁ۱ﺅﺙsimulation/production?
2. `idx_accounts_broker`: ﮔﮒﺕﮒﮔ۴ﻟﺁ۱ﺅﺙﻠ۷ﮒﻝﺑ۱ﮒﺙﺅﺙﻛﭨﻠﻝ۸ﭦﮒﺙﺅﺙ
3. `idx_accounts_total_assets`: ﮔﮔﭨﻟﭖﻛﭦ۶ﮔﮒﭦﺅﺙﻠﮒﭦﺅﺙﮔﺁﮔTOP Nﮔ۴ﻟﺁ۱?
4. `idx_accounts_updated_at`: ﮔﮔﺑﮔﺍﮔﭘﻠﺑﮔ۴ﻟﺁ۱ﺅﺙﮔﺁﮔﮒ۱ﻠﮒﮔ­۴?
5. `idx_accounts_status_type`: ﮒ۳ﮒﻝﺑ۱ﮒﺙﺅﺙﻝﭘ?ﻝﺎﭨﮒﺅﺙﮔﺁﮔﻝﭨﮒﮔ۴ﻟﺁ۱ﺅﺙ

---

#### positionsﻟ۰۷ﻝﺑ۱ﮒﺙﻛﺙﮒﺅﺙﮒ۱ﮒ ?ﻛﺕ۹ﻝﺑ۱ﮒﺙﺅﺙ

```sql
-- ﮒﺛﮒﻝﺑ۱ﮒﺙ
CREATE INDEX idx_positions_account_id ON positions(account_id);
CREATE INDEX idx_positions_stock_code ON positions(stock_code);
CREATE UNIQUE INDEX idx_positions_unique ON positions(account_id, stock_code);
CREATE INDEX idx_positions_updated_at ON positions(updated_at);

-- ﮔﺍﮒ۱ﻝﺑ۱ﮒﺙﺅﺙﻛﺕﻛﺕﮔ ﮒﺅﺙ
CREATE INDEX idx_positions_exchange ON positions(exchange);
CREATE INDEX idx_positions_quantity ON positions(quantity DESC) WHERE quantity > 0;
CREATE INDEX idx_positions_market_value ON positions(market_value DESC);
CREATE INDEX idx_positions_unrealized_pnl ON positions(unrealized_pnl DESC);
CREATE INDEX idx_positions_last_trade_date ON positions(last_trade_date DESC);

-- ﮒ۳ﮒﻝﺑ۱ﮒﺙﺅﺙﮔ۴ﻟﺁ۱ﻛﺙﮒﺅﺙ
CREATE INDEX idx_positions_account_stock ON positions(account_id, stock_code, quantity);
```

**ﮔﺍﮒ۱ﻝﺑ۱ﮒﺙﻟﺁﺑﮔ**:
1. `idx_positions_exchange`: ﮔﻛﭦ۳ﮔﮔﮔ۴ﻟﺁ۱ﺅﺙSH/SZ?
2. `idx_positions_quantity`: ﮔﮔﻛﭨﮔﺍﻠﮔ۴ﻟﺁ۱ﺅﺙﻠ۷ﮒﻝﺑ۱ﮒﺙﺅﺙﻛﭨﮔﻛﭨ>0?
3. `idx_positions_market_value`: ﮔﮒﺕﮒﺙﮔﮒﭦﺅﺙﻠﮒﭦﺅﺙﮔﺁﮔTOP Nﮔ۴ﻟﺁ۱?
4. `idx_positions_unrealized_pnl`: ﮔﮔﭖ؟ﮒ۷ﻝﻛﭦﮔﮒﭦﺅﺙﻠﮒﭦﺅﺙﮔﺁﮔﻝﻛﭦﮒﮔﺅﺙ
5. `idx_positions_last_trade_date`: ﮔﮔﮒﻛﭦ۳ﮔﮔ۴ﮔﮔﮒﭦﺅﺙﮔﺁﮔﮔﺑﭨﻟﺓﮔﻛﭨﮔ۴ﻟﺁ۱?
6. `idx_positions_account_stock`: ﮒ۳ﮒﻝﺑ۱ﮒﺙﺅﺙﻟﺑ۵?ﻟ۰ﻝ۴۷+ﮔﺍﻠﺅﺙﮔﺁﮔﮒﺟ،ﻠﮔ۴ﻟﺁ۱ﺅﺙ

---

#### ordersﻟ۰۷ﻝﺑ۱ﮒﺙﻛﺙﮒﺅﺙﮒ۱ﮒ ?2ﻛﺕ۹ﻝﺑ۱ﮒﺙﺅﺙ

```sql
-- ﮒﺛﮒﻝﺑ۱ﮒﺙ
CREATE UNIQUE INDEX idx_orders_code ON orders(order_code);
CREATE INDEX idx_orders_account_id ON orders(account_id);
CREATE INDEX idx_orders_signal_id ON orders(signal_id);
CREATE INDEX idx_orders_stock_code ON orders(stock_code);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_engine_id ON orders(engine_id);

-- ﮔﺍﮒ۱ﻝﺑ۱ﮒﺙﺅﺙﻛﺕﻛﺕﮔ ﮒﺅﺙ
CREATE INDEX idx_orders_direction ON orders(direction);
CREATE INDEX idx_orders_order_type ON orders(order_type);
CREATE INDEX idx_orders_filled_at ON orders(filled_at) WHERE filled_at IS NOT NULL;
CREATE INDEX idx_orders_status_created ON orders(status, created_at DESC);
CREATE INDEX idx_orders_account_status ON orders(account_id, status, created_at DESC);

-- ﻠ۷ﮒﻝﺑ۱ﮒﺙﺅﺙﮔﺑﭨﻟﺓﻟ؟۱ﮒﺅﺙ
CREATE INDEX idx_orders_active ON orders(account_id, stock_code, created_at DESC)
WHERE status IN ('pending', 'submitted', 'partial_filled');
```

**ﮔﺍﮒ۱ﻝﺑ۱ﮒﺙﻟﺁﺑﮔ**:
1. `idx_orders_direction`: ﮔﻛﭦ۳ﮔﮔﺗﮒﮔ۴ﻟﺁ۱ﺅﺙbuy/sell?
2. `idx_orders_order_type`: ﮔﻟ؟۱ﮒﻝﺎﭨﮒﮔ۴ﻟﺁ۱ﺅﺙmarket/limit?
3. `idx_orders_filled_at`: ﮔﮔﻛﭦ۳ﮔﭘﻠﺑﮔ۴ﻟﺁ۱ﺅﺙﻠ۷ﮒﻝﺑ۱ﮒﺙﺅﺙﻛﭨﮒﺓﺎﮔﻛﭦ۳ﻟ؟۱ﮒﺅﺙ
4. `idx_orders_status_created`: ﮒ۳ﮒﻝﺑ۱ﮒﺙﺅﺙﻝﭘ?ﮒﮒﭨﭦﮔﭘﻠﺑﺅﺙﮔﺁﮔﻝﭘﮔﮔ۴ﻟﺁ۱ﺅﺙ
5. `idx_orders_account_status`: ﮒ۳ﮒﻝﺑ۱ﮒﺙﺅﺙﻟﺑ۵?ﻝ?ﮔﭘﻠﺑﺅﺙﮔﺁﮔﻟﺑ۵ﮔﺓﻟ؟۱ﮒﮔ۴ﻟﺁ۱ﺅﺙ
6. `idx_orders_active`: ﻠ۷ﮒﻝﺑ۱ﮒﺙﺅﺙﮔﺑﭨﻟﺓﻟ؟۱ﮒﺅﺙﻛﺙﮒﮔ۴ﻟﺁ۱ﮔ۶ﻟﺛ?

---

#### tradesﻟ۰۷ﻝﺑ۱ﮒﺙﻛﺙﮒﺅﺙﮒ۱ﮒ ?0ﻛﺕ۹ﻝﺑ۱ﮒﺙﺅﺙ

```sql
-- ﮒﺛﮒﻝﺑ۱ﮒﺙ
CREATE UNIQUE INDEX idx_trades_code ON trades(trade_code);
CREATE INDEX idx_trades_order_id ON trades(order_id);
CREATE INDEX idx_trades_account_id ON trades(account_id);
CREATE INDEX idx_trades_stock_code ON trades(stock_code);
CREATE INDEX idx_trades_traded_at ON trades(traded_at);
CREATE INDEX idx_trades_engine_id ON trades(engine_id);

-- ﮔﺍﮒ۱ﻝﺑ۱ﮒﺙﺅﺙﻛﺕﻛﺕﮔ ﮒﺅﺙ
CREATE INDEX idx_trades_direction ON trades(direction);
CREATE INDEX idx_trades_account_traded ON trades(account_id, traded_at DESC);
CREATE INDEX idx_trades_stock_traded ON trades(stock_code, traded_at DESC);
CREATE INDEX idx_trades_amount ON trades(trade_amount DESC);
```

**ﮔﺍﮒ۱ﻝﺑ۱ﮒﺙﻟﺁﺑﮔ**:
1. `idx_trades_direction`: ﮔﻛﭦ۳ﮔﮔﺗﮒﮔ۴ﻟﺁ۱ﺅﺙbuy/sell?
2. `idx_trades_account_traded`: ﮒ۳ﮒﻝﺑ۱ﮒﺙﺅﺙﻟﺑ۵?ﮔﭘﻠﺑﺅﺙﮔﺁﮔﻟﺑ۵ﮔﺓﻛﭦ۳ﮔﮒﮒﺎﮔ۴ﻟﺁ۱ﺅﺙ
3. `idx_trades_stock_traded`: ﮒ۳ﮒﻝﺑ۱ﮒﺙﺅﺙﻟ۰?ﮔﭘﻠﺑﺅﺙﮔﺁﮔﻟ۰ﻝ۴۷ﻛﭦ۳ﮔﮒﮒﺎﮔ۴ﻟﺁ۱ﺅﺙ
4. `idx_trades_amount`: ﮔﻛﭦ۳ﮔﻠﻠ۱ﮔﮒﭦﺅﺙﻠﮒﭦﺅﺙﮔﺁﮔﮒ۳۶ﻠ۱ﻛﭦ۳ﮔﮔ۴ﻟﺁ۱ﺅﺙ

---

### 5.4 ﻛﺕﻛﺕﮒﭨﭦﻟ؟؟

**ﮔ۷ﻟﮔﺗﮔ۰**: **ﮒ۱ﮒ ﻝﺑ۱ﮒﺙﻟﺏﻛﺕﻛﺕﮔ ?*

**ﻝﻝﺎ**:
1. **ﮔ۴ﻟﺁ۱ﮔ۶ﻟﺛ**: ﻝﺑ۱ﮒﺙﮒﻟﭘﺏﮒﺁﮔﺝﻟﮔﮒﮔ۴ﻟﺁ۱ﮔ۶ﻟﺛ?-10ﮒﺅﺙ
2. **ﻟ۵ﻝﮔ۴ﻟﺁ۱**: ﮒ۳ﮒﻝﺑ۱ﮒﺙﮒﺁﻟ۵ﻝﮒ۳۶ﻠ۷ﮒﮔ۴ﻟﺁ۱ﮒﭦﮔﺁ
3. **ﻠ۷ﮒﻝﺑ۱ﮒﺙ**: ﮒﮒﺍﻝﺑ۱ﮒﺙﮒ۳۶ﮒﺍﺅﺙﮔﮒﮔ۶ﻟﺛ
4. **ﻛﺕﻛﺕﮔ ﮒ**: ﻝ؛۵ﮒﻠ۰ﭘﻝﭦ۶ﻠﮒﮔﭦﮔﮔ ﮒ

**ﮒ؟ﮔﺛﮒﭨﭦﻟ؟؟**:
1. ﮒ۱ﮒ ﻝﺑ۱ﮒﺙﻟﺏﻛﺕﻛﺕﮔ ﮒﺅﺙaccounts: 7? positions: 9? orders: 12? trades: 10ﻛﺕ۹ﺅﺙ
2. ﮒﮒﭨﭦﮒ۳ﮒﻝﺑ۱ﮒﺙﻟ۵ﻝﻠ،ﻠ۱ﮔ۴ﻟﺁ۱
3. ﻛﺛﺟﻝ۷ﻠ۷ﮒﻝﺑ۱ﮒﺙﻛﺙﮒﮔ۶ﻟﺛ
4. ﮒﭨﭦﻝ،ﻝﺑ۱ﮒﺙﻝﮔ۶ﮔﭦﮒﭘﺅﺙﮒ؟ﮔﮒﮔﻝﺑ۱ﮒﺙﻛﺛﺟﻝ۷ﻝ?

---

## 6. ﻝﭨﺙﮒﻛﺙﮒﮔﺗﮔ۰

### 6.1 ﻛﺙﮒﻛﺙﮒ?

| ﻛﺙﮒ?| ﻠ۲ﻠ۸ﻝ­ﻝﭦ۶ | ﻛﺙﮒﻠﺝﮒﭦ۵ | ﻛﺙﮒ?| ﻠ۱ﻟ؟۰ﮒﺓ۴ﮔﭘ |
|--------|----------|----------|--------|----------|
| **ﮔﺍﮔ؟ﻝﺎﭨﮒﻛﺙﮒ** | ﻭﺑ ﻠ،ﻠ۲?| ?| P0 | 0.5?|
| **ﮒﮒﭦﻝ­ﻝ۴ﻛﺙﮒ** | ﻭﺑ ﻠ،ﻠ۲?| ?| P0 | 1?|
| **ﻝﺑ۱ﮒﺙﻝ­ﻝ۴ﻛﺙﮒ** | ﻭ۰ ﻛﺕ­ﻠ۲?| ?| P1 | 0.5?|
| **ﻟ۰۷ﻝﭨﮔﻛﺙ?* | ﻭ۱ ﻛﺛﻠ۲?| ?| P2 | 0.5?|

### 6.2 ﻛﺙﮒﮒ؟ﮔﺛﻟ؟۰ﮒ

#### ﻝ؛؛ﻛﺕﮔ­۴ﺅﺙﮔﺍﮔ؟ﻝﺎﭨﮒﻛﺙﮒ?.5ﮒ۳۸ﺅﺙ

```sql
-- ﮔ۶ﻟ۰ﮔﺍﮔ؟ﻝﺎﭨﮒﻛﺙﮒﻟﮔ؛
-- ﻟﺁ۵ﻟ۶?.3ﻟﮔﺗﮔ۰A
```

#### ﻝ؛؛ﻛﭦﮔ­۴ﺅﺙﮒﮒﭦﻝ­ﻝ۴ﻛﺙﮒ?ﮒ۳۸ﺅﺙ

```sql
-- ﻠﮔﺍﮒﮒﭨﭦﮒﮒﭦ?
-- ﻟﺁ۵ﻟ۶?.3ﻟﻛﺙﮒﮔﺗ?
```

#### ﻝ؛؛ﻛﺕﮔ­۴ﺅﺙﻝﺑ۱ﮒﺙﻝ­ﻝ۴ﻛﺙﮒ?.5ﮒ۳۸ﺅﺙ

```sql
-- ﮒﮒﭨﭦﮔﺍﮒ۱ﻝﺑ۱ﮒﺙ
-- ﻟﺁ۵ﻟ۶?.3ﻟﻛﺙﮒﮔﺗ?
```

#### ﻝ؛؛ﮒﮔ­۴ﺅﺙﻟ۰۷ﻝﭨﮔﻛﺙﮒﺅﺙ0.5ﮒ۳۸ﺅﺙ

```sql
-- ﮒ ﻠ۳ﮒﻛﺛﮒ­ﮔ؟ﭖ
ALTER TABLE accounts DROP COLUMN total_market_value;
ALTER TABLE accounts DROP COLUMN daily_pnl;
```

### 6.3 ﻛﺙﮒﮒﻝ؛۵ﮒﮒﭦ۵ﻟﺁﻛﺙﺍ

| ﻟ؟ﺝﻟ؟۰ﻝﭨﺑﮒﭦ۵ | ﻛﺙﮒﮒﻝ؛۵ﮒﮒﭦ۵ | ﻛﺙﮒﮒﻝ؛۵ﮒﮒﭦ۵ | ﮔﮒﮒﺗﮒﭦ۵ | ﻟﺝﺝﮔ ﻝ?|
|----------|--------------|--------------|----------|----------|
| **ﻟ۰۷ﻝﭨﮔﻟ؟ﺝ?* | 85% | 95% | +10% | ?ﻟﺝﺝﮔ  |
| **ﮔﺍﮔ؟ﻝﺎﭨﮒﻠﮔ۸** | 70% | 100% | +30% | ?ﻟﺝﺝﮔ  |
| **ﮒﮒﭦﻝ­ﻝ۴** | 60% | 95% | +35% | ?ﻟﺝﺝﮔ  |
| **ﻝﺑ۱ﮒﺙﻝ­ﻝ۴** | 80% | 95% | +15% | ?ﻟﺝﺝﮔ  |
| **ﮔﺑﻛﺛﻝ؛۵ﮒ?* | 75% | **96%** | +21% | ?**ﻟﺝﺝﮔ ** |

---

## 7. ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﻛﺛﺏﮒ؟?

### 7.1 ﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﮒ?

1. **ﻝﺎﺝﮒﭦ۵ﻛﺙﮒ**: ﮒ؟ﮒﺁﻟﺟﮒﭦ۵ﻝﺎﺝﻝ۰؟ﺅﺙﻛﺕﮒﺁﻝﺎﺝﮒﭦ۵ﻛﺕ?
2. **ﮒﮒﭦﻝﭨﮒ**: ﮔﮔﮒﮒﭦﺅﺙﮔ۴ﻟﺁ۱ﮔ۶ﻟﺛﮔ?
3. **ﻝﺑ۱ﮒﺙﮒﻟﭘﺏ**: ﻟ۵ﻝﮔ۴ﻟﺁ۱ﺅﺙﻠﺟﮒﮒ۷ﻟ۰۷ﮔ،?
4. **ﻛﺟﻝﮒﭨﭘﻠﺟ**: ﮔﭨ۰ﻟﭘﺏﻝﻝ؟۰ﻟ۵ﮔﺎﺅﺙﮔﺁﮔﮒﮒﺎﮒ?

### 7.2 ﻟ۰ﻛﺕﮔ۰ﻛﺝﮒ?

| ﮔﭦﮔﮒﻝ۶ﺍ | ﻝ؟۰ﻝﻟ۶ﮔ۷۰ | ﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﻝﺗ?| ﮒﺁﮒﻠﺑ?|
|----------|----------|----------------|----------|
| **ﮒﺗﭨﮔﺗﻠﮒ** | 600? | DECIMAL(20,4)ﻙﮔﮔﮒﮒﭦﻙﻝﺑ۱ﮒﺙﮒ?| ﻝﺎﺝﮒﭦ۵ﮔ ﮒﻙﮒﮒﭦﻝ­?|
| **ﻛﺗﮒ۳ﮔﻟﭖ** | 500? | ﻠ،ﻝﺎﺝﮒﭦ۵ﻟ؟۰ﻝ؟ﻙﮒ؟ﮔﭘﻝﮔ۶ﻙﮒﮒﺎﻟﺟﺛ?| ﮔﺍﮔ؟ﻝﺎﭨﮒﻙﻝﮔ۶ﻟ؟ﺝ?|
| **ﮔﮔﺎﺁﮔﻟﭖ** | 400? | ﮒ۳ﮒﻝﺑ۱ﮒﺙﻙﻠ۷ﮒﻝﺑ۱ﮒﺙﻙﮔ۴ﻟﺁ۱ﻛﺙ?| ﻝﺑ۱ﮒﺙﻝ­ﻝ۴ |
| **ﻟ۰ﮒ۳ﮔﻟﭖ** | 300? | ﮒﮒﭦﻟ۹ﮒ۷ﮒﻙﮔﺍﮔ؟ﻝﮒﺛﮒ۷ﮔﻝ؟۰?| ﮒﮒﭦﻝ؟۰ﻝﻙﮔﺍﮔ؟ﮔﺎﭨ?|

### 7.3 ﻝﻝ؟۰ﮒﻟ۶ﻟ۵ﮔﺎ

| ﻝﻝ؟۰ﻟ۵ﮔﺎ | ﮒﺓﻛﺛﻟ۶ﮒ؟ | ﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﻟ۵?| ﮒﺛﮒﻟ؟ﺝﻟ؟۰ﻝ؛۵ﮒ?|
|----------|----------|----------------|----------------|
| **ﻟﺁﻝ?* | ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﻛﺟﻝ7?| tradesﻟ۰۷ﻛﺟ??| ?ﻝ؛۵ﮒﺅﺙﻛﺙﮒﮒ?|
| **ﻛﺕ­ﮒﭦ?* | ﻛﭦ۳ﮔﮔ۴ﮒﺟﮒ؟ﮔﺑﻛﺟﻝ | ﮔ۴ﮒﺟﻟ۰۷ﻟ؟ﺝﻟ؟۰ﮒ؟?| ?ﻝ؛۵ﮒ |
| **ﻛﭦ۳ﮔﮔ** | ﻛﭦ۳ﮔﮔﺍﮔ؟ﮒﺁﻟﺟﺛ?| ﮒ؟۰ﻟ؟۰ﮒ­ﮔ؟ﭖﮒ؟ﮔﺑ | ?ﻝ؛۵ﮒ |

---

## 8. ﻟﺁﮒ؟۰ﻝﭨﻟ؟ﭦﻛﺕﮒﭨﭦ?

### 8.1 ﻟﺁﮒ؟۰ﻝﭨﻟ؟ﭦ

**ﮒﺛﮒﻟ؟ﺝﻟ؟۰ﻝ؛۵ﮒ?*: 75%ﺅﺙﻛﺕﻟﺝﺝﮔ ?

**ﻛﺙﮒﮒﻝ؛۵ﮒﮒﭦ۵**: 96%ﺅﺙﻟﺝﺝﮔ ﺅﺙ

**ﻟﺁﮒ؟۰ﻝﭨﻟ؟ﭦ**: **ﮔﮔ۰ﻛﭨﭘﮔﺗ?*

**ﮔﺗﮒﮔ۰ﻛﭨﭘ**:
1. ﮒﺟﻠ۰ﭨﻛﺙﮒﮔﺍﮔ؟ﻝﺎﭨﮒﺅﺙP0ﺅﺙﻠ،ﻠ۲ﻠ۸?
2. ﮒﺟﻠ۰ﭨﻛﺙﮒﮒﮒﭦﻝ­ﻝ۴ﺅﺙP0ﺅﺙﻠ،ﻠ۲ﻠ۸?
3. ﮒﭨﭦﻟ؟؟ﻛﺙﮒﻝﺑ۱ﮒﺙﻝ­ﻝ۴ﺅﺙP1ﺅﺙﻛﺕ­ﻠ۲ﻠ۸?
4. ﮒﭨﭦﻟ؟؟ﻛﺙﮒﻟ۰۷ﻝﭨﮔﺅﺙP2ﺅﺙﻛﺛﻠ۲ﻠ۸?

### 8.2 ﻛﺕﻛﺕﮔ­۴ﻟ۰?

**ﻝ،ﮒﺏﻟ۰ﮒ۷**?026-04-02?
1. ﮔ۶ﻟ۰ﮔﺍﮔ؟ﻝﺎﭨﮒﻛﺙﮒ?.5ﮒ۳۸ﺅﺙ
2. ﮔ۶ﻟ۰ﮒﮒﭦﻝ­ﻝ۴ﻛﺙﮒ?ﮒ۳۸ﺅﺙ
3. ﮔ۶ﻟ۰ﻝﺑ۱ﮒﺙﻝ­ﻝ۴ﻛﺙﮒ?.5ﮒ۳۸ﺅﺙ
4. ﮔ۶ﻟ۰ﻟ۰۷ﻝﭨﮔﻛﺙﮒﺅﺙ0.5ﮒ۳۸ﺅﺙ

**ﻛﺙﮒﮒ؟ﮔ?*:
1. ﮔﺑﮔﺍﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﮔ?
2. ﻝﮔﻛﺙﮒﮒﻝDDLﻟﮔ؛
3. ﮒﺙﮒ۶P0-2ﮔﺍﮔ؟ﮒ­ﮒﺕﻟ؟ﺝﻟ؟۰

---

**ﻝﮔ؛**: 1.0.0 | **ﮔﺑﮔﺍﮔ۴ﮔ**: 2026-04-02 | **ﻝ?*: ?ﮒﺓﺎﻟﺁ? 
**ﻟﺁﮒ؟۰ﻝﭨﻟ؟ﭦ**: ﮔﮔ۰ﻛﭨﭘﮔﺗ? 
**ﻝ؛۵ﮒ?*: ﻛﺙﮒ?5% ?ﻛﺙﮒ?6%  
**ﻛﺕﻛﺕ?*: ﮔ۶ﻟ۰ﻛﺙﮒﮔﺗﮔ۰ ?ﮔﺑﮔﺍﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲ ?ﮒﺙﮒ۶P0-2ﮔﺍﮔ؟ﮒ­ﮒﺕﻟ؟ﺝﻟ؟۰