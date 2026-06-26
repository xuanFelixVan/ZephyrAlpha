---
module_id: KE-1168--------mod-p3-003
status: active
title: MAD-003：依赖关系合规（MOD-P3）
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# MAD-003：依赖关系合规（MOD-P3）

MAD-003：依赖关系合规（MOD-P3）

- 通过条件：depends_on 中所有模块 ID 已在注册表中存在，依赖图无环，且依赖方向符合 GOV-ARCH-001 的跨层规则（cold 层禁止依赖 hot 层）
- 否决条件：引用不存在的模块 ID、形成循环依赖、或违反跨层依赖方向约束
