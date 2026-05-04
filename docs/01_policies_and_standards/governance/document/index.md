---
module_id: GOV-DOC-000
title: "文档治理目录索引"
doc_type: index
status: active
version: "1.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
ai_autonomy: human_gated
created_by: human_plus_agent
date: "2026-05-01"
valid_from: "2026-05-01"
ttl: permanent
summary: "governance/document/ 目录的导航索引。声明本目录的责任范围、文件清单及每文件的核心职责。新 AI session 进入本目录时，应首先读取本文件以建立全局认知。"
tags: [index, document, governance, navigation]
depends_on:
  - target: PS-STD-001
    at: "§5.8"
    why: "metadata-registry.md 定义 GOV-DOC 模块 ID 的分配规则"
---

# 文档治理目录索引

> **module_id**: GOV-DOC-000 | **version**: 1.0.0 | **status**: active

---

## §1 本目录的责任

`governance/document/` 是 ZephyrAlpha 的**文档治理中心**。这里管的是一切与"文件怎么命名、怎么放、怎么发现、怎么活、怎么死"相关的规则。

**正向责任**（本目录管的事）：
1. 目录结构规范——docs/ 和 src/zephyr/ 的双轨治理
2. 文件命名规范——所有文件的命名格式
3. 文件路径规范——文件放在哪个目录的确定性规则
4. 编码安全规范——禁止特定操作（PowerShell echo 写 .md 等）
5. 文档生命周期——TTL 分级、状态机、归档流程
6. 文件操作安全门禁——删除/移动前的安全检查
7. 统一编号标准——module_id 和编号的分配规则
8. 文档控制原则——引用链、审计、决策边界
9. 文档可发现性——AI 和人类如何找到需要的文档

**负向责任**（本目录不管的事，去对应目录找）：
- 元规则（"规则怎么写"）→ `meta/`
- 模块治理规则 → `governance/module/`
- AI 行为铁律 → `governance/module/ai-behavior-iron-policy.md`
- 代码实现的 Schema → `src/zephyr/shared/contracts/`

---

## §2 文件清单

| 文件 | module_id | 一句话职责 |
|------|-----------|-----------|
| [directory-structure-standard.md](../../governance/document/directory-structure-standard.md) | GOV-DOC-002 | 定义 docs/ + src/zephyr/ 双轨目录结构 |
| [file-naming-standard.md](../../governance/document/file-naming-standard.md) | GOV-DOC-003 | 定义所有文件的命名格式 |
| [file-path-standard.md](../../governance/document/file-path-standard.md) | GOV-DOC-004 | 定义文件的确定存放路径 |
| [encoding-safety-standard.md](../../governance/document/encoding-safety-standard.md) | GOV-DOC-005 | 编码安全硬规则 |
| [document-lifecycle-standard.md](../../governance/document/document-lifecycle-standard.md) | GOV-DOC-006 | TTL 分级 + 状态机 + 归档流程 |
| [file-operation-safety-policy.md](../../governance/document/file-operation-safety-policy.md) | GOV-DOC-007 | 删除/移动文件前的安全门禁（操作安全）。质量保全以 AGENTS.md §6.8 为准 |
| [unified-numbering-standard.md](../../governance/document/unified-numbering-standard.md) | GOV-DOC-001 | module_id 编号分配规则 |
| [document-control-policy.md](../../governance/document/document-control-policy.md) | GOV-DOC-009 | 引用链、审计、决策边界 |
| [document-discovery-policy.md](document-discovery-policy.md) | GOV-DOC-010 | AI 和人类如何发现文档 |

---

## §3 依赖关系速览

```
GOV-DOC-002 (directory-structure)     ← 路径总图，被所有文件引用
    ├── GOV-DOC-004 (file-path)        ← 依赖 §1 路径规范
    │       └── GOV-DOC-007 (safety-policy) ← 依赖 §4 锚点保护
    ├── GOV-DOC-003 (file-naming)      ← 独立：命名格式不与结构耦合
    ├── GOV-DOC-005 (encoding-safety)  ← 独立：硬规则不与结构耦合
    ├── GOV-DOC-006 (lifecycle)        ← 依赖 DOC 结构中的 TTL字段
    ├── GOV-DOC-001 (numbering)        ← 依赖 module_id 前缀体系
    ├── GOV-DOC-009 (control-principles) ← 依赖引用链完整性
    └── GOV-DOC-010 (discovery)        ← 依赖注册表 + 索引 + 工具搜索三路径
```

---

## §4 对 AI 的使用指引

每个新 AI session 进入本目录后，应按以下顺序建立认知：

1. **先读本文件**（你正在读的这个）——了解全貌
2. **再读 directory-structure-standard.md**——理解"文件放在哪里"
3. **按需读取**其余文件——根据当前任务类型选读

所有文件均标记 `ai_autonomy: human_gated`——AI 可以读取和应用这些规则，但**不得单方面修改**。任何修改必须由 Owner 审批。

---
