---
doc_type: index
module_id: GOV-067
layer: cross_layer
status: Active
version: 1.0.0
date: '2026-05-02'
owner: ZephyrAlpha-Owner
summary: docs/ 根目录索引 — 抽屉式文档体系的总入口，声明每个抽屉的唯一责任
depends_on:
- target: GOV-DOC-002
  at: §5
  why: 防幻觉路径映射表——确定文件归属
- target: GOV-DOC-002
  at: §7
  why: 新建目录的 KB 决策记录审批流程
title: Docs
---

# ZephyrAlpha 文档体系 — 根目录索引

## 责任声明（Single Responsibility）

本目录是 **ZephyrAlpha 2.0 文档体系的物理根目录**。采用**抽屉式（Drawer System）**组织：每个编号子目录是一个"抽屉"，有且仅有一项唯一责任。

> **核心原则**：任何文件只有一个正确的存放位置。如果你不确定一个文件该放哪，先查 GOV-DOC-002 的防幻觉路径映射表。

---

## 根目录文件

| 文件 | 说明 |
|------|------|
| `index.md` | 本文件——目录索引（AI 入口） |

---

## 子目录（抽屉）一览

| 编号 | 目录 | 责任（单一） | 对标 |
|------|------|-------------|------|
| 01 | `01_policies_and_standards/` | C/B 轨共享：治理规范 / 标准 / 协议 / 操作手册 / 元规则 / 注册表 / 模板 | ITIL SACM · Linux FHS |
| 02 | `02_enterprise_architecture/` | 企业架构文档（TOGAF 视图 + KB 决策记录 + 架构模型 YAML） | TOGAF · KB 决策记录 |
| 03 | `03_modules/` | C 轨镜像：14 层模块生命周期文档（蓝图 → 施工图 → 交付） | Google Monorepo · Linux FHS |
| 07 | `03_modules/_b_track_interfaces/` | B 轨镜像：5 大 AI 核心服务接口合同（LSG/VMS/CE/Orc/FLE）——物理位于 03_modules/ 下，编号独立为 07 | K8s API · Terraform Provider Contract |
| 08 | `08_knowledge/` | 知识库：项目经验教训（KE）、最佳实践 | — |
| 09 | `09_audit/` | 审计总控与审计报告（Ex-post，对已发生事实的验证） | ITIL Audit · ISO 27001 内部审计 |

> **预留编号**：04-06（已合并/预留）、10-18（预留）、19（已移出项目至外部工作区）、20-98（预留）、99（终态归档，待建）

---

## AI 使用指南

1. **找文件**：查上表中对应抽屉 → 进入其 `index.md` → 继续下钻
2. **放文件**：查 GOV-DOC-002 §5 防幻觉路径映射表 → 确定唯一目标目录 → 放进去
3. **新建目录**：必须走 KB 决策记录审批流程（GOV-DOC-002 §7）
4. **不确定**：在 `09_audit/findings/` 登记为审计发现，不实施

---

## 排除规则（不应放入本目录）

- ❌ 任何治理规范/标准/协议 → `01_policies_and_standards/`
- ❌ 架构视图/KB 决策记录/YAML 模型 → `02_enterprise_architecture/`
- ❌ 模块蓝图/施工图/交付记录 → `03_modules/`
- ❌ AI 服务接口合同 → `03_modules/_b_track_interfaces/`
- ❌ 知识库条目 → `08_knowledge/`
- ❌ 审计报告/状态 → `09_audit/`
