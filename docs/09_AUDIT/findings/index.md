---
module_id: AUD-FINDINGS-IDX
title: 审计与安全事件 Finding 目录
doc_type: index
status: Active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
date: "2026-05-06"
ttl: permanent
summary: "安全泄漏类与事件响应 Finding Markdown 落盘目录（对齐 06-security-architecture.md）"
tags: [audit, findings, security-incident]
---

# findings / Finding 落盘说明

本目录为 **Finding 与事后事件记录** 的人工编写落点，与 `reports/`（自动或批处理审计报告）区分。

## 命名约定

| 场景 | 文件名模式 |
|------|------------|
| Secret 泄漏类 | `secret-leak-<short-id>.md` |
| 通用安全事件（24h 内初稿） | `incident-YYYYMMDD-<id>.md` |

具体内容结构见 `docs/02_enterprise_architecture/target-architecture/06-security-architecture.md` 对应章节。
