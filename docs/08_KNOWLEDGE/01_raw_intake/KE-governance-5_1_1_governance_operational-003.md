---
module_id: KE-governance-5_1_1_governance_operational-003
title: 5.1.1 governance/operational 边界判据
category: governance
---

# 5.1.1 governance/operational 边界判据

5.1.1 governance/operational 边界判据

> **这是 `01_policies_and_standards/` 内部 governance/ 和 operational/ 的唯一判据。**
> 所有子目录准入条件都从这个判据推导。

**判据定义**：

| 类型 | 特征 | 关键词 | 归属 |
|------|------|--------|------|
| **声明式** | 描述"什么是对的/错的"，不描述"怎么做" | 必须、禁止、不得、允许、要求 | `governance/` |
| **过程式** | 描述"怎么做"，按步骤执行 | 步骤、流程、检查清单、操作手册 | `operational/` |

**判据测试**：问一个问题——**"这个文件是在定义规则，还是在描述执行步骤？"**

| 答案 | 归属 | 例子 |
|------|------|------|
| 定义规则 → 声明式 | `governance/` | "所有 API 密钥必须存储在环境变量中" |
| 描述步骤 → 过程式 | `operational/` | "Step 1: 检查 .env → Step 2: 验证密钥格式" |

**边界案例判例表**：

| 文件 | 表面看 | 实际是 | 归属 | 理由 |
|------|--------|--------|------|------|
| module-injection-rules.yaml | YAML 配置 | **声明式** | governance/module/ | 定义"模块注入前必须满足的 6 条铁律"，不描述执行步骤 |
| ai-behavior-iron-policy.md | "AI行为铁律" | **声明式** | governance/module/ | 定义"AI 模型在任何操作中必须遵守的 7 条行为铁律"，不描述执行步骤 |
| vibe-coding-session-state-runbook.md | "状态机" | **过程式** | operational/vibe_coding/ | 描述 session 状态转换流程 |
| vibe-coding-gate-checklist.md | "可验证性" | **声明式** | operational/vibe_coding（保留） | 定义"规则必须可验证"的约束，但与 vibe coding 操作紧密耦合，按耦合豁免保留 |
| pre-commit-simplification-plan.md | "plan" | **过程式** | operational/devops/ | 描述 pre-commit 配置的简化执行步骤 |
| file-operation-safety-policy.md | "gate" | **声明式** | governance/document/ | 定义"文件操作前必须通过的安全检查"，是约束不是步骤 |

**混合内容处理原则**：

| 原则 | 说明 |
|------|------|
| **看主体** | 文件 70% 以上内容是声明式 → governance/；70% 以上是过程式 → operational/ |
| **看意图** | 文件的核心目的是"定规矩"还是"教操作"？ |
| **耦合豁免** | 如果声明式内容与某个 operational 子域紧密耦合，允许留在 operational/，但 frontmatter 必须标注 `rule_form: declarative` |
