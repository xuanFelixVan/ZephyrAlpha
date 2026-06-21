---
module_id: PS-STD-009
title: 规则治理标准
doc_type: standard
status: active
version: "3.0.2"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
ttl: permanent
summary: "规则治理标准——规则生命周期状态机 + 变更门控审批体系。定义 draft→active→deprecated 状态转换规则、P0-P3 四级变更审批流程、退役级联、自动归档。原 PS-STD-010（rule-lifecycle-standard.md）已合并入本文件。"
tags: [governance, lifecycle, change-gate, protocol, derivation-based, state-machine]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§2~§3", why: "字段定义+受控词表——变更门控字段合法性依据"}
ai_autonomy: human_gated
---

# 规则治理标准

> **module_id**: PS-STD-009 | **version**: 3.0.2 | **status**: active | **layer**: cross_layer

本标准是 ZephyrAlpha 规则体系**生命周期状态机和变更门控审批体系**的唯一真源。

> **合并声明**：v3.0.0 合并原 PS-STD-010（rule-lifecycle-standard.md）。理由：生命周期定义"规则有哪些状态"，变更门控定义"状态迁移要谁批准"——数据和算子的供需关系，分开存储增加 AI 的上下文翻页成本。合并后 meta/ 从 13 减为 12 个文件。

> **铁律**：MUST 按变更门控审批流程修改规则——自由修改 = 分级失效 + 规则不一致。

> **治根方案**：分级基于声明属性（stability+scope）。属性来源：[PS-STD-004 rule-classification-and-arbitration-standard.md](rule-classification-and-arbitration-standard.md)。

---

## 1. 目的与范围

### 1.1 目的

定义 ZephyrAlpha 规则文件的完整治理流程——从起草到退役的**状态机**，以及每次状态迁移需要的**审批门控**。

### 1.2 适用范围

- `01_policies_and_standards/` 下所有 doc_type 文件
- `domains/` 下所有治理/操作规则文件
- `meta/` 下所有元标准文件

**不适用**：Session Log、审计报告（ttl: 30d/7d）、临时文件（ttl: session）。

### 1.3 与 document-lifecycle-standard.md（GOV-DOC-006）的区别

> 完整路径：`../governance/document/document-lifecycle-standard.md`

| 维度 | GOV-DOC-006 | 本标准 |
|------|-----------|--------|
| 管辖对象 | 所有文档（含非规则） | 仅规则文件 |
| 核心机制 | TTL 分级 + 归档 | 状态机 + 变更门控 + 退役级联 |
| 废弃触发 | 新版本发布 | 新版本 + 合并 + 删除 |
| 级联效应 | 无 | 废弃级联影响依赖方 |

**冲突时以本标准为准**（规则文件有特殊治理机制）。

---

## 2. 状态机

| 状态 | 含义 | 可执行操作 |
|------|------|-----------|
| draft | 草稿，正在编写中 | 编辑、删除、提交审批 |
| active | 已生效，当前有效 | 引用、P1/P2/P3 变更 |
| deprecated | 已废弃，有替代品 | 只读引用、不可修改 |

迁移路径：draft → active → deprecated（返工：draft ← draft；替代：active → deprecated via `superseded_by`）

> **archived 不是独立状态**：PS-STD-001 §4.1 裁定 archived 和 deprecated 对 AI 而言行为一致（都不再参考），归档是文件操作（git mv 到 archive/ 子目录），不是文档状态。deprecated 满 6 个月后执行文件物理迁移，但 status 字段保持 `deprecated` 不变。

### 2.2 状态迁移与门控映射

| 迁移 | 触发条件 | 变更级别 | 审批要求 | 前置检查 |
|------|---------|:---:|---------|---------|
| draft → active | Owner 批准 | P2 | Owner 签收 | PS-STD-001 §2.5 必填字段齐全 |
| active → deprecated | 新版本/合并/删除 | P1 | Owner 批准 | `superseded_by` 已填；依赖方已迁移 |
| draft → draft（返工） | 审批不通过 | — | — | 返工原因已记录 |

---

## 3. 变更分级

| 级别 | 定义 | 推导公式 | 审批要求 |
|:---:|------|---------|---------|
| **P0** | 修改 `stability: frozen` 的文件 | `stability=frozen` | Owner 必须手动执行，AI 禁止操作 |
| **P1** | 修改 `stability: stable` + `scope: global` 的文件中的强制条款 | `stability=stable AND scope=global` | Owner 明确批准后 AI 可执行 |
| **P2** | 修改 `stable`（scope≠global）或 `evolving` 的非强制条款 | `stable+非global` 或 `evolving` | AI 可执行，Session Log 记录 |
| **P3** | 新增规则文档（含完整 frontmatter） | 新文件 | AI 可执行，Session Log 记录 |

---

## 4. 变更流程

### 4.1 P0 变更

| 步骤 | 操作者 | 操作 |
|------|--------|------|
| 1 | Owner | 识别需要变更的 frozen 文件 |
| 2 | Owner | 直接编辑文件（不通过 AI） |
| 3 | Owner | 更新 document-metadata-index.yaml |
| 4 | Owner | Session Log 记录变更原因 |
| 5 | Owner | 通知所有正在工作的 AI（next_session_handover） |

