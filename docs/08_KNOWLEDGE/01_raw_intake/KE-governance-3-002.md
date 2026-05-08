---
module_id: KE-governance-3-002
title: 3. 受控枚举定义
category: governance
---

# 3. 受控枚举定义

3. 受控枚举定义

本文档定义了 **8 个生命周期阶段**作为受控枚举——这些值的 SSoT 在本文件中，不可在其他文件中重新定义：

| 枚举值 | 含义 | 进入条件（摘要） | 退出条件 |
|--------|------|---------|---------|
| `planned` | 规划中 | 新模块 ID 分配 | 准入通过（GOV-MOD-001）→ in_design |
| `in_design` | 设计中 | 准入通过 | 接口契约草案完成 → in_dev |
| `in_dev` | 开发中 | 设计完成 | 代码实现+单测通过 → testing |
| `testing` | 测试中 | 开发完成 | 集成测试+Owner 审批 → active |
| `active` | 生产活跃 | 测试通过 | Owner 裁决 → suspended/deprecated |
| `suspended` | 暂停中 | 外部依赖不可用等 | 原因消除 → active |
| `deprecated` | 已废弃 | 替代模块就绪 | 迁移完成 → archived |
| `archived` | 已归档 | 迁移完成 | —（终态） |

**受控约束**：新增或删除阶段需要创建 KB 决策记录（见 §12 修改条件）。所有使用 `status` 字段的文件（GOV-MOD-001 §7 #3 准入否决条件、GOV-MOD-005 INJ-004）必须从本枚举表中消费值。
