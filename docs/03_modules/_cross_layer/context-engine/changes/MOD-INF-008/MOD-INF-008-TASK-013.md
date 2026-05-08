---
task_id: "MOD-INF-008-TASK-013"
task_title: "深度对标分析落地 — §13 工业对标：Anthropic/Google/Cursor/Windsurf/VibeCoding"
module_id: "MOD-INF-008"
blueprint_section: "§13 深度对标分析 (§13.1-§13.4)"
status: "backlog"
priority: "P1"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "ANALYSIS"
estimated_effort_hours: 3
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-INF-008-TASK-008"
    why: "对标缺口需要决策落地"
  - task_id: "MOD-INF-008-TASK-014"
    why: "beta 补齐是对标落地的施工阶段"
parent_task_id: null
child_task_ids: ["MOD-INF-008-TASK-014"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\benchmarking_gaps.md"
tags: ["context-engine", "benchmarking", "industry-analysis", "gap-analysis"]
acceptance_criteria:
  - "AC-001: §13.1 Anthropic 5 项实践逐条对照：Context Rot/XML Tag/Multi-Turn Curation/System Prompt 版本化/Hybrid Approach"
  - "AC-002: §13.2 Google Hot/Warm/Cold 缓存分级对照：缺失 → 标记为需实现"
  - "AC-003: §13.3 氛围编程社区 5 大模式对照：Memory Bank/Cursor Rules/Windsurf/Spec Coding/Skill 展开"
  - "AC-004: §13.4 对标总结表 8 项差距分析：逐项标记是否已通过后续 beta 补齐"
  - "AC-005: 生成 benchmarking_gaps.md 记录差距 + 对应的 task_id"
rollback_instructions: "删除 benchmarking_gaps.md"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §13"
  required_standards: []
  required_templates: []
  required_references: []
---
# MOD-INF-008-TASK-013: 深度对标分析落地

## 1. Purpose

将 §13 中的工业对标分析转化为可追踪的差距文档，确保每条对标缺口都有对应的任务卡负责补齐。

## 2. Anthropic Context Engineering (§13.1)

| 实践 | 我们有？ | 差距 | 对应任务 |
|------|:---:|------|---------|
| Context Rot 模型 | ❌ | 有预算追踪，无注意力衰减模型 | TASK-014 (beta a) |
| XML Tag 强制分区 | ❌ | Flat concat 注入 | TASK-005 (四层注入) |
| Multi-Turn Curation Loop | ❌ | 单次 build→inject | TASK-014 (beta b) |
| System Prompt 版本化 | ❌ | 未追踪 prompt version | TASK-013 (本任务审计标记) |
| Hybrid Approach | 部分 | context_rules_v1.yaml 存在但未集成 | TASK-010 |

## 3. Google Context Caching (§13.2)

| 层级 | 特征 | 我们有？ | 对应任务 |
|------|------|:---:|---------|
| Hot | 同 session 高频复用 | ❌ | AP4 缓存 |
| Warm | 跨 session 共享 60min | ❌ | TASK-014 (beta a eviction) |
| Cold | 长期存储 permanent | ✅ | VMS 全量 KE |

## 4. Vibe Coding Community Patterns (§13.3)

| 模式 | 我们有？ | 差距 |
|------|:---:|------|
| Memory Bank | ❌ | 蓝图 ≠ AI 工作记忆 |
| Cursor Rules | 部分 | depends_on 静态 |
| Windsurf Freshness Decay | ❌ | 有字段，无计算 |
| Spec Coding | 部分 | 规约驱动方向正确 |
| Skill 展开 | ❌ | 无渐进式上下文 |

## 5. Acceptance Criteria

- benchmarking_gaps.md 包含 §13.4 中所有 8 项差距
- 每条差距有对应的 task_id 引用
- "有字段，无计算" 类差距标记为 P1
