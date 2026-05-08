---
module_id: KE-documentat-2_7_____________b5-004
title: 2.7 任务卡 / 知识库组件（B5 施工图产出）
category: documentation
---

# 2.7 任务卡 / 知识库组件（B5 施工图产出）

2.7 任务卡 / 知识库组件（B5 施工图产出）

| 组件 | 权限 | 判定理由 |
|------|------|---------|
| TagSchemaRegistry | Immutable Core | 元规则锁定，schema 变更走 rationale-log |
| InvariantGuard | Immutable Core | 不变量定义不可运行时改 |
| ProvenanceLogger | Immutable Core | 自身变更需走流程 |
| TagEngine | AI-Modifiable | 每次标签变更必须写 Provenance |
| AutoCleanScheduler（**修正**：原 Human-Gated） | **Immutable Core** | 删除规则不可改 |
| EpicAggregator / EpicVirtualRegistry（**修正**） | **Human-Gated** | Epic 创建涉及架构层级变更 |
| DomainLayerMapper | Human-Gated | 映射表修改需 Owner |
| KBCrawler | AI-Modifiable + 约束 | 输出只能写 quarantine |
