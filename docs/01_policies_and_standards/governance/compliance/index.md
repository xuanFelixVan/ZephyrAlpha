---
module_id: GOV-CMP-000
title: "合规治理目录索引"
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
summary: "governance/compliance/ 目录的导航索引。声明本目录的责任范围、文件清单及每文件的核心职责。新 AI session 进入本目录时，应首先读取本文件以建立全局认知。"
tags: [index, compliance, governance, navigation]
depends_on:
  - target: PS-STD-001
    at: "§5.8"
    why: "metadata-registry.md 定义 GOV-CMP 模块 ID 的分配规则"
  - target: GOV-DOC-002
    at: "§1"
    why: "directory-structure-standard.md 定义本目录的物理路径规范"
  - target: GOV-IDX-001
    at: "§1.1"
    why: "治理域总索引定义 compliance/ 的职责——监管分类、审计追踪"
---

# 合规治理目录索引

> **module_id**: GOV-CMP-000 | **version**: 1.0.0 | **status**: active

---

## §1 本目录的责任

`governance/compliance/` 是 ZephyrAlpha 的**合规治理中心**。这里管的是"系统怎么才能满足监管要求——哪些操作必须留痕、不同市场适用哪些监管框架"。

**正向责任**（本目录管的事）：
1. 监管框架分类——不同市场/管辖区适用哪些规则、合规检查维度
2. 审计追踪——什么操作必须留痕、审计日志格式、保留期限、访问权限

**负向责任**（本目录不管的事，去对应目录找）：
- 安全防护机制（密钥/访问/事件）→ `governance/security/` ——合规管"证"，安全管"锁"
- 数据保留的具体期限 → `governance/data/data-retention-policy.md` ——合规引用它的期限
- 审计日志的技术实现 → `src/zephyr/` / `scripts/governance/`
- 具体合规检查的执行步骤 → `operational/`

---

## §2 文件清单

| 文件 | module_id | 一句话职责 |
|------|-----------|-----------|
| [regulatory-taxonomy-policy.md](regulatory-taxonomy-policy.md) | GOV-CMP-001 | 监管框架分类——各市场/管辖区适用规则 + 合规检查维度 |
| [audit-trail-policy.md](audit-trail-policy.md) | GOV-CMP-002 | 审计追踪——6 类必须审计操作、日志格式、保留、访问 |
| [audit-protocol.md](audit-protocol.md) | GOV-CMP-003 | 治理审计执行协议——审计类型、范围、规则、工具、频率 |

---

## §3 依赖关系速览

```
GOV-CMP-001 (regulatory-taxonomy)   ← 被 GOV-CMP-002 引用（合规检查覆盖所有维度）
    │
    ├── GOV-CMP-002 (audit-trail)    → 汇总点
            │
            ├── → GOV-DATA-003 §2：审计日志保留7年（引用数据保留期限）
            └── → GOV-SEC-002 §2~§4：审计日志访问受限（引用角色和权限矩阵）
```

跨域引用链：
- `compliance/audit-trail → data/retention → _registry/schemas/session-log-schema`（CMP → DATA → AI，3 域链）
- `compliance/audit-trail → security/access-control`（CMP → SEC）

CMP-001 与 CMP-002 的关系：
- CMP-001 定义"要满足哪些监管框架"——为 CMP-002 提供合规检查的目标
- CMP-002 定义"怎么留痕以满足合规"——实现 CMP-001 要求的操作可追溯性

---

## §4 对 AI 的使用指引

每个新 AI session 进入本目录后，应按以下顺序建立认知：

1. **先读本文件**（你正在读的这个）——了解全貌
2. **再读 regulatory-taxonomy-policy.md**——理解"不同市场受谁管"
3. **最后读 audit-trail-policy.md**——理解"什么操作必须留痕、审计日志怎么存"

所有文件均标记 `ai_autonomy: human_gated` —— AI 可以读取和应用这些规则，但**不得单方面修改**。任何修改必须由 Owner 审批。

**关键边界——安全 vs 合规不重叠**：
| 维度 | security/ | compliance/ |
|------|----------|------------|
| 核心关注 | 保护机制（防攻击/防泄露） | 举证能力（能证明合规） |
| 对标 | ISO 27001 Annex A | NIST 800-53 AU 控制族 |
| 举例 | "密钥不能明文存储" | "密钥操作必须可审计" |

> **大白话**：安全管"锁门关窗"（不让坏人进来），合规管"装监控"（谁来过留下证据）。两个域互相引用但不重复定义。
