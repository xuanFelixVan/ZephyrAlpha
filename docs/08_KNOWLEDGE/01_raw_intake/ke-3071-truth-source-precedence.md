---
module_id: KE-2970
status: active
title: 零之零、真源优先级宪章（Truth Source Precedence）
category: module_blueprint
---

# 零之零、真源优先级宪章（Truth Source Precedence）

零之零、真源优先级宪章（Truth Source Precedence）

> **级别：P0 硬性约束。** 违反此优先级链的任何 AI agent 行为均构成架构违规（AP1）。

当多个文档源对同一事实给出不同定义时，按以下顺序裁决——**前一级别总是覆盖后一**：

| 优先级 | 文档源 | 裁决范围 | 说明 |
|:---:|------|------|------|
| **Tier 0** | 本蓝图（MOD-MASTER-001） | 跨系统集成契约 | 所有 CT-* 契约的最终权威——inter-system 的"how to connect"以我为准 |
| **Tier 1** | `architecture-model/layers/{module}.yaml` | 单模块结构定义 | 模块边界、组件清单、依赖声明的原子真源——intra-module 的"what exists"以此为准 |
| **Tier 2** | `docs/03_modules/{layer}/blueprint.md` | 模块级实现指引 | 模块的"how to implement"由蓝图指引——但不得覆盖 Tier 0/1 的结构定义 |
| **Tier 3** | `docs/01_policies_and_standards/` | 通用规范与策略 | 编码规范、命名约定、流程定义——仅在没有 Tier 0-2 覆盖时适用 |
| **Tier 4** | 实际代码 | 运行时现实 | 代码是执行真相——但若代码与 Tier 0-3 矛盾，代码为 bug，需修复代码而非文档 |

**冲突裁决流程**：
1. AI agent 发现不一致 → 按此表确定权威源
2. 以权威源为准执行
3. 同时创建一个 `Finding（severity=LOW, type=DOC_INCONSISTENCY）` 记录不一致
4. 不得自行修改权威源来"修复"不一致

**反模式（禁止）**：
- ❌ "代码和蓝图不一致，我以代码为准"（除非代码是 Tier 4 且无 Tier 0-3 覆盖）
- ❌ "architecture-model 说 X，蓝图说 Y，我选我觉得合理的"
- ❌ "我发现不一致就顺便改了蓝图"（必须先创建 Finding）

---
---
