---
task_id: "MOD-INF-008-TASK-014"
task_title: "beta a-c 一期补齐 — ContextRot + Provenance + Eviction + Curation + MemoryBank"
module_id: "MOD-INF-008"
blueprint_section: "§15 beta 补齐计划 (§15.1 beta a, §15.2 beta b, §15.3 beta c)"
status: "backlog"
priority: "P0"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "CODE_GEN"
estimated_effort_hours: 18
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-INF-008-TASK-003"
    why: "beta a context_rot_model 扩展 Compress 阶段"
  - task_id: "MOD-INF-008-TASK-005"
    why: "beta a provenance 扩展 Inject 阶段"
  - task_id: "MOD-INF-008-TASK-002"
    why: "beta b curation_loop 扩展 Build 阶段"
parent_task_id: "MOD-INF-008-TASK-001"
child_task_ids:
  - "MOD-INF-008-TASK-014A"
  - "MOD-INF-008-TASK-014B"
  - "MOD-INF-008-TASK-014C"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_budget_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_injector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_assembler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\doc_compressor.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_rot_model.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_evictor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\curation_loop.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_evaluator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\memory_bank.py"
  - "D:\\ZephyrAlpha\\tests\\test_context_rot_model.py"
  - "D:\\ZephyrAlpha\\tests\\test_context_evictor.py"
tags: ["context-engine", "beta-a", "beta-b", "beta-c", "context-rot", "provenance", "eviction", "curation-loop", "memory-bank"]
acceptance_criteria:
  - "AC-001: beta a: context_rot_model.py — n² attention 衰减数学模型实现 (DD7)，~200 行"
  - "AC-002: beta a: context_evictor.py — 三维逐出排序 (优先级×新鲜度×相关性) 实现 (DD9)，~250 行"
  - "AC-003: beta a: context_injector.py 升级 — 添加 provenance 溯源字段 (DD8)"
  - "AC-004: beta a: context_budget_tracker.py 升级 — 接入动态阈值"
  - "AC-005: beta a: 含 18 测试 test_context_rot_model.py + 18 测试 test_context_evictor.py"
  - "AC-006: beta b: curation_loop.py — per-turn curation 策展实现 (DD10)，~300 行"
  - "AC-007: beta b: context_evaluator.py — AI 引用率 = 上下文效率计算，~200 行"
  - "AC-008: beta b: context_assembler 升级 — 单次→per-turn；CompressionPolicy 加 efficiency_threshold"
  - "AC-009: beta c: memory_bank.py — AI 读写 6 个结构化 .md 持久上下文，~350 行"
  - "AC-010: beta c: context_injector 升级 — XML 分区注入；budget_tracker 成本感知"
rollback_instructions: "删除 beta a-c 所有新增文件和升级代码，恢复被修改文件至 beta 前版本"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §15, §15.1-§15.3"
  required_standards: []
  required_templates: []
  required_references:
    - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_context_engine.yaml"
---
# MOD-INF-008-TASK-014: beta a-c 补齐

## 1. Purpose

实现 §15 中定义的三期 beta 补齐计划，弥补 §13 和 §14 中识别的缺口，将 Context Engine 从 phase_1_partial 推进到 beta 完整。

## 2. beta a — 核心缺失 (ContextRot + Provenance + Eviction)

| 新增文件 | 职责 | 约行数 |
|---|---|---|
| context_rot_model.py | n² attention 衰减数学模型 (幂函数 n^{-k}) | ~200 |
| context_evictor.py | 三维逐出：优先级×新鲜度×相关性 | ~250 |

升级：context_injector.py 加 provenance、context_budget_tracker.py 接入动态阈值

## 3. beta b — 多轮能力 (Curation Loop + Effectiveness Eval)

| 新增文件 | 职责 | 约行数 |
|---|---|---|
| curation_loop.py | per-turn curation 策展—不重复注入 | ~300 |
| context_evaluator.py | AI 引用率 = 上下文效率 | ~200 |

升级：context_assembler 单次→per-turn、CompressionPolicy 加 efficiency_threshold

## 4. beta c — 持久化+结构化 (Memory Bank + XML Partitioning)

| 新增文件 | 职责 | 约行数 |
|---|---|---|
| memory_bank.py | AI 读写 6 个结构化 .md | ~350 |

升级：context_injector XML 分区、budget_tracker 成本感知

## 5. Test Requirements

| 文件 | 测试数 | 说明 |
|------|:---:|------|
| test_context_rot_model.py | 18 | beta a |
| test_context_evictor.py | 18 | beta a |

## 6. Acceptance Criteria

- context_rot_model.compute_decay(n_tokens) 返回正确的 n^{-k} 衰减值
- context_evictor.evict(context_items, budget) 按三维排序返回需要逐出的 items
- curation_loop 不重复注入已注入的 KE
- context_evaluator 可计算 Agent 实际引用了多少注入的 KE
- memory_bank 可读写 6 类结构化 .md
- 36 个测试全部通过
