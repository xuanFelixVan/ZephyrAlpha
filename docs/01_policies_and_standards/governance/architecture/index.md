---
module_id: GOV-ARCH-000
title: "架构治理目录索引"
doc_type: index
status: active
version: "1.1.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
ai_autonomy: human_gated
created_by: human_plus_agent
date: "2026-05-02"
valid_from: "2026-05-01"
ttl: permanent
summary: "governance/architecture/ 目录的导航索引。声明本目录的责任范围、文件清单及每文件的核心职责。新 AI session 进入本目录时，应首先读取本文件以建立全局认知。"
tags: [index, architecture, governance, navigation]
depends_on:
  - target: PS-STD-001
    at: "§5.8"
    why: "metadata-registry.md 定义 GOV-ARCH 模块 ID 的分配规则"
---

# 架构治理目录索引

> **module_id**: GOV-ARCH-000 | **version**: 1.1.0 | **status**: active

---

## §1 本目录的责任

`governance/architecture/` 是 ZephyrAlpha 的**架构治理中心**。这里管的是一切与"架构决策怎么记录、架构变更怎么评审、架构文档怎么版本化"相关的规则。

**正向责任**（本目录管的事）：
1. 架构决策记录（ADR）的协议——谁提 ADR、怎么审批、怎么归档
2. 架构评审门控——什么变更必须经过架构评审、评审清单、否决条件
3. 架构文档版本化策略——版本号规则、变更日志要求、与代码版本的关系
4. KMS 门禁策略——5 级知识管道门禁（Ingest/Triage/Evaluate/Activate/Extract）的 SSoT
5. Phase 过渡双门协议——Phase 0-4 之间过渡的退出-准入条件与自动化校验

**负向责任**（本目录不管的事，去对应目录找）：
- 架构决策记录的具体内容 → `docs/02_enterprise_architecture/adr/`
- 架构评审的具体执行步骤 → `operational/vibe_coding/`
- 代码实现的架构契约 → `src/zephyr/shared/contracts/`
- 企业架构模型（TOGAF）→ `docs/02_enterprise_architecture/`

---

## §2 文件清单

| 文件 | module_id | 一句话职责 |
|------|-----------|-----------|
| [adr-protocol.md](adr-protocol.md) | GOV-ARCH-001 | ADR 的创建、审批、状态机和归档规则 |
| [architecture-review-policy.md](architecture-review-policy.md) | GOV-ARCH-002 | 架构评审门控——什么变更必须评审、否决条件 |
| [architecture-versioning-policy.md](architecture-versioning-policy.md) | GOV-ARCH-003 | 架构文档版本号规则、变更日志要求 |
| [ctr-injection-rules.yaml](ctr-injection-rules.yaml) | GOV-ARC-CTR-001 | CTR 注入规则 |
| [system-qualification-standard.md](system-qualification-standard.md) | GOV-ARCH-004 | 系统资质标准 |
| [gate-strategy-standard.md](gate-strategy-standard.md) | GOV-ARCH-006 | 5 级门禁策略——KMS 知识管道门禁体系（Ingest/Triage/Evaluate/Activate/Extract）|
| [phase-transition-protocol.md](phase-transition-protocol.md) | GOV-ARCH-005 | Phase 过渡双门协议——退出-准入门条件与自动化校验 |

---

## §3 依赖关系速览

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

## §4 对 AI 的使用指引

每个新 AI session 进入本目录后，应按以下顺序建立认知：

1. **先读本文件**（你正在读的这个）——了解全貌
2. **再读 GOV-ARCH-001**（adr-protocol.md）——理解 ADR 是什么、怎么管理
3. **按需读取**：
   - 如果任务是"审查架构变更"→ 读 GOV-ARCH-002（review-gate）
   - 如果任务是"给架构文档定版本号"→ 读 GOV-ARCH-003（versioning）
   - 如果任务是"KMS 管道门禁"→ 读 GOV-ARCH-006（gate-strategy）
   - 如果任务是"Phase 过渡"→ 读 GOV-ARCH-005（phase-transition-protocol）

所有文件均标记 `ai_autonomy: human_gated` —— AI 可以读取和应用这些规则，但**不得单方面修改**。任何修改必须由 Owner 审批。

**关键背景**：ADR 系统已于 2026-04-27 冻结（ADR-0001~ADR-0041 归入冻结区）。新 ADR 编号从 0042 开始，由本目录的 GOV-ARCH-001 管辖。
