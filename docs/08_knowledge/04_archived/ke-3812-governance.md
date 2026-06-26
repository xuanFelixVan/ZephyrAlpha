---
module_id: KE-3661
title: ARG-005：评审记录格式
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# ARG-005：评审记录格式

ARG-005：评审记录格式

| 条件 | 规则 | 违反后果 |
|------|------|---------|
| 所有架构评审 | 评审记录必须包含：评审日期（ISO 8601 UTC）、评审人 ID、变更描述、§4 清单逐项检查结果、否决/通过决定、决定理由。存放于 `docs/_working/audit/architecture-reviews/YYYY-MM-DD-变更简述.md` | 评审不可追溯；变更不得合并 |

---
