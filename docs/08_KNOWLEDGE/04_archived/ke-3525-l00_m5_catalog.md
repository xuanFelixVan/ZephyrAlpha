---
module_id: KE-3389-----l00-m5--catalog-000
title: 7.3 与旧体系 L00-M5 `catalog/` 的关系
category: documentation
ttl: permanent
---

# 7.3 与旧体系 L00-M5 `catalog/` 的关系

7.3 与旧体系 L00-M5 `catalog/` 的关系

旧体系 `construction-plan-l00-data-source.md` 中的 L00-M5 `catalog`（标的、交易所日历、数据源版本与血缘登记）就是 MDM 在代码层的物化点。本视图与旧体系设计**完全兼容**，新增的是"必须 bitemporal"+"必须经 OpenLineage 注册血缘"两条强约束。

---
