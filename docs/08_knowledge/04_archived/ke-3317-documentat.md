---
module_id: KE-3200
title: 2.1 五档定义
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 2.1 五档定义

2.1 五档定义

| 档位 | 名称 | 定义 | 证据类型 | 对应 Goldman/BlackRock/CMMI |
|---|---|---|---|---|
| **L0** ⚪ | **Missing** 缺失 | 能力完全不存在，无代码 / 无文档 / 无 ADR | — | — |
| **L1** 🔵 | **Designed** 设计级 | 有 ADR / 有架构视图 / 有 canonical 设计稿 / 无代码 | ADR-00XX accepted + 视图定义 | Emerging / Draft / Initial |
| **L2** 🟡 | **Drafted** 草稿级 | 有代码原型 / skeleton 目录 / 部分模块 stub 级实现 | 代码存在但无生产级测试 | Defined / Alpha / Repeatable |
| **L3** 🟢 | **Usable** 可用级 | 核心功能实现 + 测试覆盖 ≥ 60% + 文档齐全 + 已在 Sprint 内验证 | pytest ≥ 60% + 文档 + Sprint 验收记录 | Managed / Beta / Defined |
| **L4** 🟣 | **Production** 生产级 | 真实资金 / 真实流量 / 治理三层（09-GOV）完整覆盖 + 监控告警 + Runbook | SLO 达标 + 治理通过 + 生产运行证据 | Optimized / Production / Managed |
| **L5** 🔴 | **Leading** 顶级机构对标 | 对标 Goldman/JPM/Two Sigma/Citadel 等顶级机构同能力的业界领先实现 | 公开论文 / 开源贡献 / 业界 benchmark | Leading / World-Class / Optimizing |
