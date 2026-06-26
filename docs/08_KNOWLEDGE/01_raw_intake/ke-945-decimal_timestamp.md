---
module_id: KE-867-----timestamp-----002
status: active
title: 3.4 `Decimal` / `Timestamp` / `Money` 强制
category: governance
ttl: permanent
---

# 3.4 `Decimal` / `Timestamp` / `Money` 强制

3.4 `Decimal` / `Timestamp` / `Money` 强制

- 金额、价格、数量 → `Decimal`（禁止 `float`）
- 时间戳 → `Timestamp`（纳秒 UTC，禁止裸 `datetime`）
- 货币运算 → `Money` 类型

以上三条对齐 AGENTS.md §四 和 cross_layer_contracts.yaml CTR-000 契约。

---
