---
module_id: KE-3627
title: 8. 修改条件
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 8. 修改条件

8. 修改条件

本标准 `ai_autonomy: ai_modifiable`——AI 可自主修改，但受以下分级约束：

| 级别 | 变更范围 | 审批方 | 要求 |
|:---:|---------|--------|------|
| L0 | 错别字、措辞优化、格式调整 | AI 自批 | Session Log 记录 |
| L1 | MRS-001 矩阵中新增/删除操作行 | AI 可建议，Owner 确认 | 需对照 registry-master-index.yaml 验证新增登记表已注册 |
| L2 | 修改 MRS-002~005 规则本体 | Owner 审批 | 涉及操作纪律——需 Owner 确认新规则可落地 |
| L3 | 新增登记表到 MRS-001 矩阵 / 新增工件类型 | Owner 审批 | 必须同时更新 registry-master-index.yaml + registry_of_registries.yaml |

---
