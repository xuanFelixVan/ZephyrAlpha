---
module_id: GOV-CMP-002
title: 审计追踪策略
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
summary: "定义 ZephyrAlpha 系统中什么操作必须留痕、审计日志格式、保留期限和访问权限。"
tags: [compliance, governance, audit]
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§2.5", why: "frontmatter字段唯一真源——策略文件的doc_type/rule_form一致性约束"}
  - {target: PS-STD-003, at: "§3", why: "行为边界标准——审计操作的安全宪法级约束基准"}
ai_autonomy: human_gated
---

# 审计追踪策略

> module_id: GOV-CMP-002 | version: 0.2.0 | status: draft | layer: L1

---

## 1. 目的与范围

本策略定义 ZephyrAlpha 系统中审计追踪的规则。适用于：

- 交易操作
- 系统配置变更
- 密钥/权限变更
- 数据访问
- AI 操作

---

## 2. 必须审计的操作

> 保留期限参见 `../../governance/data/data-retention-policy.md`（GOV-DATA-003）§2 保留期限表。

| # | 操作类型 | 审计内容 |
|---|---------|---------|
| 1 | 交易下单/撤单 | 时间、标的、方向、数量、价格、操作者 |
| 2 | 系统配置变更 | 变更前值、变更后值、操作者、时间 |
| 3 | 密钥/权限变更 | 变更类型、影响范围、审批者、时间 |
| 4 | 数据库读写（生产） | 查询内容、操作者、时间、影响行数 |
| 5 | AI 操作 | 操作内容、AI代理ID、权限级别、时间 |
| 6 | 安全事件 | 事件级别、描述、响应措施、复盘结论 |

---

## 3. 规则

### AUD-001：必须审计的操作不可绕过

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| AUD-001 | 上述6类操作的审计记录必须自动生成，不可被关闭或绕过 | 视为 P1 安全事件 |

### AUD-002：审计日志不可篡改

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| AUD-002 | 审计日志一旦生成，任何人（包括 Owner）不得修改或删除，直到保留期满 | 视为 P0 安全事件 |

### AUD-003：审计日志访问受限

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| AUD-003 | 审计日志只有 Auditor 和 Owner 角色可读（角色定义见 [GOV-SEC-002](../security/access-control-policy.md)），其他角色禁止访问 | 收回越权访问权限 |

### AUD-004：审计记录格式

| 条件 | 规则 | 违反后果 |
|------|------|---------|
| 所有审计记录 | 每条审计记录必须包含以下字段：`timestamp`（ISO 8601 格式 `YYYY-MM-DDTHH:MM:SSZ`，UTC 时区）、`operator_id`、`operation_type`、`operation_detail`、`result`。字段名使用 snake_case | 格式不合规的记录需补录 |

---

## 4. 验证方式

| 规则 | 验证方式 | 频率 |
|------|---------|------|
| AUD-001 | 检查6类操作是否都有审计记录 | 每月 |
| AUD-002 | 检查审计日志是否有被修改的痕迹 | 每季度 |
| AUD-003 | 检查审计日志的访问权限配置 | 每月 |
| AUD-004 | 抽查审计日志格式是否合规 | 每周 |

---

## 5. 修订记录

| 日期 | 版本 | 修改内容 |
|------|------|---------|
| 2026-05-01 | 0.2.0 | #25 审批修复。(1) 编号前缀：ABS/COND → AUD-（AUD-001~AUD-004）。(2) AUD-004 审计记录格式：指定字段名使用 snake_case（timestamp/operator_id/operation_type/operation_detail/result），ISO 8601 格式 `YYYY-MM-DDTHH:MM:SSZ`。(3) `depends_on: GOV-DATA-003, GOV-SEC-002, ai_autonomy: human_gated`。(4) `date` → 2026-05-01。 |
| 2026-04-30 | 0.1.0 | 初始版本 |
