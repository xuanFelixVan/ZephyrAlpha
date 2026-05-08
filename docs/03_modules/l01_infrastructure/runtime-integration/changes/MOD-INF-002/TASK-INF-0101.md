---
task_id: "TASK-INF-0101"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §1 概述与模块定位 + §3 边界"
title: "runtime-integration 模块骨架搭建——目录结构、边界声明、上下游文件初始化"
description: |
  创建 runtime-integration 模块的完整目录骨架。
  包含：changes/MOD-INF-002/ 目录初始化、模块定位文档锚定（§1 概述确认此模块为 L01 Infrastructure 的运行时集成层）、
  边界声明落地（§3.1 覆盖：RI-01~15 + RL-001~048 + FMEA + ADR + 五视图；§3.2 不覆盖：审计守卫→MOD-INF-001、安全网关→MOD-INF-014 等）。
  输出模块 README.md（自描述）、模块级 directory-structure-standard 合规校验。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\changes\\MOD-INF-002\\"
    description: "任务卡存放目录——已完成初始化"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\README.md"
    description: "模块 README——自描述：15 RI 模块清单、边界声明、Phase 路线图摘要"
allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\changes\\MOD-INF-002\\**\\*.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\README.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"
  - "D:\\ZephyrAlpha\\config\\**\\*.yaml"
applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "所有路径必须与路径映射一致——目录结构标准"
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式 TASK-INF-NNNN"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "本蓝图——了解 §1 模块定位、§3 边界声明、§1.3 与 MOD-INF-016 承载关系"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
    reason: "目录结构标准——确保目录创建符合路径规范"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 8000
timeout_minutes: 30
acceptance_criteria:
  - "changes/MOD-INF-002/ 目录存在且可写"
  - "README.md 包含 15 个 RI 模块的完整清单"
  - "README.md 包含 §3.1 覆盖范围声明（6 项）和 §3.2 不覆盖路由（7 项）"
  - "README.md 包含 Phase 路线图（1a→1b→2a→2b→3→4→∞）摘要"
  - "所有路径符合 directory-structure-standard.md"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\runtime-integration\README.md（如已创建）
  2. 清空 D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\runtime-integration\changes\MOD-INF-002\ 目录下所有文件
  3. 删除 MOD-INF-002 目录（如仅含任务卡文件）
depends_on: []
blocked_by: []
status: "done"
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-002"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
