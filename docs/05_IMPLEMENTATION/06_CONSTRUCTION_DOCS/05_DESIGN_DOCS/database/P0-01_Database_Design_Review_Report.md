---
module_id: DB_REVIEW_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﻟﮒﺝﮔﭘﮔ?
responsibility:
  - 因子计算
  - 交易执行
  - 数据源
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﻟﺁ?
applicable_scope: ﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﻟﺁﮒ؟۰ﻛﺕﻛﺙﮒ
compliance_level: ﻛﺕﻛﺕﮔﭦﮔﮔ ﮒ
parent_document: ../INDEX.md
implementation_status: ﻟﺟﻟ۰?---


# ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﻟﺁﮒ؟۰ﮔ۴?
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.0 - ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﻟﺁ?
> **ﻟﺁﮒ؟۰ﮒﺁﺗﻟﺎ۰**: P0-01_Database_Design_Document.md
> **ﻟﺁﮒ؟۰ﮔ ﮒ**: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮔﺁﻟ۶ﮔ ﺙﮔ ﮒv5.3
> **ﻟﺁﮒ؟۰ﮔﺗﮔﺏ**: ﮒﺁﺗﮔﺁﮒﮔ + ﻟ۰ﻛﺕﮔﻛﺛﺏﮒ؟?+ ﻠ۲ﻠ۸ﻟﺁﻛﺙﺍ

## 1. ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﮔ ?

### 1.1 ﻟ۰ﻛﺕﮔ ﮒﮒﺁﺗﮔﺁ

| ﻟ؟ﺝﻟ؟۰ﻝﭨﺑﮒﭦ۵ | ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒ | ﮒﺛﮒﻟ؟ﺝﻟ؟۰ﮔﺗﮔ۰ | ﻝ؛۵ﮒ?| ﻟﺁﮒ؟۰ﻝﭨﻟ؟ﭦ |
|----------|------------------|--------------|--------|----------|
| **ﻟ۰۷ﻝﭨﮔﻟ؟ﺝ?* | ﮔ ﺕﮒﺟ?5-25ﻛﺕ۹ﮒ­?| 18-30ﻛﺕ۹ﮒ­?| 85% | ﻗ ﺅﺕ ﻠﻛﺙﮒ |
| **ﮔﺍﮔ؟ﻝﺎﭨﮒﻠﮔ۸** | ﻠﻠ۱DECIMAL(20,4) | DECIMAL(18,2) | 70% | ?ﻠﻟﺍﮔﺑ |
| **ﮒﮒﭦﻝ­ﻝ۴** | ﮔﮔﮒﮒﭦﺅﺙﻛﺟ??| ﮔﮒ­۲ﮒﭦ۵ﮒﮒﭦﺅﺙﻛﺟﻝ1-5?| 60% | ?ﻠﻟﺍﮔﺑ |
| **ﻝﺑ۱ﮒﺙﻝ­ﻝ۴** | ﮔ ﺕﮒﺟ?-10ﻛﺕ۹ﻝﺑ۱?| ﮒﺗﺏﮒ4ﻛﺕ۹ﻝﺑ۱?| 80% | ﻗ ﺅﺕ ﻠﻛﺙﮒ |
| **ﮔﺑﻛﺛﻝ؛۵ﮒ?* | ?0% | 75% | ?**ﻛﺕﻟﺝﺝ?* |

**ﻟﺁﮒ؟۰ﻝﭨﻟ؟ﭦ**: ﮒﺛﮒﻟ؟ﺝﻟ؟۰ﻝ؛۵ﮒ?5%ﺅﺙﻟﺓﻝ۵ﭨﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒﺅﺙ?0%ﺅﺙﻟﺟ?*15%ﻝﮒﺓ؟?*ﺅﺙﻠﻟ۵ﻟﺟﻟ۰ﻛﺙﮒﻟﺍﮔ?

---

## 2. ﻝ۰؟ﻟ؟۳?: ﻟ۰۷ﻝﭨﮔﻟ؟ﺝﻟ؟۰ﻟﺁ?

### 2.1 ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒ

**ﮔ ﺕﮒﺟﮒﮒ**: ﮒ­ﮔ؟ﭖﮔﺍﻠﻠﻛﺕ­ﺅﺙﻟﻟﺑ۲ﮒﻛﺕﺅﺙﻠﺟﮒﻟﺟﮒﭦ۵ﻟ؟ﺝ?

| ﻟ۰۷ﻝﺎﭨ?| ﻛﺕﻛﺕﮔ ﮒﮒ­ﮔ؟ﭖ?| ﻝﻝﺎ | ﻟ۰ﻛﺕﮔ۰ﻛﺝ |
|--------|----------------|------|----------|
| **ﻟﺑ۵ﮔﺓ?* | 15-20ﻛﺕ۹ﮒ­?| ﮔ ﺕﮒﺟﻛﺕﮒ۰ﮒ؟ﻛﺛﺅﺙﮒ­ﮔ؟ﭖﻠﻛﺕ­ | ﮒﺗﭨﮔﺗﻠﮒﻙﻛﺗﮒ۳ﮔ?|
| **ﮔﻛﭨ?* | 18-22ﻛﺕ۹ﮒ­?| ﻠﻟ۵ﻟﺁ۵ﻝﭨﻝﮔﻛﭨﻛﺟ۰ﮔﺁ | ﮔﮔﺎﺁﮔﻟﭖﻙﻟ۰ﮒ۳ﮔ?|
| **ﻟ؟۱ﮒ?* | 25-30ﻛﺕ۹ﮒ­?| ﻟ؟۱ﮒﻝﮒﺛﮒ۷ﮔﮒ۳ﮔﺅﺙﮒ­ﮔ؟ﭖﻟﺝ?| ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |
| **ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ?* | 15-18ﻛﺕ۹ﮒ­?| ﻛﭦ۳ﮔﮔﻝﭨﺅﺙﮒ­ﮔ؟ﭖﻝﺎﺝﻝ؟ | ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |

### 2.2 ﮒﺛﮒﻟ؟ﺝﻟ؟۰ﻟﺁﮒ؟۰

| ﻟ۰۷ﮒ | ﮒﺛﮒﮒ­ﮔ؟ﭖ?| ﻛﺕﻛﺕﮔ ﮒ | ﻟﺁﮒ؟۰ﻝﭨﮔ | ﻛﺙﮒﮒﭨﭦﻟ؟؟ |
|------|------------|----------|----------|----------|
| **accounts** | 21?| 15-20?| ﻗ ﺅﺕ ﻝ۴ﮒ۳ | ﮒﮒﺍ1-2ﻛﺕ۹ﻠﮔ ﺕﮒﺟﮒ­ﮔ؟ﭖ |
| **positions** | 20?| 18-22?| ?ﮒﮔ ﺙ | ﮔ ﻠﻟﺍﮔﺑ |
| **orders** | 30?| 25-30?| ?ﮒﮔ ﺙ | ﮔ ﻠﻟﺍﮔﺑ |
| **trades** | 18?| 15-18?| ?ﮒﮔ ﺙ | ﮔ ﻠﻟﺍﮔﺑ |

### 2.3 ﻛﺕﻛﺕﻛﺙﮒﮒﭨﭦﻟ؟؟

#### accountsﻟ۰۷ﻛﺙﮒﺅﺙﮒﮒﺍ?9ﻛﺕ۹ﮒ­ﮔ؟ﭖﺅﺙ

