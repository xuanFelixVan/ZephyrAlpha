---
task_id: TASK-INF-0120
status: planned
priority: P1
severity: medium
module_id: MOD-INF-007
phase: 1
category: audit
effort_estimated: 1h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §13
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files: []
downstream_outputs: []
acceptance_criteria:
  - "AC1: 蓝图 §13 依赖关系表（依赖模块名称+版本）与 `pyproject.toml`/`requirements.txt` 一致"
  - "AC2: context-engine、task-system、metadata-registry、orchestrator、tool_contracts.yaml 依赖路径均可访问"
  - "AC3: 依赖为 Python→部署环境 `pip install -r requirements.txt` 不报 missing"
rollback_instructions: "本卡仅验证，无需回退"
created_at: 2026-05-06T23:54:00Z
updated_at: 2026-05-06T23:54:00Z
closed_at: null
dependencies: []
blocked_by: []
blocks: []
tags: [gate-engine, dependency-validation, pyproject, pip]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 基于 blueprint.md §13 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§13 依赖关系"]
  keywords: [dependency, validate, pip, pyproject, requirements]
  ai_reads_for_inference: true
---

# TASK-INF-0120: 依赖关系验证

## 背景

blueprint.md §13 列出 gate-engine 的外部依赖。本卡验证这些依赖在生产环境中可获取。

## 实施

比对 §13 表中的模块名称与 `pyproject.toml` 和实际代码库中的 import 语句。

## 验收

AC1-AC3。
