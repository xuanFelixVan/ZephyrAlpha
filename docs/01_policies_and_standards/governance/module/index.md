---
module_id: GOV-MOD-000
title: "模块治理目录索引"
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
summary: "governance/module/ 目录的导航索引。声明本目录的责任范围、文件清单及每文件的核心职责。新 AI session 进入本目录时，应首先读取本文件以建立全局认知。"
tags: [index, module, governance, navigation]
depends_on:
  - target: PS-STD-001
    at: "§5.8"
    why: "metadata-registry.md 定义 GOV-MOD 模块 ID 的分配规则"
---

# 模块治理目录索引

> **module_id**: GOV-MOD-000 | **version**: 1.0.0 | **status**: active

---

## §1 本目录的责任

`governance/module/` 是 ZephyrAlpha 的**模块治理中心**。这里管的是一切与"模块怎么接入、怎么活着、怎么改、怎么退役"相关的规则。

**正向责任**（本目录管的事）：
1. 模块准入门禁——新增/变更/迁移模块必须满足的条件
2. AI 模型行为铁律——AI 在任何操作中必须遵守的 10 条铁律
3. 模块注入规则——模块注入系统的 YAML 格式规则
4. 模块接口契约——模块对外暴露接口的格式要求
5. 模块生命周期——模块从注册到退役的全过程管理
6. 多登记表同步——模块操作后的多登记表一致性维护
7. 模型上线前 10 条规则——新模型上线前的准入检查事项

**负向责任**（本目录不管的事，去对应目录找）：
- 架构治理（ADR、评审门控）→ `governance/architecture/`
- AI 自治权限注册表 → `governance/ai/ai-autonomy-authority-registry.md`
- 文档命名和路径规范 → `governance/document/`
- 代码实现的模块接口 Schema → `src/zephyr/shared/contracts/`

---

## §2 文件清单

| 文件 | module_id | 一句话职责 |
|------|-----------|-----------|
| [module-admission-policy.md](../../governance/module/module-admission-policy.md) | GOV-MOD-001 | 模块新增/变更/迁移的准入条件与评审流程 |
| [ai-behavior-iron-policy.md](../../governance/module/ai-behavior-iron-policy.md) | GOV-MOD-002 | AI 模型的 10 条行为铁律 |
| [module-injection-rules.yaml](../../governance/module/module-injection-rules.yaml) | GOV-MOD-005 | 模块注入系统的规则格式定义 |
| [module-interface-contract-policy.md](../../governance/module/module-interface-contract-policy.md) | GOV-MOD-004 | 模块对外接口的契约格式要求 |
| [module-lifecycle-policy.md](../../governance/module/module-lifecycle-policy.md) | GOV-MOD-003 | 模块注册→退役的全生命周期管理 |
| [multi-registry-synchronization-standard.md](../../governance/module/multi-registry-synchronization-standard.md) | GOV-MOD-007 | 全部工件类型的多登记表同步操作规范（v2.0.0，覆盖 15 个分类） |

---
| *（GOV-MOD-006 已废止）* | — | 原"模型入驻前10条铁律"，全部内容已迁移至 GOV-MOD-002（AI 模型行为铁律）|

---

---

## §3 依赖关系速览

```
GOV-MOD-001 (admission-policy)        ← 准入总入口，被所有其他文件引用
    ├── GOV-MOD-002 (iron-policy)     ← 行为铁律——原 GOV-MOD-006 内容已归入此文件
    ├── GOV-MOD-005 (injection)      ← 注入规则依赖准入格式
    ├── GOV-MOD-004 (interface)      ← 接口契约依赖准入的模块边界
    ├── GOV-MOD-003 (lifecycle)      ← 生命周期依赖准入的注册→退役流程
    └── GOV-MOD-007 (sync)           ← 多登记表同步——修改任何模块登记数据须遵循此规范
```

---

## §4 对 AI 的使用指引

每个新 AI session 进入本目录后，应按以下顺序建立认知：

1. **先读本文件**（你正在读的这个）——了解全貌
2. **再读 ai-behavior-iron-policy.md**——理解自己绝对不能做什么
3. **再读 module-admission-policy.md**——理解模块改动的边界
4. **再读 multi-registry-synchronization-standard.md**——知道改模块数据必须同步哪些登记表
5. **按需读取**其余文件

除 GOV-MOD-007（多登记表同步标准，`ai_autonomy: ai_editable`）外，其余文件均标记 `ai_autonomy: human_gated`——AI 可以读取和应用这些规则，但**不得单方面修改**。任何修改必须由 Owner 审批。

---