**ﮒﭨﭦﻟ؟؟ﮒ ﻠ۳ﻝﮒ­?*:
```sql
-- ﮒ ﻠ۳ﻛﭨ۴ﻛﺕ2ﻛﺕ۹ﮒ­ﮔ؟ﭖﺅﺙﮒﺁﻠﻟﺟﻟ؟۰ﻝ؟ﮒﺝﮒﭦ?
-- 1. total_market_valueﺅﺙﮔﭨﮒﺕﮒﺙﺅﺙ - ﮒﺁﻠﻟﺟpositionsﻟ۰۷ﻟﮒﻟ؟۰?
-- 2. daily_pnlﺅﺙﮒﺛﮔ۴ﻝﻛﭦﺅﺙ - ﮒﺁﻠﻟﺟaccount_snapshotsﻟ۰۷ﮔ۴?

-- ﻛﺙﮒﮒﻝaccountsﻟ۰۷ﺅﺙ19ﻛﺕ۹ﮒ­ﮔ؟ﭖﺅﺙ
accounts (
    id, account_code, account_name, account_type, broker,
    initial_capital, current_capital, available_cash, frozen_cash,
    total_assets, total_pnl, max_drawdown, status,
    created_at, updated_at, metadata  -- 16ﻛﺕ۹ﮒﭦﻝ۰ﮒ­ﮔ؟ﭖ
    -- ﮒ ﻠ۳: total_market_value, daily_pnl
)
```

**ﻝﻝﺎ**:
1. **ﻠﺟﮒﮔﺍﮔ؟ﮒﻛﺛ**: `total_market_value`ﮒﺁﻠﻟﺟﮔﻛﭨﻟ۰۷ﮒ؟ﮔﭘﻟ؟۰?
2. **ﮔﺍﮔ؟ﻛﺕﻟ?*: `daily_pnl`ﮒ۷account_snapshotsﻟ۰۷ﻛﺕ­ﮒﺓﺎﮔﻟ؟ﺍﮒﺛ
3. **ﻛﺕﻛﺕﮒ؟ﻟﺓﭖ**: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﻠﮒﺕﺕﮒﺍﻟ؟۰ﻝ؟ﮒ­ﮔ؟ﭖﻛﺕﮒﭦﻝ۰ﮒ­ﮔ؟ﭖﮒﻝ۵ﭨ

---

## 3. ﻝ۰؟ﻟ؟۳?: ﮔﺍﮔ؟ﻝﺎﭨﮒﻠﮔ۸ﻟﺁﮒ؟۰

### 3.1 ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒ

**ﮔ ﺕﮒﺟﮒﮒ**: ﻝﺎﺝﮒﭦ۵ﻛﺙﮒﺅﺙﮒ؟ﮒﺁﻟﺟﮒﭦ۵ﻝﺎﺝﻝ۰؟ﺅﺙﻛﺕﮒﺁﻝﺎﺝﮒﭦ۵ﻛﺕﻟﭘﺏ

| ﮒ­ﮔ؟ﭖﻝﺎﭨﮒ | ﻛﺕﻛﺕﮔ ﮒ | ﻝﻝﺎ | ﻟ۰ﻛﺕﮔ۰ﻛﺝ |
|----------|----------|------|----------|
| **ﻠﻠ۱ﮒ­ﮔ؟ﭖ** | DECIMAL(20,4) | 1. ﮔﺁﮔﻛﺕﻛﭦﺟﻝﭦ۶ﻟﭖ?br>2. ﻝﺎﺝﮒﭦ۵4ﻛﺛﮒﺍﮔﺍﺅﺙ0.0001?br>3. ﻠﺟﮒﻝﺎﺝﮒﭦ۵ﮔﮒ۳ﺎ | ﮒﺗﭨﮔﺗﻠﮒﺅﺙﻝ؟۰ﻝﻟ۶?00??|
| **ﻝﺝﮒﮔﺁﮒ­?* | DECIMAL(12,6) | 1. ﻝﺎﺝﮒﭦ۵6ﻛﺛﮒﺍﮔﺍﺅﺙ0.000001?br>2. ﮔﺁﮔﻝﺎﺝﻝ۰؟ﻟ؟۰ﻝ؟<br>3. ﻠﺟﮒﻝﺑﺁﻟ؟۰ﻟﺁﺁﮒﺓ؟ | ﻛﺗﮒ۳ﮔﻟﭖﺅﺙﻠ،ﻠ۱ﻛﭦ۳ﮔﺅﺙ |
| **ﻛﭨﺓﮔ ﺙﮒ­ﮔ؟ﭖ** | DECIMAL(12,4) | 1. ﻝﺎﺝﮒﭦ۵4ﻛﺛﮒﺍﮔﺍﺅﺙ0.0001?br>2. ﮔﺁﮔﻝﺎﺝﻝ۰؟ﻛﭨﺓﮔ ﺙ<br>3. ﮒﺙﮒ؟ﺗAﻟ۰ﮔﮒﺍﮒﮒ۷ﮒ?| ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |
| **ﮔﺍﻠﮒ­ﮔ؟ﭖ** | BIGINT | 1. ﮔﺁﮔﮒ۳۶ﮔﺍﻠﻝﭦ۶<br>2. ﻠﺟﮒﮔﭦ۱ﮒﭦ<br>3. ﮒﺙﮒ؟ﺗﮔﻛﭦ۳?| ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |

### 3.2 ﮒﺛﮒﻟ؟ﺝﻟ؟۰ﻟﺁﮒ؟۰

| ﮒ­ﮔ؟ﭖﻝﺎﭨﮒ | ﮒﺛﮒﻟ؟ﺝﻟ؟۰ | ﻛﺕﻛﺕﮔ ﮒ | ﮒﺓ؟ﻟﺓ | ﻠ۲ﻠ۸ﻝ­ﻝﭦ۶ |
|----------|----------|----------|------|----------|
| **ﻠﻠ۱ﮒ­ﮔ؟ﭖ** | DECIMAL(18,2) | DECIMAL(20,4) | ﻝﺎﺝﮒﭦ۵ﻛﺕﻟﭘﺏ | ﻭﺑ ﻠ،ﻠ۲?|
| **ﻝﺝﮒﮔﺁﮒ­?* | DECIMAL(10,4) | DECIMAL(12,6) | ﻝﺎﺝﮒﭦ۵ﻛﺕﻟﭘﺏ | ﻭ۰ ﻛﺕ­ﻠ۲?|
| **ﻛﭨﺓﮔ ﺙﮒ­ﮔ؟ﭖ** | DECIMAL(10,4) | DECIMAL(12,4) | ﻟﮒﺑﻛﺕﻟﭘﺏ | ﻭ۰ ﻛﺕ­ﻠ۲?|
| **ﮔﺍﻠﮒ­ﮔ؟ﭖ** | INTEGER | BIGINT | ﻟﮒﺑﻛﺕﻟﭘﺏ | ﻭ۰ ﻛﺕ­ﻠ۲?|

### 3.3 ﻛﺕﻛﺕﻛﺙﮒﮔﺗﮔ۰

#### ﮔﺗﮔ۰A: ﮒ۷ﻠ۱ﮔﮒﻝﺎﺝﮒﭦ۵ﺅﺙﮔ۷ﻟﺅﺙ

```sql
-- ﻠﻠ۱ﮒ­ﮔ؟ﭖﻛﺙﮒ
ALTER TABLE accounts 
    ALTER COLUMN initial_capital TYPE DECIMAL(20,4),
    ALTER COLUMN current_capital TYPE DECIMAL(20,4),
    ALTER COLUMN available_cash TYPE DECIMAL(20,4),
    ALTER COLUMN frozen_cash TYPE DECIMAL(20,4),
    ALTER COLUMN total_assets TYPE DECIMAL(20,4);

-- ﻝﺝﮒﮔﺁﮒ­ﮔ؟ﭖﻛﺙ?
ALTER TABLE accounts
    ALTER COLUMN max_drawdown TYPE DECIMAL(12,6);

ALTER TABLE positions
    ALTER COLUMN unrealized_pnl_pct TYPE DECIMAL(12,6);

-- ﻛﭨﺓﮔ ﺙﮒ­ﮔ؟ﭖﻛﺙﮒ
ALTER TABLE orders
    ALTER COLUMN order_price TYPE DECIMAL(12,4),
    ALTER COLUMN filled_price TYPE DECIMAL(12,4);

-- ﮔﺍﻠﮒ­ﮔ؟ﭖﻛﺙﮒ
ALTER TABLE positions
    ALTER COLUMN quantity TYPE BIGINT,
    ALTER COLUMN available_quantity TYPE BIGINT,
    ALTER COLUMN frozen_quantity TYPE BIGINT;

ALTER TABLE orders
    ALTER COLUMN order_quantity TYPE BIGINT,
    ALTER COLUMN filled_quantity TYPE BIGINT;
```

