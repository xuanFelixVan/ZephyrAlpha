---
module_id: KE-336
status: active
title: 4. View dependencies / 视图依赖关系
category: documentation
---

# 4. View dependencies / 视图依赖关系

4. View dependencies / 视图依赖关系

> **📊 视图依赖关系总览**：见 [`diagrams/readme_view_dependency_graph.mmd`](diagrams/readme_view_dependency_graph.mmd)

**正交视图说明**：`04bis` 和 `04ter` 使用**黄色高亮节点**表示它们是 **TOGAF 10 视图之外的正交视图**——虚线 `-.正交标注叠加.->` 表示它们**不改变 TOGAF 视图的业务决策**，只是在这些视图上提供额外的切片标注（运行平面 / 能力成熟度）。详见 §1ter 正交视图体系。

**反向约束**：TA 成本限制 → AA 范围 → IA 范围 → BA 野心。

**IA vs DA 正交性**：IA 治"docs/ 文档抽屉"，DA 治"业务数据对象"，两者**平级且零内容重叠**。详见 `data_architecture.md §10.2`（图书馆书架 vs 账本资金往来的类比）。

**INTEG（07）的双重下游**：集成架构同时为安全架构提供"所有外部接入点清单"，为运维架构提供"需要监控的集成点列表"——这也是为什么 07 建议在 06/08 之前阅读。

---
