---
module_id: MOD-RPT-027
title: "A股交易记录模板引擎蓝图 — 11必填字段模板+强制校验+模板版本管理"
doc_type: blueprint
status: Active
version: "0.1.0"
ttl: permanent
layer: L07_reporting
layer_name: reporting
functional_domain: reporting
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P2
blueprint_level: module
responsibility_domain: 
design_maturity: design
build_status: planned
---

# MOD-RPT-027 A股交易记录模板引擎 — A股交易记录模板引擎 蓝图

> **module_id**: MOD-RPT-027 | **域**: D_REPORTING | **层**: L07 报告
> **优先级**: P2 | **成熟度**: production | **对标能力**: C-010(报告归档/审计)
> **SSoT**: depgraph MOD-RPT-027 | **设计真源**: D:\临时工作区\依赖图\10-D-REPORTING-报告域.md §1.3 D-REPORTING-27

## 1. 定位

A股交易记录模板引擎——为 A 股交易记录提供标准化模板:
- **11 必填字段**: 证监会交易记录留存要求的 11 个必填字段
- **强制校验**: 字段类型/格式/业务规则强制校验（缺字段/类型错/值非法拒绝）
- **模板版本管理**: 模板 schema_version 管理, 支持未来字段扩展

属 A 类基础设施(确定性模板校验), 纯消费层不发布事件。

## 2. 11 必填字段

| # | 字段 | 类型 | 校验规则 | 监管依据 |
|---|------|------|---------|---------|
| 1 | trade_date | str | YYYY-MM-DD 格式 | 证监会交易记录留存 |
| 2 | symbol | str | 6位数字代码 | 证券代码规范 |
| 3 | side | str | BUY/SELL | 交易方向 |
| 4 | quantity | Decimal | >0, 100股起(整数倍100) | A股最小交易单位 |
| 5 | price | Decimal | >0, 精度0.01 | 最小变动价位 |
| 6 | amount | Decimal | = quantity × price | 成交金额 |
| 7 | commission | Decimal | ≥0 | 佣金 |
| 8 | stamp_duty | Decimal | ≥0, SELL时>0 | 印花税(卖出) |
| 9 | transfer_fee | Decimal | ≥0 | 过户费 |
| 10 | strategy_id | str | 非空 | 策略标识 |
| 11 | account_id | str | 非空 | 账户标识 |

## 3. 核心规则

### 3.1 字段校验

- 缺必填字段 → InvalidTradeRecordError
- 类型不匹配 → InvalidTradeRecordError
- 值非法(负数/空串/格式错) → InvalidTradeRecordError
- amount ≠ quantity × price → InvalidTradeRecordError (一致性校验)
- stamp_duty > 0 且 side == BUY → InvalidTradeRecordError (买入无印花税)

### 3.2 模板版本管理

- 当前 schema_version = "1.0"
- get_required_fields() 返回字段定义列表
- validate(entry_dict) → TradeRecordEntry (frozen)

## 4. 数据模型

```python
@dataclass(frozen=True)
class TradeRecordEntry:
    trade_date: str
    symbol: str
    side: str          # BUY / SELL
    quantity: Decimal
    price: Decimal
    amount: Decimal
    commission: Decimal
    stamp_duty: Decimal
    transfer_fee: Decimal
    strategy_id: str
    account_id: str
    schema_version: str = "1.0"
```

## 5. API

```python
class AShareTradeRecordTemplate:
    def get_required_fields(self) -> list[str]: ...
    def validate(self, entry: dict) -> TradeRecordEntry: ...
    def get_template_version(self) -> str: ...
```

## 6. 依赖

| 依赖 | 类型 | 就绪 |
|------|------|------|
| errors foundation | import_depends | ✓ production |

## 7. 测试计划

- 11字段完整校验: 每字段缺/类型错/值非法
- amount一致性: amount ≠ qty×price 拒绝
- 印花税规则: BUY时stamp_duty>0拒绝
- quantity规则: 非100整数倍拒绝
- 模板版本: get_required_fields/get_template_version
- frozen不可变