**ﻛﺙﮒﺟ**:
1. **ﻝﺎﺝﮒﭦ۵ﮒﻟﭘﺏ**: ﮔﺁﮔﻛﺕﻛﭦﺟﻝﭦ۶ﻟﭖﻠﻝ؟۰?
2. **ﻠﺟﮒﻟﺁﺁﮒﺓ؟**: 4ﻛﺛﮒﺍﮔﺍﻝﺎﺝﮒﭦ۵ﻠﺟﮒﻝﺑﺁﻟ؟۰ﻟﺁﺁ?
3. **ﮔ۸ﮒﺎﮔ۶ﮒﺙﭦ**: ﮔ۹ﮔ۴ﻟ۶ﮔ۷۰ﮔ۸ﮒ۳۶ﮔ ﻠﻛﺟ؟ﮔﺗ
4. **ﻛﺕﻛﺕﮔ ﮒ**: ﻝ؛۵ﮒﻠ۰ﭘﻝﭦ۶ﻠﮒﮔﭦﮔﮔ ﮒ

**ﮒ۲ﮒﺟ**:
1. **ﮒ­ﮒ۷ﮒ۱ﮒ **: ﮔﺁﻛﺕ۹ﮒ­ﮔ؟ﭖﮒ۱ﮒ 2-4ﮒ­ﻟ
2. **ﮔ۶ﻟﺛﮒﺛﺎﮒ**: ﻝﺎﺝﮒﭦ۵ﮔﮒﮒﺁﻟﺛﮒﺛﺎﮒﻟ؟۰ﻝ؟ﮔ۶ﻟﺛ?5%?

---

#### ﮔﺗﮔ۰B: ﮒﮒﺎﻝﺎﺝﮒﭦ۵ﻟ؟ﺝﻟ؟۰ﺅﺙﮔﻛﺕ­ﮔﺗﮔ۰ﺅﺙ

```sql
-- ﮔ ﺕﮒﺟﻠﻠ۱ﮒ­ﮔ؟ﭖﻛﺛﺟﻝ۷ﻠ،ﻝﺎﺝ?
accounts: initial_capital, current_capital, total_assets ?DECIMAL(20,4)

-- ﮔ؛۰ﻟ۵ﻠﻠ۱ﮒ­ﮔ؟ﭖﻛﺛﺟﻝ۷ﮔ ﮒﻝﺎﺝﮒﭦ۵
accounts: available_cash, frozen_cash ?DECIMAL(18,2)

-- ﻝﺝﮒﮔﺁﮒ­ﮔ؟ﭖﻛﺛﺟﻝ۷ﻠ،ﻝﺎﺝﮒﭦ۵
max_drawdown, pnl_pct ?DECIMAL(12,6)

-- ﻛﭨﺓﮔ ﺙﮒ­ﮔ؟ﭖﻛﺛﺟﻝ۷ﮔ ﮒﻝﺎﺝﮒﭦ۵
order_price, filled_price ?DECIMAL(10,4)
```

**ﻛﺙﮒﺟ**:
1. **ﮒﺗﺏﻟ۰۰ﮔ۶ﻟﺛ**: ﮔ ﺕﮒﺟﮒ­ﮔ؟ﭖﻠ،ﻝﺎﺝﮒﭦ۵ﺅﺙﮔ؛۰ﻟ۵ﮒ­ﮔ؟ﭖﮔ ﮒﻝﺎﺝﮒﭦ۵
2. **ﮒ­ﮒ۷ﻛﺙﮒ**: ﮒﮒﺍﮒ­ﮒ۷ﻝ۸ﭦﻠﺑﮒ ﻝ۷
3. **ﮔ۶ﻟﺛﻛﺙﮒ**: ﻠﻛﺛﻟ؟۰ﻝ؟ﮒﺙﻠ

**ﮒ۲ﮒﺟ**:
1. **ﮒ۳ﮔﮒﭦ۵ﮒ۱?*: ﻠﻟ۵ﻝﭨﺑﮔ۳ﻛﺕﮒﻝﺎﺝﮒﭦ۵ﮔ ?
2. **ﻛﺕﻟﺑﮔ۶ﻠ۲?*: ﻛﺕﮒﻝﺎﺝﮒﭦ۵ﮒﺁﻟﺛﮒﺁﺙﻟﺑﻟ؟۰ﻝ؟ﻟﺁﺁﮒﺓ؟

---

### 3.4 ﻛﺕﻛﺕﮒﭨﭦﻟ؟؟

**ﮔ۷ﻟﮔﺗﮔ۰**: **ﮔﺗﮔ۰A - ﮒ۷ﻠ۱ﮔﮒﻝﺎﺝﮒﭦ۵**

**ﻝﻝﺎ**:
1. **ﻛﺕﻛﺕﮔ ﮒ**: ﻝ؛۵ﮒﻠ۰ﭘﻝﭦ۶ﻠﮒﮔﭦﮔﮔ ﮒﺅﺙﮒﺗﭨﮔﺗﻙﻛﺗﮒ۳ﻙﮔﮔﺎﺁﺅﺙ
2. **ﻠﺟﮒﻟﺟﮒﺓ۴**: ﮔ۹ﮔ۴ﻟ۶ﮔ۷۰ﮔ۸ﮒ۳۶ﮔ ﻠﻛﺟ؟ﮔﺗﮔﺍﮔ؟?
3. **ﻝﺎﺝﮒﭦ۵ﻛﺙﮒ**: ﻠﮒﻛﭦ۳ﮔﮒﺁﺗﻝﺎﺝﮒﭦ۵ﻟ۵ﮔﺎﮔﻠ،ﺅﺙﮒ؟ﮒﺁﻟﺟﮒﭦ۵ﻝﺎﺝﻝ۰؟
4. **ﮔﮔ؛ﮒﺁﮔ۶**: ﮒ­ﮒ۷ﮒﮔ۶ﻟﺛﮔﮔ؛ﮒ۱ﮒ ﮒﺁﮔ۶?10%?

**ﮒ؟ﮔﺛﮒﭨﭦﻟ؟؟**:
1. ﻝ،ﮒﺏﻛﺟ؟ﮔﺗﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﮔ?
2. ﮔﺑﮔﺍﮔﮔﻟ۰۷ﻝﮒ­ﮔ؟ﭖﻝﺎﭨﮒﮒ؟?
3. ﻠﮔﺍﻝﮔDDLﻟﮔ؛
4. ﮔﺑﮔﺍﮔﺍﮔ؟ﮒ­ﮒﺕ

---

## 4. ﻝ۰؟ﻟ؟۳?: ﮒﮒﭦﻝ­ﻝ۴ﻟﺁﮒ؟۰

### 4.1 ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒ

**ﮔ ﺕﮒﺟﮒﮒ**: ﮒﮒﭦﻝﺎﮒﭦ۵ﻝﭨﻙﻛﺟﻝﮔﭘﻠﺑﻠﺟﻙﮔ۴ﻟﺁ۱ﮔ۶ﻟﺛ?

