---
module_id: KE-1491---------4-------anthrop-003
title: 13.6 E. 氛围编程适配（4个）——对标 Anthropic Context Engineering + Cursor Rules
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 13.6 E. 氛围编程适配（4个）——对标 Anthropic Context Engineering + Cursor Rules

13.6 E. 氛围编程适配（4个）——对标 Anthropic Context Engineering + Cursor Rules

> **现状**：VMS 是 AI session 的"长期记忆"层。但蓝图没有约束不同成熟度 session 应该注入多少向量记忆。这是氛围编程最大未解决问题之一——AI 看到的记忆量直接决定了它的认知质量。

| # | 盲点ID | 盲点描述 | S | O | D | RPN | 触发场景 |
|:--|:--|------|:--:|:--:|:--:|:--:|------|
| 16 | **V-VMS-416** | **无"按 Session 成熟度"检索预算**——M1 模块施工应注入 ≤2000 tokens 向量记忆（仅 rules + lessons），M4 模块可注入 ≤5000 tokens（全 Collection）。没有预算控制→VMS 注入占用了 CT-BUDGET 的蓝图层预算 | 4 | 4 | 4 | **64** 🔴 | 每次 Context Engine build |
| 17 | **V-VMS-417** | **无检索结果的"时间衰减"权重**——30 天前的 decisions 和今天的 decisions 不应等权。时间越近越相关。RRF 融合阶段应加入 `time_decay = e^(-λ·age_days)` 因子 | 4 | 3 | 3 | 36 🔴 | 历史决策检索 |
| 18 | **V-VMS-418** | **无"检索质量负反馈"闭环**——当 AI 发现检索结果不相关/错误时，没有机制把这个信号写回 VMS。需要在 RetrievalTrace 中追加 `was_useful` 字段 + 定期分析低质量检索 → 调整分块策略/嵌入模型 | 3 | 3 | 3 | 27 🟠 | AI发现检索偏差 |
| 19 | **V-VMS-419** | **无跨 Collection 联合检索**——AI 经常问"这个模式以前遇到过吗？"→ 需要同时检索 lessons + execution_traces + decisions 找出历史相似情境。当前 single-Collection 检索无法回答交叉问题 | 4 | 4 | 3 | **48** 🔴 | AI做跨领域决策 |
