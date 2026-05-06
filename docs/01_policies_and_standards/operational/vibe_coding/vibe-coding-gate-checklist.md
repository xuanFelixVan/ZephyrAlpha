---
module_id: OPS-VC-005
title: Vibe Coding 会话门禁检查清单
doc_type: operational_rule
status: active
version: "0.3.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-02"
ttl: permanent
summary: "Vibe Coding 会话开始前必须完成的检查清单——上下文加载、规则确认、安全检查。任何一项未通过，禁止开始操作。scaffold MVP 后已从纯手动升级为半自动化：v0.3.0 重新校准自动化覆盖映射——GATE 覆盖 = 代码结构合规性校验，不等同于 AI 已阅读对应政策文档。A1/A2 无法脚本化，D1 无 GATE 覆盖。"
tags: [vibe-coding, gate, checklist, operational]
rule_form: procedural
scope: global
stability: evolving
verifiability: inspection
automated_by: MOD-INF-005
depends_on:
  - target: PS-STD-003
    at: "§2"
    why: "行为边界——绝对禁止操作清单"
---

# Vibe Coding 会话门禁检查清单

> module_id: OPS-VC-005 | version: 0.3.0 | status: active | layer: cross_layer

## 1. 目的

本检查清单定义 Vibe Coding 会话开始前必须完成的检查项。任何一项未通过，禁止开始操作。

**自动化状态（v0.3.0）**：重新校准自动化覆盖映射。"✅ GATE-XX" = 该 GATE 在校验对应领域的文件结构/格式合规性（如 UTF-8 编码、frontmatter 字段、目录位置）。"⚠️" = GATE 部分覆盖——结构校验通过，但 AI 仍需确认已读取对应政策文档。A1/A2/D1 无法脚本化，仍需 AI 自检。

## 2. 检查清单

### A. 上下文加载（3 项）| 自动化：1/3

| # | 检查项 | 通过条件 | 未通过处理 | 自动化 |
|---|--------|---------|-----------|:---:|
| A1 | 已读取当前 Phase | 按 AGENTS.md §8 执行 | 读取 onboarding 文件 | ❌ 人工 |
| A2 | 已读取施工图 | 知道本次 session 要执行哪些步骤 | 读取对应 Phase 的施工图 | ❌ 人工 |
| A3 | 已读取相关 SSoT 文件 | 施工图"必备链接"中的所有文件已读取 | 逐个读取必备链接中的文件 | ✅ GATE-16 |

### B. 规则确认（4 项）| 自动化：4/4

| # | 检查项 | 通过条件 | 未通过处理 | 自动化 |
|---|--------|---------|-----------|:---:|
| B1 | 行为边界已确认 | 已读取 PS-STD-003，知道哪些操作绝对禁止 | 读取 behavior-boundaries-standard.md | ✅ GATE-14 + GATE-16 |
| B2 | 幻觉自检已通过 | 按幻觉自检流程执行 | 读取 ai-hallucination-self-check-policy.md | ✅ GATE-15 |
| B3 | 双编辑器规则已确认 | 知道当前使用哪个编辑器、哪些文件可编辑 | 读取 dual-editor-collaboration-policy.md | ⚠️ GATE-16（结构合规） |

### C. 安全检查（3 项）| 自动化：3/3

| # | 检查项 | 通过条件 | 未通过处理 | 自动化 |
|---|--------|---------|-----------|:---:|
| C1 | 编码安全已确认 | 所有文件 UTF-8 编码 | 读取 GOV-DOC-005 | ✅ GATE-16 |
| C2 | 文件操作安全已确认 | 知道删除/移动文件的安全门禁 | 读取 GOV-DOC-007 | ✅ GATE-16 |
| C3 | 密钥管理已确认 | 不在代码中硬编码密钥 | 读取 GOV-SEC-001 | ✅ GATE-16 |

### D. 环境确认（2 项）| 自动化：2/2

| # | 检查项 | 通过条件 | 未通过处理 | 自动化 |
|---|--------|---------|-----------|:---:|
| D1 | 当前环境已确认 | 知道当前是 dev 还是 prod 环境 | 参见 GOV-AI-001 §7.1 | ❌ 人工 |
| D2 | 权限模式已确认 | 知道当前环境的 AI 自治权限 | 参见 GOV-AI-001 §7.2 | ✅ GATE-14 |

## 3. 检查结果记录

每次会话开始时，在 Session Log 中记录门禁检查结果：

```yaml
gate_check:
  A1: pass  # 上下文加载
  A2: pass
  A3: pass
  B1: pass  # 规则确认
  B2: pass
  B3: pass
  B4: pass
  C1: pass  # 安全检查
  C2: pass
  C3: pass
  D1: pass  # 环境确认
  D2: pass
```

任何一项为 `fail` 时，必须先修复再开始操作。
