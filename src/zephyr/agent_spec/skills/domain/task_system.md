---

skill_id: SKILL-DOM-TSK-001
name: task-system
description: "Task system full chain — draft→blueprint→TaskCard→dual-pipeline→script-system. Covers 62-field TaskCard model, BlueprintDecomposer, TaskRepo CRUD+state machine, PipelineOrchestrator dispatch, G7 gate validation."
allowed-tools: [Read, Write, Grep, SearchCodebase, RunCommand]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-08
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
blueprint_id: MOD-INF-019
---


# Domain Skill: Task System

## CRITICAL Rules

1. Every task MUST have a valid TaskCard before pipeline dispatch
2. Task state transitions MUST follow the state machine (draft→ready→in_progress→completed→closed)
3. Pipeline dispatch requires G7 gate validation pass
4. TaskCard fields MUST conform to the 62-field schema
5. Blueprint decomposition MUST produce actionable TaskCards with batch_id assignment
6. Script system output MUST reference originating TaskCard

## Core Operations

- TaskCard creation with 62-field schema validation
- Blueprint decomposition into actionable subtasks
- Task state machine transitions (draft→ready→in_progress→completed→closed)
- TaskRepo CRUD operations with persistence
- PipelineOrchestrator dispatch with G7 gate check
- Batch_id assignment for cross-session continuity
- Task dependency graph construction and cycle detection

## Unique Constraints

- No task can skip a state in the state machine
- G7 gate check is non-bypassable for pipeline dispatch
- TaskCard must reference a valid blueprint
- Dependency cycles MUST be detected and rejected
- Completed tasks are immutable (no field edits)

## Common Error Patterns

- TaskCard created without required 62 fields
- State machine violation (e.g., skipping from draft to completed)
- Pipeline dispatch without G7 gate pass
- Dependency cycle not detected
- Orphan task (no batch_id, no blueprint reference)

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| TASKCARD_FIELD_COUNT | 62 | Required fields |
| STATE_MACHINE_STEPS | 5 | draft→ready→in_progress→completed→closed |
| MAX_TASK_DEPTH | 10 | Max subtask nesting depth |
| GATE_REQUIRED_BEFORE_DISPATCH | G7 | Pipeline gate |