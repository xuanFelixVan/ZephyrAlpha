---
module_id: KE-664
status: active
title: ZephyrAlpha 标准文档模板
category: documentation
ttl: permanent
---

# ZephyrAlpha 标准文档模板

ZephyrAlpha 标准文档模板

> **module_id**: PS-STD-002 | **version**: 3.2.0 | **status**: active
>
> 本文档是 ZephyrAlpha 项目所有 **policy / standard** 类文档的**元标准**。
> 它规定了：一份标准文档**必须包含哪些章节**、**必须声明哪些治理信息**、
> **变更时必须同步哪些消费者**。
>
> v3.2.0 `adr` 从 L2 重分类至 L3——ADR 对标 Nygard ADR 轻量格式（信息性决策记录），
> 不应承受 L2 的 10 章治理负担。L3 只需 4 个 MUST 章。
>
> v3.1.0 L1 引入**标准子类型**——行为规则型、数据注册表型、宪法原则型、格式定义型。
> 不同子类型适用不同的章节集合，消除"所有标准必须包含所有 19 章"的一刀切。
>
> 对标：ISO/IEC Directives Part 2（IS/TS/TR 分层）、IETF BCP 14（MUST/SHOULD/MAY）、
> OpenLineage（producer/consumer 契约）。
>
> **根因**：元数据注册表（PS-STD-001）在 v4.2.0 之前缺失消费者注册表、
> 受控枚举与代码层的同步规则、SSoT 声明，导致字段改名后 18+ 个代码文件
> 需要人工逐个排查。本模板确保新标准不再重蹈覆辙。

---
