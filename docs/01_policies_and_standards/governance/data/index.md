---
module_id: GOV-DATA-000
title: "数据治理目录索引"
doc_type: index
status: active
version: "1.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
ai_autonomy: human_gated
created_by: human_plus_agent
date: "2026-05-01"
valid_from: "2026-05-01"
ttl: permanent
summary: "governance/data/ 目录的导航索引。声明本目录的责任范围、文件清单及每文件的核心职责。新 AI session 进入本目录时，应首先读取本文件以建立全局认知。"
tags: [index, data, governance, navigation]
depends_on:
  - target: PS-STD-001
    at: "§5.8"
    why: "metadata-registry.md 定义 GOV-DATA 模块 ID 的分配规则"
---

# 数据治理目录索引

> **module_id**: GOV-DATA-000 | **version**: 1.0.0 | **status**: active

---

## §1 本目录的责任

`governance/data/` 是 ZephyrAlpha 的**数据治理中心**。这里管的是"数据怎么才是好的、数据从哪来到哪去、数据存多久"相关的全局数据标准。

**正向责任**（本目录管的事）：
1. 数据质量标准——质量维度（完整性/准确性/时效性/一致性/唯一性）、检查规则
2. 数据血缘追溯——从数据源到消费者全链路"谁动了这个数据"
3. 数据保留策略——不同类型数据保留多久、何时删除、合规例外

**负向责任**（本目录不管的事，去对应目录找）：
- 数据的具体实现 Schema → `src/zephyr/shared/contracts/`
- AI 会话日志的格式定义 → `_registry/schemas/session-log-schema.yaml` (GOV-AI-007)（已从 governance/ai/ 迁出）
- 审计日志的格式和保留 → `governance/compliance/audit-trail-policy.md`
- 层域数据管线的具体规则 → `domains/L02_alpha_factor/` / `domains/L04_risk_management/`

---

## §2 文件清单

| 文件 | module_id | 一句话职责 |
|------|-----------|-----------|
| [data-quality-policy.md](data-quality-policy.md) | GOV-DATA-001 | 数据质量维度定义——数据必须满足的标准 |
| [data-lineage-policy.md](data-lineage-policy.md) | GOV-DATA-002 | 数据血缘追溯——关键数据从哪来到哪去必须可追踪 |
| [data-retention-policy.md](data-retention-policy.md) | GOV-DATA-003 | 数据保留期限表——不同类型数据存多久、什么时候删 |

---

## §3 依赖关系速览

```
GOV-DATA-001 (data-quality)    ← 被 GOV-DATA-002 引用：血缘依赖质量维度定义
    │
    ├── GOV-DATA-002 (data-lineage) → 引用 GOV-DATA-001 §2~§3，关键数据范围
    │
    └── GOV-DATA-003 (data-retention) → 引用 GOV-AI-007（AI会话日志保留1年）
            │
            └── 被 GOV-DATA-001 引用：数据质量检查结果的保留期限
```

跨域引用：
- `GOV-AI-007 (session-log-schema)` → `GOV-DATA-003`：AI 会话日志的保留期限（1 年）
- `GOV-CMP-002 (audit-trail)` → `GOV-DATA-003 §2`：审计数据保留期限引用

---

## §4 对 AI 的使用指引

每个新 AI session 进入本目录后，应按以下顺序建立认知：

1. **先读本文件**（你正在读的这个）——了解全貌
2. **再读 data-quality-policy.md**——理解"合格数据长什么样"（DQA-001~003）
3. **再读 data-retention-policy.md**——理解"数据存多久、什么时候删"（DRP-001~003）
4. **最后读 data-lineage-policy.md**——理解"数据从哪来的必须能说清楚"（DLG-001~003）

所有文件均标记 `ai_autonomy: human_gated` —— AI 可以读取和应用这些规则，但**不得单方面修改**。任何修改必须由 Owner 审批。

**数据保留速查**：
| 数据类型 | 保留期限 |
|---------|:---:|
| AI 会话日志 | 1 年 |
| 审计日志 | 7 年 |
| 业务交易数据 | 5 年 |
| 临时/调试数据 | 30 天 |
