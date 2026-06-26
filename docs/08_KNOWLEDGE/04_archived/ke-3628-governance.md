---
module_id: KE-3483
title: 11. 审查周期
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 11. 审查周期

11. 审查周期

对标 ISO 11179 §6.2 定期审查要求：

| 触发条件 | 审查内容 |
|---------|---------|
| 新增登记表（registry-master-index.yaml 增加条目） | MRS-001 矩阵是否需要新增列 |
| 新增工件类型（项目中出现新的可创建实体） | MRS-001 矩阵是否需要新增行 |
| Phase 边界（scaffold→1, 1→2...） | 操作矩阵是否仍覆盖当前操作类型 |
| check_registry_consistency.py 重大修改 | MRS-003 校验步骤描述是否准确 |
| 最低频率：每 6 个月 | 全量审查 |

---
