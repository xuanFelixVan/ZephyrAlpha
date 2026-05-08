---
module_id: KE-documentat-5_1-002
title: 5.1 三类需要处理的"消失/变化"
category: documentation
---

# 5.1 三类需要处理的"消失/变化"

5.1 三类需要处理的"消失/变化"

| 类型 | 例子 | DA 处理 |
|------|------|---------|
| **退市 / Delisting** | 长航油运退市、瑞幸 ADR 退市 | `Security.delisting_date` + `status='delisted'`，查询时按 PIT 包含 |
| **合并 / Merger** | 中国南车 + 中国北车 → 中国中车 | 旧 symbol 在 `delisting_date` 后映射到新 symbol，保留 mapping 表 |
| **指数成分调整** | 沪深 300 季度调仓 | `IndexConstituent` bitemporal，PIT 查询返回当时成分 |