| ﮔﺍﮔ؟ﻝﺎﭨﮒ | ﻛﺕﻛﺕﮔ ﮒﮒﮒﭦﻝﺎﮒﭦ۵ | ﻛﺕﻛﺕﮔ ﮒﻛﺟﻝﮔﭘﻠﺑ | ﻝﻝﺎ | ﻟ۰ﻛﺕﮔ۰ﻛﺝ |
|----------|------------------|------------------|------|----------|
| **ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ** | ﮔﮔﮒﮒﭦ | 7-10?| 1. ﻝﻝ؟۰ﻟ۵ﮔﺎ<br>2. ﮒﮒﺎﮒﮔﭖ<br>3. ﮒ؟۰ﻟ؟۰ﻟﺟﺛﮔﭦﺁ | ﻟﺁﻝﻛﺙﻟ۵??|
| **ﮔﻛﭨﮒﮒﺎ** | ﮔﮔﮒﮒﭦ | 5-7?| 1. ﮔﻛﭨﮒﮔ<br>2. ﻠ۲ﻠ۸ﮒﮔﭦﺁ<br>3. ﻛﺕﻝﭨ۸ﮒﺛﮒ  | ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |
| **ﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶** | ﮔﮔﮒﮒﭦ | 5-7?| 1. ﻟﭖﻠﮔﺎﻝﭦﺟ<br>2. ﻠ۲ﻠ۸ﮒﮔ<br>3. ﻛﺕﻝﭨ۸ﻟﺁﻛﺙﺍ | ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |
| **ﻝﺏﭨﻝﭨﮔﮔ ** | ﮔﮒ۷ﮒﮒﭦ | 1-2?| 1. ﮔ۶ﻟﺛﻝﮔ۶<br>2. ﮒ؟ﺗﻠﻟ۶ﮒ<br>3. ﮒﺙﮒﺕﺕﮒﮔ | ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |

### 4.2 ﮒﺛﮒﻟ؟ﺝﻟ؟۰ﻟﺁﮒ؟۰

| ﻟ۰۷ﮒ | ﮒﺛﮒﮒﮒﭦﻝﺎﮒﭦ۵ | ﻛﺕﻛﺕﮔ ﮒ | ﮒﺛﮒﻛﺟﻝﮔﭘﻠﺑ | ﻛﺕﻛﺕﮔ ﮒ | ﻟﺁﮒ؟۰ﻝﭨﮔ |
|------|--------------|----------|--------------|----------|----------|
| **trades** | ﮔﮒ­۲?| ﮔﮔ | 5?| 7-10?| ?ﻛﺕﻟﺝﺝ?|
| **position_history** | ﮔﮒ­۲?| ﮔﮔ | 3?| 5-7?| ?ﻛﺕﻟﺝﺝ?|
| **account_snapshots** | ﮔﮒ­۲?| ﮔﮔ | 3?| 5-7?| ?ﻛﺕﻟﺝﺝ?|
| **system_metrics** | ﮔﮒ­۲?| ﮔﮒ۷ | 1?| 1-2?| ﻗ ﺅﺕ ﻠﻛﺙﮒ |

### 4.3 ﻛﺕﻛﺕﻛﺙﮒﮔﺗﮔ۰

#### ﻛﺙﮒﮔﺗﮔ۰ﺅﺙﮔﮔﮒ?+ ﮒﭨﭘﻠﺟﻛﺟﻝﮔﭘﻠﺑ

```sql
-- ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﻟ۰۷ﺅﺙﮔﮔﮒﮒﭦﺅﺙﻛﺟ?0?
CREATE TABLE trades (
    -- ﮒ­ﮔ؟ﭖﮒ؟ﻛﺗ
) PARTITION BY RANGE (traded_at);

-- ﮒﮒﭨﭦ2026?ﮔﻝﮒﮒﭦ
CREATE TABLE trades_202601 PARTITION OF trades
FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- ﮒﮒﭨﭦ2026?ﮔﻝﮒﮒﭦ
CREATE TABLE trades_202602 PARTITION OF trades
FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- ... ﻛﭨ۴ﮔ­۳ﻝﺎﭨﮔ۷ﺅﺙﮒ?20ﻛﺕ۹ﮔﮒﮒﭦ?0ﮒﺗﺑﺅﺙ

-- ﮔﻛﭨﮒﮒﺎﻟ۰۷ﺅﺙﮔﮔﮒﮒﭦﺅﺙﻛﺟ??
CREATE TABLE position_history (
    -- ﮒ­ﮔ؟ﭖﮒ؟ﻛﺗ
) PARTITION BY RANGE (created_at);

-- ﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶ﻟ۰۷ﺅﺙﮔﮔﮒﮒﭦﺅﺙﻛﺟ??
CREATE TABLE account_snapshots (
    -- ﮒ­ﮔ؟ﭖﮒ؟ﻛﺗ
) PARTITION BY RANGE (snapshot_date);

-- ﻝﺏﭨﻝﭨﮔﮔ ﻟ۰۷ﺅﺙﮔﮒ۷ﮒﮒﭦﺅﺙﻛﺟ??
CREATE TABLE system_metrics (
    -- ﮒ­ﮔ؟ﭖﮒ؟ﻛﺗ
) PARTITION BY RANGE (recorded_at);

-- ﮒﮒﭨﭦ2026ﮒﺗﺑﻝ؛؛1ﮒ۷ﻝﮒﮒﭦ
CREATE TABLE system_metrics_202601 PARTITION OF system_metrics
FOR VALUES FROM ('2026-01-01') TO ('2026-01-08');
```

#### ﮒﮒﭦﻝ؟۰ﻝﻟ۹ﮒ۷ﮒﻟ?

```python
# scripts/manage_partitions.py
import psycopg2
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def create_monthly_partition(table_name, start_date, end_date):
    """ﮒﮒﭨﭦﮔﮒﭦ۵ﮒﮒﭦ"""
    partition_name = f"{table_name}_{start_date.strftime('%Y%m')}"
    
    sql = f"""
    CREATE TABLE {partition_name} PARTITION OF {table_name}
    FOR VALUES FROM ('{start_date.strftime('%Y-%m-%d')}') 
    TO ('{end_date.strftime('%Y-%m-%d')}');
    """
    
    return sql

def create_weekly_partition(table_name, start_date, end_date):
    """ﮒﮒﭨﭦﮒ۷ﮒﭦ۵ﮒﮒﭦ"""
    partition_name = f"{table_name}_{start_date.strftime('%Y%W')}"
    
    sql = f"""
    CREATE TABLE {partition_name} PARTITION OF {table_name}
    FOR VALUES FROM ('{start_date.strftime('%Y-%m-%d')}') 
    TO ('{end_date.strftime('%Y-%m-%d')}');
    """
    
    return sql

def auto_create_partitions(conn, table_name, partition_type='monthly', months_ahead=12):
    """ﻟ۹ﮒ۷ﮒﮒﭨﭦﮔ۹ﮔ۴ﮒﮒﭦ"""
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
            print(f"ﮒﮒﭨﭦﮒﮒﭦﮔﮒ: {sql}")
        except Exception as e:
            print(f"ﮒﮒﭨﭦﮒﮒﭦﮒ۳ﺎﻟﺑ۴: {e}")
    
    conn.commit()
    cursor.close()

# ﻛﺛﺟﻝ۷ﻝ۳ﭦﻛﺝ
conn = psycopg2.connect(
    host='localhost',
    database='zephyr_alpha',
    user='postgres',
    password='password'
)

# ﻟ۹ﮒ۷ﮒﮒﭨﭦﮔ۹ﮔ۴12ﻛﺕ۹ﮔﻝﮒ?
auto_create_partitions(conn, 'trades', 'monthly', 12)
auto_create_partitions(conn, 'position_history', 'monthly', 12)
auto_create_partitions(conn, 'account_snapshots', 'monthly', 12)
auto_create_partitions(conn, 'system_metrics', 'weekly', 52)
```

### 4.4 ﻛﺕﻛﺕﮒﭨﭦﻟ؟؟

**ﮔ۷ﻟﮔﺗﮔ۰**: **ﮔﮔﮒﮒﭦ + ﮒﭨﭘﻠﺟﻛﺟﻝﮔﭘﻠﺑ**

