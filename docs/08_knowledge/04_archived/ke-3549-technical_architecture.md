---
module_id: KE-3409-----------------04-ta-000
title: 8.3 业界工具映射（建议，最终选型归 04-TA）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 8.3 业界工具映射（建议，最终选型归 04-TA）

8.3 业界工具映射（建议，最终选型归 04-TA）

| 业界工具 | 本项目用途 |
|---------|----------|
| **Great Expectations** | 适合 batch 断言（EOD bar / 因子值） |
| **Soda Core** | 适合 SQL-first 团队，与 dbt 集成好 |
| **自研 fitness functions** | PIT / Survivorship / Lineage 这三类**业界工具不覆盖**的量化专属断言，必须自研（呼应 OQ-032 Build vs Buy 五大铁律之一） |
