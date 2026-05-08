---
module_id: GOV-ARCH-003
title: 架构版本化策略
doc_type: policy
status: Draft
version: "0.2.0"
layer: L01
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
valid_from: "2026-05-01"
ttl: permanent
summary: "定义架构文档的版本号规则、变更日志要求和与代码版本的关系。"
tags: [architecture, governance, versioning]
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§2~§3", why: "字段定义+受控词表——版本号格式的metadata基准"}
ai_autonomy: human_gated
---
# 架构版本化策略
> module_id: GOV-ARCH-003 | version: 0.2.0 | status: Draft | layer: L1

---

## 1. 目的与范围

本策略定义 ZephyrAlpha 系统中架构文档的版本化规则。适用于：

- 架构视图文档
- 架构决策记录（KB 决策记录）
- 系统设计文档

---

## 2. 规则

### AVP-001：架构文档必须有版本号

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| AVP-001 | 所有架构文档的 frontmatter 必须包含 `version` 字段，格式为 `X.Y.Z` | 文档不合规 |

### AVP-002：版本号递增规则

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| AVP-002 | 版本号递增规则：Patch（Z+1）= 文字修正；Minor（Y+1）= 新增章节/规则；Major（X+1）= 架构方向变更 | 版本号混乱 |

### AVP-003：变更日志

| 条件 | 规则 | 违反后果 |
|------|------|---------|
| Minor 及以上变更 | 必须在文档末尾的修订记录中记录变更日期、版本和内容 | 审计不通过 |

### AVP-004：与代码版本的关系

| 条件 | 规则 | 违反后果 |
|------|------|---------|
| 架构变更导致代码修改 | 代码变更的 PR 必须引用对应的架构文档版本。架构决策记录参见 KB:decisions namespace（原 adr-protocol.md 已删除） | PR 不被接受 |

---

## 3. 验证方式

| 规则 | 验证方式 | 频率 |
|------|---------|------|
| AVP-001 | 检查架构文档是否有 version 字段 | 每次修改 |
| AVP-002 | 检查版本号递增是否符合规则 | 每次修改 |
| AVP-003 | 检查修订记录是否完整 | 每次修改 |
| AVP-004 | 检查代码 PR 是否引用架构版本 | 每次合并 |

---

## 4. 修订记录

| 日期 | 版本 | 修改内容 |
|------|------|---------|
| 2026-05-01 | 0.2.0 | #20 审批修复：ABS/COND → AVP-（AVP-001~AVP-004）。补齐 `depends_on: [GOV-ARCH-001]` + `ai_autonomy: human_gated`。`date` → 2026-05-01。 |
| 2026-04-30 | 0.1.0 | 初始版本 |
