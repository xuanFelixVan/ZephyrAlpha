---
module_id: KE-091
status: active
title: 1.4 适用范围
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 1.4 适用范围

1.4 适用范围

本模板采用**三层模板体系**（对标 ISO/IEC Directives Part 2、IETF RFC 7841、IEEE SA Operations Manual、W3C Process Document 的分层做法）：

| 模板层 | 适用 doc_type | 对标专业机构 | 规范性语言 |
|--------|-------------|------------|----------|
| **L1 治理模板** | `policy` `standard` `ai_governance` | ISO IS / IETF Standards Track / IEEE Standard / W3C REC | MUST/SHOULD/MAY |
|   | → 含 4 种**标准子类型**（§3.2）：行为规则型、数据注册表型、宪法原则型、格式定义型——不同子类型适用不同章节集合 |
| **L2 设计模板**（中等 10 章） | `blueprint` `design` `service_spec` | ISO TS / IETF BCP / IEEE RecPractice | SHOULD/MAY |

> 注：`construction_plan` 原为独立 L2 模板，已于 2026-05-02 合并入 `blueprint`（§12 施工指引）。对历史文档 `doc_type: construction_plan` 仍保留。 2026-05-26 升级：施工细节职责从蓝图转移到任务卡（详见 GOV-TASK-001 6），蓝图只写设计，任务卡写施工。
| **L3 基础模板**（轻量 5 章） | `adr` 及其他所有 doc_type | ISO TR / IETF Informational / IEEE Guide / W3C Note | 禁止 MUST/SHOULD |

> **核心区分机制**（四家专业机构一致）：规范性语言是分层的核心。
> L1 允许最高级规范性语言（MUST），L2 降级为 SHOULD，L3 完全禁止规范性语言。
> 这不是随意限制——信息性文档使用 MUST 会导致读者误以为有强制约束力。

各层模板的章节清单见 §3.1。L1 标准的子类型与章节适用性见 §3.2。
