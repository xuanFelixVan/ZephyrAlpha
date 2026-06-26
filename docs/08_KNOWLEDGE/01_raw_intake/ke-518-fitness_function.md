---
module_id: KE-467-----fitness-function-000
status: active
title: 6.4 血缘的 fitness function
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 6.4 血缘的 fitness function

6.4 血缘的 fitness function

`scripts/fitness_functions/test_lineage_completeness.py`（规划中）应保证：
- 任何派生实体（FactorValue / Signal / PnL / RiskMetric）创建时必填 `lineage_root`
- 任何 lineage_root 必须能解析出至少一条上游边
- 任何代码层 commit 不允许引入"无血缘的派生实体"

---
