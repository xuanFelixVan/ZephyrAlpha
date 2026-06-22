---
module_id: GOV-054
title: 审计总控索引
doc_type: index
status: Active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-06"
ttl: permanent
summary: "ZephyrAlpha 审计体系入口索引（Ex-post——对已发生事实的验证）"
tags: [audit, index, governance]
depends_on:
  - {target: GOV-CMP-003, at: "全文", why: "审计协议——每次审计的唯一入口文档"}
---

# 审计总控

> **定位**：Ex-post 验证——审计已发生事实的结果和合规性。
> **治理规则**见 `docs/01_policies_and_standards/rules/`。
> **审计协议**：每次审计启动前必读 [GOV-CMP-003](../01_policies_and_standards/rules/trae_044_compliance_audit.yaml)。

## 子目录

| 子目录 | 用途 |
|--------|------|
| `reports/` | 审计报告（架构对齐审计、SSoT 验证 LATEST） |
| `state/` | 审计状态数据（SSoT 问题追踪 yaml） |
| `handoff/` | AI Session 交接日志（会话级上下文传递） |
| `findings/` | 安全/合规 Finding 与事件初稿（对齐安全架构视图约定的 Markdown 落盘） |

## 快速导航

- **Finding 与安全事件初稿**：[findings/index.md](findings/index.md)
- **审计协议**：[GOV-CMP-003](../01_policies_and_standards/rules/trae_044_compliance_audit.yaml)
