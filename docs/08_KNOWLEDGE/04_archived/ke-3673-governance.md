---
module_id: KE-3528
title: 2.2 状态迁移与门控映射
category: governance_rule
ttl: permanent
doc_type: knowledge_entry
---

# 2.2 状态迁移与门控映射

2.2 状态迁移与门控映射

| 迁移 | 触发条件 | 变更级别 | 审批要求 | 前置检查 |
|------|---------|:---:|---------|---------|
| draft → active | Owner 批准 | P2 | Owner 签收 | PS-STD-001 §2.5 必填字段齐全 |
| active → deprecated | 新版本/合并/删除 | P1 | Owner 批准 | `superseded_by` 已填；依赖方已迁移 |
| draft → draft（返工） | 审批不通过 | — | — | 返工原因已记录 |

---
