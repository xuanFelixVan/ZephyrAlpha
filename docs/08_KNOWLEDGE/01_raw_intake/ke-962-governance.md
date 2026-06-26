---
module_id: KE-884
title: 4. 消费者注册表
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 4. 消费者注册表

4. 消费者注册表

以下文件直接依赖本文档——生命周期规则变更时必须同步更新：

| 消费者 | 文件 | Tier | 依赖内容 |
|--------|------|:---:|---------|
| GOV-MOD-ALPHA_SIGNAL_DOMAIN | module-admission-policy.md | 1 | §7 #3 准入否决条件 使用本规范的 `status` 枚举值（8 阶段列表）——INJ-004 映射 |
| GOV-MOD-005 | module-injection-rules-policy.md | 1 | INJ-004 `valid_values` 直接从本文档 §3 枚举表复制——此复制值必须在本文档变更时同步 |
| GOV-MOD-004 | module-interface-contract-policy.md | 1 | IFC-005 契约状态受本规范阶段约束——契约状态映射到模块生命周期状态 |
| module-id-registry.json | `data/` | 1 | 每个模块的 `status` 字段值必须来自本规范枚举表 |
| GOV-ARCH-001 | governance/architecture/ | 2 | suspended/archived 阶段的模块在架构图中需特殊标识 |
