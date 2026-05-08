---
module_id: KE-governance-2__ssot-003
title: 2. SSoT 声明
category: governance
---

# 2. SSoT 声明

2. SSoT 声明

本文档是 ZephyrAlpha 系统中**跨登记表同步操作规范**的唯一真源（SSoT）。

**本文档定义了**：
- 12 种工件操作 × 13 个登记目标分类的完整同步矩阵（MRS-001）
- 同步原子性约束（MRS-002）
- 同步后校验要求（MRS-003）
- 6 条禁止行为（MRS-004）

**本文档与以下文件互补**（非取代关系）：
- [registry-master-index.yaml](../../_registry/catalogs/registry-master-index.yaml)：列出 `total_registries` 条 catalogs 收录项——本标准是"创建 X 后怎么写"，它是"写到哪张表"
- [registry-of-registries.yaml](../../_registry/catalogs/registry-of-registries.yaml)：共享字段和 SSoT 归属——本标准是"怎么同步"，它是"同步什么共享字段"
- GOV-MOD-001 准入门控：创建模块时的审批流程——本标准是准入通过后登记数据的操作规范
- GOV-MOD-003 生命周期策略：status 枚举值定义——本标准是 status 变更后的同步操作

**若其他文件中出现与本标准冲突的多登记表同步规则，以本文档为准。**

---
