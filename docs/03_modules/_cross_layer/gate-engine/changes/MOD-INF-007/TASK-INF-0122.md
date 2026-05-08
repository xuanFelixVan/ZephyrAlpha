---
task_id: TASK-INF-0122
status: planned
priority: P1
severity: high
module_id: MOD-INF-007
phase: 1
category: integration
effort_estimated: 3h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §15
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\orchestration\orchestrator.py
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
acceptance_criteria:
  - "AC1: Orchestrator集成→task run 前 GateEngine.evaluate_all(G0-G7)→所有执行入口路径被门控覆盖"
  - "AC2: KMS Gate G1-G5→在BlueprintDecomposer分解蓝图前执行→确保决策治理"
  - "AC3: Script Runner→task run中调用后G6 Artifact验证产出"
  - "AC4: CLI工具→gate-health dashboard可查看实时门控状态"
rollback_instructions:
  - "回退集成点：移除Orchestrator中gate调用 / BlueprintDecomposer中KMS gate禁用 / 脚本run不调用G6"
created_at: 2026-05-06T23:56:00Z
updated_at: 2026-05-06T23:56:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
  - TASK-INF-0102
  - TASK-INF-0115
blocked_by: [TASK-INF-0101, TASK-INF-0102, TASK-INF-0115]
blocks: []
tags: [gate-engine, integration, orchestrator, blueprint-decomposer, script-runner]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 基于 blueprint.md §15 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§15 集成目标"]
  keywords: [integration, target, orchestrator, decomposer, runner, CLI]
  ai_reads_for_inference: true
---

# TASK-INF-0122: 集成目标实现

## 背景

blueprint.md §15 定义了 gate-engine 的 4 个集成接入点：Orchestrator、BlueprintDecomposer、ScriptRunner、CLI。本卡完成各接入点对接。

## 实施

1. **Orchestrator**：在 `task.run()` 前置 `GateEngine.evaluate_all(G0-G7)`
2. **BlueprintDecomposer**：在 `decompose()` 前置 `KMSGate.evaluate(G1-G5)`
3. **ScriptRunner**：在脚本执行完成后 `G6ArtifactGate.check()`
4. **CLI**：`gate-health` 命令 → `GateHealthDashboard.render()`

## 验收

见 AC1-AC4.