**ﻝﻝﺎ**:
1. **ﻝﻝ؟۰ﮒﻟ۶**: ﻟﺁﻝﻛﺙﻟ۵ﮔﺎﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﻛﺟ??
2. **ﮔ۴ﻟﺁ۱ﮔ۶ﻟﺛ**: ﮔﮔﮒﮒﭦﮔ۴ﻟﺁ۱ﮔ۶ﻟﺛﮔﺑﻛﺙﺅﺙﮒﮒﺍﮔ،ﮔﻟﮒﺑﺅﺙ
3. **ﮒﮒﺎﮒﮔﭖ**: 7-10ﮒﺗﺑﮔﺍﮔ؟ﮔﺁﮔﻠﺟﮔﻝ­ﻝ۴ﮒ?
4. **ﻛﺕﻛﺕﮔ ﮒ**: ﻝ؛۵ﮒﻠ۰ﭘﻝﭦ۶ﻠﮒﮔﭦﮔﮔ ﮒ

**ﮒ؟ﮔﺛﮒﭨﭦﻟ؟؟**:
1. ﻛﺟ؟ﮔﺗﮒﮒﭦﻝ­ﻝ۴ﻛﺕﭦﮔﮔﮒ?
2. ﮒﭨﭘﻠﺟﻛﺟﻝﮔﭘﻠﺑﻟﺏﻛﺕﻛﺕﮔ ?
3. ﮒ؟ﻝﺍﮒﮒﭦﻟ۹ﮒ۷ﻝ؟۰ﻝﻟﮔ؛
4. ﮒﭨﭦﻝ،ﮒﮒﭦﻝﮔ۶ﮒﻟ­۵ﮔﭦﮒﭘ

---

## 5. ﻝ۰؟ﻟ؟۳?: ﻝﺑ۱ﮒﺙﻝ­ﻝ۴ﻟﺁﮒ؟۰

### 5.1 ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒ

**ﮔ ﺕﮒﺟﮒﮒ**: ﻝﺑ۱ﮒﺙﮒﻟﭘﺏﻙﻟ۵ﻝﮔ۴ﻟﺁ۱ﻙﻠﺟﮒﮒ?

| ﻟ۰۷ﻝﺎﭨ?| ﻛﺕﻛﺕﮔ ﮒﻝﺑ۱ﮒﺙ?| ﮔ ﺕﮒﺟﻝﺑ۱ﮒﺙﻝﺎﭨﮒ | ﻝﻝﺎ | ﻟ۰ﻛﺕﮔ۰ﻛﺝ |
|--------|----------------|--------------|------|----------|
| **ﻟﺑ۵ﮔﺓ?* | 6-8ﻛﺕ۹ﻝﺑ۱?| B-tree + ﮒﺁﻛﺕﻝﺑ۱ﮒﺙ | ﮔ۴ﻟﺁ۱ﻠ۱ﻝﺗﻙﮒﺏﻟﮒ۳ | ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |
| **ﮔﻛﭨ?* | 8-10ﻛﺕ۹ﻝﺑ۱?| B-tree + ﮒ۳ﮒﻝﺑ۱ﮒﺙ | ﮔ۴ﻟﺁ۱ﮒ۳ﮔﻙﮒﺏﻟﮒ۳ | ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |
| **ﻟ؟۱ﮒ?* | 10-15ﻛﺕ۹ﻝﺑ۱?| B-tree + ﮒ۳ﮒﻝﺑ۱ﮒﺙ + ﻠ۷ﮒﻝﺑ۱ﮒﺙ | ﮔ۴ﻟﺁ۱ﮔﮒ۳ﮔﻙﻝﭘﮔﮒ۳ | ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |
| **ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛ?* | 8-12ﻛﺕ۹ﻝﺑ۱?| B-tree + ﮒ۳ﮒﻝﺑ۱ﮒﺙ + ﮔﭘﻠﺑﻝﺑ۱ﮒﺙ | ﮔ۴ﻟﺁ۱ﻠ۱ﻝﺗﻙﮔﭘﻠﺑﻟ?| ﻟ۰ﻛﺕﻠﻝ۷ﮔ ﮒ |

### 5.2 ﮒﺛﮒﻟ؟ﺝﻟ؟۰ﻟﺁﮒ؟۰

| ﻟ۰۷ﮒ | ﮒﺛﮒﻝﺑ۱ﮒﺙ?| ﻛﺕﻛﺕﮔ ﮒ | ﮒﺓ؟ﻟﺓ | ﻟﺁﮒ؟۰ﻝﭨﮔ |
|------|------------|----------|------|----------|
| **accounts** | 3?| 6-8?| -3~-5?| ?ﻛﺕﻟﭘﺏ |
| **positions** | 4?| 8-10?| -4~-6?| ?ﻛﺕﻟﭘﺏ |
| **orders** | 7?| 10-15?| -3~-8?| ?ﻛﺕﻟﭘﺏ |
| **trades** | 6?| 8-12?| -2~-6?| ﻗ ﺅﺕ ﻝ۴ﮒﺍ |

### 5.3 ﻛﺕﻛﺕﻛﺙﮒﮔﺗﮔ۰

#### accountsﻟ۰۷ﻝﺑ۱ﮒﺙﻛﺙﮒﺅﺙﮒ۱ﮒ ?ﻛﺕ۹ﻝﺑ۱ﮒﺙﺅﺙ

```sql
-- ﮒﺛﮒﻝﺑ۱ﮒﺙ
CREATE UNIQUE INDEX idx_accounts_code ON accounts(account_code);
CREATE INDEX idx_accounts_status ON accounts(status);
CREATE INDEX idx_accounts_created_at ON accounts(created_at);

-- ﮔﺍﮒ۱ﻝﺑ۱ﮒﺙﺅﺙﻛﺕﻛﺕﮔ ﮒﺅﺙ
CREATE INDEX idx_accounts_type ON accounts(account_type);
CREATE INDEX idx_accounts_broker ON accounts(broker) WHERE broker IS NOT NULL;
CREATE INDEX idx_accounts_total_assets ON accounts(total_assets DESC);
CREATE INDEX idx_accounts_updated_at ON accounts(updated_at);

-- ﮒ۳ﮒﻝﺑ۱ﮒﺙﺅﺙﮔ۴ﻟﺁ۱ﻛﺙﮒﺅﺙ
CREATE INDEX idx_accounts_status_type ON accounts(status, account_type);
```

**ﮔﺍﮒ۱ﻝﺑ۱ﮒﺙﻟﺁﺑﮔ**:
1. `idx_accounts_type`: ﮔﻟﺑ۵ﮔﺓﻝﺎﭨﮒﮔ۴ﻟﺁ۱ﺅﺙsimulation/production?
2. `idx_accounts_broker`: ﮔﮒﺕﮒﮔ۴ﻟﺁ۱ﺅﺙﻠ۷ﮒﻝﺑ۱ﮒﺙﺅﺙﻛﭨﻠﻝ۸ﭦﮒﺙﺅﺙ
3. `idx_accounts_total_assets`: ﮔﮔﭨﻟﭖﻛﭦ۶ﮔﮒﭦﺅﺙﻠﮒﭦﺅﺙﮔﺁﮔTOP Nﮔ۴ﻟﺁ۱?
4. `idx_accounts_updated_at`: ﮔﮔﺑﮔﺍﮔﭘﻠﺑﮔ۴ﻟﺁ۱ﺅﺙﮔﺁﮔﮒ۱ﻠﮒﮔ­۴?
5. `idx_accounts_status_type`: ﮒ۳ﮒﻝﺑ۱ﮒﺙﺅﺙﻝﭘ?ﻝﺎﭨﮒﺅﺙﮔﺁﮔﻝﭨﮒﮔ۴ﻟﺁ۱ﺅﺙ

---

#### positionsﻟ۰۷ﻝﺑ۱ﮒﺙﻛﺙﮒﺅﺙﮒ۱ﮒ ?ﻛﺕ۹ﻝﺑ۱ﮒﺙﺅﺙ

