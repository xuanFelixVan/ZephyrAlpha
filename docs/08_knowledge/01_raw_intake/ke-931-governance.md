---
module_id: KE-853
status: active
title: §3 依赖关系速览
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# §3 依赖关系速览

§3 依赖关系速览

```
GOV-ARCH-001 (adr-protocol)    ← ADR 状态机和废弃规则
    ├── GOV-ARCH-002 (review-policy)     → 引用 §3，检查变更是否违反已有 ADR
    └── GOV-ARCH-003 (versioning)      → 引用全文，架构版本号与 ADR 的关系

GOV-ARCH-006 (gate-strategy-standard)           ← KMS 门禁策略 SSoT
    ├── 定义 5 级门禁的触发条件、检查项、severity 映射
    └── 关联 GOV-ARCH-003 的版本策略（门禁 YAML schema 版本化）

GOV-ARCH-005 (phase-transition-protocol) ← Phase 过渡双门协议
    ├── 定义 exit_criteria / next_phase_entry_criteria
    └── 引用 GOV-ARCH-004 的门禁概念（Phase 门禁 ≠ KMS 门禁）
```

> **注意**：GOV-ARCH-001 与 GOV-ARCH-002 曾存在循环依赖（A→B, B→A），已于 2026-05-01 解除——移除 ARCH-001 对 ARCH-002 的依赖。ADP 协议定义 ADR 生命周期时不需要评审门控。

---
