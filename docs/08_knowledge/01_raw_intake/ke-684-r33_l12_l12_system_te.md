---
module_id: KE-DOCUMENTAT-R33-L12-L12-SYSTEM-TE-001
status: active
title: 决策 R33：L12 命名最终锁定为 `infra_ops`（Closes OQ-030）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 决策 R33：L12 命名最终锁定为 `infra_ops`（Closes OQ-030）

决策 R33：L12 命名最终锁定为 `infra_ops`（Closes OQ-030）

**决策**：L12 命名采用 `infra_ops`，永久否决 `l12_observability`。

**完整理由链**：
- `system_telemetry` 强调"系统产出的结构化指标流"（metrics/logs/traces 三支柱），是机器消费（AI 读取）的数据流——这与 L07 `post_trade_analytics`（给人看的业务报表）明确区分，避免歧义
- `observability` 是 Google SRE Book 的工程文化概念（含 Debugging / Profiling / Post-mortem 等人工活动维度），适合做工程理念标签，不适合做代码层名
- `zephyr-src-gap-analysis.pdf` 原始分析文档明确使用 `infra_ops`，与本决策一致
- 前期设计稿 `ai-autonomy-architecture-design.md v1.1.0` 已采用 `infra_ops`
- **业界对标**：Google 内部层命名倾向于 "telemetry" 而非 "observability" 作为代码模块名（前者是技术准确描述，后者是文化/哲学描述）；Netflix OSS 同理

**落盘位置**：`application_architecture.md` §4.1 `infra_ops/` 完整子模块清单 + rationale 注释
