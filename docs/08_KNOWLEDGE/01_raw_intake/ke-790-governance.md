---
module_id: KE-713
status: active
title: 10. 废弃流程
category: governance
---

# 10. 废弃流程

10. 废弃流程

若本标准被更高层级的治理文件取代：

1. **搜索影响**：全项目搜索 `MRS-001|MRS-002|MRS-003|MRS-004`——确认所有引用都有迁移路径
2. **通知期**：30 天提前通知全部消费者（Session Log + ADR）
3. **废弃标记**：`status: deprecated`，`superseded_by` 指向替代文件
4. **过渡期**：至少 90 天保留本文件，期间消费者完成迁移
5. **延期**：90 天到期后有引用未迁移 → Owner 可批准延期（最长再延 90 天）——必须 Session Log 记录原因
6. **归档**：过渡期满、全部引用已迁移 → `status: archived`

---