**禁止**：AI 执行 P0 变更（即使 Owner 口头要求——必须 Owner 手动操作）。

受 P0 约束的文件示例（按属性判定）：

| 文件 | stability | scope |
|------|-----------|-------|
| PS-STD-001 metadata-registry.md | frozen | global |
| PS-STD-002 document-structure-standard.md | frozen | global |
| PS-STD-003 behavior-boundaries-standard.md | frozen | global |

### 4.2 P1 变更

| 步骤 | 操作者 | 操作 |
|------|--------|------|
| 1 | AI | 识别需要变更的强制条款 → Session Log 提出请求 |
| 2 | Owner | 审查并明确批准 |
| 3 | AI | 执行变更 → 更新 version 和 date |
| 4 | AI | 更新 document-metadata-index.yaml |
| 5 | AI | Session Log 记录变更详情 |

### 4.3 P2/P3 变更

| 步骤 | 操作 |
|------|------|
| 1 | AI 执行变更 |
| 2 | AI 更新 version 和 date |
| 3 | AI Session Log 记录：变更文件、摘要、原因 |
| 4 | P3 新增：分配 module_id → 完整 frontmatter → 更新 document-metadata-index.yaml → 同步 PS-STD-004 §8 画像表 |

---

## 5. 退役流程

### LFC-001：退役前必须完成依赖迁移

1. 搜索全项目引用该规则 module_id 的文件
2. 逐个确认引用方已迁移到替代规则
3. 如有未迁移的依赖方：先迁移，再退役

### LFC-002：退役必须填写 superseded_by

- 有替代规则：填写替代规则的 module_id + 路径
- 无替代（规则删除）：填写 `N/A` + reason

---

## 6. 废弃级联

| 级联类型 | 触发条件 | 处理方式 |
|---------|---------|---------|
| 依赖级联 | 被废弃规则引用了其他文件 | 依赖方需更新引用或同步废弃 |
| 编号级联 | 废弃规则的 module_id 被引用 | 引用方需更新 module_id |
| 注册表级联 | 废弃规则在注册表中 | 注册表自动更新 status |

### LFC-003：级联影响 ≥ 5 个文件时需 Owner 批准

> ⚠️ **待补充**：阈值"5"为工程经验值，尚未做专业机构对标论证（Google API Deprecation Policy / Kubernetes Deprecation Policy 影响面阈值）。beta+ 统一验证并写入依据。

---

## 7. 自动归档

| 规则 | 条件 | 动作 |
|------|------|------|
| deprecated 满 6 个月 | `status: deprecated` 且距今 ≥ 180 天 | `git mv` 移入 `archive/` 子目录，status 保持 `deprecated` |
| 归档保留 | `ttl: permanent` 规则 | 永久保留，不删除 |

---

## 8. 紧急变更

| 步骤 | 操作 |
|------|------|
| 1 | AI 立即停止当前操作 |
| 2 | Session Log 记录发现的问题和建议修复方案 |
| 3 | 等待 Owner 确认后执行修复 |
| 4 | **禁止** AI 自行判断"紧急"并绕过审批流程 |

---

## 9. 禁止行为

| 禁止操作 | 原因 |
|---------|------|
| AI 修改 `stability: frozen` 的文件 | P0 变更，Owner 专属 |
| AI 无 Owner 批准修改 P1 条款 | P1 变更必须批准 |
| AI 修改后不更新 Session Log | 违反变更记录要求 |
| AI 修改后不更新 version 和 date | 违反版本控制规范 |
| AI 绕过推导链声称"这条优先" | 违反 PS-STD-004 §9 推导链 |
| AI 基于"记忆"判断文件属性（不读 frontmatter） | 违反 PS-STD-003 ABS-52 |

---

## 10. SSoT 声明

| 声明项 | 值 |
|--------|-----|
| 本标准是什么的唯一真源 | 规则文件的状态机 + 变更门控分级 + 退役级联 |
| LFC 编号前缀 | 本标准的内部规则编号空间 LFC-001~003 |
| 属性来源 | stability / scope 定义于 PS-STD-004 |

---

## 11. 消费者注册表

| 消费者 | 消费方式 | Tier |
|--------|---------|:----:|
| PS-STD-004 | 画像表引用 stability/scope 维度 | 1 |
| PS-STD-012 | 验证标准引用门控分级 | 1 |
| PS-STD-011 | 方法论 MTH-007 引用 P0 阻断 | 1 |
| document-metadata-index.yaml | 注册表同步 | 1 |
| document-lifecycle-standard.md (GOV-DOC-006) | 规则 vs 文档生命周期区别引用 | 2 |

---

## 12. 与相关文件联动

| 文件 | 关系 |
|------|------|
| PS-STD-004 | **数据源**：stability / scope / 推导链定义 |
| PS-STD-003 | **禁止行为 SSoT**：P1 级条款来自 ABS 条目 |
| PS-STD-011 | **决策方法论**：MTH-002/MTH-007 引用 |
| GOV-DOC-005 | **P3 前置检查**：新建文件前走 DOC-005 |
| document-metadata-index.yaml | **注册表**：变更后同步 |

---
