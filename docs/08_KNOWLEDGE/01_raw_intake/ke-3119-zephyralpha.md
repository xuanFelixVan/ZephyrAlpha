---
module_id: KE-MODULE-BLU-ZEPHYRALPHA-004
status: active
title: ZephyrAlpha 蓝图体系架构标准
category: module_blueprint
ttl: permanent
---

# ZephyrAlpha 蓝图体系架构标准

ZephyrAlpha 蓝图体系架构标准

> **module_id**: PS-STD-005 | **version**: 1.0.0 | **status**: active | **layer**: cross_layer

> 本标准是 ZephyrAlpha 蓝图体系的**元标准**——定义蓝图的三级金字塔结构。
>
> **根因**：现有 19 份蓝图全部平铺在 `03_modules/infra_ops/` 下，没有任何层级归属声明。
> 新 AI session 打开项目后，不知道"哪份蓝图是总蓝图、哪份是子蓝图、子蓝图归属于哪个总蓝图"。
> 当项目从 19 份蓝图扩展到 100+ 份蓝图（14 层 × 多域）时，扁平化将不可持续——新蓝图不知道在哪个目录创建、与谁建立引用关系。
>
> **对标**：
> - **Codified Context** (arXiv 2602.20478, 2026-02)：三层记忆模型——Tier 1 热记忆宪法（~660 行每 session 自动加载）→ Tier 2 领域专家 Agent（19 个按触发条件加载）→ Tier 3 冷记忆知识库（34 份 MCP 按需检索）
> - **Microsoft Edge AI**：`master-blueprint/`（总蓝图）→ `blueprints/{domain}/`（领域蓝图）→ `src/{component}/`（组件库）。总蓝图只定义组件如何组合。
> - **HP Inc AI Blueprints**：`specification.md`（蓝图总设计——"放哪、怎么命名"）+ `blueprint.md`（具体架构）。两层分离。
> - **TOGAF**：Architecture Repository 按层存放（Architecture Landscape / Reference Library / Standards Information Base / Governance Log）
> - **ITIL SACM**：CI Hierarchy（Logical CI → Physical CI，逐级细化）
>
> **本标准与 PS-STD-002 的关系**：
> - PS-STD-002（标准文档模板）管"**单个标准怎么写**"——章节清单、治理章、消费者注册表
> - PS-STD-005（本标准）管"**整个蓝图体系怎么建**"——层级结构、目录归属、ID 命名、引用链
> - 两者互补，不重复。蓝图编写者需要同时查 PS-STD-002（章节模板）+ PS-STD-005（放在哪个层级目录下）

---
