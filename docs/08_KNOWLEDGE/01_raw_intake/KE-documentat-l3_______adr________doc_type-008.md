---
module_id: KE-documentat-l3_______adr________doc_type-008
title: L3 基础模板（`adr` 及其他所有 doc_type）
category: documentation
---

# L3 基础模板（`adr` 及其他所有 doc_type）

L3 基础模板（`adr` 及其他所有 doc_type）

对标：ISO Technical Report / IETF Informational / IEEE Guide / W3C Note

> v3.2.0：`adr` 从 L2 重分类至 L3。ADR（Architecture Decision Record）对标 Michael Nygard 原始格式（5 段极轻结构：Context → Decision → Rationale → Consequences → Alternatives），性质是信息性决策记录，非设计规范。L2 的 10 章治理要求不适合 ADR——强制补治理章会导致 ADR 失去"快写快读"的核心价值。

| # | 章节 | 必要性 | 说明 |
|---|------|:------:|------|
| 1 | **目的与范围** | MUST | 包含 §1.2 责任范围 + §1.3 责任边界 |
| 2 | **主体内容** | MUST | 禁止使用 MUST/SHOULD（L3 是纯信息性文档） |
| 3 | **AI 自治权限标注** | MUST | 标注 AI 对本文档的操作权限 |
| 4 | **TTL 与生命周期** | MUST | 标注保留期限和过期处理方式 |
| 5 | **变更记录** | SHOULD | 版本历史（TTL <= 7d 的可省略） |

> **L3 与 L2 的关键差异**：
> - L3 完全禁止规范性语言（MUST/SHOULD），只能使用信息性措辞
> - L3 不需要消费者注册表、SSoT 声明、变更同步规则
> - L3 必须标注 TTL（信息性文档容易堆积，TTL 是清理机制）
