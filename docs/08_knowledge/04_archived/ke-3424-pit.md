---
module_id: KE-3297
title: 4.2 PIT 违反的三种典型场景与防御
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 4.2 PIT 违反的三种典型场景与防御

4.2 PIT 违反的三种典型场景与防御

| 场景 | 例子 | 防御 |
|------|------|------|
| **Look-ahead bias / 前视偏差** | 用今天收盘价做今天开盘的决策 | factor 必须显式声明 `asof_offset`（如"昨日收盘后可知"） + fitness function `test_no_lookahead_bias.py` 在 CI 强制扫描 |
| **Restated data / 财报修订** | Q1 财报 4/30 公布，6/15 修订；回测 5/15 用了 6/15 修订版 | 财务实体存 bitemporal，查询走 `vendor_release_ts ≤ T` |
| **Index rebalance / 指数成分调整** | 沪深 300 半年调整，回测 2024 年 Q1 不能用 Q3 后调进的成分股 | `IndexConstituent` 必须 bitemporal；查询用 PIT API |