```sql
-- ﮒﺛﮒﻝﺑ۱ﮒﺙ
CREATE INDEX idx_positions_account_id ON positions(account_id);
CREATE INDEX idx_positions_stock_code ON positions(stock_code);
CREATE UNIQUE INDEX idx_positions_unique ON positions(account_id, stock_code);
CREATE INDEX idx_positions_updated_at ON positions(updated_at);

-- ﮔﺍﮒ۱ﻝﺑ۱ﮒﺙﺅﺙﻛﺕﻛﺕﮔ ﮒﺅﺙ
CREATE INDEX idx_positions_exchange ON positions(exchange);
CREATE INDEX idx_positions_quantity ON positions(quantity DESC) WHERE quantity > 0;
CREATE INDEX idx_positions_market_value ON positions(market_value DESC);
CREATE INDEX idx_positions_unrealized_pnl ON positions(unrealized_pnl DESC);
CREATE INDEX idx_positions_last_trade_date ON positions(last_trade_date DESC);

-- ﮒ۳ﮒﻝﺑ۱ﮒﺙﺅﺙﮔ۴ﻟﺁ۱ﻛﺙﮒﺅﺙ
CREATE INDEX idx_positions_account_stock ON positions(account_id, stock_code, quantity);
```

**ﮔﺍﮒ۱ﻝﺑ۱ﮒﺙﻟﺁﺑﮔ**:
1. `idx_positions_exchange`: ﮔﻛﭦ۳ﮔﮔﮔ۴ﻟﺁ۱ﺅﺙSH/SZ?
2. `idx_positions_quantity`: ﮔﮔﻛﭨﮔﺍﻠﮔ۴ﻟﺁ۱ﺅﺙﻠ۷ﮒﻝﺑ۱ﮒﺙﺅﺙﻛﭨﮔﻛﭨ>0?
3. `idx_positions_market_value`: ﮔﮒﺕﮒﺙﮔﮒﭦﺅﺙﻠﮒﭦﺅﺙﮔﺁﮔTOP Nﮔ۴ﻟﺁ۱?
4. `idx_positions_unrealized_pnl`: ﮔﮔﭖ؟ﮒ۷ﻝﻛﭦﮔﮒﭦﺅﺙﻠﮒﭦﺅﺙﮔﺁﮔﻝﻛﭦﮒﮔﺅﺙ
5. `idx_positions_last_trade_date`: ﮔﮔﮒﻛﭦ۳ﮔﮔ۴ﮔﮔﮒﭦﺅﺙﮔﺁﮔﮔﺑﭨﻟﺓﮔﻛﭨﮔ۴ﻟﺁ۱?
6. `idx_positions_account_stock`: ﮒ۳ﮒﻝﺑ۱ﮒﺙﺅﺙﻟﺑ۵?ﻟ۰ﻝ۴۷+ﮔﺍﻠﺅﺙﮔﺁﮔﮒﺟ،ﻠﮔ۴ﻟﺁ۱ﺅﺙ

---

#### ordersﻟ۰۷ﻝﺑ۱ﮒﺙﻛﺙﮒﺅﺙﮒ۱ﮒ ?2ﻛﺕ۹ﻝﺑ۱ﮒﺙﺅﺙ

```sql
-- ﮒﺛﮒﻝﺑ۱ﮒﺙ
CREATE UNIQUE INDEX idx_orders_code ON orders(order_code);
CREATE INDEX idx_orders_account_id ON orders(account_id);
CREATE INDEX idx_orders_signal_id ON orders(signal_id);
CREATE INDEX idx_orders_stock_code ON orders(stock_code);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_engine_id ON orders(engine_id);

-- ﮔﺍﮒ۱ﻝﺑ۱ﮒﺙﺅﺙﻛﺕﻛﺕﮔ ﮒﺅﺙ
CREATE INDEX idx_orders_direction ON orders(direction);
CREATE INDEX idx_orders_order_type ON orders(order_type);
CREATE INDEX idx_orders_filled_at ON orders(filled_at) WHERE filled_at IS NOT NULL;
CREATE INDEX idx_orders_status_created ON orders(status, created_at DESC);
CREATE INDEX idx_orders_account_status ON orders(account_id, status, created_at DESC);

-- ﻠ۷ﮒﻝﺑ۱ﮒﺙﺅﺙﮔﺑﭨﻟﺓﻟ؟۱ﮒﺅﺙ
CREATE INDEX idx_orders_active ON orders(account_id, stock_code, created_at DESC)
WHERE status IN ('pending', 'submitted', 'partial_filled');
```

**ﮔﺍﮒ۱ﻝﺑ۱ﮒﺙﻟﺁﺑﮔ**:
1. `idx_orders_direction`: ﮔﻛﭦ۳ﮔﮔﺗﮒﮔ۴ﻟﺁ۱ﺅﺙbuy/sell?
2. `idx_orders_order_type`: ﮔﻟ؟۱ﮒﻝﺎﭨﮒﮔ۴ﻟﺁ۱ﺅﺙmarket/limit?
3. `idx_orders_filled_at`: ﮔﮔﻛﭦ۳ﮔﭘﻠﺑﮔ۴ﻟﺁ۱ﺅﺙﻠ۷ﮒﻝﺑ۱ﮒﺙﺅﺙﻛﭨﮒﺓﺎﮔﻛﭦ۳ﻟ؟۱ﮒﺅﺙ
4. `idx_orders_status_created`: ﮒ۳ﮒﻝﺑ۱ﮒﺙﺅﺙﻝﭘ?ﮒﮒﭨﭦﮔﭘﻠﺑﺅﺙﮔﺁﮔﻝﭘﮔﮔ۴ﻟﺁ۱ﺅﺙ
5. `idx_orders_account_status`: ﮒ۳ﮒﻝﺑ۱ﮒﺙﺅﺙﻟﺑ۵?ﻝ?ﮔﭘﻠﺑﺅﺙﮔﺁﮔﻟﺑ۵ﮔﺓﻟ؟۱ﮒﮔ۴ﻟﺁ۱ﺅﺙ
6. `idx_orders_active`: ﻠ۷ﮒﻝﺑ۱ﮒﺙﺅﺙﮔﺑﭨﻟﺓﻟ؟۱ﮒﺅﺙﻛﺙﮒﮔ۴ﻟﺁ۱ﮔ۶ﻟﺛ?

---

#### tradesﻟ۰۷ﻝﺑ۱ﮒﺙﻛﺙﮒﺅﺙﮒ۱ﮒ ?0ﻛﺕ۹ﻝﺑ۱ﮒﺙﺅﺙ

```sql
-- ﮒﺛﮒﻝﺑ۱ﮒﺙ
CREATE UNIQUE INDEX idx_trades_code ON trades(trade_code);
CREATE INDEX idx_trades_order_id ON trades(order_id);
CREATE INDEX idx_trades_account_id ON trades(account_id);
CREATE INDEX idx_trades_stock_code ON trades(stock_code);
CREATE INDEX idx_trades_traded_at ON trades(traded_at);
CREATE INDEX idx_trades_engine_id ON trades(engine_id);

-- ﮔﺍﮒ۱ﻝﺑ۱ﮒﺙﺅﺙﻛﺕﻛﺕﮔ ﮒﺅﺙ
CREATE INDEX idx_trades_direction ON trades(direction);
CREATE INDEX idx_trades_account_traded ON trades(account_id, traded_at DESC);
CREATE INDEX idx_trades_stock_traded ON trades(stock_code, traded_at DESC);
CREATE INDEX idx_trades_amount ON trades(trade_amount DESC);
```

**ﮔﺍﮒ۱ﻝﺑ۱ﮒﺙﻟﺁﺑﮔ**:
1. `idx_trades_direction`: ﮔﻛﭦ۳ﮔﮔﺗﮒﮔ۴ﻟﺁ۱ﺅﺙbuy/sell?
2. `idx_trades_account_traded`: ﮒ۳ﮒﻝﺑ۱ﮒﺙﺅﺙﻟﺑ۵?ﮔﭘﻠﺑﺅﺙﮔﺁﮔﻟﺑ۵ﮔﺓﻛﭦ۳ﮔﮒﮒﺎﮔ۴ﻟﺁ۱ﺅﺙ
3. `idx_trades_stock_traded`: ﮒ۳ﮒﻝﺑ۱ﮒﺙﺅﺙﻟ۰?ﮔﭘﻠﺑﺅﺙﮔﺁﮔﻟ۰ﻝ۴۷ﻛﭦ۳ﮔﮒﮒﺎﮔ۴ﻟﺁ۱ﺅﺙ
4. `idx_trades_amount`: ﮔﻛﭦ۳ﮔﻠﻠ۱ﮔﮒﭦﺅﺙﻠﮒﭦﺅﺙﮔﺁﮔﮒ۳۶ﻠ۱ﻛﭦ۳ﮔﮔ۴ﻟﺁ۱ﺅﺙ

