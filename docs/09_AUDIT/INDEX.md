---
classification: internal
date: '2026-05-02'
doc_type: index
generated: '2026-05-02'
layer: cross_layer
module_id: AUDIT-ROOT-README-001
status: Active
title: 审计文档目录
version: "1.0.0"
ttl: permanent
depends_on:
  - target: GOV-DOC-002
    at: "§5"
    why: "防幻觉路径映射表——审计报告应归入 09_audit/ 的合规依据"
---

# 09 Audit — 目录索引

## 责任声明（Single Responsibility）

本目录只存放：**审计报告与审计状态数据（Ex-post — 执行得怎样）**。

## 文件清单

| 路径 | 文件 | 说明 |
|------|------|------|
| `reports/` | `architecture-alignment-audit.md` | 架构合规审计报告（2026-04-25） |
| `reports/` | `ssot-validation-LATEST.md` | SSoT 矛盾扫描报告（2026-05-02） |
| `state/` | `index.md` | 审计状态目录入口 |
| `state/` | `ssot-issue-tracking.yaml` | SSoT 已知问题追踪登记表（对标 ITIL KEDB——2026-05-03 创建） |
| — | `index.md` | 本文件 |

## 目录用途

存放审计报告与审计状态数据。

## 准入规则

- ✅ 架构合规性审计报告
- ✅ SSoT 验证扫描报告
- ✅ 审计状态数据（如元数据库快照）
- ❌ 任何形式的治理规则、合规规范、标准文件（→ `01_policies_and_standards/`）

## 当前文件清单

```
09_audit/
├── index.md                                     ← 本文件
├── reports/
│   ├── architecture-alignment-audit.md           ← 架构合规审计报告（2026-04-25）
│   └── ssot-validation-LATEST.md               ← SSoT 矛盾扫描报告（2026-05-02）
└── state/
    ├── index.md                                  ← 审计状态目录（运行时数据）
    └── ssot-issue-tracking.yaml                ← SSoT 已知问题追踪（对标 ITIL KEDB）2026-05-03
```

## 责任边界

本目录只存审计**报告**（"执行得怎样" / Ex-post）。合规规范（"规则是什么" / Ex-ante）属于 `01_policies_and_standards/`——治理规则只有一个家。

## 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-05-01 | 1.1.0 | 移除 10_compliance/ 引用——合规规范归 01_policies_and_standards/ 管辖 |
| 2026-05-01 | 1.0.0 | 初始创建——补齐缺失的目录入口文件 |


## 排除规则（不应放入本目录的内容）

- ❌ 治理规范/合规标准 → `01_policies_and_standards/`
- ❌ 架构文档 → `02_enterprise_architecture/`

## 父级目录

- 父级：[docs 根目录](../index.md)
