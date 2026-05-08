---
task_id: "TASK-INF-0200"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §1 概述与模块定位 + §3 文件组成"

title: "模块骨架搭建——rollback-system 目录结构与注册"
description: |
  创建 MOD-INF-021 rollback-system 模块的完整目录骨架，包括：
  - 代码目录 `src/zephyr/rollback/` 及 `__init__.py`
  - 数据目录 `data/rollback/db_snapshots/` / `data/rollback/down/`
  - 运行时目录 `.zephyr/rollback_in_flight/`
  - 在 blueprint-registry.yaml 中注册 MOD-INF-021
  - 模块级 `__init__.py` 声明回滚系统公共接口
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\__init__.py"
    description: "回滚系统模块入口——导出核心公共接口"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\_manifest_.py"
    description: "模块文件清单——声明模块内所有 .py 文件及其职责"
  - path: "D:\\ZephyrAlpha\\data\\rollback\\db_snapshots\\"
    description: "SQLite 快照存放目录——{commit_sha}.jsonl，git tracked"
  - path: "D:\\ZephyrAlpha\\data\\rollback\\down\\"
    description: "Down-migration 脚本目录——{commit_sha}.sh/.ps1，自动生成"
  - path: "D:\\ZephyrAlpha\\.zephyr\\rollback_in_flight\\"
    description: "回滚 flight 记录目录——幂等保护 + 崩溃恢复"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\_manifest_.py"
  - "D:\\ZephyrAlpha\\data\\rollback\\"
  - "D:\\ZephyrAlpha\\.zephyr\\rollback_in_flight\\"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\*.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\**\\*.md"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "路径映射——产出物物理存放必须符合目录结构标准"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规创建——新建目录前验证路径架构合规"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——所有模型基座"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——了解模块定位(§1)、代码落位 src/zephyr/rollback/、文件组成(§3)"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
    reason: "目录结构标准——确认 03_modules 路径规范和 changes/ 子目录规则"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 2000
timeout_minutes: 15

acceptance_criteria:
  - "src/zephyr/rollback/__init__.py 存在且含 module-level docstring 说明模块身份"
  - "src/zephyr/rollback/_manifest_.py 存在且列出 §3 文件组成表中所有 18 个 .py 文件"
  - "data/rollback/db_snapshots/ 目录存在且被 git track"
  - "data/rollback/down/ 目录存在且被 git track"
  - ".zephyr/rollback_in_flight/ 目录存在"
  - "blueprint-registry.yaml 中 MOD-INF-021 已注册且状态为 Draft"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\rollback\__init__.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\rollback\_manifest_.py
  3. 删除 D:\ZephyrAlpha\data\rollback\（如仅含本任务创建的空目录）
  4. 删除 D:\ZephyrAlpha\.zephyr\rollback_in_flight\（如仅含本任务创建的空目录）
  5. 从 blueprint-registry.yaml 移除 MOD-INF-021 条目

depends_on: []
blocked_by: []
status: "done"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-021"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
