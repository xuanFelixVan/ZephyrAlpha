---
module_id: KE-212
status: active
title: 2.6 一致性约束
category: documentation
ttl: permanent
---

# 2.6 一致性约束

2.6 一致性约束

> 以下约束确保 frontmatter 各字段之间不矛盾。AI 写 frontmatter 时必须逐项检查。

| # | 约束 | 说明 |
|---|------|------|
| 1 | `stability: frozen` → `ai_autonomy: immutable_core` | 冻结文件 AI 不可修改 |
| 2 | `stability: volatile` → `ai_autonomy` ≠ `immutable_core` | 易变文件不可能是不可修改的 |
| 3 | `doc_type: policy` → `rule_form: declarative` | policy 必须是声明式 |
| 4 | `doc_type: standard` → `rule_form: declarative` | standard 必须是声明式 |
| 5 | `doc_type: operational_rule` → `rule_form: procedural` | operational_rule 必须是过程式 |
| 6 | `doc_type: register` → `rule_form: data` | register 必须是数据形式 |
| 7 | `doc_type: template` → `rule_form: structural` | template 必须是结构形式 |
| 8 | `doc_type: adr` → `rule_form: declarative` | ADR 是声明式决策记录（对标 Nygard ADR 原始定义） |
| 9 | `doc_type: blueprint` → `rule_form: structural` | blueprint 是结构化设计规范（对标 TOGAF Architecture Definition Document） |
| 10 | `doc_type: construction_plan` → `rule_form: structural` | construction_plan 是结构化执行计划（对标 ITIL Change Enablement Plan） |
| 11 | `doc_type: roadmap` → `rule_form: declarative` | roadmap 是声明式方向规划，AI 不执行 roadmap 本身 |

> **架构公民原则（避免误判）**：
> - 约束 #1 是单向的（`frozen` → `immutable_core`），其**逆面不成立**：`stability: stable` + `ai_autonomy: immutable_core` 是合法组合（如 PS-STD-003——稳定但 AI 不可修改的核心规则）
> - `stability` 描述文件的"内容变更频率"，`ai_autonomy` 描述"谁有权改"——两者正交不耦合
> - 合法映射光谱：
>   - `frozen` → `immutable_core`（强制）
>   - `stable` → `immutable_core` 或 `human_gated`（均合法）
>   - `evolving` → `human_gated` 或 `ai_modifiable`（均合法）
>   - `volatile` → 不能是 `immutable_core`（约束 #2）
