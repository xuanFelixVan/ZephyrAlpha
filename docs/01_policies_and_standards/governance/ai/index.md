---
module_id: GOV-AI-000
title: "AI 治理目录索引"
doc_type: index
status: active
version: "2.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
ai_autonomy: human_gated
created_by: human_plus_agent
date: "2026-05-01"
valid_from: "2026-05-01"
ttl: permanent
summary: "governance/ai/ 目录的导航索引。声明本目录的责任范围、文件清单及每文件的核心职责。新 AI session 进入本目录时，应首先读取本文件以建立全局认知。v2.0.0：ai-onboarding-guide.md 废除（被 AGENTS.md §8 取代），架构图更新。"
tags: [index, ai, governance, navigation]
depends_on:
  - target: PS-STD-001
    at: "§5.8"
    why: "metadata-registry.md 定义 GOV-AI 模块 ID 的分配规则"
---

# AI 治理目录索引

> **module_id**: GOV-AI-000 | **version**: 2.0.0 | **status**: active

---

## §1 本目录的责任

`governance/ai/` 是 ZephyrAlpha 的**AI 治理中心**。这里管的是一切与"AI 能做什么、不能做什么、怎么检查自己做错了、怎么协同、怎么花钱"相关的规则。

**正向责任**（本目录管的事）：
1. AI 自治权限注册表——AI 对每个操作的自主权级别
2. AI 幻觉自检机制——AI 如何检测和防止幻觉（手动自检 GOV-AI-003 + 自动检测 GOV-AI-009）
3. AI 冷启动流程—— inv: AI session 的规则加载策略（由 AGENTS.md §8 定义）
4. AI 运营预算——Token 成本控制和预算上限
5. 双编辑器协同规则——防止 Cursor 和 Trae 同时编辑同一文件
6. 模型能力契约——当前 AI 模型的能力边界定义
7. Session Log 格式——会话记录的标准化 Schema
8. Session 交接协议——跨 Session 的 Handoff/Carryover 流程（handoff-protocol.md）

**负向责任**（本目录不管的事，去对应目录找）：
- AI 行为铁律（绝对禁止的操作）→ `governance/module/ai-behavior-iron-policy.md`
- Vibe Coding 上下文规则 → `operational/vibe_coding/`
- 元规则定义 → `meta/`

---

## §2 文件清单

| 文件 | module_id | 一句话职责 |
|------|-----------|-----------|
| [ai-autonomy-authority-registry.md](../../_registry/catalogs/ai-autonomy-authority-registry.md) | GOV-AI-001 | AI 对每个操作的自主权限级别注册表（已迁至 _registry/catalogs/） |
| [ai-hallucination-self-check-policy.md](../../governance/ai/ai-hallucination-self-check-policy.md) | GOV-AI-003 | AI 检测和防止幻觉的自我检查机制 |
| [dual-editor-collaboration-policy.md](../../governance/ai/dual-editor-collaboration-policy.md) | GOV-AI-004 | Cursor 和 Trae 双编辑器协同防冲突规则 |
| [model-capability-contract.yaml](../../_registry/contracts/model-capability-contract.yaml) | GOV-AI-006 | 当前 AI 模型的能力边界契约（已迁至 _registry/contracts/） |
| [session-log-schema.yaml](../../_registry/schemas/session-log-schema.yaml) | GOV-AI-007 | Session Log 的标准化 YAML Schema（已迁至 _registry/schemas/） |
| [handoff-protocol.md](../../governance/ai/handoff-protocol.md) | GOV-AI-008 | Session 交接包格式和 5 项反腐败校验（原 GOV-TASK-003，2026-05-01 迁入） |
| [model-routing-policy.md](../../governance/ai/model-routing-policy.md) | GOV-AI-002 | AI 模型路由策略——按任务类型选择最优模型 |
| [ai-hallucination-detection-rules.md](../../governance/ai/ai-hallucination-detection-rules.md) | GOV-AI-009 | 10 条 AI 代码产出物的自动化幻觉检测规则（与 GOV-AI-003 互补） |

---

## §3 依赖关系速览

```
GOV-AI-001 (autonomy)           ← 权限真源，被 security/access-control 引用
    └── GOV-AI-008 (handoff)      ← 依赖 autonomy 决定交接包可包含什么
GOV-AI-003 (hallucination)        ← 独立：手动自检清单
GOV-AI-009 (hallucination-detection) ← 依赖 GOV-AI-003 + architecture-contract.yaml
GOV-AI-004 (dual-editor)          ← 独立：协同规则不与权限耦合
GOV-AI-006 (model-capability)     ← 独立：模型能力定义
GOV-AI-007 (session-log-schema)   ← 被 handoff-protocol.md 引用
```

---

## §4 对 AI 的使用指引

每个新 AI session 进入本目录后，应按以下顺序建立认知：

1. **先读本文件**（你正在读的这个）——了解全貌
2. **再读 AGENTS.md §8**——理解冷启动流程和规则加载策略
3. **再读 ai-autonomy-authority-registry.md**（现位于 `_registry/catalogs/`）——明确自己什么能做什么不能做
4. **按需读取**其余文件

所有文件均标记 `ai_autonomy: human_gated`——AI 可以读取和应用这些规则，但**不得单方面修改**。任何修改必须由 Owner 审批。

---