---

### 5.4 ﻛﺕﻛﺕﮒﭨﭦﻟ؟؟

**ﮔ۷ﻟﮔﺗﮔ۰**: **ﮒ۱ﮒ ﻝﺑ۱ﮒﺙﻟﺏﻛﺕﻛﺕﮔ ?*

**ﻝﻝﺎ**:
1. **ﮔ۴ﻟﺁ۱ﮔ۶ﻟﺛ**: ﻝﺑ۱ﮒﺙﮒﻟﭘﺏﮒﺁﮔﺝﻟﮔﮒﮔ۴ﻟﺁ۱ﮔ۶ﻟﺛ?-10ﮒﺅﺙ
2. **ﻟ۵ﻝﮔ۴ﻟﺁ۱**: ﮒ۳ﮒﻝﺑ۱ﮒﺙﮒﺁﻟ۵ﻝﮒ۳۶ﻠ۷ﮒﮔ۴ﻟﺁ۱ﮒﭦﮔﺁ
3. **ﻠ۷ﮒﻝﺑ۱ﮒﺙ**: ﮒﮒﺍﻝﺑ۱ﮒﺙﮒ۳۶ﮒﺍﺅﺙﮔﮒﮔ۶ﻟﺛ
4. **ﻛﺕﻛﺕﮔ ﮒ**: ﻝ؛۵ﮒﻠ۰ﭘﻝﭦ۶ﻠﮒﮔﭦﮔﮔ ﮒ

**ﮒ؟ﮔﺛﮒﭨﭦﻟ؟؟**:
1. ﮒ۱ﮒ ﻝﺑ۱ﮒﺙﻟﺏﻛﺕﻛﺕﮔ ﮒﺅﺙaccounts: 7? positions: 9? orders: 12? trades: 10ﻛﺕ۹ﺅﺙ
2. ﮒﮒﭨﭦﮒ۳ﮒﻝﺑ۱ﮒﺙﻟ۵ﻝﻠ،ﻠ۱ﮔ۴ﻟﺁ۱
3. ﻛﺛﺟﻝ۷ﻠ۷ﮒﻝﺑ۱ﮒﺙﻛﺙﮒﮔ۶ﻟﺛ
4. ﮒﭨﭦﻝ،ﻝﺑ۱ﮒﺙﻝﮔ۶ﮔﭦﮒﭘﺅﺙﮒ؟ﮔﮒﮔﻝﺑ۱ﮒﺙﻛﺛﺟﻝ۷ﻝ?

---

## 6. ﻝﭨﺙﮒﻛﺙﮒﮔﺗﮔ۰

### 6.1 ﻛﺙﮒﻛﺙﮒ?

| ﻛﺙﮒ?| ﻠ۲ﻠ۸ﻝ­ﻝﭦ۶ | ﻛﺙﮒﻠﺝﮒﭦ۵ | ﻛﺙﮒ?| ﻠ۱ﻟ؟۰ﮒﺓ۴ﮔﭘ |
|--------|----------|----------|--------|----------|
| **ﮔﺍﮔ؟ﻝﺎﭨﮒﻛﺙﮒ** | ﻭﺑ ﻠ،ﻠ۲?| ?| P0 | 0.5?|
| **ﮒﮒﭦﻝ­ﻝ۴ﻛﺙﮒ** | ﻭﺑ ﻠ،ﻠ۲?| ?| P0 | 1?|
| **ﻝﺑ۱ﮒﺙﻝ­ﻝ۴ﻛﺙﮒ** | ﻭ۰ ﻛﺕ­ﻠ۲?| ?| P1 | 0.5?|
| **ﻟ۰۷ﻝﭨﮔﻛﺙ?* | ﻭ۱ ﻛﺛﻠ۲?| ?| P2 | 0.5?|

### 6.2 ﻛﺙﮒﮒ؟ﮔﺛﻟ؟۰ﮒ

#### ﻝ؛؛ﻛﺕﮔ­۴ﺅﺙﮔﺍﮔ؟ﻝﺎﭨﮒﻛﺙﮒ?.5ﮒ۳۸ﺅﺙ

```sql
-- ﮔ۶ﻟ۰ﮔﺍﮔ؟ﻝﺎﭨﮒﻛﺙﮒﻟﮔ؛
-- ﻟﺁ۵ﻟ۶?.3ﻟﮔﺗﮔ۰A
```

#### ﻝ؛؛ﻛﭦﮔ­۴ﺅﺙﮒﮒﭦﻝ­ﻝ۴ﻛﺙﮒ?ﮒ۳۸ﺅﺙ

```sql
-- ﻠﮔﺍﮒﮒﭨﭦﮒﮒﭦ?
-- ﻟﺁ۵ﻟ۶?.3ﻟﻛﺙﮒﮔﺗ?
```

#### ﻝ؛؛ﻛﺕﮔ­۴ﺅﺙﻝﺑ۱ﮒﺙﻝ­ﻝ۴ﻛﺙﮒ?.5ﮒ۳۸ﺅﺙ

```sql
-- ﮒﮒﭨﭦﮔﺍﮒ۱ﻝﺑ۱ﮒﺙ
-- ﻟﺁ۵ﻟ۶?.3ﻟﻛﺙﮒﮔﺗ?
```

#### ﻝ؛؛ﮒﮔ­۴ﺅﺙﻟ۰۷ﻝﭨﮔﻛﺙﮒﺅﺙ0.5ﮒ۳۸ﺅﺙ

```sql
-- ﮒ ﻠ۳ﮒﻛﺛﮒ­ﮔ؟ﭖ
ALTER TABLE accounts DROP COLUMN total_market_value;
ALTER TABLE accounts DROP COLUMN daily_pnl;
```

### 6.3 ﻛﺙﮒﮒﻝ؛۵ﮒﮒﭦ۵ﻟﺁﻛﺙﺍ

| ﻟ؟ﺝﻟ؟۰ﻝﭨﺑﮒﭦ۵ | ﻛﺙﮒﮒﻝ؛۵ﮒﮒﭦ۵ | ﻛﺙﮒﮒﻝ؛۵ﮒﮒﭦ۵ | ﮔﮒﮒﺗﮒﭦ۵ | ﻟﺝﺝﮔ ﻝ?|
|----------|--------------|--------------|----------|----------|
| **ﻟ۰۷ﻝﭨﮔﻟ؟ﺝ?* | 85% | 95% | +10% | ?ﻟﺝﺝﮔ  |
| **ﮔﺍﮔ؟ﻝﺎﭨﮒﻠﮔ۸** | 70% | 100% | +30% | ?ﻟﺝﺝﮔ  |
| **ﮒﮒﭦﻝ­ﻝ۴** | 60% | 95% | +35% | ?ﻟﺝﺝﮔ  |
| **ﻝﺑ۱ﮒﺙﻝ­ﻝ۴** | 80% | 95% | +15% | ?ﻟﺝﺝﮔ  |
| **ﮔﺑﻛﺛﻝ؛۵ﮒ?* | 75% | **96%** | +21% | ?**ﻟﺝﺝﮔ ** |

---

## 7. ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﻛﺛﺏﮒ؟?

### 7.1 ﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﮒ?

