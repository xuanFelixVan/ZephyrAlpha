---
task_id: TASK-INF-0119
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
source_section: §12、§4
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files: []
downstream_outputs: []
acceptance_criteria:
  - "AC1: 蓝图中 §12 代码文件路径与磁盘实际文件一致→全路径存在且文件>0字节"
  - "AC2: §4 代码文件路径索引（29个文件条目）一一对应 §3.1 骨架定义"
  - "AC3: `glob src/zephyr/gates/**/*.py` 的文件计数=29（不含__pycache__）"
rollback_instructions: "无代码修改——本卡仅验证"
created_at: 2026-05-06T23:53:00Z
updated_at: 2026-05-06T23:53:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
blocked_by: [TASK-INF-0101]
blocks: []
tags: [gate-engine, path-index, verification, file-count]
version: 1.0.0
change_log: "v1.0.0 (2026-05-06): 基于 blueprint.md §12+§4 v1.4.3"
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections: ["§12 已实现代码路径索引", "§4 代码文件路径索引"]
  keywords: [code-path, index, file-count, verify, disk-exists]
  ai_reads_for_inference: true
---

# TASK-INF-0119: 代码文件路径索引验证

## 背景

blueprint.md §4和§12 都包含 gate-engine 的完整代码文件路径索引。本卡验证索引与磁盘实际一致。

## 实施

```bash
Get-ChildItem -Recurse -File D:\ZephyrAlpha\src\zephyr\gates\*.py | Measure-Object | Select-Object -ExpandProperty Count
```

返回=29（不含__pycache__）。

对 §4 表的每一条手动验证 `Test-Path $path`。

## 验收

AC1: 路径存在；AC2: 29 条目；AC3: glob 计数。
