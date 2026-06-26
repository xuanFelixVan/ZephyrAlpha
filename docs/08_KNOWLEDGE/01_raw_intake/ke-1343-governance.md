---
module_id: KE-1255
status: active
title: ZephyrAlpha 规则分类与冲突裁决标准
category: governance_rule
ttl: permanent
---

# ZephyrAlpha 规则分类与冲突裁决标准

ZephyrAlpha 规则分类与冲突裁决标准

> **module_id**: PS-STD-004 | **version**: 2.0.2 | **status**: active
>
> 本标准是 ZephyrAlpha 项目**规则分类体系**和**规则冲突裁决机制**的唯一真源。
>
> **上半卷（§2-§8）**：五维分类体系——所有规则文档按五个维度（Domain/Layer/Scope/Stability/Executor）分类。
> **下半卷（§9-§11）**：冲突裁决推导链——当两条规则冲突时，按 stability → layer → scope → Owner 链式推导优先级。
>
> > **合并声明**：v2.0.0 合并原 PS-STD-008（rule-priority-hierarchy.md）。理由：PS-STD-008 自述"本文不存数据，只存推导规则……PS-STD-004 的五维分类是数据源"——分类与裁决是供需关系，分开存储增加 AI 的上下文翻页成本。合并后 12 个 meta 文件减为 11 个。
>
> **根因**：当前规则分类仅依赖 `doc_type` 一个维度，无法表达：
> - 这条规则的作用范围是全局还是模块级？
> - 这条规则能不能被 AI 自主修改？
> - 这条规则是稳定的还是可能频繁变更？
> - 这条规则属于哪个领域？
> - 两条规则冲突时，按什么顺序裁决？
>
> 对标：ISO 11179（元数据分类）、Library of Congress Classification（多维分类）、
> Kubernetes SIG（领域分组）、Google Canonical Sources（权威层级）、
> ITIL Problem Management（冲突优先）。

---
