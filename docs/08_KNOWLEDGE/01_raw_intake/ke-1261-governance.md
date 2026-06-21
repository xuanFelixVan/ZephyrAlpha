---
module_id: KE-1174
status: active
title: MLC-003：退役必须完成引用迁移
category: governance
---

# MLC-003：退役必须完成引用迁移

MLC-003：退役必须完成引用迁移

模块从 active 转为 deprecated 前，必须完成以下步骤：

1. 确认所有依赖方已迁移到替代模块
2. 全项目搜索旧 module_id，确认无断链
3. 在 `module-id-registry.json` 中标记 `status: deprecated`
4. 设置 `superseded_by` 字段
5. 保留文件至少 90 天，90 天后经 Owner 批准方可物理删除（进入 archived）
6. **延期机制**：如果 90 天到期后仍有引用未迁移，Owner 可批准延期（最长再延 90 天）。延期必须在 Session Log 中记录原因和截止日期
7. **契约级联废弃**：模块进入 `archived` 时，触发以下级联动作（IFC-007）：
   a. 该模块在 `cross_layer_contracts.yaml` 中的所有 frozen 契约自动标记为 `deprecated`
   b. 消费者在迁移期限内完成迁移（从模块归档之日起算，迁移期限见 GOV-MOD-004 §18 废弃流程）
   c. 期满后契约自动进入 `archived` 状态
