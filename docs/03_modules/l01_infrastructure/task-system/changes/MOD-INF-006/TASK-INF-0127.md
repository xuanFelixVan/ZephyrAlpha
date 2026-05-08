---
task_id: "TASK-INF-0127"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §5 依赖关系（13项）+ §6 产出物存放目录（19项）+ §7 集成目标（7项）"

title: "实现集成目标验证——7项集成点 + 13项依赖 + 19项产出物目录确认"
description: |
  验证蓝图 §7 的 7 项集成目标是否全部可集成。
  验证 §5 的 13 项依赖关系——14项必备链接中的真源文件全部存在。
  验证 §6 的 19 项产出物存放目录路径合法且层级合规。
  依赖可用性检查——task_repo/模块/蓝图注册表/meta注册表可用。
  集成契约确认——MCP Server 6 Tool 输入/输出契约符合 §3.5 定义。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\mcp\\task_manager_server.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\pipeline\\pipeline-module-registry.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\mcp\\tool_contracts.yaml"
  - "D:\\ZephyrAlpha\\data\\tasks.db"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\tests\\integration\\test_integration_targets.py"
    description: "集成目标——7项集成点的集成测试"
  - path: "D:\\ZephyrAlpha\\tests\\integration\\test_dependency_health.py"
    description: "依赖关系——13项依赖健康检查"

allowed_touch:
  - "D:\\ZephyrAlpha\\tests\\integration\\test_integration_targets.py"
  - "D:\\ZephyrAlpha\\tests\\integration\\test_dependency_health.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§7"
    reason: "集成目标 7项——SSoT"
  - module_id: "MOD-INF-006"
    section: "§5"
    reason: "依赖关系 13项——SSoT"
  - module_id: "MOD-INF-006"
    section: "§6"
    reason: "产出物存放目录 19项——SSoT"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§5 13项 + §6 19项 + §7 7项——全部验证目标"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
  - "M4"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "7项集成目标：全部有对应的集成测试通过"
  - "13项依赖关系：13项必备链接 + 超链接 + 所有文件在磁盘存在"
  - "19项产出物存放目录：路径层级合规——不超过 docs/03_modules/l01_infrastructure/task-system/ 下三级"
  - "task_repo 健康——create/transition 可执行"
  - "§5 超链接到策略/标准/模板等——所有路径存在"
  - "确认无 missing/invalid 路径"

rollback_instructions: |
  1. 删除新增集成测试文件

depends_on: ["TASK-INF-0102", "TASK-INF-0104", "TASK-INF-0106"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
  - "integration"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-006"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 实现集成目标验证——7集成 + 13依赖 + 19目录

## 目标

验证蓝图声明的全部集成点、依赖关系、产出物目录：
1. 7项集成目标 → 集成测试覆盖
2. 13项依赖 → 健康检查通过
3. 19项产出物存放目录 → 路径合规

## 触发条件

- TASK-INF-0102/0104/0106 完成

## 执行步骤

### 读
- 蓝图 §5 / §6 / §7 完整清单

### 做
1. 编写集成测试——验证 7项集成点的端到端可用性
2. 编写依赖健康检查——验证 13项 + 超链接在磁盘存在
3. 目录合规——验证 19项产出物存放路径

### 产
- test_integration_targets.py + test_dependency_health.py

### 检
```bash
pytest tests/integration/test_integration_targets.py -v
pytest tests/integration/test_dependency_health.py -v
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | test | 集成目标 / 依赖健康 全部通过 |
| 2 | files | 必备链接 14项全部可达 |
