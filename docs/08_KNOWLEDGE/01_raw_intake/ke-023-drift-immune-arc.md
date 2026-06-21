---
module_id: KE-023----------drift-immune-arc-006
status: active
title: 6.15 漂移免疫架构原则（Drift-Immune Architecture Mandate）
category: agent_instruction
---

# 6.15 漂移免疫架构原则（Drift-Immune Architecture Mandate）

6.15 漂移免疫架构原则（Drift-Immune Architecture Mandate）

> **v1.0.0（2026-05-03）**：触发条件——任何涉及 SSoT/派生/索引/引用链的治理操作。本节是 §6.9~§6.13 的**元防御层**——前面五节定义"应该怎么做"，本节定义"如何确保做到了"。对标 K8s Admission Controller（准入控制器——规则不执行 = 规则不存在）/ OpenAPI CI drift guard（spec:lint + spec:check——不一致就合不进去）/ Terraform drift detection（exit code 2 = drift——漂移立刻被发现）/ Vibe Coding context engineering（建议性规则是必要条件但不是充分条件）。

**核心原则**：**写在纸上的法律对零记忆系统无效——治理必须由代码执行，不能依赖 AI 的自愿遵循。** 本项目 100% Vibe Coding AI 开发，AI 每次进入都是"新员工"（§5.1），它不会"记得"上次签的合同。因此，治理的执行层不能是 prose 规则，必须是 CI 门禁和自动派生。

- **追问到底根因分析**（2026-05-03 审计 29 项问题的根因追溯）：

  | 层级 | 问题 | 回答 |
  |:---:|------|------|
  | 症状 | 枚举漂移、索引数字错误、幽灵引用、module_id 冲突 | 表面现象 |
  | Why-1 | 为什么枚举值在 5 个文件中不一致？ | 每个文件独立硬编码了自己的枚举列表 |
  | Why-2 | 为什么每个文件独立硬编码？ | 没有派生机制——AI 只知道"这个文件需要枚举"，就在本地写了一份 |
  | Why-3 | 为什么 AI 记不住其他文件已经有了一份？ | Vibe Coding AI 上下文记忆极短（§5.1），跨 session 零记忆 |
  | Why-4 | 为什么没有 CI 门禁在漂移发生时拦截？ | 治理模型是"建议性"的——规则写在 prose 里，没有代码强制执行 |
  | **Why-5（根因）** | **为什么治理模型是建议性的？** | **项目从第一天起就依赖"AI 读规则 → AI 遵循"的模式，而不是"CI 自动检测 → CI 拦截"的模式。治理的执行层缺失** |

- **专业机构对标**：

  | 机构 | 他们的做法 | 我们的差距 | 核心洞察 |
  |------|-----------|-----------|---------|
  | K8s CRD | Schema 从 Go 类型**自动派生**（derive macro），物理上不可能手动创建不一致的 schema | vocabulary YAML → 派生文件是**手动复制** | 消除手动复制 = 消除漂移的可能 |
  | K8s CEL | CRD 内嵌声明式校验规则，API Server 写入时自动校验 | architecture-contract.yaml 有规则但**没有执行器** | 规则不执行 = 规则不存在 |
  | OpenAPI | CI 中 `spec:lint` + `spec:check`，生成类型必须匹配 spec 否则 CI 失败 | 没有 `vocabulary:check` 等价物 | CI 门禁是最低可行防御 |
  | Terraform | `terraform plan -detailed-exitcode`（exit 2 = drift），TF-Controller 持续对账 | 没有持续对账机制 | 漂移检测必须自动化和持续化 |
  | Vibe Coding | CLAUDE.md 持久记忆，context engineering > vibe coding | AGENTS.md 是持久记忆但**仅靠 AI 自愿遵循** | 建议性规则是必要条件但不是充分条件 |

- **三层防御模型**：

  ```
  ┌─────────────────────────────────────────────────────┐
  │  Level 3：自动派生（终极防御）                         │
  │  vocabulary YAML → 脚本自动生成所有派生文件              │
  │  对标：K8s derive macro、terraform-docs               │
  │  效果：物理上不可能漂移                                  │
  │  状态：📋 远期目标                                      │
  ├─────────────────────────────────────────────────────┤
  │  Level 2：CI 门禁（最低可行防御）                       │
  │  validate_enum_consistency.py → 枚举漂移检测           │
  │  validate_index_reality.py → 索引-实际对账             │
  │  validate_cross_references.py → 引用链完整性            │
  │  对标：OpenAPI spec:check、Terraform drift detection   │
  │  效果：漂移在 CI 阶段被拦截，不会累积                    │
  │  状态：📋 beta（本节定义规格，下个 session 实施）      │
  ├─────────────────────────────────────────────────────┤
  │  Level 1：建议性规则（当前防御）                         │
  │  AGENTS.md §6.9~§6.13 的 prose 规则                   │
  │  AI 读取并遵循——单次 session 内有效                     │
  │  对标：Vibe Coding CLAUDE.md 持久记忆                   │
  │  效果：减少但不能消除漂移                                │
  │  状态：✅ 已实施                                        │
  └─────────────────────────────────────────────────────┘
  ```

- **Level 2 CI 门禁规格**（beta 实施时 MUST 遵循的规格定义）：

  | 门禁脚本 |