1. **ﻝﺎﺝﮒﭦ۵ﻛﺙﮒ**: ﮒ؟ﮒﺁﻟﺟﮒﭦ۵ﻝﺎﺝﻝ۰؟ﺅﺙﻛﺕﮒﺁﻝﺎﺝﮒﭦ۵ﻛﺕ?
2. **ﮒﮒﭦﻝﭨﮒ**: ﮔﮔﮒﮒﭦﺅﺙﮔ۴ﻟﺁ۱ﮔ۶ﻟﺛﮔ?
3. **ﻝﺑ۱ﮒﺙﮒﻟﭘﺏ**: ﻟ۵ﻝﮔ۴ﻟﺁ۱ﺅﺙﻠﺟﮒﮒ۷ﻟ۰۷ﮔ،?
4. **ﻛﺟﻝﮒﭨﭘﻠﺟ**: ﮔﭨ۰ﻟﭘﺏﻝﻝ؟۰ﻟ۵ﮔﺎﺅﺙﮔﺁﮔﮒﮒﺎﮒ?

### 7.2 ﻟ۰ﻛﺕﮔ۰ﻛﺝﮒ?

| ﮔﭦﮔﮒﻝ۶ﺍ | ﻝ؟۰ﻝﻟ۶ﮔ۷۰ | ﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﻝﺗ?| ﮒﺁﮒﻠﺑ?|
|----------|----------|----------------|----------|
| **ﮒﺗﭨﮔﺗﻠﮒ** | 600? | DECIMAL(20,4)ﻙﮔﮔﮒﮒﭦﻙﻝﺑ۱ﮒﺙﮒ?| ﻝﺎﺝﮒﭦ۵ﮔ ﮒﻙﮒﮒﭦﻝ­?|
| **ﻛﺗﮒ۳ﮔﻟﭖ** | 500? | ﻠ،ﻝﺎﺝﮒﭦ۵ﻟ؟۰ﻝ؟ﻙﮒ؟ﮔﭘﻝﮔ۶ﻙﮒﮒﺎﻟﺟﺛ?| ﮔﺍﮔ؟ﻝﺎﭨﮒﻙﻝﮔ۶ﻟ؟ﺝ?|
| **ﮔﮔﺎﺁﮔﻟﭖ** | 400? | ﮒ۳ﮒﻝﺑ۱ﮒﺙﻙﻠ۷ﮒﻝﺑ۱ﮒﺙﻙﮔ۴ﻟﺁ۱ﻛﺙ?| ﻝﺑ۱ﮒﺙﻝ­ﻝ۴ |
| **ﻟ۰ﮒ۳ﮔﻟﭖ** | 300? | ﮒﮒﭦﻟ۹ﮒ۷ﮒﻙﮔﺍﮔ؟ﻝﮒﺛﮒ۷ﮔﻝ؟۰?| ﮒﮒﭦﻝ؟۰ﻝﻙﮔﺍﮔ؟ﮔﺎﭨ?|

### 7.3 ﻝﻝ؟۰ﮒﻟ۶ﻟ۵ﮔﺎ

| ﻝﻝ؟۰ﻟ۵ﮔﺎ | ﮒﺓﻛﺛﻟ۶ﮒ؟ | ﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﻟ۵?| ﮒﺛﮒﻟ؟ﺝﻟ؟۰ﻝ؛۵ﮒ?|
|----------|----------|----------------|----------------|
| **ﻟﺁﻝ?* | ﻛﭦ۳ﮔﻟ؟ﺍﮒﺛﻛﺟﻝ7?| tradesﻟ۰۷ﻛﺟ??| ?ﻝ؛۵ﮒﺅﺙﻛﺙﮒﮒ?|
| **ﻛﺕ­ﮒﭦ?* | ﻛﭦ۳ﮔﮔ۴ﮒﺟﮒ؟ﮔﺑﻛﺟﻝ | ﮔ۴ﮒﺟﻟ۰۷ﻟ؟ﺝﻟ؟۰ﮒ؟?| ?ﻝ؛۵ﮒ |
| **ﻛﭦ۳ﮔﮔ** | ﻛﭦ۳ﮔﮔﺍﮔ؟ﮒﺁﻟﺟﺛ?| ﮒ؟۰ﻟ؟۰ﮒ­ﮔ؟ﭖﮒ؟ﮔﺑ | ?ﻝ؛۵ﮒ |

---

## 8. ﻟﺁﮒ؟۰ﻝﭨﻟ؟ﭦﻛﺕﮒﭨﭦ?

### 8.1 ﻟﺁﮒ؟۰ﻝﭨﻟ؟ﭦ

**ﮒﺛﮒﻟ؟ﺝﻟ؟۰ﻝ؛۵ﮒ?*: 75%ﺅﺙﻛﺕﻟﺝﺝﮔ ?

**ﻛﺙﮒﮒﻝ؛۵ﮒﮒﭦ۵**: 96%ﺅﺙﻟﺝﺝﮔ ﺅﺙ

**ﻟﺁﮒ؟۰ﻝﭨﻟ؟ﭦ**: **ﮔﮔ۰ﻛﭨﭘﮔﺗ?*

**ﮔﺗﮒﮔ۰ﻛﭨﭘ**:
1. ﮒﺟﻠ۰ﭨﻛﺙﮒﮔﺍﮔ؟ﻝﺎﭨﮒﺅﺙP0ﺅﺙﻠ،ﻠ۲ﻠ۸?
2. ﮒﺟﻠ۰ﭨﻛﺙﮒﮒﮒﭦﻝ­ﻝ۴ﺅﺙP0ﺅﺙﻠ،ﻠ۲ﻠ۸?
3. ﮒﭨﭦﻟ؟؟ﻛﺙﮒﻝﺑ۱ﮒﺙﻝ­ﻝ۴ﺅﺙP1ﺅﺙﻛﺕ­ﻠ۲ﻠ۸?
4. ﮒﭨﭦﻟ؟؟ﻛﺙﮒﻟ۰۷ﻝﭨﮔﺅﺙP2ﺅﺙﻛﺛﻠ۲ﻠ۸?

### 8.2 ﻛﺕﻛﺕﮔ­۴ﻟ۰?

**ﻝ،ﮒﺏﻟ۰ﮒ۷**?026-04-02?
1. ﮔ۶ﻟ۰ﮔﺍﮔ؟ﻝﺎﭨﮒﻛﺙﮒ?.5ﮒ۳۸ﺅﺙ
2. ﮔ۶ﻟ۰ﮒﮒﭦﻝ­ﻝ۴ﻛﺙﮒ?ﮒ۳۸ﺅﺙ
3. ﮔ۶ﻟ۰ﻝﺑ۱ﮒﺙﻝ­ﻝ۴ﻛﺙﮒ?.5ﮒ۳۸ﺅﺙ
4. ﮔ۶ﻟ۰ﻟ۰۷ﻝﭨﮔﻛﺙﮒﺅﺙ0.5ﮒ۳۸ﺅﺙ

**ﻛﺙﮒﮒ؟ﮔ?*:
1. ﮔﺑﮔﺍﮔﺍﮔ؟ﮒﭦﻟ؟ﺝﻟ؟۰ﮔ?
2. ﻝﮔﻛﺙﮒﮒﻝDDLﻟﮔ؛
3. ﮒﺙﮒ۶P0-2ﮔﺍﮔ؟ﮒ­ﮒﺕﻟ؟ﺝﻟ؟۰

---

**ﻝﮔ؛**: 1.0.0 | **ﮔﺑﮔﺍﮔ۴ﮔ**: 2026-04-02 | **ﻝ?*: ?ﮒﺓﺎﻟﺁ? 
**ﻟﺁﮒ؟۰ﻝﭨﻟ؟ﭦ**: ﮔﮔ۰ﻛﭨﭘﮔﺗ? 
**ﻝ؛۵ﮒ?*: ﻛﺙﮒ?5% ?ﻛﺙﮒ?6%  
**ﻛﺕﻛﺕ?*: ﮔ۶ﻟ۰ﻛﺙﮒﮔﺗﮔ۰ ?ﮔﺑﮔﺍﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲ ?ﮒﺙﮒ۶P0-2ﮔﺍﮔ؟ﮒ­ﮒﺕﻟ؟ﺝﻟ؟۰